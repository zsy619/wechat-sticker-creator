#!/usr/bin/env python3
"""
qa_check.py - 贴图质量检查

自动化检查贴图的尺寸、格式、文件名、词汇表合规性。

Usage:
    python3 scripts/qa_check.py \
        --input assets-cyberpunk/ \
        --vocabulary docs/prompts-format.md \
        --prompts prompts/

    python3 scripts/qa_check.py --input assets/ --vocabulary docs/prompts-format.md
"""

import os, re, argparse
from PIL import Image

# ── 词汇表（来自 _vocab 共享模块）────────────────────────────
try:
    from _vocab import VOCABULARY as VOCAB_KEYS, filter_valid_keys
    _vocab_available = True
except ImportError:
    VOCAB_KEYS = None
    filter_valid_keys = None
    _vocab_available = False

# ── 标准规格 ──────────────────────────────────────────────

STANDARD_W = 1080
STANDARD_H = 1440
VALID_EXTS = {'.png', '.gif'}

# ── 词汇表解析 ────────────────────────────────────────────

def parse_vocabulary_from_md(vocab_path):
    """从 prompts-format.md 解析词汇表 key"""
    try:
        with open(vocab_path) as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[警告] 词汇表文件不存在: {vocab_path}，跳过词汇表校验", file=__import__('sys').stderr)
        return None

    keys = set()
    # 匹配 | `key` | emoji | 说明 |
    for match in re.finditer(r'\| `([^`]+)` \|', content):
        keys.add(match.group(1))
    return keys

def _parse_frontmatter(content):
    """解析 frontmatter，返回 dict"""
    front = {}
    in_front = False
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped == '---':
            if not in_front:
                in_front = True
            else:
                break
            continue
        if in_front and ':' in line:
            k, v = line.split(':', 1)
            front[k.strip()] = v.strip().strip('"').strip("'")
    return front

def _parse_list(s):
    """Parse a simple unquoted comma-separated list: [a, b, c]"""
    s = s.strip()
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1]
    return [x.strip() for x in s.split(',') if x.strip()]

def parse_prompts_vocabulary(prompts_dir):
    """从 prompts/ 目录提取所有 visual_elements key（使用 frontmatter 解析）"""
    keys = set()
    if not os.path.isdir(prompts_dir):
        return keys

    for fname in os.listdir(prompts_dir):
        if not fname.endswith('.md'):
            continue
        fpath = os.path.join(prompts_dir, fname)
        with open(fpath) as f:
            content = f.read()
        front = _parse_frontmatter(content)
        ve_str = front.get('visual_elements', '')
        try:
            for k in _parse_list(ve_str):
                keys.add(k)
        except Exception:
            pass
    return keys

# ── 检查函数 ─────────────────────────────────────────────

def check_size(img_path):
    """检查图片尺寸，返回 (ok, message)"""
    try:
        with Image.open(img_path) as img:
            w, h = img.size
        if w == STANDARD_W and h == STANDARD_H:
            return True, f"{w}x{h}"
        return False, f"{w}x{h} (期望 {STANDARD_W}x{STANDARD_H})"
    except Exception as e:
        return False, f"无法读取: {e}"

def check_format(fname):
    """检查文件扩展名"""
    ext = os.path.splitext(fname)[1].lower()
    if ext in VALID_EXTS:
        return True, ext
    return False, ext

def check_manifest_compliance(manifest_path, valid_themes):
    """检查 manifest 推荐主题是否合规，返回 (ok, theme_or_error)"""
    try:
        with open(manifest_path) as f:
            content = f.read()
        m = re.search(r'\*\*推荐主题\*\*:\s*(\w+)', content)
        if not m:
            return False, "未找到推荐主题字段"
        theme = m.group(1).strip()
        if theme in valid_themes:
            return True, theme
        return False, f"'{theme}' 不在有效主题列表中"
    except FileNotFoundError:
        return False, "manifest 文件不存在"
    except Exception as e:
        return False, f"读取失败: {e}"

def check_filename(fname):
    """检查文件名是否符合 {num}-{name}.png 格式"""
    pattern = r'^\d{2,}-.+\.(png|gif)$'
    if re.match(pattern, fname, re.IGNORECASE):
        return True, fname
    return False, fname

def check_vocabulary(visual_elements, vocab_keys):
    """检查 visual_elements 是否都在词汇表中"""
    if vocab_keys is None:
        return True, []
    invalid = [k for k in visual_elements if k not in vocab_keys]
    return len(invalid) == 0, invalid

# ── 报告 ─────────────────────────────────────────────────

def print_result(check_name, ok, detail=''):
    icon = '✅' if ok else '❌'
    msg = f"  {icon} {check_name}"
    if detail:
        msg += f": {detail}"
    print(msg)

