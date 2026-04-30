# Changelog - wechat-sticker-skill

All notable changes to this skill are documented in this file.

## v3.3.0 (2026-04-30)

### 方案D · 场景构图系统（重大重构）

- **重构布局引擎**：网格平铺 → 场景构图（BG → FOCUS → ACCENT 分层合成）
  - 新增4种zone场景：`outer_ring`（单主体外围8方位）| `fill_gaps`（双主体缝隙填补）| `top_bottom`（三主体上下两端）| `full_scatter`（无主体全场弥散）
  - 语义映射表 `ELEMENT_SCENE_ROLE`：关键词 → 场景角色（FOCUS/ACCENT/BG）
  - 角色映射扩展：数学公式/AI图标/手写识别框 → ACCENT（不再误判为主体）
  - 每个元素独立位置：不再共享布局，每个元素对应一个独立绘制区域
  - 语义角色定义：FOCUS=居中放大，ACCENT=小尺寸散布

### 词汇表驱动（v3.2）

- **重构绘制引擎**：name路由 → `visual_elements`词汇表驱动
  - 词汇表注册表 `ELEMENT_VOCAB`：中英文别名 → 绘制函数
  - 智能网格布局算法：根据元素数量自动排列（1/2/3/N个元素）
  - 回退机制：词汇表无匹配时自动回退到name-based专用函数
  - 新项目无需编写代码，只需要在prompts中描述 `visual_elements`

### ai-math-notes 专属视觉函数

- 新增6个专属视觉函数：画布手写 / AI计算 / 等号求解 / MathNotes / 清空重写 / 答案揭晓
- SKILL.md 路由表：warp-terminal 6个 + ai-math-notes 6个 = 12个视觉函数

### generate_stickers.py 修复

- [修复] `parse_prompt_file` 返回值与 `main()` 解包数量不匹配（返回5值: name/text/copy/visual_elements/style_keywords）
- [修复] `STICKER_SIZE=500` → `W=1080, H=1440`（微信贴图标准）
- [修复] 字体大小按1080×1440比例放大（60→140等，约×2.2）
- [重构] 所有风格 `Image.new` 背景从实色不透明改为透明 `RGBA(0,0,0,0)`
- [重构] 圆形遮罩只应用于背景层，文字层独立绘制不受裁切
- [修复] 文字底部改为以画布底边为基准（`y=H-30=1410`），圆形主题文字不再被裁切
- [修复] WARP标签位置：改到主文字上方（`label_draw`在`text_bottom_draw`之前绘制，`y=tt-行高-8`）
- [修复] `alpha_composite`层叠顺序：bg_layer在下、text_layer在上，文字完全覆盖背景
- [完成] T1.1 圆形遮罩羽化（GaussianBlur r=15，边缘alpha渐进过渡）
- [完成] T1.4 文字发光效果（8层外发光 + 4层中发光 + 黑色描边 + 白字）
- [完成] 字体大小 120→110px（减10）

### SKILL.md 更新

- [更新] 版本 2.0.0 → 3.3.0
- [新增] Prompt 格式 v3.0：`visual_elements` + `style_keyword` frontmatter 字段
- [新增] 实际项目 Prompt 示例（warp-terminal：AI补全、命令面板）
- [新增] 每张贴图的专属视觉生成规则（name→视觉函数路由机制）
- [更新] Manifest 格式 v3.0：引用 prompts 中的 visual_elements，不再重复写入文案
- [更新] 项目目录结构：新增 `assets-{theme}/` 多风格目录
- [新增] 四阶段图片生成工作流（阶段一PIL → 阶段二AI混合 → 阶段三评估 → 阶段四自动化）
- [新增] 阶段二AI主体生成：nano-banana-pro + 调色一致性方案
- [新增] 阶段三质量评估维度表（光影/丰富度/文字精度/一致性/成本）
- [新增] 阶段四自动化功能规划（`--mode ai-bg` / `--seed` / `--ai-provider`）

## v3.1 核心机制

- 每张贴图通过 `name` 字段路由到专属 PIL 绘图函数（6种已实现）
- 文字固定在画布底部（距底边30px），不受圆形遮罩影响
- 背景层应用圆形遮罩（R=500），文字层独立叠加
- 支持7种风格：cyberpunk / kawaii / neon / retro / hand-drawn / minimal / meme

## v3.0 初始版本

- 四阶段图片生成工作流：阶段一PIL本地生成 → 阶段二AI背景+PIL合成 → 阶段三质量评估 → 阶段四自动化集成
