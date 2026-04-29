#!/usr/bin/env python3
"""
generate_stickers.py - 微信贴图 PIL 生成器
PIL 纯代码生成，无 API 依赖，所有 API 失败时的最终兜底方案
参考 video-creator scripts/generate_cover.py 的 PIL 兜底机制
"""
import os
import sys
import glob
import argparse
import math
from PIL import Image, ImageDraw, ImageFont

# 字体路径（macOS 系统字体，按优先级）
FONT_PATHS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
]

# 主题配色
THEMES = {
    "kawaii": {
        "skin": (255, 220, 180),      # 肤色
        "cheek": (255, 160, 160),      # 红晕
        "eye": (60, 40, 40),           # 眼珠
        "mouth": (220, 80, 80),         # 嘴巴
        "hair": (80, 50, 30),           # 头发
        "bg": (245, 240, 255),         # 背景
        "shadow": (200, 180, 220),     # 阴影
    },
    "minimal": {
        "skin": (240, 235, 230),
        "cheek": (200, 200, 210),
        "eye": (40, 40, 40),
        "mouth": (180, 60, 60),
        "hair": (50, 50, 50),
        "bg": (255, 255, 255),
        "shadow": (220, 220, 220),
    },
    "meme": {
        "skin": (255, 220, 180),
        "cheek": (255, 100, 100),
        "eye": (30, 30, 30),
        "mouth": (200, 50, 50),
        "hair": (40, 40, 40),
        "bg": (255, 240, 200),
        "shadow": (200, 180, 150),
    },
    "hand-drawn": {
        "skin": (255, 235, 210),
        "cheek": (255, 180, 180),
        "eye": (50, 30, 30),
        "mouth": (200, 80, 80),
        "hair": (60, 40, 20),
        "bg": (255, 250, 240),
        "shadow": (220, 200, 180),
    },
}


