#!/usr/bin/env python3
"""
generate_prompts.py - 从 manifest 生成 prompts 文件

读取 sticker-manifest.md，为每张贴图生成 prompts/{num}-{name}.md。
自动校验 visual_elements 中的 key 是否在词汇表范围内。

Usage:
    python3 scripts/generate_prompts.py \
        --input sticker-manifest.md \
        --output prompts/
"""

import os, re, argparse

# ── 词汇表 ────────────────────────────────────────────────

VOCABULARY = {
    'brain', 'neural_network', 'terminal', 'lightning', 'ai_chip', 'spotlight',
    'network_node', 'button', 'code', 'algorithm', 'function', 'variable',
    'debug', 'deploy', 'cpu', 'server', 'database', 'cloud', 'data',
    'equals_sign', 'question_mark', 'eraser', 'checkmark', 'math_canvas', 'robot',
    'heart', 'thumbs_up', 'clap', 'pray', 'muscle', 'thinking', 'eyes',
    'trophy', 'medal', 'crown', 'star', 'fire', 'hundred',
    'laugh', 'cry', 'angry', 'cool', 'shy', 'sleeping',
    'rocket', 'alarm', 'bell', 'megaphone', 'wrench', 'hammer',
    'scissors', 'pencil', 'book', 'lightbulb', 'bulb', 'envelope', 'gift',
    'tada', 'balloon', 'confetti',
    'coffee', 'tea', 'beer', 'cocktail', 'wine',
    'pizza', 'rice', 'fruit', 'cake', 'cookie', 'bread',
    'phone', 'camera', 'clipboard', 'chart', 'calendar',
    'key', 'lock', 'folder', 'file', 'email', 'call',
    'microphone', 'video', 'tv', 'clock', 'hourglass',
    'pen', 'ruler', 'paperclip', 'stamp', 'inbox', 'outbox',
    'earth', 'moon', 'sun', 'rainbow', 'snowflake', 'wave', 'anchor',
    'airplane', 'car', 'bicycle', 'map', 'compass',
    'flag', 'satellite', 'telescope', 'microscope',
    'money', 'gem', 'love_letter', 'warning', 'no_entry', 'busy', 'free', 'secret',
    'goal', 'puzzle', 'music', 'headphones', 'sound', 'mute',
    'eye', 'ear', 'nose', 'footprints',
    'bone', 'microbe', 'pill', 'syringe', 'thermometer',
    'magnet', 'gear', 'atom', 'dna', 'biohazard', 'radioactive', 'bio',
    'four_leaf', 'maple', 'cherry', 'tulip', 'rose', 'hibiscus', 'shell', 'feather',
    'sparkle', 'diamond', 'fleur', 'comet',
    'satellite', 'music',
}

# ── 主题配色表 ────────────────────────────────────────────

THEMES = {
    "cyberpunk":  {"primary": "#00FFFF", "secondary": "#FF00FF", "bg": "#0D0D1A", "text": "#FFFFFF"},
    "kawaii":     {"primary": "#FF69B4", "secondary": "#FFB6C1", "bg": "#FFF0F5", "text": "#4A4A4A"},
    "neon":       {"primary": "#FF00FF", "secondary": "#00FFFF", "bg": "#1A0033", "text": "#FFFFFF"},
    "retro":      {"primary": "#FFD700", "secondary": "#FF6B35", "bg": "#2D1B00", "text": "#FFFFFF"},
    "hand-drawn": {"primary": "#8B4513", "secondary": "#D2691E", "bg": "#FFF8DC", "text": "#4A4A4A"},
    "minimal":    {"primary": "#212529", "secondary": "#495057", "bg": "#F8F9FA", "text": "#212529"},
    "meme":       {"primary": "#FF4500", "secondary": "#FFD700", "bg": "#1A1A1A", "text": "#FFFFFF"},
}

# ── Manifest 解析 ────────────────────────────────────────

def parse_manifest(path):
    """解析 sticker-manifest.md，返回 [(num, name, copy, visual_elements, style_keyword, theme), ...]"""
    with open(path) as f:
        content = f.read()

    stickers = []
    # 匹配 ## 贴图N: {名称}
    sections = re.split(r'^## 贴图\d+:', content, flags=re.MULTILINE)
    for i, section in enumerate(sections[1:], 1):
        num = f"{i:02d}"
        # 提取名称
        name_match = re.search(r'\*\*名称\*\*:\s*(.+)', section)
        name = name_match.group(1).strip() if name_match else f"贴图{i}"

        # 提取核心文案
        copy_match = re.search(r'\*\*核心文案\*\*:\s*(.+)', section)
        copy = copy_match.group(1).strip() if copy_match else ''

        # 提取 visual_elements（[el1, el2, el3] 格式）
        ve_match = re.search(r'\*\*视觉元素\*\*:\s*\[([^\]]+)\]', section)
        if ve_match:
            elements_str = ve_match.group(1)
            visual_elements = [e.strip() for e in elements_str.split(',') if e.strip()]
        else:
            # 尝试中文逗号分隔
            ve_match2 = re.search(r'\*\*视觉元素\*\*:\s*(.+)', section)
            if ve_match2:
                raw = ve_match2.group(1)
                elements = re.findall(r'[`"（）()【】\[\]a-zA-Z_]+', raw)
                visual_elements = [e.strip('`"（）()【】[]').strip() for e in elements if e.strip()]
            else:
                visual_elements = []

        # 提取风格
        style_match = re.search(r'\*\*风格\*\*:\s*\[([^\]]+)\]', section)
        if style_match:
            style_str = style_match.group(1)
            style_keyword = [s.strip() for s in style_str.split(',')]
        else:
            style_keyword = ['cyberpunk']

        # 提取 theme（从文档中的 manifest 级别 theme 字段）
        theme_match = re.search(r'\*\*主题(?:键)?\*\*:\s*(\w+)', section)
        if not theme_match:
            theme_match = re.search(r'theme:\s*(\w+)', content)
        theme = theme_match.group(1).strip() if theme_match else 'cyberpunk'
        if theme not in THEMES:
            theme = 'cyberpunk'

        stickers.append({
            'num': num,
            'name': name,
            'copy': copy,
            'visual_elements': visual_elements,
            'style_keyword': style_keyword,
            'theme': theme,
        })
    return stickers

