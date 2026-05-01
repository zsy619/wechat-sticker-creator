/**
 * StickerComponent.tsx - 贴图外层组件（返回 <Composition>）
 *
 * 占位符替换规则（由 generate_frames.py 执行）：
 * __FPS__ → 帧率，如 30
 * __W__  → 宽度，如 1080
 * __H__  → 高度，如 1440
 */

import React from 'react';
import { Composition } from 'remotion';
import { StickerContent } from './StickerContent';

export const StickerComponent: React.FC = () => {
  return (
    <Composition
      id="StickerComponent"
      component={StickerContent}
      durationInFrames={90}
      fps={__FPS__}
      width={__W__}
      height={__H__}
    />
  );
};
