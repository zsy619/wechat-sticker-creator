#!/usr/bin/env python3
"""
generate_session_log.py - 生成项目级 Session Log

基于项目信息生成 session-log.md，记录 token 消耗和时间线。

Usage:
    python3 scripts/generate_session_log.py \
        --project opengeometry \
        --theme neon \
        --sticker-count 8 \
        --output ~/wechat-stickers/opengeometry/session-log.md
"""

import os
import re
import argparse
import sys
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)


# ── Token 估算常量 ──────────────────────────────────────────

TOKEN_RATES = {
    'minimax/MiniMax-M2.7': {'input': 1.0, 'output': 1.0},
    'claude': {'input': 3.0, 'output': 15.0},
    'gpt': {'input': 2.5, 'output': 10.0},
}


def estimate_tokens(sticker_count, has_content_analysis=True, has_manifest=True,
                   has_prompts=True, has_frames=True):
    estimates = {}
    estimates['content_analysis'] = {
        'input': 3000 if has_content_analysis else 0,
        'output': 2000 if has_content_analysis else 0,
    }
    estimates['manifest'] = {
        'input': 5000 if has_manifest else 0,
        'output': 3000 if has_manifest else 0,
    }
    per_prompt = {'input': 4000, 'output': 2500}
    estimates['prompts'] = {
        'input': per_prompt['input'] * sticker_count if has_prompts else 0,
        'output': per_prompt['output'] * sticker_count if has_prompts else 0,
    }
    per_frame = {'input': 2000, 'output': 1500}
    estimates['frames'] = {
        'input': per_frame['input'] * sticker_count if has_frames else 0,
        'output': per_frame['output'] * sticker_count if has_frames else 0,
    }
    return estimates


def calc_cost(input_tokens, output_tokens, model='minimax/MiniMax-M2.7'):
    rate = TOKEN_RATES.get(model, TOKEN_RATES['minimax/MiniMax-M2.7'])
    return (input_tokens + output_tokens) / 1_000_000 * (rate['input'] + rate['output'])


# ── 主函数

def generate_session_log(project_name, theme, sticker_count, output,
                         input_type='N', generation_mode='auto',
                         input_total=None, output_total=None,
                         grand_total=None, cost_total=None,
                         status='已完成', verbose=True):
    """从模板生成 session-log.md（降级方案）"""

    # 统一归一化：'N' 字符串视为 None，触发内部自动计算
    if input_total in (None, 'N'):
        input_total = None
    if output_total in (None, 'N'):
        output_total = None
    if grand_total in (None, 'N'):
        grand_total = None
    if cost_total in (None, 'N'):
        cost_total = None

    # 始终计算 token 估算值（供各路径使用）
    est = estimate_tokens(sticker_count)

    # 如果调用方没传 token 估算值，内部自动计算
    if input_total is None:
        inp = sum(e['input'] for e in est.values())
        out = sum(e['output'] for e in est.values())
        input_total = inp
        output_total = out
        grand_total = inp + out
        cost_total = calc_cost(inp, out)

    return _generate_inline(project_name, theme, sticker_count, output,
                           input_type, generation_mode, input_total,
                           output_total, grand_total, cost_total, status, verbose)