# ── Prompt 文件生成 ───────────────────────────────────────

def generate_prompt_content(sticker, theme_colors):
    """生成单个 prompt 文件的完整内容"""
    t = theme_colors
    emoji_desc = ', '.join(sticker['visual_elements'][:3])

    content = f"""---
name: {sticker['name']}
copy: {sticker['copy']}
visual_elements: [{', '.join(sticker['visual_elements'])}]
style_keyword: [{', '.join(sticker['style_keyword'])}]
theme: {sticker['theme']}
aspect_ratio: "3:4"
---

# {sticker['num']}-{sticker['name']}

## 核心文案（必须展示在贴图中）
{sticker['copy']}

## 视觉设计规则

### 主体
深色背景 + 居中显示 {emoji_desc}
三元素横向排列，霓虹发光滤镜，底部白色文案居中

### 风格要求
- 主题：{sticker['theme']}
- 主色：{t['primary']}（{sticker['style_keyword'][0] if sticker['style_keyword'] else 'cyberpunk'}）
- 副色：{t['secondary']}
- 背景：{t['bg']}
- 文字：{t['text']}，底部居中

### 动画
- 呼吸发光：opacity 0.4→1 脉冲
- 脉冲缩放：scale 1→1.06→1
- 浮空动效：translateY 浮起
- 文字闪烁：快速微妙闪烁同步

### 文字展示
- 核心文案：{sticker['copy']}
- 字体：PingFang SC，90px
- 位置：底部居中
- 效果：霓虹发光 text-shadow 多层{theme_colors.get(sticker['theme'], {}).get('primary', '#00FFFF')}
"""
    return content

# ── 校验 ─────────────────────────────────────────────────

def validate_vocabulary(visual_elements):
    """返回 (valid_elements, invalid_elements)"""
    valid = [e for e in visual_elements if e in VOCABULARY]
    invalid = [e for e in visual_elements if e not in VOCABULARY]
    return valid, invalid

# ── 主函数 ───────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='微信贴图 - Prompt 文件生成')
    ap.add_argument('--input', required=True, help='sticker-manifest.md 路径')
    ap.add_argument('--output', required=True, help='prompts/ 输出目录')
    ap.add_argument('--theme', default='cyberpunk', help='默认主题（manifest 未指定时使用）')
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"[错误] 文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"[解析 manifest] {args.input}")
    stickers = parse_manifest(args.input)
    print(f"[贴图数量] {len(stickers)} 张")

    os.makedirs(args.output, exist_ok=True)

    all_valid = True
    for s in stickers:
        # 词汇表校验
        valid_elems, invalid_elems = validate_vocabulary(s['visual_elements'])
        if invalid_elems:
            print(f"  ⚠️ 贴图{s['num']} 词汇表警告: {invalid_elems} 不在词汇表中，已忽略")
            all_valid = False

        # 确定 theme
        theme_key = s['theme'] if s['theme'] in THEMES else args.theme
        theme_colors = THEMES.get(theme_key, THEMES['cyberpunk'])

        # 生成文件
        content = generate_prompt_content(s, theme_colors)
        filename = f"{s['num']}-{s['name']}.md"
        filepath = os.path.join(args.output, filename)

        # 确保文件名合法
        safe_name = re.sub(r'[<>:"/\\|?*]', '-', s['name'])
        if safe_name != s['name']:
            filename = f"{s['num']}-{safe_name}.md"
            filepath = os.path.join(args.output, filename)

        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✅ {filename}")

    if all_valid:
        print(f"\n✅ 所有贴图的 visual_elements 均在词汇表范围内")
    else:
        print(f"\n⚠️  部分 key 不在词汇表中，已自动忽略（用 emoji 渲染兜底）")

    print(f"\n✅ Prompts 已生成: {args.output}")
    print(f"   下一步: python3 scripts/generate_frames.py --input {args.output} --output assets-{args.theme}/ --theme {args.theme}")
    print(f"   QA检查: python3 scripts/qa_check.py --input {args.output} --vocabulary docs/prompts-format.md")

if __name__ == '__main__':
    main()
