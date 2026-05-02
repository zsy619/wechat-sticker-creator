#!/usr/bin/env python3
"""
generate_frames.py - 微信贴图两段式生成器 v4.9.0

优先级：AI → Remotion
AI 失败后尝试 Remotion，Remotion 失败则报错不再降级。

输出格式：
  - AI 模式：PNG
  - Remotion 模式：GIF（90帧动画，由 Remotion 序列帧 + ffmpeg 合成）

Usage:
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk --mode remotion
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk --continue-on-error
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk --debug-remotion
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk --template-dir ./my-templates
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk --remotion-version 4.0.448
    python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk --dry-run
"""

import os, sys, json, time, glob, subprocess, argparse, re
import urllib.request, urllib.error

# ── 常量 ───────────────────────────────────────────────────
W, H = 1080, 1440
FPS = 30
FRAMES_PER_STICKER = 90  # 每张贴图 90 帧 @ 30fps = 3 秒
REMOTION_CACHE_DIR = os.path.expanduser("~/.cache/wechat-sticker-remotion")
DEFAULT_REMOTION_VERSION = "4.0.448"

# ── 全局参数（由 main() 设置）────────────────────────────────
_args = None   # argparse.Namespace，持有所有 CLI 参数

# ── 主题定义 ────────────────────────────────────────────────

from _vocab import THEMES, parse_prompt_file, _parse_list

_EMOJI_FALLBACK = {
    "brain": "🧠", "ai大脑": "🧠", "ai计算": "🧠", "神经网络": "🧠", "neural_network": "🧠",
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

# ── 辅助函数 ────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")

# ═══════════════════════════════════════════════════════════════
# P1-2: Remotion 版本检测
# ═══════════════════════════════════════════════════════════════

def get_remotion_version():
    """读取全局 npx remotion --version，返回版本字符串或 None"""
    try:
        r = subprocess.run(['npx', 'remotion', '--version'],
                          capture_output=True, timeout=30, text=True)
        if r.returncode == 0:
            return r.stdout.strip().split('\n')[0]
    except Exception:
        pass
    return None

# ═══════════════════════════════════════════════════════════════
# P0-2: 环境预检（增强版）
# ═══════════════════════════════════════════════════════════════

def _check_remotion_environment():
    """
    全面检查 Remotion 运行环境。
    返回 (ok: bool, reason: str)
    """
    # 检查 npx
    try:
        r = subprocess.run(['npx', '--version'], capture_output=True, timeout=10, text=True)
        if r.returncode != 0:
            return False, "npx 不可用（returncode != 0）"
    except FileNotFoundError:
        return False, "npx 未找到（Node.js 未安装）"
    except subprocess.TimeoutExpired:
        return False, "npx --version 超时"

    # 检查 Remotion CLI（v3.3.0 的 `versions` 和 `--version` 都返回 exitcode=1，
    # 但 stdout 包含版本信息视为成功）
    version_str = ""
    try:
        r = subprocess.run(['npx', 'remotion', '--version'],
                          capture_output=True, timeout=30, text=True)
        # exitcode=1 仍视为成功（只要有版本输出）
        version_str = r.stdout.strip().split('\n')[0] if r.stdout.strip() else ""
        if not version_str or '@remotion/cli' not in version_str:
            return False, f"remotion CLI 不可用（无有效版本输出）"
        log(f"[Remotion] 检测到版本: {version_str}", "INFO")
    except FileNotFoundError:
        return False, "npx remotion 未安装"
    except subprocess.TimeoutExpired:
        return False, "npx remotion --version 超时"

    # 版本兼容性检查（> 4.0.80 提示可能兼容问题）
    if version_str:
        try:
            parts = version_str.lstrip('v').split('.')
            major, minor = int(parts[0]), int(parts[1])
            if major > 4 or (major == 4 and minor > 0):
                log(f"[Remotion] 版本 {version_str} > 4.0.x，可能存在兼容差异", "WARN")
        except Exception:
            pass

    return True, "OK"

# ═══════════════════════════════════════════════════════════════
# P1-3: 错误解析
# ═══════════════════════════════════════════════════════════════

_ERROR_PATTERNS = [
    (re.compile(r'delayRender.*timeout', re.I),    "delayRender() 超时：esbuild 编译过慢或 chromium 无响应。解决方案：升级 chromium 或降低 FPS"),
    (re.compile(r'chromium.*not.*found', re.I),     "Chromium 未找到：Remotion 需要 chromium。brew install chromium 或 playwright install chromium"),
    (re.compile(r'No such file.*index\.tsx', re.I),"index.tsx 未找到：项目目录未正确创建或被误删"),
    (re.compile(r'Unexpected token.*class', re.I),  "JSX 语法错误：模板字符串替换可能产生语法问题。使用 --debug-remotion 查看写入的 TSX 文件"),
    (re.compile(r'Cannot find module', re.I),       "模块未找到：package.json 依赖缺失。检查 npm install 是否成功"),
    (re.compile(r'EACCES|permission denied', re.I),"权限拒绝：项目目录不可写。chmod -R 755 或使用 sudo"),
    (re.compile(r'ENOMEM|out of memory', re.I),    "内存不足：渲染帧过多。减少贴图数量或关闭其他程序"),
    (re.compile(r'fps.*must be a number', re.I),   "fps 参数类型错误：spring() 未传入 fps 参数"),
    (re.compile(r'Expected.*but found.*1', re.I),  "JSX 属性语法错误：fps=30 应为 fps={30}"),
]

def _parse_remotion_error(stderr_text):
    """将原始 stderr 解析为用户友好错误信息"""
    for pattern, advice in _ERROR_PATTERNS:
        if pattern.search(stderr_text):
            return f"{advice}\n  原始错误: {stderr_text[:300]}"
    # 通用截断
    if len(stderr_text) > 300:
        return f"{stderr_text[:300]}...\n  完整错误见 project_dir/logs/"
    return stderr_text

# ═══════════════════════════════════════════════════════════════
# P2-1: 日志工具
# ═══════════════════════════════════════════════════════════════

def _write_log(subdir, name, content, mode='w'):
    """写入项目子目录日志文件"""
    log_file = os.path.join(subdir, name)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, mode) as f:
        f.write(content)

