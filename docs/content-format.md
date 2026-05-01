# 内容格式文档

本文档定义贴图项目中各类格式规范。

---

## 内容聚合分析 (content-analysis.md)

项目创建后，首先进行内容聚合分析，生成 `content-analysis.md`。

### 输入来源

- **URL链接**：使用 `baoyu-url-to-markdown` 提取页面内容
- **主题词**：使用 `WebSearch` 联网搜索相关内容
- **内容文本**：直接使用输入内容

### 内容获取

```bash
# URL 链接
baoyu-url-to-markdown --url "https://github.com/ayushpai/AI-Math-Notes"

# 主题词搜索
WebSearch "AI Math Notes Apple WWDC 2024"
```

### 核心主题

从内容中提取核心主题，形成 1-2 句话概括。

### 关键概念

列出 5-10 个与主题相关的关键概念。

### 情感基调

- **轻松幽默**：适合娱乐类贴图
- **专业干练**：适合工具/科技类贴图
- **温暖治愈**：适合生活/情感类贴图
- **酷炫潮流**：适合时尚/科技类贴图

### 使用场景

列出 3-5 个典型使用场景。

### 热点趋势

通过搜索了解当前热点和趋势。

### 贴图设计方向

根据以上分析，给出贴图设计的整体方向建议。

---

## 贴图设计清单 (sticker-manifest.md)

每套贴图设计 6 张（最常见数量），覆盖不同使用场景：

### 贴图类型定义

| 序号 | 名称 | 使用场景 |
|------|------|---------|
| 01 | {场景1} | 开场/引入 |
| 02 | {场景2} | 核心功能展示 |
| 03 | {场景3} | 操作/使用中 |
| 04 | {场景4} | 结果/完成 |
| 05 | {场景5} | 意外/趣味 |
| 06 | {场景6} | 收藏/标志 |

### Manifest 文件格式（v3.0）

```yaml
# 贴图设计清单

## 贴图1: {sticker-name}

- **序号**: 01
- **名称**: {sticker-name}
- **使用场景**: {场景描述}
- **核心文案**: {copy}
- **视觉元素**: [元素1, 元素2, 元素3]
- **风格**: {style_keyword}

## 贴图2: {sticker-name}

...

## 标签汇总

- 平台标签: #微信表情 #微信贴图 #WeChatStickers
- 情感标签: {根据内容确定}
- 主题标签: {根据内容确定}
```

### 贴图命名规则

- 格式：`{num}-{name}.md`，如 `01-画布手写.md`
- 名称使用中文，简洁明了
- 序号固定2位数字

---

## 提示词生成 (prompts/*.md)

每张贴图对应一个 `prompts/{num}-{name}.md` 文件：

### Prompt 格式（v3.0）

