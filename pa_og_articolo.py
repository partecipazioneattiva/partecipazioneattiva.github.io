from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

BASE = Path("/Users/luigia/SITO-PA")
dst = BASE / "images" / "cittadini-attivi.webp"

W, H = 840, 1120                      # verticale 3:4, come le altre card
BLU, ORO = (13, 27, 75), (232, 144, 10)

img = Image.new("RGB", (W, H), BLU)
d = ImageDraw.Draw(img)

# vignettatura: piu' scuro ai bordi
for y in range(H):
    q = abs(y - H / 2) / (H / 2)
    c = int(13 + 26 * (1 - q)), int(27 + 34 * (1 - q)), int(75 + 55 * (1 - q))
    d.line([(0, y), (W, y)], fill=c)

# --- puntini sparsi: i cittadini "invisibili" ---
import random
random.seed(7)
punti = [(random.randint(60, W - 60), random.randint(90, H - 260)) for _ in range(46)]

# alcuni collegati fra loro (la rete che si forma), gli altri isolati
rete = punti[:14]
for i, p in enumerate(rete):
    for q in rete[i + 1:]:
        dist = ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5
        if dist < 230:
            d.line([p, q], fill=(232, 144, 10, 90), width=1)

# alone morbido sui punti connessi
glow = Image.new("RGB", (W, H), (0, 0, 0))
g = ImageDraw.Draw(glow)
for p in rete:
    g.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=(120, 74, 5))
glow = glow.filter(ImageFilter.GaussianBlur(9))
img = Image.blend(img, Image.blend(img, glow, 0.0), 0.0)
img.paste(Image.blend(img.copy(), glow, 0.45), (0, 0),
          glow.convert("L").point(lambda v: min(255, v * 3)))

d = ImageDraw.Draw(img)
for p in punti:
    connesso = p in rete
    r = 5 if connesso else 3
    col = ORO if connesso else (108, 116, 150)     # spenti = isolati
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)

# --- barra oro e titolo in basso ---
d.rectangle([(0, H - 210), (W, H)], fill=(9, 18, 52))
d.rectangle([(56, H - 176), (56 + 86, H - 170)], fill=ORO)

F = "/System/Library/Fonts/HelveticaNeue.ttc"
from PIL import ImageFont
f_big = ImageFont.truetype(F, 46, index=1)
f_sm = ImageFont.truetype(F, 25, index=0)

d.text((56, H - 148), "Non mancano", font=f_big, fill="white")
d.text((56, H - 96), "i cittadini attivi.", font=f_big, fill=ORO)
d.text((56, H - 42), "Manca che si vedano.", font=f_sm, fill=(190, 198, 225))

img.save(dst, "WEBP", quality=88, method=6)
print("creato:", dst, img.size)
