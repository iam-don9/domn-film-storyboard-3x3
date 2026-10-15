# 3×3 分镜图 Prompt 组装模板

> 本模板供主 agent 在「Prompt QA」之后、调用 `run_storyboard.py` 之前，把 9 格分镜
> 组装成发给模型的 `--prompt`。方法论遵循 huashu-gpt-image：**中文短句拆语义、
> 真实参考名替代形容词、不堆 `Subject:`/`Style:` 伪结构**。

## 硬约束（违反会被底层脚本拒绝或判失败）

1. `--prompt` 正文必须内嵌 `16:9` 和 `1672x941` 两个字符串（底层 `api_imagegen.py`
   校验 prompt 含 canvas 值，缺失直接退出）。
2. `--prompt` 末尾必须**原样**以这句中文结尾，不得改字：
   `画面干净通透、避免过度锐化、噪点、伪细节。`
3. `--prompt-zh` 是中文版，只用于生成后报告，**不发送模型**。
4. 禁止在 prompt 里写 `8K`、`极致细节`、`ultra-detailed` 等诱发伪纹理的词。

## 组装顺序（5 段）

### 第 1 段 · 参考图声明（i2i）

逐张声明参考图，说清用途。参考图数量须与 `--reference-image` 完全一致。

- 角色设定图：`Image 1 is the character reference: <服装/配色/发型/面部特征/体态>。`
- 画风参考图：`Image 2 is the style reference: <笔触/色调/光影/材质>。`

### 第 2 段 · 任务 + 网格硬约束

```
Create one single image that is a 3x3 storyboard grid of 9 equal panels
(3 rows, 3 columns), each panel ratio 16:9 and identical size, separated by
thin white gutters, numbered 1 to 9 in reading order (top-left to bottom-right).
```

### 第 3 段 · 全局一致性锚定（角色 + 光影 + 画风）

写死这三条，9 格共用，是「角色一致、光影统一」的关键：

```
Keep the SAME character across all 9 panels: same face, hairstyle, outfit,
colors, proportions — no redesign, no costume change.
Keep ONE consistent lighting direction and ONE unified color grade across all
panels, matching the style reference.
Style: <真实参考名，如 吉卜力/宫崎骏、新海诚、Jim Lee、Denis Villeneuve 摄影、
Penguin Books 封面、MUJI 版式>。
```

> 画风用**真实参考名**锚定，不要写「很好看、很有质感」这类形容词。

### 第 4 段 · 逐格分镜描述

每格一句，固定「景别 + 机位 + 动作/内容」结构，编号对应阅读顺序：

```
Panel 1: <景别> shot, <机位/角度>, <动作/内容>。
Panel 2: ...
...
Panel 9: <景别> shot, <机位/角度>, <动作/内容>。
```

### 第 5 段 · 比例/分辨率 + 结尾固定句

```
Ratio 16:9, resolution 1672x941. No watermark, no extra text outside the panels.
画面干净通透、避免过度锐化、噪点、伪细节。
```

## 景别术语速查

| 景别 | 英文 | 说明 |
|---|---|---|
| 远景 | extreme wide / wide shot | 交代环境全貌，人物很小 |
| 全景 | full shot | 人物全身 + 少量环境 |
| 中景 | medium shot | 腰部以上，动作与对话主体 |
| 近景 | medium close-up | 胸部以上，强调表情 |
| 特写 | close-up | 面部/局部，情绪焦点 |

机位：`eye-level`（平视）/ `high angle`（俯拍）/ `low angle`（仰拍）/ `over-the-shoulder`
（过肩）/ `POV`（主观视角）/ `tracking`（跟拍）。

## 画风参考名对照（替代形容词）

| 目标画风 | 用这些真实参考名 |
|---|---|
| 写实电影感 | Denis Villeneuve、Wes Anderson、Christopher Nolan 的摄影风格 |
| 日漫赛璐璐 | 吉卜力/宫崎骏、新海诚 |
| 美漫 | Jim Lee、Alex Ross |
| 水墨 | 中国传统水墨、齐白石 |
| 复古/纸感 | Penguin Books 封面、MUJI 版式 |
| 3D 卡通 | Pixar、DreamWorks |

## 完整组装示例（填空后）

```
Image 1 is the character reference: a young woman with short black hair, a
red scarf, and a beige trench coat.
Image 2 is the style reference: soft painterly cel shading with warm evening
light.

Create one single image that is a 3x3 storyboard grid of 9 equal panels
(3 rows, 3 columns), each panel ratio 16:9 and identical size, separated by
thin white gutters, numbered 1 to 9 in reading order (top-left to bottom-right).

Keep the SAME character across all 9 panels: same face, hairstyle, outfit,
colors, proportions. Keep ONE consistent lighting direction and ONE unified
color grade, matching the style reference. Style: 吉卜力/宫崎骏.

Panel 1: wide shot, eye-level, she walks into a quiet train station at dusk.
Panel 2: full shot, low angle, she looks up at the departure board.
Panel 3: medium close-up, eye-level, she checks her watch nervously.
Panel 4: wide shot, high angle, a train pulls into the platform.
Panel 5: medium shot, over-the-shoulder, she steps toward the open door.
Panel 6: close-up, eye-level, her hand grips the door frame.
Panel 7: medium shot, tracking, she walks down the aisle looking for a seat.
Panel 8: medium close-up, eye-level, she sits and stares out the window.
Panel 9: wide shot, eye-level, the train departs into the night.

Ratio 16:9, resolution 1672x941. No watermark, no extra text outside the panels.
画面干净通透、避免过度锐化、噪点、伪细节。
```
