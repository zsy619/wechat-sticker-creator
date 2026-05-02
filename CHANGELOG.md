# Changelog - wechat-sticker-skill

## v4.4.0 (2026-05-02) - Remotion 构建流程全面优化

### P0 关键修复（Remotion 流程现在真正可工作）

- **P0-1**: `npx remotion render --frames` 参数不存在 → 改用 `npx remotion still` 逐帧渲染 PNG，然后 PIL 合成 GIF。断点续传：已存在的帧跳过
- **P0-2**: `check_remotion_available()` 仅检查 `npx --version` → 新增 `_check_remotion_environment()` 全面预检（npx + Remotion CLI + 版本兼容性）
- **P0-3**: GIF 合成逻辑修复 — `generate_remotion_gif()` 现在正确渲染 90 帧 PNG，再通过 `_frames_to_gif_from_paths()` 用 PIL 合成 GIF

### P1 稳定性与性能提升

- **P1-1**: 持久化 Remotion 项目缓存于 `~/.cache/wechat-sticker-remotion/` — 新项目从缓存复制（跳过 npm install），节省 10-30s/次
- **P1-2**: 版本自动检测 — `get_remotion_version()` 读取全局 `npx remotion --version`，不一致时输出 WARN；`--remotion-version` 参数覆盖
- **P1-3**: 错误友好化 — `_parse_remotion_error()` 识别 10 种常见错误模式（delayRender timeout / chromium not found / JSX syntax error 等），输出可操作的建议
- **P1-4**: 动态超时 — `timeout = max(120, total_frames * 2)`，替代固定 600s

### P2 可维护性与调试体验

- **P2-1**: 独立渲染日志 — `project_dir/logs/render_{N}.log` 记录每张贴图的 stdout/stderr/returncode
- **P2-2**: `--continue-on-error` 批量处理 — 失败贴图跳过继续，最终报告成功/失败统计
- **P2-3**: 帮助文档更新 — `--help` 输出包含全部新参数的完整 Usage
- **P2-4**: `--debug-remotion` 调试模式 — `debug/` 目录保留写入的 TSX 源码

### P3 架构改进

- **P3-1**: 模板热重载检测 — `.template_mtime` 记录模板修改时间，有变更则强制重建项目
- **P3-2**: `--template-dir` 自定义模板 — 覆盖内置 `remotion/template/` 路径
- **P3-3**: 后台 PIL 预计算 — Remotion 渲染期间同时启动 PIL 生成，失败时立即使用预计算结果降级

### 代码质量

- `generate_frames.py` 从 833 行 → 1222 行（含完整注释和新增函数）
- 全部 Python 文件通过 `py_compile` 语法检查
- `_EMOJI_FALLBACK` 常量内联化，替代多处重复硬编码
- `pil_fallback()` 保持与 v4.3.5 行为完全一致（无破坏性变更）

### 第二轮优化（v4.4.1，2026-05-02）

#### P3-3-FIX: `_background_pil_worker` 假并发修复
- **问题**：`threading.Thread(target=lambda: [list comprehension])` — lambda 同步执行列表推导，线程形同虚设
- **修复**：改用 `ThreadPoolExecutor(max_workers=N)` + `executor.submit()` 真正并发调度

#### P2-5: `--dry-run` 预览模式
- `generate_frames.py` 新增 `--dry-run` 参数，解析所有 `.md` 文件并打印每张贴图的主题/关键词/视觉元素，不生成任何文件

#### P2-6: `--gif-only` / `--png-only` 过滤
- `pack_stickers.py` 新增两个互斥过滤参数，`create_zip` / `generate_cover` / `generate_thumbnail` 全部受同一 filter 控制

#### P2-7: 缩略图布局保护
- `generate_thumbnail()` 新增 `MAX_THUMB=20` 限制，超出部分截断（原来 20 张贴图在 200×267 规格下每行高度仅 ~13px，多张时更小至不可读）
- 缩略图输出文件名 `thumbnail-` → `thumb-`（更简洁）

#### PIPELINE: v4.4.0 flags 透传
- `run_full_pipeline.py` 新增 `--continue-on-error` / `--debug-remotion` / `--template-dir` / `--remotion-version` 参数，正确透传到 `generate_frames.py`

