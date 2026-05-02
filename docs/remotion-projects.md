# Remotion 项目结构

本文档描述**阶段二（Remotion 帧导出）**生成的项目结构。

> **核心规范**：微信贴图场景的 Remotion 核心规范（`<Composition>` 包装、竖屏字体规格、Sequence + AbsoluteFill 陷阱、CLI 限制）直接记录在本文档下方，无需外部 skill。

## 项目位置

```
{项目根目录}/remotion-sticker-{贴图名称}/
```

每张贴图独立一个 Remotion 项目，**保留在项目目录中，不清理**。

## 项目文件结构

详见 [project-structure.md](project-structure.md)。

## 关键文件内容

### src/index.tsx — 注册入口

```tsx
import { registerRoot } from 'remotion';
import { StickerComponent } from './StickerComponent';

registerRoot(StickerComponent);
```

```tsx
import React from 'react';
import { Composition } from 'remotion';
import { StickerContent } from './StickerContent';

type StickerComponentProps = {
  totalFrames: number;
  fps: number;
  width: number;
  height: number;
};

export const StickerComponent: React.FC<StickerComponentProps> = ({
  totalFrames, fps, width, height,
}) => {
  return (
    <Composition
      id="StickerComponent"
      component={StickerContent}
      durationInFrames={totalFrames ?? 720}
      fps={fps ?? 30}
      width={width ?? 1080}
      height={height ?? 1440}
    />
  );
};
```

**注意**：必须使用 `??` 为 `<Composition>` 属性提供 fallback 值，否则 Discovery 阶段（`props=undefined`）会抛出验证错误。

### src/StickerContent.tsx — 内部组件（实际视觉）

```tsx
import { useCurrentFrame, interpolate, spring } from 'remotion';
import './styles.css';

const FPS = 30;

export const StickerContent = () => {
  const frame = useCurrentFrame();
  const glowOpacity = interpolate(
    spring({ frame, fps: FPS, config: { damping: 200, stiffness: 10 } }),
    [0, 1], [0.3, 1]
  );
  return (
    <div style={{
      width: 1080, height: 1440,
      background: '#0D0D1A',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
    }}>
      <div style={{ opacity: glowOpacity, display: 'flex', gap: 40, alignItems: 'center' }}>
        {/* emoji 元素 */}
      </div>
    </div>
  );
};
```

## 三层组件架构

```
registerRoot(StickerComponent)
    ↓
StickerComponent (外层包装)
    ↓ 返回 <Composition component={StickerContent}>
    ↓
StickerContent (实际视觉，使用 useCurrentFrame)
```

**为什么需要两层？**
- Remotion v4 要求：`useCurrentFrame()` 只能在被 `<Composition>` 注册的组件或其子树中调用
- `registerRoot()` 接收的是返回 `<Composition>` 的外层组件
- `<Composition component={StickerContent}>` 将 inner 组件注册为可渲染的 composition

## 项目文件来源

模板文件位于技能目录 `remotion/template/`：

```
remotion/template/
├── index.tsx             ← 入口模板
├── StickerComponent.tsx  ← 外层组件模板
└── StickerContent.tsx    ← 内层组件模板
```

生成时 Python 脚本从 `remotion/template/` 复制并注入主题色、emoji 元素。

## 渲染命令

```bash
cd {项目根目录}/.remotion-sticker-{name}/
npm install
npx remotion still src/index.tsx StickerComponent --output out.png
```

## 版本锁定

```json
{
  "dependencies": {
    "@remotion/cli": "4.0.448",
    "remotion": "4.0.448"
  }
}
```

**必须与全局 `@remotion/cli` 版本一致**，否则 esbuild bundling 会报 `delayRender() timeout` 错误。

## 生命周期

```
生成项目 → npm install → npx remotion still → 导出PNG
     ↓            ↓              ↓                ↓
  一次性创建   约10-30s      约30-180s         成功/失败
```

## 核心规范

### 架构：必须用 `<Composition>` 包装

禁止 `registerRoot` 直接传组件，否则 `useCurrentFrame()`、`spring()` 等 hooks 全部失效：

```tsx
// ✅ 正确 — Root.tsx 用 <Composition> 包装
export const RemotionRoot = () => (
  <Composition
    id="StickerVideo"
    component={StickerContent}
    durationInFrames={90}
    fps={30}
    width={1080}
    height={1440}
  />
);
registerRoot(RemotionRoot);

// ❌ 错误 — 直接传组件，hooks 上下文丢失
registerRoot(StickerContent); // useCurrentFrame() 全部报错
```

### 包管理：只装 `remotion`

