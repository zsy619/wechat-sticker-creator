#!/usr/bin/env python3
"""
generate_stickers.py - 微信表情包 PIL 生成器
每个贴图有专属视觉元素（通过 sticker name 路由）
风格统一（--theme），文字固定在画布底部

支持7种风格: cyberpunk / kawaii / hand-drawn / retro / neon / minimal / meme
每个贴图独立视觉: AI补全 / 命令面板 / 闪电速度 / 智能建议 / 团队协作 / Warp粉丝
"""
import os, sys, math, glob, random
from PIL import Image, ImageDraw, ImageFont

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

def text_bottom_draw(draw, text, theme_key, font_sz=120):
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
    # 装饰线
    ly = tt - 16
    c = hex_to_rgb(theme["primary"])
    draw.line([(W//2-100, ly),(W//2+100, ly)], fill=c+(150,), width=2)
    # 文字
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0,0), line, font=font)
        lw = bbox[2]-bbox[0]
        tx = (W-lw)//2
        ty = tt + i*lh
        draw.text((tx+2,ty+2), line, fill=(0,0,0,120), font=font)
        draw.text((tx,ty), line, fill=hex_to_rgb(theme["text"])+(255,), font=font)
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
#  6种专属视觉绘制函数（统一入口: draw_visual(draw, name, theme_key)）
# ═══════════════════════════════════════════════════════════

def draw_visual(draw, name, theme_key):
    """根据贴图名称分发到专属视觉绘制函数"""
    dispatch = {
        "AI补全":    _draw_ai_autocomplete,
        "命令面板":  _draw_cmd_palette,
        "闪电速度":  _draw_lightning_speed,
        "智能建议":  _draw_smart_suggest,
        "团队协作":  _draw_team_collab,
        "Warp粉丝":  _draw_warp_fan,
    }
    fn = dispatch.get(name)
    if fn:
        fn(draw, theme_key)

# ── 01: AI补全 ── 代码补全下拉框 ──────────────────────
def _draw_ai_autocomplete(draw, theme_key):
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
    alpha_mask = Image.new("L", (W,H), 0)
    ImageDraw.Draw(alpha_mask).ellipse(
        [CIRCLE_CX-CIRCLE_R, CIRCLE_CY-CIRCLE_R,
         CIRCLE_CX+CIRCLE_R, CIRCLE_CY+CIRCLE_R], fill=255)
    canvas.putalpha(alpha_mask)


# ═══════════════════════════════════════════════════════════
#  主生成函数（per-sticker 路由）
# ═══════════════════════════════════════════════════════════

def create_sticker(text, output_path, name, theme_key="cyberpunk", font_size=120):
    # 背景层（含圆形遮罩）
    bg_layer = Image.new("RGBA", (W,H), (0,0,0,0))
    draw_bg = ImageDraw.Draw(bg_layer)
    apply_theme_bg(draw_bg, theme_key)
    draw_visual(draw_bg, name, theme_key)
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
            create_sticker(copy, out, name, args.theme, args.font_size)
            tags=", ".join(s_kw[:3]) if s_kw else ""
            print(f"✓ {name}: {tags}")
            ok+=1
        except Exception as e:
            print(f"✗ {name}: {e}")
    print(f"\n✅ {ok}/{len(files)} 张贴图 | 专属视觉 ✓")
    print(f"📦 {args.output}")

if __name__=="__main__":
    main()