### 代码行数变化

| 文件 | v4.3.5 | v4.4.0 |
|------|--------|--------|
| `generate_frames.py` | 833 | 1222 |
| `SKILL.md` | 186 | ~222 |

---

## v4.3.5 (2026-05-01) - Emoji分布 + 词汇表完整性 + __init__.py

### 高严重修复

- **FIX-F2**: `generate_frames.py` 的 `generate_pil_frames()` 函数（line ~705）— emoji 兜底渲染仍为同一坐标 Bug，修复为与 `pil_fallback.py` 一致的横向均匀分布（`emoji_elements` 列表 + `start_x + i*120`）
- **FIX-F1**: `generate_manifest.py` — 移除 `build_manifest_prompt()` 内的 `from _vocab import VOCABULARY as _VOCAB` 本地 import，避免遮蔽模块级 `VOCABULARY`（该文件顶部已 `from _vocab import VOCABULARY`）；同时将 `THEMES` 加入顶部导入
- **FIX-F3**: `generate_content_analysis.py` 的 fallback THEMES（`_vocab` 不可用时的内嵌副本）— 补全所有 5 键（`primary/secondary/bg/text/accent`），原来仅 3 键

### 词汇表扩充

- **FIX-F4**: `generate_frames.py` 两处 emoji_map fallback（新扩充的 fallback 副本）— 补全 `_vocab.EMOJI_MAP` 独有而原来 fallback 未覆盖的 key，包括 ai/robotic_arm/wifi/server/database/virus/race_car/helicopter/boom/zap/impact/vs/versus/gender系/heart系/melt/absolutely/tiger/dragon/fairy/ghost/skull/天气类/植物类等约 40 个 key

### 基础设施

- **FIX-F5**: `scripts/__init__.py` — 新建空 `__init__.py`，使 `scripts/` 成为合规 Python 包，解决直接运行脚本时 `from _vocab import` 的模块解析问题

### 验证通过

- 全部 12 个 Python 文件通过 `py_compile` 语法检查
- `_vocab.py` 导入验证：`VOCABULARY`=281 keys（set）、`EMOJI_MAP`=169 keys（dict）、`THEMES`=7 themes
- `filter_valid_keys(['brain','terminal','ai_chip'])` → valid=['brain','terminal','ai_chip']，invalid=['invalid_key'] ✅
- `generate_frames.py` 总行数：834 行（从 801 行增加 33 行）

### 高严重修复

- **FIX-1**: `run_full_pipeline.py` — `cwd=script_dir` 拼写错误修复为 `cwd=cwd`（参数默认值生效）
- **FIX-2**: `qa_check.py` — `valid_themes` NameError 修复（移除无效的变量引用）
- **FIX-3**: `pil_fallback.py` — emoji 兜底渲染重叠 Bug（所有 emoji 画在同一坐标）修复为横向均匀分布

### 数据源统一

- **FIX-6**: `generate_frames.py` 两处 emoji_map 改为从 `_vocab.EMOJI_MAP` 导入（优先），fallback 保持内嵌副本
- **FIX-7**: `generate_frames.py` 和 `pil_fallback.py` 的 THEMES 改为从 `_vocab.THEMES` 导入（优先），fallback 保持内嵌副本
- **FIX-4**: `generate_prompts.py` / `generate_tags.py` — `_vocab` import 添加 try/except fallback（防止 _vocab 不存在时崩溃）

## v4.3.3 (2026-05-01) - Theme流 + 格式约束 + 竖版裁剪

### 修复

- **T-1.5**: `--theme` 参数现在正确传递给 LLM prompt（build_content_analysis_prompt 新增 theme 参数）
- **T-2.4**: `generate_manifest` 从 content-analysis 的 recommended_theme 字段提取主题，并写入 manifest 的 **推荐主题** 字段
- **T-2.3**: `build_manifest_prompt` 使用 _vocab.VOCABULARY（281 key）提供词汇表约束，并增加严格 YAML frontmatter 格式示例
- **T-1.3**: `fetch_url()` 移除对不存在的 baoyu-url-to-markdown 依赖，改用 curl + User-Agent 头
- **T-2.2**: `parse_manifest` style 字段解析支持多种格式（主题键/风格/主题/recommended_theme）
- **T-4.5**: Remotion --frames 参数验证（已确认正确：start-end 格式）
- **T-6.2**: `qa_check.py` 新增 manifest 推荐主题合规性检查（check_manifest_compliance）
- **T-4.6**: `generate_frames.py` AI 图像下载后增加竖版 3:4 中心裁剪逻辑（应对 API 返回方图/横图）