```bash
npm install remotion react react-dom
# NOT: @remotion/core @remotion/react @remotion/cli（这些在 v4 不存在）
```

### Sequence + AbsoluteFill 陷阱

在 `Sequence` 内直接用 `AbsoluteFill` 做 `justifyContent: 'center'` 居中——在 Chrome headless 下完全失效，文字渲染为空白/透明（max channel ~100 而非 255）。

**正确模式：场景拆为独立组件**

```tsx
// ✅ 正确 — Scene 是独立组件，内部用 AbsoluteFill
<Sequence from={0} durationInFrames={90}>
  <SceneComponent />  {/* SceneComponent 内部调用 useCurrentFrame() */}
</Sequence>

// ❌ 错误 — AbsoluteFill 直接放 Sequence 内，居中失效
<Sequence from={0} durationInFrames={90}>
  <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
    {/* 文字在 headless 下不可见 */}
  </AbsoluteFill>
</Sequence>
```

### 竖屏字体规格（1080×1440）

| 元素 | 规格 | 说明 |
|------|------|------|
| 主标题 | ≤96px | 竖屏宽度有限，过大被裁剪 |
| 正文 | ≤28px | 保持可读性 |
| 辅助文字 | ≤22px | 说明注释等 |
| 代码/mono | ≤20px | 窄屏易溢出 |
| 左右 padding | ≥50px | 防止文字贴边 |

### Chrome SSL 错误

Remotion 下载 Chrome headless 失败（`unable to get local issuer certificate`）时，指定系统 Chrome：

```ts
// remotion.config.ts
import { Config } from '@remotion/cli/config';
Config.setBrowserExecutable('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome');
```

## 故障排查

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `delayRender() timeout` | 版本不一致或 chromium 问题 | 确认 package.json 版本为 4.0.448 |
| `Expected "{" but found "1"` | JSX 属性写成了 `fps=30` | 属性值必须用 `{}`，如 `fps={30}` |
| `useCurrentFrame() can only be called...` | 组件未通过 `<Composition>` 注册 | 确认有 outer 组件返回 `<Composition>` |
| `"fps" must be a number` | `spring()` 缺少 `fps` 参数 | 显式传入 `spring({ frame, fps: FPS, config: {...} })` |
| `Module build failed...` | esbuild 编译 TSX 语法错误 | 检查模板字符串拼接是否产生语法错误 |
| `No such file or directory` | 目录未创建 | 主循环前添加 `os.makedirs(args.output, exist_ok=True)` |

## CLI 命令限制

### `remotion still` 与 Discovery 阶段

`npx remotion still` 命令存在架构限制：

**Discovery 阶段**：当 Remotion 加载项目时，会立即调用 `registerRoot` 注册的工厂组件（`StickerComponent(undefined)`）来发现所有 `<Composition>` 定义。**此时 props 为 `undefined`**。

**结果**：如果 `<Composition>` 的 `width`、`height`、`durationInFrames` 直接使用外层 props 而没有默认值，会抛出验证错误：

```
width prop must be a number, but passed undefined
```

**解决方案**：在 `<Composition>` 的 JSX 属性中使用 `??`（nullish coalescing）提供默认值：

```tsx
// ✅ 正确 — Discovery 阶段 props=undefined 时使用 fallback
<Composition
  id="StickerComponent"
  component={StickerContent}
  durationInFrames={totalFrames ?? 720}
  fps={fps ?? 30}
  width={width ?? 1080}
  height={height ?? 1440}
/>

// ❌ 错误 — Discovery 阶段 width=undefined 报错
<Composition
  width={width}  // undefined 时抛错
  height={height}
/>
```

### `--props` 参数无法穿透到 Composition 的 JSX 属性

`--props` 传给 `registerRoot(StickerComponent)(props)`，但 `<Composition>` 的 `width`/`height`/`fps` 来自 **JSX 属性本身**，而非外层 props：

```tsx
// --props '{"width": 1080, "height": 1440}' 不影响这里
<Composition
  width={width ?? 1080}  // width 来自外层 props，不是 --props
  height={height ?? 1440}
/>
```

这是 Remotion Composition 工厂模式的已知限制。正式渲染时应通过 `--props` 传参给 `StickerContent`（实际视觉组件），而非 `<Composition>` 的外层属性。

### 渲染尺寸可能不等于预期尺寸

`remotion still` 的输出尺寸可能因 Remotion 内部缩放逻辑而略大于 `<Composition>` 的 `width`×`height`（如预期 1080×1440，实际输出 1523×2030）。这是 Remotion 内部行为，不影响内容正确性。

## 异常处理

Remotion 帧导出失败时直接报错，不再降级。
