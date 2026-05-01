# 微信贴图生成器

一个智能化的微信贴图生成工具，可以根据链接、主题或内容自动生成一套完整的微信表情贴图，并附带推广文案和标签。

## 功能特点

- 🤖 **智能识别**: 自动识别输入类型（URL链接、主题词或内容文本）
- 🔍 **内容聚合**: 联网搜索相关内容，整合热点趋势
- ✨ **自动设计**: 基于内容分析设计贴图方案
- 🎨 **多种风格**: 支持赛博朋克、可爱、简约、表情包、手绘等多种风格（默认赛博朋克）
- ✍️ **文案生成**: 为每张贴图生成推广文案（20-50字）
- 🏷️ **标签推荐**: 为每张贴图自动生成标签（至少5个）
- 📊 **Token统计**: 记录输入输出Token消耗和费用估算
- 📱 **公众号发布**: 支持生成公众号封面、正文配图、缩略图等多种规格
- 🔄 **兜底机制**: API 不可用时自动切换到本地 PIL 生成

## 快速开始

当你想要创建微信表情包时，只需说：

- "做微信贴图"
- "创建微信贴图"
- "根据内容生成贴图"
- "做一套贴图"

### 输入类型

本工具支持三种输入类型：

#### 1. URL 链接

输入一个网页链接，工具会自动：

- 获取链接内容
- 提取核心主题
- 联网搜索相关内容

```
示例: https://example.com/ai-news
```

#### 2. 主题词

输入一个简短主题（≤15字符），工具会：

- 使用主题作为搜索关键词
- 联网搜索相关内容
- 提取热点和趋势

```
示例: "AI编程助手" 或 "摸鱼神器"
```

#### 3. 内容文本

输入一段文字或文章，工具会：

- 提取核心主题和关键词
- 联网搜索相关内容
- 聚合使用场景和情感基调

```
示例: 用户分享的公众号文章、备忘录笔记等
```

## 工作流程

```
用户输入 → 输入类型检测 → 内容聚合分析 → 贴图设计 → 提示词生成 → 文案生成 → 图片生成 → 输出
```

1. **输入检测**: 识别输入是链接、主题还是内容
2. **内容聚合**: 联网搜索，收集相关热点和趋势
3. **设计贴图**: 基于内容分析设计贴图方案（至少3张）
4. **生成提示词**: 为每张贴图生成详细的图像提示词
5. **生成文案**: 为每张贴图生成推广文案（20-50字）
6. **生成标签**: 为每张贴图生成标签（至少5个）
7. **图片生成**: 使用 AI API 或本地 PIL 生成图片
8. **输出汇总**: 提供文件路径、文案和标签

## 项目结构

生成的表情包项目会保存在以下目录结构中：

```
wechat-stickers/{项目根目录}/                              ← 用户项目目录
│
├── prompts/                             ← 贴图提示词源文件（输入）
│   ├── 01-贴图1.md
│   └── 02-贴图2.md
│
├── remotion-sticker/      ← 阶段二 Remotion 项目（每张贴图一个帧）
│   ├── package.json                     ← @remotion/cli 4.0.448, remotion 4.0.448
│   └── src/
│       ├── index.tsx                    ← registerRoot 入口
│       ├── StickerComponent.tsx          ← 外层组件（返回 <Composition>）
│       ├── StickerContent.tsx           ← 内层组件（含 useCurrentFrame + 动画）
│       └── styles.css
│
├── assets/                              ← 非指定风格的统一 PNG（可选）
├── assets-cyberpunk/                    ← cyberpunk 风格 PNG
├── assets-kawaii/                       ← kawaii 风格 PNG
├── assets-neon/                         ← neon 风格 PNG
├── assets-retro/                        ← retro 风格 PNG
├── assets-hand-drawn/                   ← hand-drawn 风格 PNG
├── assets-minimal/                      ← minimal 风格 PNG
├── assets-meme/                         ← meme 风格 PNG
│
├── content-analysis.md                  ← 内容聚合分析文档
├── sticker-manifest.md                  ← 贴图设计清单
└── stickers.zip                        ← 最终打包（可选）
```

