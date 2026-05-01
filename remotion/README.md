# remotion/ - Remotion 帧组件模板

本目录包含 Remotion 阶段生成贴图时使用的模板代码。

## 目录结构

```
remotion/
├── README.md              ← 本文件
├── template/              ← 基础模板（每张贴图的项目起点）
│   ├── index.tsx           ← registerRoot 入口
│   ├── StickerComponent.tsx ← 外层组件（返回 <Composition>）
│   └── StickerContent.tsx   ← 内层组件（含 useCurrentFrame）
├── components/            ← 可复用组件
│   └── EmojiElement.tsx  ← emoji 元素组件（带呼吸动画）
└── styles/
    └── base.css           ← 基础样式
```

## 模板流程

```
remotion/template/
    ├── index.tsx           → /tmp/remotion-sticker-{name}/src/index.tsx
    ├── StickerComponent.tsx → /tmp/remotion-sticker-{name}/src/StickerComponent.tsx
    └── StickerContent.tsx → /tmp/remotion-sticker-{name}/src/StickerContent.tsx
```

## 三层组件架构

```
registerRoot(StickerComponent)
    ↓
StickerComponent（外层，返回 <Composition>）
    ↓
StickerContent（内层，使用 useCurrentFrame + 动画）
```

## 渲染命令

```bash
cd /tmp/remotion-sticker-{name}/
npm install
npx remotion still src/index.tsx StickerComponent --output out.png
```

## 快速复制模板到项目

```python
import shutil
src = "/Users/zhushuyan/.agents/skills/wechat-sticker-skill-v2/remotion/template"
dst = "/tmp/remotion-sticker-{name}/src"
shutil.copy(f"{src}/index.tsx", f"{dst}/index.tsx")
shutil.copy(f"{src}/StickerComponent.tsx", f"{dst}/StickerComponent.tsx")
shutil.copy(f"{src}/StickerContent.tsx", f"{dst}/StickerContent.tsx")
shutil.copy("/Users/zhushuyan/.agents/skills/wechat-sticker-skill-v2/remotion/styles/base.css", f"{dst}/styles.css")
```
