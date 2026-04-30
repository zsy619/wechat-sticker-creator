#!/usr/bin/env python3
"""
generate_stickers.py - 微信表情包 PIL 生成器
支持多种风格主题，默认使用赛博朋克风格

Bug修复记录 (2026-04-30):
- STICKER_SIZE 500→1080×1440 (微信贴图标准3:4)
- parse_prompt_file 返回3值，解包从2→3
- 字体大小按1080×1440比例调整
"""
import os
import sys
import math
import glob
from PIL import Image, ImageDraw, ImageFont

# 系统字体路径（macOS）
FONT_PATHS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
]

# 微信贴图标准尺寸 1080×1440 (3:4竖版)
W, H = 1080, 1440

# 风格主题配色方案
THEMES = {
    "cyberpunk": {
        "name": "赛博朋克",
        "bg_top": "#0D0D1A",
        "bg_bot": "#1A0A2E",
        "primary": "#00FFFF",
        "secondary": "#FF00FF",
        "accent": "#00FF88",
        "grid": "#1A1A3A",
        "glow": "#FF00FF",
        "text": "#FFFFFF",
    },
    "kawaii": {
        "name": "可爱",
        "bg_top": "#FFE4EC",
        "bg_bot": "#FFC0CB",
        "primary": "#FF69B4",
        "secondary": "#FFB6C1",
        "accent": "#FF1493",
        "text": "#4A4A4A",
    },
    "minimal": {
        "name": "简约",
        "bg_top": "#FFFFFF",
        "bg_bot": "#F8F9FA",
        "primary": "#212529",
        "secondary": "#6C757D",
        "accent": "#0D6EFD",
        "text": "#212529",
    },
    "meme": {
        "name": "表情包",
        "bg_top": "#FFE135",
        "bg_bot": "#FFA500",
        "primary": "#FF4500",
        "secondary": "#FF6347",
        "accent": "#DC143C",
        "text": "#000000",
    },
    "hand-drawn": {
        "name": "手绘",
        "bg_top": "#FFF8DC",
        "bg_bot": "#FAEBD7",
        "primary": "#8B4513",
        "secondary": "#A0522D",
        "accent": "#D2691E",
        "text": "#2F2F2F",
    },
    "retro": {
        "name": "复古像素",
        "bg_top": "#8B0000",
        "bg_bot": "#4A0E0E",
        "primary": "#FFD700",
        "secondary": "#FF8C00",
        "accent": "#00FF00",
        "text": "#FFFFFF",
    },
    "neon": {
        "name": "霓虹灯",
        "bg_top": "#0A0A0A",
        "bg_bot": "#1A1A1A",
        "primary": "#FF00FF",
        "secondary": "#00FFFF",
        "accent": "#FF6600",
        "glow": "#FF00FF",
        "text": "#FFFFFF",
    },
}


def hex_to_rgb(hex_color):
    """将十六进制颜色转换为RGB元组"""
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def get_font(font_size):
    """加载可用字体，返回第一个成功加载的字体"""
    for fp in FONT_PATHS:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, font_size)
            except Exception:
                pass
    return ImageFont.load_default()


def gradient_bg(draw, w, h, color_top, color_bot, direction="vertical"):
    """绘制渐变背景"""
    r1, g1, b1 = hex_to_rgb(color_top)
    r2, g2, b2 = hex_to_rgb(color_bot)
    for y in range(h):
        t = y / h
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def draw_grid(draw, w, h, grid_color, spacing=60):
    """绘制网格线（科技感）"""
    r, g, b = hex_to_rgb(grid_color)
    for x in range(0, w, spacing):
        draw.line([(x, 0), (x, h)], fill=(r, g, b, 30))
    for y in range(0, h, spacing):
        draw.line([(0, y), (w, y)], fill=(r, g, b, 30))


def draw_neon_glow(draw, cx, cy, radius, color):
    """绘制霓虹光晕效果"""
    r, g, b = hex_to_rgb(color)
    for i in range(5):
        alpha = 60 - i * 12
        draw.ellipse(
            [cx - radius - i*20, cy - radius - i*20,
             cx + radius + i*20, cy + radius + i*20],
            fill=(r, g, b, alpha)
        )


def draw_pixel_art(draw, x, y, size, color):
    """绘制像素风格方块（复古主题）"""
    r, g, b = hex_to_rgb(color)
    draw.rectangle([x, y, x + size, y + size], fill=(r, g, b))


