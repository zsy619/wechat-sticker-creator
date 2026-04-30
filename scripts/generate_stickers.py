#!/usr/bin/env python3
"""
generate_stickers.py - 微信表情包 PIL 生成器

【核心设计】: 通用视觉词汇表驱动
- prompts/*.md 中的 visual_elements 字段直接驱动绘制
- 词汇表中的每个元素对应一个 draw_element() 函数
- 新项目无需编写代码，只需要在 prompts 中描述 visual_elements

支持7种风格: cyberpunk / kawaii / hand-drawn / retro / neon / minimal / meme
内置词汇表: brain / neural_network / terminal / lightning / heart /
            math_canvas / equals_sign / question_mark / ai_chip /
            eraser / button / checkmark / command_k / spotlight / network_node
"""
import os, sys, math, glob, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_PATHS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
]
W, H = 1080, 1440
TEXT_MARGIN, TEXT_BOTTOM = 30, 30
CIRCULAR_THEMES = {"cyberpunk", "kawaii", "neon"}
CIRCLE_CX, CIRCLE_CY, CIRCLE_R = W//2, H//2, 500

THEMES = {
    "cyberpunk":  {"primary":"#00FFFF","secondary":"#FF00FF","glow":"#FF00FF","text":"#FFFFFF","bg":"#0D0D1A"},
    "kawaii":     {"primary":"#FF69B4","secondary":"#FFB6C1","glow":"#FF69B4","text":"#4A4A4A","bg":"#FFE4EC"},
    "hand-drawn": {"primary":"#8B4513","secondary":"#A0522D","glow":"#D2691E","text":"#2F2F2F","bg":"#FFF8DC"},
    "retro":      {"primary":"#FFD700","secondary":"#FF8C00","glow":"#FFD700","text":"#FFFFFF","bg":"#8B0000"},
    "neon":       {"primary":"#FF00FF","secondary":"#00FFFF","glow":"#FF00FF","text":"#FFFFFF","bg":"#0A0A0A"},
    "minimal":    {"primary":"#212529","secondary":"#6C757D","glow":"#0D6EFD","text":"#212529","bg":"#FFFFFF"},
    "meme":       {"primary":"#FF4500","secondary":"#FF6347","glow":"#DC143C","text":"#000000","bg":"#FFE135"},
}

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def get_font(sz):
    for fp in FONT_PATHS:
        if os.path.exists(fp):
            try: return ImageFont.truetype(fp, sz)
            except: pass
    return ImageFont.load_default()

def wrap_text(text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        bbox = ImageDraw.Draw(Image.new("RGB",(1,1))).textbbox((0,0),test,font=font)
        if bbox[2]-bbox[0] > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur = test
    if cur: lines.append(cur)
    return lines

def text_bottom_draw(draw, text, theme_key, font_sz=110):
    """文字渲染在底部（圆形内底部 or 画布底部），返回text_top位置"""
    theme = THEMES[theme_key]
    font = get_font(font_sz)
    max_w = W - 2 * TEXT_MARGIN
    lines = wrap_text(text, font, max_w)
    lh = int(font.size * 1.3)
    total_h = len(lines) * lh
    # 圆形主题: 文字底部以圆形内底边为基准; 其他: 以画布底边为基准
    tb = H - TEXT_BOTTOM  # 统一以画布底边为基准，距底边30px
    tt = tb - total_h
    # 文字发光效果（多层描边 → 辉光 → 文字）
    primary_c = hex_to_rgb(theme["primary"])
    text_c = hex_to_rgb(theme["text"])
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0,0), line, font=font)
        lw = bbox[2]-bbox[0]
        tx = (W-lw)//2
        ty = tt + i*lh
        # 第1层：外发光（主题色，大范围，低alpha）
        for offset in range(8, 0, -1):
            draw.text((tx, ty), line,
                      fill=primary_c + (max(10, 30 - offset*3),),
                      font=font)
        # 第2层：中发光（主题色，中等范围）
        for offset in range(4, 0, -1):
            draw.text((tx, ty), line,
                      fill=primary_c + (60 + offset*10,),
                      font=font)
        # 第3层：黑色描边阴影
        draw.text((tx+2,ty+2), line, fill=(0,0,0,140), font=font)
        # 第4层：白色主文字
        draw.text((tx,ty), line, fill=text_c+(255,), font=font)
    return tt, tb

