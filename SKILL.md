---
name: wechat-sticker-skill
description: Create WeChat emoji sticker series from any input (URL, topic, or content). Use when user asks to "做微信贴图", "微信贴图", "创建微信贴图包", "WeChat stickers", "微信emoji", "根据内容生成贴图", "做一套贴图", "生成贴图". Triggers on sticker creation, emoji design, reaction images, or any WeChat sticker-related request.
version: 4.1.0
tags: ["wechat", "sticker", "emoji", "表情包", "贴图", "微信贴图", "remotion", "frame-generation"]
metadata:
  author: zhushuyan
  updated: "2026-05-01"
---

> **更新日志**：所有变更记录在 [CHANGELOG.md](./CHANGELOG.md)。

# 微信贴图生成器 v4.1.0 (WeChat Sticker Creator)

本技能根据用户输入（链接、主题或内容），自动进行内容聚合、贴图设计和生成，输出一套完整的微信表情包。

## 核心设计：三段式图像生成

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
│     每张贴图构建独立 Remotion 项目，每帧 = <Composition> 组件
│     导出 **GIF**（90帧动画），独特视觉设计 + 动画特效                              │
│     ↓ 异常                                              │
│  ③ PIL 本地生成（兜底）                                 │
│     词汇表驱动，场景构图，程序化几何绘制                 │
└────────────────────────────────────────────────────────┘
    ↓
最终输出（ZIP / 公众号发布）
```

**优先级**：AI → Remotion → PIL。每层失败自动降级，无需人工干预。

## skill 项目结构

```
wechat-stickers/                    ← 技能根目录
│
├── SKILL.md                              ← 入口文件
├── CHANGELOG.md                          ← 更新日志
│
├── remotion/                              ← Remotion 模板源文件（阶段二读取）
│   ├── template/
│   │   ├── index.tsx                     ← registerRoot 入口模板
│   │   ├── StickerComponent.tsx          ← 外层组件模板（返回 <Composition>）
│   │   └── StickerContent.tsx            ← 内层组件模板（含 useCurrentFrame）
│   ├── components/
│   │   └── EmojiElement.tsx              ← 可复用 emoji 组件
│   └── styles/
│       └── base.css                      ← 基础样式
│
├── scripts/
│   ├── generate_frames.py                ← 主脚本（读取 remotion/template/ 生成项目）
│   └── pil_fallback.py                   ← PIL 兜底生成器
│
└── docs/                                ← 规范文档
    ├── workflow.md                       ← 核心工作流
    ├── content-format.md                ← 内容格式（content-analysis / manifest / prompts）
    ├── frame-design.md                  ← Remotion 帧设计规范
    ├── remotion-projects.md             ← Remotion 项目完整结构
    ├── project-structure.md              ← 项目目录结构
    ├── image-generation.md               ← 三段式图像生成流程
    ├── output.md                        ← 最终输出与打包
    └── qa.md                           ← 质量检查

```

## 项目目录结构

详见 [docs/project-structure.md](docs/project-structure.md)。

## 快速开始

```bash
# 完整生成流程（自动三段式降级）
python3 scripts/generate_frames.py \
  --input prompts/ \
  --output assets/ \
  --theme cyberpunk

# 仅 PIL 兜底（调试用）
python3 scripts/pil_fallback.py \
  --input prompts/ \
  --output assets-pil/ \
  --theme cyberpunk
```

## 核心概念

### 为什么是 Remotion？

PIL 的程序化绘制有上限——无法生成真正的语义图像（大模型理解"赛博朋克风格 AI 大脑"的细节远超过几何堆叠）。Remotion 作为 React 组件，可以用代码精确控制每一帧的视觉元素，适合需要高质量、独特视觉设计的贴图。

### 三段式降级机制

| 优先级 | 方式 | 优势 | 劣势 |
|--------|------|------|------|
| 1 | AI生成 | 语义理解、真实光影、细节丰富 | API成本、调用失败可能 |
| 2 | Remotion帧导出 | 像素级控制、程序化精确、动画可能 | 需要Node.js环境、帧组件编写 |
| 3 | PIL | 无需网络、完全本地、执行稳定 | 视觉上限低、程序化几何 |

### Remotion 帧设计原则

每套贴图使用**单一 Remotion 项目 + Sequence 架构**：
- **外层**（StickerComponent）：返回 `<Composition>`，**不使用** `useCurrentFrame()`
- **中层**（StickerContent）：持有 `<Sequence>` 列表，注入 `__SEQUENCES__`
- **内层**（StickerScene）：每张贴图的视觉组件，**使用** `useCurrentFrame()` + 5个动画函数

**输出规格**：1080×1440，90帧@30fps（3秒），**GIF 动画**

详见 [docs/content-format.md](docs/content-format.md#remotion-帧设计frame-designmd)。

## 支持的风格

`cyberpunk` / `kawaii` / `neon` / `retro` / `hand-drawn` / `minimal` / `meme`

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