def draw_handdrawn_border(draw, w, h, color, roughness=5):
    """绘制手绘风格边框"""
    r, g, b = hex_to_rgb(color)
    # 顶部
    for x in range(0, w, 20):
        y_offset = int((math.sin(x * 0.1) + 1) * roughness)
        draw.point((x, y_offset), fill=(r, g, b))
        draw.point((x, y_offset + 1), fill=(r, g, b))
    # 底部
    for x in range(0, w, 20):
        y_offset = h - int((math.sin(x * 0.1) + 1) * roughness) - 1
        draw.point((x, y_offset), fill=(r, g, b))
        draw.point((x, y_offset - 1), fill=(r, g, b))
    # 左侧
    for y in range(0, h, 20):
        x_offset = int((math.sin(y * 0.1) + 1) * roughness)
        draw.point((x_offset, y), fill=(r, g, b))
        draw.point((x_offset + 1, y), fill=(r, g, b))
    # 右侧
    for y in range(0, h, 20):
        x_offset = w - int((math.sin(y * 0.1) + 1) * roughness) - 1
        draw.point((x_offset, y), fill=(r, g, b))
        draw.point((x_offset - 1, y), fill=(r, g, b))


def create_cyberpunk_sticker(text, output_path):
    """生成赛博朋克风格贴图"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    theme = THEMES["cyberpunk"]

    gradient_bg(draw, W, H, theme["bg_top"], theme["bg_bot"])
    draw_grid(draw, W, H, theme.get("grid", "#1A1A3A"), spacing=60)
    draw_neon_glow(draw, W // 2, H // 2, 200, theme["glow"])

    font = get_font(140)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (W - text_w) // 2
    text_y = (H - text_h) // 2

    draw.text((text_x + 4, text_y + 4), text, fill=(0, 0, 0, 180), font=font)
    draw.text((text_x, text_y), text, fill=hex_to_rgb(theme["primary"]), font=font)

    img.save(output_path, "PNG")


def create_kawaii_sticker(text, output_path):
    """生成可爱风格贴图"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    theme = THEMES["kawaii"]

    gradient_bg(draw, W, H, theme["bg_top"], theme["bg_bot"])

    cx, cy = W // 2, H // 2
    draw.ellipse([cx - 300, cy - 300, cx + 300, cy + 300], fill=(255, 255, 255))
    r, g, b = hex_to_rgb(theme["primary"])
    draw.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], outline=(r, g, b), width=8)

    font = get_font(120)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (W - text_w) // 2
    text_y = (H - text_h) // 2 - 40
    draw.text((text_x, text_y), text, fill=hex_to_rgb(theme["text"]), font=font)

    e1, e2 = hex_to_rgb("#4A4A4A"), hex_to_rgb("#4A4A4A")
    draw.ellipse([cx - 120, cy - 60, cx - 50, cy + 10], fill=e1)
    draw.ellipse([cx + 50, cy - 60, cx + 120, cy + 10], fill=e2)

    img.save(output_path, "PNG")


def create_minimal_sticker(text, output_path):
    """生成简约风格贴图"""
    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    theme = THEMES["minimal"]

    r, g, b = hex_to_rgb(theme["primary"])
    cx, cy = W // 2, H // 2
    draw.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], outline=(r, g, b), width=6)

    font = get_font(130)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (W - text_w) // 2
    text_y = (H - text_h) // 2
    draw.text((text_x, text_y), text, fill=hex_to_rgb(theme["text"]), font=font)

    img.save(output_path, "PNG")


def create_meme_sticker(text, output_path):
    """生成表情包风格贴图"""
    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    theme = THEMES["meme"]

    r, g, b = hex_to_rgb(theme["primary"])
    margin = 80
    draw.rectangle([margin, margin, W - margin, H - margin], fill=(r, g, b), outline=(0, 0, 0), width=8)

    font = get_font(160)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (W - text_w) // 2
    text_y = (H - text_h) // 2
    draw.text((text_x + 5, text_y + 5), text, fill=(0, 0, 0, 150), font=font)
    draw.text((text_x, text_y), text, fill=hex_to_rgb("#FFFFFF"), font=font)

    img.save(output_path, "PNG")


def create_handdrawn_sticker(text, output_path):
    """生成手绘风格贴图"""
    img = Image.new("RGBA", (W, H), (255, 248, 220, 255))
    draw = ImageDraw.Draw(img)
    theme = THEMES["hand-drawn"]

    draw_handdrawn_border(draw, W, H, theme["primary"], roughness=12)

    font = get_font(130)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (W - text_w) // 2
    text_y = (H - text_h) // 2
    draw.text((text_x, text_y), text, fill=hex_to_rgb(theme["text"]), font=font)

    img.save(output_path, "PNG")