# ═══════════════════════════════════════════════════════════════
# P1-1: 持久化 Remotion 缓存
# ═══════════════════════════════════════════════════════════════

def _get_cached_remotion_base(theme_key):
    """
    从 ~/.cache/wechat-sticker-remotion/ 返回已预构建的 Remotion 项目路径。
    如果不存在则创建（复制模板 + npm install）。
    返回 (cache_dir, version_used)
    """
    version = _args.remotion_version if _args and _args.remotion_version else DEFAULT_REMOTION_VERSION
    cache_dir = os.path.join(REMOTION_CACHE_DIR, f"base-{version}")

    marker = os.path.join(cache_dir, ".npm_installed")
    if os.path.exists(marker):
        log(f"[Remotion 缓存] 使用已缓存项目: {cache_dir}", "INFO")
        return cache_dir, version

    os.makedirs(cache_dir, exist_ok=True)

    # 读取模板文件
    tmpl_base = _get_template_dir()
    for fname in ["index.tsx", "StickerComponent.tsx", "StickerContent.tsx"]:
        src = os.path.join(tmpl_base, fname)
        dst = os.path.join(cache_dir, "src", fname)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(src) as f:
            content = f.read()
        # 模板占位符用默认值填充（实际渲染时会再替换）
        content = (content
            .replace("__FPS__", str(FPS))
            .replace("__W__", str(W))
            .replace("__H__", str(H))
            .replace("__BG_COLOR__", THEMES.get(theme_key, THEMES["cyberpunk"])["bg"])
            .replace("__TEXT_COLOR__", THEMES.get(theme_key, THEMES["cyberpunk"])["text"])
            .replace("__PRIMARY__", THEMES.get(theme_key, THEMES["cyberpunk"])["primary"])
            .replace("__SECONDARY__", THEMES.get(theme_key, THEMES["cyberpunk"])["secondary"])
            .replace("__THEME_KEY__", theme_key)
            .replace("__TOTAL_FRAMES__", str(FRAMES_PER_STICKER))
            .replace("__SEQUENCES__", ""))
        with open(dst, "w") as f:
            f.write(content)

    pkg = {
        "name": "wechat-sticker-remotion-base",
        "version": "1.0.0",
        "dependencies": {"@remotion/cli": version, "remotion": version}
    }
    with open(os.path.join(cache_dir, "package.json"), "w") as f:
        json.dump(pkg, f, indent=2)

    # 写基础 styles.css（从 remotion/styles/base.css 复制）
    # tmpl_base = remotion/template/，os.pardir = remotion/，styles/base.css 存在
    tmpl_css_src = os.path.join(tmpl_base, os.pardir, "styles", "base.css")
    if os.path.exists(tmpl_css_src):
        with open(tmpl_css_src) as f:
            css_src = f.read()
    else:
        css_src = ""  # 空 CSS（styles 由内联 style 提供）
    with open(os.path.join(cache_dir, "src", "styles.css"), "w") as f:
        f.write(css_src)

    # npm install
    log(f"[Remotion 缓存] 首次构建，执行 npm install（版本 {version}）...", "INFO")
    install_log = os.path.join(cache_dir, "logs", "npm_install.log")
    os.makedirs(os.path.dirname(install_log), exist_ok=True)
    r = subprocess.run(
        ["npm", "install", "--prefer-offline"],
        cwd=cache_dir, capture_output=True, text=True, timeout=300
    )
    with open(install_log, "w") as f:
        f.write(r.stdout)
        f.write(r.stderr)
    if r.returncode != 0:
        log(f"[Remotion 缓存] npm install 失败，见 {install_log}", "ERROR")
    else:
        with open(marker, "w") as f:
            f.write(version + "\n")
        log(f"[Remotion 缓存] npm install 完成", "OK")
    return cache_dir, version

