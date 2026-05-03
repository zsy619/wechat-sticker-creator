#!/usr/bin/env python3
"""
generate_post.py - 生成微信公众号推广文档 post.md

基于 manifest 内容生成符合微信公众号发布格式的 post.md。

Usage:
    python3 scripts/generate_post.py \
        --project ~/wechat-stickers/opengeometry \
        --theme neon \
        --link https://github.com/OpenGeometry-io/OpenGeometry \
        --output post.md
"""

import os
import re
import random
import argparse
import sys
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


# ── 信息提取 ─────────────────────────────────────────────


def extract_info(project_root, theme, link):
    """从项目目录提取信息用于生成 post"""

    manifest_path = os.path.join(project_root, "sticker-manifest.md")
    tags_path = os.path.join(project_root, "docs", "tags.md")
    content_path = os.path.join(project_root, "content-analysis.md")
    prompts_dir = os.path.join(project_root, "prompts")

    # 优先从 prompts frontmatter 的 name 字段获取项目名（最可靠）
    # 降级：manifest 第一行 / content-analysis 第一行 / 目录名
    project_name = None

    if os.path.isdir(prompts_dir):
        for fname in sorted(os.listdir(prompts_dir)):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(prompts_dir, fname)
            with open(fpath) as f:
                raw = f.read()
            # 取第一个文件的 frontmatter name
            front = {}
            in_front = False
            for line in raw.split('\n'):
                if line.strip() == '---':
                    if not in_front:
                        in_front = True
                    else:
                        break
                if in_front and ':' in line:
                    k, v = line.split(':', 1)
                    front[k.strip()] = v.strip().strip('"').strip("'")
            if 'name' in front:
                project_name = front['name']
                break

    # 降级取目录名（避免取到技能根目录名）
    if not project_name:
        project_name = os.path.basename(os.path.abspath(project_root.rstrip('/')))

    # 优先从 manifest 的项目信息节提取真实项目名（覆盖上述 fallback）
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            m_content = f.read()
        # 匹配 "**项目名称**: value" 或 "- **项目名称**: value"
        m = re.search(r'\*{0,2}项目名称\*{0,2}:\s*(.+)', m_content)
        if m:
            project_name = m.group(1).strip()

    stickers_count = 0
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            content = f.read()
        patterns = [
            r"^## sticker_\d+",
            r"^## (?:\d+[.-]|贴图\d+:)",
        ]
        for pat in patterns:
            matches = re.findall(pat, content, re.MULTILINE)
            if matches:
                stickers_count = len(matches)
                break

    tags = []
    if os.path.exists(tags_path):
        with open(tags_path) as f:
            content = f.read()
        found_tags = re.findall(r"\*\*([^*]+)\*\*", content)
        tags = [t.strip() for t in found_tags if len(t.strip()) >= 2][:10]

    description = ""
    if os.path.exists(content_path):
        with open(content_path) as f:
            content = f.read()
        sections = content.split("---")
        for section in sections:
            if "核心功能" in section or "项目概述" in section or "## 项目" in section:
                lines = []
                for line in section.split("\n"):
                    stripped = line.strip()
                    if (
                        stripped.startswith("#")
                        or not stripped
                        or stripped.startswith("|")
                        or stripped.startswith("- **")
                        or stripped.startswith("**")
                    ):
                        continue
                    if len(stripped) > 20:
                        lines.append(stripped)
                if lines:
                    description = " ".join(lines[:2])
                    break

    all_tags = PLATFORM_TAGS + tags
    seen = set()
    unique_tags = []
    for t in all_tags:
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)

    return {
        "project": project_name,
        "theme": theme,
        "link": link,
        "count": stickers_count,
        "tags": unique_tags,
        "description": description,
    }


def extract_manifest_details(project_root):
    """提取 manifest 中的贴图详情"""
    manifest_path = os.path.join(project_root, "sticker-manifest.md")
    manifest_content = ""
    sticker_details = []
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest_content = f.read()
        sections = re.split(r"^## 贴图\d+:", manifest_content, flags=re.MULTILINE)
        for s in sections[1:]:
            name_match = re.search(r"\*\*名称\*\*:\s*(.+)", s)
            copy_match = re.search(r"\*\*核心文案\*\*:\s*(.+)", s)
            if name_match:
                sticker_details.append(
                    {
                        "name": name_match.group(1).strip(),
                        "copy": copy_match.group(1).strip() if copy_match else "",
                    }
                )
    return sticker_details


def extract_project_desc(project_root):
    """提取 content-analysis 中的项目描述"""
    content_path = os.path.join(project_root, "content-analysis.md")
    if os.path.exists(content_path):
        with open(content_path) as f:
            c = f.read()
        match = re.search(r"## 核心主题\s*\n+(.*?)(?=\n##|\Z)", c, re.DOTALL)
        if match:
            return match.group(1).strip()[:300]
    return ""


# ── 主函数


def generate_title(project, theme):
    template = random.choice(TITLE_TEMPLATES)
    title = template.format(project=project.upper() if len(project) <= 8 else project)
    title = title[:20].rstrip("，、。；：")
    return title


def generate_content(info):
    project = info["project"]
    theme = info["theme"]
    link = info["link"]
    count = info["count"]
    description = info["description"]

    theme_names = {
        "neon": "霓虹科技",
        "cyberpunk": "赛博朋克",
        "kawaii": "可爱治愈",
        "retro": "复古怀旧",
        "hand-drawn": "手绘文艺",
        "minimal": "简约冷淡",
        "meme": "搞笑网络",
    }
    theme_cn = theme_names.get(theme, theme)

    content_parts = []

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

    content_parts.append(
        f"喜欢这套 {project} 主题表情包吗？快去微信表情包商店搜索「{project}」下载使用吧！"
    )

    return "\n\n".join(content_parts)


def generate_tags_line(tags):
    selected = tags[:8]
    if len(selected) < 5:
        defaults = ["AI", "人工智能", "程序员", "代码", "科技"]
        for d in defaults:
            if d not in selected:
                selected.append(d)
            if len(selected) >= 5:
                break
    return "#" + " #".join(selected[:8])


def generate_post(project_root, theme, link, output, title=None, verbose=True):
    """生成 post.md 文件（降级方案：结构化模板）"""

    info = extract_info(project_root, theme, link)

    if not title:
        title = generate_title(info["project"], theme)
    if title:
        title = title[:20].rstrip("，、。；：")

    content = generate_content(info)
    tags_line = generate_tags_line(info["tags"])

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

    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(doc)

    if verbose:
        print(f"✅ post.md 已生成（模板模式）: {output}")
        print(f"   标题: {title}（{len(title)}字）")
        print(f"   贴图: {info['count']} 张")
        print(f"   标签: {tags_line}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="生成微信公众号推广文档 post.md（Agent LLM 双调用模式）"
    )
    parser.add_argument("--project", required=True, help="项目目录")
    parser.add_argument("--theme", required=True, help="主题")
    parser.add_argument("--link", default="", help="项目链接")
    parser.add_argument("--output", required=True, help="post.md 输出路径")
    parser.add_argument("--title", default=None, help="自定义标题（不超过20字符）")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    return (
        0
        if generate_post(
            project_root=os.path.abspath(args.project),
            theme=args.theme,
            link=args.link,
            output=args.output,
            title=args.title,
            verbose=not args.quiet,
        )
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