```yaml
---
name: 画布手写
copy: 随手一画，AI帮你算
visual_elements: [math_canvas, equals_sign, question_mark]
style_keyword: [cyberpunk, 赛博朋克, tech-modern]
theme: cyberpunk
aspect_ratio: "3:4"
---

## 视觉设计规则
- 中心：数学画布，深色背景
- 等号 + 问号气泡，等待动画
- 底部：核心文案居中显示

## 风格要求
- 主色：青色 (#00FFFF)
- 背景：深空黑 (#0D0D1A)
- 光效：霓虹发光

## 文字展示
- 位置：画布底部居中
- 字体：PingFang SC, 110px
- 颜色：白色
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 贴图中英文标识 |
| `copy` | ✅ | 核心文案（≥10字） |
| `visual_elements` | ✅ | 视觉元素列表 |
| `style_keyword` | ✅ | 风格关键词 |
| `theme` | ✅ | 主题键 |
| `aspect_ratio` | ✅ | 宽高比（3:4） |

### visual_elements 词汇表

**FOCUS 元素**（适合居中放大）：

| 关键词 | 说明 |
|--------|------|
| `brain` / `ai大脑` | AI大脑图标 |
| `ai计算` | AI计算 |
| `神经网络` / `neural_network` | 神经网络节点图 |
| `terminal` / `终端窗口` | 终端窗口 |
| `math_canvas` / `canvas` / `画布` | 数学画布 |
| `equals_sign` / `等号` | 等号 |
| `command_k` / `⌘k` | ⌘K 按键 |
| `lightning` / `闪电` | 闪电符号 |
| `ai_chip` / `芯片` | AI芯片 |

**ACCENT 元素**（适合小尺寸散布）：

| 关键词 | 说明 |
|--------|------|
| `heart` / `红心` | 红心 |
| `question_mark` / `问号` | 问号气泡 |
| `checkmark` / `对勾` | 对勾 |
| `spotlight` / `光晕` | 聚光灯/光晕 |
| `network_node` / `节点` | 节点 |
| `eraser` / `橡皮擦` | 橡皮擦 |
| `button` / `按钮` | 按钮 |

### style_keyword 主题映射

```tsx
const THEMES = {
  cyberpunk:  { primary: '#00FFFF', secondary: '#FF00FF', bg: '#0D0D1A', text: '#FFFFFF', accent: '#00FF88' },
  kawaii:     { primary: '#FF69B4', secondary: '#FFB6C1', bg: '#FFF0F5', text: '#4A4A4A', accent: '#FF1493' },
  neon:       { primary: '#FF00FF', secondary: '#00FFFF', bg: '#1A0033', text: '#FFFFFF', accent: '#FF69B4' },
  retro:      { primary: '#FFD700', secondary: '#FF6B35', bg: '#2D1B00', text: '#FFFFFF', accent: '#FF4500' },
  'hand-drawn': { primary: '#8B4513', secondary: '#D2691E', bg: '#FFF8DC', text: '#4A4A4A', accent: '#CD853F' },
  minimal:    { primary: '#212529', secondary: '#495057', bg: '#F8F9FA', text: '#212529', accent: '#6C757D' },
  meme:       { primary: '#FF4500', secondary: '#FFD700', bg: '#1A1A1A', text: '#FFFFFF', accent: '#FF6347' },
};
```

### 解析脚本（v4.1+）

> ⚠️ **注意**：原 `eval()` 解析无法处理中文词（如 `[黑色画布, 数学公式]`），已被 `_parse_list()` 替代。

```python
def _parse_list(s):
    """解析逗号分隔的非引号列表：[a, b, c] → ['a','b','c']"""
    s = s.strip()
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1]
    return [x.strip() for x in s.split(',') if x.strip()]

def parse_prompt_file(path):
    with open(path) as f:
        content = f.read()
    front = {}
    in_front = False
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped == '---':
            if not in_front: in_front = True  # 跳过开头的 ---
            else: break                         # 遇到第二个 --- → 结束
            continue
        if in_front and ':' in line:
            k, v = line.split(':', 1)
            front[k.strip()] = v.strip().strip('"').strip("'")
    name  = front.get('name', os.path.basename(path).replace('.md',''))
    copy  = front.get('copy', '')
    try:    visual_elements = _parse_list(front.get('visual_elements', '[]'))
    except: visual_elements = []
    try:    style_keyword = _parse_list(front.get('style_keyword', '[]'))
    except: style_keyword = []
    theme = front.get('theme', 'cyberpunk')
    return name, copy, visual_elements, style_keyword, theme
```

### 常用 visual_elements 组合示例

```yaml
# 画布手写：画布 + AI大脑 + 等号
visual_elements: [math_canvas, brain, equals_sign]

# AI计算：AI大脑 + 神经网络 + 芯片
visual_elements: [brain, neural_network, ai_chip]

# 等号求解：等号 + 问号 + AI
visual_elements: [equals_sign, question_mark, brain]

# 清空重写：橡皮擦 + 问号 + AI
visual_elements: [eraser, question_mark, brain]


# 答案揭晓：等号 + AI + 对勾
visual_elements: [equals_sign, brain, checkmark]
```

---

## Remotion 帧设计（frame-design.md）

> 详见 [frame-design.md](frame-design.md) 独立文档。

每张贴图对应一个 Remotion `<Still>` 组件，用代码精确控制每一帧的视觉元素。

### 设计原则

1. **独特性**：每帧根据贴图主题单独设计视觉元素
2. **精细化**：字体、颜色、位置、动画曲线均可精确控制
3. **导出PNG**：通过 `npx remotion still` 导出单帧图像

### 项目结构

```
remotion/{sticker-name}/
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

### 导出命令

```bash
npx remotion still src/Root.tsx {CompositionId} \
  --output out/{sticker-name}.png \
  --width 1080 --height 1440
```

详见 [frame-design.md](frame-design.md)。
