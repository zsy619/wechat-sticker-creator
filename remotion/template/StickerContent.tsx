/**
 * StickerContent.tsx - 贴图内容组件
 *
 * 占位符替换由 generate_frames.py 执行。
 *
 * __FPS__         → 帧率
 * __W__           → 宽度
 * __H__           → 高度
 * __BG_COLOR__    → 背景色
 * __TEXT_COLOR__  → 文字色
 * __PRIMARY__     → 主色
 * __SECONDARY__   → 副色
 * __TOTAL_FRAMES__ → 总帧数
 * __SEQUENCES__   → Sequence JSX 拼接字符串（每张贴图一个 Sequence）
 */

import React from 'react';
import { useCurrentFrame, interpolate, spring, Sequence } from 'remotion';

const FPS: number = __FPS__;
const W: number = __W__;
const H: number = __H__;
const BG: string = '__BG_COLOR__';
const TEXT: string = '__TEXT_COLOR__';
const PRIMARY: string = '__PRIMARY__';
const SECONDARY: string = '__SECONDARY__';
const TOTAL: number = __TOTAL_FRAMES__;

/* ── 动画工具函数（全部显式传入 fps） ─────────────────── */

const glowOpacity = (frame: number): number =>
  interpolate(
    spring({ frame, fps: FPS, config: { damping: 200, stiffness: 10 } }),
    [0, 1], [0.4, 1]
  );

const pulseScale = (frame: number): number =>
  interpolate(frame, [0, 15, 30], [1, 1.06, 1], { extrapolateRight: 'clamp' });

const floatY = (frame: number): number =>
  interpolate(frame, [0, 30], [0, -18], { extrapolateRight: 'clamp' });

const textFlash = (frame: number): number =>
  interpolate(frame, [0, 8, 15, 22, 30], [1, 0.85, 1, 0.9, 1], { extrapolateRight: 'clamp' });

const outerGlow = (frame: number): number =>
  interpolate(frame, [0, 15, 30], [1, 1.4, 1], { extrapolateRight: 'clamp' });

/* ── 5层霓虹 text-shadow ─────────────────────────────── */

const neonTextShadow = (og: number): string => `
  0 0 ${20 * og}px ${PRIMARY}60,
  0 0 ${40 * og}px ${PRIMARY}40,
  0 0 ${60 * og}px ${PRIMARY}25,
  0 0 ${80 * og}px ${PRIMARY}15,
  0 0 ${12 * og}px ${SECONDARY}80,
  0 0 ${24 * og}px ${SECONDARY}50,
  0 0 ${6 * og}px ${PRIMARY}cc,
  0 0 ${10 * og}px ${PRIMARY}99,
  0 0 ${3 * og}px rgba(255,255,255,0.9),
  3px 3px 0 rgba(0,0,0,0.9),
  4px 4px 8px rgba(0,0,0,0.7)
`;

/* ── 单张贴图场景组件（内层，使用 useCurrentFrame） ───── */

type StickerSceneProps = {
  copy: string;
  emojis_str: string;  // JSON-encoded string array
  frameOffset: number;
};

const StickerScene: React.FC<StickerSceneProps> = ({ copy, emojis_str, frameOffset }) => {
  const frame = useCurrentFrame();
  const localFrame = frame - frameOffset;
  const dur = 90;

  const g = glowOpacity(localFrame % dur);
  const s = pulseScale(localFrame % dur);
  const fy = floatY(localFrame % dur);
  const fl = textFlash(localFrame % dur);
  const og = outerGlow(localFrame % dur);

  const emojis: string[] = JSON.parse(emojis_str);

  return (
    <div style={{
      width: W, height: H,
      background: BG,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
      overflow: 'hidden',
    }}>
      {/* 背景光晕层 */}
      <div style={{
        position: 'absolute',
        top: '8%',
        left: '50%',
        transform: 'translateX(-50%)',
        width: W * 0.85,
        height: H * 0.52,
        background: `radial-gradient(ellipse at center, ${PRIMARY}28 0%, transparent 68%)`,
        opacity: g * 0.65,
        pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute',
        bottom: '20%',
        left: '50%',
        transform: 'translateX(-50%)',
        width: W * 0.55,
        height: H * 0.32,
        background: `radial-gradient(ellipse at center, ${SECONDARY}22 0%, transparent 68%)`,
        opacity: g * 0.5,
        pointerEvents: 'none',
      }} />

      {/* 主视觉：emoji 元素 */}
      <div style={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        zIndex: 2,
        transform: `scale(${s}) translateY(${fy}px)`,
        opacity: g,
        gap: 40,
        width: '100%',
        height: '58%',
      }}>
        {emojis.map((emoji, i) => (
          <span key={i} style={{
            fontSize: 380,
            lineHeight: 1,
            filter: `drop-shadow(0 0 24px ${PRIMARY}) drop-shadow(0 0 48px ${SECONDARY}) drop-shadow(0 0 80px ${PRIMARY}50)`,
            WebkitTextStroke: `1px ${PRIMARY}`,
            paintOrder: 'stroke fill',
            display: 'inline-block',
          }}>{emoji}</span>
        ))}
      </div>

      {/* 底部文案（≤96px 字体，5层霓虹阴影，渐变填充） */}
      <div style={{
        position: 'absolute',
        bottom: 52,
        left: 0,
        right: 0,
        textAlign: 'center',
        fontSize: 90,
        fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
        fontWeight: 'bold',
        color: TEXT,
        opacity: fl,
        transform: `scale(${1 + (1 - fl) * 0.05})`,
        textShadow: neonTextShadow(og),
        padding: '0 36px',
        zIndex: 3,
        wordBreak: 'break-all',
        // 文字渐变填充
        background: `linear-gradient(180deg, #FFFFFF 0%, ${PRIMARY} 100%)`,
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
      }}>
        {copy}
      </div>

      {/* 圆形遮罩（cyberpunk 主题风格） */}
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: H * 0.92,
        height: H * 0.92,
        borderRadius: '50%',
        boxShadow: `0 0 0 2px ${PRIMARY}40, 0 0 40px ${PRIMARY}30, 0 0 80px ${SECONDARY}20`,
        pointerEvents: 'none',
        zIndex: 1,
      }} />
    </div>
  );
};

/* ── 主组件（外层，注册 Composition，不直接用帧） ─────── */

export const StickerContent: React.FC = () => {
  useCurrentFrame(); // 保持调用，但不直接参与动画逻辑
  return (
    <div>
      __SEQUENCES__
    </div>
  );
};
