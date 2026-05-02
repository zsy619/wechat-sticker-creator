#!/usr/bin/env python3
"""
_vocab.py - 微信贴图技能共享词汇表（单一数据源）

所有脚本必须从此模块导入 VOCABULARY，禁止内嵌副本。
导入方式：from _vocab import VOCABULARY, THEMES

更新词汇表时，只需修改本文件。
"""

# ── 标准词汇表（prompts-format.md 同步）─────────────────────
# 共 13 分类，约 120 个 key（包含英文 key + 中文别名）

VOCABULARY = {
    # ── 核心 AI/技术 ──────────────────────────────────────
    "brain", "neural_network", "terminal", "lightning", "ai_chip", "spotlight",
    "network_node", "button", "code", "algorithm", "function", "variable",
    "debug", "deploy", "cpu", "server", "database", "cloud", "data",
    "ai大脑", "ai计算", "神经网络", "终端窗口", "闪电", "等号", "问号",
    "橡皮擦", "对勾", "画布", "芯片", "光晕", "网络节点", "链接", "按钮",

    # ── 情感/反应 ─────────────────────────────────────────
    "heart", "thumbs_up", "clap", "pray", "muscle", "thinking", "eyes",
    "trophy", "medal", "crown", "star", "fire", "hundred",
    "laugh", "cry", "angry", "cool", "shy", "sleeping",
    "红心", "点赞", "鼓掌", "祈祷", "加油", "思考", "围观",
    "奖杯", "奖牌", "王冠", "星星", "火", "100分",

    # ── 物品/工具 ─────────────────────────────────────────
    "rocket", "alarm", "bell", "megaphone", "wrench", "hammer",
    "scissors", "pencil", "book", "lightbulb", "envelope", "gift",
    "tada", "balloon", "confetti",
    "火箭", "闹钟", "铃铛", "广播", "扳手", "锤子", "剪刀", "铅笔", "书本", "灯泡", "信封", "礼物",

    # ── 食物/饮料 ─────────────────────────────────────────
    "coffee", "tea", "beer", "cocktail", "wine",
    "pizza", "rice", "fruit", "cake", "cookie", "bread",
    "咖啡", "茶", "啤酒", "鸡尾酒", "葡萄酒", "披萨", "米饭", "水果", "蛋糕", "饼干", "面包",

    # ── 办公/效率 ─────────────────────────────────────────
    "phone", "camera", "clipboard", "chart", "calendar",
    "key", "lock", "folder", "file", "email", "call",
    "microphone", "video", "tv", "clock", "hourglass",
    "pen", "ruler", "paperclip", "stamp", "inbox", "outbox",
    "手机", "相机", "剪贴板", "图表", "日历", "钥匙", "锁", "文件夹", "文件", "邮件", "电话",
    "麦克风", "视频", "电视", "计时器", "沙漏", "笔", "直尺", "回形针", "邮票", "收件箱", "发件箱",

    # ── 自然/科学 ─────────────────────────────────────────
    "earth", "moon", "sun", "rainbow", "snowflake", "wave", "anchor",
    "airplane", "car", "bicycle", "map", "compass",
    "flag", "satellite", "telescope", "microscope",
    "地球", "月亮", "太阳", "彩虹", "雪花", "海浪", "锚",
    "飞机", "汽车", "自行车", "地图", "指南针",
    "旗帜", "卫星", "望远镜", "显微镜",

    # ── 心情/状态 ─────────────────────────────────────────
    "money", "gem", "love_letter", "warning", "no_entry", "busy", "free", "secret",
    "钱", "宝石", "情书", "警告", "禁止", "忙", "免费", "秘密",

    # ── 创意/兴趣 ─────────────────────────────────────────
    "goal", "puzzle", "music", "headphones", "sound", "mute",
    "eye", "ear", "nose", "footprints",
    "目标", "拼图", "音乐", "耳机", "声音", "静音", "眼睛", "耳朵", "鼻子", "脚印",

    # ── 健康/医疗 ─────────────────────────────────────────
    "bone", "microbe", "pill", "syringe", "thermometer",
    "骨头", "微生物", "药", "注射", "体温计",

    # ── 工业/科学符号 ──────────────────────────────────────
    "magnet", "gear", "atom", "dna", "biohazard", "radioactive", "bio",
    "磁铁", "齿轮", "原子", "DNA", "生物危害", "辐射", "生态",

    # ── 植物/自然 ─────────────────────────────────────────
    "four_leaf", "maple", "cherry", "tulip", "rose", "hibiscus", "shell", "feather",
    "四叶草", "枫叶", "樱花", "郁金香", "玫瑰", "木芙蓉", "贝壳", "羽毛",

    # ── 装饰/特殊 ─────────────────────────────────────────
    "sparkle", "diamond", "fleur", "comet",
    "闪光", "钻石", "百合", "彗星",

    # ── 特殊符号（纯符号，无 emoji 渲染）───────────────────
    "equals_sign", "question_mark", "eraser", "checkmark",
    "math_canvas", "robot",
}

