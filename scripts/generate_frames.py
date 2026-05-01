#!/usr/bin/env python3
"""
generate_frames.py - 微信贴图三段式生成器

优先级：AI → Remotion → PIL
每层失败自动降级，无需人工干预。

输出格式：
  - AI 模式：PNG
  - Remotion 模式：GIF（90帧动画）
  - PIL 模式：PNG

Usage:
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk --mode pil
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk --mode remotion

注意：
  - 输出扩展名自动根据模式决定（.gif 或 .png）
  - Remotion 模式需要 Node.js + npx remotion 环境
  - PIL 模式完全离线，字体支持受限（推荐安装 Noto Color Emoji）
"""

import os, sys, json, time, glob, subprocess, argparse, re
import urllib.request, urllib.error

# ── 常量 ───────────────────────────────────────────────────
W, H = 1080, 1440
FPS = 30
FRAMES_PER_STICKER = 90  # 每张贴图 90 帧 @ 30fps = 3 秒

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

# ── 辅助函数 ────────────────────────────────────────────────

FONT_CACHE = {}  # 缓存已加载的字体

def get_font(size=60):
    """加载支持 emoji 的字体，优先使用系统字体"""
    if size in FONT_CACHE:
        return FONT_CACHE[size]
    
    # 按优先级尝试各字体
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
            log(f"[字体] 加载成功: {path}", "INFO")
            return font
        except Exception:
            continue
    
    # 兜底：使用默认字体（无法渲染 emoji）
    font = ImageFont.load_default(size)
    log(f"[字体] 警告：未找到 emoji 字体，使用默认位图字体", "WARN")
    FONT_CACHE[size] = font
    return font

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

def _call_ai_provider(provider, prompt, timeout=60, max_retries=3):
    """
    统一 HTTP 调用逻辑：429 重试（10s 等待，最多3次）+ 超时降级 + 各 Provider 响应解析。
    返回 (image_data_or_url, is_b64) 或抛出异常。
    """
    url = provider["url"]
    headers = provider["headers"]()
    body = json.dumps(provider["body"]()).encode()

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            resp = urllib.request.urlopen(req, timeout=timeout)
            status = resp.status
            data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                err_body = json.loads(e.read())
            except Exception:
                err_body = {}
        except (urllib.error.URLError, TimeoutError) as e:
            # 超时或网络错误 → 抛出特定异常，触发降级
            raise RuntimeError(f"网络错误/超时: {e}")

        # 429 限流：等待后重试
        if status == 429:
            if attempt < max_retries - 1:
                wait_sec = 10 * (attempt + 1)
                log(f"[{provider['name']}] 429 限流，等待 {wait_sec}s 后重试（第 {attempt+1}/{max_retries} 次）", "WARN")
                import time; time.sleep(wait_sec)
                continue
            else:
                raise RuntimeError(f"429 限流，已重试 {max_retries} 次仍失败")

        # 401/403/402 等认证/付款错误 → 跳过该 provider
        if status in (401, 403, 402):
            raise RuntimeError(f"认证/付款错误 ({status})")

        # 其他 HTTP 错误
        if status >= 400:
            raise RuntimeError(f"HTTP {status}: {err_body}")

        # 正常：解析 image_url
        image_url = None
        if provider["name"] == "dashscope" and "data" in data:
            image_url = data["data"][0].get("url")
        elif provider["name"] == "seedream":
            # 火山引擎 Seedream 响应格式
            if "data" in data and data["data"]:
                image_url = data["data"][0].get("image_url") or data["data"][0].get("image_base64")
        elif "data" in data and len(data["data"]) > 0:
            image_url = data["data"][0].get("url") or data["data"][0].get("b64_json")

        if not image_url:
            raise RuntimeError(f"响应中无 image_url: {str(data)[:200]}")
        return image_url

    raise RuntimeError(f"重试耗尽")


