#!/usr/bin/env python3
"""
generate_post.py - 生成微信公众号推广文档 post.md

根据项目信息（content-analysis.md / sticker-manifest.md / tags.md）生成
符合微信公众号发布格式的 post.md，包含标题、内容和标签。

Usage:
    python3 scripts/generate_post.py \\
        --project ~/wechat-stickers/opengeometry \\
        --theme neon \\
        --link https://github.com/OpenGeometry-io/OpenGeometry \\
        --output docs/post.md

    # 或在工作流中自动调用（由 run_full_pipeline.py 步骤 8 执行）
"""

import os
import re
import random
import argparse
from datetime import date


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)


# ── 标题模板库 ────────────────────────────────────────────

TITLE_TEMPLATES = [
    "「{project}」微信表情包上线！",
    "{project} 专属表情包来了",
    "程序员专属！{project} 微信表情包",
    "{project} 趣味表情包，工程师必备",
    "【{project}】微信贴图正式发布",
    "这款 {project} 表情包，太适合程序员了",
    "{project} 定制贴图，让聊天更有趣",
    "工程师必备！{project} 主题表情包上线",
]


# ── 平台标签（固定） ─────────────────────────────────────

PLATFORM_TAGS = ["微信表情", "微信贴图", "WeChatStickers"]


def extract_info(project_root, theme, link):
    """从项目目录提取信息用于生成 post"""

    manifest_path = os.path.join(project_root, 'sticker-manifest.md')
    tags_path = os.path.join(project_root, 'docs', 'tags.md')
    content_path = os.path.join(project_root, 'content-analysis.md')

    # 项目名称
    project_name = os.path.basename(project_root)

    # 贴图数量 - 尝试多种格式
    stickers_count = 0
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            content = f.read()
        # 兼容多种格式: ## sticker_01, ## 1., ## 1-
        patterns = [
            r'^## sticker_\d+',      # ## sticker_01
            r'^## \d+[.-]',          # ## 1. 或 ## 1-
        ]
        for pat in patterns:
            matches = re.findall(pat, content, re.MULTILINE)
            if matches:
                stickers_count = len(matches)
                break

    # 从 tags.md 提取标签（## 推荐标签 章节下的加粗项）
    tags = []
    if os.path.exists(tags_path):
        with open(tags_path) as f:
            content = f.read()
        # 提取 **标签名**（加粗格式）
        found_tags = re.findall(r'\*\*([^*]+)\*\*', content)
        # 过滤，保留中文/英文标签
        tags = [t.strip() for t in found_tags if len(t.strip()) >= 2][:10]

    # 从 content-analysis 提取项目描述
    description = ""
    if os.path.exists(content_path):
        with open(content_path) as f:
            content = f.read()
        # 提取第一段有意义的内容（跳过 frontmatter）
        sections = content.split('---')
        for section in sections:
            if '核心功能' in section or '项目概述' in section or '## 项目' in section:
                # 提取描述性段落
                lines = []
                for line in section.split('\n'):
                    stripped = line.strip()
                    # 跳过标题、空行、列表、表格
                    if (stripped.startswith('#') or
                        not stripped or
                        stripped.startswith('|') or
                        stripped.startswith('- **') or
                        stripped.startswith('**')):
                        continue
                    # 跳过纯技术词汇行，保留自然段落
                    if len(stripped) > 20:
                        lines.append(stripped)
                if lines:
                    description = ' '.join(lines[:2])
                    break

    # 合并标签：平台标签 + 提取的标签
    all_tags = PLATFORM_TAGS + tags
    # 去重保持顺序
    seen = set()
    unique_tags = []
    for t in all_tags:
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)

    return {
        'project': project_name,
        'theme': theme,
        'link': link,
        'count': stickers_count,
        'tags': unique_tags,
        'description': description,
    }


def generate_title(project, theme):
    """生成标题：从模板库选择，替换占位符"""
    template = random.choice(TITLE_TEMPLATES)
    title = template.format(project=project.upper() if len(project) <= 8 else project)
    # 限制 ≤20 字符，清理末尾标点
    title = title[:20].rstrip('，、。；：')
    return title


