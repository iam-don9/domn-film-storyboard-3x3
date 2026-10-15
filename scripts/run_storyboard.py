#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""domn-film-storyboard-3x3 dispatcher：单次 i2i 生成 3x3 分镜大图，再裁成 9 张单图。

职责是「薄编排」——只负责把组装好的分镜 prompt 交给底层
gpt-imagegen-uuapi 的 api_imagegen.py 出图，再调用 crop_3x3.py 裁切。
不复制生图逻辑，不做分镜拆解（拆解由主 agent 按 SKILL.md 完成）。

调用链：
  run_storyboard.py  ->  api_imagegen.py (i2i, 16:9, 1672x941)
                     ->  crop_3x3.py     (最高画质三等分 -> 9 张)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def locate_imagegen_script():
    """从当前脚本逐级上溯，找 gpt-imagegen-uuapi/scripts/api_imagegen.py。"""
    for base in [SCRIPT_DIR, *list(SCRIPT_DIR.parents)[:8]]:
        cand = base / "gpt-imagegen-uuapi" / "scripts" / "api_imagegen.py"
        if cand.is_file():
            return cand
    raise SystemExit(
        "找不到 gpt-imagegen-uuapi/scripts/api_imagegen.py。"
        "请确认该 skill 与本 skill 在同一 skills 库下（~/.workbuddy/skills/）。"
    )


def main():
    ap = argparse.ArgumentParser(
        description="单次 i2i 生成 3x3 分镜大图并裁成 9 张单图。"
    )
    ap.add_argument("--prompt-file", help="组装好的 9 格分镜 prompt 文本文件。")
    ap.add_argument("--prompt", help="分镜 prompt 字符串（与 --prompt-file 二选一）。")
    ap.add_argument("--prompt-zh", required=True, help="中文 prompt，用于报告，不发送模型。")
    ap.add_argument(
        "--reference-image", action="append", default=[], metavar="PATH",
        help="参考图路径（角色设定图 / 画风参考），可重复传多张。",
    )
    ap.add_argument(
        "--reference-description", action="append", default=[],
        help="每张参考图的简短描述，数量须与 --reference-image 一致。",
    )
    ap.add_argument(
        "--reference-focus", action="append", default=[],
        help="每张参考图要保留的区域/属性，数量须与 --reference-image 一致。",
    )
    ap.add_argument("--size", default="1672x941", help="输出分辨率，默认 1672x941（网关 16:9 桶）。")
    ap.add_argument("--aspect-ratio", default="16:9", help="画布比例，默认 16:9。")
    ap.add_argument("--out-dir", default="output/storyboard", help="输出目录。")
    ap.add_argument("--prefix", default="cell", help="裁切单图文件名前缀。")
    ap.add_argument("--proxy", action="store_true", help="经本地代理 127.0.0.1:7890 请求（Clash fake-ip 场景）。")
    args = ap.parse_args()

    if bool(args.prompt) == bool(args.prompt_file):
        raise SystemExit("Provide exactly one of --prompt or --prompt-file.")
    if not args.reference_image:
        raise SystemExit("i2i 至少需要一张 --reference-image。")
    if len(args.reference_description) != len(args.reference_image):
        raise SystemExit("--reference-description 数量须与 --reference-image 一致。")
    if len(args.reference_focus) != len(args.reference_image):
        raise SystemExit("--reference-focus 数量须与 --reference-image 一致。")

    imagegen = locate_imagegen_script()
    if args.proxy:
        imagegen = imagegen.parent / "run_via_proxy.py"
        if not imagegen.is_file():
            raise SystemExit("--proxy 需要 gpt-imagegen-uuapi/scripts/run_via_proxy.py，未找到。")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    grid_path = out_dir / "grid.png"

    # 组装底层 api_imagegen.py 的命令
    cmd = [
        sys.executable, str(imagegen),
        "--mode", "i2i",
        "--aspect-ratio", args.aspect_ratio,
        "--size", args.size,
        "--prompt-zh", args.prompt_zh,
        "--out-dir", str(out_dir),
        "--filename", "grid.png",
    ]
    if args.prompt_file:
        cmd += ["--prompt-file", str(Path(args.prompt_file).resolve())]
    else:
        cmd += ["--prompt", args.prompt]
    for ref in args.reference_image:
        cmd += ["--reference-image", ref]
    for desc in args.reference_description:
        cmd += ["--reference-description", desc]
    for focus in args.reference_focus:
        cmd += ["--reference-focus", focus]

    print("== 生成 3x3 分镜大图 ==", file=sys.stderr)
    print("  " + " ".join(cmd), file=sys.stderr)
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    if proc.returncode not in (0, 2):
        raise SystemExit(f"api_imagegen.py 退出码 {proc.returncode}。")
    if proc.returncode == 2:
        # 出图成功但尺寸/比例/i2i 校验未达标，仍尝试裁切但给出警告
        sys.stderr.write("WARNING: 底层报告「失败」（尺寸/比例/i2i 未达标），仍继续裁切。\n")

    try:
        result = json.loads(proc.stdout.strip())
    except json.JSONDecodeError:
        raise SystemExit("无法解析 api_imagegen.py 的 JSON 输出。")

    image_path = result.get("image_path")
    if not image_path or not Path(image_path).is_file():
        raise SystemExit(f"未得到有效成果图，底层报告: {result.get('报告')}")

    # 裁切成 9 张
    cells_dir = out_dir / "cells"
    crop_script = SCRIPT_DIR / "crop_3x3.py"
    print("\n== 裁切 9 张单图 ==", file=sys.stderr)
    crop_proc = subprocess.run(
        [sys.executable, str(crop_script), "--input", image_path,
         "--out-dir", str(cells_dir), "--prefix", args.prefix],
        capture_output=True, text=True, encoding="utf-8",
    )
    print(crop_proc.stdout, file=sys.stderr)
    if crop_proc.returncode != 0:
        print(crop_proc.stderr, file=sys.stderr)
        raise SystemExit("裁切失败。")

    cells = sorted(cells_dir.glob(f"{args.prefix}_*.png"))
    summary = {
        "分镜大图": image_path,
        "裁切单图目录": str(cells_dir.resolve()),
        "单图数量": len(cells),
        "单图列表": [str(p.resolve()) for p in cells],
        "底层报告": result.get("报告"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
