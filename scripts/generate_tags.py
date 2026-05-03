#!/usr/bin/env python3
"""
generate_tags.py - 贴图标签生成

基于项目 prompts 内容提取关键词，生成 tags.md 文件。

Usage:
    python3 scripts/generate_tags.py --input sticker-manifest.md --output tags.md --theme neon
    python3 scripts/generate_tags.py --input prompts/ --output tags.md --theme cyberpunk
"""

import os, re, argparse, sys

# ── 主题配色（来自 _vocab）────────────────────────────────
try:
    from _vocab import THEMES
except ImportError:
    THEMES = {
        'cyberpunk': {'primary': '#00FFFF', 'secondary': '#FF00FF', 'bg': '#0D0221', 'text': '#FFFFFF', 'accent': '#00FF88'},
        'kawaii': {'primary': '#FF69B4', 'secondary': '#FFB6C1', 'bg': '#FFF0F5', 'text': '#4A4A4A', 'accent': '#FF69B4'},
        'neon': {'primary': '#39FF14', 'secondary': '#FF073A', 'bg': '#0A0A0A', 'text': '#FFFFFF', 'accent': '#39FF14'},
        'retro': {'primary': '#F4A460', 'secondary': '#8B4513', 'bg': '#2F2F2F', 'text': '#FFD700', 'accent': '#FF6347'},
        'hand-drawn': {'primary': '#8B7355', 'secondary': '#D2691E', 'bg': '#FFF8DC', 'text': '#3E2723', 'accent': '#8B4513'},
        'minimal': {'primary': '#333333', 'secondary': '#666666', 'bg': '#FFFFFF', 'text': '#000000', 'accent': '#333333'},
        'meme': {'primary': '#FFD700', 'secondary': '#FF4500', 'bg': '#000000', 'text': '#FFFFFF', 'accent': '#FFD700'},
    }

# ── 标签类别定义 ────────────────────────────────────────────
TAG_CATEGORIES = {
    "positive": "情绪/正面 — 开心、快乐、加油、努力、点赞、棒、优秀",
    "negative": "情绪/负面 — 难过、崩溃、无语、愤怒、焦虑、累",
    "reactions": "网络反应 — 哈哈、笑死、666、绝了、躺平、摆烂",
    "social": "社交场景 — 职场、打工人、开会、学习、沟通",
    "tech": "科技/效率 — 程序员、代码、AI、工具、效率、bug",
    "lifestyle": "生活方式 — 美食、咖啡、健身、旅行、游戏",
    "trending": "热门话题 — 打工人、内卷、绝绝子、YYDS",
}


# ── 信息提取 ─────────────────────────────────────────────

def extract_manifest_info(manifest_path):
    """从 manifest 提取主题和贴图信息"""
    with open(manifest_path) as f:
        content = f.read()

    theme_match = re.search(r'\*\*主题(?:键)?\*\*:\s*(\w+)', content)
    if not theme_match:
        theme_match = re.search(r'theme:\s*(\w+)', content)
    theme = theme_match.group(1) if theme_match else None

    # 提取所有贴图章节内容
    sections = re.split(r'^## 贴图\d+:', content, flags=re.MULTILINE)
    stickers = []
    for section in sections[1:]:
        name_match = re.search(r'\*\*名称\*\*:\s*(.+)', section)
        copy_match = re.search(r'\*\*核心文案\*\*:\s*(.+)', section)
        ve_match = re.search(r'\*\*视觉元素\*\*:\s*\[([^\]]+)\]', section)
        stickers.append({
            'name': name_match.group(1).strip() if name_match else '',
            'copy': copy_match.group(1).strip() if copy_match else '',
            'visual_elements': ve_match.group(1).strip() if ve_match else '',
        })

    count = len(sections) - 1
    words = re.findall(r'[\u4e00-\u9fff]+', content)
    keywords = [w for w in words if len(w) >= 2][:20]
    return theme, count, keywords, stickers


def extract_prompts_info(prompts_dir):
    """从 prompts 目录提取主题和贴图信息"""
    keywords = set()
    themes = set()
    stickers = []

    for fname in sorted(os.listdir(prompts_dir)):
        if not fname.endswith('.md'):
            continue
        fpath = os.path.join(prompts_dir, fname)
        with open(fpath) as f:
            content = f.read()

        front = {}
        in_front = False
        for line in content.split('\n'):
            if line.strip() == '---':
                if not in_front:
                    in_front = True
                else:
                    break
                continue
            if in_front and ':' in line:
                k, v = line.split(':', 1)
                front[k.strip()] = v.strip().strip('"').strip("'")

        name = front.get('name', fname.replace('.md', ''))
        copy = front.get('copy', '')
        ve = front.get('visual_elements', '')
        theme = front.get('theme', '')
        stickers.append({'name': name, 'copy': copy, 'visual_elements': ve})
        if theme:
            themes.add(theme)

        # 提取 body 内容的关键词（跳过 frontmatter）
        body = content.split('---', 2)[-1] if content.count('---') >= 2 else content
        # 停用词表：markdown 语法词 / 写作引导词 / 通用的无意义词
        stop_words = {
            '核心文案', '视觉设计', '主体', '风格要求', '动画', '文字展示',
            '核心', '文案', '底部', '主题', '主色', '副色', '背景', '文字',
            '贴图设计', '设计清单', '来源', '生成时间', '手动生成', '推荐主题',
            '项目信息', '项目名称', '微信贴图包', '贴图数量', '情感基调',
            '关键词', '描述', '内容', '方法', '说明', '特点', '优势', '劣势',
            # 多词短语（子串匹配，防止 "必须展示在贴图中" 等漏网
            '必须展示在贴图中', '底部白色文案居中', '快速微妙闪烁同步',
            '视觉设计规则', '风格要求', '三元素横向排列',
        }
        for w in re.findall(r'[\u4e00-\u9fff]{2,}', body):
            if w not in stop_words and len(w) >= 2:
                keywords.add(w)

    theme = list(themes)[0] if themes else None
    return theme, len(stickers), list(keywords)[:20], stickers


