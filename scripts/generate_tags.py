#!/usr/bin/env python3
"""
generate_tags.py - 贴图标签生成

根据 manifest 或 prompts 目录，生成微信贴图标签推荐文档。

Usage:
    python3 scripts/generate_tags.py --input sticker-manifest.md --output tags.md
    python3 scripts/generate_tags.py --input prompts/ --output tags.md --theme cyberpunk
"""

import os, re, argparse, json
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

# ── 常用微信贴图标签库 ──────────────────────────────────────

WECHAT_STICKER_TAGS = {
    # 情绪/心情
    "positive": [
        "开心", "快乐", "愉快", "喜悦", "欢喜", "乐意",
        "加油", "努力", "奋斗", "拼搏", "坚持",
        "点赞", "优秀", "棒", "厉害", "强",
        "可爱", "萌", "甜", "暖", "治愈",
    ],
    "negative": [
        "难过", "伤心", "崩溃", "无语", "无奈", "抓狂",
        "愤怒", "生气", "暴躁", "郁闷", "烦躁",
        "焦虑", "压力", "疲惫", "困", "累",
    ],
    "reactions": [
        "哈哈", "笑死", "666", "绝了", "服了", "醉了",
        "我裂开了", "我太难了", "打工人", "社畜",
        "摸鱼", "划水", "躺平", "摆烂",
    ],
    "social": [
        "职场", "打工", "上班", "下班", "加班", "周末",
        "摸鱼", "人际", "沟通", "合作", "开会",
        "学习", "考试", "作业", "论文", "毕业",
    ],
    "tech": [
        "程序员", "代码", "编程", "开发", "bug", "debug",
        "GitHub", "AI", "人工智能", "ChatGPT", "Copilot",
        "效率", "工具", "软件", "App", "网站",
    ],
    "lifestyle": [
        "美食", "咖啡", "奶茶", "下午茶", "干饭",
        "熬夜", "失眠", "养生", "健身", "减肥",
        "旅行", "周末", "宅", "追剧", "游戏",
    ],
    "trending": [
        "打工人", "干饭人", "尾款人", "恋爱脑", "内卷", "躺平",
        "绝绝子", "YYDS", "栓Q", "emo", "YYKK",
    ],
}

# ── 主题到标签的映射 ───────────────────────────────────────

THEME_TAG_MAP = {
    "cyberpunk": ["程序员", "代码", "bug", "AI", "效率", "工具"],
    "kawaii":    ["可爱", "萌", "甜", "治愈", "暖"],
    "neon":      ["科技", "AI", "人工智能", "未来", "赛博"],
    "retro":     ["怀旧", "经典", "复古", "回忆"],
    "hand-drawn": ["手绘", "原创", "文艺", "插画"],
    "minimal":   ["简约", "高级感", "冷淡", "克制"],
    "meme":      ["哈哈", "笑死", "666", "绝了", "干饭人", "打工人"],
}


def extract_manifest_info(manifest_path):
    """从 manifest 提取主题和贴图数量"""
    with open(manifest_path) as f:
        content = f.read()

    # 提取 theme
    theme_match = re.search(r'\*\*主题(?:键)?\*\*:\s*(\w+)', content)
    if not theme_match:
        theme_match = re.search(r'theme:\s*(\w+)', content)
    theme = theme_match.group(1) if theme_match else None

    # 统计贴图数量
    stickers = re.findall(r'^## \d+[.-]', content, re.MULTILINE)
    count = len(stickers)

    # 提取关键词
    words = re.findall(r'[\u4e00-\u9fff]+', content)
    keywords = [w for w in words if len(w) >= 2][:20]

    return theme, count, keywords


def extract_prompts_info(prompts_dir):
    """从 prompts 目录提取主题和关键词"""
    keywords = set()
    themes = set()
    count = 0

    for fname in sorted(os.listdir(prompts_dir)):
        if not fname.endswith('.md'):
            continue
        count += 1
        fpath = os.path.join(prompts_dir, fname)
        with open(fpath) as f:
            content = f.read()

        # frontmatter theme
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
                front[k.strip()] = v.strip()

        if 'theme' in front:
            themes.add(front['theme'])

        # 提取中文关键词
        for w in re.findall(r'[\u4e00-\u9fff]{2,}', content):
            if w not in ('核心文案', '视觉设计', '主体', '风格要求',
                         '动画', '文字展示', '核心', '文案', '底部',
                         '主题', '主色', '副色', '背景', '文字'):
                keywords.add(w)

    theme = list(themes)[0] if themes else None
    return theme, count, list(keywords)[:20]


