/**
 * StickerContent.tsx - 贴图内容组件（重写版 v4.14）
 *
 * 占位符替换由 generate_frames.py 执行。
 *
 * 主题配置化：
 *   __FPS__          → 帧率（默认 30）
 *   __W__           → 宽度（默认 1080）
 *   __H__           → 高度（默认 1440）
 *   __BG_COLOR__    → 背景色（theme.bg）
 *   __PRIMARY__     → 主色（theme.primary）
 *   __SECONDARY__   → 副色（theme.secondary）
 *   __THEME_KEY__   → 主题键名（cyberpunk / kawaii / neon / retro / hand-drawn / minimal / meme）
 *   __TOTAL_FRAMES__→ 总帧数
 *   __SEQUENCES__   → Sequence JSX（每张贴图一个）
 *
 * 版本清理记录：
 *   v4.14: M7清理剩余旧版本注释（M/A/F/G/H/K/L系列前缀标记全部移除）
 *   v4.13: M2连续空行/M4 isDark缓存/M6 3字符hex/M2 SVG注释
 *   v4.12: L1移除15个旧版本遗留注释
 *   v4.11: J1/J2移除未使用theme字段
 *   v4.10: I类清理（无reach default、flash opacity、类型注释）
 *   v4.9:  H类精细清理
 *   v4.8:  G类代码质量
 *   v4.7:  F类视觉增强
 *   v4.6:  A/C类动画修复与主题配置
 */

import React from 'react';
import { useCurrentFrame, interpolate, spring } from 'remotion';

/* ── 常量（来自编译期占位符）────────────────────────────── */

const FPS_VAL: number = __FPS__;
const W: number = __W__;
const H: number = __H__;
const PRIMARY: string = '__PRIMARY__';
const SECONDARY: string = '__SECONDARY__';
const THEME_KEY: string = '__THEME_KEY__';

/* ── 内联主题配置（v4.6 C1修复：基于 W=1080 比例计算）────── */

/* ── 类型定义（I5: 联合字面量可直接 as const 断言）────── */

type AnimationType = 'glow' | 'bounce' | 'spin' | 'shake' | 'float';
type MaskShape    = 'circle' | 'rounded-square' | 'parallelogram' | 'blob';
type BgStyle      = 'radial-gradient' | 'grid' | 'dots' | 'gradient-dots' | 'solid';
type TextAnim     = 'flash' | 'typewriter' | 'bounce' | 'jitter';

type ThemeConfig = {
  maskShape: MaskShape;
  bgStyle: BgStyle;
  textAnim: TextAnim;
  emojiSize: string;
  emojiGap: string;
  fontSize: string;
};

// C1修复：emojiSize = W×7.4% ≈ 80px（W=1080），fontSize = W×3.3% ≈ 36px
const THEME_CONFIGS: Record<string, ThemeConfig> = {
  cyberpunk:    { maskShape: 'circle',          bgStyle: 'radial-gradient', textAnim: 'flash',     emojiSize: '80px', emojiGap: '10px', fontSize: '36px' },
  kawaii:       { maskShape: 'rounded-square', bgStyle: 'dots',           textAnim: 'bounce',   emojiSize: '80px', emojiGap: '12px', fontSize: '36px' },
  neon:         { maskShape: 'circle',          bgStyle: 'grid',           textAnim: 'flash',    emojiSize: '80px', emojiGap: '10px', fontSize: '36px' },
  retro:        { maskShape: 'parallelogram',   bgStyle: 'gradient-dots', textAnim: 'typewriter',emojiSize: '80px', emojiGap: '10px', fontSize: '36px' },
  'hand-drawn': { maskShape: 'blob',            bgStyle: 'solid',          textAnim: 'jitter',   emojiSize: '80px', emojiGap: '12px', fontSize: '36px' },
  minimal:      { maskShape: 'rounded-square', bgStyle: 'solid',          textAnim: 'flash',    emojiSize: '80px', emojiGap: '8px',  fontSize: '36px' },
  meme:         { maskShape: 'rounded-square', bgStyle: 'solid',          textAnim: 'bounce',   emojiSize: '80px', emojiGap: '12px', fontSize: '36px' },
};