# ═══════════════════════════════════════════════════════════════
# P3-2: 模板路径解析
# ═══════════════════════════════════════════════════════════════

def _get_template_dir():
    """返回模板目录路径（支持 --template-dir 覆盖）"""
    if _args and _args.template_dir:
        return os.path.abspath(_args.template_dir)
    # 默认使用技能内置模板
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "remotion", "template")

# ═══════════════════════════════════════════════════════════════
# P3-1: 模板热重载检测
# ═══════════════════════════════════════════════════════════════

def _get_template_mtime():
    """返回模板目录最新修改时间（递归）"""
    tmpl = _get_template_dir()
    latest = 0
    for root, dirs, files in os.walk(tmpl):
        for fname in files:
            if fname.endswith(('.tsx', '.ts', '.css')):
                fpath = os.path.join(root, fname)
                try:
                    latest = max(latest, os.path.getmtime(fpath))
                except OSError:
                    pass
    return latest

# ═══════════════════════════════════════════════════════════════
# P0-1 / P0-3 / P1-4: 核心 Remotion 渲染（重写）
# ═══════════════════════════════════════════════════════════════

# 共享 Remotion 项目路径缓存（模块级，避免同一 session 重复创建）
_remotion_project_cache = {}

def _get_or_create_remotion_project(project_dir, stickers, theme_key):
    """
    创建或返回已有的单一 Remotion 项目（含多 Sequence）。

    P1-1 优化：从 ~/.cache/wechat-sticker-remotion/ 复制预构建项目，
           避免每次都 npm install（节省 10-30s）。
    P3-1 优化：对比模板修改时间，如有变更则强制重建。
    """
    cache_key = (project_dir, tuple(s[0] for s in stickers), theme_key)
    if cache_key in _remotion_project_cache:
        return _remotion_project_cache[cache_key]

    # P3-1: 模板修改时间对比
    tmpl_mtime_marker = os.path.join(project_dir, ".template_mtime")
    current_mtime = _get_template_mtime()
    force_rebuild = False
    if os.path.exists(tmpl_mtime_marker):
        try:
            prev_mtime = float(open(tmpl_mtime_marker).read().strip())
            if current_mtime > prev_mtime:
                force_rebuild = True
                log("[Remotion] 模板已修改，强制重建项目", "WARN")
        except (ValueError, IOError):
            pass

    # 目录存在但需要重建：删除旧项目
    if os.path.exists(project_dir) and (force_rebuild or not os.path.exists(os.path.join(project_dir, "package.json"))):
        import shutil
        shutil.rmtree(project_dir)

    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

        # P1-1: 从持久化缓存复制项目
        cached_base, version_used = _get_cached_remotion_base(theme_key)
        if os.path.exists(os.path.join(cached_base, "node_modules")):
            import shutil
            # 复制整个预构建项目
            for item in os.listdir(cached_base):
                if item in ("logs", ".npm_installed"):
                    continue
                src = os.path.join(cached_base, item)
                dst = os.path.join(project_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            log(f"[Remotion] 从缓存复制项目成功: {cached_base}", "INFO")

    theme = THEMES.get(theme_key, THEMES["cyberpunk"])
    bg_color    = theme["bg"]
    text_color  = theme["text"]

    # 获取 emoji_map
    try:
        from _vocab import EMOJI_MAP
        emoji_map = EMOJI_MAP
    except ImportError:
        emoji_map = _EMOJI_FALLBACK

    # 构建 Sequence JSX（每张贴图 90 帧）
    sequences_jsx = ""
    for i, (name, copy, v_elems) in enumerate(stickers):
        emojis = [emoji_map.get(e, "📝") for e in v_elems if e in emoji_map]
        if not emojis:
            emojis = ["📝"]
        copy_escaped = (copy
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("`", "\\`")
            .replace("$", "\\$")
            .replace("{", "\\{")
            .replace("}", "\\}"))
        emoji_json = json.dumps(emojis, ensure_ascii=False)
        sequences_jsx += (
            f"      <Sequence from={{{i} * {FRAMES_PER_STICKER}}} durationInFrames={{{FRAMES_PER_STICKER}}}>\n"
            f"        <StickerScene copy={{'{copy_escaped}'}} emojis_str={{{repr(emoji_json)}}} frameOffset={{{i} * {FRAMES_PER_STICKER}}} stickerIndex={{{i}}} />\n"
            f"      </Sequence>\n"
        )

    # 读取模板文件
    tmpl_base = _get_template_dir()
    try:
        with open(os.path.join(tmpl_base, "StickerContent.tsx")) as f:
            inner_code = f.read()
        with open(os.path.join(tmpl_base, "StickerComponent.tsx")) as f:
            outer_code = f.read()
        with open(os.path.join(tmpl_base, "index.tsx")) as f:
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
        .replace("__THEME_KEY__", theme_key)
        .replace("__TOTAL_FRAMES__", str(total_frames))
        .replace("__SEQUENCES__", sequences_jsx)
    )
    outer_code = (outer_code
        .replace("__FPS__", str(FPS))
        .replace("__W__", str(W))
        .replace("__H__", str(H))
        .replace("__TOTAL_FRAMES__", str(total_frames))
    )
    # B3修复：将占位符替换为实际常量值（StickerComponent 显式接收 Props）
    outer_code = (outer_code
        .replace("totalFrames={__TOTAL_FRAMES__}", f"totalFrames={{{total_frames}}}")
        .replace("fps={__FPS__}", f"fps={{{FPS}}}")
        .replace("width={__W__}", f"width={{{W}}}")
        .replace("height={__H__}", f"height={{{H}}}")
    )

    # B1+B2修复：CSS 单一来源，仅全局重置（无 :root 变量，TS 使用内联常量）
    # B2：删除 :root { --primary, --secondary } 变量块（TS 不读取 CSS 变量）
    css_content = f"""body {{ margin: 0; padding: 0; overflow: hidden; background: {bg_color}; }}
* {{ box-sizing: border-box; }}"""

    # P2-4: debug 模式下保留原始 TSX 内容
    if _args and _args.debug_remotion:
        debug_dir = os.path.join(project_dir, "debug")
        os.makedirs(debug_dir, exist_ok=True)
        _write_log(debug_dir, "StickerContent.tsx", inner_code)
        _write_log(debug_dir, "StickerComponent.tsx", outer_code)
        _write_log(debug_dir, "index.tsx", entry_code)

    # 写入最终 TSX 文件
    for fname, code in [("StickerContent.tsx", inner_code),
                         ("StickerComponent.tsx", outer_code),
                         ("index.tsx", entry_code)]:
        with open(os.path.join(project_dir, "src", fname), "w") as f:
            f.write(code)
    with open(os.path.join(project_dir, "src", "styles.css"), "w") as f:
        f.write(css_content)

    # P3-1: 记录模板 mtime
    with open(tmpl_mtime_marker, "w") as f:
        f.write(str(current_mtime) + "\n")

    # 版本写入 package.json（允许 --remotion-version 覆盖）
    version = _args.remotion_version if _args and _args.remotion_version else DEFAULT_REMOTION_VERSION
    pkg = {
        "name": "sticker-project",
        "version": "1.0.0",
        "dependencies": {"@remotion/cli": version, "remotion": version}
    }
    with open(os.path.join(project_dir, "package.json"), "w") as f:
        json.dump(pkg, f, indent=2)

    _remotion_project_cache[cache_key] = project_dir
    return project_dir