# ── emoji 映射（所有 key → emoji 字符）───────────────────────
# 仅包含有明确 emoji 对应的 key；纯符号（equals_sign 等）不在此表中

EMOJI_MAP = {
    # 核心 AI/技术
    "brain": "🧠", "ai大脑": "🧠", "ai计算": "🧠",
    "神经网络": "🧠", "neural_network": "🧠",
    "terminal": "💻", "终端窗口": "💻",
    "lightning": "⚡", "闪电": "⚡", "zap": "⚡",
    "ai_chip": "🤖", "芯片": "🤖", "robot": "🤖",
    "spotlight": "🔦", "光晕": "🔦",
    "network_node": "🔗", "网络节点": "🔗", "link": "🔗",
    "button": "🔘", "按钮": "🔘",
    "code": "💻", "cpu": "🖥️", "server": "🗄️",
    "database": "🗃️", "cloud": "☁️", "data": "📊",
    "algorithm": "🔣",
    "function": "ƒ",
    "variable": "x",
    "debug": "🐛", "deploy": "🚀",
    # 情感/反应
    "heart": "❤", "红心": "❤",
    "thumbs_up": "👍", "clap": "👏",
    "pray": "🙏", "muscle": "💪",
    "thinking": "🤔", "eyes": "👀",
    "trophy": "🏆", "medal": "🏅", "crown": "👑",
    "star": "⭐", "fire": "🔥", "hundred": "💯",
    "laugh": "😂", "cry": "😭", "angry": "😡",
    "cool": "😎", "shy": "😳", "sleeping": "😴",
    # 物品/工具
    "rocket": "🚀", "alarm": "⏰", "bell": "🔔",
    "megaphone": "📢", "wrench": "🔧", "hammer": "🔨",
    "scissors": "✂️", "pencil": "✏️", "book": "📖",
    "lightbulb": "💡", "bulb": "💡",
    "envelope": "✉️", "gift": "🎁",
    "tada": "🎉", "balloon": "🎈", "confetti": "🎊",
    # 食物/饮料
    "coffee": "☕", "tea": "🍵", "beer": "🍺",
    "cocktail": "🍸", "wine": "🍷",
    "pizza": "🍕", "rice": "🍚", "fruit": "🍎",
    "cake": "🎂", "cookie": "🍪", "bread": "🍞",
    # 办公/效率
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
    # 自然/科学
    "earth": "🌏", "moon": "🌙", "sun": "☀️",
    "rainbow": "🌈", "snowflake": "❄️",
    "wave": "🌊", "anchor": "⚓",
    "airplane": "✈️", "car": "🚗", "bicycle": "🚲",
    "map": "🗺️", "compass": "🧭",
    "flag": "🚩", "satellite": "🛰️",
    "telescope": "🔭", "microscope": "🔬",
    # 心情/状态
    "money": "💰", "gem": "💎",
    "love_letter": "💌",
    "warning": "⚠️", "no_entry": "⛔",
    "busy": "🉐", "free": "🆓",
    "secret": "***",
    # 创意/兴趣
    "goal": "🎯", "puzzle": "🧩",
    "music": "🎵", "headphones": "🎧",
    "sound": "🔊", "mute": "🔇",
    "eye": "👁️", "ear": "👂", "nose": "👃",
    "footprints": "👣",
    # 健康/医疗
    "bone": "🦴", "microbe": "🦠",
    "pill": "💊", "syringe": "💉",
    "thermometer": "🌡️",
    # 工业/科学符号
    "magnet": "🧲", "gear": "⚙️",
    "atom": "⚛️", "dna": "🧬",
    "biohazard": "☣️", "radioactive": "☢️",
    "bio": "🌱",
    # 植物/自然
    "four_leaf": "🍀", "maple": "🍁",
    "cherry": "🌸", "tulip": "🌷",
    "rose": "🌹", "hibiscus": "🌺",
    "shell": "🐚", "feather": "🪶",
    # 装饰/特殊
    "sparkle": "✨", "diamond": "💠",
    "fleur": "⚜️", "comet": "☄️",
    # 特殊符号（纯文本，无 emoji）
    "equals_sign": "＝", "等号": "＝",
    "question_mark": "？", "问号": "？",
    "eraser": "🧹", "橡皮擦": "🧹",
    "checkmark": "✓", "对勾": "✓",
    "math_canvas": "📐", "canvas": "📐", "画布": "📐",
}