type ThemeColors = {
  primary: string; secondary: string;
  bg: string;
};

const THEME_COLORS: Record<string, ThemeColors> = {
  cyberpunk:    { primary: '#00FFFF', secondary: '#FF00FF', bg: '#0D0D1A' },
  kawaii:       { primary: '#FF69B4', secondary: '#FFB6C1', bg: '#FFF0F5' },
  neon:         { primary: '#FF00FF', secondary: '#00FFFF', bg: '#1A0033' },
  retro:        { primary: '#FFD700', secondary: '#FF6B35', bg: '#2D1B00' },
  'hand-drawn': { primary: '#8B4513', secondary: '#D2691E', bg: '#FFF8DC' },
  minimal:      { primary: '#212529', secondary: '#495057', bg: '#F8F9FA' },
  meme:         { primary: '#FF4500', secondary: '#FFD700', bg: '#1A1A1A' },
};

const ANIMATION_TYPES: AnimationType[] = ['glow', 'bounce', 'spin', 'shake', 'float'];
const FRAMES_PER_STICKER = 90;

const cfg   = THEME_CONFIGS[THEME_KEY]   ?? THEME_CONFIGS['cyberpunk']!;
const theme = THEME_COLORS[THEME_KEY] ?? THEME_COLORS['cyberpunk']!;

/* ── 动画函数库 ──────────────────────────────────────── */

const dur = FRAMES_PER_STICKER;

// 呼吸发光（0→1→0 循环）
const glowOpacity = (f: number): number =>
  interpolate(
    spring({ frame: f, fps: FPS_VAL, config: { damping: 200, stiffness: 10 } }),
    [0, 1], [0.4, 1]
  );

const overshoot = (t: number): number =>
  t >= 1 ? 1 : 1 + Math.sin(t * Math.PI) * 0.08;

// 弹跳缩放（0→1.08→1）
const bounceScale = (f: number): number =>
  interpolate(f, [0, 12, 25, 40, 55, dur], [0, 1.08, 0.97, 1.03, 1, 1],
    { extrapolateRight: 'clamp' });

// 旋转角度（0→360°）
const spinRotate = (f: number): number =>
  interpolate(f, [0, dur], [0, 360], { extrapolateRight: 'clamp' });

// 旋转弹性入场（0→1.15→1）
const spinScaleIn = (f: number): number =>
  interpolate(f, [0, 15, dur], [0, 1.15, 1], { extrapolateRight: 'clamp' });

// 横向抖动（故障效果）— A5修复：叠加 exitF 衰减
const shakeX = (f: number, exitF: number): number => {
  const base = interpolate(f, [0, 5, 10, 15, 20, dur], [0, -8, 8, -5, 3, 0],
    { extrapolateRight: 'clamp' });
  return base * exitF;
};

const exitScale = (enterF: number, exitF: number): number => {
  return enterF * (0.6 + 0.4 * exitF);
};

/* ── 入场/退场动画 ────────────────────────────────── */

// 入场进度（占前20%帧：0→1）
const enterProgress = (f: number): number =>
  interpolate(f, [0, Math.floor(dur * 0.2)], [0, 1], { extrapolateRight: 'clamp' });

// 退场进度（占后20%帧：1→0）
const exitProgress = (f: number): number =>
  interpolate(f, [Math.floor(dur * 0.8), dur], [1, 0], { extrapolateRight: 'clamp' });

// 入场 scale（弹性 overshoot，0.7→1.0）
const enterScaleFn = (f: number): number => {
  const t = enterProgress(f);
  if (t >= 1) return 1;
  return 0.7 + 0.3 * (1 - Math.pow(1 - t, 3)) + Math.sin(t * Math.PI) * 0.04;
};