def get_font(size):
    """加载可用字体"""
    for fp in FONT_PATHS:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_kawaii_face(draw, cx, cy, theme, expression="happy"):
    """绘制 Kawaii 卡通脸"""
    r = 120  # 脸半径

    # 脸（圆形肤色）
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=theme["skin"])

    # 阴影（脸下方的微妙阴影）
    draw.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10],
                 outline=theme["shadow"], width=3)

    # 头发（上部半圆）
    hair_r = r + 5
    draw.ellipse([cx - hair_r, cy - r - 40, cx + hair_r, cy + r - 50],
                 fill=theme["hair"])
    # 留海遮住额头
    draw.ellipse([cx - r, cy - r - 10, cx + r, cy - 30],
                 fill=theme["hair"])

    # 眼睛
    eye_y = cy - 15
    eye_offset = 45

    # 左眼（大眼睛）
    draw.ellipse([cx - eye_offset - 25, eye_y - 30, cx - eye_offset + 25, eye_y + 30],
                 fill=(255, 255, 255))  # 眼白
    draw.ellipse([cx - eye_offset - 15, eye_y - 18, cx - eye_offset + 15, eye_y + 18],
                 fill=theme["eye"])  # 瞳孔
    draw.ellipse([cx - eye_offset - 5, eye_y - 8, cx - eye_offset + 5, eye_y + 2],
                 fill=(255, 255, 255))  # 高光

    # 右眼
    draw.ellipse([cx + eye_offset - 25, eye_y - 30, cx + eye_offset + 25, eye_y + 30],
                 fill=(255, 255, 255))
    draw.ellipse([cx + eye_offset - 15, eye_y - 18, cx + eye_offset + 15, eye_y + 18],
                 fill=theme["eye"])
    draw.ellipse([cx + eye_offset - 5, eye_y - 8, cx + eye_offset + 5, eye_y + 2],
                 fill=(255, 255, 255))

    # 表情
    if expression == "happy":
        # 微笑（圆弧）
        draw.arc([cx - 35, cy + 20, cx + 35, cy + 70], 0, 180,
                 fill=theme["mouth"], width=5)
    elif expression == "sad":
        # 不开心（向下弯的弧线 + 眼泪）
        draw.arc([cx - 35, cy + 35, cx + 35, cy + 75], 180, 360,
                 fill=theme["mouth"], width=4)
        # 眼泪
        draw.line([cx - 55, eye_y + 15, cx - 55, eye_y + 45],
                  fill=(100, 180, 255), width=4)
        draw.line([cx + 55, eye_y + 15, cx + 55, eye_y + 45],
                  fill=(100, 180, 255), width=4)
    elif expression == "angry":
        # 生气（皱眉 + 嘴巴）
        draw.line([cx - 55, eye_y - 50, cx - 20, eye_y - 30],
                  fill=theme["hair"], width=6)
        draw.line([cx + 20, eye_y - 30, cx + 55, eye_y - 50],
                  fill=theme["hair"], width=6)
        draw.ellipse([cx - 30, cy + 25, cx + 30, cy + 55],
                     fill=theme["mouth"])
    elif expression == "surprised":
        # 惊讶（圆嘴）
        draw.ellipse([cx - 20, cy + 30, cx + 20, cy + 60],
                     fill=theme["mouth"])
    elif expression == "cool":
        # 酷（墨镜 + 抿嘴）
        # 墨镜
        draw.ellipse([cx - 60, eye_y - 20, cx - 20, eye_y + 15],
                     fill=(30, 30, 30))
        draw.ellipse([cx + 20, eye_y - 20, cx + 60, eye_y + 15],
                     fill=(30, 30, 30))
        draw.line([cx - 20, eye_y - 3, cx + 20, eye_y - 3],
                  fill=(30, 30, 30), width=4)
        # 抿嘴
        draw.arc([cx - 25, cy + 40, cx + 25, cy + 65], 0, 180,
                 fill=theme["mouth"], width=4)
    elif expression == "sleepy":
        # 困（眯眼 + 口水）
        draw.arc([cx - 50, eye_y - 5, cx - 20, eye_y + 15], 0, 180,
                 fill=theme["eye"], width=3)
        draw.arc([cx + 20, eye_y - 5, cx + 50, eye_y + 15], 0, 180,
                 fill=theme["eye"], width=3)
        # 口水
        draw.line([cx + 25, cy + 70, cx + 35, cy + 100],
                  fill=(150, 200, 255), width=5)
    elif expression == "love":
        # 喜欢（爱心眼 + 脸红）
        draw.ellipse([cx - 55, eye_y - 25, cx - 15, eye_y + 5],
                     fill=(255, 100, 150))  # 爱心代替眼睛
        draw.ellipse([cx + 15, eye_y - 25, cx + 55, eye_y + 5],
                     fill=(255, 100, 150))
        # 腮红
        draw.ellipse([cx - 75, cy + 5, cx - 45, cy + 35],
                     fill=theme["cheek"])
        draw.ellipse([cx + 45, cy + 5, cx + 75, cy + 35],
                     fill=theme["cheek"])
    elif expression == "working":
        # 认真工作（专注眼神）
        draw.ellipse([cx - 25, eye_y - 25, cx - 20, eye_y - 20],
                     fill=theme["eye"])
        draw.ellipse([cx + 20, eye_y - 25, cx + 25, eye_y - 20],
                     fill=theme["eye"])
        draw.ellipse([cx - 28, eye_y - 28, cx - 17, eye_y - 17],
                     fill=(255, 255, 255))
        draw.ellipse([cx + 17, eye_y - 28, cx + 28, eye_y - 17],
                     fill=(255, 255, 255))
        # 抿嘴
        draw.arc([cx - 20, cy + 35, cx + 20, cy + 55], 0, 180,
                 fill=theme["mouth"], width=3)

    # 腮红（通用）
    if expression not in ["love", "cool"]:
        draw.ellipse([cx - 80, cy + 5, cx - 50, cy + 25],
                     fill=theme["cheek"])
        draw.ellipse([cx + 50, cy + 5, cx + 80, cy + 25],
                     fill=theme["cheek"])


def draw_text_in_sticker(draw, text, cx, bottom_y, font_size, color):
    """在贴图底部绘制文字"""
    font = get_font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x = cx - text_w // 2
    draw.text((x, bottom_y), text, fill=color, font=font)


def generate_sticker(output_path, text, theme_name="kawaii", expression="happy"):
    """生成单张贴图"""
    W, H = 500, 500
    theme = THEMES.get(theme_name, THEMES["kawaii"])

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 背景
    draw.ellipse([0, 0, W, H], fill=theme["bg"])

    # 绘制卡通脸（居中偏上，留出底部文字空间）
    cx, cy = W // 2, H // 2 - 30
    draw_kawaii_face(draw, cx, cy, theme, expression)

    # 绘制文字（如果有）
    if text:
        draw_text_in_sticker(draw, text, cx, H - 70, 40, (80, 60, 60))

    # 添加装饰元素（气泡、星光等）
    # 左上角小星星
    draw_star(draw, 50, 60, 15, theme["cheek"])
    # 右下角小星星
    draw_star(draw, W - 50, H - 100, 12, theme["cheek"])

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, "PNG")
    print(f"  ✅ {os.path.basename(output_path)}")


