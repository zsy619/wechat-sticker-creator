/**
 * EmojiElement.tsx - 可复用的 emoji 元素组件
 * 
 * 支持的 visual_elements：
 * - brain        → 🧠
 * - terminal     → 💻
 * - lightning    → ⚡
 * - heart        → ❤
 * - equals_sign  → =
 * - question_mark→ ?
 * - eraser       → 🧹
 * - checkmark    → ✓
 * - math_canvas  → 📐
 * - ai_chip      → 🤖
 */

import { useCurrentFrame, interpolate, spring } from 'remotion';

type EmojiElementProps = {
  /** visual_elements 中的键名 */
  elementKey: string;
  /** 主题主色（用于发光效果） */
  themeColor: string;
  /** 是否启用呼吸动画 */
  glowEnabled?: boolean;
  /** 额外的内联样式 */
  style?: React.CSSProperties;
};

const EMOJI_MAP: Record<string, string> = {
  brain: '🧠',
  ai大脑: '🧠',
  ai计算: '🧠',
  神经网络: '🧠',
  neural_network: '🧠',
  terminal: '💻',
  终端窗口: '💻',
  lightning: '⚡',
  闪电: '⚡',
  heart: '❤',
  红心: '❤',
  equals_sign: '=',
  等号: '=',
  question_mark: '?',
  问号: '?',
  eraser: '🧹',
  橡皮擦: '🧹',
  checkmark: '✓',
  对勾: '✓',
  math_canvas: '📐',
  canvas: '📐',
  画布: '📐',
  ai_chip: '🤖',
  芯片: '🤖',
};

export const EmojiElement: React.FC<EmojiElementProps> = ({
  elementKey,
  themeColor,
  glowEnabled = true,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const emoji = EMOJI_MAP[elementKey] || '❓';

  const glowOpacity = glowEnabled
    ? interpolate(
        spring({ frame, fps: 30, config: { damping: 200, stiffness: 10 } }),
        [0, 1],
        [0.3, 1]
      )
    : 1;

  return (
    <div
      style={{
        opacity: glowOpacity,
        fontSize: 200,
        filter: glowEnabled
          ? `drop-shadow(0 0 20px ${themeColor})`
          : undefined,
        ...style,
      }}
    >
      {emoji}
    </div>
  );
};
