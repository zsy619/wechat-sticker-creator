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

import os, sys, re, argparse

# ── 词汇表（来自 _vocab 共享模块）────────────────────────────
try:
    from _vocab import VOCABULARY, THEMES, filter_valid_keys
except ImportError:
    VOCABULARY = {}
    THEMES = {
        'cyberpunk': {'primary': '#00FFFF', 'secondary': '#FF00FF', 'bg': '#0D0221', 'text': '#FFFFFF', 'accent': '#00FF88'},
        'kawaii': {'primary': '#FF69B4', 'secondary': '#FFB6C1', 'bg': '#FFF0F5', 'text': '#4A4A4A', 'accent': '#FF69B4'},
        'neon': {'primary': '#39FF14', 'secondary': '#FF073A', 'bg': '#0A0A0A', 'text': '#FFFFFF', 'accent': '#39FF14'},
        'retro': {'primary': '#F4A460', 'secondary': '#8B4513', 'bg': '#2F2F2F', 'text': '#FFD700', 'accent': '#FF6347'},
        'hand-drawn': {'primary': '#8B7355', 'secondary': '#D2691E', 'bg': '#FFF8DC', 'text': '#3E2723', 'accent': '#8B4513'},
        'minimal': {'primary': '#333333', 'secondary': '#666666', 'bg': '#FFFFFF', 'text': '#000000', 'accent': '#333333'},
        'meme': {'primary': '#FFD700', 'secondary': '#FF4500', 'bg': '#000000', 'text': '#FFFFFF', 'accent': '#FFD700'},
    }
    def filter_valid_keys(keys): return [k for k in keys if k in VOCABULARY]

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

        # 提取 visual_elements（灵活的 key 解析：支持 [key1, key2] 或分散格式）
        ve_match = re.search(r'\*\*视觉元素\*\*:\s*\[([^\]]+)\]', section)
        if ve_match:
            elements_str = ve_match.group(1)
            # 提取每个 key（英文/数字/下划线）
            visual_elements = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', elements_str)
            visual_elements = [e.strip() for e in visual_elements if e.strip()]
        else:
            # 降级：从整段文本提取所有看起来像 key 的词
            ve_match2 = re.search(r'\*\*视觉元素\*\*:\s*(.+)', section)
            if ve_match2:
                raw = ve_match2.group(1)
                # 提取英文词（包括带下划线的复合词）
                visual_elements = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', raw)
                visual_elements = [e for e in visual_elements if len(e) > 2]
            else:
                visual_elements = []

        # 提取风格（支持多种格式：主题键/风格/主题）
        style_match = re.search(r'\*\*主题键\*\*:\s*(\w+)', section)
        if not style_match:
            style_match = re.search(r'\*\*风格\*\*:\s*\[([^\]]+)\]', section)
        if not style_match:
            style_match = re.search(r'theme:\s*(\w+)', content)
        if style_match:
            theme_candidate = style_match.group(1).strip()
            if theme_candidate in THEMES:
                style_keyword = [theme_candidate]
            else:
                style_keyword = [style_match.group(1).strip()]
        else:
            style_keyword = ['cyberpunk']

        # 提取 theme（项目级别，**主题** 字段优先）
        theme_match = re.search(r'\*\*主题\*\*:\s*(\w+)', content)
        if not theme_match:
            theme_match = re.search(r'recommended_theme.*?:\s*(\w+)', content)
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
    return filter_valid_keys(visual_elements)

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

    if len(stickers) == 0:
        print(f"\n❌ 错误：未能从 manifest 中解析到任何贴图", file=sys.stderr)
        print(f"   请检查 manifest 格式是否正确（需包含 ## 贴图1: 等章节）", file=sys.stderr)
        sys.exit(1)

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
