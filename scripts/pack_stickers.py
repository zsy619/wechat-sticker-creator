#!/usr/bin/env python3
"""
pack_stickers.py - 贴图打包与封面生成

将 assets-{theme}/ 目录下的贴图打包为 ZIP，并可选生成公众号封面和缩略图。
全部使用 ffmpeg，不依赖 PIL。

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

import os, re, argparse, zipfile, subprocess, shutil, tempfile

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

def find_sticker_files(input_dir, filter_ext=None):
    """找到所有贴图文件，按文件名排序。可选按扩展名过滤。"""
    valid_exts = {'.png', '.gif', '.jpg', '.jpeg', '.webp'}
    files = []
    for f in os.listdir(input_dir):
        ext = os.path.splitext(f)[1].lower()
        if ext in valid_exts:
            if filter_ext and ext != filter_ext:
                continue
            files.append(f)
    return sorted(files, key=natural_sort_key)

def _run(cmd, capture=True):
    """执行 ffmpeg 命令，返回是否成功。cmd 可以是字符串或列表。"""
    try:
        if isinstance(cmd, str):
            result = subprocess.run(
                cmd, shell=True,
                capture_output=capture, text=True,
                timeout=120
            )
        else:
            result = subprocess.run(
                cmd,
                capture_output=capture, text=True,
                timeout=120
            )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)

def generate_cover(input_dir, output_path, size, filter_ext=None):
    """生成封面图：将前6张贴图缩放后横向拼接（ffmpeg hstack）"""
    w, h = size
    files = find_sticker_files(input_dir, filter_ext)[:6]

    if not files:
        print(f"[警告] 未找到贴图文件，无法生成封面", file=__import__('sys').stderr)
        return False

    cols = len(files)
    thumb_w = w // cols
    thumb_h = h

    # 构建 scale crop 滤镜链和 hstack 输入链
    scale_crop_labels = []
    for i in range(cols):
        scale_crop_labels.append(f"[{i}:v]scale={thumb_w}:{thumb_h}:force_original_aspect_ratio=increase,crop={thumb_w}:{thumb_h}[s{i}]")

    stack_inputs = ''.join(f"[s{i}]" for i in range(cols))
    filter_complex = ';'.join(scale_crop_labels) + f';{stack_inputs}hstack=inputs={cols}[out]'

    # 构建 ffmpeg 输入参数
    inputs = []
    for fname in files:
        inputs.extend(['-i', os.path.join(input_dir, fname)])

    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error'] + inputs + \
          ['-filter_complex', filter_complex, '-map', '[out]', '-frames:v', '1', output_path]

    ok, stdout, stderr = _run(cmd)
    if ok:
        print(f"  ✅ 封面: {output_path} ({w}x{h})")
        return True
    else:
        print(f"[警告] 封面生成失败: {stderr}")
        return False

def generate_thumbnail(input_dir, output_path, size, filter_ext=None):
    """生成缩略图：将所有贴图缩放后纵向拼接（ffmpeg vstack，最多20张）"""
    w, h = size
    files = find_sticker_files(input_dir, filter_ext)

    if not files:
        print(f"[警告] 未找到贴图文件，无法生成缩略图", file=__import__('sys').stderr)
        return False

    MAX_THUMB = 20
    files = files[:MAX_THUMB]
    thumb_w = w
    count = len(files)
    thumb_h = max(1, h // count)

    # 构建 scale crop 滤镜链和 vstack 输入链
    scale_crop_labels = []
    for i in range(count):
        scale_crop_labels.append(f"[{i}:v]scale={thumb_w}:{thumb_h}:force_original_aspect_ratio=increase,crop={thumb_w}:{thumb_h}[s{i}]")

    stack_inputs = ''.join(f"[s{i}]" for i in range(count))
    filter_complex = ';'.join(scale_crop_labels) + f';{stack_inputs}vstack=inputs={count}[out]'

    # 构建 ffmpeg 输入参数
    inputs = []
    for fname in files:
        inputs.extend(['-i', os.path.join(input_dir, fname)])

    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error'] + inputs + \
          ['-filter_complex', filter_complex, '-map', '[out]', '-frames:v', '1', output_path]

    ok, stdout, stderr = _run(cmd)
    if ok:
        print(f"  ✅ 缩略图: {output_path} ({w}x{h}, {len(files)} 张)")
        return True
    else:
        print(f"[警告] 缩略图生成失败: {stderr}")
        return False

def create_zip(input_dir, output_path, filter_ext=None):
    """将 input_dir 下的贴图打包为 ZIP，可选按扩展名过滤"""
    files = find_sticker_files(input_dir, filter_ext)
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
    ap.add_argument('--gif-only', action='store_true',
                     help='只打包 GIF 文件，忽略 PNG/JPG')
    ap.add_argument('--png-only', action='store_true',
                     help='只打包 PNG 文件，忽略 GIF/JPG')
    args = ap.parse_args()

    if args.gif_only:
        filter_ext = '.gif'
    elif args.png_only:
        filter_ext = '.png'
    else:
        filter_ext = None

    if not os.path.isdir(args.input):
        print(f"[错误] 目录不存在: {args.input}", file=__import__('sys').stderr)
        __import__('sys').exit(1)

    output_dir = os.path.dirname(os.path.abspath(args.output)) or '.'
    os.makedirs(output_dir, exist_ok=True)

    print(f"[打包] {args.input}")
    ok = True

    # ZIP
    if not create_zip(args.input, args.output, filter_ext):
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
        if not generate_cover(args.input, cover_path, size, filter_ext):
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

        thumb_path = os.path.join(output_dir, f"thumb-{args.thumbnail}.png")
        if not generate_thumbnail(args.input, thumb_path, size, filter_ext):
            ok = False

    if ok:
        print(f"\n✅ 打包完成: {args.output}")
    else:
        print(f"\n⚠️  打包完成（有警告）: {args.output}")
        __import__('sys').exit(1)

if __name__ == '__main__':
    main()
