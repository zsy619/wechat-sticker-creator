# remotion/ - Remotion 帧组件模板

本目录包含 Remotion 阶段生成贴图时使用的模板代码。

## 目录结构

```
remotion/
├── README.md              ← 本文件
├── template/              ← 模板文件（generate_frames.py 读取并复制）
│   ├── index.tsx          ← registerRoot 入口
│   ├── StickerComponent.tsx ← 外层组件（返回 <Composition>）
│   └── StickerContent.tsx   ← 核心动画逻辑（自包含所有主题配置）
└── styles/
    └── base.css           ← 全局 CSS 重置（仅 body/margin）
```

## 模板流程

```
remotion/template/
    ├── index.tsx           → /tmp/remotion-sticker-{name}/src/index.tsx
    ├── StickerComponent.tsx → /tmp/remotion-sticker-{name}/src/StickerComponent.tsx
    └── StickerContent.tsx   → /tmp/remotion-sticker-{name}/src/StickerContent.tsx
```

`generate_frames.py` 执行以下替换后写入最终项目：

| 占位符 | 替换为 |
|--------|--------|
| `__FPS__` | 帧率（默认 30） |
| `__W__` | 宽度（默认 1080） |
| `__H__` | 高度（默认 1440） |
| `__BG_COLOR__` | 主题背景色 |
| `__TEXT_COLOR__` | 主题文字色 |
| `__PRIMARY__` | 主题主色 |
| `__SECONDARY__` | 主题副色 |
| `__THEME_KEY__` | 主题键名 |
| `__TOTAL_FRAMES__` | 总帧数 |
| `__SEQUENCES__` | Sequence JSX（每张贴图一个） |

## 三层组件架构

```
registerRoot(StickerComponent)
    ↓
StickerComponent（外层，返回 <Composition>）
    ↓
StickerContent（内层，含所有动画逻辑）
    ├── StickerScene（每张贴图的场景）
    │   ├── EmojiItem（每个 emoji，含错位动画）
    │   └── CopyText（底部文案，支持 4 种文字动画）
    ├── getBgStyle()（主题背景）
    └── getMaskRadius()（主题遮罩形状）
```

## v4.5 动画系统

**5 种贴图动画类型**（按 stickerIndex 循环分配）：

| 类型 | 效果 |
|------|------|
| `glow` | 轻微脉冲缩放（0.92~1.0） |
| `bounce` | 弹跳缩放入场 |
| `spin` | 360° 旋转 + 弹性入场 |
| `shake` | 横向故障抖动 |
| `float` | 正弦波漂浮（-18px 振幅） |

**入场/退场**：每张贴图前 20% 帧入场（弹性 overshoot），后 20% 帧退场（scale→0.5）。

**emoji 错位**：相邻 emoji 相位差 4 帧，防止同步。

**4 种文字动画**（按主题配置）：

| 类型 | 主题 | 效果 |
|------|------|------|
| `flash` | cyberpunk/neon/minimal | 透明度闪烁 |
| `bounce` | kawaii/meme | 逐字弹跳 |
| `typewriter` | retro | 逐字显现 + 光标 |
| `jitter` | hand-drawn | skewX 抖动 |

## 渲染命令

```bash
cd /tmp/remotion-sticker-{name}/
npm install
npx remotion still src/index.tsx StickerComponent --output out.png
```
