#!/usr/bin/env python3
"""
copy_docs.py - 复制技能内置文档到项目目录

Usage:
    from copy_docs import copy_skill_docs
    copy_skill_docs('/path/to/project', theme='neon')

    python3 scripts/copy_docs.py --project /path/to/project --theme neon
"""

import os
import shutil
import argparse


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(SKILL_DIR, 'docs')


# 要复制的文档列表（技能内置只读文档）
# 注意：session-log-template.md 不复制 — 由 generate_session_log.py 在工作流中直接渲染到项目
SKILL_DOCS = [
    'content-format.md',
    'copy.md',
    'frame-design.md',
    'image-generation.md',
    'output.md',
    'project-structure.md',
    'prompts-format.md',
    'qa.md',
    'remotion-projects.md',
    'workflow.md',
]


def copy_skill_docs(project_root, theme=None, verbose=True):
    """复制技能内置文档到项目 docs/ 目录"""
    if theme:
        print(f"[文档复制] 主题={theme}", flush=True)

    project_docs = os.path.join(project_root, 'docs')
    os.makedirs(project_docs, exist_ok=True)

    copied = []
    skipped = []
    for doc in SKILL_DOCS:
        src = os.path.join(DOCS_DIR, doc)
        dst = os.path.join(project_docs, doc)
        if not os.path.exists(src):
            if verbose:
                print(f"[跳过] {doc} (源文件不存在)", flush=True)
            skipped.append(doc)
            continue
        shutil.copy2(src, dst)
        copied.append(doc)
        if verbose:
            print(f"[复制] {doc} → {project_docs}/", flush=True)

    if verbose:
        print(f"\n✅ 文档复制完成: {len(copied)} 复制, {len(skipped)} 跳过")

    return len(copied) > 0


def main():
    parser = argparse.ArgumentParser(description='复制技能内置文档到项目目录')
    parser.add_argument('--project', required=True,
                        help='项目根目录路径')
    parser.add_argument('--theme', default=None,
                        help='主题（仅用于日志）')
    args = parser.parse_args()

    copy_skill_docs(
        project_root=os.path.abspath(args.project),
        theme=args.theme,
        verbose=True,
    )


if __name__ == '__main__':
    main()
