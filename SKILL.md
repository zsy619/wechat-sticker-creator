***

name: wechat-sticker-skill
description: Create WeChat emoji sticker series from any input (URL, topic, or content). Use when user asks to "做微信贴图", "微信贴图", "创建微信贴图包", "WeChat stickers", "微信emoji", "根据内容生成贴图", "做一套贴图", "生成贴图". Triggers on sticker creation, emoji design, reaction images, or any WeChat sticker-related request.
version: 2.0.0
metadata:
author: zhushuyan
tags: ["wechat", "sticker", "emoji", "表情包", "贴图", "微信贴图"]
----------------------------------------------------------

# 微信贴图生成器 (WeChat Sticker Creator)

本技能根据用户输入（链接、主题或内容），自动进行内容聚合、贴图设计和生成，输出一套完整的微信表情包。

## 核心工作流程

```
用户输入(链接/主题/内容)
    ↓
┌─ 输入类型检测 ─┐
│ 1. URL链接    │ → 获取链接内容 + 联网搜索相关内容
│ 2. 主题词     │ → 联网搜索相关内容
│ 3. 内容文本   │ → 提取核心 + 联网搜索相关内容
└───────────────┘
    ↓
内容聚合分析 (content-analysis.md)
    ↓
贴图设计 Manifest (sticker-manifest.md)
    ↓
生成推广文案 (copy.md) ⭐
    ↓
生成贴图提示词 (prompts/*.md)
    ↓
图片生成 (assets/*.png) - 至少3张
    ↓
输出汇总 & 标签推荐
```

## 输入类型检测规则

### 1. URL 链接

- **检测规则**: 输入以 `http://` 或 `https://` 开头
- **处理流程**:
  1. 使用 `baoyu-url-to-markdown` 获取链接内容
  2. 提取核心主题（标题、首段内容）
  3. 联网搜索相关内容（使用 WebSearch 工具）
- **示例**: `https://example.com/ai-news`

### 2. 主题词

- **检测规则**: 短文本（≤15字符），不包含URL模式
- **处理流程**:
  1. 直接使用主题作为搜索关键词
  2. 联网搜索相关内容（使用 WebSearch 工具）
  3. 提取热点、趋势、相关概念
- **示例**: "AI编程助手"、"摸鱼神器"、"职场黑话"

### 3. 内容文本

- **检测规则**: 长文本、段落、文章等
- **处理流程**:
  1. 提取核心主题和关键词
  2. 联网搜索相关内容（使用 WebSearch 工具）
  3. 聚合热点趋势和使用场景
- **示例**: 用户分享的公众号文章、备忘录笔记等

> **注意**: 如果网络API不可用，则跳过搜索步骤，直接使用原始输入进行内容聚合。

## 联网搜索策略

当需要进行联网搜索时，执行以下步骤：

### 搜索关键词构建

```
1. 从输入中提取 2-4 个核心关键词
2. 结合搜索类型添加后缀：
   - 新闻/热点类: "+最新消息"、"+2024趋势"
   - 话题/概念类: "+是什么"、"+解析"
   - 产品/工具类: "+使用技巧"、"+推荐"
3. 限制搜索结果数量：5-10条
```

### 内容提取重点

- 提取搜索结果中的核心观点
- 识别热点话题和趋势
- 发现相关的使用场景和受众痛点
- 收集流行语、梗、表情包素材

## 项目命名规则

### Topic Slug 生成规则

```
1. 从输入中提取 2-4 个核心关键词
2. 转换为 kebab-case（小写+连字符）
3. 最大长度：40个字符
4. 特殊字符处理：中文转拼音或英文翻译
```

**命名示例**:

| 原始输入              | 生成Slug                        |
| ----------------- | ----------------------------- |
| "AI编程工具推荐"        | `ai-biancheng-gongju-tuijian` |
| "摸鱼神器"            | `moyu-shenqi`                 |
| "Claude Code最佳实践" | `claude-code-zuijia-shijian`  |
| "打工人日常"           | `darengong-richang`           |

### 目录冲突解决规则

