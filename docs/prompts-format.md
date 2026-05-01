# 贴图 Prompt 生成规范（完整版）

本文档定义 `prompts/{num}-{name}.md` 的完整写法，涵盖 frontmatter 字段规范、正文结构、视觉元素词汇表、主题配色、字体特效描述。

---

## 一、文件命名

```
prompts/
├── 01-{贴图名}.md     ← 格式：序号-中文名
├── 02-{贴图名}.md
└── 03-{贴图名}.md
```

- 序号从 01 开始，不足两位补零
- 文件名只用中文，不含空格和英文（如 `01-画布手写.md`）
- 每个 prompt 文件对应一张贴图

---

## 二、文件结构

```markdown
---
name: {贴图中英文标识}
copy: {核心文案}
visual_elements: [{元素1}, {元素2}, {元素3}]
style_keyword: [{风格词1}, {风格词2}]
theme: {主题键}
---

# {贴图标题}

## 核心文案（必须展示在贴图中）
{核心文案全文}

## 视觉设计规则

### 主体
{主体描述：有什么视觉元素，它们的关系}

### 风格要求
- 主题：{主题描述}
- 主色：{十六进制颜色}（{颜色名}）
- 副色：{十六进制颜色}（{颜色名}）
- 背景：{十六进制颜色}
- 文字：{颜色描述}

### 动画
- {动画效果描述}

### 文字展示
- 核心文案：{核心文案}
- 字体：{字体名}，{字号}px
- 位置：{位置描述}
- 效果：{效果描述}
```

---

## 三、Frontmatter 字段详解

### 3.1 `name` — 贴图标识

| 规则 | 说明 |
|------|------|
| 格式 | 中文，建议2-4字 |
| 用途 | 生成文件名和贴图标题 |
| 示例 | `name: 画布手写` |

### 3.2 `copy` — 核心文案

| 规则 | 说明 |
|------|------|
| 字数 | 建议8-16字（微信文案上限） |
| 语言 | 中文为主 |
| 内容 | 表达贴图的使用场景或情感 |
| 样式 | 短促有力、口语化、适合当表情包文案 |
| 示例 | `copy: 随手一画，AI帮你算` |

**copy 写作原则**：
- ✅ 有画面感（"随手一画"比"开始计算"更有画面）
- ✅ 有情感钩子（"AI帮你算"暗示省力）
- ❌ 不要太正式（"正在进行数学运算"太严肃）
- ❌ 不要超20字（微信限制）
- ❌ 不要纯描述（"这是等号"没有情绪）

**常见 copy 类型**：

| 类型 | 示例 | 适用场景 |
|------|------|---------|
| 动作类 | 随手一画，AI帮你算 | 画布手写 |
| 结果类 | AI一画答案就出来咯 | AI计算 |
| 等待类 | 写完等号等答案出来 | 等号求解 |
| 感叹类 | Apple看了也说绝 | MathNotes |
| 情绪类 | 不对不对全部清掉 | 清空重写 |
| 确认类 | AI算出答案是八没错 | 答案揭晓 |

### 3.3 `visual_elements` — 视觉元素列表

| 规则 | 说明 |
|------|------|
| 格式 | `[元素1, 元素2, 元素3]`（逗号分隔，**不用引号**） |
| 数量 | 推荐3个元素（太少无层次，太多显拥挤） |
| 键值 | **必须**使用 emoji 词汇表中的英文 key |
| 顺序 | 从左到右对应贴图中从左到右的 emoji 排列 |

**标准词汇表**：

| key（前端 yaml 写这个） | emoji | 含义 |
|----------------------|-------|------|
| `brain` | 🧠 | AI 大脑 / 神经网络 |
| `neural_network` | 🧠 | 神经网络节点 |
| `terminal` | 💻 | 终端窗口 |
| `math_canvas` | 📐 | 数学画布 |
| `equals_sign` | ＝ | 等号（全角，避免 JSX 冲突） |
| `question_mark` | ？ | 问号（全角） |
| `ai_chip` | 🤖 | AI 芯片 |
| `eraser` | 🧹 | 橡皮擦 |
| `checkmark` | ✓ | 对勾 |
| `lightning` | ⚡ | 闪电 |
| `heart` | ❤ | 红心 |
| `spotlight` | 🔦 | 光晕 |

