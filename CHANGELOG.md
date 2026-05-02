# 更新日志

All notable changes to the wechat-sticker-skill are documented here.

## [4.9.1] - 2026-05-03

### 彻底移除 PIL 依赖

**问题**：技能中仍有 4 个文件依赖 PIL（pack_stickers.py、qa_check.py、_vocab.py、generate_frames.py），违背两段式架构承诺。

**变更**：

- **P-1**: 删除 `scripts/pil_fallback.py`（独立降级脚本，已废弃）
- **P-2**: 重写 `scripts/pack_stickers.py` — 封面/缩略图生成从 PIL 改为 ffmpeg `tile` 滤镜
- **P-3**: 重写 `scripts/qa_check.py` — 图片尺寸读取从 PIL 改为 struct 直接解析 PNG/GIF 头
- **P-4**: 清理 `scripts/_vocab.py` — 移除 `get_font()`、`FONT_PATHS`、`_FONT_CACHE`（从未被调用）
- **P-5**: 重写 `scripts/generate_frames.py` — `_frames_to_gif()` 改为 ffmpeg `paletteuse`；`get_font()` 完全删除（从未被调用）；fetch_image 中的图片处理改为 ffmpeg
- **P-6**: `docs/output.md` — PIL 缩放示例改为 ffmpeg 示例
- **P-7**: `docs/qa.md` — `FONT_PATHS` 相关解决方案改为字体安装建议

**保留**：Remotion 项目中 `node_modules` 的 `@remotion/bundler` 等包依赖 PIL（Chromium/Puppeteer 内部），属于 Remotion 自身依赖，无法也不应移除。

**P-8**: 删除 `scripts/generate_stickers.py`（废弃桩，已被 run_full_pipeline.py 取代）

**P-9**: 删除 `scripts/generate_cover.py`（废弃桩，已被 pack_stickers.py 取代）

**P-10**: `docs/qa.md` — `Image.resize()/save()` 改为 ffmpeg scale/crop

**PIL 零残留**：技能所有 Python 脚本（总计 3669 行）不再依赖 PIL。

## [4.9.0] - 2026-05-03

### 架构变更：移除 PIL 兜底，改为两段式

**问题**：PIL 作为第三层降级方案实际上从未被需要，反而增加了维护负担（`pil_fallback()` 函数、`--mode pil` 参数、文档中的大量 PIL 说明）。

**变更**：

- **G-1**: `generate_frames.py` 重写——移除 `pil_fallback()`、`_background_pil_worker()`、`_pil_precomputed` 缓存、`--mode pil`、`--parallel` 参数；`failure_rate > 0.5` 和 `available_frames < 10` 条件从"降级 PIL"改为"抛出 RuntimeError"
- **G-2**: `docs/image-generation.md` 重写——移除阶段三（PIL 本地生成），流程图从三段式改为两段式
- **G-3**: `docs/qa.md` 移除"所有 API 不可用"、"AI 生成全部失败"、"降级到 PIL"三个故障排除条目；Remotion 导出失败解决方案从"降级到 PIL"改为"检查 Node.js 安装，升级 Remotion 版本"
- **G-4**: `docs/output.md` 移除 PIL 相关说明（格式描述、生成方式选项、PIL 缩放命令）
- **G-5**: `docs/frame-design.md` 移除"为什么不用 PIL"章节
- **G-6**: `docs/remotion-projects.md` 移除"自动降级路径"章节（整个降级流程图），替换为"异常处理"章节
- **G-7**: `docs/session-log-template.md` 模式描述从"AI → Remotion → PIL 自动降级"改为"AI → Remotion 两段式"
- **G-8**: `SKILL.md` 版本 4.8.5 → 4.9.0；所有"三段式"/"PIL"相关描述更新为两段式；移除 `--mode pil` 参数说明
- **G-9**: `run_full_pipeline.py` 版本注释待更新（由脚本自行维护）
- **G-10**: `prompts-format.md` 词汇表描述中"PIL elem_fns"改为"Remotion elem_fns"

**保留**：`scripts/pil_fallback.py` 独立脚本文件保留，供需要完全离线生成的场景使用，但不再作为技能的标准降级路径。

## [4.8.5] - 2026-05-03

### 新增：微信公众号推广文档生成

**问题**：缺少用于微信公众号发布的推广文档。

**修复**：