```
{slug}/ → 已存在？ → {slug}-YYYYMMDD-HHMMSS/
```

**示例**:

- 首次创建: `wechat-stickers/ai-tools/`
- 冲突时: `wechat-stickers/ai-tools-20260429-143052/`

## 项目目录结构

```
wechat-stickers/{topic-slug}/
├── project.yaml                    # 项目元数据
├── content-analysis.md             # 内容聚合分析
├── sticker-manifest.md             # 贴图设计清单
├── copy.md                         # 推广文案文档
├── token-stats.md                  # Token输入输出统计
├── prompts/                        # 贴图提示词目录
│   ├── 01-{sticker-name}.md        # 贴图1提示词
│   ├── 02-{sticker-name}.md        # 贴图2提示词
│   └── ...                         # 每张贴图一个文件
├── assets/                         # 贴图图片目录
│   ├── 01-{sticker-name}.png       # 贴图1图片
│   ├── 02-{sticker-name}.png       # 贴图2图片
│   └── ...                         # 每张贴图一张图片
├── batch.json                      # 批量生成任务文件
└── output/                         # 最终输出目录
    └── stickers-{topic-slug}.zip   # ZIP打包文件（可选）
```

## 内容聚合分析 (content-analysis.md)

完成联网搜索后，生成内容聚合分析文档：

```markdown
# 内容聚合分析

## 输入来源
- **类型**: [URL链接/主题词/内容文本]
- **原始输入**: <用户输入内容>
- **搜索关键词**: <构建的搜索关键词>

## 内容获取
- **主要来源**: <URL内容或原始内容的核心摘要>
- **相关搜索**: <联网搜索获取的相关内容摘要>

## 核心主题
- **主题**: <提取的主要主题>
- **子主题**: <2-4个相关子主题>

## 关键概念
| 概念 | 描述 | 应用场景 |
|-----|------|---------|
| 概念1 | <详细描述> | <使用场景> |
| 概念2 | <详细描述> | <使用场景> |

## 情感基调
- **主基调**: <funny/cute/professional/sarcastic/wholesome/emotional>
- **强度**: <高/中/低>
- **目标受众**: <目标用户群体描述>

## 使用场景
1. <场景1>: <具体描述>
2. <场景2>: <具体描述>
3. <场景3>: <具体描述>

## 热点趋势
- <当前热点1>
- <当前热点2>
- <流行语/梗>

## 贴图设计方向
基于以上分析，建议的贴图设计方向：
- <设计风格建议>
- <色彩方案建议>
- <文字内容建议>
```

## 贴图设计清单 (sticker-manifest.md)

### 贴图类型定义

| 类型          | 描述     | 典型示例            |
| ----------- | ------ | --------------- |
| `reaction`  | 快速反应表情 | "好的"、"收到"、"赞"   |
| `emotion`   | 情感表达   | 开心、悲伤、惊讶、生气     |
| `situation` | 场景化设计  | 加班、摸鱼、周末、咖啡时间   |
| `text`      | 文字表情   | "摸鱼"、"太强了"、"绝了" |
| `mascot`    | 角色形象   | 品牌IP、吉祥物反应      |

### Manifest 文件格式

```markdown
---
project: {topic-slug}
sticker_count: {N}
emotional_tone: {tone}
target_audience: {audience}
created: {YYYY-MM-DD HH:mm:ss}
---

# 贴图设计清单

## 贴图1: {sticker-name}
- **类型**: {type}
- **中文标签**: {中文标签}
- **英文标签**: {English label}
- **描述**: {贴图展示内容详细描述}
- **使用场景**: {何时发送此贴图}
- **文案**: {社交媒体推广文案，20-50字，适合社交媒体发布，务必包含贴图展示内容并在贴图中展示}
- **标签**: #{tag1} #{tag2} #{tag3} #{tag4} #{tag5}

## 贴图2: {sticker-name}
... (至少3张，最多12张)

## 标签汇总
- 平台标签: #微信表情 #微信贴图 #WeChatStickers
- 情感标签: #可爱 #搞笑 #治愈 #社恐自救 #打工人
- 主题标签: <根据内容生成>
- 风格标签: #表情包 #卡通 #每日壁纸 #头像
```