def generate_content(info):
    """生成 post.md 正文内容"""
    project = info['project']
    theme = info['theme']
    link = info['link']
    count = info['count']
    description = info['description']

    # 主题中文名
    theme_names = {
        'neon': '霓虹科技',
        'cyberpunk': '赛博朋克',
        'kawaii': '可爱治愈',
        'retro': '复古怀旧',
        'hand-drawn': '手绘文艺',
        'minimal': '简约冷淡',
        'meme': '搞笑网络',
    }
    theme_cn = theme_names.get(theme, theme)

    content_parts = []

    # 第一段
    if description:
        content_parts.append(
            f"给大家介绍一套专为 {project} 量身定制的微信表情包！"
            f"这套表情以 {theme_cn} 风格呈现，收录了 {count} 张精心设计的动态贴图，"
            f"每一张都捕捉了开发者日常工作中的精彩瞬间。"
        )
    else:
        content_parts.append(
            f"一套专为 {project} 开发者打造的微信表情包来啦！"
            f"以 {theme_cn} 风格呈现，包含 {count} 张精心设计的动态贴图，"
            f"让你的聊天更加生动有趣。"
        )

    # 第二段
    if link:
        content_parts.append(
            f"无论是调试代码时的兴奋、解决 Bug 后的成就感，还是迎接新项目时的期待——"
            f"这套表情包都能准确表达工程师的心声。"
            f"现在就去体验吧：{link}"
        )
    else:
        content_parts.append(
            f"无论是调试代码时的兴奋、解决 Bug 后的成就感，还是迎接新项目时的期待——"
            f"这套表情包都能准确表达工程师的心声。"
        )

    # 第三段
    content_parts.append(
        f"喜欢这套 {project} 主题表情包吗？快去微信表情包商店搜索「{project}」下载使用吧！"
    )

    return '\n\n'.join(content_parts)


def generate_tags_line(tags):
    """生成标签行（≥5 个）"""
    # 取前 8 个标签
    selected = tags[:8]
    if len(selected) < 5:
        # 补充默认标签
        defaults = ['AI', '人工智能', '程序员', '代码', '科技']
        for d in defaults:
            if d not in selected:
                selected.append(d)
            if len(selected) >= 5:
                break
    return '#' + ' #'.join(selected[:8])


def generate_post(project_root, theme, link, output, title=None, verbose=True):
    """生成 post.md 文件"""

    # 提取信息
    info = extract_info(project_root, theme, link)

    # 生成标题
    if not title:
        title = generate_title(info['project'], theme)

    # 外部指定标题时也做清理
    if title:
        title = title[:20].rstrip('，、。；：')

    # 生成内容
    content = generate_content(info)

    # 生成标签
    tags_line = generate_tags_line(info['tags'])

    # 组装完整文档（无 frontmatter 重复）
    doc = f"""---
name: {info['project']}-post
title: {title}
theme: {theme}
date: {date.today().isoformat()}
tags: {tags_line}
link: {link or ''}
---

{content}

## 标签

{tags_line}
"""

    # 写入文件
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        f.write(doc)

    if verbose:
        print(f"✅ post.md 已生成: {output}")
        print(f"   标题: {title}（{len(title)}字）")
        print(f"   贴图: {info['count']} 张")
        print(f"   标签: {tags_line}")

    return True


def main():
    parser = argparse.ArgumentParser(description='生成微信公众号推广文档 post.md')
    parser.add_argument('--project', required=True,
                        help='项目根目录')
    parser.add_argument('--theme', required=True,
                        help='主题')
    parser.add_argument('--link', default='',
                        help='项目链接')
    parser.add_argument('--output', required=True,
                        help='post.md 输出路径')
    parser.add_argument('--title', default=None,
                        help='自定义标题（不超过20字符）')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    generate_post(
        project_root=os.path.abspath(args.project),
        theme=args.theme,
        link=args.link,
        output=args.output,
        title=args.title,
        verbose=not args.quiet,
    )


if __name__ == '__main__':
    main()