def generate_ai_image(name, copy, style_keyword, theme_key, output_path):
    """
    调用 AI API 生成图像。
    按 Provider 优先级尝试，成功则保存到 output_path。
    失败则抛出异常，触发降级。
    支持 429 自动重试、超时降级、多 Provider 格式解析。
    """
    prompt = build_ai_prompt(name, copy, style_keyword, theme_key)

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
            "name": "seedream",
            "url": "https://visual.volcengineapi.com/?Action=TextToImage&Version=2023-05-01",
            "headers": lambda: {
                "Authorization": f"Bearer {os.environ.get('VOLCENGINE_API_KEY', os.environ.get('SEEDREAM_API_KEY',''))}",
                "Content-Type": "application/json",
            },
            "body": lambda: {
                "model": "doubao-seedream-5-0-260128",
                "prompt": prompt,
                "width": 1024,
                "height": 1360,   # 竖版 3:4（微信贴图标准）
                "num_images": 1,
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
                "height": 1360,   # 竖版 3:4
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
            image_url = _call_ai_provider(p, prompt)

            # 下载图片数据
            if image_url.startswith('data:'):
                import base64
                b64 = image_url.split(',')[1]
                img_data = base64.b64decode(b64)
            else:
                img_req = urllib.request.Request(image_url)
                with urllib.request.urlopen(img_req, timeout=30) as r:
                    img_data = r.read()

            from PIL import Image
            import io
            img = Image.open(io.BytesIO(img_data)).convert("RGBA")
            # 竖版 3:4 中心裁剪（API 可能返回方图或横图）
            img_w, img_h = img.size
            target_ratio = W / H  # 3:4 = 0.75
            current_ratio = img_w / img_h
            if current_ratio > target_ratio:
                # API 图比目标更宽：裁剪左右两侧
                new_w = int(img_h * target_ratio)
                offset_x = (img_w - new_w) // 2
                img = img.crop((offset_x, 0, offset_x + new_w, img_h))
            elif current_ratio < target_ratio:
                # API 图比目标更高：裁剪上下两侧
                new_h = int(img_w / target_ratio)
                offset_y = (img_h - new_h) // 2
                img = img.crop((0, offset_y, img_w, offset_y + new_h))
            img = img.resize((W, H), Image.LANCZOS)
            img.save(output_path, "PNG")

            log(f"[AI:{p['name']}] {name} 生成成功", "OK")
            return True

        except RuntimeError as e:
            err_msg = str(e)
            if "429" in err_msg or "限流" in err_msg:
                log(f"[AI:{p['name']}] {name} 限流: {err_msg}", "WARN")
            elif "超时" in err_msg or "网络错误" in err_msg:
                log(f"[AI:{p['name']}] {name} 超时/网络错误，降级: {err_msg}", "WARN")
            elif "认证" in err_msg or "付款" in err_msg or "402" in err_msg or "403" in err_msg:
                log(f"[AI:{p['name']}] {name} 认证/付款错误: {err_msg}", "WARN")
            else:
                log(f"[AI:{p['name']}] {name} 失败: {err_msg}", "WARN")
            continue
        except Exception as e:
            log(f"[AI:{p['name']}] {name} 异常: {e}", "ERROR")
            continue

    raise RuntimeError(f"所有 AI Provider 均失败: {name}")

# ── 阶段二：Remotion 帧导出 ────────────────────────────────

def check_remotion_available():
    """检查 npx remotion 是否可用"""
    try:
        r = subprocess.run(['npx', '--version'], capture_output=True, timeout=10)
        return r.returncode == 0
    except:
        return False

# 共享 Remotion 项目路径（模块级缓存，避免重复创建）
_remotion_project_cache = {}

def _get_or_create_remotion_project(project_dir, stickers, theme_key):
    """创建或返回已有的单一 Remotion 项目（含多 Sequence）"""
    if project_dir in _remotion_project_cache:
        return project_dir

    tmpl_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "remotion", "template")
    theme = THEMES.get(theme_key, THEMES["cyberpunk"])
    bg_color = theme["bg"]
    text_color = theme["text"]

    try:
        from _vocab import EMOJI_MAP
        emoji_map = EMOJI_MAP
    except ImportError:
        emoji_map = {
            "brain": "🧠", "ai大脑": "🧠", "ai计算": "🧠",
            "神经网络": "🧠", "neural_network": "🧠",
            "terminal": "💻", "终端窗口": "💻",
            "lightning": "⚡", "闪电": "⚡", "zap": "⚡",
            "equals_sign": "＝", "等号": "＝",
            "question_mark": "？", "问号": "？",
            "eraser": "🧹", "橡皮擦": "🧹",
            "checkmark": "✓", "对勾": "✓",
            "math_canvas": "📐", "canvas": "📐", "画布": "📐",
            "ai_chip": "🤖", "芯片": "🤖", "robot": "🤖",
            "spotlight": "🔦", "光晕": "🔦",
            "network_node": "🔗", "网络节点": "🔗", "link": "🔗",
            "button": "🔘", "按钮": "🔘",
            "code": "💻", "cpu": "🖥️", "server": "🗄️",
            "database": "🗃️", "cloud": "☁️", "data": "📊",
            "algorithm": "🔣", "function": "ƒ", "variable": "x",
            "debug": "🐛", "deploy": "🚀",
            "heart": "❤", "红心": "❤",
            "thumbs_up": "👍", "clap": "👏",
            "pray": "🙏", "muscle": "💪",
            "thinking": "🤔", "eyes": "👀",
            "trophy": "🏆", "medal": "🏅", "crown": "👑",
            "star": "⭐", "fire": "🔥", "hundred": "💯",
            "laugh": "😂", "cry": "😭", "angry": "😡",
            "cool": "😎", "shy": "😳", "sleeping": "😴",
            "rocket": "🚀", "alarm": "⏰", "bell": "🔔",
            "megaphone": "📢", "wrench": "🔧", "hammer": "🔨",
            "scissors": "✂️", "pencil": "✏️", "book": "📖",
            "lightbulb": "💡", "bulb": "💡",
            "envelope": "✉️", "gift": "🎁",
            "tada": "🎉", "balloon": "🎈", "confetti": "🎊",
            "coffee": "☕", "tea": "🍵", "beer": "🍺",
            "cocktail": "🍸", "wine": "🍷",
            "pizza": "🍕", "rice": "🍚", "fruit": "🍎",
            "cake": "🎂", "cookie": "🍪", "bread": "🍞",
            "phone": "📱", "camera": "📷", "clipboard": "📋",
            "chart": "📈", "calendar": "📅",
            "key": "🔑", "lock": "🔒",
            "folder": "📁", "file": "📄",
            "email": "📧", "call": "📞",
            "microphone": "🎤", "video": "🎬", "tv": "📺",
            "clock": "⏱️", "hourglass": "⏳",
            "pen": "🖊️", "ruler": "📏",
            "paperclip": "📎", "stamp": "📮",
            "inbox": "📥", "outbox": "📤",
            "earth": "🌏", "moon": "🌙", "sun": "☀️",
            "rainbow": "🌈", "snowflake": "❄️",
            "wave": "🌊", "anchor": "⚓",
            "airplane": "✈️", "car": "🚗", "bicycle": "🚲",
            "map": "🗺️", "compass": "🧭",
            "flag": "🚩", "satellite": "🛰️",
            "telescope": "🔭", "microscope": "🔬",
            "money": "💰", "gem": "💎",
            "love_letter": "💌",
            "warning": "⚠️", "no_entry": "⛔",
            "busy": "🉐", "free": "🆓", "secret": "***",
            "goal": "🎯", "puzzle": "🧩",
            "music": "🎵", "headphones": "🎧",
            "sound": "🔊", "mute": "🔇",
            "eye": "👁️", "ear": "👂", "nose": "👃",
            "footprints": "👣",
            "bone": "🦴", "microbe": "🦠",
            "pill": "💊", "syringe": "💉",
            "thermometer": "🌡️",
            "magnet": "🧲", "gear": "⚙️",
            "atom": "⚛️", "dna": "🧬",
            "biohazard": "☣️", "radioactive": "☢️",
            "bio": "🌱",
            "four_leaf": "🍀", "maple": "🍁",
            "cherry": "🌸", "tulip": "🌷",
            "rose": "🌹", "hibiscus": "🌺",
            "shell": "🐚", "feather": "🪶",
            "sparkle": "✨", "diamond": "💠",
            "fleur": "⚜️", "comet": "☄️",
        }

    sequences_jsx = ""
    for i, (name, copy, v_elems) in enumerate(stickers):
        emojis = [emoji_map[e] for e in v_elems if e in emoji_map]
        if not emojis: emojis = ["📝"]
        copy_escaped = copy.replace("'", "\\'").replace("`", "\\`").replace("$", "\\$").replace("{", "\\{").replace("}", "\\}")
        emoji_json = json.dumps(emojis, ensure_ascii=False)
        sequences_jsx += (
            "      <Sequence from={" + str(i) + " * 90} durationInFrames={90}>\n"
            "        <StickerScene copy={" + repr(copy_escaped) + "} emojis_str={" + repr(emoji_json) + "} frameOffset={" + str(i) + " * 90} />\n"
            "      </Sequence>\n"
        )
    try:
        with open(tmpl_base + "/StickerContent.tsx") as f:
            inner_code = f.read()
        with open(tmpl_base + "/StickerComponent.tsx") as f:
            outer_code = f.read()
        with open(tmpl_base + "/index.tsx") as f:
            entry_code = f.read()
    except FileNotFoundError:
        raise RuntimeError(f"模板文件不存在: {tmpl_base}")

    total_frames = len(stickers) * FRAMES_PER_STICKER

    inner_code = (inner_code
        .replace("__FPS__", str(FPS))
        .replace("__W__", str(W))
        .replace("__H__", str(H))
        .replace("__BG_COLOR__", bg_color)
        .replace("__TEXT_COLOR__", text_color)
        .replace("__PRIMARY__", theme['primary'])
        .replace("__SECONDARY__", theme['secondary'])
        .replace("__TOTAL_FRAMES__", str(total_frames))
        .replace("__SEQUENCES__", sequences_jsx)
    )
    outer_code = (outer_code
        .replace("__FPS__", str(FPS))
        .replace("__W__", str(W))
        .replace("__H__", str(H))
        .replace("__TOTAL_FRAMES__", str(total_frames))
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
        "name": "sticker-project",
        "version": "1.0.0",
        "dependencies": {"@remotion/cli": "4.0.448", "remotion": "4.0.448"}
    }
    with open(project_dir + "/package.json", "w") as f:
        json.dump(pkg, f, indent=2)

    # npm install
    subprocess.run(["npm", "install"], cwd=project_dir, capture_output=True, timeout=300)
    _remotion_project_cache[project_dir] = True
    return project_dir


