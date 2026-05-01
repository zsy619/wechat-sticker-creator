#!/usr/bin/env python3
"""
generate_content_analysis.py - 内容聚合分析

分析用户输入（URL / 主题 / 内容文本），联网搜索相关内容，
生成 content-analysis.md。

Usage:
    python3 scripts/generate_content_analysis.py \
        --input "AI编程助手" \
        --output wechat-stickers/ai-coding-assistant/

    python3 scripts/generate_content_analysis.py \
        --input "https://github.com/xxx/ai-tool" \
        --output wechat-stickers/ai-tool/
"""

import os, sys, re, argparse, subprocess

# ── 主题配色（来自 _vocab）────────────────────────────────
try:
    from _vocab import THEMES
except ImportError:
    THEMES = {
        "cyberpunk":  {"primary": "#00FFFF", "secondary": "#FF00FF", "bg": "#0D0D1A", "text": "#FFFFFF", "accent": "#00FF88"},
        "kawaii":     {"primary": "#FF69B4", "secondary": "#FFB6C1", "bg": "#FFF0F5", "text": "#4A4A4A", "accent": "#FF1493"},
        "neon":       {"primary": "#FF00FF", "secondary": "#00FFFF", "bg": "#1A0033", "text": "#FFFFFF", "accent": "#FF69B4"},
        "retro":      {"primary": "#FFD700", "secondary": "#FF6B35", "bg": "#2D1B00", "text": "#FFFFFF", "accent": "#FF4500"},
        "hand-drawn": {"primary": "#8B4513", "secondary": "#D2691E", "bg": "#FFF8DC", "text": "#4A4A4A", "accent": "#CD853F"},
        "minimal":    {"primary": "#212529", "secondary": "#495057", "bg": "#F8F9FA", "text": "#212529", "accent": "#6C757D"},
        "meme":       {"primary": "#FF4500", "secondary": "#FFD700", "bg": "#1A1A1A", "text": "#FFFFFF", "accent": "#FF6347"},
    }

# ── 输入类型检测 ──────────────────────────────────────────

def detect_input_type(raw_input):
    """返回 'url' | 'topic' | 'text'"""
    raw = raw_input.strip()
    if raw.startswith('http://') or raw.startswith('https://'):
        return 'url'
    # 纯英文字符（无空格、无中文）且较短 = 主题词
    if re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_-]*', raw) and len(raw) <= 20:
        return 'topic'
    return 'text'

# ── 内容获取 ──────────────────────────────────────────────

def fetch_url(url):
    """使用 curl 获取网页内容（降级：移除对 baoyu-url-to-markdown 的依赖）"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '--max-time', '30', '-A',
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
             url],
            capture_output=True, text=True, timeout=35
        )
        if result.returncode == 0 and len(result.stdout) > 100:
            return result.stdout
    except Exception as e:
        print(f"[WARN] curl 失败: {e}")
    return ""


# ── 联网搜索 ──────────────────────────────────────────────
def web_search(query):
    """通过 claude --web-search 联网搜索"""
    try:
        result = subprocess.run(
            ['claude', '--print', '-p',
             f'search: {query}', 'Please search the web for: ' + query],
            capture_output=True, text=True, timeout=90,
            env={**os.environ, 'NO_CONFIG': '1'}
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:2000]
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return f"[WebSearch unavailable: {query}]"

# ── LLM 内容聚合 ──────────────────────────────────────────

def build_content_analysis_prompt(raw_input, input_type, web_results, theme):
    """构建发送给 LLM 的内容聚合 prompt"""
    theme_lines = '\n'.join([
        f"- {k}: primary={v['primary']}, secondary={v['secondary']}, bg={v['bg']}"
        for k, v in THEMES.items()
    ])

    return f"""你是微信贴图设计师，擅长分析用户需求并生成贴图设计方向。

## 用户输入
{raw_input}

## 输入类型
{input_type}

## 联网搜索结果
{web_results if web_results else '[无可用搜索结果]'}

## 你的任务
生成一份「内容聚合分析」，供后续贴图设计使用。