# ── 主题配色 ──────────────────────────────────────────────

THEMES = {
    "cyberpunk":  {"primary": "#00FFFF", "secondary": "#FF00FF", "bg": "#0D0D1A", "text": "#FFFFFF", "accent": "#00FF88"},
    "kawaii":     {"primary": "#FF69B4", "secondary": "#FFB6C1", "bg": "#FFF0F5", "text": "#4A4A4A", "accent": "#FF1493"},
    "neon":       {"primary": "#FF00FF", "secondary": "#00FFFF", "bg": "#1A0033", "text": "#FFFFFF", "accent": "#FF69B4"},
    "retro":      {"primary": "#FFD700", "secondary": "#FF6B35", "bg": "#2D1B00", "text": "#FFFFFF", "accent": "#FF4500"},
    "hand-drawn": {"primary": "#8B4513", "secondary": "#D2691E", "bg": "#FFF8DC", "text": "#4A4A4A", "accent": "#CD853F"},
    "minimal":    {"primary": "#212529", "secondary": "#495057", "bg": "#F8F9FA", "text": "#212529", "accent": "#6C757D"},
    "meme":       {"primary": "#FF4500", "secondary": "#FFD700", "bg": "#1A1A1A", "text": "#FFFFFF", "accent": "#FF6347"},
}

def validate_key(key):
    """校验单个 key 是否在词汇表中"""
    return key in VOCABULARY


def filter_valid_keys(keys):
    """过滤出合法的 key，返回 (valid_list, invalid_list)"""
    valid = [k for k in keys if k in VOCABULARY]
    invalid = [k for k in keys if k not in VOCABULARY]
    return valid, invalid


# ── 字体（带缓存）────────────────────────────────────────────

_FONT_CACHE = {}   # {size: ImageFont}

FONT_PATHS = [
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


def get_font(size=60):
    """
    加载支持 emoji 的字体（带模块级缓存）。
    依次尝试 FONT_PATHS 中的路径，返回第一个可用字体。
    """
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    from PIL import ImageFont
    import os
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                _FONT_CACHE[size] = font
                return font
            except Exception:
                continue
    font = ImageFont.load_default(size)
    _FONT_CACHE[size] = font
    return font


# ── 解析 ───────────────────────────────────────────────────

def _parse_list(s):
    """Parse a simple unquoted comma-separated list: [a, b, c]"""
    s = s.strip()
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1]
    return [x.strip() for x in s.split(',') if x.strip()]


def parse_prompt_file(path):
    """
    解析 prompts/*.md，返回 (name, copy, visual_elements, style_keyword, theme)
    统一实现，所有脚本共享。
    """
    with open(path) as f:
        content = f.read()
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
    name = front.get('name', os.path.basename(path).replace('.md', ''))
    copy = front.get('copy', '')
    try:
        visual_elements = _parse_list(front.get('visual_elements', '[]'))
    except:
        visual_elements = []
    try:
        style_keyword = _parse_list(front.get('style_keyword', '[]'))
    except:
        style_keyword = []
    theme = front.get('theme', 'cyberpunk')
    return name, copy, visual_elements, style_keyword, theme