### 清理

- 修复 `fetch_url()` 死代码（line 61 return 后不可达语句）

## v4.3.2 (2026-05-01) - 共享模块 + 致命Bug修复

### 架构改进

**T-2.1+T-3.1 — VOCABULARY 统一为共享模块**：
- 新建 `scripts/_vocab.py`：单一数据源，包含 VOCABULARY（80+ key）、THEMES（7主题）、filter_valid_keys()
- `generate_manifest.py` 和 `generate_prompts.py` 的内嵌 VOCABULARY 已移除，改为从 `_vocab` 导入
- 消除三份副本不同步的根本性问题

**T-5.1 — 新建 `scripts/generate_tags.py`**：
- 根据 manifest 或 prompts 目录，生成微信贴图标签推荐文档（tags.md）
- 内置 WECHAT_STICKER_TAGS 词库（7分类，80+ 标签）
- THEME_TAG_MAP 自动推荐主题相关标签

**T-TOP.3 — SKILL.md 目录结构更新**：
- 新增 `_vocab.py`（共享词汇表）和 `generate_tags.py`（标签生成）的说明
- 8个脚本时代（原来2个）

### Bug 修复

**T-1.1 — generate_content_analysis.py 致命崩溃修复**：
- `call_llm()`：移除 `hermes_tools.call_llm()`（模块不存在），改用 `subprocess.run(['claude', '--print', '-p', prompt])`
- `web_search()`：移除 `subprocess.run(['WebSearch', ...])`（CLI 不存在），改用 `claude --print -p search`
- THEMES：从内嵌副本改为从 `_vocab` 导入（统一数据源）
- `detect_input_type()`：改进纯英文短词判断，`re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_-]*', raw)` 避免误判

**T-3.2 — parse_manifest() visual_elements 正则解析改进**：
- 修复脆弱正则 `re.findall(r'[`"（）()【】\[\]a-zA-Z_]+')` → `re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*')`
- 支持下划线/数字复合词（neural_network、debug_log 等）

**T-4.4 — AI API size 参数改为竖版 3:4**：
- seedream：`height: 1024` → `height: 1360`（3:4 竖版）
- minim：`height: 1024` → `height: 1360`（3:4 竖版）
- 避免 1:1 方形图在竖版贴图中的裁剪损失

**T-6.1 — qa_check.py 改用 frontmatter 解析**：
- 新增 `_parse_frontmatter()`：按行解析 YAML frontmatter
- 新增 `_parse_list()`：安全解析 `[a, b, c]` 列表
- `parse_prompts_vocabulary()` 改用 frontmatter 解析，替代脆弱正则
- 优先使用 `_vocab` 共享词汇表（`--vocabulary` 参数降级）

**T-5.2 — pack_stickers.py 缩略图高度安全整数除法**：
- `thumb_h = h // len(files)` → `count = max(1, len(files))` + `thumb_h = h // count`
- 防止 len(files)==0 时崩溃

**T-TOP.1 — run_full_pipeline.py 捕获 subprocess stdout/stderr**：
- `subprocess.run()` 增加 `capture_output=True, text=True`
- 失败时打印 stdout/stderr（各最多1000字符），成功时打印 stdout（最多500字符）
- 修复 `cwd=script_dir`（原来错误使用 `cwd=cwd`）

**T-4.1+T-4.2 — elem_fns 确认同步**：
- `pil_fallback.py` 与 `generate_frames.py` 的 elem_fns 22个函数逐行对比，完全一致
- emoji 渲染逻辑使用 `emoji_map.get(elem)` 安全查找，无空字符串 bug

### 清理