- **P-1**: 新增 `scripts/generate_post.py` — 生成微信公众号推广文档，包含标题（≤20字）、内容（≥60字，含链接）、标签（≥5个 `#标签` 格式）
- **P-2**: `run_full_pipeline.py` 新增步骤 8（`--with-post`，默认开启），接入 `_post_step()` 函数
- **P-3**: 新增 `--link` 参数，传递项目链接到 post.md
- **P-4**: `generate_post.py` 从 `content-analysis.md` 提取项目描述，从 `tags.md` 提取标签，标题从模板库随机选择
- **P-5**: `SKILL.md` 脚本列表新增 `generate_post.py`

## [4.8.4] - 2026-05-03

### Remotion CLI 架构问题文档化

**问题**：`npx remotion still` 报错 `width prop must be a number, but passed undefined`，以及 `--props` 无法穿透到 `<Composition>` 的 JSX 属性。这导致 opengeometry 项目的 Remotion 架构验证失败。

**根因**：
1. Discovery 阶段：`registerRoot` 注册的工厂组件被立即调用一次（props=undefined），`<Composition width={width}>` 无默认值时抛验证错误
2. `--props` 限制：传给 `registerRoot` 的 props 无法穿透到 `<Composition>` 的 JSX 属性

**修复**：

- **R-1**: `remotion-projects.md` 更新示例代码，使用 `??` 为 `<Composition>` 所有数值属性提供 fallback 值
- **R-2**: `remotion-projects.md` 新增 `## CLI 命令限制` 章节（52行），记录 Discovery 阶段行为、`--props` 穿透限制、输出尺寸异常说明
- **R-3**: `remotion-projects.md` 标题改为"核心规范"，删除对外部 `remotion-best-practices` skill 的引用
- **R-4**: `qa.md` 新增 `### Remotion CLI 调试技巧` 章节（47行），记录错误症状、根因、解决方案、验证命令、正常渲染验证方法
- **R-5**: 删除调试过程中的临时文件：`StillEntry.tsx`、`render-still.ts`

**验证结论**：
- `remotion still` + `??` fallback → 单帧可正常导出（`out/StickerComponent.png`，1523×2030）
- `??` fallback 只在 Discovery 阶段生效，正常渲染时外层 props 覆盖 fallback，**不干扰正常视频渲染**

### 文档一致性修复

- **O-1**: `run_full_pipeline.py` 标题版本 `v4.8.2` → `v4.8.4`
- **O-2**: `copy_docs.py` 从复制列表中移除 `session-log-template.md`（模板由 `generate_session_log.py` 直接渲染到项目，不走复制流程）
- **O-4**: `frame-design.md` 更新 `remotion still` 说明——移除"不支持 GIF 输出"的误导表述，改为记录 Discovery 阶段 `??` fallback 要求及调试用法
- **O-5**: 新增 `docs/copy.md`（文档复制说明），明确哪些文档复制到项目、哪些由脚本生成，并加入 `copy_docs.py` 复制列表和 SKILL.md 文档列表

## [4.8.3] - 2026-05-02

### 规范修订：Tags 章节缺失 + session-log-template 不应拷贝到项目

**问题**：`workflow.md` 缺少 Tags 标签记录规范章节；`session-log-template.md` 被标记为"自动填充"但未说明它留在技能内不拷贝到项目。

**修复**：

- **F-1**: `workflow.md` 新增 `## Tags 标签记录规范` 章节（含功能、参数、标签类别、示例）
- **F-2**: `SKILL.md` docs 列表说明改为"按需复制到项目 docs/"，`session-log-template.md` 注释明确"由 generate_session_log.py 使用，不拷贝到项目"

## [4.8.2] - 2026-05-02

### 修复"规范要求的文档从未生成到项目"问题

**问题**：技能规范在 `workflow.md` L88 明确要求"每次生成贴图包必须填写 `docs/session-log.md`"，在 `prompts-format.md` L509 提及 session-log 关联记录，`generate_tags.py` 存在但从未接入工作流。这些内容最终流入了 session log 而非项目文件。

**修复**：

- **S-1**: 新增 `docs/session-log-template.md` 模板
- **S-2**: 新增 `scripts/generate_session_log.py`，从模板生成 `docs/session-log.md`
- **S-3**: 将 `generate_tags.py` 接入 `run_full_pipeline.py` 步骤 5.5（默认开启）
- **S-4**: 新增 `--with-docs/--no-docs`（步骤0，默认开启）、`--with-tags/--no-tags`（步骤5.5）、`--with-session-log/--no-session-log`（步骤7，默认开启）
- 工作流版本升至 v4.8.2

## [4.8.1] - 2026-05-02

### 文档自动复制到项目（v1）

- **T-1**: 新增 `scripts/copy_docs.py`
- **T-2**: `run_full_pipeline.py` 新增步骤0（`--with-docs/--no-docs`，默认开启）

## [4.8.0] - 2026-05-02

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