def _render_remotion_still(project_dir, sticker_index, total_stickers):
    """
    使用 npx remotion still 渲染单帧 PNG。
    P0-1: 修复 --frames 参数错误，改用 remotion still
    P0-3: 输出 PNG（Remotion still 直接输出 PNG）
    P1-4: 动态超时
    """
    target_frame = sticker_index * FRAMES_PER_STICKER  # 每张贴图的第 0 帧（Sequence 起始）
    output_path  = os.path.join(project_dir, f"out_sticker_{sticker_index}.png")

    # P1-4: 动态超时 = max(120s, 每帧约 2s * 总帧数)
    estimated_frames = total_stickers * FRAMES_PER_STICKER
    timeout = max(120, estimated_frames * 2)

    log(f"[Remotion] npx remotion still 渲染帧 {target_frame}（预计超时 {timeout}s）...", "INFO")

    # P2-1: 渲染日志
    log_file = os.path.join(project_dir, "logs", f"render_{sticker_index}.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    result = subprocess.run(
        ["npx", "remotion", "still",
         "src/index.tsx", "StickerComponent",
         "--output", output_path,
         "--frame", str(target_frame),
         "--fps", str(FPS)],
        cwd=project_dir,
        capture_output=True,
        text=True,
        timeout=timeout
    )

    # 写入日志
    with open(log_file, "w") as f:
        f.write(f"=== npx remotion still ===\n")
        f.write(f"frame: {target_frame}\n")
        f.write(f"cwd: {project_dir}\n")
        f.write(f"\n=== STDOUT ===\n")
        f.write(result.stdout)
        f.write(f"\n=== STDERR ===\n")
        f.write(result.stderr)
        f.write(f"\n=== RETURNCODE: {result.returncode} ===\n")

    return result, output_path