**T-TOP.2 — 废弃老文件**：
- `generate_stickers.py`（59KB）：重写为仅包含废弃警告的哑元脚本
- `generate_cover.py`（10KB）：重写为仅包含废弃警告的哑元脚本



### 新增脚本（节点间自动化）

**T-TOP.1 新建**：
- 新建 `scripts/run_full_pipeline.py`：顶层串联入口，一次性执行完整工作流（内容聚合 → manifest → prompts → 图片生成 → 打包 → QA）
- 支持 `--mode` 参数：auto / full / analysis / manifest / prompts / frames / qa / pack

**T-1.1 新建**：
- 新建 `scripts/generate_content_analysis.py`：内容聚合分析脚本，支持 URL / 主题词 / 纯文本三种输入类型，自动联网搜索 + LLM 聚合，输出 `content-analysis.md`

**T-2.1 新建**：
- 新建 `scripts/generate_manifest.py`：贴图设计 manifest 生成脚本，内置 vocabulary 校验（80+ key），输出 `sticker-manifest.md`

**T-3.1 新建**：
- 新建 `scripts/generate_prompts.py`：从 manifest 生成 prompts 文件脚本，支持 vocabulary 校验 + theme 配色自动填充，输出 `prompts/{num}-{name}.md`

**T-5.1 新建**：
- 新建 `scripts/pack_stickers.py`：ZIP 打包 + 封面图生成（公众号封面 900x383）+ 缩略图生成（200x267），支持 PIL 拼贴

**T-6.1 新建**：
- 新建 `scripts/qa_check.py`：QA 自动化检查脚本，支持尺寸校验（1080×1440）、格式校验（PNG/GIF）、文件名格式校验、词汇表合规性校验

### Bug 修复

**T-4.2 修复**：
- 修复 `generate_frames.py` line 414：`emoji_map.get(e, "")` 改为 `emoji_map[e]` + 过滤不存在 key，消除空字符串渲染 bug

**T-4.3 修复**：
- 统一 `SKILL.md` 与 `generate_frames.py` 的 `--mode` 参数说明，SKILL.md 新增完整工作流命令序列

### 文档修复

**DOC-1 修复**：
- 修复 `docs/content-format.md`：`visual_elements` 词汇表改为英文 key（与 prompts-format.md 一致），修正表格双竖线格式

**DOC-2 补充**：
- 补充 `docs/prompts-format.md`：新增「manifest 验证规则」节和「从 manifest 生成 prompts」说明节

**DOC-3 补充**：
- 补充 `docs/output.md`：新增「自动化打包」节（含 `pack_stickers.py` 用法）和「标签生成」节（含 `generate_tags.py` 用法）

**DOC-4 补充**：
- 补充 `docs/qa.md`：新增自动化 QA 流程（`qa_check.py`）+ 手动复核清单分离，结构化为表格

### SKILL.md 更新

- scripts 目录列表从 2 个扩充至 8 个（所有新增脚本已列入）
- 版本号升至 v4.3.1
- 快速开始新增完整 pipeline 命令序列

---

## v4.3.0 (2026-05-01) - 三段式生成器全面完善

### generate_frames.py 核心修复

**T-1 修复**：
- 新增 `seedream` provider（火山引擎 doubao-seedream-5-0-260128），支持 `VOLCENGINE_API_KEY` / `SEEDREAM_API_KEY` 环境变量
- 新增 `_call_ai_provider()` 统一 HTTP 调用函数：429 自动重试（10s 等待，最多3次）、超时/网络错误降级、401/402/403 认证错误跳过
- Provider 优先级：dashscope → seedream → minimax → openai

**T-3 修复**：
- `elem_fns` 扩充至 22 个绘制函数，新增 `code`（代码窗口）、`algorithm`（流程图）、`function`（ƒ(x)=）、`variable`（x=???）、`bio`（DNA双螺旋）、`secret`（*** + CLASSIFIED）
- 新增 `emoji_map` 兜底渲染逻辑，覆盖 80+ 词汇表所有 emoji 元素
- 移除原有的 `if True else None` 冗余表达式

### scripts/pil_fallback.py 独立脚本新建

