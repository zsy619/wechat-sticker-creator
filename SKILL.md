***

name: wechat-sticker-skill
description: Create WeChat emoji sticker series from any input (URL, topic, or content). Use when user asks to "做微信贴图", "微信贴图", "创建微信贴图包", "WeChat stickers", "微信emoji", "根据内容生成贴图", "做一套贴图", "生成贴图". Triggers on sticker creation, emoji design, reaction images, or any WeChat sticker-related request.
version: 3.0.0
metadata:
  author: zhushuyan
  updated: 2026-04-30
  changelog: |
    ## v3.0.x 更新记录 (2026-04-30)

    ### generate_stickers.py 修复
    - [修复] parse_prompt_file 返回值与 main() 解包数量不匹配（返回5值: name/text/copy/visual_elements/style_keywords）
    - [修复] STICKER_SIZE=500 → W=1080, H=1440（微信贴图标准）
    - [修复] 字体大小按1080×1440比例放大（60→140等，约×2.2）
    - [重构] 所有风格 Image.new 背景从实色不透明改为透明 RGBA(0,0,0,0)
    - [重构] 圆形遮罩只应用于背景层，文字层独立绘制不受裁切
    - [修复] 文字底部改为以画布底边为基准（y=H-30=1410），圆形主题文字不再被裁切
    - [修复] WARP标签位置：改到主文字上方（label_draw在text_bottom_draw之前绘制，y=tt-行高-8）
    - [修复] alpha_composite层叠顺序：bg_layer在下、text_layer在上，文字完全覆盖背景

    ### SKILL.md 完善
    - [更新] 版本 2.0.0 → 3.0.0
    - [新增] Prompt 格式 v3.0：visual_elements + style_keyword frontmatter 字段
    - [新增] 实际项目 Prompt 示例（warp-terminal：AI补全、命令面板）
    - [新增] 每张贴图的专属视觉生成规则（name→视觉函数路由机制）
    - [更新] Manifest 格式 v3.0：引用 prompts 中的 visual_elements，不再重复写入文案
    - [更新] 项目目录结构：新增 assets-{theme}/ 多风格目录
    - [修复] 移除不存在的 references/token-stats.md 引用
    - [修复] 残留 500×500 → 1080×1440
    - [修复] PNG透明背景 描述统一为「PNG（透明或主题相关背景）」
    - [新增] 故障排除章节：name字段不匹配、字体缺失
    - [更新] 质量检查清单 v3.0

    ## v3.0 核心机制
    - 每张贴图通过 name 字段路由到专属 PIL 绘图函数（6种已实现）
    - 文字固定在画布底部（距底边30px），不受圆形遮罩影响
    - 背景层应用圆形遮罩（R=500），文字层独立叠加
    - 支持7种风格：cyberpunk / kawaii / neon / retro / hand-drawn / minimal / meme

    ## v2.0: 基础多风格支持
tags: ["wechat", "sticker", "emoji", "表情包", "贴图", "微信贴图", "个性化", "专属视觉"]
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
├── prompts/                        # 贴图提示词目录（含专属视觉规则）
│   ├── 01-{sticker-name}.md       # 贴图1提示词（含visual_elements）
│   ├── 02-{sticker-name}.md        # 贴图2提示词
│   └── ...                         # 每张贴图一个文件
├── assets/                         # 默认风格贴图（--theme默认cyberpunk）
│   └── *.png                       # 1080×1440px PNG
├── assets-{theme1}/                # 风格1贴图（如assets-kawaii）
├── assets-{theme2}/                # 风格2贴图（如assets-neon）
└── output/                         # 最终输出目录
    └── stickers-{topic-slug}.zip   # ZIP打包文件（可选）
```

> **注意**: 多风格生成时，每种风格单独存放于 `assets-{theme}/` 目录，避免覆盖。

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

### Manifest 文件格式（v3.0）

```markdown
---
project: {topic-slug}
sticker_count: {N}
sticker_names: ["名称1", "名称2", ...]  # 对应prompts/下的name字段
them es: ["cyberpunk", "kawaii"]     # 要生成的主题风格
emotional_tone: {tone}
target_audience: {audience}
created: {YYYY-MM-DD HH:mm:ss}
---

# 贴图设计清单

## 贴图1: {sticker-name}
- **类型**: {type}
- **中文标签**: {中文标签}
- **描述**: {贴图展示内容详细描述，对应prompts中的visual_elements}
- **使用场景**: {何时发送此贴图}
- **Prompt文件**: prompts/01-{sticker-name}.md（内含copy、visual_elements）

## 贴图2: {sticker-name}
... (至少3张，最多12张)

