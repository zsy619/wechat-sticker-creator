#!/usr/bin/env python3
"""
generate_frames.py - 微信贴图三段式生成器

优先级：AI → Remotion → PIL
每层失败自动降级，无需人工干预。

Usage:
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk --mode pil
"""

import os, sys, json, time, glob, subprocess, argparse
import urllib.request, urllib.error

# ── 常量 ───────────────────────────────────────────────────
W, H = 1080, 1440
THEMES = {
    "cyberpunk":  {"primary": "#00FFFF", "secondary": "#FF00FF", "bg": "#0D0D1A", "text": "#FFFFFF", "accent": "#00FF88"},
    "kawaii":     {"primary": "#FF69B4", "secondary": "#FFB6C1", "bg": "#FFF0F5", "text": "#4A4A4A", "accent": "#FF1493"},
    "neon":       {"primary": "#FF00FF", "secondary": "#00FFFF", "bg": "#1A0033", "text": "#FFFFFF", "accent": "#FF69B4"},
    "retro":      {"primary": "#FFD700", "secondary": "#FF6B35", "bg": "#2D1B00", "text": "#FFFFFF", "accent": "#FF4500"},
    "hand-drawn": {"primary": "#8B4513", "secondary": "#D2691E", "bg": "#FFF8DC", "text": "#4A4A4A", "accent": "#CD853F"},
    "minimal":    {"primary": "#212529", "secondary": "#495057", "bg": "#F8F9FA", "text": "#212529", "accent": "#6C757D"},
    "meme":       {"primary": "#FF4500", "secondary": "#FFD700", "bg": "#1A1A1A", "text": "#FFFFFF", "accent": "#FF6347"},
}

# ── 辅助函数 ────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")

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

# ── 阶段一：AI 生成 ────────────────────────────────────────

def build_ai_prompt(name, copy, style_keyword, theme_key):
    """构建 AI 图像生成提示词"""
    theme = THEMES.get(theme_key, THEMES['cyberpunk'])
    style_str = ', '.join(style_keyword) if style_keyword else 'cyberpunk'
    return (
        f"微信贴图，1080x1440px，3:4竖版，"
        f"文字: {copy}，"
        f"风格: {style_str}，"
        f"主色: {theme['primary']}，背景色: {theme['bg']}，"
        f"高质量，精致细节"
    )

def generate_ai_image(name, copy, style_keyword, theme_key, output_path):
    """
    调用 AI API 生成图像。
    按 Provider 优先级尝试，成功则保存到 output_path。
    失败则抛出异常，触发降级。
    """
    prompt = build_ai_prompt(name, copy, style_keyword, theme_key)

    # Provider 配置
    providers = [
        {
            "name": "dashscope",
            "url": "https://api.dashscope.com/v1/images/generations",
            "headers": lambda: {"Authorization": f"Bearer {os.environ.get('DASHSCOPE_API_KEY','')}",
                                "Content-Type": "application/json"},
            "body": lambda: {
                "model": "qwen-image-2.0-pro",
                "prompt": prompt,
                "size": "1024x1024",
                "n": 1,
            },
        },
        {
            "name": "minimax",
            "url": "https://api.minimax.chat/v1/image_generation",
            "headers": lambda: {"Authorization": f"Bearer {os.environ.get('MINIMAX_API_KEY','')}",
                                "Content-Type": "application/json"},
            "body": lambda: {
                "model": "image-01",
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
            },
        },
        {
            "name": "openai",
            "url": "https://api.openai.com/v1/images/generations",
            "headers": lambda: {"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY','')}",
                                "Content-Type": "application/json"},
            "body": lambda: {
                "model": "dall-e-3",
                "prompt": prompt,
                "size": "1024x1024",
                "n": 1,
            },
        },
    ]

    for p in providers:
        try:
            body = p["body"]()
            req = urllib.request.Request(
                p["url"],
                data=json.dumps(body).encode(),
                headers=p["headers"](),
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())

            # 解析返回的图片 URL
            image_url = None
            if p["name"] == "dashscope" and "data" in data:
                image_url = data["data"][0]["url"]
            elif "data" in data and len(data["data"]) > 0:
                image_url = data["data"][0].get("url") or data["data"][0].get("b64_json")

            if not image_url:
                continue

            # 下载并保存
            if image_url.startswith('data:'):
                # base64
                import base64
                b64 = image_url.split(',')[1]
                img_data = base64.b64decode(b64)
            else:
                img_req = urllib.request.Request(image_url)
                with urllib.request.urlopen(img_req, timeout=30) as r:
                    img_data = r.read()

            # 缩放到 1080×1440
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(img_data)).convert("RGBA")
            img = img.resize((W, H), Image.LANCZOS)
            img.save(output_path, "PNG")

            log(f"[AI:{p['name']}] {name} 生成成功", "OK")
            return True

        except (urllib.error.HTTPError, urllib.error.URLError,
                KeyError, IndexError, IOError) as e:
            log(f"[AI:{p['name']}] {name} 失败: {e}", "WARN")
            continue
        except Exception as e:
            log(f"[AI:{p['name']}] {name} 异常: {e}", "ERROR")
            continue

    # 所有 provider 都失败
    raise RuntimeError(f"所有 AI Provider 均失败: {name}")