def _frames_to_gif(frame_dir_or_paths, output_gif_path, fps=30):
    """
    将帧目录或帧路径列表合成为 GIF。
    使用 ffmpeg paletteuse（高质量 GIF），无需 PIL。
    """
    import tempfile, subprocess as _sp

    if isinstance(frame_dir_or_paths, str):
        frame_files = sorted([
            os.path.join(frame_dir_or_paths, f)
            for f in os.listdir(frame_dir_or_paths)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])
    else:
        frame_files = list(frame_dir_or_paths)

    if not frame_files:
        raise RuntimeError("无可用帧")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 符号链接帧为顺序文件名
        for i, fp in enumerate(frame_files):
            ext = os.path.splitext(fp)[1]
            os.symlink(os.path.abspath(fp), os.path.join(tmpdir, f"{i:04d}{ext}"))

        # 生成调色板
        palette_cmd = (
            f"ffmpeg -y -hide_banner -loglevel error "
            f"-framerate {fps} -i '{tmpdir}/%04d.png' "
            f"-vf palettegen=/tmp/sticker_palette.png"
        )
        _sp.run(palette_cmd, shell=True)

        # 合成 GIF
        gif_cmd = (
            f"ffmpeg -y -hide_banner -loglevel error "
            f"-framerate {fps} -i '{tmpdir}/%04d.png' "
            f"-i /tmp/sticker_palette.png "
            f"-lavfi paletteuse '{output_gif_path}'"
        )
        ok = _sp.run(gif_cmd, shell=True).returncode == 0
        if not ok:
            # fallback: 直接合成（无调色板）
            fallback_cmd = (
                f"ffmpeg -y -hide_banner -loglevel error "
                f"-framerate {fps} -i '{tmpdir}/%04d.png' "
                f"-loop 0 '{output_gif_path}'"
            )
            _sp.run(fallback_cmd, shell=True)

    log(f"[GIF] 已合成 {len(frame_files)} 帧 → {output_gif_path}", "OK")


