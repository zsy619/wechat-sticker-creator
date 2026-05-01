/**
 * StickerContent.tsx - 贴图内容组件（内层，使用 useCurrentFrame）
 *
 * 占位符替换规则（由 generate_frames.py 执行）：
 * __BG_COLOR__      → 主题背景色，如 #0D0D1A
 * __TEXT_COLOR__    → 主题文字色，如 #FFFFFF
 * __COPY__          → 核心文案，如 "随手一画，AI帮你算"
 * __PRIMARY__       → 主色，如 #00FFFF
 * __SECONDARY__     → 副色，如 #FF00FF
 * __FPS__           → 帧率，如 30
 * __W__            → 宽度，如 1080
 * __H__            → 高度，如 1440
 * __ELEMENTS_HTML__ → emoji 元素 JSX
 */

import { useCurrentFrame, interpolate, spring } from 'remotion';

const FPS = __FPS__;
const W = __W__;
const H = __H__;
const BG = '__BG_COLOR__';
const TEXT = '__TEXT_COLOR__';
const COPY = '__COPY__';
const PRIMARY = '__PRIMARY__';
const SECONDARY = '__SECONDARY__';

export const StickerContent = () => {
  const frame = useCurrentFrame();

  // 呼吸发光
  const glowOpacity = interpolate(
    spring({ frame, fps: FPS, config: { damping: 200, stiffness: 10 } }),
    [0, 1],
    [0.4, 1]
  );

  // 脉冲缩放
  const scale = interpolate(frame, [0, 15, 30], [1, 1.06, 1], {
    extrapolateRight: 'clamp',
  });

  // 浮空动画
  const floatY = interpolate(frame, [0, 30], [0, -18], {
    extrapolateRight: 'clamp',
  });

  // 文字闪烁（快速闪烁效果）
  const textFlash = interpolate(frame, [0, 8, 15, 22, 30], [1, 0.85, 1, 0.9, 1], {
    extrapolateRight: 'clamp',
  });

  // 文字颜色插值（主色↔白色切换）
  const textColorPhase = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: 'clamp' });

  // 外发光强度动画
  const outerGlow = interpolate(frame, [0, 15, 30], [1, 1.4, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        width: W,
        height: H,
        background: BG,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
        overflow: 'hidden',
      }}
    >
      {/* 背景装饰：霓虹渐变光晕 */}
      <div
        style={{
          position: 'absolute',
          top: '15%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: W * 0.7,
          height: H * 0.5,
          background: `radial-gradient(ellipse at center, ${PRIMARY}22 0%, transparent 70%)`,
          opacity: glowOpacity * 0.6,
          pointerEvents: 'none',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '25%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: W * 0.5,
          height: H * 0.3,
          background: `radial-gradient(ellipse at center, ${SECONDARY}18 0%, transparent 70%)`,
          opacity: glowOpacity * 0.5,
          pointerEvents: 'none',
        }}
      />

      {/* 主视觉区域 */}
      <div
        style={{
          opacity: glowOpacity,
          transform: `scale(${scale}) translateY(${floatY}px)`,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          zIndex: 2,
        }}
      >
        {/* emoji 元素 */}
        __ELEMENTS_HTML__
      </div>

      {/* 底部核心文案 */}
      <div
        style={{
          position: 'absolute',
          bottom: 50,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontSize: 140,
          fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
          fontWeight: 'bold',
          color: TEXT,
          opacity: textFlash,
          transform: `scale(${1 + (1 - textFlash) * 0.05})`,
          // 描边：4层不同颜色叠加产生霓虹效果
          textShadow: `
            /* 第1层：外扩散光晕（最外层，大范围低透明度）*/
            0 0 ${20 * outerGlow}px ${PRIMARY}60,
            0 0 ${40 * outerGlow}px ${PRIMARY}40,
            0 0 ${60 * outerGlow}px ${PRIMARY}25,
            0 0 ${80 * outerGlow}px ${PRIMARY}15,
            /* 第2层：中距离光晕（副色）*/
            0 0 ${12 * outerGlow}px ${SECONDARY}80,
            0 0 ${24 * outerGlow}px ${SECONDARY}50,
            /* 第3层：紧密辉光（主色高透明度）*/
            0 0 ${6 * outerGlow}px ${PRIMARY}cc,
            0 0 ${10 * outerGlow}px ${PRIMARY}99,
            /* 第4层：超近辉光（白色高亮）*/
            0 0 ${3 * outerGlow}px rgba(255,255,255,0.9),
            /* 第5层：黑色阴影（立体感）*/
            3px 3px 0 rgba(0,0,0,0.9),
            4px 4px 8px rgba(0,0,0,0.7)
          `,
          padding: '0 40px',
          zIndex: 3,
          wordBreak: 'break-all',
          // 文字渐变色
          background: `linear-gradient(180deg, #FFFFFF 0%, ${PRIMARY} 100%)`,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        {COPY}
      </div>
    </div>
  );
};
