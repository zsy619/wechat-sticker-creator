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

    python3 scripts/generate_content_analysis.py \
        --input "这是一个关于程序员日常的表情包需求..." \
        --output wechat-stickers/coder-life/
"""

import os, sys, re, json, argparse

# ── 主题配色（用于背景参考）────────────────────────────────
THEMES = {
    "cyberpunk":  {"primary": "#00FFFF", "secondary": "#FF00FF", "bg": "#0D0D1A"},
    "kawaii":     {"primary": "#FF69B4", "secondary": "#FFB6C1", "bg": "#FFF0F5"},
    "neon":       {"primary": "#FF00FF", "secondary": "#00FFFF", "bg": "#1A0033"},
    "retro":      {"primary": "#FFD700", "secondary": "#FF6B35", "bg": "#2D1B00"},
    "hand-drawn": {"primary": "#8B4513", "secondary": "#D2691E", "bg": "#FFF8DC"},
    "minimal":    {"primary": "#212529", "secondary": "#495057", "bg": "#F8F9FA"},
    "meme":       {"primary": "#FF4500", "secondary": "#FFD700", "bg": "#1A1A1A"},
}

# ── 输入类型检测 ──────────────────────────────────────────

def detect_input_type(raw_input):
    """返回 'url' | 'topic' | 'text'"""
    raw = raw_input.strip()
    if raw.startswith('http://') or raw.startswith('https://'):
        return 'url'
    if len(raw) <= 15 and not re.search(r'[\u4e00-\u9fff]', raw):
        # 纯英文短文本 = 主题词
        return 'topic'
    if len(raw) <= 15 and not re.search(r'\s', raw):
        # 短文本无空格 = 主题词
        return 'topic'
    return 'text'

# ── 内容获取 ──────────────────────────────────────────────

def fetch_url_content(url):
    """调用 baoyu-url-to-markdown 获取 URL 内容"""
    import subprocess
    try:
        # 尝试 baoyu-url-to-markdown
        result = subprocess.run(
            ['baoyu-url-to-markdown', url],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return result.stdout
    except FileNotFoundError:
        pass
    except Exception:
        pass

    # fallback: 用 curl 简单获取
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode('utf-8', errors='ignore')
        # 简单提取 <title> 和前几段
        title = re.search(r'<title>(.*?)</title>', raw, re.I)
        title = title.group(1).strip() if title else ''
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', ' ', raw)
        text = re.sub(r'\s+', ' ', text).strip()
        return f"# {title}\n\n{text[:3000]}"
    except Exception as e:
        return f"[URL fetch failed: {e}]"

def web_search(query):
    """调用 WebSearch 获取相关内容（通过 OpenClaw 内置命令）"""
    import subprocess
    try:
        # 使用内置 WebSearch 工具
        result = subprocess.run(
            ['WebSearch', query],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return result.stdout
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return f"[WebSearch unavailable for: {query}]"

# ── LLM 内容聚合 ───────────────────────────────────────────

def build_content_analysis_prompt(raw_input, input_type, web_results):
    """构建发送给 LLM 的内容聚合 prompt"""
    theme_note = "\n".join([
        f"- {k}: primary={v['primary']}, secondary={v['secondary']}, bg={v['bg']}"
        for k, v in THEMES.items()
    ])

    prompt = f"""你是微信贴图设计师，擅长分析用户需求并生成贴图设计方向。

## 用户输入
{raw_input}

## 输入类型
{input_type}

## 联网搜索结果
{web_results[:4000] if web_results else '[无可用搜索结果]'}

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

## 推荐视觉元素（按优先级）
列出 10-20 个适合该主题的 emoji / 视觉元素 key（必须使用英文 key，参考 vocabulary）：
如 brain, terminal, lightning, heart, trophy, rocket, coffee, code, algorithm 等
```
"""
    return prompt

def call_llm(prompt):
    """通过 OpenClaw 的 ai_func 聚合内容"""
    try:
        from hermes_tools import terminal
        # 使用 claude-code 或内置 ai 调用
        escaped_prompt = prompt.replace('"', '\\"')
        result = terminal(
            f"""cat << 'LLM_PROMPT' | claude --print -p "
system: 你是一个贴图设计师，擅长分析用户需求并生成贴图设计方向。
user: {escaped_prompt}
LLM_PROMPT"""
        )
        if result.get('output'):
            return result['output']
    except Exception:
        pass

    # fallback: 返回纯文本提示（用户手动处理）
    return f"[LLM unavailable - please analyze manually]\n\n原始输入：{prompt[:500]}"

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
        content = fetch_url_content(raw)
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
        # 从文本中提取关键词作为搜索词
        words = re.findall(r'[\w\u4e00-\u9fff]{2,}', raw)
        search_queries = words[:3] if words else [raw[:20]]
        search_queries = [raw[:30]] + [q + " 表情包" for q in search_queries[:2]]

    # 2. 联网搜索
    web_results = []
    for q in search_queries[:3]:
        print(f"[搜索] {q}")
        r = web_search(q)
        web_results.append(f"## {q}\n{r}")
    web_results_str = "\n\n".join(web_results)

    # 3. LLM 聚合
    print("[LLM] 正在聚合内容...")
    prompt = build_content_analysis_prompt(raw, input_type, web_results_str)
    analysis = call_llm(prompt)

    # 4. 写入文件
    output_path = os.path.join(args.output, 'content-analysis.md')
    with open(output_path, 'w') as f:
        f.write(f"# 内容聚合分析\n\n")
        f.write(f"> **输入类型**: {input_type}\n")
        f.write(f"> **原始输入**: {raw}\n\n")
        f.write("---\n\n")
        f.write(analysis)

    print(f"\n✅ 内容聚合分析已生成: {output_path}")
    print(f"   下一步: python3 scripts/generate_manifest.py --input {output_path} --output {os.path.join(args.output, 'sticker-manifest.md')}")

if __name__ == '__main__':
    main()