def create_retro_sticker(text, output_path):
    """生成复古像素风格贴图"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    theme = THEMES["retro"]

    gradient_bg(draw, W, H, theme["bg_top"], theme["bg_bot"])

    pixel_size = 50
    margin = 100
    for y in range(margin, H - margin, pixel_size * 2):
        for x in range(margin, W - margin, pixel_size * 2):
            if (x + y) % (pixel_size * 4) == 0:
                draw_pixel_art(draw, x, y, pixel_size, theme["primary"])

    font = get_font(120)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (W - text_w) // 2
    text_y = (H - text_h) // 2
    draw.text((text_x, text_y), text, fill=hex_to_rgb(theme["primary"]), font=font)

    img.save(output_path, "PNG")


def create_neon_sticker(text, output_path):
    """生成霓虹灯风格贴图"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    theme = THEMES["neon"]

    font = get_font(150)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (W - text_w) // 2
    text_y = (H - text_h) // 2

    for i in range(8, 0, -2):
        r, g, b = hex_to_rgb(theme["glow"])
        draw.text((text_x, text_y), text, fill=(r, g, b, 30), font=font)

    draw.text((text_x, text_y), text, fill=hex_to_rgb(theme["primary"]), font=font)

    img.save(output_path, "PNG")


THEME_GENERATORS = {
    "cyberpunk": create_cyberpunk_sticker,
    "kawaii": create_kawaii_sticker,
    "minimal": create_minimal_sticker,
    "meme": create_meme_sticker,
    "hand-drawn": create_handdrawn_sticker,
    "retro": create_retro_sticker,
    "neon": create_neon_sticker,
}


def parse_prompt_file(prompt_file):
    """解析提示词文件，提取贴图名称、文案和标签"""
    if not os.path.exists(prompt_file):
        return None, None, None

    with open(prompt_file, "r", encoding="utf-8") as f:
        content = f.read()

    name = None
    text = None
    copy = None
    in_copy_section = False

    for line in content.split("\n"):
        if line.startswith("name:"):
            name = line.split("name:", 1)[1].strip()
        elif line.startswith("copy:"):
            copy = line.split("copy:", 1)[1].strip()
        elif "## 核心文案" in line or "## 内容" in line:
            in_copy_section = True
            continue
        elif in_copy_section and line.startswith("##"):
            in_copy_section = False
        elif in_copy_section and line.strip() and not line.startswith("#"):
            if not line.startswith("-") and not line.startswith("*"):
                copy = line.strip()
                in_copy_section = False
        elif "中文文字" in line or "Chinese text" in line.lower():
            continue
        elif text is None and len(line) > 0 and not line.startswith("#") and not line.startswith("-"):
            if ":" not in line or len(line.split(":", 1)[0]) > 10:
                if len(line.strip()) <= 10:
                    text = line.strip()

    basename = os.path.splitext(os.path.basename(prompt_file))[0]
    if name is None:
        parts = basename.split("-", 1)
        name = parts[1] if len(parts) > 1 else basename
    if text is None:
        text = name
    if copy is None:
        copy = text

    return name, text, copy


def main():
    """主函数：批量生成贴图"""
    import argparse
    parser = argparse.ArgumentParser(description="生成微信表情包（支持多种风格主题）")
    parser.add_argument("--input", "-i", required=True, help="提示词文件目录")
    parser.add_argument("--output", "-o", required=True, help="输出图片目录")
    parser.add_argument("--theme", "-t", default="cyberpunk",
                        choices=list(THEMES.keys()),
                        help=f"风格主题（默认: cyberpunk 赛博朋克）")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    prompt_files = sorted(glob.glob(os.path.join(args.input, "*.md")))

    if not prompt_files:
        print("⚠️  未找到提示词文件 (.md)")
        return

    theme_name = THEMES.get(args.theme, THEMES["cyberpunk"])["name"]
    print(f"🎨 使用风格: {theme_name} ({args.theme})")
    print(f"📂 输入目录: {args.input}")
    print(f"📁 输出目录: {args.output}")
    print(f"📐 画布尺寸: {W}×{H}px")
    print()

    generator = THEME_GENERATORS.get(args.theme, create_cyberpunk_sticker)
    success_count = 0

    for prompt_file in prompt_files:
        name, text, copy = parse_prompt_file(prompt_file)
        if name is None:
            continue

        output_file = os.path.join(args.output, f"{os.path.basename(prompt_file).replace('.md', '.png')}")
        try:
            generator(text, output_file)
            print(f"  ✓ {name}: {output_file}")
            success_count += 1
        except Exception as e:
            print(f"  ✗ {name}: 生成失败 - {e}")

    print()
    print(f"✅ 完成！成功生成 {success_count}/{len(prompt_files)} 张贴图")
    print(f"📦 输出目录: {args.output}")
    print()
    print("支持的风格主题:")
    for key, theme in THEMES.items():
        marker = "← 默认" if key == "cyberpunk" else ""
        print(f"  - {key:12s}: {theme['name']} {marker}")


if __name__ == "__main__":
    main()