### 贴图命名规则

- 使用 2-4 个汉字或英文单词
- 文件名使用 kebab-case: `zhuang-bi`, `moyu-shenqi`
- 中文友好命名示例: `摸鱼中`、`太强了`、`老板来了`
- 避免使用特殊字符和过长的名称

## Token统计文档 (token-stats.md)

参考 references/token-stats.md ，生成项目后，记录本次使用的 Token 消耗情况：

```markdown
---
project: {topic-slug}
created: {YYYY-MM-DD HH:mm:ss}
---

# Token 输入输出统计

## 项目信息
- **主题**: {topic}
- **贴图数量**: {N} 张
- **生成风格**: {style}

## Token 消耗统计

| 阶段 | 输入Token | 输出Token | 备注 |
|-----|----------|----------|------|
| 内容聚合分析 | - | - | 联网搜索消耗 |
| 贴图设计 | - | - | Manifest生成 |
| 文案生成 | - | - | copy.md生成 |
| 提示词生成 | - | - | prompts生成 |
| **总计** | **{total_input}** | **{total_output}** | |

## 费用估算

- **模型**: {model_name}
- **单价**: 输入 ${input_price}/1M tokens，输出 ${output_price}/1M tokens
- **预估费用**: ${estimated_cost}

## 优化建议

- 合并相似请求减少 API 调用
- 复用提示词模板降低输入 Token
- 批量处理提高效率
```

## 文案文档 (copy.md)

生成项目后，为所有贴图生成统一的推广文案文档：

### copy.md 格式要求

```markdown
## {贴图名称}
### 内容
{推广文案内容，20-50字左右，适合社交媒体发布}

### 标签
#标签1 #标签2 #标签3 #标签4 #标签5
```

### 字段说明

| 字段       | 要求     | 说明                |
| -------- | ------ | ----------------- |
| **贴图名称** | 2-4个汉字 | 作为标题，如"摸鱼中"、"太强了" |
| **内容**   | 20-50字 | 推广文案，适合社交媒体传播     |
| **标签**   | 至少5个   | 分类：平台、情感、主题、风格、用途 |

### 文案风格要求

- **简短有力**：突出贴图特色，15-30字为佳
- **社交友好**：适合朋友圈、微博、小红书传播
- **引发共鸣**：触达目标用户痛点或兴趣
- **行动导向**：可包含引导互动的话术

### 标签分类要求

每张贴图至少 5 个标签，分类如下：

| 类别   | 说明     | 示例           |
| ---- | ------ | ------------ |
| 平台标签 | 标注平台属性 | #微信表情 #微信贴图  |
| 情感标签 | 表达情感类型 | #可爱 #搞笑 #治愈  |
| 主题标签 | 贴合内容主题 | #摸鱼 #打工人 #职场 |
| 风格标签 | 描述视觉风格 | #赛博朋克 #卡通    |
| 用途标签 | 使用场景   | #斗图 #表情包 #头像 |

### 文案生成示例

```markdown
## 摸鱼中
### 内容
打工人必备摸鱼指南！这套表情包含超实用的摸鱼技巧，让你在职场中游刃有余，享受带薪摸鱼的快乐！

### 标签
#微信表情 #摸鱼神器 #打工人必备 #职场生存 #摸鱼技巧 #赛博朋克 #表情包 #斗图
```

### 输出要求

- **文件名**: `copy.md`
- **位置**: 项目根目录
- **格式**: Markdown
- **编码**: UTF-8

## 提示词生成 (prompts/*.md)

每张贴图生成一个独立的提示词文件：

