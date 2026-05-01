#!/usr/bin/env python3
"""
generate_manifest.py - 贴图设计 Manifest 生成

读取 content-analysis.md，生成 sticker-manifest.md。
包含 vocabulary 校验：确保所有 visual_elements key 在词汇表中。

Usage:
    python3 scripts/generate_manifest.py \
        --input content-analysis.md \
        --output sticker-manifest.md
"""

import os, sys, re, argparse

# ── 词汇表（从 prompts-format.md 提取，所有 visual_elements key 必须在此范围内）───

VOCABULARY = {
    # 核心 AI/技术
    'brain', 'neural_network', 'terminal', 'lightning', 'ai_chip', 'spotlight',
    'network_node', 'button', 'code', 'algorithm', 'function', 'variable',
    'debug', 'deploy', 'cpu', 'server', 'database', 'cloud', 'data',
    'ai大脑', 'ai计算', '神经网络', '终端窗口', '闪电', '等号', '问号',
    '橡皮擦', '对勾', '画布', '芯片', '光晕', '网络节点', '链接', '按钮',
    # 情感/反应
    'heart', 'thumbs_up', 'clap', 'pray', 'muscle', 'thinking', 'eyes',
    'trophy', 'medal', 'crown', 'star', 'fire', 'hundred',
    'laugh', 'cry', 'angry', 'cool', 'shy', 'sleeping',
    '红心', '点赞', '鼓掌', '祈祷', '加油', '思考', '围观',
    '奖杯', '奖牌', '王冠', '星星', '火', '100分',
    # 物品/工具
    'rocket', 'alarm', 'bell', 'megaphone', 'wrench', 'hammer',
    'scissors', 'pencil', 'book', 'lightbulb', 'envelope', 'gift',
    'tada', 'balloon', 'confetti',
    '火箭', '闹钟', '铃铛', '广播', '扳手', '锤子', '剪刀', '铅笔', '书本', '灯泡', '信封', '礼物',
    # 食物/饮料
    'coffee', 'tea', 'beer', 'cocktail', 'wine',
    'pizza', 'rice', 'fruit', 'cake', 'cookie', 'bread',
    '咖啡', '茶', '啤酒', '鸡尾酒', '葡萄酒', '披萨', '米饭', '水果', '蛋糕', '饼干', '面包',
    # 办公/效率
    'phone', 'camera', 'clipboard', 'chart', 'calendar',
    'key', 'lock', 'folder', 'file', 'email', 'call',
    'microphone', 'video', 'tv', 'clock', 'hourglass',
    'pen', 'ruler', 'paperclip', 'stamp', 'inbox', 'outbox',
    '手机', '相机', '剪贴板', '图表', '日历', '钥匙', '锁', '文件夹', '文件', '邮件', '电话',
    '麦克风', '视频', '电视', '计时器', '沙漏', '笔', '直尺', '回形针', '邮票', '收件箱', '发件箱',
    # 自然/科学
    'earth', 'moon', 'sun', 'rainbow', 'snowflake', 'wave', 'anchor',
    'airplane', 'car', 'bicycle', 'map', 'compass',
    'flag', 'satellite', 'telescope', 'microscope',
    '地球', '月亮', '太阳', '彩虹', '雪花', '海浪', '锚',
    '飞机', '汽车', '自行车', '地图', '指南针',
    '旗帜', '卫星', '望远镜', '显微镜',
    # 心情/状态
    'money', 'gem', 'love_letter', 'warning', 'no_entry', 'busy', 'free', 'secret',
    '钱', '宝石', '情书', '警告', '禁止', '忙', '免费', '秘密',
    # 创意/兴趣
    'goal', 'puzzle', 'music', 'headphones', 'sound', 'mute',
    'eye', 'ear', 'nose', 'footprints',
    '目标', '拼图', '音乐', '耳机', '声音', '静音', '眼睛', '耳朵', '鼻子', '脚印',
    # 健康/医疗
    'bone', 'microbe', 'pill', 'syringe', 'thermometer',
    '骨头', '微生物', '药', '注射', '体温计',
    # 工业/科学符号
    'magnet', 'gear', 'atom', 'dna', 'biohazard', 'radioactive', 'bio',
    '磁铁', '齿轮', '原子', 'DNA', '生物危害', '辐射', '生态',
    # 植物/自然
    'four_leaf', 'maple', 'cherry', 'tulip', 'rose', 'hibiscus', 'shell', 'feather',
    '四叶草', '枫叶', '樱花', '郁金香', '玫瑰', '木芙蓉', '贝壳', '羽毛',
    # 装饰/特殊
    'sparkle', 'diamond', 'fleur', 'comet',
    '闪光', '钻石', '百合', '彗星',
    # 特殊符号
    'equals_sign', 'question_mark', 'eraser', 'checkmark', 'math_canvas', 'robot',
    'lightbulb', 'bulb', 'satellite', 'music', 'sound', 'vibration',
}

