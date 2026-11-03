# VSети: рисует значок (монограмма VS на полупрозрачном глобусе) в два файла:
# icon_full.png (с надписью VSети) и icon_notext.png (для маленьких размеров).
# Запуск: python make_icons.py <Inter-Bold.otf> <Inter-Medium.otf> <папка>
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

FB, FM, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W = 1254; K = 3; S = W * K
gold = (232, 206, 130, 255); bg = (1, 30, 15, 255); G1 = (61, 220, 132, 255)
p = lambda x, y: (x * K, y * K)


def base():
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    r = int(0.18 * S); t = int(0.008 * S)
    d.rounded_rectangle((0, 0, S - 1, S - 1), radius=r, fill=gold)
    d.rounded_rectangle((t, t, S - 1 - t, S - 1 - t), radius=r - t, fill=bg)
    return img


def content(text=True):
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    gl = Image.new('RGBA', (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    cx, cy, R = 627, 535, 345; col = (61, 220, 132, 90)
    g.ellipse((p(cx - R, cy - R), p(cx + R, cy + R)), outline=col, width=16 * K)
    for f in (0.36, 0.72):
        g.ellipse((p(cx - R * f, cy - R), p(cx + R * f, cy + R)), outline=col, width=10 * K)
    g.line([p(cx, cy - R), p(cx, cy + R)], fill=col, width=10 * K)
    for f in (-0.5, 0, 0.5):
        yy = cy + R * f; hw = math.sqrt(R * R - (R * f) ** 2)
        g.line([p(cx - hw, yy), p(cx + hw, yy)], fill=col, width=10 * K)
    img.alpha_composite(gl); d = ImageDraw.Draw(img)
    fv = ImageFont.truetype(FB, 640 * K); fs = ImageFont.truetype(FM, 470 * K)
    d.text(p(590, 770), 'V', font=fv, fill=G1, anchor='ms')
    d.text(p(680, 745), 'S', font=fs, fill=gold, anchor='ms', stroke_width=14 * K, stroke_fill=bg)
    if text:
        big = ImageFont.truetype(FM, 205 * K); small = ImageFont.truetype(FM, 137 * K)
        vw = d.textlength('VS', font=big); ew = d.textlength('ети', font=small)
        x0 = S / 2 - (vw + 5 * K + ew) / 2; by = 1100 * K
        d.text((x0, by), 'VS', font=big, fill=gold, anchor='ls')
        d.text((x0 + vw + 5 * K, by), 'ети', font=small, fill=gold, anchor='ls')
    return img


full = base(); full.alpha_composite(content())
full.resize((1024, 1024), Image.LANCZOS).save(os.path.join(OUT, 'icon_full.png'))
c = content(text=False); cc = c.crop(c.getbbox())
sc = 0.78 * S / max(cc.size); cc = cc.resize((int(cc.width * sc), int(cc.height * sc)), Image.LANCZOS)
nt = base(); nt.alpha_composite(cc, ((S - cc.width) // 2, (S - cc.height) // 2))
nt.resize((1024, 1024), Image.LANCZOS).save(os.path.join(OUT, 'icon_notext.png'))
print('OK картинки значка')