```markdown
---
name: {sticker-name}
type: {type}
chinese_label: {中文标签}
copy: {社交媒体推广文案，20-50字，将在贴图中展示}
tags: [{tag1}, {tag2}, {tag3}, {tag4}, {tag5}]
aspect_ratio: "1:1"
---

# 贴图提示词: {sticker-name}

## 核心文案（必须展示在贴图中）
{copy_text}（必须将这段文案以艺术字形式展示在贴图上）

## 视觉描述
<详细描述贴图应呈现的视觉效果，文案需醒目展示>

## 风格要求
- **风格**: {cartoon/kawaii/minimalist/hand-drawn/meme-style}
- **色彩方案**: <推荐的主色调和配色>
- **背景**: {transparent/white/单色背景}
- **尺寸**:1080×1440px（微信贴图标准尺寸）
- **格式**: PNG透明背景

## 文案展示要求
- 文案必须以艺术字形式展示在贴图上
- 文案位置：居中或底部
- 文案大小：醒目但不影响整体美观
- 文案样式：符合整体风格

## 参考元素
<任何参考图片或风格示例描述>

## 设计细节
- 表情/动作: <具体描述>
- 配饰/道具: <如有>
- 背景元素: <背景中的装饰元素>

## 文案内容
<用于社交媒体推广的文案内容，20-50字左右>

## 推荐标签
#标签1 #标签2 #标签3 #标签4 #标签5 #标签6
```

## 图片生成

### 阶段A: AI API 生成（按优先级尝试）

**API Provider 优先级**:

| 优先级 | Provider     | 模型                                    | 备注      |
| --- | ------------ | ------------------------------------- | ------- |
| 1   | `dashscope`  | qwen-image-2.0-pro                    | 账户欠费时跳过 |
| 2   | `seedream`   | doubao-seedream-5-0-260128            | 账户欠费时跳过 |
| 3   | `minimax`    | image-01                              | 未配置时跳过  |
| 4   | `openai`     | gpt-image-1.5                         | 未配置时跳过  |
| 5   | `openrouter` | google/gemini-3.1-flash-image-preview | 未配置时跳过  |
| 6   | `replicate`  | google/nano-banana-pro                | 未配置时跳过  |

**批量执行命令**:

```bash
# 生成 batch.json 文件
cd wechat-stickers/{slug}

# 按优先级尝试各 Provider
BUN_X=bun bun ~/.agents/skills/baoyu-imagine/scripts/main.ts \
  --batchfile batch.json \
  --provider {provider_name} \
  --json
```

**batch.json 格式**:

```json
{
  "tasks": [
    {
      "id": "01-sticker-name",
      "promptFiles": ["prompts/01-{sticker-name}.md"],
      "image": "assets/01-{sticker-name}.png",
      "ar": "1:1"
    },
    {
      "id": "02-sticker-name",
      "promptFiles": ["prompts/02-{sticker-name}.md"],
      "image": "assets/02-{sticker-name}.png",
      "ar": "1:1"
    }
  ]
}
```

### 阶段B: PIL 本地生成（所有API不可用时执行）

> ⚠️ **重要**: 必须执行此兜底方案，不能跳过图片生成步骤。

**脚本路径说明**:

根据 skill 安装方式不同，脚本路径可能有所差异。以下提供三种定位方式：

| 定位方式 | 命令 | 说明 |
| ------ | ---- | ---- |
| **默认路径** | `~/.agents/skills/wechat-sticker-skill/scripts/generate_stickers.py` | 常规安装位置 |
| **自定义目录** | `$AGENTS_SKILLS_DIR/wechat-sticker-skill/scripts/generate_stickers.py` | 通过环境变量指定 |
| **全局搜索** | `find ~ -name "generate_stickers.py" -type f 2>/dev/null` | 未知路径时使用 |

> 💡 **快速定位**: 如果不确定脚本位置，可直接运行 `find ~ -name "generate_stickers.py" -type f 2>/dev/null | head -1` 获取完整路径。

**PIL 生成命令**:

```bash
cd wechat-stickers/{slug}

# 使用环境变量（如果已设置），否则使用默认路径
python3 ${AGENTS_SKILLS_DIR:-~/.agents}/skills/wechat-sticker-skill/scripts/generate_stickers.py \
  --input prompts/ \
  --output assets/ \
  --theme cyberpunk
```