const textEnterProgress = (f: number): number =>
  interpolate(f, [0, Math.floor(dur * 0.15)], [0, 1], { extrapolateRight: 'clamp' });

const textEnterScale = (f: number): number => {
  const t = textEnterProgress(f);
  if (t >= 1) return 1;
  // cubic ease-out + 微小 overshoot
  return 1 - Math.pow(1 - t, 3) + Math.sin(t * Math.PI) * 0.06;
};

//    t=0→高光在左侧，t=1→高光移动到右侧
const shimmerOffset = (f: number): number => {
  const t = f / dur;
  // diagonal sweep: -100% → 200%
  return -100 + t * 300;
};

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

/* ── 主题遮罩形状 ──────────────────────────────────── */

const getMaskRadius = (): string => {
  switch (cfg.maskShape) {
    case 'circle':          return '50%';
    case 'rounded-square':  return '24px';
    case 'parallelogram':   return '8px';
    case 'blob':            return '60% 40% 55% 45% / 55% 45% 60% 40%';
  }
};

const isParallelogram = (): boolean => cfg.maskShape === 'parallelogram';

/* ── 主题背景（C2修复：深色主题 pattern 透明度提升）────── */

const isDarkTheme = (): boolean => {
  const bg = theme.bg;
  const hex = bg.replace('#', '');
  // 支持3字符hex（#RGB → #RRGGBB）
  const normalized = hex.length === 3
    ? hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2]
    : hex;
  if (normalized.length < 6) return false;
  const r = parseInt(normalized.slice(0, 2), 16);
  const g = parseInt(normalized.slice(2, 4), 16);
  const b = parseInt(normalized.slice(4, 6), 16);
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255 < 0.4;
};

// 主题亮度缓存（theme.bg 在运行时不变）
const IS_DARK = isDarkTheme();

const getBgStyle = (): React.CSSProperties => {
  const t = theme;
  // C2修复：深色主题 pattern 透明度 40%，浅色主题 20%
  const patternAlpha = IS_DARK ? '40' : '20';

  switch (cfg.bgStyle) {
    case 'radial-gradient':
      return {
        background: `
          radial-gradient(ellipse at 50% 30%, ${t.primary}18 0%, transparent 55%),
          radial-gradient(ellipse at 30% 70%, ${t.secondary}14 0%, transparent 50%),
          ${t.bg}
        `,
      };
    case 'grid':
      return {
        background: `
          linear-gradient(${t.primary}${patternAlpha} 1px, transparent 1px),
          linear-gradient(90deg, ${t.primary}${patternAlpha} 1px, transparent 1px),
          ${t.bg}
        `,
        backgroundSize: '48px 48px',
      };
    case 'dots':
      return {
        background: `radial-gradient(${t.primary}${dark ? '50' : '30'} 2px, transparent 2px)`,
        backgroundSize: '32px 32px',
        backgroundColor: t.bg,
      };
    case 'gradient-dots':
      return {
        background: `
          radial-gradient(${t.primary}${patternAlpha} 1.5px, transparent 1.5px),
          radial-gradient(${t.secondary}${patternAlpha} 1px, transparent 1px)
        `,
        backgroundSize: '28px 28px, 20px 20px',
        backgroundPosition: '0 0, 14px 14px',
        backgroundColor: t.bg,
      };
    case 'solid':
      return { background: t.bg };
  }
};

/* ── Emoji 组件（含错位动画）─────────────────────────── */

type EmojiItemProps = {
  emoji: string;
  index: number;
  total: number;
  animType: AnimationType;
  enterF: number;
  exitF: number;
};