**❌ 常见错误**（会导致 emoji 不显示）：
```yaml
# ❌ 错误：中文词不在词汇表中
visual_elements: [黑色画布, 白色手写笔迹, 数学公式]

# ✅ 正确：使用英文 key
visual_elements: [math_canvas, brain, equals_sign]
```

**元素组合原则**：
- 第一个元素：视觉焦点（如 `brain` 最常见作为主视觉）
- 最后一个元素：收尾（如 `checkmark` 表示完成感）
- 中间元素：辅助说明（如 `question_mark` 增加等待感）

### 3.4 `style_keyword` — 风格关键词

| 规则 | 说明 |
|------|------|
| 格式 | `[{风格词1}, {风格词2}]` |
| 作用 | 传给 AI 图像生成 API（用于 AI 生成模式） |
| 数量 | 2-3个词 |
| 常用词 | cyberpunk / neon / kawaii / retro / hand-drawn / minimal / meme |

### 3.5 `theme` — 主题键

| 规则 | 说明 |
|------|------|
| 格式 | 对应 THEMES 对象中的 key |
| 值域 | `cyberpunk` / `kawaii` / `neon` / `retro` / `hand-drawn` / `minimal` / `meme` |
| 作用 | 决定配色方案、字体发光颜色 |

**各主题配色**：

| theme | primary | secondary | bg | text |
|-------|---------|-----------|----|------|
| cyberpunk | #00FFFF | #FF00FF | #0D0D1A | #FFFFFF |
| kawaii | #FF69B4 | #FFB6C1 | #FFF0F5 | #4A4A4A |
| neon | #FF00FF | #00FFFF | #1A0033 | #FFFFFF |
| retro | #FFD700 | #FF6B35 | #2D1B00 | #FFFFFF |
| hand-drawn | #8B4513 | #DEB887 | #FFF8DC | #4A4A4A |
| minimal | #333333 | #666666 | #FFFFFF | #333333 |
| meme | #FFFF00 | #FF6600 | #000000 | #FFFFFF |

---

## 四、正文结构详解

### 4.1 标题行

```
# {num}-{贴图名}
```

如 `# 01-画布手写`，与文件名保持一致。

### 4.2 核心文案节

```markdown
## 核心文案（必须展示在贴图中）
随手一画，AI帮你算
```

- 必须包含完整核心文案，与 frontmatter 的 `copy` 字段一致
- 用于 body 展示（优先级高于 frontmatter）

### 4.3 主体描述

```markdown
### 主体
深色背景 + 居中显示 📐画布 + 🧠AI大脑 + ＝等号符号
三元素横向排列，霓虹发光滤镜，底部140px白色文案居中
```

**描述要素**：
1. **背景**（颜色/效果）
2. **主体元素**（emoji + 排列方式）
3. **光效/滤镜**
4. **文案位置**

### 4.4 风格要求

```markdown
### 风格要求
- 主题：cyberpunk / tech-modern
- 主色：#00FFFF（霓虹青）
- 副色：#FF00FF（品红）
- 背景：深色 #0D0D1A
- 文字：白色，底部居中
```

### 4.5 动画描述

```markdown
### 动画
- 呼吸发光：opacity 0.4→1 脉冲
- 脉冲缩放：scale 1→1.06→1
- 浮空动效：translateY 浮起
```

**可描述的动画维度**：
- `opacity`：明暗呼吸
- `scale`：缩放脉冲
- `translateY`：上下浮动
- `filter`：发光/模糊变化
- `textShadow`：霓虹扩散

### 4.6 文字展示

```markdown
### 文字展示
- 核心文案：随手一画，AI帮你算
- 字体：PingFang SC，140px
- 位置：画布底部居中
- 效果：霓虹发光 text-shadow 多层青色
```

---

## 五、完整示例

### 示例一：画布手写