# ── 主函数 ───────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='微信贴图 - QA 自动化检查')
    ap.add_argument('--input', required=True,
                    help='assets-{theme}/ 目录 或 prompts/ 目录')
    ap.add_argument('--vocabulary',
                    help='词汇表文件路径（prompts-format.md）')
    ap.add_argument('--prompts',
                    help='prompts/ 目录路径（用于词汇表来源检查）')
    args = ap.parse_args()

    input_path = args.input
    is_assets = os.path.isdir(input_path)

    # 词汇表来源优先级：_vocab > prompts-format.md
    vocab_keys = None
    if _vocab_available:
        vocab_keys = VOCAB_KEYS
        print(f"[词汇表] 使用 _vocab共享模块（{len(VOCAB_KEYS)} 个 key）")
    elif args.vocabulary:
        vocab_keys = parse_vocabulary_from_md(args.vocabulary)
        if vocab_keys:
            print(f"[词汇表] 加载 {len(vocab_keys)} 个 key")
        else:
            print(f"[词汇表] 解析失败，跳过词汇表检查")

    # 解析 prompts 的 visual_elements
    prompt_vocab = set()
    if args.prompts and os.path.isdir(args.prompts):
        prompt_vocab = parse_prompts_vocabulary(args.prompts)
        if prompt_vocab:
            print(f"[Prompts] 发现 {len(prompt_vocab)} 个 visual_elements key")

    # 检查 assets 目录
    if is_assets:
        print(f"\n[检查] {input_path}\n")
        all_ok = True

        for fname in sorted(os.listdir(input_path)):
            fpath = os.path.join(input_path, fname)
            if os.path.isdir(fpath):
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in {'.png', '.gif', '.jpg', '.jpeg'}:
                continue

            print(f"  📄 {fname}")
            file_ok = True

            # 格式检查
            fmt_ok, _ = check_format(fname)
            print_result('  格式', fmt_ok, ext if fmt_ok else f'不支持的格式({ext})')
            if not fmt_ok: file_ok = False

            # 文件名检查
            fname_ok, _ = check_filename(fname)
            print_result('  文件名', fname_ok,
                        '正确' if fname_ok else f'不符合{STANDARD_W}x{STANDARD_H}命名规范')
            if not fname_ok: file_ok = False

            # 尺寸检查
            size_ok, detail = check_size(fpath)
            print_result('  尺寸', size_ok, detail)
            if not size_ok: file_ok = False

            # manifest 主题检查（仅第一个文件检查一次）
            if fname == sorted(f for f in os.listdir(input_path)
                               if os.path.splitext(f)[1].lower() in {'.png','.gif'})[0]:
                manifest_path = os.path.join(input_path, '..', 'sticker-manifest.md')
                if os.path.exists(manifest_path):
                    from _vocab import THEMES as VALID_THEMES
                    theme_ok, theme_detail = check_manifest_compliance(
                        manifest_path, set(VALID_THEMES.keys()))
                    status = "✅" if theme_ok else "❌"
                    print(f"  主题检查: {status} {theme_detail}")
                    if not theme_ok: all_ok = False
                else:
                    print(f"  主题检查: ⚠️  未找到 manifest（跳过）")

            if not file_ok:
                all_ok = False
            print()

        # 词汇表校验（prompts vs vocabulary）
        if vocab_keys and prompt_vocab:
            invalid = prompt_vocab - vocab_keys
            if invalid:
                print(f"❌ 词汇表不合规: {len(invalid)} 个 key 不在词汇表中:")
                for k in sorted(invalid):
                    print(f"   - {k}")
                all_ok = False
            else:
                print(f"✅ 所有 {len(prompt_vocab)} 个 key 全部合规")

        if all_ok:
            print(f"\n✅ 全部检查通过")
        else:
            print(f"\n❌ 检查未通过（有失败项）")
            __import__('sys').exit(1)

    # 检查 prompts 目录
    elif os.path.isdir(input_path) and args.vocabulary:
        print(f"\n[词汇表检查] {input_path} vs {args.vocabulary}\n")
        prompt_keys = parse_prompts_vocabulary(input_path)
        if vocab_keys:
            invalid = prompt_keys - vocab_keys
            if invalid:
                print(f"❌ {len(invalid)} 个 key 不合规:")
                for k in sorted(invalid):
                    print(f"   - {k}")
                __import__('sys').exit(1)
            else:
                print(f"✅ 全部 {len(prompt_keys)} 个 key 合规")
        else:
            print(f"无法加载词汇表，跳过检查")

    else:
        print(f"[错误] 既不是有效的 assets 目录也不是 prompts 目录: {input_path}",
              file=__import__('sys').stderr)
        __import__('sys').exit(1)

if __name__ == '__main__':
    main()
