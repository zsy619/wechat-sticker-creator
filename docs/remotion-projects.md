# Remotion 项目结构

本文档描述**阶段二（Remotion 帧导出）**生成的项目结构。

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

### src/StickerComponent.tsx — 外部组件（返回 Composition）

```tsx
import React from 'react';
import { Composition } from 'remotion';
import { StickerContent } from './StickerContent';

export const StickerComponent: React.FC = () => {
  return (
    <Composition
      id="StickerComponent"
      component={StickerContent}
      durationInFrames={1}
      fps={30}
      width={1080}
      height={1440}
    />
  );
};
```

**注意**：`StickerComponent` 不使用 `useCurrentFrame`，它只是一个返回 `<Composition>` 的外层包装。

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

## 故障排查

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `delayRender() timeout` | 版本不一致或 chromium 问题 | 确认 package.json 版本为 4.0.448 |
| `Expected "{" but found "1"` | JSX 属性写成了 `fps=30` | 属性值必须用 `{}`，如 `fps={30}` |
| `useCurrentFrame() can only be called...` | 组件未通过 `<Composition>` 注册 | 确认有 outer 组件返回 `<Composition>` |
| `"fps" must be a number` | `spring()` 缺少 `fps` 参数 | 显式传入 `spring({ frame, fps: FPS, config: {...} })` |
| `Module build failed...` | esbuild 编译 TSX 语法错误 | 检查模板字符串拼接是否产生语法错误 |
| `No such file or directory` | 目录未创建 | 主循环前添加 `os.makedirs(args.output, exist_ok=True)` |

## 自动降级路径

```
AI 生成（第1位）
    ↓ 异常
Remotion 帧导出（第2位）
    - 创建项目 `{项目根目录}/.remotion-sticker-{name}/`
    - npm install + npx remotion still
    - 成功 → 保存 PNG
    - 失败 → 降级 PIL
    ↓ 异常
PIL 本地生成（第3位）
    - 直接用 Pillow 绘制
    - 保证最终能生成图片
```