def _generate_inline(project_name, theme, sticker_count, output,
                     input_type, generation_mode, input_total,
                     output_total, grand_total, cost_total,
                     status, verbose):
    """内联生成（无模板时的降级方案）"""

    estimates = estimate_tokens(sticker_count)
    total_input = sum(e['input'] for e in estimates.values()) if input_total == 'N' else int(input_total)
    total_output = sum(e['output'] for e in estimates.values()) if output_total == 'N' else int(output_total)
    total_tokens = total_input + total_output if grand_total == 'N' else int(grand_total)
    cost = calc_cost(total_input, total_output) if cost_total == 'N' else float(cost_total)

    content = f"""---
name: {project_name}-session-log
project: {project_name}
theme: {theme}
generated: {date.today().isoformat()}
status: {status}
---

# Session Log - {project_name}

## 项目信息
| 字段 | 值 |
|------|-----|
| **项目名称** | {project_name} |
| **主题** | {theme} |
| **贴图数量** | {sticker_count} 张 |
| **生成时间** | {date.today().isoformat()} |
| **状态** | {status} |

## 模型配置
| 字段 | 值 |
|------|-----|
| **默认模型** | minimax/MiniMax-M2.7 |
| **Token 追踪** | session_status 工具 |

## Token 消耗记录
| 阶段 | 输入 Token | 输出 Token | 合计 Token | 估算费用 |
|------|-----------|-----------|-----------|---------|
| 内容聚合分析 | {estimates['content_analysis']['input']:,} | {estimates['content_analysis']['output']:,} | {estimates['content_analysis']['input']+estimates['content_analysis']['output']:,} | ¥{calc_cost(estimates['content_analysis']['input'], estimates['content_analysis']['output']):.4f} |
| Manifest 生成 | {estimates['manifest']['input']:,} | {estimates['manifest']['output']:,} | {estimates['manifest']['input']+estimates['manifest']['output']:,} | ¥{calc_cost(estimates['manifest']['input'], estimates['manifest']['output']):.4f} |
| Prompts × {sticker_count} | {estimates['prompts']['input']:,} | {estimates['prompts']['output']:,} | {estimates['prompts']['input']+estimates['prompts']['output']:,} | ¥{calc_cost(estimates['prompts']['input'], estimates['prompts']['output']):.4f} |
| 图片生成 × {sticker_count} | {estimates['frames']['input']:,} | {estimates['frames']['output']:,} | {estimates['frames']['input']+estimates['frames']['output']:,} | ¥{calc_cost(estimates['frames']['input'], estimates['frames']['output']):.4f} |
| **总计** | **{total_input:,}** | **{total_output:,}** | **{total_tokens:,}** | **¥{cost:.4f}** |

> 费用估算：MiniMax-M2.7 ¥1/1M tokens（输入+输出合计）

## 各阶段详情

### 内容聚合分析
- **输入**: {input_type}
- **处理时长**: 约 10-30 秒
- **备注**: 分析输入类型，提取核心主题和关键词

### Manifest 生成
- **贴图数量**: {sticker_count} 张
- **处理时长**: 约 5-15 秒
- **备注**: 生成贴图设计清单

### Prompts 生成
- **文件数**: {sticker_count}
- **处理时长**: 约 {sticker_count * 3}-{sticker_count * 8} 秒
- **备注**: 为每张贴图生成 AI 图像 prompt

### 图片生成
- **模式**: {generation_mode}（AI → Remotion 两段式）
- **成功数**: {sticker_count} / {sticker_count}
- **处理时长**: 约 {sticker_count * 15}-{sticker_count * 60} 秒
- **备注**: AI 生成为主，Remotion 帧导出备选

## 问题与修复
> 如有异常或修复，记录于此

| 日期 | 问题描述 | 修复方案 |
|------|---------|---------|
| - | - | - |

## 更新日志
| 日期 | 操作 | 结果 |
|------|------|------|
| {date.today().isoformat()} | 初始生成 | 贴图 {sticker_count} 张 |
"""

    os.makedirs(os.path.dirname(os.path.abspath(output)) or '.', exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        f.write(content)

    if verbose:
        print(f"✅ session-log.md 已生成（内联模式）: {output}")

    return True


# ── 主函数 ─────────────────────────────────────────────

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
    parser.add_argument('--input-type', default='URL',
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
    parser.add_argument('--verify', action='store_true',
                       help='仅验证输出目录，不生成文档')
    args = parser.parse_args()

    # --verify 模式
    if args.verify:
        output_dir = os.path.dirname(os.path.abspath(args.output)) or '.'
        exists = os.path.exists(output_dir)
        print(f"[verify] {'✅' if exists else '❌'} 输出目录: {output_dir}")
        return 0 if exists else 1

    return 0 if generate_session_log(
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
    ) else 1


if __name__ == '__main__':
    sys.exit(main())
