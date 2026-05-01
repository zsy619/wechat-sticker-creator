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

# ── elem_fns（绘制函数，仅 PIL 模式使用）────────────────────
# 这些是纯符号/复杂几何绘制，不走 emoji 渲染路径

from PIL import ImageDraw, ImageFont

def _get_font(size=60):
    """字体加载（延迟导入避免顶import）"""
    import os
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/seguiemj.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default(size)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def build_elem_fns(draw, cx, cy, primary, secondary, get_font_fn=_get_font):
    """
    返回 elem_fns 字典，供 pil_fallback 使用。
    参数：draw (ImageDraw), cx, cy (中心点), primary/secondary (RGB元组), get_font_fn
    """
    return {
        # ── 几何绘制元素 ──────────────────────────────────
        'brain': lambda: draw.ellipse([cx-150, cy-150, cx+150, cy+150], fill=primary + (80,)),
        'neural_network': lambda: [
            draw.ellipse([cx-200+nx*80, cy-100+ny*60, cx-200+nx*80+24, cy-100+ny*60+24],
              fill=primary+(180,) if (nx+ny)%2==0 else secondary+(180,))
             for nx in range(6) for ny in range(4)
        ],
        'terminal': lambda: draw.rectangle([cx-300, cy-175, cx+300, cy+175], fill=(15,15,28,255), outline=primary+(200,), width=2),
        'math_canvas': lambda: draw.rectangle([cx-380, cy-250, cx+380, cy+250], fill=(10,10,10,255)),
        'ai_chip': lambda: draw.rectangle([cx-120, cy-120, cx+120, cy+120], fill=primary+(60,), outline=primary+(200,), width=3),
        'spotlight': lambda: (
            draw.ellipse([cx-200, cy-250, cx+200, cy+250], fill=(255,255,200,25)),
            draw.ellipse([cx-100, cy-150, cx+100, cy+150], fill=(255,255,200,40)),
        ),
        'network_node': lambda: [
            draw.ellipse([cx-180+nx*90, cy-90+ny*70, cx-180+nx*90+20, cy-90+ny*70+20],
              fill=primary+(200,))
             for nx in range(5) for ny in range(3)
        ],
        'button': lambda: draw.rectangle([cx-150, cy-60, cx+150, cy+60], fill=primary+(200,), outline=primary+(255,), width=3),
        # ── 符号/文本绘制元素 ──────────────────────────────
        'lightning': lambda: draw.text((cx-50, cy-80), "⚡", fill=(255,255,255,255), font=get_font_fn(80)),
        'heart': lambda: draw.text((cx-60, cy-60), "❤", fill=(255,60,90,255), font=get_font_fn(80)),
        'equals_sign': lambda: draw.text((cx-50, cy-50), "=", fill=(255,255,255,255), font=get_font_fn(80)),
        'question_mark': lambda: draw.text((cx-30, cy-40), "?", fill=primary+(255,), font=get_font_fn(80)),
        'eraser': lambda: draw.text((cx-40, cy-40), "🧹", fill=(200,150,100,255), font=get_font_fn(60)),
        'checkmark': lambda: draw.text((cx-40, cy-40), "✓", fill=(0,255,136,255), font=get_font_fn(80)),
        # ── 复杂绘制元素 ──────────────────────────────────
        'code': lambda: (
            draw.rectangle([cx-300, cy-175, cx+300, cy+175], fill=(15,15,28,255), outline=primary+(200,), width=2),
            draw.text((cx-240, cy-100), ">>>", fill=(0,255,136,255), font=get_font_fn(48)),
            draw.text((cx-240, cy-40), "def f(x):", fill=(0,200,255,255), font=get_font_fn(40)),
            draw.text((cx-240, cy+20), "    return x", fill=(150,150,150,255), font=get_font_fn(36)),
        ),
        'algorithm': lambda: (
            draw.rectangle([cx-260, cy-200, cx-60, cy-120], fill=primary+(60,), outline=primary+(200,), width=2),
            draw.rectangle([cx-60, cy-200, cx+140, cy-120], fill=secondary+(60,), outline=secondary+(200,), width=2),
            draw.rectangle([cx-160, cy-60, cx+40, cy+20], fill=primary+(60,), outline=primary+(200,), width=2),
            draw.text((cx-200, cy-170), "IN", fill=(255,255,255,255), font=get_font_fn(32)),
            draw.text((cx-10, cy-170), "PROC", fill=(255,255,255,255), font=get_font_fn(32)),
            draw.text((cx-120, cy-30), "OUT", fill=(255,255,255,255), font=get_font_fn(32)),
        ),
        'function': lambda: draw.text((cx-200, cy-40), "ƒ(x) =", fill=primary+(255,), font=get_font_fn(72)),
        'variable': lambda: (
            draw.text((cx-120, cy-40), "x =", fill=primary+(255,), font=get_font_fn(72)),
            draw.text((cx+20, cy-30), "???", fill=secondary+(255,), font=get_font_fn(56)),
        ),
        'bio': lambda: [
            (
                draw.ellipse([cx-160+ny*40-8, cy-120+ny*30-8, cx-160+ny*40+8, cy-120+ny*30+8], fill=primary+(180,)),
                draw.ellipse([cx+160-ny*40-8, cy-120+ny*30-8, cx+160-ny*40+8, cy-120+ny*30+8], fill=secondary+(180,)),
                draw.line([cx-160+ny*40, cy-120+ny*30, cx+160-ny*40, cy-120+ny*30], fill=primary+(80,), width=2),
            ) for ny in range(9)
        ],
        'secret': lambda: (
            draw.text((cx-140, cy-50), "***", fill=(255,215,0,255), font=get_font_fn(80)),
            draw.text((cx-200, cy+50), "CLASSIFIED", fill=(255,100,100,255), font=get_font_fn(28)),
        ),
    }


def validate_key(key):
    """校验单个 key 是否在词汇表中"""
    return key in VOCABULARY


def filter_valid_keys(keys):
    """过滤出合法的 key，返回 (valid_list, invalid_list)"""
    valid = [k for k in keys if k in VOCABULARY]
    invalid = [k for k in keys if k not in VOCABULARY]
    return valid, invalid
