#!/usr/bin/env python3
"""
generate_manifest.py - 贴图设计 Manifest 生成

读取 content-analysis.md，生成 sticker-manifest.md。
vocabulary 校验使用 _vocab 模块（单一数据源）。

Usage:
    python3 scripts/generate_manifest.py \
        --input content-analysis.md \
        --output sticker-manifest.md
"""

import os, sys, re, argparse

# ── 词汇表（来自 _vocab 共享模块）────────────────────────────
from _vocab import VOCABULARY, THEMES, filter_valid_keys

# ── 校验函数 ──────────────────────────────────────────────


def validate_vocabulary(visual_elements):
    """校验 visual_elements 中的 key 是否在词汇表范围内"""
    _, invalid = filter_valid_keys(visual_elements)
    return invalid


def parse_content_analysis(path):
    """解析 content-analysis.md，提取关键信息（含 theme 推荐）"""
    with open(path) as f:
        content = f.read()

    # 提取核心主题
    theme_match = re.search(r"## 核心主题\s*\n+(.*?)(?=\n##|\Z)", content, re.DOTALL)
    core_theme = theme_match.group(1).strip() if theme_match else ""

    # 提取关键词汇
    kw_match = re.search(r"## 关键词汇\s*\n+(.*?)(?=\n##|\Z)", content, re.DOTALL)
    keywords = kw_match.group(1).strip() if kw_match else ""

    # 提取情感基调
    tone_match = re.search(r"## 情感基调\s*\n+(.*?)(?=\n##|\Z)", content, re.DOTALL)
    tone = tone_match.group(1).strip() if tone_match else ""

    # 提取使用场景
    scene_match = re.search(r"## 使用场景\s*\n+(.*?)(?=\n##|\Z)", content, re.DOTALL)
    scenes = scene_match.group(1).strip() if scene_match else ""

    # 提取设计方向
    dir_match = re.search(r"## 贴图设计方向\s*\n+(.*?)(?=\n##|\Z)", content, re.DOTALL)
    direction = dir_match.group(1).strip() if dir_match else ""

    # 提取推荐的 theme 键（从分析结果的推荐主题中解析）
    recommended_theme = None
    theme_candidates = [
        "cyberpunk",
        "kawaii",
        "neon",
        "retro",
        "hand-drawn",
        "minimal",
        "meme",
    ]
    for tc in theme_candidates:
        if tc in content.lower():
            recommended_theme = tc
            break

    return {
        "core_theme": core_theme,
        "keywords": keywords,
        "tone": tone,
        "scenes": scenes,
        "direction": direction,
        "recommended_theme": recommended_theme,
    }


def build_manifest_prompt(analysis, project_name, theme_fallback):
    """构建生成 manifest 的 LLM prompt"""
    # 使用模块级导入的 VOCABULARY（来自 _vocab）
    vocab_list = ", ".join(sorted(VOCABULARY))

    # 确定推荐 theme
    recommended = analysis.get("recommended_theme") or theme_fallback or "cyberpunk"

    return f"""你是微信贴图设计师。基于以下内容聚合分析，设计一套 {project_name} 微信贴图。

## 内容聚合分析

**核心主题**: {analysis['core_theme']}

**关键词汇**:
{analysis['keywords']}

**情感基调**:
{analysis['tone']}

**使用场景**:
{analysis['scenes']}

**贴图设计方向**:
{analysis['direction']}

## 你的任务
生成「贴图设计清单」(sticker-manifest.md)，输出 6 张贴图的完整设计。

### 重要约束
1. **visual_elements 必须全部使用英文 key**，禁止使用中文 key
2. 每个 key 必须在下述词汇表范围内（已过滤无效 key）：
   {vocab_list}
3. **推荐主题**: {recommended}（来自内容分析推荐）
4. 严格按以下 Markdown 格式输出，贴图数量固定为 6 张

### 严格输出格式（必须遵循）
```markdown
# 贴图设计清单

## 项目信息
- **项目名称**: {project_name}
- **贴图数量**: 6 张
- **情感基调**: （从分析中提取）
- **主题**: {recommended}

## 贴图1: {{名称}}

- **序号**: 01
- **名称**: {{中文名}}
- **使用场景**: {{场景描述}}
- **核心文案**: {{10-16字，有画面感的口语}}
- **视觉元素**: [key1, key2, key3]  （必须全部使用英文 key）
- **主题键**: {recommended}

## 贴图2: {{名称}}
...
（共 6 张，序号 01-06）
```
"""


def call_llm(prompt):
    """调用 LLM 生成 manifest（使用 claude --print）"""
    try:
        result = subprocess.run(
            ["claude", "--print", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120,
            input=prompt,
            env={**os.environ, "NO_CONFIG": "1"},
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return (
        "[LLM unavailable - please design manifest manually]\n\n"
        "请参考上方内容分析的关键词汇和方向，手动创建 sticker-manifest.md。"
    )


# ── 主函数 ────────────────────────────────────────────────


def main():
    import subprocess  # 确保可用

    ap = argparse.ArgumentParser(description="微信贴图 - Manifest 生成")
    ap.add_argument("--input", required=True, help="content-analysis.md 路径")
    ap.add_argument("--output", required=True, help="sticker-manifest.md 输出路径")
    ap.add_argument("--project-name", default="贴图项目", help="项目名称")
    ap.add_argument("--theme", default=None, help="主题风格（manifest 未指定时使用）")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"[错误] 文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"[解析] {args.input}")
    analysis = parse_content_analysis(args.input)

    print(f"[核心主题] {analysis['core_theme'][:60]}...")
    print(f"[关键词汇] {analysis['keywords'][:80]}...")

    print(f"[LLM] 正在生成 manifest...")
    prompt = build_manifest_prompt(analysis, args.project_name, args.theme)
    manifest_content = call_llm(prompt)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w") as f:
        f.write("# 贴图设计清单\n\n")
        f.write(f"> **来源**: {os.path.basename(args.input)}\n")
        f.write(f"> **生成时间**: 自动生成\n")
        recommended = analysis.get("recommended_theme") or args.theme or "cyberpunk"
        f.write(f"> **推荐主题**: {recommended}\n\n")
        f.write("---\n\n")
        f.write(manifest_content)

    print(f"\n✅ Manifest 已生成: {args.output}")
    print(
        f"   下一步: python3 scripts/generate_prompts.py --input {args.output} --output prompts/"
    )
    print(f"\n⚠️  重要：manifest 中所有 visual_elements 必须使用英文 key（见词汇表）")
    print(
        f"   校验: python3 scripts/qa_check.py --prompts prompts/ --vocabulary docs/prompts-format.md"
    )


if __name__ == "__main__":
    main()