# ── 阶段二：Remotion 帧导出 ────────────────────────────────

# check_remotion_available kept for compatibility
def check_remotion_available():
    """检查 npx remotion 是否可用"""
    try:
        r = subprocess.run(['npx', '--version'], capture_output=True, timeout=10)
        return r.returncode == 0
    except:
        return False

def generate_remotion_gif(name, copy, visual_elements, theme_key, output_path):
    """为单张贴图创建 Remotion 项目并导出 PNG。"""
    if not check_remotion_available():
        raise RuntimeError("npx remotion 不可用")

    # 读取模板文件
    tmpl_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "remotion", "template")

    # Remotion 项目放在当前项目目录下（非 /tmp）
    project_dir = os.path.join(os.path.dirname(os.path.abspath(output_path)), ".remotion-sticker-" + name.replace(" ", "-"))
    os.makedirs(project_dir + "/src", exist_ok=True)

    theme = THEMES.get(theme_key, THEMES["cyberpunk"])
    bg_color = theme["bg"]
    text_color = theme["text"]
    FPS = 30

    emoji_map = {
        "brain": "🧠", "ai大脑": "🧠", "ai计算": "🧠",
        "神经网络": "🧠", "neural_network": "🧠",
        "terminal": "💻", "终端窗口": "💻",
        "lightning": "⚡", "闪电": "⚡",
        "heart": "❤", "红心": "❤",
        "equals_sign": "＝", "等号": "＝",
        "question_mark": "？", "问号": "？",
        "eraser": "🧹", "橡皮擦": "🧹",
        "checkmark": "✓", "对勾": "✓",
        "math_canvas": "📐", "canvas": "📐", "画布": "📐",
        "ai_chip": "🤖", "芯片": "🤖",
    }

    # 构建 emoji 视觉元素（居中大号展示）
    emojis = [emoji_map.get(e, "") for e in visual_elements if emoji_map.get(e)]
    if not emojis:
        emojis = ["📝"]

    div_style = "{{display:'flex',gap:40,alignItems:'center',justifyContent:'center'}}"  
    span_base = "{{fontSize:260,lineHeight:1,filter:`drop-shadow(0 0 " + theme["primary"] + ") drop-shadow(0 0 80px " + theme["secondary"] + "80)`}}"  
    emojis_html = "        <div style=" + div_style + ">\n"
    for em in emojis:
        emojis_html += "          <span style=" + span_base + ">" + em + "</span>\n"
    emojis_html += "        </div>\n"

    # 读取模板文件
    try:
        with open(tmpl_base + "/StickerContent.tsx") as f:
            inner_code = f.read()
        with open(tmpl_base + "/StickerComponent.tsx") as f:
            outer_code = f.read()
        with open(tmpl_base + "/index.tsx") as f:
            entry_code = f.read()
    except FileNotFoundError:
        raise RuntimeError(f"模板文件不存在: {tmpl_base}")

    # 注入主题色和文案
    inner_code = (inner_code
        .replace("__BG_COLOR__", bg_color)
        .replace("__TEXT_COLOR__", text_color)
        .replace("__COPY__", copy)
        .replace("__PRIMARY__", theme['primary'])
        .replace("__SECONDARY__", theme['secondary'])
        .replace("__ELEMENTS_HTML__", emojis_html)
        .replace("__FPS__", str(FPS))
        .replace("__W__", str(W))
        .replace("__H__", str(H))
    )
    outer_code = (outer_code
        .replace("__FPS__", str(FPS))
        .replace("__W__", str(W))
        .replace("__H__", str(H))
    )

    css_content = "body { margin: 0; background: " + bg_color + "; }\n"
    with open(project_dir + "/src/StickerContent.tsx", "w") as f:
        f.write(inner_code)
    with open(project_dir + "/src/StickerComponent.tsx", "w") as f:
        f.write(outer_code)
    with open(project_dir + "/src/index.tsx", "w") as f:
        f.write(entry_code)
    with open(project_dir + "/src/styles.css", "w") as f:
        f.write(css_content)
    pkg = {
        "name": "sticker-" + name,
        "version": "1.0.0",
        "dependencies": {"@remotion/cli": "4.0.448", "remotion": "4.0.448"}
    }
    with open(project_dir + "/package.json", "w") as f:
        json.dump(pkg, f, indent=2)

    try:
        subprocess.run(["npm", "install"], cwd=project_dir, capture_output=True, timeout=300)
        # 输出路径改为 GIF
        gif_path = output_path.replace(".png", ".gif")
        result = subprocess.run(
            ["npx", "remotion", "render",
             "src/index.tsx", "StickerComponent",
             "--output", gif_path,
             "--frames", "0-89",
             "--fps", str(FPS)],
            cwd=project_dir, capture_output=True, timeout=600
        )
        if result.returncode == 0 and os.path.exists(gif_path):
            log("[Remotion] " + name + " GIF 导出成功", "OK")
            return True
        else:
            err = result.stderr.decode() if result.stderr else "未知错误"
            raise RuntimeError(err)
    except subprocess.TimeoutExpired:
        raise RuntimeError("Remotion 导出超时")
    except FileNotFoundError:
        raise RuntimeError("Node.js 或 npm 不可用")
    raise RuntimeError("Remotion 导出失败: " + name)


