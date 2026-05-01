# 图片生成（四阶段工作流）

## 优先级总览

```
┌─────────────────────────────────────────┐
│  阶段一：AI 生成图像（首选）             │
│  调用大模型直接生成高质量帧              │
│  失败 → 自动降级                         │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  阶段二：Remotion 帧导出（第二选择）     │
│  每张贴图 = <Still>组件 → 导出 PNG      │
│  失败 → 自动降级                         │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  阶段三：PIL 本地生成（兜底）            │
│  词汇表驱动 + 场景构图                   │
└─────────────────────────────────────────┘
```

## 阶段一 · AI 生成（首选）

**适用**：所有贴图，追求最高视觉质量。

### 支持的 Provider

| 优先级 | Provider | 模型 | 备注 |
|--------|----------|------|------|
| 1 | `dashscope` | qwen-image-2.0-pro | 账户欠费时跳过 |
| 2 | `seedream` | doubao-seedream-5-0-260128 | 账户欠费时跳过 |
| 3 | `minimax` | image-01 | 未配置时跳过 |
| 4 | `openai` | gpt-image-1.5 | 未配置时跳过 |

### 提示词构建

```bash
python3 -c "
import json, glob, yaml

items = []
for pf in glob.glob('prompts/*.md'):
    with open(pf) as f:
        front = {}
        for l in f:
            if l.strip() == '---': break
            if ':' in l:
                k, v = l.split(':', 1)
                front[k.strip()] = v.strip().strip('\"').strip(\"'\")
    name = front.get('name', '')
    copy = front.get('copy', '')
    style = front.get('style_keyword', '')
    theme = front.get('theme', 'cyberpunk')
    prompt = f'微信贴图，1080x1440px，3:4竖版，文字: {copy}，风格: {style}，高质量，精致细节'
    items.append({'name': name, 'prompt': prompt})

with open('batch.json', 'w') as f:
    json.dump({'items': items}, f, ensure_ascii=False, indent=2)
"
```

### 异常处理

- **401/欠费** → 跳过该 provider，尝试下一个
- **429限流** → 等待10秒重试（最多3次）
- **超时（>60s）** → 降级到 Remotion
- **所有 provider 失败** → 降级到 Remotion

## 阶段二 · Remotion 帧导出（第二选择）

**适用**：需要精确控制视觉元素、程序化绘制。

### 流程

```
prompts/*.md
    ↓（每张贴图）
生成 {StickerName}.tsx 组件
    ↓
创建 remotion/{sticker-name}/ 项目
    ↓
npx remotion still → PNG
    ↓
输出到 assets/
```

详见 [frame-design.md](frame-design.md)。

### 项目初始化

```bash
mkdir -p remotion/{sticker-name}/src
```

### 导出 PNG

```bash
cd remotion/{sticker-name}
npx remotion still src/Root.tsx {CompositionId} \
  --output ../../assets/{sticker-name}.png \
  --width 1080 --height 1440
```

### 异常处理

- **Node.js 不可用** → 降级到 PIL
- **npx remotion 报错** → 降级到 PIL
- **组件编译错误** → 记录错误，跳过该贴图

## 阶段三 · PIL 本地生成（兜底）

**适用**：完全离线、稳定可靠。

```bash
python3 scripts/pil_fallback.py \
  --input prompts/ \
  --output assets-pil/ \
  --theme cyberpunk
```

### 词汇表驱动

`visual_elements` 字段直接映射到词汇表函数：

| 关键词 | 绘制函数 |
|--------|---------|
| `brain` / `ai大脑` | `_draw_brain()` |
| `神经网络` | `_draw_neural_network()` |
| `terminal` / `终端窗口` | `_draw_terminal()` |
| `heart` / `红心` | `_draw_heart()` |
| `equals_sign` / `等号` | `_draw_equals_sign()` |
| `question_mark` / `问号` | `_draw_question_mark()` |
| `eraser` / `橡皮擦` | `_draw_eraser()` |
| `checkmark` / `对勾` | `_draw_checkmark()` |
| `math_canvas` / `画布` | `_draw_math_canvas()` |

### 场景构图（方案D）

- **FOCUS 元素**：居中放大（brain, terminal, math_canvas 等）
- **ACCENT 元素**：小尺寸散布（heart, question_mark, checkmark 等）
- **布局预设**：`single` / `dual` / `triple` / `diffuse`

## 贴图生成核心规则（所有阶段适用）

- **尺寸**：1080×1440px（微信贴图标准）
- **格式**：PNG
- **文字**：底部居中，左右 margin 30px，距底边 30px
- **文件名**：`{num}-{name}.png`

## 每张贴图的专属视觉生成规则

`visual_elements` 中的每个关键词对应一个词汇表函数，无需为新项目编写代码。词汇表覆盖：

- FOCUS：brain / neural_network / terminal / lightning / math_canvas / ai_chip / command_k / equals_sign
- ACCENT：heart / question_mark / checkmark / eraser / spotlight / network_node / button

## 输出格式

无论哪个阶段生成，最终输出统一为：

```
assets-{theme}/
├── 01-{name}.png   ← 1080×1440px PNG
├── 02-{name}.png
└── ...
```