def generate_remotion_gif(name, copy, visual_elements, theme_key, output_path, sticker_index, total_stickers, project_dir):
    """为单张贴图渲染指定帧范围的 GIF（复用同一 Remotion 项目）"""
    if not check_remotion_available():
        raise RuntimeError("npx remotion 不可用")

    theme = THEMES.get(theme_key, THEMES["cyberpunk"])

    # 输出强制使用 .gif 扩展名
    gif_path = os.path.splitext(output_path)[0] + ".gif"
    start_frame = sticker_index * FRAMES_PER_STICKER
    end_frame = start_frame + FRAMES_PER_STICKER - 1

    result = subprocess.run(
        ["npx", "remotion", "render",
         "src/index.tsx", "StickerComponent",
         "--output", gif_path,
         "--frames", f"{start_frame}-{end_frame}",
         "--fps", str(FPS)],
        cwd=project_dir, capture_output=True, timeout=600
    )
    if result.returncode == 0:
        # 验证 GIF 文件存在且非空（Remotion 有时会生成 0 字节文件）
        if os.path.exists(gif_path) and os.path.getsize(gif_path) > 1024:
            log("[Remotion] " + name + " GIF 导出成功", "OK")
            return True
        else:
            raise RuntimeError(f"GIF 文件无效或为空: {gif_path}")
    else:
        err = result.stderr.decode() if result.stderr else "未知错误"
        raise RuntimeError(err)


