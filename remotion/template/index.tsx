/**
 * index.tsx - Remotion 项目入口（registerRoot）
 * 
 * 放置位置：/tmp/remotion-sticker-{name}/src/index.tsx
 * 
 * 职责：
 * - 导入 registerRoot
 * - 导入外层组件 StickerComponent
 * - 调用 registerRoot(StickerComponent)
 */

import { registerRoot } from 'remotion';
import { StickerComponent } from './StickerComponent';

registerRoot(StickerComponent);
