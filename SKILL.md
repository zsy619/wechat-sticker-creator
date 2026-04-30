***

name: wechat-sticker-skill
description: Create WeChat emoji sticker series from any input (URL, topic, or content). Use when user asks to "做微信贴图", "微信贴图", "创建微信贴图包", "WeChat stickers", "微信emoji", "根据内容生成贴图", "做一套贴图", "生成贴图". Triggers on sticker creation, emoji design, reaction images, or any WeChat sticker-related request.
version: 3.3.0
tags: ["wechat", "sticker", "emoji", "表情包", "贴图", "微信贴图", "个性化", "专属视觉"]
metadata:
  author: zhushuyan
  updated: 2026-04-30

> **更新日志**：所有变更记录在 [CHANGELOG.md](./CHANGELOG.md)，本文件仅保留最新版本说明。

---

# 微信贴图生成器 (WeChat Sticker Creator)

本技能根据用户输入（链接、主题或内容），自动进行内容聚合、贴图设计和生成，输出一套完整的微信表情包。

## 文档结构

```
wechat-sticker-skill/
├── SKILL.md              ← 本文件，入口
├── CHANGELOG.md          ← 更新日志
├── scripts/
│   └── generate_stickers.py   ← PIL 生成器
└── docs/
    ├── workflow.md        ← 核心工作流、输入检测、搜索策略、项目命名
    ├── content-format.md  ← content-analysis / sticker-manifest / copy / prompts 格式
    ├── image-generation.md← 四阶段图片生成工作流
    ├── output.md          ← 最终输出、ZIP打包、公众号发布规格
    └── qa.md              ← 标签策略、质量检查清单、故障排除
```

## 快速开始

```
用户输入(链接/主题/内容)
    ↓
内容聚合分析 (docs/content-format.md → content-analysis.md)
    ↓
贴图设计 Manifest (docs/content-format.md → sticker-manifest.md)
    ↓
生成贴图提示词 (docs/content-format.md → prompts/*.md)
    ↓
图片生成 (scripts/generate_stickers.py)
    ↓
输出汇总 & 标签推荐
```

## 核心设计

### 词汇表驱动绘制

`prompts/*.md` 中的 `visual_elements` 字段直接驱动 PIL 绘制，无需为新项目编写代码：

```yaml
---
name: 摸鱼神器
copy: 摸鱼中，勿扰
visual_elements: [brain, 终端窗口, 红心]
style_keyword: [cyberpunk, 赛博朋克]
---
```

脚本根据 `visual_elements` 自动匹配词汇表函数，按场景角色（FOCUS 主体 / ACCENT 点缀）布局。

### 场景构图系统（方案D）

| 布局 | 触发条件 | FOCUS分布 | ACCENT分布 |
|------|---------|----------|-----------|
| `single` | 1个FOCUS | 中心放大 | 外围8方位 |
| `dual` | 2个FOCUS | 左右均分 | 缝隙填补+外围 |
| `triple` | ≥3个FOCUS | 三列横排 | 上下两端 |
| `diffuse` | 无FOCUS | — | 全场弥散 |

语义角色：`ELEMENT_SCENE_ROLE` 将关键词映射为 FOCUS（适合居中放大）或 ACCENT（适合小尺寸散布）。

### 支持的风格

`cyberpunk` / `kawaii` / `neon` / `retro` / `hand-drawn` / `minimal` / `meme`

### 生成命令

```bash
python3 scripts/generate_stickers.py \
  --input prompts/ \
  --output assets-cyberpunk/ \
  --theme cyberpunk
```

## 详细文档

- **工作流与规范** → [docs/workflow.md](docs/workflow.md)
- **内容格式** → [docs/content-format.md](docs/content-format.md)
- **图片生成** → [docs/image-generation.md](docs/image-generation.md)
- **输出与发布** → [docs/output.md](docs/output.md)
- **质量保障** → [docs/qa.md](docs/qa.md)
