#!/usr/bin/env python3
"""
pack_stickers.py - 贴图打包与封面生成

将 assets-{theme}/ 目录下的贴图打包为 ZIP，并可选生成公众号封面和缩略图。

Usage:
    python3 scripts/pack_stickers.py \
        --input assets-cyberpunk/ \
        --output stickers-cyberpunk.zip

    python3 scripts/pack_stickers.py \
        --input assets-cyberpunk/ \
        --output stickers-cyberpunk.zip \
        --cover 900x383 \
        --thumbnail 200x267
"""

import os, re, argparse, zipfile
from PIL import Image

# ── 封面规格 ──────────────────────────────────────────────

COVER_SIZES = {
    '900x383': (900, 383),
    '900x500': (900, 500),
    '1080x444': (1080, 444),
}

THUMBNAIL_SIZES = {
    '200x267': (200, 267),
    '300x400': (300, 400),
}

# ── 工具函数 ─────────────────────────────────────────────

def natural_sort_key(s):
    """自然排序 key：提取字符串中的数字"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def find_sticker_files(input_dir):
    """找到所有贴图文件，按文件名排序"""
    valid_exts = {'.png', '.gif', '.jpg', '.jpeg', '.webp'}
    files = []
    for f in os.listdir(input_dir):
        ext = os.path.splitext(f)[1].lower()
        if ext in valid_exts:
            files.append(f)
    return sorted(files, key=natural_sort_key)

def generate_cover(input_dir, output_path, size):
    """生成封面图：将前6张贴图缩放后横向拼接"""
    w, h = size
    files = find_sticker_files(input_dir)[:6]

    if not files:
        print(f"[警告] 未找到贴图文件，无法生成封面", file=__import__('sys').stderr)
        return False

    thumb_w = w // len(files)
    thumb_h = h
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))

    for i, fname in enumerate(files):
        fpath = os.path.join(input_dir, fname)
        try:
            img = Image.open(fpath).convert('RGBA')
            # 裁剪为 3:4 后缩放
            src_w, src_h = img.size
            crop_h = int(src_w * 3 / 4)
            top = (src_h - crop_h) // 2
            img = img.crop((0, top, src_w, top + crop_h))
            img = img.resize((thumb_w, thumb_h), Image.LANCZOS)
            canvas.paste(img, (i * thumb_w, 0), img)
        except Exception as e:
            print(f"[警告] 封面第{i+1}张处理失败: {fname} ({e})")

    canvas.save(output_path, 'PNG')
    print(f"  ✅ 封面: {output_path} ({w}x{h})")
    return True

def generate_thumbnail(input_dir, output_path, size):
    """生成缩略图：将所有贴图缩放后纵向拼接"""
    w, h = size
    files = find_sticker_files(input_dir)

    if not files:
        print(f"[警告] 未找到贴图文件，无法生成缩略图", file=__import__('sys').stderr)
        return False

    thumb_w = w
    # 安全整数除法：防止 len(files) 过大/过小导致问题
    count = max(1, len(files))
    thumb_h = h // count  # floor除法，超出部分截断而非崩溃
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))

    for i, fname in enumerate(files):
        fpath = os.path.join(input_dir, fname)
        try:
            img = Image.open(fpath).convert('RGBA')
            src_w, src_h = img.size
            crop_h = int(src_w * 3 / 4)
            top = (src_h - crop_h) // 2
            img = img.crop((0, top, src_w, top + crop_h))
            img = img.resize((thumb_w, thumb_h), Image.LANCZOS)
            canvas.paste(img, (0, i * thumb_h), img)
        except Exception as e:
            print(f"[警告] 缩略图第{i+1}张处理失败: {fname} ({e})")

    canvas.save(output_path, 'PNG')
    print(f"  ✅ 缩略图: {output_path} ({w}x{h})")
    return True

def create_zip(input_dir, output_path):
    """将 input_dir 下的贴图打包为 ZIP"""
    files = find_sticker_files(input_dir)
    if not files:
        print(f"[错误] 未找到贴图文件: {input_dir}", file=__import__('sys').stderr)
        return False

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in files:
            fpath = os.path.join(input_dir, fname)
            zf.write(fpath, fname)

    print(f"  ✅ ZIP: {output_path} ({len(files)} 张贴图)")
    return True

# ── 主函数 ───────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='微信贴图 - 打包与封面生成')
    ap.add_argument('--input', required=True, help='assets-{theme}/ 目录路径')
    ap.add_argument('--output', required=True, help='输出 ZIP 路径')
    ap.add_argument('--cover', metavar='WIDTHxHEIGHT',
                     help='封面尺寸，如 900x383（微信公众号封面）')
    ap.add_argument('--thumbnail', metavar='WIDTHxHEIGHT',
                     help='缩略图尺寸，如 200x267')
    args = ap.parse_args()

    if not os.path.isdir(args.input):
        print(f"[错误] 目录不存在: {args.input}", file=__import__('sys').stderr)
        __import__('sys').exit(1)

    # 输出目录
    output_dir = os.path.dirname(os.path.abspath(args.output)) or '.'
    os.makedirs(output_dir, exist_ok=True)

    print(f"[打包] {args.input}")
    ok = True

    # ZIP
    if not create_zip(args.input, args.output):
        ok = False

    # 封面
    if args.cover:
        if args.cover in COVER_SIZES:
            size = COVER_SIZES[args.cover]
        elif re.match(r'^\d+x\d+$', args.cover):
            w, h = map(int, args.cover.split('x'))
            size = (w, h)
        else:
            print(f"[警告] 未知封面尺寸: {args.cover}，使用 900x383", file=__import__('sys').stderr)
            size = COVER_SIZES['900x383']

        cover_path = os.path.join(output_dir, f"cover-{args.cover}.png")
        if not generate_cover(args.input, cover_path, size):
            ok = False

    # 缩略图
    if args.thumbnail:
        if args.thumbnail in THUMBNAIL_SIZES:
            size = THUMBNAIL_SIZES[args.thumbnail]
        elif re.match(r'^\d+x\d+$', args.thumbnail):
            w, h = map(int, args.thumbnail.split('x'))
            size = (w, h)
        else:
            print(f"[警告] 未知缩略图尺寸: {args.thumbnail}，使用 200x267", file=__import__('sys').stderr)
            size = THUMBNAIL_SIZES['200x267']

        thumb_path = os.path.join(output_dir, f"thumbnail-{args.thumbnail}.png")
        if not generate_thumbnail(args.input, thumb_path, size):
            ok = False

    if ok:
        print(f"\n✅ 打包完成: {args.output}")
    else:
        print(f"\n⚠️  打包完成（有警告）: {args.output}")
        __import__('sys').exit(1)

if __name__ == '__main__':
    main()