const EmojiItem: React.FC<EmojiItemProps> = ({
  emoji, index, total, animType, enterF, exitF,
}) => {
  const frame = useCurrentFrame();
  // P1-3: 每个 emoji 相对相位差 = index * 4 帧
  const localFrame = Math.max(0, (frame - index * 4) % dur);

  let scale: number;
  
  const ep = enterProgress(localFrame);
  const overshootScale = overshoot(ep);
  if (animType === 'bounce') {
    scale = bounceScale(localFrame);
  } else if (animType === 'spin') {
    scale = spinScaleIn(localFrame);
  } else if (animType === 'glow') {
    scale = 0.92 + 0.08 * Math.sin((localFrame / dur) * Math.PI * 2);
  } else if (animType === 'float') {
    // float: 无循环动画，scale = 入场 overshoot（静态）
    scale = overshootScale;
  } else {
    // shake: 无循环动画，scale = 入场 overshoot
    scale = overshootScale;
  }
  
  const animScale = scale * exitScale(enterF, exitF);

  const opacity = enterF * exitF;

  // float: 每个 emoji 不同相位（内联计算）
  const floatOffset = animType === 'float'
    ? Math.sin(((index / total) + frame / dur) * Math.PI * 2) * -18
    : 0;
  
  const xShake = animType === 'shake' ? shakeX(localFrame, exitF) : 0;

  const rotation = animType === 'spin' ? spinRotate(localFrame) : 0;
  
  const shadowIntensity = enterF * exitF;

  return (
    <span
      style={{
        display: 'inline-block',
        fontSize: cfg.emojiSize,
        lineHeight: 1,
        opacity,
        transform: `
          translateY(${floatOffset}px)
          translateX(${xShake}px)
          scale(${animScale})
          rotate(${rotation}deg)
        `,
        filter: `
          drop-shadow(0 0 ${20 * shadowIntensity}px ${PRIMARY})
          drop-shadow(0 0 ${48 * shadowIntensity * 0.5}px ${SECONDARY})
        `,
        WebkitTextStroke: `1px ${PRIMARY}`,
        paintOrder: 'stroke fill',
        willChange: 'transform, opacity',
      }}
    >
      {emoji}
    </span>
  );
};

/* ── 文字动画组件（A2/A3修复）─────────────────────────── */

type CopyTextProps = {
  copy: string;
  localFrame: number;
  enterF: number;
  exitF: number;
};

const CopyText: React.FC<CopyTextProps> = ({ copy, localFrame, enterF, exitF }) => {
  const tEnter = textEnterScale(localFrame);
  
  const opacity = enterF * exitF;
  
  const neonOg = interpolate(
    localFrame, [0, 15, dur], [1, 1.4, 1],
    { extrapolateRight: 'clamp' });

  // 退场阶段冻结闪烁，改为平滑淡出
  const fl = (enterF > 0.9 && exitF > 0.5)
    ? interpolate(
        localFrame, [0, 8, 15, 22, 30, dur], [1, 0.85, 1, 0.9, 1, 1],
        { extrapolateRight: 'clamp' })
    : 1; // 退场阶段固定为1，由 opacity 统一控制淡出

  const wrapperStyle: React.CSSProperties = {
    display: 'inline-block',
    opacity: opacity * fl,
    transform: `scale(${tEnter})`,
    textShadow: neonTextShadow(neonOg),
  };

  switch (cfg.textAnim) {
    case 'typewriter': {
      const revealed = interpolate(
        localFrame, [0, Math.min(dur * 0.6, 30)], [0, copy.length],
        { extrapolateRight: 'clamp' });
      const visible = copy.slice(0, Math.floor(revealed));
      const cursor  = revealed < copy.length ? '|' : '';
      return (
        <span style={wrapperStyle}>
          {visible}{cursor}
        </span>
      );
    }
    case 'bounce': {
      return (
        <span style={wrapperStyle}>
          {copy.split('').map((ch, i) => {
            const delay = i * 2;
            const local = Math.max(0, localFrame - delay);
            const charBounce = interpolate(local, [0, 6, 12, 18, 24], [0, -8, 4, -2, 0],
              { extrapolateRight: 'clamp' });
            return (
              <span
                key={i}
                style={{
                  display: 'inline-block',
                  transform: `translateY(${charBounce}px)`,
                  willChange: 'transform',
                }}
              >
                {ch}
              </span>
            );
          })}
        </span>
      );
    }
    case 'jitter': {
      const skew = interpolate(
        localFrame, [0, 4, 8, 12, 16, 20, dur], [0, -2, 2, -1, 1.5, 0, 0],
        { extrapolateRight: 'clamp' });
      return (
        <span
          style={{
            ...wrapperStyle,
            transform: `skewX(${skew}deg) scale(${tEnter})`,
            willChange: 'transform',
          }}
        >
          {copy}
        </span>
      );
    }
    case 'flash':
    default: {
      return (
        <span
          style={{
            ...wrapperStyle,
            transform: `scale(${tEnter + (1 - fl) * 0.05})`,
            willChange: 'transform, opacity',
          }}
        >
          {copy}
        </span>
      );
    }
  }
};

