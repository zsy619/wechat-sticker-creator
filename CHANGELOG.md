# Changelog - wechat-sticker-skill

## v4.3.0 (2026-05-01) - 三段式生成器全面完善

### generate_frames.py 核心修复

**T-1 修复**：
- 新增 `seedream` provider（火山引擎 doubao-seedream-5-0-260128），支持 `VOLCENGINE_API_KEY` / `SEEDREAM_API_KEY` 环境变量
- 新增 `_call_ai_provider()` 统一 HTTP 调用函数：429 自动重试（10s 等待，最多3次）、超时/网络错误降级、401/402/403 认证错误跳过
- Provider 优先级：dashscope → seedream → minimax → openai

**T-3 修复**：
- `elem_fns` 扩充至 22 个绘制函数，新增 `code`（代码窗口）、`algorithm`（流程图）、`function`（ƒ(x)=）、`variable`（x=???）、`bio`（DNA双螺旋）、`secret`（*** + CLASSIFIED）
- 新增 `emoji_map` 兜底渲染逻辑，覆盖 80+ 词汇表所有 emoji 元素
- 移除原有的 `if True else None` 冗余表达式

### scripts/pil_fallback.py 独立脚本新建

**T-2 新建**：
- 创建独立 `pil_fallback.py` 脚本，与 `generate_frames.py` 解耦
- 支持 `--input/--output/--theme` 参数
- 内嵌完整 `elem_fns` + `emoji_map`，覆盖全部 80+ 词汇
- 可独立运行：`python3 scripts/pil_fallback.py --input prompts/ --output assets/ --theme cyberpunk`

### image-generation.md 文档修复

**T-4 修复**：
- 修正标题从"导出 PNG"改为"导出 GIF（带动画）"
- 添加说明：`npx remotion still` 导出单帧 PNG，`npx remotion render` 导出多帧 GIF

### StickerContent.tsx 清理

**T-5 修复**：
- 移除外层组件中冗余的 `useCurrentFrame()` 调用
- 注释更新为"不直接参与动画"，明确职责划分

### 演示项目

**T-6 新建**：
- 新建 `demo/ai-coding-assistant/` 完整贴图项目（6张贴图）
- `content-analysis.md` + `sticker-manifest.md` + `prompts/01-06.md` + `copy.md` + `assets/` 完整闭环
- 覆盖场景：代码秒写 / Bug秒解 / 一键部署 / 代码审查通过 / 摸鱼被发现 / 下班收工
- PIL 生成验证通过：6/6 张贴图全部成功

---

## v4.2.0 (2026-05-01) - Remotion 模板修复

### StickerContent.tsx 架构修复

**问题**：原模板外层组件直接调用 `useCurrentFrame()` 但实际动画逻辑在子组件中，职责不清。

**修复**：
- `StickerScene` 内层组件独立使用 `useCurrentFrame()`，通过 `frameOffset` 修正本地帧
- 外层 `StickerContent` 保持 `useCurrentFrame()` 调用以满足 Remotion 要求，但不直接参与动画
- `localFrame = frame - frameOffset` 确保每张贴图从第0帧开始播放

### 字体大小修复

**问题**：底部文案 `fontSize: 150` 对 1080px 宽度过大。

**修复**：调整为 `fontSize: 90`（竖屏规范 ≤96px）。

### 圆形遮罩添加

**问题**：cyberpunk/neon/kawaii 主题缺少圆形边框效果。

**修复**：添加圆形遮罩层，带 `boxShadow` 霓虹光效。

### text-shadow 修复

**问题**：原 `neonTextShadow` 函数使用模板字符串插值 `${PRIMARY}`，在某些场景下可能出现解析错误。

**修复**：改用字符串拼接，确保颜色值正确注入。

---

## v4.1.0 (2026-05-01) - GIF 动画 & 字体特效

### 重大变更：PNG → GIF 动画

所有贴图输出格式从静态 PNG 升级为动态 GIF：

| 项目 | 原值 | 新值 |
|------|------|------|
| 命令 | `remotion still` | `remotion render --frames 0-89` |
| 帧数 | 1 帧 | **90帧**（3秒@30fps） |
| 输出 | PNG (单帧) | **GIF**（动画） |
| `durationInFrames` | 1 | **90** |

### frontmatter 解析修复

`parse_prompt_file()` 之前在遇到第一个 `---` 后立即 break，导致 frontmatter 从未解析。修复为状态机：遇到第二个 `---` 才 break。

### `_parse_list()` 安全解析

`visual_elements: [黑色画布, 白色笔迹]` 中的中文词无法直接 `eval()`。新增 `_parse_list()` 函数手动解析逗号分隔数组，避免 NameError。

### emoji_map 键值标准化

`visual_elements` 中的 key 必须与 emoji_map 键完全匹配（中文 key → 英文 key）：

