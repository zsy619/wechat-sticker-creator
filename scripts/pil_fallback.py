#!/usr/bin/env python3
"""
pil_fallback.py - PIL 本地兜底生成器
当 AI 和 Remotion 均不可用时，使用此脚本生成贴图。

Usage:
    python3 pil_fallback.py --input prompts/ --output assets/ --theme cyberpunk
"""

import os, sys, math, glob, argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1440
TEXT_MARGIN = TEXT_BOTTOM = 30
CIRCULAR_THEMES = {"cyberpunk", "kawaii", "neon"}

THEMES = {
    "cyberpunk":  {"primary": "#00FFFF", "secondary": "#FF00FF", "bg": "#0D0D1A", "text": "#FFFFFF", "accent": "#00FF88"},
    "kawaii":     {"primary": "#FF69B4", "secondary": "#FFB6C1", "bg": "#FFF0F5", "text": "#4A4A4A", "accent": "#FF1493"},
    "neon":       {"primary": "#FF00FF", "secondary": "#00FFFF", "bg": "#1A0033", "text": "#FFFFFF", "accent": "#FF69B4"},
    "retro":      {"primary": "#FFD700", "secondary": "#FF6B35", "bg": "#2D1B00", "text": "#FFFFFF", "accent": "#FF4500"},
    "hand-drawn": {"primary": "#8B4513", "secondary": "#D2691E", "bg": "#FFF8DC", "text": "#4A4A4A", "accent": "#CD853F"},
    "minimal":    {"primary": "#212529", "secondary": "#495057", "bg": "#F8F9FA", "text": "#212529", "accent": "#6C757D"},
    "meme":       {"primary": "#FF4500", "secondary": "#FFD700", "bg": "#1A1A1A", "text": "#FFFFFF", "accent": "#FF6347"},
}