/* ── 单张贴图场景组件 ──────────────────────────────── */

type StickerSceneProps = {
  copy: string;
  emojis_str: string;
  frameOffset: number;
  stickerIndex: number;
};

const StickerScene: React.FC<StickerSceneProps> = ({
  copy, emojis_str, frameOffset, stickerIndex,
}) => {
  const frame = useCurrentFrame();
  const localFrame = Math.max(0, frame - frameOffset);

  // P0-2: 循环分配动画类型
  const animType: AnimationType =
    ANIMATION_TYPES[stickerIndex % ANIMATION_TYPES.length]!;

  let emojis: string[];
  try {
    emojis = JSON.parse(emojis_str);
  } catch {
    
    emojis = [...emojis_str].filter(c => /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F600}-\u{1F64F}]/u.test(c));
    if (emojis.length === 0) emojis = ['❓'];
  }

  const enterF = enterScaleFn(localFrame);
  const exitF  = exitProgress(localFrame);

  const g = glowOpacity(localFrame);
  
  const rootScale = exitScale(enterF, exitF);

  const bgStyle = getBgStyle();
  const maskRadius = getMaskRadius();
  const doSkew = isParallelogram();
  
  const shimmerX = shimmerOffset(localFrame);
  const shimmerOpacity = enterF > 0.5
    ? interpolate(localFrame, [Math.floor(dur * 0.5), Math.floor(dur * 0.5) + 20], [0, 0.6],
        { extrapolateRight: 'clamp' })
    : 0;

  // C3修复: 遮罩 boxShadow 强度差异化（根据主题亮度）
  const shadowMult = IS_DARK ? 1.4 : 0.7;
  const borderAlpha = IS_DARK ? '60' : '30';

  return (
    <div style={{
      width: W, height: H,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
      overflow: 'hidden',
      ...bgStyle,
      
      transform: `scale(${rootScale})`,
      transformOrigin: 'center center',
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
        gap: cfg.emojiGap,
        width: '100%',
        height: '58%',
      }}>
        {emojis.map((emoji, i) => (
          <EmojiItem
            key={i}
            emoji={emoji}
            index={i}
            total={emojis.length}
            animType={animType}
            enterF={enterF}
            exitF={exitF}
          />
        ))}
      </div>

      {/* 底部文案 — A4: gradient text + shimmer 光效 */}
      {/* G3: bottom 改为 H 比例（52/1440≈3.6%） */}
      <div style={{
        position: 'absolute',
        bottom: H * 0.036,
        left: 0, right: 0,
        textAlign: 'center',
        fontSize: cfg.fontSize,
        fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
        fontWeight: 'bold',
        padding: `0 ${W * 0.033}`,
        zIndex: 3,
        wordBreak: 'break-all',
      }}>
        {/* A4: 多层 gradient 实现 shimmer 效果 */}
        <span
          style={{
            position: 'relative',
            display: 'inline-block',
            background: `linear-gradient(180deg, #FFFFFF 0%, ${PRIMARY} 100%)`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          {/* 高光扫过层 */}
          <span
            style={{
              position: 'absolute',
              top: 0, left: 0, right: 0, bottom: 0,
              background: `linear-gradient(
                105deg,
                transparent 30%,
                rgba(255,255,255,0.7) 50%,
                transparent 70%
              )`,
              backgroundSize: '200% 100%',
              backgroundPosition: `${shimmerX}% 0`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              opacity: shimmerOpacity,
              pointerEvents: 'none',
            }}
          />
          <CopyText copy={copy} localFrame={localFrame} enterF={enterF} exitF={exitF} />
        </span>
      </div>

      {/* 遮罩层 — F1: 外发光呼吸环 + C3: boxShadow 差异化 */}
      {/* F3: 对角高光线 SVG叠加层 */}
      <svg
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: doSkew
            ? 'translate(-50%, -50%) skewX(-8deg)'
            : 'translate(-50%, -50%)',
          width: H * 0.94,
          height: H * 0.94,
          transformOrigin: 'center center',
          pointerEvents: 'none',
          zIndex: 2,
          overflow: 'visible',
        }}
        viewBox={`0 0 ${H * 0.94} ${H * 0.94}`}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* G4: 合并 defs — 所有渐变定义在一处 */}
        <defs>
          <linearGradient id="diagStroke" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="white" stopOpacity={enterF * 0.7} />
            <stop offset="40%" stopColor="white" stopOpacity={enterF * 0.3} />
            <stop offset="60%" stopColor="white" stopOpacity={enterF * 0.1} />
            <stop offset="100%" stopColor="white" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="diagStroke2" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="white" stopOpacity={enterF * 0.4} />
            <stop offset="50%" stopColor="white" stopOpacity={enterF * 0.15} />
            <stop offset="100%" stopColor="white" stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* 左上 → 右下的对角高光线 */}
        <line
          x1="8%" y1="4%"
          x2="28%" y2="20%"
          stroke="url(#diagStroke)"
          strokeWidth={3 * enterF}
          strokeLinecap="round"
        />
        {/* 右上 → 左下的反向高光 */}
        <line
          x1="92%" y1="4%"
          x2="72%" y2="20%"
          stroke="url(#diagStroke2)"
          strokeWidth={2 * enterF}
          strokeLinecap="round"
        />
      </svg>
      {/* F1: 外发光环（第二层，透明度随 g 变化） */}
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: doSkew
          ? 'translate(-50%, -50%) skewX(-8deg)'
          : 'translate(-50%, -50%)',
        width: H * 0.92,
        height: H * 0.92,
        borderRadius: maskRadius,
        transformOrigin: 'center center',
        boxShadow: `
          0 0 0 2px ${PRIMARY}${borderAlpha},
          0 0 ${40 * shadowMult}px ${PRIMARY}${Math.round(30 * shadowMult)},
          0 0 ${80 * shadowMult}px ${SECONDARY}${Math.round(20 * shadowMult)}
        `,
        pointerEvents: 'none',
        zIndex: 1,
      }} />
      {/* F1: 外发光环（第三层，透明度随 g 变化） */}
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: doSkew
          ? 'translate(-50%, -50%) skewX(-8deg)'
          : 'translate(-50%, -50%)',
        width: H * 0.94,
        height: H * 0.94,
        borderRadius: maskRadius,
        transformOrigin: 'center center',
        boxShadow: `
          0 0 ${30 * g}px ${PRIMARY}60,
          0 0 ${60 * g}px ${SECONDARY}40
        `,
        pointerEvents: 'none',
        zIndex: 0,
      }} />
    </div>
  );
};

/* ── 主组件（外层） ────────────────────────────────── */

export const StickerContent: React.FC = () => {
  return (
    <div>
      __SEQUENCES__
    </div>
  );
};