```yaml
# ✅ 正确
visual_elements: [math_canvas, brain, equals_sign]

# ❌ 错误（中文词不在 emoji_map 中）
visual_elements: [黑色画布, 白色手写笔迹, 数学公式]
```

### emoji 词汇表更新

| 元素键 | emoji | 备注 |
|-------|-------|------|
| brain / ai计算 / 神经网络 | 🧠 | |
| math_canvas / canvas / 画布 | 📐 | 新增 math_canvas |
| equals_sign / 等号 | ＝ | 使用全角符号避免 JSX `=` 语法冲突 |
| question_mark / 问号 | ？ | 使用全角符号 |
| ai_chip / 芯片 | 🤖 | |
| eraser / 橡皮擦 | 🧹 | |
| checkmark / 对勾 | ✓ | |
| neural_network | 🧠 | 新增 |
| terminal / 终端窗口 | 💻 | |
| lightning / 闪电 | ⚡ | |
| heart / 红心 | ❤ | |

### JSX 双括号转义

Python 生成 JSX HTML 时，`style={...}` 中的 `{}` 必须双写。修复方式：使用**字符串拼接**而非 f-string 插值。

```python
# ✅ 正确
span_base = "{{fontSize:260,lineHeight:1}}"
emojis_html += "  <span style=" + span_base + ">" + em + "</span>\n"

# ❌ 错误（f-string 中 {{ 仅为 {）
emojis_html += f'  <span style={{fontSize:260}}>{em}</span>\n'
```

### `__ELEMENTS_HTML__` 注入点修复

模板中 `__ELEMENTS_HTML__` 原来在 JSX 注释中，无法渲染。修复为直接嵌入 `<div>` 容器内的 JSX 元素。

### 动画效果系统（5个动画函数）

```tsx
// 1. 呼吸发光
const glowOpacity = interpolate(spring({...}), [0,1], [0.4,1]);

// 2. 脉冲缩放
const scale = interpolate(frame, [0,15,30], [1,1.06,1]);

// 3. 浮空动画
const floatY = interpolate(frame, [0,30], [0,-18]);

// 4. 文字闪烁
const textFlash = interpolate(frame, [0,8,15,22,30], [1,0.85,1,0.9,1]);

// 5. 外发光强度动画
const outerGlow = interpolate(frame, [0,15,30], [1,1.4,1]);
```

### 5层霓虹 text-shadow 系统

```tsx
textShadow: `
  0 0 20*outerGlow px PRIMARY60,   // 外扩散（4层）
  0 0 12*outerGlow px SECONDARY80, // 副色辉光（2层）
  0 0 6*outerGlow px PRIMARYcc,    // 主色紧密辉光
  0 0 3*outerGlow px rgba(255,255,255,0.9), // 白色高亮
  3px 3px 0 rgba(0,0,0,0.9)        // 黑色阴影
`
```

### 文字渐变填充

```tsx
background: `linear-gradient(180deg, #FFFFFF 0%, ${PRIMARY} 100%)`,
WebkitBackgroundClip: 'text',
WebkitTextFillColor: 'transparent',
backgroundClip: 'text',
```

---

## v4.0.1 (2026-04-30) - Remotion 修复

### Remotion 第二阶段问题修复（6个关键问题）

1. **@remotion/cli 3.3.0 ≠ remotion 4.0.448**：临时项目 package.json 需固定版本一致
2. **JSX 属性语法**：`<Composition fps=30>` 错误，正确为 `fps={30}`
3. **spring() 缺少 fps 参数**：必须传 `fps: FPS` 否则报错 `"fps" must be a number`
4. **React 导入**：`import React from 'remotion'` 报错，应为 `import React from 'react'`
5. **useCurrentFrame() 调用位置**：必须在 inner 组件（StickerContent）中，outer 组件（StickerComponent）不能调用
6. **超时延长**：120s → 300s（Remotion npm install + 渲染需要更长时间）
7. **目录创建**：主循环前加 `os.makedirs(args.output, exist_ok=True)`
8. **文件输入处理**：`os.path.isfile()` 支持单文件输入

### 三层组件架构确立

```
registerRoot(StickerComponent)
    ↓
StickerComponent（外层，返回 <Composition>）
    ↓
StickerContent（内层，含 useCurrentFrame）
```

---

## v4.0.0 (2026-04-30) - 重大重构

### 核心变更：三段式图像生成

| 优先级 | 方式 | 说明 |
|--------|------|------|
| 1 | AI生成图像 | 调用大模型直接生成高质量帧 |
| 2 | Remotion帧导出 | 每张贴图构建独立 Remotion 项目，导出 PNG |
| 3 | PIL本地生成 | 词汇表驱动，场景构图（兜底） |

**自动降级机制**：每层失败自动尝试下一层，无需人工干预。