def draw_star(draw, cx, cy, size, color):
    """绘制五角星"""
    points = []
    for i in range(5):
        angle = math.radians(i * 144 - 90)
        x = cx + size * math.cos(angle)
        y = cy + size * math.sin(angle)
        points.append((x, y))
        # 凹进去的点
        angle2 = math.radians(i * 144 - 90 + 72)
        x2 = cx + size * 0.4 * math.cos(angle2)
        y2 = cy + size * 0.4 * math.sin(angle2)
        points.append((x2, y2))
    draw.polygon(points, fill=color)


def generate_batch_from_manifest(manifest_path, assets_dir, theme_name="kawaii"):
    """根据 manifest 生成所有贴图"""
    import re

    if not os.path.exists(manifest_path):
        print(f"❌ Manifest not found: {manifest_path}")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析 sticker sections
    pattern = r"## Sticker \d+: (.+?)\n\*\*Type\*\*: (.+?)\n"
    matches = re.findall(pattern, content, re.DOTALL)

    print(f"📦 Generating {len(matches)} stickers (theme: {theme_name})")

    for i, (name, stype) in enumerate(matches, 1):
        name = name.strip()
        # 决定表情
        if "emotion" in stype or "反应" in stype:
            expr = "happy"
        elif "work" in stype or "工作" in stype:
            expr = "working"
        elif "love" in stype or "喜欢" in stype:
            expr = "love"
        elif "sleepy" in stype or "困" in stype:
            expr = "sleepy"
        else:
            expr = "happy"

        output_path = os.path.join(assets_dir, f"{i:02d}-{name}.png")
        generate_sticker(output_path, name, theme_name, expr)


def generate_all_from_prompts(prompts_dir, assets_dir, theme_name="kawaii"):
    """根据 prompts/ 目录批量生成贴图"""
    prompt_files = sorted(glob.glob(os.path.join(prompts_dir, "*.md")))
    if not prompt_files:
        print(f"❌ No prompt files found in {prompts_dir}")
        return

    print(f"📦 Generating {len(prompt_files)} stickers (theme: {theme_name})")

    for pf in prompt_files:
        with open(pf, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取 frontmatter
        import re
        name_match = re.search(r"^name:\s*(.+?)$", content, re.MULTILINE)
        label_match = re.search(r"^chinese_label:\s*(.+?)$", content, re.MULTILINE)
        type_match = re.search(r"^type:\s*(.+?)$", content, re.MULTILINE)

        name = name_match.group(1).strip() if name_match else os.path.basename(pf)
        label = label_match.group(1).strip() if label_match else ""
        stype = type_match.group(1).strip() if type_match else "reaction"

        # 决定表情
        if "emotion" in stype or "reaction" in stype:
            expr = "happy"
        elif "love" in stype or "喜欢" in stype:
            expr = "love"
        elif "work" in stype or "工作" in stype:
            expr = "working"
        elif "sleepy" in stype or "困" in stype:
            expr = "sleepy"
        else:
            expr = "happy"

        output_path = os.path.join(assets_dir, f"{os.path.basename(pf).replace('.md', '.png')}")
        generate_sticker(output_path, label, theme_name, expr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="微信贴图 PIL 生成器")
    parser.add_argument("--input", "-i", default="prompts/", help="prompts 目录或 manifest 文件路径")
    parser.add_argument("--output", "-o", default="assets/", help="输出目录")
    parser.add_argument("--theme", "-t", default="kawaii",
                        choices=["kawaii", "minimal", "meme", "hand-drawn"],
                        help="主题风格")
    parser.add_argument("--manifest", "-m", default=None,
                        help="sticker-manifest.md 路径（优先使用）")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if args.manifest:
        generate_batch_from_manifest(args.manifest, args.output, args.theme)
    elif os.path.isdir(args.input):
        generate_all_from_prompts(args.input, args.output, args.theme)
    else:
        print("❌ Input must be a directory or manifest file")
        sys.exit(1)

    print(f"\n✅ All stickers saved to: {args.output}")