**T-2 新建**：
- 创建独立 `pil_fallback.py` 脚本，与 `generate_frames.py` 解耦
- 支持 `--input/--output/--theme` 参数
- 内嵌完整 `elem_fns` + `emoji_map`，覆盖全部 80+ 词汇
- 可独立运行：`python3 scripts/pil_fallback.py --input prompts/ --output assets/ --theme cyberpunk`

### image-generation.md 文档修复

**T-4 修复**：
- 修正标题从"导出 PNG"改为"导出 GIF（带动画）"
- 添加说明：`npx remotion still` 导出单帧 PNG，`npx remotion render` 导出多帧 GIF

### StickerContent.tsx 清理

**T-5 修复**：
- 移除外层组件中冗余的 `useCurrentFrame()` 调用
- 注释更新为"不直接参与动画"，明确职责划分

### 演示项目

**T-6 新建**：
- 新建 `demo/ai-coding-assistant/` 完整贴图项目（6张贴图）
- `content-analysis.md` + `sticker-manifest.md` + `prompts/01-06.md` + `copy.md` + `assets/` 完整闭环
- 覆盖场景：代码秒写 / Bug秒解 / 一键部署 / 代码审查通过 / 摸鱼被发现 / 下班收工
- PIL 生成验证通过：6/6 张贴图全部成功

---

## v4.2.0 (2026-05-01) - Remotion 模板修复

### StickerContent.tsx 架构修复

**问题**：原模板外层组件直接调用 `useCurrentFrame()` 但实际动画逻辑在子组件中，职责不清。

**修复**：
- `StickerScene` 内层组件独立使用 `useCurrentFrame()`，通过 `frameOffset` 修正本地帧
- 外层 `StickerContent` 保持 `useCurrentFrame()` 调用以满足 Remotion 要求，但不直接参与动画
- `localFrame = frame - frameOffset` 确保每张贴图从第0帧开始播放

### 字体大小修复

**问题**：底部文案 `fontSize: 150` 对 1080px 宽度过大。

**修复**：调整为 `fontSize: 90`（竖屏规范 ≤96px）。

### 圆形遮罩添加

**问题**：cyberpunk/neon/kawaii 主题缺少圆形边框效果。

**修复**：添加圆形遮罩层，带 `boxShadow` 霓虹光效。

### text-shadow 修复

**问题**：原 `neonTextShadow` 函数使用模板字符串插值 `${PRIMARY}`，在某些场景下可能出现解析错误。

**修复**：改用字符串拼接，确保颜色值正确注入。

---

## v4.1.0 (2026-05-01) - GIF 动画 & 字体特效

### 重大变更：PNG → GIF 动画

所有贴图输出格式从静态 PNG 升级为动态 GIF：

| 项目 | 原值 | 新值 |
|------|------|------|
| 命令 | `remotion still` | `remotion render --frames 0-89` |
| 帧数 | 1 帧 | **90帧**（3秒@30fps） |
| 输出 | PNG (单帧) | **GIF**（动画） |
| `durationInFrames` | 1 | **90** |

### frontmatter 解析修复

`parse_prompt_file()` 之前在遇到第一个 `---` 后立即 break，导致 frontmatter 从未解析。修复为状态机：遇到第二个 `---` 才 break。

### `_parse_list()` 安全解析

`visual_elements: [黑色画布, 白色笔迹]` 中的中文词无法直接 `eval()`。新增 `_parse_list()` 函数手动解析逗号分隔数组，避免 NameError。

### emoji_map 键值标准化

`visual_elements` 中的 key 必须与 emoji_map 键完全匹配（中文 key → 英文 key）：

```yaml
# ✅ 正确
visual_elements: [math_canvas, brain, equals_sign]

# ❌ 错误（中文词不在 emoji_map 中）
visual_elements: [黑色画布, 白色手写笔迹, 数学公式]
```

### emoji 词汇表更新

| 元素键 | emoji | 备注 |
|-------|-------|------|
| brain / ai计算 / 神经网络 | 🧠 | |
| math_canvas / canvas / 画布 | 📐 | 新增 math_canvas |
| equals_sign / 等号 | ＝ | 使用全角符号避免 JSX `=` 语法冲突 |
| question_mark / 问号 | ？ | 使用全角符号 |
| ai_chip / 芯片 | 🤖 | |
| eraser / 橡皮擦 | 🧹 | |
| checkmark / 对勾 | ✓ | |
| neural_network | 🧠 | 新增 |
| terminal / 终端窗口 | 💻 | |
| lightning / 闪电 | ⚡ | |
| heart / 红心 | ❤ | |

