# 更新日志

All notable changes to the wechat-sticker-skill are documented here.

## [4.7.0] - 2026-05-02

### StickerContent.tsx 清理（E 类）

- **E1**: 删除未使用的 `floatY()` 函数（float 动画已内联在 EmojiItem 内）
- **E2**: 删除未引用的 `TOTAL` 常量
- **E3**: 移除 CopyText 内层 span 重复的 `position: relative` 声明

### StickerContent.tsx 视觉增强（F 类）

- **F1 — 遮罩外发光呼吸环**: 在原有 `boxShadow` 层外新增第二层外发光环（`H*0.94` 尺寸），透明度随 `glowOpacity` 脉动，实现 border-glow 视觉效果
- **F2 — 全动画入场 overshoot**: 新增 `overshoot(t)` 函数（`1 + sin(t*π)*0.08`），所有动画类型（bounce/spin/glow/float/shake）入场时均有 8% 弹性 overshoot，float/shake 不再是静态 scale
- **F3 — 遮罩对角高光描边**: 在遮罩层叠加 SVG 层，使用 `<linearGradient>` 实现左上+右上对角渐变线（`diagStroke` / `diagStroke2`），透明度受 `enterF` 控制
- **F4 — EmojiItem 动态阴影强度**: `shadowIntensity = enterF * exitF`，入场→退场全程跟随，淡出时阴影同步消失；分两层 `drop-shadow`（内层 20px / 外层 48px）

## [4.6.0] - 2026-03-30

### StickerContent.tsx 动画修复（A 类）

- **A1**: `exitScale(enterF, exitF) = enterF × (0.6 + 0.4×exitF)` — 退场时 emoji + 遮罩同步收缩
- **A2**: `textFlash` 条件冻结闪烁，`fl = (enterF > 0.9 && exitF > 0.5) ? flash(t) : 1`
- **A3**: `textEnterScale(localFrame)` — CopyText wrapper 入场 scale(0.5→1) + opacity(0→1)
- **A4**: `shimmerOffset(localFrame)` — diagonal conic-gradient 高光 sweep 动画（30%→70%）
- **A5**: `shakeX(f, exitF) = Math.sin(f×3.7)×8×exitF` — 退场时自然衰减

### 主题配置统一（C 类）

- **C1**: `fontSize = Math.round(W × 0.033)`（36px@1080），`emojiSize = Math.round(W × 0.074)`（80px@1080）
- **C2**: 深色主题 dots/grid 透明度分级（isDark ? 40% : 20%）
- **C3**: `boxShadow` 强度差异化（isDark ? ×1.4 : ×0.7）

### CSS 单一来源（B 类）

- **B1+B2**: `generate_frames.py` 的 CSS 精简为 2 行（无 `:root` 变量块）
- **B3**: `StickerComponentProps` 显式类型定义，Python 替换为实际值

## [4.4.1] - 2026-03-30

- 完整重构：三段式降级（AI → Remotion → PIL）
- 新增 `--continue-on-error`、`--debug-remotion`、`--dry-run` 参数
- `pack_stickers.py` 支持 `--gif-only` / `--png-only`