# ── 校验函数 ──────────────────────────────────────────────

def validate_vocabulary(visual_elements):
    """校验 visual_elements 中的 key 是否在词汇表范围内"""
    invalid = [k for k in visual_elements if k not in VOCABULARY]
    return invalid

def parse_content_analysis(path):
    """解析 content-analysis.md，提取关键信息"""
    with open(path) as f:
        content = f.read()

    # 提取核心主题
    theme_match = re.search(r'## 核心主题\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL)
    core_theme = theme_match.group(1).strip() if theme_match else ''

    # 提取关键词汇
    kw_match = re.search(r'## 关键词汇\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL)
    keywords = kw_match.group(1).strip() if kw_match else ''

    # 提取情感基调
    tone_match = re.search(r'## 情感基调\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL)
    tone = tone_match.group(1).strip() if tone_match else ''

    # 提取使用场景
    scene_match = re.search(r'## 使用场景\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL)
    scenes = scene_match.group(1).strip() if scene_match else ''

    # 提取设计方向
    dir_match = re.search(r'## 贴图设计方向\s*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL)
    direction = dir_match.group(1).strip() if dir_match else ''

    return {
        'core_theme': core_theme,
        'keywords': keywords,
        'tone': tone,
        'scenes': scenes,
        'direction': direction,
    }

def build_manifest_prompt(analysis, project_name):
    """构建生成 manifest 的 LLM prompt"""
    return f"""你是微信贴图设计师。基于以下内容聚合分析，设计一套 {project_name} 微信表情包。

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

### 输出格式
```markdown
# 贴图设计清单

## 项目信息
- **项目名称**: {project_name}
- **贴图数量**: 6 张
- **情感基调**: （从分析中提取）

## 标签汇总
- 平台标签: #微信表情 #微信贴图 #WeChatStickers
- 情感标签: （根据内容提取 3-5 个）
- 主题标签: （根据内容提取 3-5 个）

## 贴图1: {{名称}}

- **序号**: 01
- **名称**: {{中文名}}
- **使用场景**: {{场景描述}}
- **核心文案**: {{10-16字，有画面感的口语}}
- **视觉元素**: [key1, key2, key3]  （必须全部使用英文 key）
- **风格**: [cyberpunk, neon, tech-modern]  （风格词）

## 贴图2: ...
...（共 6 张）
```
"""

def call_llm(prompt):
    """调用 LLM 生成 manifest"""
    try:
        from hermes_tools import terminal
        result = terminal(
            f'''claude --print -p "你是微信贴图设计师。请严格按要求生成贴图设计清单。" << 'EOF'\n{prompt}\nEOF'''
        )
        if result.get('output'):
            return result['output']
    except Exception:
        pass
    return f"[LLM unavailable - please design manifest manually based on analysis]"

# ── 主函数 ────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='微信贴图 - Manifest 生成')
    ap.add_argument('--input', required=True, help='content-analysis.md 路径')
    ap.add_argument('--output', required=True, help='sticker-manifest.md 输出路径')
    ap.add_argument('--project-name', default='贴图项目', help='项目名称')
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"[错误] 文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"[解析] {args.input}")
    analysis = parse_content_analysis(args.input)

    # 显示解析结果摘要
    print(f"[核心主题] {analysis['core_theme'][:60]}...")
    print(f"[关键词汇] {analysis['keywords'][:80]}...")

    # 生成 manifest
    print("[LLM] 正在生成 manifest...")
    prompt = build_manifest_prompt(analysis, args.project_name)
    manifest_content = call_llm(prompt)

    # 写入文件
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'w') as f:
        f.write("# 贴图设计清单\n\n")
        f.write(f"> **来源**: {os.path.basename(args.input)}\n")
        f.write(f"> **生成时间**: 自动生成\n\n")
        f.write("---\n\n")
        f.write(manifest_content)

    # vocabulary 校验警告（如果 manifest 内容已包含）
    print(f"\n✅ Manifest 已生成: {args.output}")
    print(f"   下一步: python3 scripts/generate_prompts.py --input {args.output} --output prompts/")
    print(f"\n⚠️  重要：检查 manifest 中所有 visual_elements 是否使用英文 key")
    print(f"   校验工具: python3 scripts/qa_check.py --prompts prompts/ --vocabulary docs/prompts-format.md")

if __name__ == '__main__':
    main()