## 命名规则

### 主题命名

- 从输入中提取 2-4 个核心关键词
- 转换为小写+连字符格式
- 最大长度 40 个字符

**示例**:

| 原始输入       | 生成名称                          |
| ---------- | ----------------------------- |
| "AI编程工具推荐" | `ai-biancheng-gongju-tuijian` |
| "摸鱼神器"     | `moyu-shenqi`                 |
| "打工人日常"    | `darengong-richang`           |

### 贴图命名

- 使用 2-4 个汉字或英文单词
- 文件名使用 kebab-case 格式
- 中文友好命名示例: `摸鱼中`、`太强了`、`老板来了`

## 贴图类型

| 类型   | 描述       | 典型示例          |
| ---- | -------- | ------------- |
| 反应表情 | 快速回复场景   | "好的"、"收到"、"赞" |
| 情感表达 | 喜怒哀乐等情感  | 开心、悲伤、惊讶      |
| 场景化  | 工作生活场景   | 加班、摸鱼、周末      |
| 文字表情 | 带文字的表情   | "摸鱼"、"太强了"    |
| 角色形象 | 品牌IP或吉祥物 | 定制角色反应        |

## 生成风格

### 赛博朋克（默认）

深色背景 + 网格线 + 霓虹光晕效果，紫色/蓝色/青色系配色，适合科技感和潮流风格

### 霓虹灯

全黑背景 + 文字发光效果，强调视觉冲击力

### 可爱

圆脸卡通风格，大眼睛，粉色系配色，适合可爱系表情包

### 简约

扁平化设计，简洁线条，适合现代简约风格

### 表情包

高对比度，夸张表情，适合搞笑类表情包

### 手绘

涂鸦风格，随性自在，适合个性化表情包

### 复古像素

深红背景 + 像素方块装饰，致敬经典游戏风格

## 文案生成规则

每张贴图都会生成推广文案，保存到 `copy.md` 文件：

```markdown
## {贴图名称}（不超过20个字）
### 内容
{推广文案，20-50字左右，适合社交媒体发布}

### 标签
#标签1 #标签2 #标签3 #标签4 #标签5
```

### 文案格式要求

| 字段 | 要求 | 说明 |
|-----|------|------|
| 贴图名称 | H2，不超过20字 | 如"摸鱼中"、"太强了" |
| 内容 | H3，20-50字 | 推广文案，适合社交媒体传播 |
| 标签 | H3，至少5个 | 空格分隔，以 # 开头 |

### 文案风格

- **简短有力**：突出贴图特色，15-30字为佳
- **社交友好**：适合朋友圈、小红书传播
- **引发共鸣**：触达目标用户痛点或兴趣
- **行动导向**：可包含引导互动的话术

### 标签要求

每张贴图至少生成 5 个标签，分类如下：

| 类别 | 说明 | 示例 |
|-----|------|------|
| 平台标签 | 标注平台属性 | #微信表情 #微信贴图 |
| 情感标签 | 表达情感类型 | #可爱 #搞笑 #治愈 |
| 主题标签 | 贴合内容主题 | #摸鱼 #打工人 #职场 |
| 风格标签 | 描述视觉风格 | #赛博朋克 #卡通 |
| 用途标签 | 使用场景 | #斗图 #表情包 #头像 |

## 输出示例

