---
name: wechat-sticker-skill
description: Create WeChat emoji sticker series from any input (URL, topic, or content). Use when user asks to "做微信贴图", "微信贴图", "创建微信贴图包", "WeChat stickers", "微信emoji", "根据内容生成贴图", "做一套贴图", "生成贴图". Triggers on sticker creation, emoji design, reaction images, or any WeChat sticker-related request.
version: 4.9.6
tags: ["微信", "贴图", "表情包", "微信表情包", "微信贴图", "帧动画", "图片生成"]
metadata:
  author: zhushuyan
  updated: "2026-05-03"

---

> **更新日志**：所有变更记录在 [CHANGELOG.md](./CHANGELOG.md)。

# 微信贴图生成器 v4.9.6 (WeChat Sticker Creator)

本技能根据用户输入（链接、主题或内容），自动进行内容聚合、贴图设计和生成，输出一套完整的微信表情包。

## 核心设计：两段式图像生成

```
用户输入(链接/主题/内容)
    ↓
内容聚合分析 → 贴图设计 → 提示词生成
    ↓
┌─ 图像生成（优先级递进） ───────────────────────────────┐
│  ① AI生成图像（首选）                                   │
│     调用大模型（GPT-Image / Seedream 等）直接生成高质量帧
│     ↓ 异常                                              │
│  ② Remotion 帧导出（第二选择）                          │
│     建独立 Remotion 项目，每张贴图对应每帧 = <Composition> 组件
│     导出 **GIF**（90帧动画），独特视觉设计 + 动画特效                              │
│     ↓ 异常                                              │
│  报错停止（不再降级）                                   │
└────────────────────────────────────────────────────────┘
    ↓
最终输出（ZIP / 公众号发布）
```

**优先级**：AI → Remotion。Remotion 失败则报错，不再降级。

## skill 项目结构

```
wechat-stickers/                    ← 技能根目录
│
├── SKILL.md                              ← 入口文件
├── CHANGELOG.md                          ← 更新日志
│
│   ├── remotion/
│   │   ├── template/
│   │   │   ├── index.tsx                     ← registerRoot 入口模板
│   │   │   ├── StickerComponent.tsx         ← 外层组件模板（返回 <Composition>）
│   │   │   └── StickerContent.tsx           ← 核心动画逻辑（自包含所有主题配置）
│   │   └── styles/
│   │       └── base.css                     ← 全局 CSS 重置（仅 body/margin 重置）
│
├── scripts/
│   ├── _vocab.py                         ← 共享词汇表模块（VOCABULARY + THEMES）[共享数据源]
│   ├── run_full_pipeline.py              ← 完整工作流串联入口（一次性执行全流程）
│   ├── generate_content_analysis.py      ← 节点①：内容聚合分析（URL/主题/文本 → content-analysis.md）
│   ├── generate_manifest.py               ← 节点②：manifest 生成（含 vocabulary 校验）
│   ├── generate_prompts.py               ← 节点③：prompts 文件生成（含 vocabulary 校验）
│   ├── generate_frames.py                ← 节点④：图片生成（AI → Remotion 两段式）
│   ├── pack_stickers.py                  ← 节点⑤：打包 ZIP + 生成封面/缩略图
│   ├── qa_check.py                       ← 节点⑥：QA 自动化检查（尺寸/格式/词汇表）
│   ├── generate_tags.py                  ← 标签生成（从 prompts 提取关键词）
│   ├── generate_session_log.py            ← Session Log 生成（token 估算 + 阶段记录）
│   └── generate_post.py                   ← 公众号推广文档（从 manifest 提取贴图详情）
│
└── docs/                                ← 技能内部参考文档（不复制到项目）
    ├── workflow.md                       ← 核心工作流
    ├── prompts-format.md                ← Prompt 生成规范
    ├── content-format.md                ← 内容格式（content-analysis / manifest / prompts）
    ├── frame-design.md                  ← Remotion 帧设计规范
    ├── remotion-projects.md             ← Remotion 项目完整结构
    ├── project-structure.md              ← 项目目录结构
    ├── image-generation.md              ← 两段式图像生成流程
    ├── output.md                        ← 最终输出与打包
    ├── qa.md                            ← 质量检查

```

## 项目目录结构

详见 [docs/project-structure.md](docs/project-structure.md)。

## 快速开始

```bash
# ── 完整工作流（自动化串联）──────────────────────────────
# 一次性完成：内容聚合 → manifest → prompts → 图片生成
python3 scripts/run_full_pipeline.py \
  --input "AI编程助手" \
  --output ~/wechat-stickers/ai-coding-assistant \
  --theme cyberpunk

# ── 分步执行（调试用）───────────────────────────────────
# 步骤1：内容聚合分析
python3 scripts/generate_content_analysis.py \
  --input "AI编程助手" \
  --output ~/wechat-stickers/ai-coding-assistant/

# 步骤2：生成 manifest
python3 scripts/generate_manifest.py \
  --input ~/wechat-stickers/ai-coding-assistant/content-analysis.md \
  --output ~/wechat-stickers/ai-coding-assistant/sticker-manifest.md

# 步骤3：生成 prompts
python3 scripts/generate_prompts.py \
  --input ~/wechat-stickers/ai-coding-assistant/sticker-manifest.md \
  --output ~/wechat-stickers/ai-coding-assistant/prompts/

# 步骤4：图片生成（两段式：AI → Remotion）
python3 scripts/generate_frames.py \
  --input ~/wechat-stickers/ai-coding-assistant/prompts/ \
  --output ~/wechat-stickers/ai-coding-assistant/assets-cyberpunk/ \
  --theme cyberpunk

# 步骤5：打包 + QA 检查
python3 scripts/pack_stickers.py \
  --input ~/wechat-stickers/ai-coding-assistant/assets-cyberpunk/ \
  --output ~/wechat-stickers/ai-coding-assistant/stickers.zip

python3 scripts/qa_check.py \
  --input ~/wechat-stickers/ai-coding-assistant/assets-cyberpunk/ \
  --vocabulary docs/prompts-format.md
```

