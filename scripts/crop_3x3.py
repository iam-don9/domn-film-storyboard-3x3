#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一张 3x3 分镜大图按「最高画质」三等分裁成 9 张单图（不做重采样）。

网关 16:9 桶固定返回 1672x941（±1px），不能被 3 整除。
裁切策略：每格 = (W//3, H//3)，从左上角 (0,0) 开始行优先切，
右缘/下缘的余数像素（<3px）丢弃 —— 这样 9 格尺寸完全一致，
且不做任何 resize/上采样，保留原分辨率（最高画质）。

命名顺序即阅读顺序：cell_01 是左上第一格，cell_09 是右下最后一格
（第一行 1-3，第二行 4-6，第三行 7-9）。
"""
import argparse
from pathlib import Path

from PIL import Image


def main():
    ap = argparse.ArgumentParser(
        description="把 3x3 分镜大图按最高画质裁成 9 张等尺寸单图。"
    )
    ap.add_argument("--input", required=True, help="3x3 分镜大图 PNG 路径。")
    ap.add_argument("--out-dir", required=True, help="9 张单图输出目录。")
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--prefix", default="cell", help="输出文件名前缀，默认 cell。")
    args = ap.parse_args()

    img = Image.open(args.input).convert("RGB")
    W, H = img.size
    cw, ch = W // args.cols, H // args.rows
    used_w, used_h = cw * args.cols, ch * args.rows
    drop_w, drop_h = W - used_w, H - used_h

    if cw <= 0 or ch <= 0:
        raise SystemExit(f"图片尺寸 {W}x{H} 不足以切 {args.rows}x{args.cols} 格。")

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    cells = []
    idx = 1
    for r in range(args.rows):
        for c in range(args.cols):
            left, top = c * cw, r * ch
            box = (left, top, left + cw, top + ch)
            cell = img.crop(box)
            name = f"{args.prefix}_{idx:02d}.png"
            cell.save(out / name)
            cells.append((name, cw, ch))
            idx += 1

    print(f"整图尺寸: {W}x{H}")
    print(f"每格尺寸: {cw}x{ch}（9 格完全一致）")
    print(f"丢弃余数: 右缘 {drop_w}px, 下缘 {drop_h}px（<3px，无损画质）")
    print(f"输出 {len(cells)} 张单图:")
    for name, w, h in cells:
        print(f"  {out / name}  ({w}x{h})")


if __name__ == "__main__":
    main()