### JSX 双括号转义

Python 生成 JSX HTML 时，`style={...}` 中的 `{}` 必须双写。修复方式：使用**字符串拼接**而非 f-string 插值。

```python
# ✅ 正确
span_base = "{{fontSize:260,lineHeight:1}}"
emojis_html += "  <span style=" + span_base + ">" + em + "</span>\n"

# ❌ 错误（f-string 中 {{ 仅为 {）
emojis_html += f'  <span style={{fontSize:260}}>{em}</span>\n'
```

### `__ELEMENTS_HTML__` 注入点修复

模板中 `__ELEMENTS_HTML__` 原来在 JSX 注释中，无法渲染。修复为直接嵌入 `<div>` 容器内的 JSX 元素。

### 动画效果系统（5个动画函数）

```tsx
// 1. 呼吸发光
const glowOpacity = interpolate(spring({...}), [0,1], [0.4,1]);

// 2. 脉冲缩放
const scale = interpolate(frame, [0,15,30], [1,1.06,1]);

// 3. 浮空动画
const floatY = interpolate(frame, [0,30], [0,-18]);

// 4. 文字闪烁
const textFlash = interpolate(frame, [0,8,15,22,30], [1,0.85,1,0.9,1]);

// 5. 外发光强度动画
const outerGlow = interpolate(frame, [0,15,30], [1,1.4,1]);
```

### 5层霓虹 text-shadow 系统

```tsx
textShadow: `
  0 0 20*outerGlow px PRIMARY60,   // 外扩散（4层）
  0 0 12*outerGlow px SECONDARY80, // 副色辉光（2层）
  0 0 6*outerGlow px PRIMARYcc,    // 主色紧密辉光
  0 0 3*outerGlow px rgba(255,255,255,0.9), // 白色高亮
  3px 3px 0 rgba(0,0,0,0.9)        // 黑色阴影
`
```

### 文字渐变填充

```tsx
background: `linear-gradient(180deg, #FFFFFF 0%, ${PRIMARY} 100%)`,
WebkitBackgroundClip: 'text',
WebkitTextFillColor: 'transparent',
backgroundClip: 'text',
```

---

## v4.0.1 (2026-04-30) - Remotion 修复

### Remotion 第二阶段问题修复（6个关键问题）

1. **@remotion/cli 3.3.0 ≠ remotion 4.0.448**：临时项目 package.json 需固定版本一致
2. **JSX 属性语法**：`<Composition fps=30>` 错误，正确为 `fps={30}`
3. **spring() 缺少 fps 参数**：必须传 `fps: FPS` 否则报错 `"fps" must be a number`
4. **React 导入**：`import React from 'remotion'` 报错，应为 `import React from 'react'`
5. **useCurrentFrame() 调用位置**：必须在 inner 组件（StickerContent）中，outer 组件（StickerComponent）不能调用
6. **超时延长**：120s → 300s（Remotion npm install + 渲染需要更长时间）
7. **目录创建**：主循环前加 `os.makedirs(args.output, exist_ok=True)`
8. **文件输入处理**：`os.path.isfile()` 支持单文件输入

### 三层组件架构确立

```
registerRoot(StickerComponent)
    ↓
StickerComponent（外层，返回 <Composition>）
    ↓
StickerContent（内层，含 useCurrentFrame）
```

---

## v4.0.0 (2026-04-30) - 重大重构

### 核心变更：三段式图像生成

| 优先级 | 方式 | 说明 |
|--------|------|------|
| 1 | AI生成图像 | 调用大模型直接生成高质量帧 |
| 2 | Remotion帧导出 | 每张贴图构建独立 Remotion 项目，导出 PNG |
| 3 | PIL本地生成 | 词汇表驱动，场景构图（兜底） |

**自动降级机制**：每层失败自动尝试下一层，无需人工干预。