# ── 阶段三：PIL 兜底 ───────────────────────────────────────

def pil_fallback(name, copy, visual_elements, theme_key, output_path):
    """PIL 本地生成（兜底方案）"""
    from PIL import Image, ImageDraw, ImageFont

    theme = THEMES.get(theme_key, THEMES['cyberpunk'])
    primary = hex_to_rgb(theme['primary'])
    secondary = hex_to_rgb(theme['secondary'])

    # 创建画布
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 背景
    bg_rgb = hex_to_rgb(theme['bg'])
    draw.rectangle([0, 0, W, H], fill=bg_rgb + (255,))

    # 简单视觉元素（词汇表函数简化版）
    cx, cy = W // 2, H // 2 - 60
    elem_fns = {
        'brain': lambda: draw.ellipse([cx-150, cy-150, cx+150, cy+150],
                                       fill=primary + (80,)),
        'neural_network': lambda: [
            draw.ellipse([cx-180+dx*100, cy-60+dy*80, cx-180+dx*100+14, cy-60+dy*80+14],
                          fill=secondary + (200,))
            for dx in [-1,0,1] for dy in [-1,0,1] if not(dx==0 and dy==0)
        ] if False else None,
        'terminal': lambda: draw.rectangle([cx-300, cy-175, cx+300, cy+175],
                                            fill=(15,15,28,255), outline=primary+(200,), width=2),
        'lightning': lambda: draw.text((cx-50, cy-80), "⚡",
                                        fill=(255,255,255,255), font=ImageFont.load_default(80)),
        'heart': lambda: draw.text((cx-60, cy-60), "❤",
                                    fill=(255,60,90,255), font=ImageFont.load_default(80)),
        'equals_sign': lambda: draw.text((cx-50, cy-50), "=",
                                          fill=(255,255,255,255), font=ImageFont.load_default(80)),
        'question_mark': lambda: draw.text((cx-30, cy-40), "?",
                                            fill=primary+(255,), font=ImageFont.load_default(80)),
        'eraser': lambda: draw.text((cx-40, cy-40), "🧹",
                                     fill=(200,150,100,255), font=ImageFont.load_default(60)),
        'checkmark': lambda: draw.text((cx-40, cy-40), "✓",
                                       fill=(0,255,136,255), font=ImageFont.load_default(80)),
        'math_canvas': lambda: draw.rectangle([cx-380, cy-250, cx+380, cy+250],
                                               fill=(10,10,10,255)),
    }

    for elem in visual_elements:
        fn = elem_fns.get(elem)
        if fn: fn()

    # 底部文字
    font = ImageFont.load_default(60)
    tw = sum(font.getbbox(c)[2] for c in copy)
    th = int(60 * 1.4)
    tx = (W - tw) // 2
    ty = H - th - 30
    draw.text((tx, ty), copy, fill=hex_to_rgb(theme['text']) + (255,), font=font)

    img.save(output_path, "PNG")
    log(f"[PIL] {name} 生成成功", "OK")
    return True

