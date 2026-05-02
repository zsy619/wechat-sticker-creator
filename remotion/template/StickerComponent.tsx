/**
 * StickerComponent.tsx - 贴图外层组件（返回 <Composition>）
 *
 * 占位符替换规则（由 generate_frames.py 执行）：
 * __FPS__          → 帧率，如 30
 * __W__           → 宽度，如 1080
 * __H__           → 高度，如 1440
 * __TOTAL_FRAMES__ → 总帧数，如 540（6贴图×90帧）
 *
 * B3修复：显式定义 Props 类型，Composition props 传入
 */

import React from 'react';
import { Composition } from 'remotion';
import { StickerContent } from './StickerContent';

type StickerComponentProps = {
  /** 总帧数 = 贴图数 × FRAMES_PER_STICKER */
  totalFrames: number;
  /** 帧率 */
  fps: number;
  /** 视频宽度 */
  width: number;
  /** 视频高度 */
  height: number;
};

export const StickerComponent: React.FC<StickerComponentProps> = ({
  totalFrames, fps, width, height,
}) => {
  return (
    <Composition
      id="StickerComponent"
      component={StickerContent}
      durationInFrames={totalFrames}
      fps={fps}
      width={width}
      height={height}
    />
  );
};