CIRCLE_CX, CIRCLE_CY, CIRCLE_R = W//2, H//2, 500
CIRCLE_RADIUS_BLUR = 15

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def get_font(sz):
    for p in ["/System/Library/Fonts/PingFang.ttc",
              "/System/Library/Fonts/STHeiti Medium.ttc",
              "/System/Library/Fonts/Helvetica.ttc",
              "/System/Library/Fonts/Arial.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, sz)
            except: pass
    return ImageFont.load_default(sz)

def wrap_text(text, font, max_w):
    words = text.split()
    lines, current = [], ""
    for w in words:
        test = (current + " " + w).strip()
        if sum(font.getbbox(c)[2] for c in test) <= max_w:
            current = test
        else:
            if current: lines.append(current)
            current = w
    if current: lines.append(current)
    return lines

def apply_theme_bg(draw, theme_key):
    t = THEMES.get(theme_key, THEMES['cyberpunk'])
    draw.rectangle([0, 0, W, H], fill=hex_to_rgb(t['bg']) + (255,))

def apply_circular_mask(img):
    mask = Image.new("L", (W, H), 0)
    mdraw = ImageDraw.Draw(mask)
    for r in range(CIRCLE_RADIUS_BLUR, -1, -1):
        alpha = int(255 * (1 - r / CIRCLE_RADIUS_BLUR))
        mdraw.ellipse([CIRCLE_CX-CIRCLE_R-r, CIRCLE_CY-CIRCLE_R-r,
                        CIRCLE_CX+CIRCLE_R+r, CIRCLE_CY+CIRCLE_R+r],
                       fill=min(255, alpha))
    blurred = mask.filter(ImageFilter.GaussianBlur(CIRCLE_RADIUS_BLUR))
    img.putalpha(blurred)

def text_bottom_draw(draw, text, theme_key, font_sz=110):
    theme = THEMES[theme_key]
    font = get_font(font_sz)
    lines = wrap_text(text, font, W - 2*TEXT_MARGIN)
    line_h = int(font_sz * 1.4)
    total_h = len(lines) * line_h
    # 底部对齐
    y_start = H - TEXT_BOTTOM - total_h
    for i, line in enumerate(lines):
        tw = sum(font.getbbox(c)[2] for c in line)
        draw.text(((W - tw)//2, y_start + i*line_h),
                  line, fill=hex_to_rgb(theme['text'])+(255,), font=font)
    return y_start - 8, y_start

def label_draw(draw, label, theme_key, top_y):
    theme = THEMES[theme_key]
    font = get_font(22)
    lw = sum(font.getbbox(c)[2] for c in label)
    draw.text(((W - lw)//2, top_y - 36), label,
             fill=hex_to_rgb(theme['primary'])+(180,), font=font)

# ── 词汇表函数 ──────────────────────────────────────────────

def _draw_brain(draw, theme, cx, cy, w, h):
    p = hex_to_rgb(theme['primary'])
    for i, (r_ratio, bc) in enumerate([(0.9,(60,10,100)),(0.7,(40,5,80)),(0.5,(25,3,60))]):
        rx, ry = w*r_ratio*0.5, w*r_ratio*0.5*0.75
        draw.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=bc+(255,))
    for i in range(8, 0, -1):
        draw.ellipse([cx-i*12, cy-i*12, cx+i*12, cy+i*12], fill=p+(max(5,20-i*2),))

def _draw_neural_network(draw, theme, cx, cy, w, h):
    p = hex_to_rgb(theme['primary'])
    s = hex_to_rgb(theme['secondary'])
    offsets = [(-0.3,-0.25),(0.3,-0.25),(-0.45,0),(0,0),(0.45,0),(-0.3,0.25),(0.3,0.25)]
    nodes = [(cx+ox*w, cy+oy*h) for ox,oy in offsets]
    for i,(nx,ny) in enumerate(nodes):
        for j,(mx,my) in enumerate(nodes):
            if i<j and ((nx-mx)**2+(ny-my)**2)**0.5 < w*0.5:
                draw.line([(nx,ny),(mx,my)], fill=s+(60,), width=2)
    for nx, ny in nodes:
        for ring in range(3,0,-1):
            draw.ellipse([nx-ring*5,ny-ring*5,nx+ring*5,ny+ring*5], fill=s+(30-ring*8,))
        draw.ellipse([nx-7,ny-7,nx+7,ny+7], fill=(255,255,255,200))
        draw.ellipse([nx-4,ny-4,nx+4,ny+4], fill=s+(200,))

def _draw_terminal(draw, theme, cx, cy, w, h):
    p = hex_to_rgb(theme['primary'])
    ww, wh = int(w*0.95), int(h*0.85)
    tx, ty = cx-ww//2, cy-wh//2
    draw.rectangle([tx,ty,tx+ww,ty+wh], fill=(15,15,28,255))
    draw.rectangle([tx,ty,tx+ww,ty+wh], outline=p+(180,), width=2)
    th = int(wh*0.12)
    draw.rectangle([tx,ty,tx+ww,ty+th], fill=(30,30,50,255))
    for bx,col in [(tx+16,(255,80,80,200)),(tx+36,(255,200,80,200)),(tx+56,(80,200,100,200))]:
        draw.ellipse([bx-6,ty+th//2-6,bx+6,ty+th//2+6], fill=col)
    draw.rectangle([tx+20,ty+th+int(wh*0.15),tx+60,ty+th+int(wh*0.15)+20], fill=p+(180,))

def _draw_lightning(draw, theme, cx, cy, w, h):
    p = hex_to_rgb(theme['primary'])
    for angle in range(0, 360, 10):
        rad = math.radians(angle)
        x1,y1 = int(cx+w*0.15*math.cos(rad)), int(cy+w*0.15*math.sin(rad))
        x2,y2 = int(cx+w*0.48*math.cos(rad)), int(cy+w*0.48*math.sin(rad))
        draw.line([(x1,y1),(x2,y2)], fill=p+(40,), width=2)
    draw.text((cx-int(w*0.2),cy-int(h*0.25)), "⚡",
              fill=(255,255,255,255), font=get_font(int(min(w,h)*0.5)))

def _draw_heart(draw, theme, cx, cy, w, h):
    draw.text((cx-int(w*0.25),cy-int(h*0.35)), "❤",
              fill=(255,60,90,255), font=get_font(int(min(w,h)*0.7)))

def _draw_equals_sign(draw, theme, cx, cy, w, h):
    draw.text((cx-int(w*0.2),cy-int(h*0.2)), "=",
              fill=(255,255,255,255), font=get_font(int(min(w,h)*0.6)))

def _draw_question_mark(draw, theme, cx, cy, w, h):
    p = hex_to_rgb(theme['primary'])
    for i in range(5, 0, -1):
        draw.ellipse([cx-w*0.4-i*3,cy-h*0.35-i*3,cx+w*0.4+i*3,cy+h*0.35+i*3],
                     fill=p+(12-i*2,))
    draw.ellipse([cx-w*0.4,cy-h*0.35,cx+w*0.4,cy+h*0.35],
                 fill=(40,30,80,255), outline=p+(200,), width=2)
    draw.text((cx-int(w*0.12),cy-int(h*0.2)), "?",
              fill=p+(255,), font=get_font(int(min(w,h)*0.5)))

def _draw_eraser(draw, theme, cx, cy, w, h):
    ew, eh = int(w*0.6), int(h*0.3)
    draw.rectangle([cx-ew//2,cy-eh//2,cx+ew//2,cy+eh//2],
                   fill=(220,180,140,255), outline=(100,80,60,255), width=2)
    for i,(ox,oy) in enumerate([(-w*0.3,0),(0,0),(w*0.2,h*0.15)]):
        draw.ellipse([cx+ox-w*0.08,cy+oy-h*0.08,cx+ox+w*0.08,cy+oy+h*0.08],
                     fill=hex_to_rgb(theme['primary'])+(max(30,180-i*50),))

def _draw_checkmark(draw, theme, cx, cy, w, h):
    for i in range(5, 0, -1):
        draw.ellipse([cx-w*0.3-i*3,cy-h*0.3-i*3,cx+w*0.3+i*3,cy+h*0.3+i*3],
                     fill=(0,255,136,15-i*2,))
    draw.text((cx-int(w*0.2),cy-int(h*0.25)), "✓",
              fill=(0,255,136,255), font=get_font(int(min(w,h)*0.5)))

def _draw_math_canvas(draw, theme, cx, cy, w, h):
    cw, ch = int(w*0.9), int(h*0.8)
    draw.rectangle([cx-cw//2,cy-ch//2,cx+cw//2,cy+ch//2], fill=(10,10,10,255))
    mf = get_font(int(min(w,h)*0.18))
    for (sym,ox) in [("5",-w*0.2),("+",-w*0.08),("3",w*0.04),("=","=" and w*0.16)]:
        col = (255,200,80,255) if sym == "=" else (255,255,255,255)
        draw.text((cx+ox-int(w*0.06),cy-int(h*0.15)), sym, fill=col, font=mf)

ELEMENT_VOCAB = {
    "brain": _draw_brain, "ai大脑": _draw_brain, "ai计算": _draw_brain,
    "神经网络": _draw_neural_network, "neural_network": _draw_neural_network,
    "terminal": _draw_terminal, "终端窗口": _draw_terminal,
    "lightning": _draw_lightning, "闪电": _draw_lightning,
    "heart": _draw_heart, "红心": _draw_heart,
    "equals_sign": _draw_equals_sign, "等号": _draw_equals_sign,
    "question_mark": _draw_question_mark, "问号": _draw_question_mark,
    "eraser": _draw_eraser, "橡皮擦": _draw_eraser,
    "checkmark": _draw_checkmark, "对勾": _draw_checkmark,
    "math_canvas": _draw_math_canvas, "canvas": _draw_math_canvas, "画布": _draw_math_canvas,
}

def draw_visual(draw, visual_elements, theme_key):
    theme = THEMES[theme_key]
    cx, cy = W//2, H//2-60
    area_w, area_h = W*0.8, H*0.6
    for elem in visual_elements:
        fn = ELEMENT_VOCAB.get(elem)
        if fn: fn(draw, theme, cx, cy, area_w*0.6, area_h*0.6)

# ── 主函数 ──────────────────────────────────────────────────

def parse_prompt_file(path):
    with open(path) as f:
        content = f.read()
    front = {}
    for line in content.split('\n'):
        if line.strip() == '---': break
        if ':' in line:
            k, v = line.split(':', 1)
            front[k.strip()] = v.strip().strip('"').strip("'")
    name = front.get('name', os.path.basename(path).replace('.md',''))
    copy = front.get('copy', '')
    try:    v_elems = eval(front.get('visual_elements', '[]'))
    except: v_elems = []
    theme = front.get('theme', 'cyberpunk')
    return name, copy, v_elems, theme

def create_sticker(text, output_path, visual_elements, theme_key, font_size=110):
    bg_layer = Image.new("RGBA", (W,H), (0,0,0,0))
    draw_bg = ImageDraw.Draw(bg_layer)
    apply_theme_bg(draw_bg, theme_key)
    draw_visual(draw_bg, visual_elements, theme_key)
    if theme_key in CIRCULAR_THEMES:
        apply_circular_mask(bg_layer)

    text_layer = Image.new("RGBA", (W,H), (0,0,0,0))
    draw_txt = ImageDraw.Draw(text_layer)
    tt, tb = text_bottom_draw(draw_txt, text, theme_key, font_size)
    label_draw(draw_txt, "WARP", theme_key, tt)

    canvas = Image.alpha_composite(bg_layer, text_layer)
    canvas.save(output_path, "PNG")

def main():
    ap = argparse.ArgumentParser(description='PIL 兜底生成器')
    ap.add_argument('--input',  required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--theme',  default='cyberpunk')
    args = ap.parse_args()
    os.makedirs(args.output, exist_ok=True)

    files = sorted(glob.glob(f"{args.input}/*.md"))
    print(f"主题: {args.theme} | 文件数: {len(files)}")
    ok = 0
    for pf in files:
        name, copy, v_elems, theme = parse_prompt_file(pf)
        out = os.path.join(args.output, os.path.basename(pf).replace('.md','.png'))
        try:
            create_sticker(copy, out, v_elems, theme)
            print(f"✓ {name}")
            ok += 1
        except Exception as e:
            print(f"✗ {name}: {e}")
    print(f"\n✅ {ok}/{len(files)} 张贴图 | PIL兜底")

if __name__ == '__main__':
    main()
