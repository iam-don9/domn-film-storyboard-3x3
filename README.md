# domn-film-storyboard-3x3

> 独立技能仓库 · 来自 domn skills 集合（视频制作 域）

根据用户提供的参考图 + 剧情提示词，单次 i2i 生成一张 3×3（9 格）连续分镜大图 （整体 16:9，每格 16:9 等尺寸），再用脚本按最高画质裁成 9 张单图。触发词：分镜、 分镜图、连续分镜、storyboard、九宫格分镜、3×3 分镜、把剧情画成分镜、一图九格。 生成前必须对剧情做 Prompt QA（拆 9 格、补全或追问）。底层编排 gpt-imagegen-uuapi （锁定 gpt-image-2.5-flare，i2i 走 /images/edits），prompt 遵循 huashu-gpt-image 方法论（中文短句 + 真实参考名）。禁止 9 次独立生成，只做单次 3×3。 --- # domn-film-storyboard-3x3 连续分镜图生成 参考图 + 剧情提示词 → **单次 i2i** 生成一张 3×3（9 格）连续分镜大图 → 自动裁成 9 张单图。 ## 核心约定 - **单次出图**：一次性生成 1 张 3×3 大图，**禁止**拆成 9 次独立调用。 - **质量靠 prompt**：网格、角色一致性、光影统一全部用 prompt 约束，信任模型。

## 元信息
- **领域**：视频制作
- **触发/用途**：见上方说明
- **标签**：—

## 使用方法
将本仓库内容放入支持 `SKILL.md` 的 Agent 技能目录（如 WorkBuddy `~/.workbuddy/skills/`、Codex skills 目录）即可调用。

---
*本仓库由 domn skills 库导出，技能定义以 `SKILL.md` 为准。*
