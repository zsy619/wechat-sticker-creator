#!/usr/bin/env python3
"""
generate_cover.py - 微信封面图 PIL 生成器
支持多种封面类型和尺寸：

【主要格式】
- 小绿书图片: 1080×1440px (3:4) ⭐最佳选择
  用于单独发布图片消息，类似小红书笔记风格
  描述文案支持最长 300 字

【其他格式】
- 公众号头图封面: 900×383px (2.35:1)
- 正文配图: 1080×607px (16:9)
- 缩略图: 200×200px (1:1)
- 视频号封面: 1080×1920px (9:16)
- 小红书封面: 1440×2560px (9:16)
"""
import os
from PIL import Image, ImageDraw, ImageFont

# 字体路径（macOS 系统字体）
FONT_PATHS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
]

# 预设封面尺寸
PRESET_SIZES = {
    "wechat-cover": (900, 383, "公众号头图封面"),
    "content-image": (1080, 607, "正文配图"),
    "thumbnail": (200, 200, "缩略图"),
    "video-cover": (1080, 1920, "视频号封面"),
    "xhs-cover": (1440, 2560, "小红书封面"),
}

# 主题配色方案
THEMES = {
    "cyberpunk": {
        "name": "赛博朋克",
        "bg_top": "#0D0D1A",
        "bg_bot": "#1A0A2E",
        "primary": "#00FFFF",
        "secondary": "#FF00FF",
        "accent": "#00FF88",
        "grid": "#1A1A3A",
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
        "secondary": "#495057",
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
        "text": "#FFFFFF",
    },
}


def hex_to_rgb(hex_color):
    """#RRGGBB → (r, g, b)"""
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def get_font(font_size):
    """加载可用字体"""
    for fp in FONT_PATHS:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, font_size)
            except Exception:
                pass
    return ImageFont.load_default()


def gradient_bg(draw, w, h, color_top, color_bot):
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
            [
                cx - radius - i * 15,
                cy - radius - i * 15,
                cx + radius + i * 15,
                cy + radius + i * 15,
            ],
            fill=(r, g, b, alpha),
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


def draw_sticker_preview(draw, w, h, sticker_size=120, spacing=30):
    """绘制贴图预览（用于正文配图）"""
    cols = (w - spacing) // (sticker_size + spacing)
    rows = (h - spacing) // (sticker_size + spacing)
    total = min(cols * rows, 6)

    index = 0
    for row in range(rows):
        for col in range(cols):
            if index >= total:
                break
            x = spacing + col * (sticker_size + spacing)
            y = h - spacing - sticker_size - row * (sticker_size + spacing)
            draw.ellipse(
                [x, y, x + sticker_size, y + sticker_size],
                outline=(100, 100, 100, 200),
                width=2,
            )
            index += 1
        if index >= total:
            break


def main():
    """主函数：生成封面图"""
    import argparse

    parser = argparse.ArgumentParser(
        description="生成微信封面图 - 支持公众号封面、正文配图、缩略图等多种规格"
    )
    parser.add_argument("--output", "-o", default="cover.png", help="输出路径")
    parser.add_argument("--title", "-t", default="标题", help="主标题")
    parser.add_argument("--subtitle", "-s", default="", help="副标题")
    parser.add_argument(
        "--theme",
        default="cyberpunk",
        choices=list(THEMES.keys()),
        help="主题风格（默认: cyberpunk）",
    )
    parser.add_argument(
        "--width", "-w", type=int, default=None, help="宽度（覆盖preset）"
    )
    parser.add_argument(
        "--height", "-H", type=int, default=None, help="高度（覆盖preset）"
    )
    parser.add_argument(
        "--type",
        "-T",
        default="wechat-cover",
        choices=list(PRESET_SIZES.keys()),
        help=f"封面类型（默认: wechat-cover）",
    )
    parser.add_argument("--tags", default="", help="标签，逗号分隔")
    parser.add_argument(
        "--preview", action="store_true", help="添加贴图预览（仅正文配图）"
    )
    args = parser.parse_args()

    # 获取尺寸（优先使用命令行参数，其次使用预设）
    if args.width and args.height:
        W, H = args.width, args.height
        cover_type = "custom"
    else:
        W, H, cover_type = PRESET_SIZES[args.type]

    theme = THEMES.get(args.theme, THEMES["cyberpunk"])

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 渐变背景
    gradient_bg(draw, W, H, theme["bg_top"], theme["bg_bot"])

    # 网格（科技主题）
    if "tech" in args.theme or "cyber" in args.theme or "neon" in args.theme:
        spacing = max(40, W // 20)
        draw_grid(draw, W, H, theme.get("grid", "#1A1A3A"), spacing=spacing)

    # 霓虹光效
    if "tech" in args.theme or "cyber" in args.theme or "neon" in args.theme:
        glow_radius = min(W, H) // 6
        draw_neon_glow(draw, W // 2, H // 3, glow_radius, theme["primary"])

    # 贴图预览（仅正文配图）
    if args.preview and cover_type in ["content-image", "custom"]:
        sticker_size = max(80, min(150, W // 10))
        draw_sticker_preview(draw, W, H, sticker_size=sticker_size, spacing=W // 20)

    # 主标题
    title_size = max(20, int(H * 0.15)) if H < 500 else max(30, int(H * 0.1))
    title_font = get_font(title_size)
    title_y = H // 2 - title_size // 2
    draw_text_centered(
        draw, args.title, title_y, title_font, theme["text"], max_width=W - 60
    )

    # 副标题
    if args.subtitle:
        sub_size = max(14, int(title_size * 0.5))
        sub_font = get_font(sub_size)
        sub_y = title_y + title_size + 15
        draw_text_centered(
            draw, args.subtitle, sub_y, sub_font, theme["primary"], max_width=W - 60
        )

    # 标签
    if args.tags:
        tag_size = max(12, int(H * 0.04))
        tag_font = get_font(tag_size)
        tags = args.tags.split(",")
        total_w = sum(
            draw.textbbox((0, 0), f"#{t.strip()}", font=tag_font)[2:4][0] + 25
            for t in tags
        )
        start_x = (W - total_w) // 2
        x = start_x
        for t in tags:
            tag = f"#{t.strip()}"
            draw.text(
                (x, H - tag_size - 25), tag, fill=(128, 128, 128, 200), font=tag_font
            )
            bbox = draw.textbbox((0, 0), tag, font=tag_font)
            x += bbox[2] - bbox[0] + 25

    # 保存
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    img.save(args.output, "PNG")

    # 输出信息
    type_name = (
        PRESET_SIZES.get(cover_type, {}).get(1, "custom")
        if isinstance(PRESET_SIZES.get(cover_type), tuple)
        else cover_type
    )
    if isinstance(PRESET_SIZES.get(args.type), tuple):
        type_name = PRESET_SIZES[args.type][2]
    print(f"✅ 封面已生成: {args.output}")
    print(f"   尺寸: {W}×{H} px")
    print(f"   类型: {type_name}")
    print(f"   主题: {theme['name']} ({args.theme})")


if __name__ == "__main__":
    main()