# ── 阶段三：PIL 兜底 ───────────────────────────────────────

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
        # 非 emoji 纯符号绘制（code/algorithm/function/variable/bio/secret）
        'code': lambda: (
            draw.rectangle([cx-300, cy-175, cx+300, cy+175], fill=(15,15,28,255), outline=primary+(200,), width=2),
            draw.text((cx-240, cy-100), ">>>", fill=(0,255,136,255), font=get_font(48)),
            draw.text((cx-240, cy-40), "def f(x):", fill=(0,200,255,255), font=get_font(40)),
            draw.text((cx-240, cy+20), "    return x", fill=(150,150,150,255), font=get_font(36)),
        ),
        'algorithm': lambda: (
            draw.rectangle([cx-260, cy-200, cx-60, cy-120], fill=primary+(60,), outline=primary+(200,), width=2),
            draw.rectangle([cx-60, cy-200, cx+140, cy-120], fill=secondary+(60,), outline=secondary+(200,), width=2),
            draw.rectangle([cx-160, cy-60, cx+40, cy+20], fill=primary+(60,), outline=primary+(200,), width=2),
            draw.text((cx-200, cy-170), "IN", fill=(255,255,255,255), font=get_font(32)),
            draw.text((cx-10, cy-170), "PROC", fill=(255,255,255,255), font=get_font(32)),
            draw.text((cx-120, cy-30), "OUT", fill=(255,255,255,255), font=get_font(32)),
        ),
        'function': lambda: draw.text((cx-200, cy-40), "ƒ(x) =", fill=primary+(255,), font=get_font(72)),
        'variable': lambda: (
            draw.text((cx-120, cy-40), "x =", fill=primary+(255,), font=get_font(72)),
            draw.text((cx+20, cy-30), "???", fill=secondary+(255,), font=get_font(56)),
        ),
        'bio': lambda: (
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

    try:
        from _vocab import EMOJI_MAP
        emoji_map = EMOJI_MAP
    except ImportError:
        emoji_map = {
            "brain": "🧠", "ai大脑": "🧠", "ai计算": "🧠",
            "神经网络": "🧠", "neural_network": "🧠",
            "terminal": "💻", "终端窗口": "💻",
            "lightning": "⚡", "闪电": "⚡",
            "equals_sign": "＝", "等号": "＝",
            "question_mark": "？", "问号": "？",
            "eraser": "🧹", "橡皮擦": "🧹",
            "checkmark": "✓", "对勾": "✓",
            "math_canvas": "📐", "canvas": "📐", "画布": "📐",
            "ai_chip": "🤖", "芯片": "🤖", "robot": "🤖",
            "spotlight": "🔦", "光晕": "🔦",
            "network_node": "🔗", "网络节点": "🔗", "link": "🔗",
            "button": "🔘", "按钮": "🔘",
            "cloud": "☁️", "data": "📊",
            "algorithm": "🔣", "function": "ƒ", "variable": "x",
            "debug": "🐛", "deploy": "🚀",
            "heart": "❤", "红心": "❤",
            "thumbs_up": "👍", "clap": "👏",
            "pray": "🙏", "muscle": "💪",
            "thinking": "🤔", "eyes": "👀",
            "trophy": "🏆", "medal": "🏅", "crown": "👑",
            "star": "⭐", "fire": "🔥", "hundred": "💯",
            "laugh": "😂", "cry": "😭", "angry": "😡",
            "cool": "😎", "shy": "😳", "sleeping": "😴",
            "rocket": "🚀", "alarm": "⏰", "bell": "🔔",
            "megaphone": "📢", "wrench": "🔧", "hammer": "🔨",
            "scissors": "✂️", "pencil": "✏️", "book": "📖",
            "lightbulb": "💡", "bulb": "💡",
            "envelope": "✉️", "gift": "🎁",
            "tada": "🎉", "balloon": "🎈", "confetti": "🎊",
            "coffee": "☕", "tea": "🍵", "beer": "🍺",
            "pizza": "🍕", "rice": "🍚", "fruit": "🍎",
            "cake": "🎂", "cookie": "🍪", "bread": "🍞",
            "phone": "📱", "camera": "📷", "clipboard": "📋",
            "chart": "📈", "calendar": "📅",
            "key": "🔑", "lock": "🔒",
            "folder": "📁", "file": "📄",
            "email": "📧", "call": "📞",
            "microphone": "🎤", "video": "🎬", "tv": "📺",
            "clock": "⏱️", "hourglass": "⏳",
            "pen": "🖊️", "ruler": "📏",
            "paperclip": "📎", "stamp": "📮",
            "inbox": "📥", "outbox": "📤",
            "earth": "🌏", "moon": "🌙", "sun": "☀️",
            "rainbow": "🌈", "snowflake": "❄️",
            "wave": "🌊", "anchor": "⚓",
            "airplane": "✈️", "car": "🚗", "bicycle": "🚲",
            "map": "🗺️", "compass": "🧭",
            "flag": "🚩", "satellite": "🛰️",
            "telescope": "🔭", "microscope": "🔬",
            "money": "💰", "gem": "💎",
            "love_letter": "💌",
            "warning": "⚠️", "no_entry": "⛔",
            "busy": "🉐", "free": "🆓", "secret": "***",
            "goal": "🎯", "puzzle": "🧩",
            "music": "🎵", "headphones": "🎧",
            "sound": "🔊", "mute": "🔇",
            "eye": "👁️", "ear": "👂", "nose": "👃",
            "footprints": "👣",
            "bone": "🦴", "microbe": "🦠",
            "pill": "💊", "syringe": "💉",
            "thermometer": "🌡️",
            "magnet": "🧲", "gear": "⚙️",
            "atom": "⚛️", "dna": "🧬",
            "biohazard": "☣️", "radioactive": "☢️",
            "bio": "🌱",
            "four_leaf": "🍀", "maple": "🍁",
            "cherry": "🌸", "tulip": "🌷",
            "rose": "🌹", "hibiscus": "🌺",
            "shell": "🐚", "feather": "🪶",
            "sparkle": "✨", "diamond": "💠",
            "fleur": "⚜️", "comet": "☄️",
            # 补充 _vocab.EMOJI_MAP 独有的 key（fallback 尽可能覆盖）
            "ai": "🤖", "robotic_arm": "🦾", "wifi": "📶",
            "server": "🗄️", "database": "🗃️", "virus": "🦠",
            "race_car": "🏎️", "helicopter": "🚁", "rocket_launch": "🚀",
            "boom": "💥", "zap": "⚡", "impact": "💫",
            "vs": "⚔️", "versus": "⚔️",
            "female": "♀️", "male": "♂️",
            "transgender": "🏳️‍🌈", "nonbinary": "🏳️‍🌈",
            "heart_exclamation": "❣️", "growing_heart": "💗",
            "revolving_heart": "💞", "two_hearts": "💕",
            "broken_heart": "💔", "heart_onFire": "❤️‍🔥",
            "melt": "🫠", "absolutely": "💯",
            "100": "💯", "sparkler": "✨",
            "tiger": "🐯", "rabbit": "🐰", "dragon": "🐲",
            "fox": "🦊", "unicorn": "🦄", "mermaid": "🧜‍♀️",
            "merman": "🧜", "fairy": "🧚", "elf": "🧝",
            "mage": "🧙", "angel": "👼", "devil": "😈",
            "ghost": "👻", "skull": "💀", "fog": "🌫️",
            "snow": "❄️", "cloudy": "☁️", "partly_cloudy": "⛅",
            "sunny": "☀️", "new_moon": "🌑", "full_moon": "🌕",
            "zodiac": "♈", "shooting_star": "🌠",
            "milky_way": "🌌", "cloud_lightning": "🌩️",
            "cloud_rain": "🌧️", "rainy": "🌧️",
            "sun_flower": "🌻", "herb": "🌿", "palm_tree": "🌴",
            "cactus": "🌵", "clover": "🍀", "fallen_leaf": "🍂",
            "leaf_fluttering": "🍃", "leaf": "🍁",
        }

    tmpl_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "remotion", "template")
    theme = THEMES.get(theme_key, THEMES["cyberpunk"])
    bg_color = theme["bg"]
    text_color = theme["text"]

    for elem in visual_elements:
        fn = elem_fns.get(elem)
        if fn:
            fn()

    # 未匹配 elem_fns 的 key 横向排列为 emoji（最多 4 个，均匀分布）
    emoji_elements = [e for e in visual_elements if e not in elem_fns]
    if emoji_elements:
        max_emoji = 4
        shown = emoji_elements[:max_emoji]
        total_w = len(shown) * 120
        start_x = cx - total_w // 2
        for i, elem in enumerate(shown):
            emoji = emoji_map.get(elem, elem)
            ex = start_x + i * 120
            draw.text((ex, cy - 80), emoji, fill=(255, 255, 255, 255), font=get_font(80))

    font = get_font(60)
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

    # 预解析所有贴图数据
    all_stickers = []
    for pf in files:
        name, copy, v_elems, s_kw, theme = parse_prompt_file(pf)
        all_stickers.append((name, copy, v_elems, s_kw, theme))

    # 建立单一 Remotion 项目（模块级缓存）
    # 从 input 路径推导项目根目录（prompts/ 的父级）
    input_abs = os.path.abspath(args.input)
    project_root = os.path.dirname(input_abs) if os.path.basename(input_abs) == 'prompts' else input_abs
    project_dir = os.path.join(project_root, "remotion-sticker")
    stickers_for_remotion = [(n, c, v) for n, c, v, _, _ in all_stickers]

    remotion_project_ready = False
    remotion_used = False  # 标记本次是否使用了 Remotion（决定输出格式）
    if args.mode in ('auto', 'remotion') and check_remotion_available():
        try:
            _get_or_create_remotion_project(project_dir, stickers_for_remotion, args.theme)
            remotion_project_ready = True
            log("Remotion 项目已建立（单项目多 Sequence）", "OK")
        except Exception as e:
            log(f"Remotion 项目创建失败: {e}", "WARN")
            remotion_project_ready = False

    ok = 0
    for idx, (pf, sticker_data) in enumerate(zip(files, all_stickers)):
        name, copy, v_elems, s_kw, theme = sticker_data
        # 输出扩展名根据实际生成模式决定：Remotion 用 .gif，AI/PIL 用 .png
        ext = '.gif' if remotion_project_ready else '.png'
        out = os.path.join(args.output, os.path.basename(pf).replace('.md', ext))

        mode = args.mode
        success = False
        generated_ext = '.png'  # 默认 PNG

        # 阶段一：AI
        if mode in ('auto', 'ai'):
            try:
                generate_ai_image(name, copy, s_kw, theme, out)
                success = True
                generated_ext = '.png'
            except Exception as e:
                log(f"[AI] {name} 失败，降级: {e}", "WARN")
                if mode == 'ai': continue

        # 阶段二：Remotion（复用单一项目）
        if not success and mode in ('auto', 'remotion') and remotion_project_ready:
            try:
                generate_remotion_gif(name, copy, v_elems, theme, out, idx, len(all_stickers), project_dir)
                success = True
                generated_ext = '.gif'
                remotion_used = True
            except Exception as e:
                log(f"[Remotion] {name} 失败，降级: {e}", "WARN")
                if mode == 'remotion': continue

        # 阶段三：PIL
        if not success:
            try:
                pil_fallback(name, copy, v_elems, theme, out)
                success = True
                generated_ext = '.png'
            except Exception as e:
                log(f"[PIL] {name} 失败: {e}", "ERROR")

        if success:
            ok += 1
            print(f"✓ {name} ({generated_ext})")
        else:
            print(f"✗ {name}")

    print(f"\n✅ {ok}/{len(files)} 张贴图生成完成")
    print(f"📦 {args.output}")
    if remotion_used:
        print(f"🔧 Remotion 项目（保留用于后续调整）: {project_dir}")

if __name__ == '__main__':
    main()