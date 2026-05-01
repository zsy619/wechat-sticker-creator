# Remotion 帧设计规范

本文档定义如何使用 Remotion 为每张微信贴图生成高质量动画帧图像。

## 核心思路

每张贴图对应一个独立的 Remotion 项目。Remotion 在这里不是用来做视频，而是作为**代码驱动的精确绘图工具**——用 React + TypeScript 精确控制每个像素和动画帧。

**为什么不用 PIL？**
- PIL 是几何堆叠，视觉上限低
- Remotion 可以调用任意字体、使用精确的颜色空间、渲染 SVG 路径、实现动画曲线
- 可以精确控制每个元素的 `transform`、`opacity`、`filter`、`text-shadow`

## 实际项目结构

详见 [remotion-projects.md](remotion-projects.md)，核心结构：
详见 [project-structure.md](project-structure.md)。

## 组件设计原则

### 三层架构

```
registerRoot(StickerComponent)      ← 入口（第1层）
    ↓
StickerComponent                   ← 外层包装（第2层）
    ↓ 返回 <Composition>
    component={StickerContent}
    durationInFrames={90}         ← 动画帧数（3秒@30fps）
    fps={30}
    ↓
StickerContent                    ← 实际视觉（第3层）
    ↓
    useCurrentFrame() + 动画
```

### 外层组件规则（StickerComponent）

- **不**使用 `useCurrentFrame()`
- 必须返回 `<Composition>` 并指定 `component={StickerContent}`
- `durationInFrames={90}`（**GIF动画需要90帧**，非1帧）
- `fps={30}`，`id` 必须与 `registerRoot` 组件名一致

### 内层组件规则（StickerContent）

- **必须**使用 `useCurrentFrame()` 获取当前帧
- 动画函数（`spring`, `interpolate`）需要显式传入 `fps` 参数
- 所有样式用内联 `style`（Remotion 不支持 CSS module）

### spring() 正确用法

```tsx
// ✅ 正确：显式传入 fps
const glowOpacity = interpolate(
  spring({ frame, fps: FPS, config: { damping: 200, stiffness: 10 } }),
  [0, 1], [0.4, 1]
);

// ❌ 错误：缺少 fps 参数
spring({ frame, config: { damping: 200, stiffness: 10 } })
// → TypeError: "fps" must be a number
```

### JSX 属性语法 & 双括号转义

JSX 中 `style={...}` 的 `{}` 是 JSX 表达式语法。**当值本身包含花括号时，需要双写 `{{}}`**：

```tsx
// ✅ 正确：JSX style prop 中 value 是 JS 对象 → 双括号
<div style={{display:'flex', gap:40, fontSize:260}}>

// ❌ 错误：单括号会让 JSX 把 {display:'flex'...} 当作表达式求值
<div style={display:'flex', gap:40}>  // 语法错误

// ✅ 在 Python 生成的 emojis_html 中，所有 style= 都要用双括号
span_base = "{{fontSize:260,lineHeight:1,filter:`drop-shadow(...)`}}"
```

Python 脚本生成 emoji HTML 时的正确写法：

```python
# ❌ 错误：f-string 的 {{ 在 f-string 外只算一个 {
emojis_html += f'  <span style={{fontSize:260}}>{em}</span>\n'

# ✅ 正确：使用字符串拼接完全避免 f-string 歧义
span_base = "{{fontSize:260,lineHeight:1}}"
emojis_html += "  <span style=" + span_base + ">" + em + "</span>\n"
```

### render 命令（GIF 输出）

| 输出格式 | 命令 |
|---------|------|
| ~~still~~ | ~~`remotion still`~~ |
| **GIF** | `npx remotion render src/index.tsx StickerComponent --output out.gif --frames 0-89 --fps 30` |

> **注意**：`remotion still` 只导出单帧 PNG，且不支持 GIF 输出。所有贴图默认使用 `remotion render` 生成90帧动画。

## 主题配色注入

通过 Python 脚本将主题色注入到 TSX 文件：

| 主题 | primary | secondary | bg | text |
|------|---------|-----------|----|------|
| cyberpunk | #00FFFF | #FF00FF | #0D0D1A | #FFFFFF |
| kawaii | #FF69B4 | #FFB6C1 | #FFF0F5 | #4A4A4A |
| neon | #FF00FF | #00FFFF | #1A0033 | #FFFFFF |
| retro | #FFD700 | #FF6347 | #2D1B00 | #FFFFFF |
| hand-drawn | #8B4513 | #DEB887 | #FFF8DC | #4A4A4A |
| minimal | #333333 | #666666 | #FFFFFF | #333333 |
| meme | #FFFF00 | #FF6600 | #000000 | #FFFFFF |

## 视觉元素词汇表

在 `StickerContent` 中通过 `visual_elements` 驱动 emoji 渲染。每个 prompt 文件的 `visual_elements` 字段直接对应 emoji：

| 元素键 | emoji | 说明 |
|-------|-------|------|
| brain / ai计算 / 神经网络 | 🧠 | AI/大脑/神经网络 |
| terminal / 终端窗口 | 💻 | 终端/代码相关 |
| lightning / 闪电 | ⚡ | 速度/能量相关 |
| heart / 红心 | ❤ | 点赞/喜欢相关 |
| equals_sign / 等号 | ＝ | 数学/计算相关（等号用全角符号避免 JSX 语法冲突） |
| question_mark / 问号 | ？ | 疑问/探索相关 |
| eraser / 橡皮擦 | 🧹 | 清除/重置相关 |
| checkmark / 对勾 | ✓ | 完成/正确相关 |
| math_canvas / canvas / 画布 | 📐 | 画布/绘制相关 |
| ai_chip / 芯片 | 🤖 | AI芯片/硬件相关 |