```markdown
---
name: 画布手写
copy: 随手一画，AI帮你算
visual_elements: [math_canvas, brain, equals_sign]
style_keyword: [cyberpunk, neon, tech-modern]
theme: cyberpunk
---

# 01-画布手写

## 核心文案（必须展示在贴图中）
随手一画，AI帮你算

## 视觉设计规则

### 主体
深色背景 + 居中显示 📐画布 + 🧠AI大脑 + ＝等号符号
三元素横向排列，霓虹发光滤镜，底部140px白色文案居中

### 风格要求
- 主题：cyberpunk / tech-modern
- 主色：#00FFFF（霓虹青）
- 副色：#FF00FF（品红）
- 背景：深色 #0D0D1A
- 文字：白色，底部居中

### 动画
- 呼吸发光：opacity 0.4→1 脉冲
- 脉冲缩放：scale 1→1.06→1
- 浮空动效：translateY 浮起

### 文字展示
- 核心文案：随手一画，AI帮你算
- 字体：PingFang SC，140px
- 位置：画布底部居中
- 效果：霓虹发光 text-shadow 多层青色
```

### 示例二：答案揭晓

```markdown
---
name: 答案揭晓
copy: AI算出答案是八没错
visual_elements: [equals_sign, brain, checkmark]
style_keyword: [cyberpunk, neon, success]
theme: cyberpunk
---

# 06-答案揭晓

## 核心文案（必须展示在贴图中）
AI算出答案是八没错

## 视觉设计规则

### 主体
深色背景 + 居中显示 ＝等号 + 🧠AI + ✓对勾
三元素横向排列，青色+橙色双重发光，底部140px白色文案居中

### 风格要求
- 主题：cyberpunk / tech-modern
- 主色：#FF8C00（橙色答案）
- 副色：#00FFFF（霓虹青）
- 背景：深色 #0D0D1A
- 文字：白色，底部居中

### 动画
- 呼吸发光：opacity 0.4→1 脉冲
- 脉冲缩放：scale 1→1.06→1
- 浮空动效：translateY 浮起

### 文字展示
- 核心文案：AI算出答案是八没错
- 字体：PingFang SC，140px
- 位置：画布底部居中
- 效果：霓虹发光 text-shadow 多层橙色
```

---

## 六、自检清单

生成每个 prompt 后，按以下清单逐项检查：

- [ ] `name`：中文，2-4字
- [ ] `copy`：8-16字，口语化，有画面感
- [ ] `visual_elements`：3个，使用英文 key，不含中文词
- [ ] `visual_elements` 的 key 都在词汇表中
- [ ] `theme`：必须是7个主题键之一
- [ ] frontmatter 后有 `---` 闭合行
- [ ] body 中有 `## 核心文案` 节
- [ ] body 中有 `## 视觉设计规则` 节
- [ ] 主体描述包含：背景 + 元素 + 位置
- [ ] 风格要求标注主色/副色/背景色
- [ ] 动画描述列出具体参数
- [ ] 文字展示标注字号≥120px（竖屏大字）

---

## 七、常见错误汇总

| 错误类型 | 错误写法 | 正确写法 |
|---------|---------|---------|
| visual_elements 含中文 | `[黑色画布, AI大脑]` | `[math_canvas, brain]` |
| visual_elements 用了 `=` | `[brain, =, question]` | `[brain, equals_sign, question_mark]` |
| copy 太长 | `copy: 这个数学公式计算结果是八` | `copy: AI算出答案是八没错` |
| copy 缺情绪 | `copy: 计算结果为8` | `copy: AI算出答案是八没错` |
| theme 拼写错误 | `theme: cyberpunk` | `theme: cyberpunk` |
| 元素数量过多 | `[brain, brain, brain, brain]` | `[brain, brain, brain]` |
| 缺少闭合 `---` | 无 | frontmatter 末行 `---` |
| emoji 不在词汇表 | `[robot, computer]` | `[ai_chip, terminal]` |


---

## 八、Session Log 关联记录

每个项目的 `docs/session-log.md` 记录 Token 消耗，prompt 本身不需要写 token 信息。

**模板示例**（见 [session-log.md 模板](#session-log-记录规范)）：

| 阶段 | 输入 | 输出 | 合计 |
|------|------|------|------|
| 内容聚合分析 | N | N | N |
| sticker-manifest | N | N | N |
| prompts × N | N | N | N |
| **总计** | **N** | **N** | **N** |