### 输出格式
```markdown
# 内容聚合分析

## 核心主题
1-2 句话概括主题（不超过 50 字）

## 关键词汇
列出 8-15 个与主题紧密相关的关键词（用于后续 sticker 设计）

## 情感基调
选择最合适的基调：
- [ ] 轻松幽默（娱乐类）
- [ ] 专业干练（工具/科技类）
- [ ] 温暖治愈（生活/情感类）
- [ ] 酷炫潮流（时尚/科技类）

## 使用场景
列出 4-6 个典型使用场景（每条不超过 20 字）

## 热点趋势
根据搜索结果，总结 2-3 个当前热点或趋势

## 贴图设计方向
给出整体设计方向建议，包括：
- 适合的风格主题（可选：cyberpunk / kawaii / neon / retro / hand-drawn / minimal / meme）
- 主色调偏好（根据情感基调推荐）
- 建议的贴图数量（6 张标准 / 8 张扩展 / 4 张精简）
- **推荐主题键**: 根据内容推荐最合适的主题（从 {list(THEMES.keys())} 中选择）

## 推荐视觉元素（按优先级）
列出 10-20 个适合该主题的 emoji / 视觉元素 key（必须使用英文 key，参考 vocabulary）：
如 brain, terminal, lightning, heart, trophy, rocket, coffee, code, algorithm 等
```

### 主题参考
{theme_lines}

### 指定主题偏好
用户已选择或推荐的主题：**{theme}**
请结合该主题的配色和风格进行推荐。
"""

def call_llm(prompt):
    """通过 claude --print -p 直接调用 LLM"""
    try:
        result = subprocess.run(
            ['claude', '--print', '-p', prompt],
            capture_output=True, text=True, timeout=120,
            input=prompt,
            env={**os.environ, 'NO_CONFIG': '1'}
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except FileNotFoundError:
        return _llm_fallback_notice(prompt)
    except Exception:
        pass
    return _llm_fallback_notice(prompt)

def _llm_fallback_notice(prompt):
    """LLM 不可用时的降级提示"""
    # 尝试从 prompt 中提取原始输入（作为手动分析线索）
    match = re.search(r'## 用户输入\s+(.{10,100})', prompt)
    raw_input = match.group(1) if match else '[未提供]'
    return (
        f"[LLM unavailable - 请手动分析]\n\n"
        f"原始输入：{raw_input}\n\n"
        f"请参考上方格式，手动创建 content-analysis.md。"
    )

# ── 主函数 ────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='微信贴图 - 内容聚合分析')
    ap.add_argument('--input', required=True, help='URL / 主题词 / 内容文本')
    ap.add_argument('--output', required=True, help='输出目录（content-analysis.md 所在目录）')
    ap.add_argument('--theme', default='cyberpunk', help='推荐主题风格')
    args = ap.parse_args()

    os.makedirs(args.output, exist_ok=True)
    raw = args.input.strip()
    input_type = detect_input_type(raw)

    print(f"[输入类型] {input_type}")
    print(f"[输入内容] {raw[:80]}{'...' if len(raw) > 80 else ''}")

    # 1. 获取内容
    if input_type == 'url':
        content = fetch_url(raw)
        print("[内容获取] baoyu-url-to-markdown / curl 完成")
        search_queries = [
            raw.split('/')[-1] if '/' in raw else raw,
            raw + " 微信贴图",
        ]
    elif input_type == 'topic':
        content = raw
        search_queries = [raw, raw + " 表情包", raw + " 微信贴图"]
    else:  # text
        content = raw
        words = re.findall(r'[\w\u4e00-\u9fff]{2,}', raw)
        kw = words[:3] if words else [raw[:20]]
        search_queries = [raw[:30]] + [q + " 表情包" for q in kw[:2]]

    # 2. 联网搜索（最多 3 个query）
    web_results = []
    for q in search_queries[:3]:
        print(f"[搜索] {q}")
        r = web_search(q)
        web_results.append(f"## {q}\n{r[:500]}")
    web_results_str = '\n\n'.join(web_results)

    # 3. LLM 聚合
    print("[LLM] 正在聚合内容...")
    prompt = build_content_analysis_prompt(raw, input_type, web_results_str, args.theme)
    analysis = call_llm(prompt)

    # 4. 写入文件
    output_path = os.path.join(args.output, 'content-analysis.md')
    with open(output_path, 'w') as f:
        f.write(f"# 内容聚合分析\n\n")
        f.write(f"> **输入类型**: {input_type}\n")
        f.write(f"> **原始输入**: {raw}\n\n")
        f.write(f"> **推荐主题**: {args.theme}\n\n")
        f.write("---\n\n")
        f.write(analysis)

    print(f"\n✅ 内容聚合分析已生成: {output_path}")
    next_step = os.path.join(args.output, 'sticker-manifest.md')
    print(f"   下一步: python3 scripts/generate_manifest.py --input {output_path} --output {next_step}")

if __name__ == '__main__':
    main()