**prompt 写法示例**（`prompts/01-画布手写.md`）：
```yaml
---
name: 画布手写
copy: 随手一画，AI帮你算
visual_elements: [math_canvas, brain, equals_sign]
style_keyword: [cyberpunk, neon, tech-modern]
theme: cyberpunk
---
```

## 动画效果系统

### 全部动画函数（在 StickerContent 内层组件中定义）

```tsx
// 1. 呼吸发光（核心动画）
const glowOpacity = interpolate(
  spring({ frame, fps: FPS, config: { damping: 200, stiffness: 10 } }),
  [0, 1], [0.4, 1]
);

// 2. 脉冲缩放
const scale = interpolate(frame, [0, 15, 30], [1, 1.06, 1], {
  extrapolateRight: 'clamp',
});

// 3. 浮空动画
const floatY = interpolate(frame, [0, 30], [0, -18], {
  extrapolateRight: 'clamp',
});

// 4. 文字闪烁（快速微妙闪烁）
const textFlash = interpolate(frame, [0, 8, 15, 22, 30], [1, 0.85, 1, 0.9, 1], {
  extrapolateRight: 'clamp',
});

// 5. 外发光强度动画（光晕呼吸）
const outerGlow = interpolate(frame, [0, 15, 30], [1, 1.4, 1], {
  extrapolateRight: 'clamp',
});
```

### 5层霓虹 text-shadow 特效

```tsx
textShadow: `
  /* 第1层：外扩散光晕（最外层，大范围低透明度）*/
  0 0 ${20*outerGlow}px ${PRIMARY}60,
  0 0 ${40*outerGlow}px ${PRIMARY}40,
  0 0 ${60*outerGlow}px ${PRIMARY}25,
  0 0 ${80*outerGlow}px ${PRIMARY}15,
  /* 第2层：中距离光晕（副色）*/
  0 0 ${12*outerGlow}px ${SECONDARY}80,
  0 0 ${24*outerGlow}px ${SECONDARY}50,
  /* 第3层：紧密辉光（主色高透明度）*/
  0 0 ${6*outerGlow}px ${PRIMARY}cc,
  0 0 ${10*outerGlow}px ${PRIMARY}99,
  /* 第4层：超近辉光（白色高亮）*/
  0 0 ${3*outerGlow}px rgba(255,255,255,0.9),
  /* 第5层：黑色阴影（立体感）*/
  3px 3px 0 rgba(0,0,0,0.9),
  4px 4px 8px rgba(0,0,0,0.7)
`
```

### 文字渐变填充

```tsx
style={{
  // 渐变色从白色过渡到主色
  background: `linear-gradient(180deg, #FFFFFF 0%, ${PRIMARY} 100%)`,
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  backgroundClip: 'text',
}}
```

### 文字闪烁 + 缩放同步

```tsx
style={{
  opacity: textFlash,
  transform: `scale(${1 + (1 - textFlash) * 0.05})`,
  // ... 其他样式
}}
```

## Emoji 注入点 `__ELEMENTS_HTML__`

在 `StickerContent.tsx` 模板中，`__ELEMENTS_HTML__` 占位符被替换为 emoji JSX 元素：

```tsx
<div style={{
  opacity: glowOpacity,
  transform: `scale(${scale}) translateY(${floatY}px)`,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  position: 'relative',
  zIndex: 2,
}}>
  {/* emoji 元素（由 generate_frames.py 注入） */}
  __ELEMENTS_HTML__
</div>
```

Python 注入的 HTML 格式（确保双括号）：

```python
div_style = "{{display:'flex',gap:40,alignItems:'center',justifyContent:'center'}}"
span_base = "{{fontSize:260,lineHeight:1,filter:`drop-shadow(0 0 " + PRIMARY + ") drop-shadow(0 0 80px " + SECONDARY + "80)`}}"
emojis_html = "        <div style=" + div_style + ">\n"
for em in emojis:
    emojis_html += "          <span style=" + span_base + ">" + em + "</span>\n"
emojis_html += "        </div>\n"
```

## 样式隔离

Remotion 组件样式必须用**内联 style**，不使用 CSS class（因为是代码驱动的静态渲染）：

```tsx
// ✅ 内联 style
<div style={{
  width: 1080, height: 1440,
  background: '#0D0D1A',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}}>

// ❌ CSS class（不被支持）
<div className="container">
```

`styles.css` 只用于最基础的全局样式（如 `body { margin: 0 }`）。

## 输出规格

| 参数 | 值 |
|------|-----|
| 分辨率 | 1080 × 1440（9:16 竖屏） |
| 帧数 | **90帧**（3秒@30fps） |
| 格式 | **GIF**（动画） |
| fps | 30 |

## 故障排查

| 错误 | 原因 | 修复 |
|------|------|------|
| `useCurrentFrame() can only be called...` | inner 组件未通过 `<Composition>` 注册 | 确认 outer 组件返回 `<Composition component={inner}>` |
| `fps" must be a number` | `spring()` 缺少 `fps` 参数 | `spring({ frame, fps: FPS, config: {...} })` |
| `Expected "{" but found "1"` | JSX 属性裸数字 | `fps={30}` 而非 `fps=30` |
| `delayRender() timeout` | 版本不一致 | `package.json` 固定 `"remotion": "4.0.448"` |
| `import React from 'remotion'` | React 导入错误 | `import React from 'react'` |
| GIF 导出为黑色/空白 | `__COPY__` 或 `__ELEMENTS_HTML__` 未正确替换 | 检查 `parse_prompt_file` frontmatter 解析；检查 JSX 双括号 |
| emoji 不显示 | `visual_elements` 中的 key 不在 emoji_map | 确认 prompt 的 `visual_elements` 使用词汇表中的 key（如 `brain` 而非 `AI大脑`） |