**支持的风格主题**:

| 主题           | 特点                   | 默认     |
| ------------ | -------------------- | ------ |
| `cyberpunk`  | 赛博朋克，霓虹灯效果，紫色/蓝色/青色系 | ✓ 默认   |
| `kawaii`     | 圆脸卡通，大眼睛，粉色系         | <br /> |
| `minimal`    | 简约线条，扁平化设计           | <br /> |
| `meme`       | 表情包风格，高对比度           | <br /> |
| `hand-drawn` | 手绘涂鸦风格               | <br /> |
| `retro`      | 复古像素风格               | <br /> |
| `neon`       | 霓虹灯风格，黑色背景           | <br /> |

**macOS 字体路径**:

| 字体   | 路径                                         |
| ---- | ------------------------------------------ |
| 苹方   | `/System/Library/Fonts/PingFang.ttc`       |
| 黑体   | `/System/Library/Fonts/STHeiti Medium.ttc` |
| 华文细黑 | `/System/Library/Fonts/STHeiti Light.ttc`  |

**PIL 生成规则**:

根据不同用途，生成不同尺寸的图片：

| 类型 | 尺寸 | 宽高比 | 用途 |
|-----|------|-------|------|
| 贴图 | 1080×1440px | 3:4 | 单独图片消息发布 |
| 公众号封面 | 900×383px | 2.35:1 | 文章封面 |
| 正文配图 | 1080×607px | 16:9 | 内容展示 |
| 缩略图 | 200×200px | 1:1 | 预览缩略 |

**贴图生成规则**（默认）：
- 画布尺寸：1080×1440px
- 背景：透明（RGBA模式）
- 风格：赛博朋克（默认），霓虹灯效果
- 文字渲染：使用 ImageFont.truetype
- 输出格式：PNG透明背景


## 最终输出

### ZIP 打包（可选）

```bash
cd wechat-stickers/{slug}/assets
zip -r ../output/stickers-{slug}.zip *.png
```

### 输出汇总格式

```
═══════════════════════════════════════════
    微信表情包生成完成！
═══════════════════════════════════════════

主题: {topic}
输入类型: {URL链接/主题词/内容文本}
贴图数量: {N} 张
输出目录: wechat-stickers/{slug}/

生成文件:
  ✓ project.yaml          - 项目元数据
  ✓ content-analysis.md   - 内容聚合分析
  ✓ sticker-manifest.md   - 贴图设计清单
  ✓ prompts/              - {N} 个提示词文件
  ✓ assets/               - {N} 张PNG图片 (500×500)

推荐标签:
  #微信表情 #微信贴图 #可爱 #搞笑 #治愈
  #{主题相关标签1} #{主题相关标签2}

═══════════════════════════════════════════
```

## 公众号发布规格 (可选)

当需要通过微信公众号发布贴图内容时，生成以下规格的图片：

### 图片规格表

| 类型     | 尺寸          | 宽高比    | 文件大小  | 格式          | 用途     |
| ------ | ----------- | ------ | ----- | ----------- | ------ |
| 头图封面   | 900×383px   | 2.35:1 | ≤2MB  | JPG/PNG     | 文章封面   |
| 正文配图   | 1080×607px  | 16:9   | ≤2MB  | JPG/PNG/GIF | 内容展示   |
| 小图/缩略图 | 200×200px   | 1:1    | 无限制   | PNG/SVG     | 预览/缩略  |
| 贴图       | 1080×1440px | 3:4    | ≤10MB | JPG/PNG     | 单独图片消息 |

### 贴图生成（最佳选择）

贴图是微信推出的图片消息形式，适合单独发布贴图内容展示：

```bash
# 生成贴图图片
python3 ~/.agents/skills/wechat-sticker-skill/scripts/generate_cover.py \
  --output assets/xhs-post-{sticker-name}.png \
  --title "{贴图名称}" \
  --subtitle "{描述文案（最长50字）}" \
  --theme cyberpunk \
  --type sticker
```

**规格说明**：