```
═══════════════════════════════════════════
    微信表情包生成完成！
═══════════════════════════════════════════

主题: 摸鱼神器
输入类型: 主题词
贴图数量: 6 张
输出目录: wechat-stickers/moyu-shenqi/

生成文件:
  ✓ project.yaml          - 项目元数据
  ✓ content-analysis.md   - 内容聚合分析
  ✓ sticker-manifest.md   - 贴图设计清单
  ✓ copy.md               - 推广文案文档
  ✓ token-stats.md        - Token统计文档
  ✓ prompts/              - 6 个提示词文件
  ✓ assets/               - 6 张 PNG 图片 (500×500)

═══════════════════════════════════════════
    推广文案示例
═══════════════════════════════════════════

## 摸鱼中

### 文案内容
打工人必备摸鱼指南！这套表情包含超实用的摸鱼技巧，让你在职场中游刃有余，享受带薪摸鱼的快乐！

### 推荐标签
#微信表情 #摸鱼神器 #打工人必备 #职场生存 #摸鱼技巧 #赛博朋克 #表情包 #斗图

═══════════════════════════════════════════
```

## 公众号发布

当需要通过微信公众号发布贴图内容时，可生成以下规格的图片：

### 图片规格

| 类型 | 尺寸 | 宽高比 | 文件大小 | 格式 | 用途 |
|-----|------|-------|---------|------|------|
| 头图封面 | 900×383px | 2.35:1 | ≤2MB | JPG/PNG | 文章封面 |
| 正文配图 | 1080×607px | 16:9 | ≤2MB | JPG/PNG/GIF | 内容展示 |
| 小图/缩略图 | 200×200px | 1:1 | 无限制 | PNG/SVG | 预览/缩略 |
| **小绿书图片** | 1080×1440px | **3:4** | ≤10MB | JPG/PNG | **单独图片消息（最佳）** |

### 小绿书图片（最佳选择）

小绿书是微信推出的图片消息形式，适合单独发布贴图内容展示，类似小红书笔记风格：

```bash
# 生成小绿书格式图片
python3 generate_cover.py --output assets/xhs-post.png \
  --title "贴图名称" \
  --subtitle "描述文案（最长300字）" \
  --theme cyberpunk \
  --type xiaolvshu
```

**规格说明**：
- **最佳比例**: 3:4（竖版）
- **推荐尺寸**: 1080×1440px
- **描述文案**: 支持最长 300 字
- **适用场景**: 单独发布图片消息，类似小红书笔记风格

### 其他图片生成

```bash
# 生成公众号头图封面
python3 generate_cover.py --output assets/cover.png \
  --title "表情包主题" --theme cyberpunk --type wechat-cover

# 生成正文配图
python3 generate_cover.py --output assets/content.png \
  --title "贴图名称" --width 1080 --height 607

# 生成缩略图
python3 generate_cover.py --output assets/thumb.png \
  --title "名称" --width 200 --height 200
```

### 排版建议

1. **小绿书（推荐）**: 使用 1080×1440 的 `xhs-post-*.png`，单独发布图片消息
2. **封面图**: 使用 900×383 的 `cover.png`，文章封面
3. **正文**: 每张贴图配合 1080×607 的 `content-*.png` 展示
4. **缩略图**: 用于文末汇总展示，200×200 格式统一

## 项目初始化

当用户说"做微信贴图"后，按以下步骤创建项目：

```bash
# 1. 创建项目根目录
mkdir -p wechat-stickers/{topic-slug}/prompts

# 2. 生成 prompts/ 贴图提示词文件（由 AI 自动生成）
# 3. 运行图片生成
python3 generate_frames.py \
  --input wechat-stickers/{topic-slug}/prompts/ \
  --output wechat-stickers/{topic-slug}/assets-{theme}/ \
  --theme cyberpunk
```

**目录结构**：
```
wechat-stickers/{topic-slug}/
├── prompts/           ← 贴图提示词（AI 生成）
├── assets-cyberpunk/  ← 生成的图片（.png 或 .gif）
├── remotion-sticker/  ← Remotion 项目（保留，可调整动画）
├── content-analysis.md
└── sticker-manifest.md
```

## 技术规格