## 标签汇总
- 平台标签: #微信表情 #微信贴图 #WeChatStickers
- 情感标签: #可爱 #搞笑 #治愈 #社恐自救 #打工人
- 主题标签: <根据内容生成>
- 风格标签: #表情包 #卡通 #每日壁纸 #头像
```

> **重要**: v3.0 中文案（copy）和视觉元素（visual_elements）不再单独写入 Manifest，而是写入对应的 `prompts/*.md` frontmatter 中。Manifest 只记录设计规划，具体内容由 Prompt 文件承载。

### 贴图命名规则

- 使用 2-4 个汉字或英文单词
- 文件名使用 kebab-case: `zhuang-bi`, `moyu-shenqi`
- 中文友好命名示例: `摸鱼中`、`太强了`、`老板来了`
- 避免使用特殊字符和过长的名称

## Token统计文档 (token-stats.md)

生成项目后，记录本次使用的 Token 消耗情况（联网搜索消耗可使用平台计费工具估算）：

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
| 内容聚合分析 | - | - | 联网搜索消耗（估算） |
| 贴图设计 | - | - | Manifest生成 |
| 提示词生成 | - | - | prompts生成 |
| **总计** | **{total_input}** | **{total_output}** | |

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

每张贴图生成一个独立的提示词文件，**每个贴图有专属视觉元素**（不只是模板文字）。

### Prompt 格式（v3.0）

```markdown
---
name: {sticker-name}
type: {type}
copy: {核心文案，≥10字，将完整展示在贴图底部}
style_keyword: [关键词1, 关键词2, 关键词3]
visual_elements: [元素1, 元素2, 元素3]
aspect_ratio: "3:4"
---

# 贴图提示词: {sticker-name}

## 核心文案（必须展示在贴图中）
{copy_text}（完整文案，≥10字，展示在贴图底部）

## 视觉设计规则
- **主体**: <专属视觉主体描述，如「代码补全下拉框」「⌘K 按键」等>
- **元素**: <每个视觉元素的详细描述>
- **动效**: <可选的动态描述>

## 风格要求
- **风格**: <由 --theme 参数决定: cyberpunk/kawaii/hand-drawn/retro/neon/minimal/meme>
- **配色**: <由主题配色方案决定>
- **主视觉**: <视觉占画面比例（如55%），文字框占底部40%>
- **尺寸**: 1080×1440px（微信贴图标准）
- **格式**: PNG（透明或主题相关背景）

## 文字展示
- **位置**: 画布底部，居中
- **左右边距**: 30px
- **距底边**: 30px
- **支持**: 多行换行
```

**实际项目 Prompt 示例（warp-terminal）**:

```markdown
---
name: AI补全
type: text
copy: AI补全让我打字停不下来
style_keyword: [代码补全条, 渐变文字, 灰色代码背景]
visual_elements: [补全下拉框, 代码片段, Tab键图标, 灰色代码背景, 青色高亮文字]
aspect_ratio: "3:4"
---

# 贴图提示词: AI补全

## 核心文案（必须展示在贴图中）
AI补全让我打字停不下来

## 视觉设计规则
- **主体**: 代码编辑器补全下拉框，内含灰色代码片段
- **补全框**: 深色半透明背景，白色边框，青色高亮当前选项
- **代码文字**: 灰色代码字 + 青色补全提示文字
- **Tab图标**: 右下角显示 Tab 键图标，暗示按Tab接受补全
- **背景**: 浅灰色代码编辑区纹理

## 风格要求
- **风格**: cyberpunk（赛博朋克）
- **配色**: 深灰背景 + 青色(#00FFFF)高亮 + 白色代码
- **主视觉**: 补全下拉框占画面60%，文字框占底部40%
- **尺寸**: 1080×1440px
- **格式**: PNG（透明或主题相关背景）

## 文字展示
- 位置: 画布底部，居中
- 左右边距: 30px
- 距底边: 30px
- 支持多行换行
```

```markdown
---
name: 命令面板
type: text
copy: ⌘K一按命令全搞定超方便
style_keyword: [Command+K按键, 搜索框, 霓虹边框]
visual_elements: [⌘K大按键, 深色搜索框, 模糊命令列表, 霓虹发光边框]
aspect_ratio: "3:4"
---

# 贴图提示词: 命令面板

## 核心文案（必须展示在贴图中）
⌘K一按命令全搞定超方便

## 视觉设计规则
- **主体**: 超大 ⌘K 按键，占据画面中心上方40%
- **按键设计**: 圆形/圆角矩形，青色边框发光，内含 ⌘ 和 K 两个字母
- **搜索框**: 按键下方，半透明深色框，内有模糊的命令列表
- **发光效果**: 按键边缘青色霓虹发光

## 风格要求
- **风格**: cyberpunk（赛博朋克）
- **配色**: 黑色背景 + 青色发光(#00FFFF) + 洋红点缀(#FF00FF)
- **主视觉**: ⌘K 按键占50%，文字框占底部40%
- **尺寸**: 1080×1440px
- **格式**: PNG（透明或主题相关背景）

## 文字展示
- 位置: 画布底部，居中
- 左右边距: 30px
- 距底边: 30px
- 支持多行换行
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

| 主题           | 配色主色     | 背景风格            | 默认     |
| ------------ | ---------- | --------------- | ------ |
| `cyberpunk`  | 青色 #00FFFF | 深色圆形+网格+光晕    | ✓ 默认   |
| `kawaii`     | 粉色 #FF69B4 | 粉色渐变椭圆+圆脸眼睛   | <br /> |
| `minimal`    | 深灰 #212529 | 白色+圆形轮廓         | <br /> |
| `meme`       | 橙红 #FF4500 | 橙黄实色+边框         | <br /> |
| `hand-drawn` | 棕色 #8B4513 | 米色+手绘抖动线条      | <br /> |
| `retro`      | 金色 #FFD700 | 深红像素+棋盘格       | <br /> |
| `neon`       | 洋红 #FF00FF | 深黑圆形+多层霓虹光晕    | <br /> |

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
- 背景：主题相关（透明或实色）
- 文字位置：**画布底部居中**，左右边距30px，距底边30px，多行换行
- 文字渲染：使用 ImageFont.truetype
- 输出格式：PNG

### 每张贴图的专属视觉生成规则

**核心机制**: PIL 脚本根据贴图 `name` 字段自动路由到专属视觉绘制函数，与 `--theme` 风格组合生成最终图片。

**Prompt 中的专属视觉字段**:

```yaml
visual_elements: [元素1, 元素2, 元素3]
style_keyword: [关键词1, 关键词2, 关键词3]
```

**当前已实现的 name → 视觉路由**:

| name 值 | 视觉主体 | 视觉元素 |
|---------|---------|---------|
| `AI补全` | 代码补全框 | 终端窗口 + 下拉列表 + Tab键图标 |
| `命令面板` | ⌘K 按键 | 圆形发光按键 + 搜索框 + 命令列表 |
| `闪电速度` | 闪电符号 | ⚡ + 速度放射线 + 光芒爆发 |
| `智能建议` | AI 大脑 | 神经网络 + 节点发光 + 终端建议条 |
| `团队协作` | 多窗口 | 多个终端窗口并排 + 同步图标 + 连接线 |
| `Warp粉丝` | 终端+红心 | 终端窗口 + 大红心 + 漂浮小心形 |

**自定义新贴图流程**:
1. 在 `prompts/` 下创建 `{num}-{name}.md`
2. `name` 字段写中文贴图名（如 `摸鱼中`）
3. `copy` 字段写核心文案（≥10字）
4. `visual_elements` 列出视觉元素供 AI 生成参考
5. `style_keyword` 列出风格关键词
6. 运行 PIL 生成时，脚本根据 `name` 自动匹配合适的视觉结构

> **注意**: `name` 字段决定视觉结构。若新建贴图的 `name` 不在已实现列表中，脚本将使用通用文字贴图（仅文字渲染，无专属视觉元素）。


## 最终输出

### ZIP 打包（可选）

```bash
cd wechat-stickers/{slug}/assets
zip -r ../output/stickers-{slug}.zip *.png
```

### 输出汇总格式

```
═══════════════════════════════════════════
    微信贴图生成完成！
═══════════════════════════════════════════

主题: {topic}
输入类型: {URL链接/主题词/内容文本}
贴图数量: {N} 张
输出目录: wechat-stickers/{slug}/

生成文件:
  ✓ project.yaml          - 项目元数据
  ✓ content-analysis.md   - 内容聚合分析
  ✓ sticker-manifest.md   - 贴图设计清单
  ✓ prompts/              - {N} 个提示词文件（含专属视觉规则）
  ✓ assets/               - {N} 张PNG图片 (1080×1440)

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
├── 01-{sticker-name}.png         # 原始贴图 (1080×1440)
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
- [ ] 所有贴图为 PNG 格式
- [ ] 所有贴图尺寸为 1080×1440px（3:4竖版）
- [ ] 贴图风格保持一致（同一--theme）
- [ ] 文字清晰可读，底部居中、左右边距30px、距底边30px
- [ ] 每张贴图copy字段≥10字
- [ ] 每张贴图的visual_elements字段已填写
- [ ] 所有文件保存到正确的目录结构
- [ ] PIL兜底方案已验证（所有API不可用时使用）
- [ ] 内容聚合分析完整准确
- [ ] 标签推荐覆盖全面（每张≥5个标签）
- [ ] 同一项目多风格生成（如需）: 分别存放于 assets-{theme}/ 目录
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

- **微信贴图标准**: 1080×1440px
- **文件格式**: PNG（透明或主题相关背景）
- **如需调整**: 使用 Image.resize() 和 img.save() 方法

### name 字段不匹配

- **症状**: 生成的贴图只有文字，无专属视觉
- **原因**: 新建贴图的 name 不在已实现路由列表中
- **解决方案**: 在 generate_stickers.py 的 dispatch 字典中新增路由函数，或回退到通用文字贴图

### 字体缺失

- **症状**: 文字渲染为默认字体或警告
- **原因**: macOS 系统字体路径不存在
- **解决方案**: 检查 FONT_PATHS 列表，确保至少一个路径有效

