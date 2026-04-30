## 图片生成

### 阶段A: AI API 生成（按优先级尝试）

**API Provider 优先级**:

| 优先级 | Provider     | 模型                                    | 备注      |
| --- | ------------ | ------------------------------------- | ------- |
| 1   | `dashscope`  | qwen-image-2.0-pro                    | 账户欠费时跳过 |
| 2   | `seedream`   | doubao-seedream-5-0-260128            | 账户欠费时跳过 |
| 3   | `minimax`    | image-01                              | 未配置时跳过  |
| 4   | `openai`     | gpt-image-1.5                         | 未配置时跳过  |
| 5   | `openrouter` | google/gemini-3.1-flash-image-preview | 未配置时跳过  |
| 6   | `replicate`  | google/nano-banana-pro                | 未配置时跳过  |

**批量执行命令**:

```bash
# 生成 batch.json 文件
cd wechat-stickers/{slug}

# 按优先级尝试各 Provider
BUN_X=bun bun ~/.agents/skills/baoyu-imagine/scripts/main.ts \
  --batchfile batch.json \
  --provider {provider_name} \
  --json
```

**batch.json 格式**:

```json
{
  "tasks": [
    {
      "id": "01-sticker-name",
      "promptFiles": ["prompts/01-{sticker-name}.md"],
      "image": "assets/01-{sticker-name}.png",
      "ar": "1:1"
    },
    {
      "id": "02-sticker-name",
      "promptFiles": ["prompts/02-{sticker-name}.md"],
      "image": "assets/02-{sticker-name}.png",
      "ar": "1:1"
    }
  ]
}
```

### 阶段B: PIL 本地生成（所有API不可用时执行）

> ⚠️ **重要**: 必须执行此兜底方案，不能跳过图片生成步骤。

**脚本路径说明**:

根据 skill 安装方式不同，脚本路径可能有所差异。以下提供三种定位方式：

| 定位方式 | 命令 | 说明 |
| ------ | ---- | ---- |
| **默认路径** | `~/.agents/skills/wechat-sticker-skill/scripts/generate_stickers.py` | 常规安装位置 |
| **自定义目录** | `$AGENTS_SKILLS_DIR/wechat-sticker-skill/scripts/generate_stickers.py` | 通过环境变量指定 |
| **全局搜索** | `find ~ -name "generate_stickers.py" -type f 2>/dev/null` | 未知路径时使用 |

> 💡 **快速定位**: 如果不确定脚本位置，可直接运行 `find ~ -name "generate_stickers.py" -type f 2>/dev/null | head -1` 获取完整路径。

**PIL 生成命令**:

```bash
cd wechat-stickers/{slug}

# 使用环境变量（如果已设置），否则使用默认路径
python3 ${AGENTS_SKILLS_DIR:-~/.agents}/skills/wechat-sticker-skill/scripts/generate_stickers.py \
  --input prompts/ \
  --output assets/ \
  --theme cyberpunk
```

**支持的风格主题**:

| 主题           | 配色主色     | 背景风格            | 默认     |
| ------------ | ---------- | --------------- | ------ |
| `cyberpunk`  | 青色 #00FFFF | 深色圆形+网格+光晕    | ✓ 默认   |
| `kawaii`     | 粉色 #FF69B4 | 粉色渐变椭圆+圆脸眼睛   | <br /> |
| `minimal`    | 深灰 #212529 | 白色+圆形轮廓         | <br /> |
| `meme`       | 橙红 #FF4500 | 橙黄实色+边框         | <br /> |
| `hand-drawn` | 棕色 #8B4513 | 米色+手绘抖动线条      | <br /> |
| `retro`      | 金色 #FFD700 | 深红像素+棋盘格       | <br /> |
| `neon`       | 洋红 #FF00FF | 深黑圆形+多层霓虹光晕    | <br /> |

**macOS 字体路径**:

| 字体   | 路径                                         |
| ---- | ------------------------------------------ |
| 苹方   | `/System/Library/Fonts/PingFang.ttc`       |
| 黑体   | `/System/Library/Fonts/STHeiti Medium.ttc` |
| 华文细黑 | `/System/Library/Fonts/STHeiti Light.ttc`  |

**PIL 生成规则**:

根据不同用途，生成不同尺寸的图片：

| 类型 | 尺寸 | 宽高比 | 用途 |
|-----|------|-------|------|
| 贴图 | 1080×1440px | 3:4 | 单独图片消息发布 |
| 公众号封面 | 900×383px | 2.35:1 | 文章封面 |
| 正文配图 | 1080×607px | 16:9 | 内容展示 |
| 缩略图 | 200×200px | 1:1 | 预览缩略 |

**贴图生成规则**（默认）：
- 画布尺寸：1080×1440px
- 背景：主题相关（透明或实色）
- 文字位置：**画布底部居中**，左右边距30px，距底边30px，多行换行
- 文字渲染：使用 ImageFont.truetype
- 输出格式：PNG

### 每张贴图的专属视觉生成规则

**核心机制**: PIL 脚本根据贴图 `name` 字段自动路由到专属视觉绘制函数，与 `--theme` 风格组合生成最终图片。

**Prompt 中的专属视觉字段**:

```yaml
visual_elements: [元素1, 元素2, 元素3]
style_keyword: [关键词1, 关键词2, 关键词3]
```

**当前已实现的 name → 视觉路由**:

| name 值 | 视觉主体 | 视觉元素 |
|---------|---------|---------|
| `AI补全` | 代码补全框 | 终端窗口 + 下拉列表 + Tab键图标 |
| `命令面板` | ⌘K 按键 | 圆形发光按键 + 搜索框 + 命令列表 |
| `闪电速度` | 闪电符号 | ⚡ + 速度放射线 + 光芒爆发 |
| `智能建议` | AI 大脑 | 神经网络 + 节点发光 + 终端建议条 |
| `团队协作` | 多窗口 | 多个终端窗口并排 + 同步图标 + 连接线 |
| `Warp粉丝` | 终端+红心 | 终端窗口 + 大红心 + 漂浮小心形 |

**自定义新贴图流程**:
1. 在 `prompts/` 下创建 `{num}-{name}.md`
2. `name` 字段写中文贴图名（如 `摸鱼中`）
3. `copy` 字段写核心文案（≥10字）
4. `visual_elements` 列出视觉元素供 AI 生成参考
5. `style_keyword` 列出风格关键词
6. 运行 PIL 生成时，脚本根据 `name` 自动匹配合适的视觉结构

> **注意**: `name` 字段决定视觉结构。若新建贴图的 `name` 不在已实现列表中，脚本将使用通用文字贴图（仅文字渲染，无专属视觉元素）。