- **图片尺寸**: 1080×1440 像素（微信贴图标准）、900×383 像素（公众号封面）
- **文件格式**: PNG（AI/PIL 模式）或 GIF（Remotion 模式，90帧动画）
- **贴图数量**: 最少 6 张，建议 8-12 张为一套
- **文案长度**: 每张贴图核心文案 8-16 字
- **标签数量**: 每张贴图至少 5 个标签
- **图片生成**: AI API（优先）或 PIL 本地生成（兜底）

## 安装指南

## 常见问题

### Q: 网络搜索失败怎么办？

A: 工具会自动跳过搜索步骤，直接使用原始输入进行内容聚合。

### Q: AI API 不可用怎么办？

A: 工具会自动切换到本地 PIL 生成模式，确保图片能够正常生成。

### Q: 可以生成多少张贴图？

A: 最少 3 张，建议 6-12 张为一套完整的表情包。

### Q: 支持哪些图片格式？

A: 生成 PNG 格式，透明背景，符合微信表情包标准。

### Q: 文案会自动生成吗？

A: 是的，每张贴图都会自动生成推广文案（20-50字）和标签（至少5个）。

### Q: 默认风格是什么？

A: 默认使用赛博朋克风格，也支持其他风格如可爱、简约、表情包等。

## 安装指南

本技能支持在多种 AI 工具中安装使用。

### 通用安装方式

**无需 npm/npx**，Skills 只是 Markdown 文档，只需复制到对应目录即可：

```bash
# 1. 克隆或下载本仓库
git clone https://github.com/zsy619/wechat-sticker-skill.git
cd wechat-sticker-skill

# 2. 安装依赖（如需要 PIL 生成图片）
pip3 install Pillow

# 3. 复制到 skills 目录（见下方各工具说明）
```

### Trae IDE

在 Trae IDE 中安装本技能：

```bash
# 方法1：复制到用户 skills 目录
mkdir -p ~/.agents/skills
cp -r . ~/.agents/skills/wechat-sticker-skill

# 方法2：创建符号链接（推荐，修改后自动同步）
ln -sf "$(pwd)" ~/.agents/skills/wechat-sticker-skill
```

### Claude Code

在 Claude Code 中安装本技能：

```bash
# 安装到用户目录
mkdir -p ~/.claude/skills
git clone https://github.com/zsy619/wechat-sticker-skill.git ~/.claude/skills/wechat-sticker-skill

# 或手动复制
mkdir -p ~/.claude/skills/wechat-sticker-skill
cp -r . ~/.claude/skills/wechat-sticker-skill/
```

### Cursor IDE

在 Cursor 中安装本技能：

```bash
# 方法1：复制到 Cursor skills 目录
mkdir -p ~/.cursor/skills
cp -r . ~/.cursor/skills/wechat-sticker-skill

# 方法2：使用 Cursor CLI（如有）
cursor --install-skill wechat-sticker-skill
```

### Windsurf AI

在 Windsurf 中安装本技能：

```bash
# 复制到 Windsurf skills 目录
mkdir -p ~/.windsurf/skills
cp -r . ~/.windsurf/skills/wechat-sticker-skill
```

### Continue (VSCode/JetBrains 插件)

在 Continue 插件中安装本技能：

```json
// 在 .continue/config.json 中添加
{
  "skills": [
    {
      "name": "wechat-sticker-skill",
      "description": "根据链接、主题或内容自动生成微信表情包",
      "repo": "https://github.com/zsy619/wechat-sticker-skill"
    }
  ]
}
```

### 验证安装

安装完成后，在 AI 工具中输入以下触发词测试：

```
做微信贴图
创建微信表情包
根据内容生成贴图
```

## 相关链接

- 项目源码: [wechat-sticker-skill](https://github.com/zsy619/wechat-sticker-skill)

---

*本工具由 Claude Agent 驱动，自动完成从内容分析到贴图生成的全流程，包含文案和标签生成。*