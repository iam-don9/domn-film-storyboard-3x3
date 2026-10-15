---
name: domn-film-storyboard-3x3
description: |
  根据用户提供的参考图 + 剧情提示词，单次 i2i 生成一张 3×3（9 格）连续分镜大图
  （整体 16:9，每格 16:9 等尺寸），再用脚本按最高画质裁成 9 张单图。触发词：分镜、
  分镜图、连续分镜、storyboard、九宫格分镜、3×3 分镜、把剧情画成分镜、一图九格。
  生成前必须对剧情做 Prompt QA（拆 9 格、补全或追问）。底层编排 gpt-imagegen-uuapi
  （锁定 gpt-image-2.5-flare，i2i 走 /images/edits），prompt 遵循 huashu-gpt-image
  方法论（中文短句 + 真实参考名）。禁止 9 次独立生成，只做单次 3×3。
---

# domn-film-storyboard-3x3 连续分镜图生成

参考图 + 剧情提示词 → **单次 i2i** 生成一张 3×3（9 格）连续分镜大图 → 自动裁成 9 张单图。

## 核心约定

- **单次出图**：一次性生成 1 张 3×3 大图，**禁止**拆成 9 次独立调用。
- **质量靠 prompt**：网格、角色一致性、光影统一全部用 prompt 约束，信任模型。
- **最高画质裁切**：三等分不做任何 resize，每格约 557×313（网关 16:9 桶 1672×941
  不能被 3 整除，右/下缘各丢 <3px，9 格完全等尺寸）。
- **后端**：`gpt-imagegen-uuapi` / `gpt-image-2.5-flare`，i2i 走 `/images/edits`，
  参考图 base64 传入，须 `image_tokens>0` 才算参考图真正生效。

## 工作流（5 步，逐步确认，不跳过 QA）

### 第 1 步 · 输入解析（智能判断，不确定就问）

- **参考图用途**：看参考图内容 + 用户提示词，判断是「角色设定图 / 画风参考 / 两者」。
  只给一张图说不清时，**问用户**是当角色还是当画风用。
- **画风**：从用户需求判断（写实 / 日漫 / 美漫 / 水墨 / 其他）。判不出就**问**。
  用真实参考名锚定（见 `references/PROMPT-TEMPLATE.md` 对照表）。

### 第 2 步 · Prompt QA（拆 9 格，这是硬性环节）

把剧情拆成 9 个连续分镜，每格定「景别 + 机位 + 动作/内容」：

- **正好 9 格**：进入第 3 步。
- **不足 9 格**：列出**补全清单**（用什么过渡镜头/细节填充到 9 格），
  **先给用户确认再生成**（有限度补全，不擅自脑补关键情节）。
- **超过 9 格**：**追问用户**——是否精简到 9 格，还是额外生成第二张 3×3。
- 确认分镜顺序、景别（远景/中景/特写）、动作描述是否清晰后再往下走。

### 第 3 步 · 组装 prompt

按 `references/PROMPT-TEMPLATE.md` 的 5 段结构组装 `--prompt`（英文正文 + 中文结尾固定句）。
**必须**满足两条硬校验：prompt 内嵌 `16:9` 与 `1672x941`；结尾原样写
`画面干净通透、避免过度锐化、噪点、伪细节。`

### 第 4 步 · 生成（单次 i2i）

```bash
PY="C:/Users/44155/.workbuddy/binaries/python/versions/3.13.12/python.exe"
"$PY" "C:/Users/44155/.workbuddy/skills/domn-film-storyboard-3x3/scripts/run_storyboard.py" \
  --prompt-file "<组装好的prompt.txt>" \
  --prompt-zh "<中文版分镜描述，仅报告用>" \
  --reference-image "F:/path/char.png" \
  --reference-description "角色设定图：<简述>" \
  --reference-focus "保留服装/配色/发型/面部特征" \
  --reference-image "F:/path/style.png" \
  --reference-description "画风参考：<简述>" \
  --reference-focus "保留笔触/色调/光影" \
  --out-dir "output/storyboard"
```

- 参考图可传多张，`--reference-description` / `--reference-focus` 数量须与
  `--reference-image` 一一对应。
- **Clash fake-ip 场景**（长请求被 `SSL UNEXPECTED_EOF` 掐断）加 `--proxy`
  走本地代理 127.0.0.1:7890。
- 参考图路径避免非 ASCII 字符（argv 编码会乱），必要时先 `cp` 到 ASCII 暂存目录。

### 第 5 步 · 裁切 + 报告

dispatcher 生成 `grid.png` 后自动调用 `crop_3x3.py` 裁出 `cells/cell_01.png ~ cell_09.png`。
最终向用户报告（中文）：

```text
分镜大图（3×3）
9 张单图路径（cell_01 ~ cell_09，阅读顺序）
每格尺寸与画质说明（最高画质三等分，未缩放）
本次生图情况（模型 / 模式 / provider / i2i 是否生效）
```

## 落盘与依赖

- 本 skill：`~/.workbuddy/skills/domn-film-storyboard-3x3/`。
- 依赖：同库下 `gpt-imagegen-uuapi`（`scripts/api_imagegen.py` 与 `run_via_proxy.py`）。
  dispatcher 会逐级上溯自动定位，无需改路径。
- 裁切依赖 PIL（两个内置 Python 均已装）。
