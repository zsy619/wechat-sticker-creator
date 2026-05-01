#!/usr/bin/env python3
"""
pil_fallback.py - PIL 本地兜底生成器

纯离线运行，无需网络。读取 prompts/ 目录，生成 PNG 贴图。

Usage:
    python3 scripts/pil_fallback.py --input prompts/ --output assets-pil/ --theme cyberpunk
"""

import os, sys, glob, argparse

# ── 常量 ───────────────────────────────────────────────────
W, H = 1080, 1440

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

# ── 字体 ───────────────────────────────────────────────────

FONT_CACHE = {}

def get_font(size=60):
    """加载支持 emoji 的字体，优先使用系统字体"""
    if size in FONT_CACHE:
        return FONT_CACHE[size]

    font_paths = [
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        # Linux
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        # Windows
        "C:/Windows/Fonts/seguiemj.ttf",
    ]

    from PIL import ImageFont
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, size)
            FONT_CACHE[size] = font
            print(f"[字体] 加载成功: {path}")
            return font
        except Exception:
            continue

    font = ImageFont.load_default(size)
    print(f"[字体] 警告：未找到 emoji 字体，使用默认位图字体")
    FONT_CACHE[size] = font
    return font

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")

# ── 解析 ───────────────────────────────────────────────────

def _parse_list(s):
    """Parse a simple unquoted comma-separated list: [a, b, c]"""
    s = s.strip()
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1]
    return [x.strip() for x in s.split(',') if x.strip()]

def parse_prompt_file(path):
    """解析 prompts/*.md，返回 (name, copy, visual_elements, style_keyword, theme)"""
    with open(path) as f:
        content = f.read()
    front = {}
    in_front = False
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped == '---':
            if not in_front: in_front = True
            else: break
            continue
        if in_front and ':' in line:
            k, v = line.split(':', 1)
            front[k.strip()] = v.strip().strip('"').strip("'")
    name    = front.get('name', os.path.basename(path).replace('.md',''))
    copy    = front.get('copy', '')
    try:    visual_elements = _parse_list(front.get('visual_elements', '[]'))
    except: visual_elements = []
    try:    style_keyword = _parse_list(front.get('style_keyword', '[]'))
    except: style_keyword = []
    theme   = front.get('theme', 'cyberpunk')
    return name, copy, visual_elements, style_keyword, theme

# ── 核心生成 ───────────────────────────────────────────────