### --mode 参数

`generate_frames.py` 支持强制指定生成模式：

| 值 | 行为 |
|----|------|
| `auto`（默认） | AI → Remotion 两段式 |
| `ai` | 仅 AI 生成，失败则整张贴图失败 |
| `remotion` | 仅 Remotion 生成，失败则报错 |

### 新增参数（v4.4.0）

| 参数 | 说明 |
|------|------|
| `--continue-on-error` | 某张贴图失败时跳过继续处理下一张 |
| `--debug-remotion` | 保留 Remotion 调试文件（TSX 源码写入 `debug/` 目录） |
| `--template-dir` | 自定义 Remotion 模板目录（覆盖内置模板 `remotion/template/`） |
| `--remotion-version` | 指定 Remotion 版本（default: `4.0.448`） |
| `--dry-run` | 仅解析 `.md` 文件并打印生成计划，不生成任何文件 |

`pack_stickers.py` 参数：

| 参数 | 说明 |
|------|------|
| `--gif-only` | 只打包 GIF 文件，忽略 PNG/JPG |
| `--png-only` | 只打包 PNG 文件，忽略 GIF/JPG |

## 核心概念

### 为什么是 Remotion？

Remotion 作为 React 组件，可以用代码精确控制每一帧的视觉元素，适合需要高质量、独特视觉设计的贴图。

### 两段式降级机制

| 优先级 | 方式 | 优势 | 劣势 |
|--------|------|------|------|
| 1 | AI生成 | 语义理解、真实光影、细节丰富 | API成本、调用失败可能 |
| 2 | Remotion帧导出 | 像素级控制、程序化精确、动画可能 | 需要Node.js环境、帧组件编写 |

Remotion 失败则报错，不再降级。

### Remotion 帧设计原则

每套贴图使用**单一 Remotion 项目 + Sequence 架构**：
- **外层**（StickerComponent）：返回 `<Composition>`，**不使用** `useCurrentFrame()`
- **中层**（StickerContent）：持有 `<Sequence>` 列表，注入 `__SEQUENCES__`
- **内层**（StickerScene）：每张贴图的视觉组件，**使用** `useCurrentFrame()` + 5个动画函数

**输出规格**：1080×1440，90帧@30fps（3秒），**GIF 动画**

详见 [docs/frame-design.md](docs/frame-design.md)。

## 支持的风格

`cyberpunk` / `kawaii` / `neon` / `retro` / `hand-drawn` / `minimal` / `meme`

## 项目文档

> **说明**：`tags.md` / `session-log.md` / `post.md` 由 pipeline **自动生成**（步骤 5.5、7、8），直接输出到项目根目录。技能 `docs/` 目录下的文档为内部参考，不复制到项目。

| 文档 | 生成脚本 | 输出位置 | 说明 |
|------|----------|----------|------|
| `tags.md` | `generate_tags.py` | 项目根目录 | 从 prompts 提取关键词，微信贴图标签 |
| `session-log.md` | `generate_session_log.py` | 项目根目录 | Token 估算、阶段耗时、项目记录 |
| `post.md` | `generate_post.py` | 项目根目录 | 公众号推广文案（从 manifest 提取） |

**自动生成时机**：完整 pipeline（`--mode auto`）中，步骤 5.5/7/8 自动执行。单独运行时需手动调用对应脚本。

**补跑命令**：pipeline 中断后，可使用以下命令单独生成缺失文档：
```bash
python3 scripts/generate_tags.py --input sticker-manifest.md --output tags.md --theme cyberpunk
python3 scripts/generate_session_log.py --project <name> --theme cyberpunk --sticker-count 8 --output session-log.md
python3 scripts/generate_post.py --project ~/wechat-stickers/<project> --theme cyberpunk --output post.md
```

## 详细文档

- **Remotion 帧设计** → [docs/frame-design.md](docs/frame-design.md)
- **Remotion 项目结构** → [docs/remotion-projects.md](docs/remotion-projects.md)
- **项目目录结构** → [docs/project-structure.md](docs/project-structure.md)
- **工作流与规范** → [docs/workflow.md](docs/workflow.md)
- **内容格式** → [docs/content-format.md](docs/content-format.md)
    - **Prompt 生成规范** → [docs/prompts-format.md](docs/prompts-format.md)
- **图片生成** → [docs/image-generation.md](docs/image-generation.md)
- **输出与发布** → [docs/output.md](docs/output.md)
- **质量保障** → [docs/qa.md](docs/qa.md)
