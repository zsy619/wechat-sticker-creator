#!/usr/bin/env python3
"""
generate_cover.py - 微信封面图 PIL 生成器
参考 video-creator scripts/generate_cover.py
支持: 公众号封面(900×383)、视频号封面(1080×1920)、小红书封面(1440×2560)
"""
import sys
import os
import math
from PIL import Image, ImageDraw, ImageFont

# 字体路径（macOS 系统字体）
FONT_PATHS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
]

# 主题配色方案
THEMES = {
    "tech-modern": {
        "bg_top": "#0F172A", "bg_bot": "#1E293B",
        "primary": "#00FFFF", "secondary": "#00FF88",
        "accent": "#FF00FF", "grid": "#1A1A3A",
        "text": "#FFFFFF",
    },
    "cyberpunk": {
        "bg_top": "#0D0D1A", "bg_bot": "#1A0A2E",
        "primary": "#00FFFF", "secondary": "#FF00FF",
        "accent": "#00FF88", "grid": "#1A1A3A",
        "text": "#FFFFFF",
    },
    "business": {
        "bg_top": "#1A1A2E", "bg_bot": "#16213E",
        "primary": "#0F4C75", "secondary": "#3282B8",
        "accent": "#BBE1FA", "text": "#FFFFFF",
    },
    "minimal": {
        "bg_top": "#FFFFFF", "bg_bot": "#F8F9FA",
        "primary": "#212529", "secondary": "#495057",
        "accent": "#0D6EFD", "grid": "#E9ECEF",
        "text": "#212529",
    },
    "warm": {
        "bg_top": "#FF6B35", "bg_bot": "#F7C59F",
        "primary": "#2EC4B6", "secondary": "#FFFF",
        "accent": "#FFD166", "text": "#FFFFFF",
    },
}


def hex_to_rgb(hex_color):
    """#RRGGBB → (r, g, b)"""
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def get_font(font_size):
    """加载可用字体"""
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
    """绘制网格线"""
    r, g, b = hex_to_rgb(grid_color)
    for x in range(0, w, spacing):
        draw.line([(x, 0), (x, h)], fill=(r, g, b, 30))
    for y in range(0, h, spacing):
        draw.line([(0, y), (w, y)], fill=(r, g, b, 30))


def draw_neon_glow(draw, cx, cy, radius, color):
    """绘制霓虹光晕"""
    r, g, b = hex_to_rgb(color)
    for i in range(3):
        alpha = 60 - i * 20
        draw.ellipse(
            [cx - radius - i*15, cy - radius - i*15,
             cx + radius + i*15, cy + radius + i*15],
            fill=(r, g, b, alpha)
        )


def draw_text_centered(draw, text, y, font, color, max_width=None):
    """居中绘制文字，支持自动换行"""
    r, g, b = hex_to_rgb(color)
    if max_width is None:
        bbox = draw.textbbox((0, 0), text, font=font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), text, fill=(r, g, b), font=font)
        return y + (bbox[3] - bbox[1])
    else:
        # 自动换行
        lines = []
        current = ""
        for char in text:
            test = current + char
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width and current:
                lines.append(current)
                current = char
            else:
                current = test
        if current:
            lines.append(current)
        line_h = font.size * 1.4
        total_h = len(lines) * line_h
        start_y = y + (0 if total_h < 100 else 0)
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (W - (bbox[2] - bbox[0])) // 2
            draw.text((x, start_y + i * line_h), line, fill=(r, g, b), font=font)
        return start_y + total_h


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="生成微信封面图")
    parser.add_argument("--output", "-o", default="cover.png", help="输出路径")
    parser.add_argument("--title", "-t", default="标题", help="主标题")
    parser.add_argument("--subtitle", "-s", default="", help="副标题")
    parser.add_argument("--theme", default="tech-modern",
                        choices=list(THEMES.keys()), help="主题风格")
    parser.add_argument("--width", "-w", type=int, default=900, help="宽度")
    parser.add_argument("--height", "-H", type=int, default=383, help="高度")
    parser.add_argument("--tags", default="", help="标签，逗号分隔")
    parser.add_argument("--type", default="wechat-cover",
                        choices=["wechat-cover", "video-cover", "xhs-cover"],
                        help="封面类型")
    args = parser.parse_args()

    W, H = args.width, args.height
    theme = THEMES.get(args.theme, THEMES["tech-modern"])

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 渐变背景
    gradient_bg(draw, W, H, theme["bg_top"], theme["bg_bot"])

    # 网格（科技主题）
    if "tech" in args.theme or "cyber" in args.theme:
        draw_grid(draw, W, H, theme.get("grid", "#1A1A3A"), spacing=80)

    # 霓虹光效
    if "tech" in args.theme or "cyber" in args.theme:
        draw_neon_glow(draw, W // 2, H // 3, 80, theme["primary"])

    # 主标题
    title_size = int(H * 0.15) if H < 500 else int(H * 0.12)
    title_font = get_font(title_size)
    title_y = H // 2 - title_size // 2
    draw_text_centered(draw, args.title, title_y, title_font, theme["text"], max_width=W - 60)

    # 副标题
    if args.subtitle:
        sub_size = int(title_size * 0.5)
        sub_font = get_font(sub_size)
        sub_y = title_y + title_size + 10
        draw_text_centered(draw, args.subtitle, sub_y, sub_font, theme["primary"], max_width=W - 60)

    # 标签
    if args.tags:
        tag_size = int(H * 0.05)
        tag_font = get_font(tag_size)
        tags = args.tags.split(",")
        total_w = sum(draw.textbbox((0, 0), f"#{t.strip()}", font=tag_font)[2:4][0] + 20 for t in tags)
        start_x = (W - total_w) // 2
        x = start_x
        for t in tags:
            tag = f"#{t.strip()}"
            draw.text((x, H - tag_size - 20), tag, fill=(128, 128, 128, 200), font=tag_font)
            bbox = draw.textbbox((0, 0), tag, font=tag_font)
            x += bbox[2] - bbox[0] + 20

    # 保存
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    img.save(args.output, "PNG")
    print(f"✅ 封面已生成: {args.output} ({W}×{H})")