# ── 主入口 ────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='微信贴图三段式生成器')
    ap.add_argument('--input',  required=True, help='prompts/ 目录路径')
    ap.add_argument('--output', required=True, help='输出目录路径')
    ap.add_argument('--theme',  default='cyberpunk', help='主题风格')
    ap.add_argument('--mode',   choices=['auto', 'ai', 'remotion', 'pil'], default='auto',
                   help='强制使用指定模式（auto=自动降级）')
    args = ap.parse_args()

    os.makedirs(args.output, exist_ok=True)
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
    log(f"主题: {args.theme} | 模式: {args.mode} | 文件数: {len(files)}")

    ok = 0
    for pf in files:
        name, copy, v_elems, s_kw, theme = parse_prompt_file(pf)
        out = os.path.join(args.output, os.path.basename(pf).replace('.md', '.png'))

        mode = args.mode
        success = False

        # 阶段一：AI
        if mode in ('auto', 'ai'):
            try:
                generate_ai_image(name, copy, s_kw, theme, out)
                success = True
            except Exception as e:
                log(f"[AI] {name} 失败，降级: {e}", "WARN")
                if mode == 'ai':
                    continue  # 强制AI模式不降级

        # 阶段二：Remotion
        if not success and mode in ('auto', 'remotion'):
            try:
                generate_remotion_gif(name, copy, v_elems, theme, out)
                success = True
            except Exception as e:
                log(f"[Remotion] {name} 失败，降级: {e}", "WARN")
                if mode == 'remotion':
                    continue

        # 阶段三：PIL
        if not success:
            try:
                pil_fallback(name, copy, v_elems, theme, out)
                success = True
            except Exception as e:
                log(f"[PIL] {name} 失败: {e}", "ERROR")

        if success:
            ok += 1
            print(f"✓ {name}")
        else:
            print(f"✗ {name}")

    print(f"\n✅ {ok}/{len(files)} 张贴图生成完成")
    print(f"📦 {args.output}")

if __name__ == '__main__':
    main()