def label_draw(draw, label_text, theme_key, tt, font_sz=22):
    """标签渲染在文字上方（tt为文字块顶部，标签置于其上方8px）"""
    theme = THEMES[theme_key]
    font = get_font(font_sz)
    bbox = draw.textbbox((0,0), label_text, font=font)
    lw = bbox[2]-bbox[0]
    draw.text(((W-lw)//2, tt - int(font_sz * 1.2) - 8), label_text,
              fill=hex_to_rgb(theme["primary"])+(140,), font=font)


# ═══════════════════════════════════════════════════════════
#  方案D · 场景构图系统（替代网格平铺）
#  核心设计：visual_elements 按角色分层合成，而非网格平铺
#  布局模式：BG（背景）→ FOCUS（主体）→ ACCENT（点缀）
# ═══════════════════════════════════════════════════════════

ROLE_BG     = "bg"
ROLE_FOCUS  = "focus"
ROLE_ACCENT = "accent"

# 单主体 | 双主体 | 三主体横排 | 弥散（无主体）
LAYOUT_PRESETS = {
    # single: FOCUS居中大区域，ACCENT在FOCUS外围8方位散布
    "single":  {"bg": {"zone": "full",       "layer": 0},
                  "focus": {"zone": "center",      "layer": 1},
                  "accent": {"zone": "outer_ring", "layer": 2}},
    # dual: FOCUS×2左右均分，ACCENT在中间缝隙和外围
    "dual":    {"bg": {"zone": "full",       "layer": 0},
                  "focus": {"zone": "left_right",  "layer": 1},
                  "accent": {"zone": "fill_gaps",   "layer": 2}},
    # triple: FOCUS×3横排，ACCENT在上下两端
    "triple":  {"bg": {"zone": "full",       "layer": 0},
                  "focus": {"zone": "center_row_3","layer": 1},
                  "accent": {"zone": "top_bottom",  "layer": 2}},
    # diffuse: 无主体，所有元素全场弥散（手写/随意风格）
    "diffuse": {"bg": {"zone": "full",       "layer": 0},
                  "accent": {"zone": "full_scatter","layer": 1}},
}

# 语义映射：关键词 → 场景角色
ELEMENT_SCENE_ROLE = {
    # ── FOCUS（主体，适合居中/放大，不适合散布）
    "brain": ROLE_FOCUS, "ai大脑": ROLE_FOCUS, "ai计算": ROLE_FOCUS,
    "神经网络": ROLE_FOCUS, "neural_network": ROLE_FOCUS,
    "terminal": ROLE_FOCUS, "终端窗口": ROLE_FOCUS,
    "math_canvas": ROLE_FOCUS, "数学画布": ROLE_FOCUS, "canvas": ROLE_FOCUS, "画布": ROLE_FOCUS,
    "ai_chip": ROLE_FOCUS, "芯片": ROLE_FOCUS,
    "equals_sign": ROLE_FOCUS, "等号": ROLE_FOCUS,
    "command_k": ROLE_FOCUS, "⌘k": ROLE_FOCUS, "cmd_k": ROLE_FOCUS,
    "lightning": ROLE_FOCUS, "闪电": ROLE_FOCUS,

    # ── ACCENT（点缀，适合小尺寸+散布，不适合放大）
    "heart": ROLE_ACCENT, "红心": ROLE_ACCENT,
    "question_mark": ROLE_ACCENT, "问号": ROLE_ACCENT,
    "checkmark": ROLE_ACCENT, "对勾": ROLE_ACCENT,
    "spotlight": ROLE_ACCENT, "光晕": ROLE_ACCENT,
    "network_node": ROLE_ACCENT, "节点": ROLE_ACCENT,
    "eraser": ROLE_ACCENT, "橡皮擦": ROLE_ACCENT,
    "button": ROLE_ACCENT, "按钮": ROLE_ACCENT,
    "数学公式": ROLE_ACCENT,  # 数学公式作为点缀（小符号散布）
    "ai图标": ROLE_ACCENT,    # 小AI图标作为点缀
    "手写识别框": ROLE_ACCENT,

    # ── BG（背景，适合全屏铺）
    "bg_gradient": ROLE_BG, "背景": ROLE_BG, "渐变背景": ROLE_BG,
}

def _layout_for_role(role, zone, cx, cy, area_w, area_h):
    """返回列表 [(x,y,w,h), ...] — 每个元素独立位置"""
    if role == ROLE_BG:
        return [(0, 0, W, H)]
    elif role == ROLE_FOCUS:
        if zone == "center":
            # 单主体：居中大区域（占80%宽度）
            return [(cx-area_w*0.4, cy-area_h*0.4, area_w*0.8, area_h*0.8)]
        elif zone == "left_right":
            # 双主体：左右均分，中间留隙
            w2 = area_w * 0.40
            return [
                (cx-area_w*0.45, cy, w2, area_h*0.72),
                (cx+area_w*0.05, cy, w2, area_h*0.72),
            ]
        elif zone == "center_row_3":
            # 三主体：横排三列
            w3 = area_w * 0.28
            return [
                (cx-area_w*0.44, cy, w3, area_h*0.72),
                (cx-w3*0.5, cy, w3, area_h*0.72),
                (cx+area_w*0.16, cy, w3, area_h*0.72),
            ]
    elif role == ROLE_ACCENT:
        if zone == "outer_ring":
            # 外围8方位（单主体的外围，保护中心主体）
            r = min(area_w, area_h) * 0.45
            angles = [30, 75, 120, 165, 210, 255, 300, 345]
            return [(cx+r*math.cos(math.radians(a)), cy+r*math.sin(math.radians(a)),
                     min(area_w,area_h)*0.2, min(area_w,area_h)*0.2)
                    for a in angles]
        elif zone == "fill_gaps":
            # 填补双主体缝隙 + 少量外围
            positions = []
            # 中间缝隙（2个元素）
            mid_y = cy - area_h*0.15
            for dx in [-area_w*0.08, area_w*0.08]:
                positions.append((cx+dx-area_w*0.1, mid_y, area_w*0.2, area_h*0.25))
            # 外围（4个元素）
            r = min(area_w, area_h) * 0.42
            for ang in [150, 210, 330, 30]:
                positions.append((cx+r*math.cos(math.radians(ang)),
                                  cy+r*math.sin(math.radians(ang)),
                                  area_w*0.15, area_h*0.18))
            return positions
        elif zone == "top_bottom":
            # 上下两端（3个主体的上下方）
            positions = []
            # 上方2个
            for dx in [-area_w*0.25, area_w*0.05]:
                positions.append((cx+dx, cy-area_h*0.38, area_w*0.2, area_h*0.22))
            # 下方2个
            for dx in [-area_w*0.05, area_w*0.25]:
                positions.append((cx+dx, cy+area_h*0.16, area_w*0.2, area_h*0.22))
            return positions
        elif zone == "full_scatter":
            # 全场弥散（无主体，所有元素均匀分布）
            angles = [0, 40, 80, 120, 160, 200, 240, 280, 320]
            r_base = min(area_w, area_h) * 0.35
            return [(cx+r_base*(0.6+i%3*0.3)*math.cos(math.radians(a)),
                     cy+r_base*(0.6+i%3*0.3)*math.sin(math.radians(a)),
                     area_w*(0.18+i%2*0.06), area_h*(0.18+i%2*0.06))
                    for i, a in enumerate(angles)]
    # fallback
    return [(cx-area_w*0.3, cy-area_h*0.3, area_w*0.6, area_h*0.6)]

def _compose_scene(draw, visual_elements, theme_key):
    """方案D核心：场景构图驱动绘制。
    - 角色分层：BG → FOCUS → ACCENT（按layer顺序合成）
    - 语义布局：FOCUS按预设分布，ACCENT独立位置弥散
    """
    theme = THEMES[theme_key]
    cx, cy = W//2, H//2-60
    area_w, area_h = W*0.8, H*0.6

    # ── 角色分组 ──
    bg_elems, focus_elems, accent_elems = [], [], []
    for elem in visual_elements:
        ec = elem.strip().lower()
        role = ELEMENT_SCENE_ROLE.get(ec)
        if role is None:
            for k, v in ELEMENT_SCENE_ROLE.items():
                if k in ec or ec in k: role = v; break
        if role == ROLE_BG:       bg_elems.append(ec)
        elif role == ROLE_FOCUS:  focus_elems.append(ec)
        elif role == ROLE_ACCENT: accent_elems.append(ec)
        else:                     focus_elems.append(ec)

    # ── 选定布局预设 ──
    n_focus = len(focus_elems)
    if accent_elems and n_focus == 0:
        preset_key = "diffuse"
    elif n_focus == 1:
        preset_key = "single"
    elif n_focus == 2:
        preset_key = "dual"
    else:
        preset_key = "triple"
    preset = LAYOUT_PRESETS[preset_key]

    # ── 绘制组 ──
    def draw_group(elems, role, zone):
        if not elems: return
        positions = _layout_for_role(role, zone, cx, cy, area_w, area_h)
        # 每个元素对应一个位置（位置数 >= 元素数）
        for i, elem in enumerate(elems):
            if i < len(positions):
                lx, ly, lw, lh = positions[i]
                fn = ELEMENT_VOCAB.get(elem)
                if fn: fn(draw, theme, lx+lw//2, ly+lh//2, lw, lh)

    # 按layer顺序合成
    if "bg"     in preset: draw_group(bg_elems,     ROLE_BG,     preset["bg"]["zone"])
    if "focus"  in preset: draw_group(focus_elems,  ROLE_FOCUS,  preset["focus"]["zone"])
    if "accent" in preset: draw_group(accent_elems, ROLE_ACCENT, preset["accent"]["zone"])

# ── 词汇表函数（每个元素一个绘制函数）──────────────────────

def _draw_brain(draw, theme, cx, cy, w, h):
    """AI大脑图标"""
    primary = hex_to_rgb(theme["primary"])
    secondary = hex_to_rgb(theme["secondary"])
    # 多层椭圆叠加
    for i, (r_ratio, bc) in enumerate([
        (0.9, (60,10,100)), (0.7,(40,5,80)), (0.5,(25,3,60))
    ]):
        rx = w * r_ratio * 0.5
        ry = rx * 0.75
        draw.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=bc+(255,))
    # 中心发光核心
    for i in range(8, 0, -1):
        draw.ellipse([cx-i*12, cy-i*12, cx+i*12, cy+i*12],
                      fill=primary+(max(5,20-i*2),))

def _draw_neural_network(draw, theme, cx, cy, w, h):
    """神经网络节点图"""
    primary = hex_to_rgb(theme["primary"])
    secondary = hex_to_rgb(theme["secondary"])
    # 预定义节点位置（相对偏移）
    offsets = [(-0.3,-0.25),(0.3,-0.25),(-0.45,0), (0,0),(0.45,0),(-0.3,0.25),(0.3,0.25)]
    nodes = [(cx+ox*w, cy+oy*h) for ox,oy in offsets]
    # 连线
    for i, (nx,ny) in enumerate(nodes):
        for j, (mx,my) in enumerate(nodes):
            if i < j and ((nx-mx)**2+(ny-my)**2)**0.5 < w*0.5:
                draw.line([(nx,ny),(mx,my)], fill=secondary+(60,), width=2)
    # 节点
    for nx, ny in nodes:
        for ring in range(3,0,-1):
            draw.ellipse([nx-ring*5, ny-ring*5, nx+ring*5, ny+ring*5],
                         fill=secondary+(30-ring*8,))
        draw.ellipse([nx-7,ny-7,nx+7,ny+7], fill=(255,255,255,200))
        draw.ellipse([nx-4,ny-4,nx+4,ny+4], fill=secondary+(200,))

def _draw_terminal(draw, theme, cx, cy, w, h):
    """终端窗口"""
    primary = hex_to_rgb(theme["primary"])
    win_w, win_h = int(w*0.95), int(h*0.85)
    tx, ty = cx - win_w//2, cy - win_h//2
    # 背景
    draw.rectangle([tx, ty, tx+win_w, ty+win_h], fill=(15,15,28,255))
    # 边框
    draw.rectangle([tx, ty, tx+win_w, ty+win_h],
                   outline=primary+(180,), width=2)
    # 标题栏
    title_h = int(win_h * 0.12)
    draw.rectangle([tx, ty, tx+win_w, ty+title_h], fill=(30,30,50,255))
    # 三个点
    for i, (px, col) in enumerate([(tx+16,(255,80,80,200)),(tx+36,(255,200,80,200)),(tx+56,(80,200,100,200))]):
        draw.ellipse([px-6,ty+title_h//2-6,px+6,ty+title_h//2+6], fill=col)
    # 光标闪烁条
    cursor_y = ty + title_h + int(win_h*0.15)
    draw.rectangle([tx+20, cursor_y, tx+60, cursor_y+20],
                   fill=primary+(180,))
    # 命令提示符
    cmd_y = ty + title_h + int(win_h*0.35)
    draw.text((tx+20, cmd_y), "~/ $",
              fill=(100,100,130,200), font=get_font(int(h*0.08)))

def _draw_lightning(draw, theme, cx, cy, w, h):
    """闪电符号"""
    primary = hex_to_rgb(theme["primary"])
    # 速度放射线
    for angle in range(0, 360, 10):
        rad = math.radians(angle)
        inner_r = w*0.15
        outer_r = w*0.48
        x1 = int(cx + inner_r*math.cos(rad))
        y1 = int(cy + inner_r*math.sin(rad))
        x2 = int(cx + outer_r*math.cos(rad))
        y2 = int(cy + outer_r*math.sin(rad))
        draw.line([(x1,y1),(x2,y2)], fill=primary+(40,), width=2)
    # 闪电 emoji
    font = get_font(int(min(w,h)*0.5))
    draw.text((cx-int(w*0.2), cy-int(h*0.25)), "⚡",
              fill=(255,255,255,255), font=font)

def _draw_heart(draw, theme, cx, cy, w, h):
    """红心"""
    heart_font = get_font(int(min(w,h)*0.7))
    draw.text((cx-int(w*0.25), cy-int(h*0.35)), "❤",
              fill=(255,60,90,255), font=heart_font)
    # 小漂浮爱心
    for ox, oy, sz in [(-w*0.4,-h*0.2,0.4), (w*0.35,-h*0.1,0.3), (w*0.4,h*0.2,0.35)]:
        draw.text((cx+ox-int(w*sz*0.25), cy+oy-int(h*sz*0.35)),
                  "❤", fill=(255,100,130,150), font=get_font(int(min(w,h)*sz*0.4)))

def _draw_math_canvas_vocab(draw, theme, cx, cy, w, h):
    """数学画布（黑色背景+手写公式）"""
    primary = hex_to_rgb(theme["primary"])
    # 黑色画布
    canvas_w, canvas_h = int(w*0.9), int(h*0.8)
    draw.rectangle([cx-canvas_w//2, cy-canvas_h//2,
                    cx+canvas_w//2, cy+canvas_h//2],
                   fill=(10,10,10,255))
    # 数学公式
    math_font = get_font(int(min(w,h)*0.18))
    eq_y = cy - int(h*0.15)
    for (sym, ox) in [("5",-w*0.2),("+",-w*0.08),("3",w*0.04),("=",w*0.16)]:
        col = (255,200,80,255) if sym == "=" else (255,255,255,255)
        draw.text((cx+ox-int(w*0.06), eq_y), sym, fill=col, font=math_font)
    # 画笔图标
    draw.text((cx+int(w*0.28), cy-int(h*0.35)),
              "✏️", fill=(255,220,100,200), font=get_font(int(min(w,h)*0.15)))

def _draw_equals_sign(draw, theme, cx, cy, w, h):
    """等号（手写风格）"""
    primary = hex_to_rgb(theme["primary"])
    eq_font = get_font(int(min(w,h)*0.6))
    draw.text((cx-int(w*0.2), cy-int(h*0.2)),
              "=", fill=(255,255,255,255), font=eq_font)
    # 上下横线手写感
    line_y1 = cy - int(h*0.12)
    line_y2 = cy + int(h*0.05)
    for ly in [line_y1, line_y2]:
        draw.line([(cx-int(w*0.3), ly),(cx+int(w*0.05), ly)],
                  fill=(255,255,255,200), width=6)

def _draw_question_mark(draw, theme, cx, cy, w, h):
    """问号气泡"""
    primary = hex_to_rgb(theme["primary"])
    # 气泡背景
    for i in range(5, 0, -1):
        draw.ellipse([cx-w*0.4-i*3, cy-h*0.35-i*3,
                      cx+w*0.4+i*3, cy+h*0.35+i*3],
                     fill=primary+(12-i*2,))
    draw.ellipse([cx-w*0.4, cy-h*0.35, cx+w*0.4, cy+h*0.35],
                 fill=(40,30,80,255), outline=primary+(200,), width=2)
    # 问号
    q_font = get_font(int(min(w,h)*0.5))
    draw.text((cx-int(w*0.12), cy-int(h*0.2)),
              "?", fill=primary+(255,), font=q_font)
    # 等待省略号
    for i, dx in enumerate([-w*0.15, 0, w*0.15]):
        draw.ellipse([cx+dx-w*0.04, cy+h*0.2, cx+dx+w*0.04, cy+h*0.2+int(h*0.1)],
                     fill=primary+(max(80,255-i*60),))

def _draw_ai_chip(draw, theme, cx, cy, w, h):
    """AI芯片图标"""
    primary = hex_to_rgb(theme["primary"])
    cs = int(min(w,h)*0.35)
    # 芯片外框
    draw.rectangle([cx-cs, cy-cs, cx+cs, cy+cs],
                   fill=(15,15,25,255), outline=primary+(200,), width=2)
    # 内部引脚线
    for i in range(-2, 3):
        draw.line([(cx-w*0.2, cy+i*cs*0.4),(cx+w*0.2, cy+i*cs*0.4)],
                  fill=primary+(80,), width=1)
    # AI 文字
    draw.text((cx-int(w*0.12), cy-int(h*0.15)),
              "AI", fill=primary+(255,), font=get_font(int(min(w,h)*0.2)))

def _draw_eraser(draw, theme, cx, cy, w, h):
    """橡皮擦"""
    primary = hex_to_rgb(theme["primary"])
    ew, eh = int(w*0.6), int(h*0.3)
    draw.rectangle([cx-ew//2, cy-eh//2, cx+ew//2, cy+eh//2],
                   fill=(220,180,140,255), outline=(100,80,60,255), width=2)
    draw.line([(cx-ew//2+8, cy),(cx+ew//2-8, cy)],
              fill=(200,160,120,200), width=2)
    # 擦除轨迹点
    for i, (ox,oy) in enumerate([(-w*0.3,0),(0,0),(w*0.2,h*0.15)]):
        alpha = 180 - i*50
        draw.ellipse([cx+ox-w*0.08, cy+oy-h*0.08,
                      cx+ox+w*0.08, cy+oy+h*0.08],
                     fill=primary+(max(30,alpha),))

def _draw_button(draw, theme, cx, cy, w, h):
    """按钮（清空/确认）"""
    primary = hex_to_rgb(theme["primary"])
    bw, bh = int(w*0.5), int(h*0.3)
    draw.rounded_rectangle([cx-bw//2, cy-bh//2, cx+bw//2, cy+bh//2],
                            8, fill=(60,20,20,255), outline=(255,80,80,200,), width=2)
    draw.text((cx-int(w*0.12), cy-int(h*0.1)),
              "清空", fill=(255,100,100,220,), font=get_font(int(min(w,h)*0.15)))

def _draw_checkmark(draw, theme, cx, cy, w, h):
    """对勾/成功标记"""
    primary = hex_to_rgb(theme["primary"])
    # 发光
    for i in range(5, 0, -1):
        draw.ellipse([cx-w*0.3-i*3, cy-h*0.3-i*3,
                      cx+w*0.3+i*3, cy+h*0.3+i*3],
                     fill=(0,255,136,15-i*2,))
    draw.text((cx-int(w*0.2), cy-int(h*0.25)),
              "✓", fill=(0,255,136,255), font=get_font(int(min(w,h)*0.5)))

def _draw_command_k(draw, theme, cx, cy, w, h):
    """⌘K 按键"""
    primary = hex_to_rgb(theme["primary"])
    kr = int(min(w,h)*0.35)
    # 外发光
    for i in range(6, 0, -1):
        draw.ellipse([cx-kr-i*4, cy-kr-i*4, cx+kr+i*4, cy+kr+i*4],
                     fill=primary+(12-i,))
    draw.ellipse([cx-kr, cy-kr, cx+kr, cy+kr],
                  fill=(20,20,35,255), outline=primary+(255,), width=3)
    draw.text((cx-int(w*0.22), cy-int(h*0.28)),
              "⌘", fill=primary+(255,), font=get_font(int(min(w,h)*0.35)))
    draw.text((cx+int(w*0.05), cy-int(h*0.2)),
              "K", fill=primary+(255,), font=get_font(int(min(w,h)*0.25)))

def _draw_spotlight(draw, theme, cx, cy, w, h):
    """聚光灯/光晕效果"""
    primary = hex_to_rgb(theme["primary"])
    for i in range(10, 0, -1):
        draw.ellipse([cx-w*0.5-i*w*0.05, cy-h*0.5-i*h*0.05,
                      cx+w*0.5+i*w*0.05, cy+h*0.5+i*h*0.05],
                     fill=primary+(max(2,18-i*2),))

def _draw_network_node(draw, theme, cx, cy, w, h):
    """网络节点（可连接）"""
    primary = hex_to_rgb(theme["primary"])
    secondary = hex_to_rgb(theme["secondary"])
    for ring in range(4, 0, -1):
        draw.ellipse([cx-ring*6, cy-ring*6, cx+ring*6, cy+ring*6],
                     fill=secondary+(30-ring*6,))
    draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill=(255,255,255,220))
    draw.ellipse([cx-4, cy-4, cx+4, cy+4], fill=primary+(220,))

# ── 词汇表注册表 ───────────────────────────────────────────
# key: prompt中的visual_elements关键词 → 对应绘制函数

ELEMENT_VOCAB = {
    "brain":            _draw_brain,
    "ai大脑":          _draw_brain,
    "神经网络":        _draw_neural_network,
    "neural_network":  _draw_neural_network,
    "terminal":        _draw_terminal,
    "终端窗口":        _draw_terminal,
    "lightning":        _draw_lightning,
    "闪电":            _draw_lightning,
    "heart":           _draw_heart,
    "红心":            _draw_heart,
    "数学画布":        _draw_math_canvas_vocab,
    "canvas":          _draw_math_canvas_vocab,
    "画布":            _draw_math_canvas_vocab,
    "equals_sign":     _draw_equals_sign,
    "等号":            _draw_equals_sign,
    "question_mark":   _draw_question_mark,
    "问号":            _draw_question_mark,
    "ai_chip":         _draw_ai_chip,
    "芯片":            _draw_ai_chip,
    "eraser":          _draw_eraser,
    "橡皮擦":          _draw_eraser,
    "button":          _draw_button,
    "按钮":            _draw_button,
    "checkmark":       _draw_checkmark,
    "对勾":            _draw_checkmark,
    "command_k":       _draw_command_k,
    "⌘k":             _draw_command_k,
    "cmd_k":           _draw_command_k,
    "spotlight":       _draw_spotlight,
    "光晕":            _draw_spotlight,
    "network_node":    _draw_network_node,
    "节点":            _draw_network_node,
    "ai计算":          _draw_brain,
    "智能":            _draw_brain,
    "数学公式":        _draw_math_canvas_vocab,
    "ai图标":          _draw_ai_chip,
    "刷新图标":        _draw_spotlight,
    "刷新":            _draw_spotlight,
    "重置符号":        _draw_eraser,
    "手写识别框":      _draw_math_canvas_vocab,
}

# ── 主入口 ─────────────────────────────────────────────────

def draw_visual(draw, visual_elements, name, theme_key):
    """
    通用视觉绘制入口（词汇表优先 + name回退）。
    visual_elements: list of element names from prompt frontmatter
    name: sticker name (used as fallback dispatch key)
    theme_key: current theme key (cyberpunk/kawaii/etc.)

    工作流程:
    1. 解析 visual_elements 列表，在词汇表中查找匹配
    2. 若找到≥1个匹配元素 → 词汇表驱动绘制
    3. 若无匹配 → 回退到 name-based 专用函数绘制
    """
    theme = THEMES[theme_key]
    cx, cy = W // 2, H // 2 - 60
    area_w, area_h = W * 0.85, H * 0.65

    # ── 步骤1+2: 词汇表匹配 ──
    registered = []
    for elem in visual_elements:
        elem_clean = elem.strip().lower()
        if elem_clean in ELEMENT_VOCAB:
            registered.append(elem_clean)
        else:
            for vocab_key in ELEMENT_VOCAB:
                if vocab_key in elem_clean or elem_clean in vocab_key:
                    registered.append(vocab_key)
                    break

    # 去重保持顺序
    seen = set()
    unique_elems = []
    for e in registered:
        if e not in seen:
            seen.add(e); unique_elems.append(e)

    # ── 步骤3: 场景构图驱动（方案D）或回退到name ──
    if unique_elems:
        # 方案D场景构图：角色分层 + 语义布局 + 独立位置
        _compose_scene(draw, unique_elems, theme_key)
    else:
        # 回退：name-based dispatch（兼容旧项目）
        _name_dispatch(draw, name, theme_key)

# ── Name回退分发器（兼容旧项目）────────────────────────
def _name_dispatch(draw, name, theme_key):
    """Name-based fallback dispatch（词汇表无匹配时启用）"""
    dispatch = {
        "AI补全":     _draw_terminal_autocomplete,
        "命令面板":   _draw_cmd_palette,
        "闪电速度":   _draw_lightning_speed,
        "智能建议":   _draw_smart_suggest,
        "团队协作":   _draw_team_collab,
        "Warp粉丝":   _draw_warp_fan,
        "画布手写":   _draw_math_canvas,
        "AI计算":     _draw_ai_math,
        "等号求解":   _draw_equals_wait,
        "MathNotes":  _draw_math_notes,
        "清空重写":   _draw_eraser,
        "答案揭晓":   _draw_answer_reveal,
    }
    fn = dispatch.get(name)
    if fn:
        fn(draw, theme_key)


# ── 01: AI补全 ── 代码补全下拉框（升级版）───────────────
def _draw_terminal_autocomplete(draw, theme_key):
    theme = THEMES[theme_key]
    cx, cy = W//2, H//2 - 60
    primary = hex_to_rgb(theme["primary"])
    secondary = hex_to_rgb(theme["secondary"])

    # 终端窗口背景
    win_h, win_w = 360, 700
    draw.rectangle([cx-win_w//2, cy-win_h//2, cx+win_w//2, cy+win_h//2],
                   fill=(20,20,30,255), outline=primary+(200,), width=3)

    # 窗口标题栏
    title_h = 40
    draw.rectangle([cx-win_w//2, cy-win_h//2, cx+win_w//2, cy-win_h//2+title_h],
                   fill=(40,40,55,255))
    # 三个窗口按钮
    for bx, col in [(cx-win_w//2+18, (255,100,100,200)),
                    (cx-win_w//2+46, (255,200,80,200)),
                    (cx-win_w//2+74, (80,200,100,200))]:
        draw.ellipse([bx-8, cy-win_h//2+10, bx+8, cy-win_h//2+26], fill=col)

    # 代码行（灰色）
    code_font = get_font(32)
    codes = ["func fetchData() {", "  let result = await api", "  return process(result)"]
    for i, code in enumerate(codes):
        draw.text((cx-win_w//2+30, cy-win_h//2+title_h+20+i*50),
                  code, fill=(120,120,140,255), font=code_font)

    # 补全高亮行（青色）
    sel_y = cy-win_h//2+title_h+20+3*50
    draw.rectangle([cx-win_w//2+20, sel_y, cx+win_w//2-20, sel_y+45],
                   fill=(0,255,255,30), outline=primary+(200,), width=2)
    draw.text((cx-win_w//2+30, sel_y+5), "→ api.getAIComplete()",
              fill=primary+(255,), font=code_font)

    # Tab键图标
    tab_x, tab_y = cx+win_w//2-110, sel_y+10
    draw.rounded_rectangle([tab_x, tab_y, tab_x+90, tab_y+30], 5,
                           fill=(60,60,80,255), outline=primary+(200,), width=2)
    draw.text((tab_x+12, tab_y+3), "Tab▸", fill=primary+(255,), font=get_font(22))

    # 底部状态栏
    stat_y = cy+win_h//2-40
    draw.rectangle([cx-win_w//2, stat_y, cx+win_w//2, cy+win_h//2],
                   fill=(30,30,45,255))
    draw.text((cx-win_w//2+20, stat_y+8),
              "Warp AI · 补全建议", fill=(0,255,255,150,), font=get_font(20))


# ── 02: 命令面板 ── ⌘K 按键 ───────────────────────────
def _draw_cmd_palette(draw, theme_key):
    theme = THEMES[theme_key]
    cx, cy = W//2, H//2 - 80
    primary = hex_to_rgb(theme["primary"])
    secondary = hex_to_rgb(theme["secondary"])

    # 搜索框背景
    box_w, box_h = 700, 120
    draw.rounded_rectangle([cx-box_w//2, cy-box_h//2, cx+box_w//2, cy+box_h//2],
                           16, fill=(15,15,25,255), outline=primary+(220,), width=3)

    # ⌘K 按键
    kx, ky = cx - 60, cy
    kr = 50
    # 外发光
    for i in range(6, 0, -1):
        draw.ellipse([kx-kr-i*6, ky-kr-i*6, kx+kr+i*6, ky+kr+i*6],
                     fill=primary+(15-i,))
    # 圆形按键
    draw.ellipse([kx-kr, ky-kr, kx+kr, ky+kr],
                  fill=(20,20,35,255), outline=primary+(255,), width=4)
    # ⌘ 符号
    draw.text((kx-28, ky-35), "⌘", fill=primary+(255,), font=get_font(70))
    draw.text((kx+10, ky-28), "K", fill=primary+(255,), font=get_font(55))

    # 搜索提示文字
    draw.text((cx+80, cy-15), "Search commands...",
              fill=(100,100,130,255), font=get_font(36))

    # 命令列表（模糊条）
    cmd_y = cy + box_h//2 + 30
    cmd_font = get_font(30)
    cmds = [
        ("git commit",       "#00FF88"),
        ("npm run dev",      "#FFD700"),
        ("docker build",     "#00FFFF"),
    ]
    for i, (cmd, col) in enumerate(cmds):
        by = cmd_y + i * 55
        draw.rectangle([cx-box_w//2+30, by, cx+box_w//2-30, by+48],
                       fill=(20,20,35,200), outline=(50,50,70,100), width=1)
        draw.text((cx-box_w//2+50, by+8), cmd, fill=hex_to_rgb(col)+(255,), font=cmd_font)


# ── 03: 闪电速度 ── 闪电 + 速度线 ─────────────────────
def _draw_lightning_speed(draw, theme_key):
    theme = THEMES[theme_key]
    cx, cy = W//2, H//2 - 80
    primary = hex_to_rgb(theme["primary"])

    # 速度放射线
    for angle in range(0, 360, 8):
        rad = math.radians(angle)
        inner_r = 80
        outer_r = 380
        # 随机长度变化
        var_r = outer_r + random.randint(-30, 30)
        x1 = int(cx + inner_r * math.cos(rad))
        y1 = int(cy + inner_r * math.sin(rad))
        x2 = int(cx + var_r * math.cos(rad))
        y2 = int(cy + var_r * math.sin(rad))
        alpha = random.randint(30, 120)
        draw.line([(x1,y1),(x2,y2)], fill=primary+(alpha,), width=2)

    # 内圈白色光晕
    for i in range(8, 0, -1):
        draw.ellipse([cx-80-i*10, cy-80-i*10, cx+80+i*10, cy+80+i*10],
                      fill=(255,255,255,max(1,20-i*2)))

    # 巨大闪电符号
    font = get_font(280)
    draw.text((cx-80, cy-100), "⚡", fill=(255,255,255,255), font=font)

    # 底部 ">" 光标闪烁
    cursor_font = get_font(80)
    draw.text((cx-30, cy+160), ">", fill=primary+(255,), font=cursor_font)
    # 青色下划线
    draw.line([(cx-20, cy+250),(cx+120, cy+250)], fill=primary+(200,), width=4)


# ── 04: 智能建议 ── AI大脑 + 神经网络 ─────────────────
def _draw_smart_suggest(draw, theme_key):
    theme = THEMES[theme_key]
    cx, cy = W//2, H//2 - 60
    primary = hex_to_rgb(theme["primary"])
    secondary = hex_to_rgb(theme["secondary"])

    # 抽象大脑轮廓（由多个椭圆组成）
    brain_color = (20, 10, 50, 255)
    for r in [160, 130, 100, 70]:
        draw.ellipse([cx-r, cy-r*0.8, cx+r, cy+r*0.8], fill=brain_color)

    # 神经网络连线
    nodes = [
        (cx-80, cy-60), (cx+80, cy-60),
        (cx-120, cy+20), (cx, cy), (cx+120, cy+20),
        (cx-60, cy+80), (cx+60, cy+80),
    ]
    for i, (nx, ny) in enumerate(nodes):
        for j, (mx, my) in enumerate(nodes):
            if i < j:
                dist = ((nx-mx)**2+(ny-my)**2)**0.5
                if dist < 200:
                    alpha = int(150 - dist * 0.5)
                    draw.line([(nx,ny),(mx,my)], fill=secondary+(max(30,alpha),), width=2)

    # 节点发光
    for nx, ny in nodes:
        for i in range(4, 0, -1):
            draw.ellipse([nx-15-i*3, ny-15-i*3, nx+15+i*3, ny+15+i*3],
                         fill=secondary+(30-i*5,))
        draw.ellipse([nx-12, ny-12, nx+12, ny+12], fill=(255,255,255,255))
        draw.ellipse([nx-6, ny-6, nx+6, ny+6], fill=secondary+(200,))

    # 中心AI核心发光
    for i in range(10, 0, -1):
        draw.ellipse([cx-i*12, cy-i*12, cx+i*12, cy+i*12],
                      fill=primary+(20-i,))

    # 终端建议条
    term_y = cy + 160
    draw.rounded_rectangle([cx-200, term_y, cx+200, term_y+50], 8,
                           fill=(10,10,25,255), outline=primary+(180,), width=2)
    draw.text((cx-180, term_y+10), "suggest: git commit -m",
               fill=primary+(255,), font=get_font(26))


# ── 05: 团队协作 ── 多终端窗口并排 ────────────────────
def _draw_team_collab(draw, theme_key):
    theme = THEMES[theme_key]
    primary = hex_to_rgb(theme["primary"])

    # 三个终端窗口
    wins = []
    for i, (user, cmd, color) in enumerate([
        ("Alice",  "git push",   "#FF6B6B"),
        ("Bob",    "npm test",   "#4ECDC4"),
        ("Carol",  "make build", "#FFE66D"),
    ]):
        wx = 140 + i * 300
        wy = 200
        ww, wh = 260, 320

        # 窗口
        draw.rectangle([wx, wy, wx+ww, wy+wh], fill=(15,15,25,255),
                       outline=hex_to_rgb(color)+(180,), width=3)
        # 标题栏
        draw.rectangle([wx, wy, wx+ww, wy+35], fill=(30,30,50,255))
        # 用户头像圆点
        draw.ellipse([wx+12, wy+8, wx+28, wy+24], fill=hex_to_rgb(color))
        # 用户名
        draw.text((wx+40, wy+6), user, fill=(200,200,220,255), font=get_font(22))
        # 命令
        draw.text((wx+20, wy+60), cmd, fill=primary+(255,), font=get_font(28))
        # 输出占位
        for j in range(5):
            draw.text((wx+20, wy+110+j*35), f"output line {j+1}",
                       fill=(80,80,100,200), font=get_font(22))

        # 连接线（到中心）
        cx2 = W//2 + (i-1) * 0
        draw.line([(wx+ww//2, wy+wh), (W//2, H//2)],
                   fill=hex_to_rgb(color)+(80,), width=2)

    # 中心同步图标
    cx, cy = W//2, H//2
    for i in range(5, 0, -1):
        draw.ellipse([cx-30-i*5, cy-30-i*5, cx+30+i*5, cy+30+i*5],
                      fill=primary+(25-i*4,))
    sync_font = get_font(50)
    draw.text((cx-35, cy-28), "↔", fill=(255,255,255,255), font=sync_font)


# ═══════════════════════════════════════════════════════════
# ai-math-notes 专属视觉（6个）
# ═══════════════════════════════════════════════════════════

def _draw_math_canvas(draw, theme_key):
    """01 画布手写：黑色画布 + 白色手写公式 + Apple Pencil"""
    theme = THEMES[theme_key]
    primary = hex_to_rgb(theme["primary"])
    cx, cy = W//2, H//2 - 60

    # 深色画布背景
    draw.rectangle([cx-380, cy-260, cx+380, cy+220],
                   fill=(10,10,10,255))

    # 手写数学公式（白色，有笔触质感）
    math_font = get_font(90)
    draw.text((cx-280, cy-180), "5",   fill=(255,255,255,255), font=math_font)
    draw.text((cx-180, cy-180), "+",   fill=(255,255,255,220), font=math_font)
    draw.text((cx-90,  cy-180), "3",   fill=(255,255,255,255), font=math_font)
    draw.text((cx,     cy-180), "=",   fill=(255,200,100,255), font=math_font)
    # 等号右侧待写区域（虚线框）
    for x in range(cx+90, cx+260, 12):
        draw.line([(x, cy-165),(x+6, cy-165)], fill=(255,255,255,80), width=3)

    # 画笔图标（右上角）
    draw.text((cx+300, cy-260), "✏️",  fill=(255,220,100,200), font=get_font(60))

    # Apple Pencil 风格的细腻下划线
    draw.line([(cx-290, cy-80),(cx+280, cy-80)], fill=primary+(60,), width=2)

    # 底部提示：Math Notes
    note_font = get_font(28)
    draw.text((cx-90, cy+160), "Math Notes", fill=primary+(120,), font=note_font)


def _draw_ai_math(draw, theme_key):
    """02 AI计算：AI大脑 + 数学符号神经网络 + 算式"""
    theme = THEMES[theme_key]
    primary = hex_to_rgb(theme["primary"])
    secondary = hex_to_rgb(theme["secondary"])
    cx, cy = W//2, H//2 - 60

    # AI大脑：多层椭圆叠加
    brain_colors = [(80,20,120),(60,10,100),(40,5,80)]
    for i, bc in enumerate(brain_colors):
        r = 160 - i*25
        draw.ellipse([cx-r, cy-r*0.7, cx+r, cy+r*0.7], fill=bc+(255,))

    # 神经网络节点
    nodes = [
        (cx-100, cy-80), (cx+100, cy-80),
        (cx-60, cy), (cx+60, cy),
        (cx-120, cy+80), (cx, cy+90), (cx+120, cy+80),
    ]
    for nx, ny in nodes:
        for i in range(3, 0, -1):
            draw.ellipse([nx-8-i*2, ny-8-i*2, nx+8+i*2, ny+8+i*2],
                         fill=secondary+(40-i*10,))
        draw.ellipse([nx-7, ny-7, nx+7, ny+7], fill=(255,255,255,200))
        draw.ellipse([nx-4, ny-4, nx+4, ny+4], fill=secondary+(220,))

    # 节点连线
    for i, (nx, ny) in enumerate(nodes):
        for j, (mx, my) in enumerate(nodes):
            if i < j and ((nx-mx)**2+(ny-my)**2)**0.5 < 180:
                draw.line([(nx,ny),(mx,my)], fill=secondary+(60,), width=2)

    # 中心AI核心
    for i in range(8, 0, -1):
        draw.ellipse([cx-i*10, cy-i*10, cx+i*10, cy+i*10],
                      fill=primary+(25-i*2,))

    # 数学符号浮现在周围
    math_syms = [("∑", cx-260, cy-200), ("∫", cx+240, cy-180),
                 ("π", cx-280, cy+60),  ("∞", cx+260, cy+80)]
    for sym, sx, sy in math_syms:
        draw.text((sx, sy), sym, fill=primary+(80,), font=get_font(50))

    # 终端建议条
    bar_y = cy + 200
    draw.rounded_rectangle([cx-250, bar_y, cx+250, bar_y+55], 10,
                           fill=(5,5,15,255), outline=primary+(180,), width=2)
    draw.text((cx-220, bar_y+12), "AI: ⌘K to calculate",
              fill=primary+(220,), font=get_font(28))


def _draw_equals_wait(draw, theme_key):
    """03 等号求解：手写等号 + 问号气泡 + 等待"""
    theme = THEMES[theme_key]
    primary = hex_to_rgb(theme["primary"])
    cx, cy = W//2, H//2 - 80

    # 黑色画布
    draw.rectangle([cx-400, cy-200, cx+400, cy+200], fill=(8,8,12,255))

    # 手写等号（粗白笔触）
    eq_font = get_font(120)
    draw.text((cx-120, cy-60), "=", fill=(255,255,255,255), font=eq_font)
    # 等号上横线（手写感）
    draw.line([(cx-140, cy-70),(cx-20, cy-65)], fill=(255,255,255,220), width=8)
    draw.line([(cx-140, cy-40),(cx-20, cy-45)], fill=(255,255,255,220), width=8)

    # 问号气泡（等号右边，带闪烁感）
    bubble_x, bubble_y = cx+120, cy-80
    # 气泡背景
    draw.ellipse([bubble_x-70, bubble_y-70, bubble_x+70, bubble_y+70],
                 fill=(40,30,80,255), outline=primary+(200,), width=3)
    # 问号
    q_font = get_font(80)
    draw.text((bubble_x-30, bubble_y-50), "?", fill=primary+(255,), font=q_font)
    # 问号发光
    for i in range(5, 0, -1):
        draw.ellipse([bubble_x-70-i*3, bubble_y-70-i*3,
                      bubble_x+70+i*3, bubble_y+70+i*3],
                     fill=primary+(15-i*2,))

    # 等待省略号动画（三个点）
    dot_colors = [primary+(255,), primary+(180,), primary+(80,)]
    for i, dx in enumerate([cx-40, cx, cx+40]):
        draw.ellipse([dx-8, cy+50, dx+8, cy+66], fill=dot_colors[i])

    # 底部：虚线等号（未写完的等号）
    draw.line([(cx-250, cy+160),(cx-50, cy+160)], fill=(255,255,255,100), width=4)
    draw.line([(cx+50, cy+160),(cx+250, cy+160)], fill=(255,255,255,100), width=4)


def _draw_math_notes(draw, theme_key):
    """04 MathNotes：Apple风格 + 数学公式 + AI图标"""
    theme = THEMES[theme_key]
    primary = hex_to_rgb(theme["primary"])
    cx, cy = W//2, H//2 - 60

    # Apple白色卡片背景
    card_w, card_h = 700, 420
    draw.rounded_rectangle([cx-card_w//2, cy-card_h//2,
                             cx+card_w//2, cy+card_h//2],
                            20, fill=(25,25,30,255), outline=(60,60,70,255), width=2)

    # Apple风格标题栏
    draw.rounded_rectangle([cx-card_w//2, cy-card_h//2,
                             cx+card_w//2, cy-card_h//2+50],
                            20, fill=(35,35,42,255))
    # Apple Logo 符号
    draw.text((cx-card_w//2+30, cy-card_h//2+10),
              "🍎", fill=(255,255,255,200), font=get_font(30))
    draw.text((cx-card_w//2+70, cy-card_h//2+12),
              "Math Notes", fill=(200,200,210,200), font=get_font(22))

    # 数学公式区
    math_font = get_font(80)
    eq_y = cy - 20
    draw.text((cx-280, eq_y),   "x²",   fill=(255,255,255,220), font=math_font)
    draw.text((cx-140, eq_y),   "+",    fill=(255,255,255,180), font=math_font)
    draw.text((cx-60,  eq_y),   "y",    fill=(255,255,255,220), font=math_font)
    draw.text((cx+20,  eq_y),   "=",    fill=(100,220,255,255), font=math_font)
    draw.text((cx+100, eq_y),   "?",    fill=(100,220,255,255), font=math_font)

    # AI处理指示（底部线条）
    draw.line([(cx-card_w//2+40, cy+140),
               (cx+card_w//2-40, cy+140)],
              fill=primary+(80,), width=2)

    # AI芯片图标
    chip_x, chip_y = cx, cy+200
    chip_sz = 50
    draw.rectangle([chip_x-chip_sz, chip_y-chip_sz,
                    chip_x+chip_sz, chip_y+chip_sz],
                   fill=(15,15,25,255), outline=primary+(200,), width=2)
    # 芯片内部线条
    for i in range(-2, 3):
        draw.line([(chip_x-40, chip_y+i*12),(chip_x+40, chip_y+i*12)],
                  fill=primary+(80,), width=1)
    draw.text((chip_x-18, chip_y-28), "AI",
              fill=primary+(255,), font=get_font(28))


def _draw_eraser(draw, theme_key):
    """05 清空重写：橡皮擦划过 + 画布清空效果"""
    theme = THEMES[theme_key]
    primary = hex_to_rgb(theme["primary"])
    cx, cy = W//2, H//2 - 60

    # 画布背景
    draw.rectangle([cx-380, cy-250, cx+380, cy+200],
                   fill=(10,10,10,255))

    # 被擦掉的残留痕迹（淡化效果）
    eras_font = get_font(60)
    eras_items = [("5", cx-200, cy-120), ("+", cx-80, cy-120),
                  ("3", cx+40, cy-120), ("=", cx+140, cy-120)]
    for item, ex, ey in eras_items:
        draw.text((ex, ey), item, fill=(80,80,80,150), font=eras_font)

    # 橡皮擦图标（带倾斜角度）
    eraser_x, eraser_y = cx-60, cy-60
    draw.rectangle([eraser_x-60, eraser_y-30, eraser_x+60, eraser_y+30],
                   fill=(220,180,140,255), outline=(100,80,60,255), width=3)
    # 橡皮擦纹理
    draw.line([(eraser_x-50, eraser_y),(eraser_x+50, eraser_y)],
              fill=(200,160,120,200), width=2)

    # 擦除轨迹（从左上到右下的渐隐线条）
    for i, (lx, ly) in enumerate([
        (cx-300, cy-180), (cx-200, cy-100), (cx-100, cy-20),
        (cx, cy+60), (cx+100, cy+140)
    ]):
        alpha = 200 - i*35
        draw.ellipse([lx-15, ly-8, lx+15, ly+8],
                     fill=primary+(max(30,alpha),))

    # 清空按钮（右下角）
    btn_x, btn_y = cx+280, cy+100
    draw.rounded_rectangle([btn_x-60, btn_y-30, btn_x+60, btn_y+30], 8,
                           fill=(60,20,20,255), outline=(255,80,80,200,), width=2)
    draw.text((btn_x-40, btn_y-22), "清空",
              fill=(255,100,100,220,), font=get_font(28))

    # 刷新图标
    draw.text((btn_x-18, btn_y-50), "🔄",
              fill=(100,200,255,200,), font=get_font(36))


def _draw_answer_reveal(draw, theme_key):
    """06 答案揭晓：等号旁橙色答案 + 成就感视觉"""
    theme = THEMES[theme_key]
    primary = hex_to_rgb(theme["primary"])
    cx, cy = W//2, H//2 - 80

    # 深色画布
    draw.rectangle([cx-400, cy-200, cx+400, cy+200], fill=(8,8,12,255))

    # 公式部分（淡化表示已识别）
    old_font = get_font(70)
    draw.text((cx-300, cy-80), "5",   fill=(100,100,120,180), font=old_font)
    draw.text((cx-200, cy-80), "+",   fill=(100,100,120,150), font=old_font)
    draw.text((cx-130, cy-80), "3",   fill=(100,100,120,180), font=old_font)

    # 等号（白色）
    eq_font = get_font(100)
    draw.text((cx-50, cy-90), "=", fill=(255,255,255,255), font=eq_font)

    # 答案高亮框（橙色，醒目）
    ans_x, ans_y = cx+100, cy-110
    ans_font = get_font(130)
    # 外发光（多层橙色）
    for i in range(10, 0, -1):
        draw.ellipse([ans_x-80-i*5, ans_y-i*5, ans_x+100+i*5, ans_y+100+i*5],
                     fill=(255,140,0,max(1,25-i*2)),)
    # 答案背景框
    draw.rounded_rectangle([ans_x-80, ans_y-10, ans_x+100, ans_y+100],
                            15, fill=(255,140,0,255))
    # 答案数字
    draw.text((ans_x-30, ans_y), "8",
              fill=(255,255,255,255), font=ans_font)

    # 成功标记（对勾符号）
    check_x, check_y = cx+300, cy-100
    check_font = get_font(70)
    draw.text((check_x, check_y), "✓",
              fill=(0,255,136,255), font=check_font)
    # 对勾发光
    for i in range(4, 0, -1):
        draw.ellipse([check_x-20-i*3, check_y-20-i*3,
                      check_x+50+i*3, check_y+50+i*3],
                     fill=(0,255,136,15-i*3))

    # 底部：AI处理完毕提示
    done_font = get_font(24)
    draw.text((cx-90, cy+160), "✨ AI计算完成",
              fill=primary+(150,), font=done_font)


# ── 06: Warp粉丝 ── 终端 + 红心 ──────────────────────
def _draw_warp_fan(draw, theme_key):
    theme = THEMES[theme_key]
    primary = hex_to_rgb(theme["primary"])

    cx, cy = W//2, H//2 - 80

    # 终端窗口
    win_w, win_h = 620, 380
    draw.rectangle([cx-win_w//2, cy-win_h//2, cx+win_w//2, cy+win_h//2],
                   fill=(15,15,25,255), outline=primary+(200,), width=3)
    # 标题栏
    draw.rectangle([cx-win_w//2, cy-win_h//2, cx+win_w//2, cy-win_h//2+40],
                   fill=(30,30,55,255))
    for bx, col in [(cx-win_w//2+16,(255,80,80,200)),
                    (cx-win_w//2+42,(255,200,80,200)),
                    (cx-win_w//2+68,(80,200,80,200))]:
        draw.ellipse([bx-7,cy-win_h//2+9,bx+7,cy-win_h//2+23], fill=col)
    draw.text((cx-win_w//2+90, cy-win_h//2+8),
               "Warp Terminal", fill=(0,255,255,180,), font=get_font(24))

    # 终端内容
    term_font = get_font(30)
    draw.text((cx-win_w//2+30, cy-win_h//2+70),
              "~/projects $ warp", fill=(100,100,120,255), font=term_font)
    draw.text((cx-win_w//2+30, cy-win_h//2+115),
              "✓ Warp loaded!", fill=(0,255,136,255), font=term_font)
    draw.text((cx-win_w//2+30, cy-win_h//2+160),
              "~/projects $", fill=(255,255,255,255), font=term_font)

    # 闪烁光标
    draw.rectangle([cx-win_w//2+190, cy-win_h//2+162,
                    cx-win_w//2+210, cy-win_h//2+182],
                   fill=(0,255,255,200))

    # 大红心（中心偏右）
    hx, hy = cx + 180, cy + 80
    heart_font = get_font(180)
    draw.text((hx-60, hy-80), "❤", fill=(255,60,80,255), font=heart_font)

    # 漂浮小爱心
    small_hearts = [(100,200),(900,250),(150,500),(950,450),(80,350)]
    for sx, sy in small_hearts:
        draw.text((sx, sy), "❤", fill=(255,100,130,150), font=get_font(50))


# ═══════════════════════════════════════════════════════════
#  7种主题背景（可选装饰，不影响专属视觉）
# ═══════════════════════════════════════════════════════════

def apply_theme_bg(draw, theme_key):
    """应用主题背景装饰（圆形内）"""
    theme = THEMES[theme_key]
    cx, cy = W//2, H//2
    radius = 500
    bg = hex_to_rgb(theme["bg"])

    if theme_key == "cyberpunk":
        for i in range(radius, 0, -4):
            r = int(5*i/radius + 15*(1-i/radius))
            g = int(8*i/radius + 5*(1-i/radius))
            b = int(20*i/radius + 40*(1-i/radius))
            draw.ellipse([cx-i,cy-i,cx+i,cy+i],fill=(r,g,b))
        for x in range(60,W-60,40):
            for y in range(60,H-60,40):
                if ((x-cx)**2+(y-cy)**2)**0.5 < radius-10:
                    draw.ellipse([x-1,y-1,x+1,y+1],fill=(0,255,255,30))
        for i in range(6,0,-1):
            draw.ellipse([cx-200-i*12,cy-200-i*12,cx+200+i*12,cy+200+i*12],
                          fill=(255,0,255,max(1,20-i*3)))
        draw.ellipse([cx-radius,cy-radius,cx+radius,cy+radius],
                      outline=(0,255,255,255),width=4)

    elif theme_key == "kawaii":
        rx, ry = 480, 620
        for i in range(min(rx,ry),0,-4):
            ratio = i/min(rx,ry)
            r = int(255*ratio+255*(1-ratio))
            g = int(182*ratio+105*(1-ratio))
            b = int(193*ratio+180*(1-ratio))
            draw.ellipse([cx-i,cy-i*ry//rx,cx+i,cy+i*ry//rx],fill=(r,g,b))
        draw.ellipse([cx-350,cy-350,cx+350,cy+350],
                      outline=(255,105,180,255),width=6)

    elif theme_key == "neon":
        draw.ellipse([cx-radius,cy-radius,cx+radius,cy+radius],fill=(5,5,15))
        for x in range(0,W,60):
            for y in range(0,H,60):
                if ((x-cx)**2+(y-cy)**2)**0.5<radius-10:
                    draw.line([(x,y),(x+2,y)],fill=(0,255,255,20))
        for i in range(10,0,-1):
            draw.ellipse([cx-280-i*12,cy-280-i*12,cx+280+i*12,cy+280+i*12],
                          fill=(255,0,255,max(1,15-i)))
        draw.ellipse([cx-radius,cy-radius,cx+radius,cy+radius],
                      outline=(0,255,255,255),width=4)

    elif theme_key == "hand-drawn":
        random.seed(42)
        pts = []
        for angle in range(0,360,3):
            rad = math.radians(angle)
            r = 480+random.randint(-8,8)
            pts.append((int(cx+r*math.cos(rad)),int(cy+r*math.sin(rad))))
        for i in range(len(pts)-1):
            draw.line([pts[i],pts[i+1]],fill=(255,235,205),width=40)
        draw.line([pts[-1],pts[0]],fill=(255,235,205),width=40)
        for w,alpha,rough in [(8,200,6),(5,255,4)]:
            pts2=[]
            for angle in range(0,360,2):
                rad=math.radians(angle)
                r=480+random.randint(-rough,rough)
                pts2.append((int(cx+r*math.cos(rad)),int(cy+r*math.sin(rad))))
            for i in range(len(pts2)-1):
                draw.line([pts2[i],pts2[i+1]],fill=(139,69,19,alpha),width=w)
            draw.line([pts2[-1],pts2[0]],fill=(139,69,19,alpha),width=w)

    elif theme_key == "retro":
        pixel=10
        for y in range(0,H,pixel):
            ratio=y/H
            r=int(60*ratio+30*(1-ratio));g=0;b=0
            draw.rectangle([0,y,W,y+pixel],fill=(r,g,b))
        for y in range(0,H,pixel*2):
            for x in range(0,W,pixel*2):
                idx=((x//pixel)+(y//pixel))%3
                if idx==0: draw.rectangle([x,y,x+pixel,y+pixel],fill=(255,215,0,50))
                elif idx==1: draw.rectangle([x,y,x+pixel,y+pixel],fill=(255,140,0,30))
        border=(255,215,0)
        for i in range(4):
            o=i*pixel
            draw.rectangle([o,o,W-o-1,H-o-1],outline=border+(255,),width=4-i)

    elif theme_key == "minimal":
        draw.ellipse([cx-200,cy-200,cx+200,cy+200],
                      outline=(33,33,33,255),width=6)

    elif theme_key == "meme":
        m=80
        draw.rectangle([m,m,W-m,H-m],fill=(255,69,0,255),outline=(0,0,0,255),width=8)


# ═══════════════════════════════════════════════════════════
#  透明遮罩（圆形外透明）
# ═══════════════════════════════════════════════════════════

def apply_circular_mask(canvas):
    """圆形遮罩：边缘羽化（GaussianBlur），过渡自然"""
    alpha_mask = Image.new("L", (W,H), 0)
    draw_mask = ImageDraw.Draw(alpha_mask)
    draw_mask.ellipse(
        [CIRCLE_CX-CIRCLE_R, CIRCLE_CY-CIRCLE_R,
         CIRCLE_CX+CIRCLE_R, CIRCLE_CY+CIRCLE_R], fill=255)
    # 羽化边缘：模糊 + 还原（使边缘渐变过渡）
    blurred = alpha_mask.filter(ImageFilter.GaussianBlur(radius=15))
    canvas.putalpha(blurred)


# ═══════════════════════════════════════════════════════════
#  主生成函数（per-sticker 路由）
# ═══════════════════════════════════════════════════════════

def create_sticker(text, output_path, name, visual_elements, theme_key="cyberpunk", font_size=110):
    # 背景层（含圆形遮罩）
    bg_layer = Image.new("RGBA", (W,H), (0,0,0,0))
    draw_bg = ImageDraw.Draw(bg_layer)
    apply_theme_bg(draw_bg, theme_key)
    # 词汇表驱动绘制：visual_elements 列表直接映射到词汇表函数
    draw_visual(draw_bg, visual_elements, name, theme_key)
    # 圆形遮罩只应用于背景层
    if theme_key in CIRCULAR_THEMES:
        apply_circular_mask(bg_layer)

    # 文字层（不受遮罩影响，直接贴画布底）
    text_layer = Image.new("RGBA", (W,H), (0,0,0,0))
    draw_txt = ImageDraw.Draw(text_layer)
    tt, tb = text_bottom_draw(draw_txt, text, theme_key, font_size)
    label_draw(draw_txt, "WARP", theme_key, tt)  # 标签在文字上方

    # 合并：bg_layer在下、text_layer在上（文字覆盖背景）
    canvas = Image.alpha_composite(bg_layer, text_layer)
    canvas.save(output_path, "PNG")


# ═══════════════════════════════════════════════════════════
#  解析提示词文件
# ═══════════════════════════════════════════════════════════

def parse_prompt_file(pf):
    if not os.path.exists(pf):
        return None, None, None, [], []
    with open(pf, encoding="utf-8") as f:
        content = f.read()
    name=text=copy=None
    visual_elements=[]
    style_keywords=[]
    in_copy=in_vis=in_style=False

    for line in content.split("\n"):
        if line.startswith("name:"):
            name=line.split("name:",1)[1].strip()
        elif line.startswith("copy:"):
            copy=line.split("copy:",1)[1].strip()
        elif line.startswith("visual_elements:"):
            raw=line.split("visual_elements:",1)[1].strip()
            visual_elements=[v.strip() for v in raw.strip("[]").split(",")]
        elif line.startswith("style_keyword:"):
            raw=line.split("style_keyword:",1)[1].strip()
            style_keywords=[v.strip() for v in raw.strip("[]").split(",")]
        elif "## 核心文案" in line or "## 内容" in line:
            in_copy=True; continue
        elif in_copy and line.startswith("##"):
            in_copy=False
        elif in_copy and line.strip() and not line.startswith("#"):
            if not line.startswith("-") and not line.startswith("*"):
                copy=line.strip(); in_copy=False
        elif "## 视觉设计规则" in line:
            in_vis=True; in_style=False
        elif "## 风格要求" in line:
            in_style=True; in_vis=False
        elif in_vis and line.strip() and not line.startswith("#"):
            if not line.startswith("-") and not line.startswith("*"):
                pass  # 已通过 visual_elements 字段解析
        elif "中文文字" in line or "Chinese text" in line.lower():
            continue
        elif text is None and len(line)>0 and not line.startswith("#") and not line.startswith("-"):
            if ":" not in line or len(line.split(":",1)[0])>10:
                if len(line.strip())<=10:
                    text=line.strip()

    basename=os.path.splitext(os.path.basename(pf))[0]
    if name is None:
        parts=basename.split("-",1)
        name=parts[1] if len(parts)>1 else basename
    if text is None: text=name
    if copy is None: copy=text
    return name, text, copy, visual_elements, style_keywords


# ═══════════════════════════════════════════════════════════
#  main
# ═══════════════════════════════════════════════════════════

def main():
    import argparse
    parser=argparse.ArgumentParser(description="生成微信表情包（每个贴图专属视觉）")
    parser.add_argument("--input","-i",required=True)
    parser.add_argument("--output","-o",required=True)
    parser.add_argument("--theme","-t",default="cyberpunk",
                        choices=list(THEMES.keys()))
    parser.add_argument("--font-size","-f",type=int,default=120)
    args=parser.parse_args()
    os.makedirs(args.output, exist_ok=True)

    files=sorted(glob.glob(os.path.join(args.input,"*.md")))
    if not files:
        print("⚠️  未找到提示词文件"); return

    print(f"🎨 风格: {THEMES[args.theme]['primary']} {args.theme}")
    print(f"📂 {args.input} → {args.output}")
    print(f"📐 {W}×{H}px | 文字:底部居中 左右{TEXT_MARGIN}px 距底{TEXT_BOTTOM}px\n")

    ok=0
    for pf in files:
        name,text,copy,v_elems,s_kw=parse_prompt_file(pf)
        if name is None: continue
        out=os.path.join(args.output, os.path.basename(pf).replace(".md",".png"))
        try:
            create_sticker(copy, out, name, v_elems, args.theme, args.font_size)
            tags=", ".join(s_kw[:3]) if s_kw else ""
            print(f"✓ {name}: {tags}")
            ok+=1
        except Exception as e:
            print(f"✗ {name}: {e}")
    print(f"\n✅ {ok}/{len(files)} 张贴图 | 专属视觉 ✓")
    print(f"📦 {args.output}")

if __name__=="__main__":
    main()