- **最佳比例**: 3:4（竖版）
- **推荐尺寸**: 1080×1440px
- **描述文案**: 支持最长 50 字
- **适用场景**: 单独发布图片消息，类似小红书笔记风格

### 公众号封面生成

```bash
# 生成公众号头图封面
python3 ~/.agents/skills/wechat-sticker-skill/scripts/generate_cover.py \
  --output assets/cover-wechat.png \
  --title "{主题}" \
  --subtitle "{副标题}" \
  --theme cyberpunk \
  --type wechat-cover
```

### 正文配图生成

```bash
# 生成正文配图
python3 ~/.agents/skills/wechat-sticker-skill/scripts/generate_cover.py \
  --output assets/content-{sticker-name}.png \
  --title "{贴图名称}" \
  --theme cyberpunk \
  --width 1080 \
  --height 607 \
  --type content-image
```

### 缩略图生成

```bash
# 生成缩略图
python3 ~/.agents/skills/wechat-sticker-skill/scripts/generate_cover.py \
  --output assets/thumb-{sticker-name}.png \
  --title "{贴图名称}" \
  --theme cyberpunk \
  --width 200 \
  --height 200 \
  --type thumbnail
```

### 公众号发布输出

```
assets/
├── cover-wechat.png              # 公众号头图封面 (900×383)
├── content-01-{name}.png         # 正文配图 (1080×607)
├── content-02-{name}.png         # 正文配图
├── thumb-01-{name}.png           # 缩略图 (200×200)
├── 01-{sticker-name}.png         # 原始贴图 (500×500)
└── ...
```

### 公众号排版建议

1. **封面图**: 使用 `cover-wechat.png`，突出主题和风格
2. **正文**: 每张贴图配合 `content-{name}.png` 展示
3. **缩略图**: 用于文末汇总展示，格式统一

## 标签推荐策略

自动生成 5-10 个相关标签：

### 标签分类

| 类别   | 标签                          |
| ---- | --------------------------- |
| 平台标签 | #微信表情 #微信贴图 #WeChatStickers |
| 情感标签 | #可爱 #搞笑 #治愈 #社恐自救 #打工人 #摸鱼  |
| 主题标签 | 根据内容自动提取（如 #AI #编程 #职场 #生活） |
| 风格标签 | #表情包 #卡通 #每日壁纸 #头像          |

### 标签生成规则

```
1. 必须包含：平台标签（1-2个）
2. 情感标签：根据贴图基调选择（2-3个）
3. 主题标签：从内容分析中提取（1-3个）
4. 风格标签：基于设计风格选择（1-2个）
```

## 质量检查清单

在生成完成后，进行以下质量检查：

- [ ] 至少生成 3 张贴图
- [ ] 所有贴图为 PNG 格式且背景透明
- [ ] 贴图风格保持一致
- [ ] 文字清晰可读（如有）
- [ ] 情感基调符合预期
- [ ] 每张贴图都分配了标签（至少5个）
- [ ] 每张贴图都包含社交媒体推广文案（20-50字）
- [ ] 所有文件保存到正确的目录结构
- [ ] 已验证 PIL 兜底方案（如所有API不可用）
- [ ] 内容聚合分析完整准确
- [ ] 标签推荐覆盖全面
- [ ] copy.md 文案文件已生成
- [ ] token-stats.md 统计文件已生成

## 故障排除

### 网络搜索失败

- **解决方案**: 跳过搜索步骤，直接使用原始输入
- **影响**: 内容分析可能不够全面，但不影响生成

### 所有API不可用

- **解决方案**: 使用 PIL 本地生成
- **命令**: `python3 generate_stickers.py --input prompts/ --output assets/`
- **注意**: 确保已创建 prompts/ 目录并包含所有提示词文件

### 目录冲突

- **解决方案**: 添加时间戳后缀
- **格式**: `{slug}-YYYYMMDD-HHMMSS/`

### 图片尺寸问题

- **微信贴图标准**:1080×1440px
- **文件格式**: PNG透明背景
- **如需调整**: 使用 Image.resize() 和 img.save() 方法