def pil_fallback(name, copy, visual_elements, theme_key, output_path):
    """PIL 本地生成（兜底方案）"""
    from PIL import Image, ImageDraw, ImageFont

    theme = THEMES.get(theme_key, THEMES['cyberpunk'])
    primary = hex_to_rgb(theme['primary'])
    secondary = hex_to_rgb(theme['secondary'])

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bg_rgb = hex_to_rgb(theme['bg'])
    draw.rectangle([0, 0, W, H], fill=bg_rgb + (255,))

    cx, cy = W // 2, H // 2 - 60

    # elem_fns：程序化绘制函数（非 emoji 纯符号元素）
    # emoji 元素（coffee, rocket 等）统一通过 get_font() 渲染
    elem_fns = {
        # FOCUS 元素（几何绘制）
        'brain': lambda: draw.ellipse([cx-150, cy-150, cx+150, cy+150], fill=primary + (80,)),
        'neural_network': lambda: (
            [draw.ellipse([cx-200+nx*80, cy-100+ny*60, cx-200+nx*80+24, cy-100+ny*60+24],
              fill=primary+(180,) if (nx+ny)%2==0 else secondary+(180,))
             for nx in range(6) for ny in range(4)]
        ),
        'terminal': lambda: draw.rectangle([cx-300, cy-175, cx+300, cy+175], fill=(15,15,28,255), outline=primary+(200,), width=2),
        'math_canvas': lambda: draw.rectangle([cx-380, cy-250, cx+380, cy+250], fill=(10,10,10,255)),
        'ai_chip': lambda: draw.rectangle([cx-120, cy-120, cx+120, cy+120], fill=primary+(60,), outline=primary+(200,), width=3),
        'spotlight': lambda: (
            draw.ellipse([cx-200, cy-250, cx+200, cy+250], fill=(255,255,200,25)),
            draw.ellipse([cx-100, cy-150, cx+100, cy+150], fill=(255,255,200,40)),
        ),
        'network_node': lambda: (
            [draw.ellipse([cx-180+nx*90, cy-90+ny*70, cx-180+nx*90+20, cy-90+ny*70+20],
              fill=primary+(200,))
             for nx in range(5) for ny in range(3)]
        ),
        'button': lambda: draw.rectangle([cx-150, cy-60, cx+150, cy+60], fill=primary+(200,), outline=primary+(255,), width=3),
        # 符号元素（通过 Unicode/emoji 渲染）
        'lightning': lambda: draw.text((cx-50, cy-80), "⚡", fill=(255,255,255,255), font=get_font(80)),
        'heart': lambda: draw.text((cx-60, cy-60), "❤", fill=(255,60,90,255), font=get_font(80)),
        'equals_sign': lambda: draw.text((cx-50, cy-50), "=", fill=(255,255,255,255), font=get_font(80)),
        'question_mark': lambda: draw.text((cx-30, cy-40), "?", fill=primary+(255,), font=get_font(80)),
        'eraser': lambda: draw.text((cx-40, cy-40), "🧹", fill=(200,150,100,255), font=get_font(60)),
        'checkmark': lambda: draw.text((cx-40, cy-40), "✓", fill=(0,255,136,255), font=get_font(80)),
        # 非 emoji 纯符号绘制
        'code': lambda: (
            draw.rectangle([cx-300, cy-175, cx+300, cy+175], fill=(15,15,28,255), outline=primary+(200,), width=2),
            draw.text((cx-240, cy-100), ">>>", fill=(0,255,136,255), font=get_font(48)),
            draw.text((cx-240, cy-40), "def f(x):", fill=(0,200,255,255), font=get_font(40)),
            draw.text((cx-240, cy+20), "    return x", fill=(150,150,150,255), font=get_font(36)),
        ),
        'algorithm': lambda: (
            # 流程图样式
            draw.rectangle([cx-260, cy-200, cx-60, cy-120], fill=primary+(60,), outline=primary+(200,), width=2),
            draw.rectangle([cx-60, cy-200, cx+140, cy-120], fill=secondary+(60,), outline=secondary+(200,), width=2),
            draw.rectangle([cx-160, cy-60, cx+40, cy+20], fill=primary+(60,), outline=primary+(200,), width=2),
            draw.text((cx-200, cy-170), "IN", fill=(255,255,255,255), font=get_font(32)),
            draw.text((cx-10, cy-170), "PROC", fill=(255,255,255,255), font=get_font(32)),
            draw.text((cx-120, cy-30), "OUT", fill=(255,255,255,255), font=get_font(32)),
        ),
        'function': lambda: (
            draw.text((cx-200, cy-40), "ƒ(x) =", fill=primary+(255,), font=get_font(72)),
        ),
        'variable': lambda: (
            draw.text((cx-120, cy-40), "x =", fill=primary+(255,), font=get_font(72)),
            draw.text((cx+20, cy-30), "???", fill=secondary+(255,), font=get_font(56)),
        ),
        'bio': lambda: (
            # DNA 双螺旋示意
            [(
                draw.ellipse([cx-160+ny*40-8, cy-120+ny*30-8, cx-160+ny*40+8, cy-120+ny*30+8], fill=primary+(180,)),
                draw.ellipse([cx+160-ny*40-8, cy-120+ny*30-8, cx+160-ny*40+8, cy-120+ny*30+8], fill=secondary+(180,)),
                draw.line([cx-160+ny*40, cy-120+ny*30, cx+160-ny*40, cy-120+ny*30], fill=primary+(80,), width=2),
            ) for ny in range(9)],
        ),
        'secret': lambda: (
            draw.text((cx-140, cy-50), "***", fill=(255,215,0,255), font=get_font(80)),
            draw.text((cx-200, cy+50), "CLASSIFIED", fill=(255,100,100,255), font=get_font(28)),
        ),
    }

    # 渲染所有 visual_elements：先尝试 elem_fns 绘图，未匹配的做 emoji 兜底
    emoji_elements = []
    for elem in visual_elements:
        fn = elem_fns.get(elem)
        if fn:
            fn()
        else:
            emoji_elements.append(elem)
    # 未匹配 elem_fns 的 key 横向排列为 emoji（最多4个）
    if emoji_elements:
        emoji_fonts = {
            "ai大脑": "🧠", "ai计算": "🧠", "神经网络": "🧠",
            "终端窗口": "💻", "芯片": "🤖",
            "闪电": "⚡", "网络节点": "🔗", "按钮": "🔘",
            "画布": "📐", "光晕": "🔦",
            "机器人": "🤖", "ai芯片": "🤖",
        }
        max_emoji = 4
        shown = emoji_elements[:max_emoji]
        total_w = len(shown) * 120
        start_x = cx - total_w // 2
        for i, elem in enumerate(shown):
            emoji = emoji_fonts.get(elem, elem)
            ex = start_x + i * 120
            draw.text((ex, cy - 80), emoji, fill=(255, 255, 255, 255), font=get_font(80))

    # 渲染底部文案
    font = get_font(60)
    tw = sum(font.getbbox(c)[2] for c in copy)
    th = int(60 * 1.4)
    tx = (W - tw) // 2
    ty = H - th - 30
    draw.text((tx, ty), copy, fill=hex_to_rgb(theme['text']) + (255,), font=font)

    img.save(output_path, "PNG")
    log(f"[PIL] {name} 生成成功", "OK")
    return True


# ── 主入口 ───────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='PIL 本地兜底生成器（纯离线）')
    ap.add_argument('--input',  required=True, help='prompts/ 目录路径')
    ap.add_argument('--output', required=True, help='输出目录路径')
    ap.add_argument('--theme',  default='cyberpunk', help='主题风格')
    args = ap.parse_args()

    input_path = args.input
    if os.path.isfile(input_path):
        files = [input_path]
    elif os.path.isdir(input_path):
        files = sorted(glob.glob(f"{input_path}/*.md"))
        if not files:
            log(f"未找到 .md 文件: {input_path}", "ERROR")
            return
    else:
        log(f"输入路径不存在: {input_path}", "ERROR")
        return

    os.makedirs(args.output, exist_ok=True)
    log(f"主题: {args.theme} | 文件数: {len(files)}")

    ok = 0
    for pf in files:
        name, copy, v_elems, s_kw, theme = parse_prompt_file(pf)
        out = os.path.join(args.output, os.path.basename(pf).replace('.md', '.png'))

        try:
            pil_fallback(name, copy, v_elems, args.theme, out)
            ok += 1
            print(f"✓ {name}")
        except Exception as e:
            log(f"[PIL] {name} 失败: {e}", "ERROR")
            print(f"✗ {name}")

    print(f"\n✅ {ok}/{len(files)} 张贴图生成完成")
    print(f"📦 {args.output}")


if __name__ == '__main__':
    main()
