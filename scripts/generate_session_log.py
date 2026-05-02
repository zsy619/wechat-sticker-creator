#!/usr/bin/env python3
"""
generate_session_log.py - 生成项目级 Session Log

Usage:
    python3 scripts/generate_session_log.py \
        --project opengeometry \
        --theme neon \
        --sticker-count 8 \
        --output ~/wechat-stickers/opengeometry/docs/session-log.md

    # 或在 run_full_pipeline.py 末尾自动调用
"""

import os
import argparse
from datetime import date


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
TEMPLATE_PATH = os.path.join(SKILL_DIR, 'docs', 'session-log-template.md')


def generate_session_log(project_name, theme, sticker_count, output,
                         input_type='N', generation_mode='auto',
                         input_total='N', output_total='N',
                         grand_total='N', cost_total='N',
                         status='已完成', verbose=True):
    """从模板生成 session-log.md"""

    if not os.path.exists(TEMPLATE_PATH):
        print(f"❌ 模板不存在: {TEMPLATE_PATH}", file=__import__('sys').stderr)
        return False

    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    # 替换占位符
    replacements = {
        '{project_name}': project_name,
        '{theme}': theme,
        '{sticker_count}': str(sticker_count),
        '{generated_date}': date.today().isoformat(),
        '{status}': status,
        '{input_type}': input_type,
        '{generation_mode}': generation_mode,
        '{input_total}': input_total,
        '{output_total}': output_total,
        '{grand_total}': grand_total,
        '{cost_total}': cost_total,
    }

    content = template
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        f.write(content)

    if verbose:
        print(f"✅ session-log.md 已生成: {output}")

    return True


def main():
    parser = argparse.ArgumentParser(description='生成项目 session-log.md')
    parser.add_argument('--project', required=True,
                        help='项目名称（用于文档标题）')
    parser.add_argument('--theme', required=True,
                        help='主题')
    parser.add_argument('--sticker-count', type=int, required=True,
                        help='贴图数量')
    parser.add_argument('--output', required=True,
                        help='session-log.md 输出路径')
    parser.add_argument('--input-type', default='N',
                        help='输入类型（URL/主题词/文本）')
    parser.add_argument('--generation-mode', default='auto',
                        help='生成模式（auto/ai/remotion）')
    parser.add_argument('--input-total', default='N',
                        help='总输入 Token')
    parser.add_argument('--output-total', default='N',
                        help='总输出 Token')
    parser.add_argument('--grand-total', default='N',
                        help='总 Token')
    parser.add_argument('--cost-total', default='N',
                        help='总估算费用')
    parser.add_argument('--status', default='已完成',
                        help='项目状态')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    generate_session_log(
        project_name=args.project,
        theme=args.theme,
        sticker_count=args.sticker_count,
        output=args.output,
        input_type=args.input_type,
        generation_mode=args.generation_mode,
        input_total=args.input_total,
        output_total=args.output_total,
        grand_total=args.grand_total,
        cost_total=args.cost_total,
        status=args.status,
        verbose=not args.quiet,
    )


if __name__ == '__main__':
    main()