def score_tags(tags, keywords, theme):
    """为标签打分，返回排序后的列表"""
    scored = []
    for category, tag_list in WECHAT_STICKER_TAGS.items():
        for tag in tag_list:
            score = 0
            # 主题匹配
            if theme and theme in THEME_TAG_MAP:
                if tag in THEME_TAG_MAP.get(theme, []):
                    score += 5
            # 关键词命中
            if tag in keywords:
                score += 3
            # 类别加成
            if category in ('reactions', 'trending'):
                score += 1
            if score > 0:
                scored.append((score, tag, category))
    # 按分数降序，相同分数按固定顺序
    scored.sort(key=lambda x: (-x[0], WECHAT_STICKER_TAGS[x[2]].index(x[1])))
    return scored


def generate_tags_content(theme, count, keywords, top_tags):
    """生成 tags.md 内容"""
    theme_label = THEMES.get(theme, {}).get('primary', '#00FFFF') if theme else '#00FFFF'
    theme_display = theme or 'cyberpunk'

    lines = [
        "---",
        f"name: {theme_display}-tags",
        f"theme: {theme_display}",
        f"sticker_count: {count}",
        f"generated: auto",
        "---",
        "",
        f"# {theme_display.title()} 贴图标签推荐",
        "",
        f"## 基本信息",
        "",
        f"- 主题：{theme_display}",
        f"- 贴图数量：{count} 张",
        f"- 关键词：{', '.join(keywords[:10])}",
        "",
        f"## 推荐标签",
        "",
        "微信贴图标签建议（按热度排列）：",
        "",
    ]

    # 按类别分组输出
    categories_display = {
        'positive': '情绪/正面',
        'negative': '情绪/负面',
        'reactions': '网络反应',
        'social': '社交场景',
        'tech': '科技/效率',
        'lifestyle': '生活方式',
        'trending': '热门话题',
    }

    used = set()
    for score, tag, category in top_tags:
        if tag in used:
            continue
        used.add(tag)
        cat_name = categories_display.get(category, category)
        lines.append(f"- **{tag}**（{cat_name}）")

    lines += [
        "",
        "## 标签使用建议",
        "",
        f"- 主题标签：{theme_display}、{THEME_TAG_MAP.get(theme_display, ['通用'])[0]}",
        "- 情绪标签：选取 5-8 个高频情绪词",
        "- 场景标签：职场/学习/生活选 3-5 个",
        "- 热点标签：结合当前网络热词（1-3个）",
        "",
        "## 微信标签格式",
        "",
        "```",
        f"{' / '.join([t for _, t, _ in top_tags[:8]])}",
        "```",
        "",
        f"> 自动生成于 {__import__('datetime').date.today().isoformat()}，基于 {count} 张贴图的视觉元素分析",
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
    args = ap.parse_args()

    input_path = args.input

    # 解析输入
    if os.path.isfile(input_path):
        theme, count, keywords = extract_manifest_info(input_path)
    elif os.path.isdir(input_path):
        theme, count, keywords = extract_prompts_info(input_path)
    else:
        print(f"[错误] 不存在的路径: {input_path}", file=__import__('sys').stderr)
        return 1

    theme = theme or args.theme or 'cyberpunk'

    print(f"[标签生成] 主题={theme}, 贴图={count}张, 关键词={len(keywords)}个")

    # 打分并选择 top 标签
    top_tags = score_tags(WECHAT_STICKER_TAGS, keywords, theme)[:20]

    if not top_tags:
        print("[警告] 未能匹配到合适标签，使用默认标签")
        top_tags = [(1, t, 'default') for t in ['开心', '加油', '哈哈哈', '绝了', '666']]

    print(f"[标签] 匹配到 {len(top_tags)} 个标签")

    # 生成
    content = generate_tags_content(theme, count, keywords, top_tags)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'w') as f:
        f.write(content)

    print(f"✅ 标签已生成: {args.output}")
    print(f"   推荐标签: {', '.join([t for _, t, _ in top_tags[:8]])}")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