# ── 模板生成 ─────────────────────────────────────────────

def build_tags_content(theme, count, keywords, stickers_info):
    """根据项目内容生成 tags.md"""
    theme_display = theme or 'cyberpunk'

    category_tags = {'positive': [], 'negative': [], 'reactions': [],
                     'social': [], 'tech': [], 'lifestyle': [], 'trending': []}

    if theme in ('cyberpunk', 'neon'):
        category_tags['tech'] = ['程序员', '代码', 'AI', '工具', '效率']
        category_tags['positive'] = ['厉害', '优秀', '加油', '棒']
        category_tags['reactions'] = ['666', '绝了', '哈哈']
        category_tags['trending'] = ['打工人', '内卷', '躺平']
    elif theme == 'kawaii':
        category_tags['positive'] = ['可爱', '萌', '甜', '治愈', '暖', '开心']
        category_tags['lifestyle'] = ['美食', '咖啡', '下午茶']
    elif theme == 'meme':
        category_tags['reactions'] = ['哈哈', '笑死', '666', '绝了', '躺平', '摆烂']
        category_tags['trending'] = ['打工人', '内卷', '绝绝子', 'YYDS']
    else:
        category_tags['positive'] = ['开心', '加油', '优秀', '棒']
        category_tags['tech'] = ['程序员', '代码', 'AI', '工具']

    all_text = ' '.join([s.get('copy', '') + ' ' + s.get('name', '') for s in stickers_info or []])
    if any(w in all_text for w in ['Bug', 'debug', '调试']):
        category_tags['tech'].extend(['bug', 'debug', '程序员'])
    if any(w in all_text for w in ['完成', '成功', '解决']):
        category_tags['positive'].extend(['厉害', '优秀', '棒'])
    if any(w in all_text for w in ['崩溃', '难', '压力']):
        category_tags['negative'].extend(['焦虑', '压力', '累'])

    used = set()
    tag_lines = []
    category_display = {
        'positive': '情绪/正面', 'negative': '情绪/负面',
        'reactions': '网络反应', 'social': '社交场景',
        'tech': '科技/效率', 'lifestyle': '生活方式', 'trending': '热门话题',
    }
    for cat, tags in category_tags.items():
        cat_name = category_display.get(cat, cat)
        for tag in tags:
            if tag not in used:
                used.add(tag)
                tag_lines.append(f"- **{tag}**（{cat_name}）")

    wechat_tags = list(used)[:12]

    import datetime
    lines = [
        "---",
        f"name: {theme_display}-tags",
        f"theme: {theme_display}",
        f"sticker_count: {count}",
        f"generated: structured-template",
        "---",
        "",
        f"# {theme_display.title()} 贴图标签推荐",
        "",
        "## 基本信息",
        "",
        f"- 主题：{theme_display}",
        f"- 贴图数量：{count} 张",
        f"- 关键词：{', '.join(keywords[:10]) if keywords else '无'}",
        "",
        "## 推荐标签",
        "",
        "微信贴图标签建议（按热度排列）：",
        "",
    ] + tag_lines + [
        "",
        "## 标签使用建议",
        "",
        f"- 主题标签：{theme_display}、通用",
        "- 情绪标签：选取 5-8 个高频情绪词",
        "- 场景标签：职场/学习/生活选 3-5 个",
        "- 热点标签：结合当前网络热词（1-3个）",
        "",
        "## 微信标签格式",
        "",
        "```",
        " / ".join(wechat_tags),
        "```",
        "",
        f"> 由结构化模板生成于 {datetime.date.today().isoformat()}",
    ]
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description='微信贴图 - 标签生成')
    ap.add_argument('--input', required=True,
                   help='sticker-manifest.md 路径 或 prompts/ 目录')
    ap.add_argument('--output', required=True,
                   help='tags.md 输出路径')
    ap.add_argument('--theme', default=None,
                   help='主题（manifest 未指定时使用）')
    ap.add_argument('--verify', action='store_true',
                   help='仅验证输入文件，不生成文档')
    args = ap.parse_args()

    input_path = args.input

    # --verify 模式
    if args.verify:
        exists = os.path.exists(input_path)
        print(f"[verify] {'✅' if exists else '❌'} {input_path}")
        return 0 if exists else 1

    # 解析输入
    if os.path.isfile(input_path):
        theme, count, keywords, stickers_info = extract_manifest_info(input_path)
    elif os.path.isdir(input_path):
        theme, count, keywords, stickers_info = extract_prompts_info(input_path)
    else:
        print(f"[错误] 不存在的路径: {input_path}", file=sys.stderr)
        return 1

    theme = theme or args.theme or 'cyberpunk'

    print(f"[标签生成] 主题={theme}, 贴图={count}张, 关键词={len(keywords)}个")

    content = build_tags_content(theme, count, keywords, stickers_info)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or '.', exist_ok=True)
    with open(args.output, 'w') as f:
        f.write(content)
    print(f"✅ 标签已生成: {args.output}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