def generate_remotion_gif(name, copy, visual_elements, theme_key, output_path,
                           sticker_index, total_stickers, project_dir):
    """
    为单张贴图渲染 GIF（90帧动画）。

    P0-1 修复：使用 npx remotion still 逐帧渲染 PNG，然后合成 GIF。
    P1-3 修复：通过 _parse_remotion_error() 提供友好错误信息。
    P1-4 修复：动态超时。
    P2-1 修复：写入渲染日志。
    """
    ok, reason = _check_remotion_environment()
    if not ok:
        raise RuntimeError(f"Remotion 环境检查失败: {reason}")

    gif_path = os.path.splitext(output_path)[0] + ".gif"

    # P1-4: 动态超时
    estimated_frames = total_stickers * FRAMES_PER_STICKER
    timeout = max(120, estimated_frames * 2)

    # 渲染 90 帧序列（每 3 帧取 1 帧 = 30 帧 GIF，文件更小）
    # 渲染全 90 帧 → ffmpeg paletteuse 合成
    frames_dir = os.path.join(project_dir, "frames", f"sticker_{sticker_index}")
    os.makedirs(frames_dir, exist_ok=True)

    log(f"[Remotion] 开始渲染 {name}（{FRAMES_PER_STICKER} 帧，timeout={timeout}s）...", "INFO")

    failed_frames = []
    for f in range(FRAMES_PER_STICKER):
        frame_idx  = sticker_index * FRAMES_PER_STICKER + f
        frame_path = os.path.join(frames_dir, f"frame_{f:03d}.png")

        if os.path.exists(frame_path) and os.path.getsize(frame_path) > 512:
            # 已渲染的帧跳过（支持断点续传）
            continue

        result = subprocess.run(
            ["npx", "remotion", "still",
             "src/index.tsx", "StickerComponent",
             "--output", frame_path,
             "--frame", str(frame_idx),
             "--fps", str(FPS)],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode != 0 or not os.path.exists(frame_path):
            err = _parse_remotion_error(result.stderr)
            failed_frames.append((f, err))
            log(f"[Remotion] 帧 {f} 渲染失败: {err[:100]}", "WARN")
            # 继续下一帧，不要中断

    # 汇总失败帧
    if failed_frames:
        failure_rate = len(failed_frames) / FRAMES_PER_STICKER
        log(f"[Remotion] {name}: {len(failed_frames)}/{FRAMES_PER_STICKER} 帧失败（{failure_rate*100:.0f}%）", "WARN")
        if failure_rate > 0.5:
            # 超过 50% 帧失败，抛出错误
            raise RuntimeError(f"渲染失败率 {failure_rate*100:.0f}% > 50%，Remotion 模式失败")

    # 检查可用帧数
    available_frames = [
        f for f in os.listdir(frames_dir)
        if os.path.join(frames_dir, f).endswith('.png') and
        os.path.getsize(os.path.join(frames_dir, f)) > 512
    ]
    if len(available_frames) < 10:
        raise RuntimeError(f"可用帧数不足（{len(available_frames)} < 10），Remotion 模式失败")

    # 合成 GIF（每隔 3 帧取一帧 = 30 帧 @ 30fps = 1 秒）
    # 实际上我们希望 3 秒 GIF，取全帧或降采样
    gif_frames = sorted([
        os.path.join(frames_dir, f)
        for f in available_frames
    ])

    # 按比例降采样（90帧→30帧，保持 3 秒时长）
    step = max(1, len(gif_frames) // 30)
    gif_frames_sampled = gif_frames[::step][:30]

    _frames_to_gif(gif_frames_sampled, gif_path)
    log(f"[Remotion] {name} GIF 导出成功（{len(gif_frames_sampled)} 帧）", "OK")
    return True


# ═══════════════════════════════════════════════════════════════
# 阶段一：AI 生成
# ═══════════════════════════════════════════════════════════════

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
    返回 image_url 或抛出异常。
    """
    url     = provider["url"]
    headers = provider["headers"]()
    body    = json.dumps(provider["body"]()).encode()

    for attempt in range(max_retries):
        try:
            req  = urllib.request.Request(url, data=body, headers=headers, method="POST")
            resp = urllib.request.urlopen(req, timeout=timeout)
            status = resp.status
            data   = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            status   = e.code
            try:
                err_body = json.loads(e.read())
            except Exception:
                err_body = {}
        except (urllib.error.URLError, TimeoutError) as e:
            raise RuntimeError(f"网络错误/超时: {e}")

        # 429 限流
        if status == 429:
            if attempt < max_retries - 1:
                wait_sec = 10 * (attempt + 1)
                log(f"[{provider['name']}] 429 限流，等待 {wait_sec}s（第 {attempt+1}/{max_retries} 次）", "WARN")
                time.sleep(wait_sec)
                continue
            else:
                raise RuntimeError(f"429 限流，已重试 {max_retries} 次仍失败")

        # 401/403/402 认证/付款错误
        if status in (401, 403, 402):
            raise RuntimeError(f"认证/付款错误 ({status})")

        if status >= 400:
            raise RuntimeError(f"HTTP {status}: {err_body}")

        # 解析 image_url
        image_url = None
        if provider["name"] == "dashscope" and "data" in data:
            image_url = data["data"][0].get("url")
        elif provider["name"] == "seedream":
            if "data" in data and data["data"]:
                image_url = data["data"][0].get("image_url") or data["data"][0].get("image_base64")
        elif "data" in data and len(data["data"]) > 0:
            image_url = data["data"][0].get("url") or data["data"][0].get("b64_json")

        if not image_url:
            raise RuntimeError(f"响应中无 image_url: {str(data)[:200]}")
        return image_url

    raise RuntimeError(f"重试耗尽")


def generate_ai_image(name, copy, style_keyword, theme_key, output_path):
    """调用 AI API 生成图像"""
    prompt = build_ai_prompt(name, copy, style_keyword, theme_key)

    providers = [
        {
            "name": "dashscope",
            "url": "https://api.dashscope.com/v1/images/generations",
            "headers": lambda: {"Authorization": f"Bearer {os.environ.get('DASHSCOPE_API_KEY','')}",
                               "Content-Type": "application/json"},
            "body": lambda: {"model": "qwen-image-2.0-pro", "prompt": prompt,
                             "size": "1024x1024", "n": 1},
        },
        {
            "name": "seedream",
            "url": "https://visual.volcengineapi.com/?Action=TextToImage&Version=2023-05-01",
            "headers": lambda: {"Authorization": f"Bearer {os.environ.get('VOLCENGINE_API_KEY', os.environ.get('SEEDREAM_API_KEY',''))}",
                               "Content-Type": "application/json"},
            "body": lambda: {"model": "doubao-seedream-5-0-260128", "prompt": prompt,
                             "width": 1024, "height": 1360, "num_images": 1},
        },
        {
            "name": "minimax",
            "url": "https://api.minimax.chat/v1/image_generation",
            "headers": lambda: {"Authorization": f"Bearer {os.environ.get('MINIMAX_API_KEY','')}",
                               "Content-Type": "application/json"},
            "body": lambda: {"model": "image-01", "prompt": prompt,
                             "width": 1024, "height": 1360},
        },
        {
            "name": "openai",
            "url": "https://api.openai.com/v1/images/generations",
            "headers": lambda: {"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY','')}",
                               "Content-Type": "application/json"},
            "body": lambda: {"model": "dall-e-3", "prompt": prompt,
                             "size": "1024x1024", "n": 1},
        },
    ]

    for p in providers:
        try:
            image_url = _call_ai_provider(p, prompt)

            # 下载图片并用 ffmpeg 裁剪缩放为标准尺寸
            import tempfile, subprocess as _sp
            if image_url.startswith('data:'):
                import base64
                b64 = image_url.split(',')[1]
                img_data = base64.b64decode(b64)
            else:
                req = urllib.request.Request(image_url)
                with urllib.request.urlopen(req, timeout=30) as r:
                    img_data = r.read()

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_in:
                tmp_in.write(img_data)
                tmp_in.flush()
                tmp_in.name  # 保持文件路径

            out_cmd = (
                f"ffmpeg -y -hide_banner -loglevel error "
                f"-i '{tmp_in.name}' "
                f"-vf 'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}' "
                f"'{output_path}'"
            )
            ok = _sp.run(out_cmd, shell=True).returncode == 0
            os.unlink(tmp_in.name)
            if not ok:
                raise RuntimeError("ffmpeg 裁剪失败")

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


# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

def main():
    global _args
    ap = argparse.ArgumentParser(
        description='微信贴图两段式生成器 v4.9.0（AI → Remotion）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 generate_frames.py --input prompts/ --output assets/ --theme cyberpunk
  python3 generate_frames.py --input prompts/ --output assets/ --mode remotion
  python3 generate_frames.py --input prompts/ --output assets/ --continue-on-error
  python3 generate_frames.py --input prompts/ --output assets/ --debug-remotion
  python3 generate_frames.py --input prompts/ --output assets/ --template-dir ./my-templates
  python3 generate_frames.py --input prompts/ --output assets/ --remotion-version 4.0.80
  python3 generate_frames.py --input prompts/ --output assets/ --dry-run
"""
    )
    ap.add_argument('--input',             required=True,  help='prompts/ 目录路径或单个 .md 文件')
    ap.add_argument('--output',            required=True,  help='输出目录路径')
    ap.add_argument('--theme',             default='cyberpunk', help='主题风格（default: cyberpunk）')
    ap.add_argument('--mode',             choices=['auto','ai','remotion'],
                                            default='auto', help='生成模式（default: auto）')
    ap.add_argument('--continue-on-error', action='store_true',
                                            help='某张贴图失败时继续处理下一张（default: False）')
    ap.add_argument('--debug-remotion',    action='store_true',
                                            help='保留 Remotion 调试文件（TSX 源码、日志）（default: False）')
    ap.add_argument('--template-dir',      default=None,
                                            help='自定义 Remotion 模板目录（覆盖内置模板）')
    ap.add_argument('--remotion-version',  default=None,
                                            help=f'Remotion 版本（default: {DEFAULT_REMOTION_VERSION}）')
    ap.add_argument('--dry-run',          action='store_true',
                                            help='仅解析并打印所有贴图的生成计划，不实际生成文件')
    _args = ap.parse_args()

    # Remotion 版本提示
    detected_version = get_remotion_version()
    if detected_version:
        log(f"[Remotion] 检测到全局版本: {detected_version}", "INFO")
    requested = _args.remotion_version or DEFAULT_REMOTION_VERSION
    if _args.mode in ('auto', 'remotion'):
        if detected_version and detected_version != requested:
            log(f"[Remotion] 版本差异: requested={requested}, detected={detected_version}", "WARN")

    input_path = _args.input
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

    os.makedirs(_args.output, exist_ok=True)
    log(f"主题: {_args.theme} | 模式: {_args.mode} | 文件数: {len(files)}")

    # 预解析所有贴图数据
    all_stickers = []
    for pf in files:
        name, copy, v_elems, s_kw, theme = parse_prompt_file(pf)
        all_stickers.append((name, copy, v_elems, s_kw, theme))

    # Dry-run 模式 - 仅打印计划不生成
    if _args.dry_run:
        log(f"===== DRY-RUN 计划（{len(all_stickers)} 张贴图）=====", "INFO")
        for i, (pf, (name, copy, v_elems, s_kw, theme)) in enumerate(zip(files, all_stickers)):
            t = theme or _args.theme
            print(f"  [{i+1}/{len(all_stickers)}] {name}")
            print(f"       文件: {pf}")
            print(f"       主题: {t}")
            print(f"       关键词: {s_kw}")
            print(f"       视觉元素: {v_elems[:3]}{'...' if len(v_elems) > 3 else ''}")
        print(f"  输出目录: {_args.output}")
        print(f"  生成模式: {_args.mode}")
        print(f"  Remotion 缓存: {REMOTION_CACHE_DIR}")
        log("===== DRY-RUN 完成，未生成任何文件 =====", "INFO")
        return

    # 建立 Remotion 项目
    input_abs    = os.path.abspath(_args.input)
    project_root = os.path.dirname(input_abs) if os.path.basename(input_abs) == 'prompts' else input_abs
    project_dir  = os.path.join(project_root, "remotion-sticker")
    stickers_for_remotion = [(n, c, v) for n, c, v, _, _ in all_stickers]

    remotion_project_ready = False
    remotion_used          = False
    if _args.mode in ('auto', 'remotion'):
        ok, reason = _check_remotion_environment()
        if ok:
            try:
                project_dir = _get_or_create_remotion_project(
                    project_dir, stickers_for_remotion, _args.theme)
                remotion_project_ready = True
                log("Remotion 项目已建立（单项目多 Sequence）", "OK")
            except Exception as e:
                log(f"Remotion 项目创建失败: {e}", "WARN")
                remotion_project_ready = False
        else:
            log(f"Remotion 环境检查失败: {reason}", "WARN")

    ok_count   = 0
    fail_count = 0
    failures    = []   # 收集失败信息

    for idx, (pf, sticker_data) in enumerate(zip(files, all_stickers)):
        name, copy, v_elems, s_kw, theme = sticker_data
        ext = '.gif' if remotion_project_ready else '.png'
        out = os.path.join(_args.output, os.path.basename(pf).replace('.md', ext))

        mode = _args.mode
        success = False
        generated_ext = '.png'

        # 阶段一：AI
        if mode in ('auto', 'ai'):
            try:
                generate_ai_image(name, copy, s_kw, theme, out)
                success = True
                generated_ext = '.png'
            except Exception as e:
                log(f"[AI] {name} 失败: {e}", "WARN")
                if mode == 'ai':
                    fail_count += 1
                    failures.append((name, str(e)))
                    if not _args.continue_on_error:
                        break
                    continue

        # 阶段二：Remotion
        if not success and mode in ('auto', 'remotion') and remotion_project_ready:
            log("[Remotion] 正在生成 GIF（单一项目 Sequence 架构）", "INFO")
            try:
                generate_remotion_gif(
                    name, copy, v_elems, theme, out,
                    idx, len(all_stickers), project_dir)
                success = True
                generated_ext = '.gif'
                remotion_used = True
            except Exception as e:
                err_str = str(e)
                log(f"[Remotion] {name} 失败: {err_str[:120]}", "WARN")
                fail_count += 1
                failures.append((name, err_str))
                if not _args.continue_on_error:
                    break
                continue

        if success:
            ok_count += 1
            print(f"✓ {name} ({generated_ext})")
        else:
            fail_count += 1
            failures.append((name, "未知错误"))

    print(f"\n✅ {ok_count}/{len(files)} 张贴图生成完成")
    print(f"📦 {_args.output}")
    if remotion_used:
        print(f"🔧 Remotion 项目（保留用于后续调整）: {project_dir}")
    if not _args.debug_remotion and os.path.exists(os.path.join(project_dir, "debug")):
        import shutil
        shutil.rmtree(os.path.join(project_dir, "debug"))
        log("[调试] 已清理 debug 目录（--debug-remotion 未指定）", "INFO")

    if failures:
        print(f"\n⚠️  失败 {fail_count} 张:")
        for name, err in failures:
            print(f"  ✗ {name}: {err[:80]}")
        if not _args.continue_on_error:
            print("\n提示：使用 --continue-on-error 可跳过失败贴图继续处理")

if __name__ == '__main__':
    main()
