import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path("/Users/luigia/SITO-PA")
dst = BASE / "images" / "cittadini-attivi-og.jpg"

W, H = 1200, 630
BLU, ORO = (13, 27, 75), (232, 144, 10)

img = Image.new("RGB", (W, H), BLU)
d = ImageDraw.Draw(img)
for y in range(H):
    q = abs(y - H / 2) / (H / 2)
    d.line([(0, y), (W, y)],
           fill=(int(13 + 24 * (1 - q)), int(27 + 30 * (1 - q)), int(75 + 50 * (1 - q))))

# punti: alcuni connessi (oro), i piu' isolati (spenti) — a destra
random.seed(7)
punti = [(random.randint(640, W - 60), random.randint(70, H - 70)) for _ in range(38)]
rete = punti[:12]
for i, p in enumerate(rete):
    for q in rete[i + 1:]:
        if ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5 < 210:
            d.line([p, q], fill=(150, 96, 20), width=1)

glow = Image.new("RGB", (W, H), (0, 0, 0))
g = ImageDraw.Draw(glow)
for p in rete:
    g.ellipse([p[0] - 12, p[1] - 12, p[0] + 12, p[1] + 12], fill=(130, 80, 6))
glow = glow.filter(ImageFilter.GaussianBlur(10))
img.paste(Image.blend(img.copy(), glow, 0.5), (0, 0),
          glow.convert("L").point(lambda v: min(255, v * 3)))

d = ImageDraw.Draw(img)
for p in punti:
    c = p in rete
    r = 6 if c else 3
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r],
              fill=ORO if c else (105, 113, 148))

# testo a sinistra
F = "/System/Library/Fonts/HelveticaNeue.ttc"
f_occ = ImageFont.truetype(F, 21, index=1)
f_big = ImageFont.truetype(F, 52, index=1)
f_sm = ImageFont.truetype(F, 25, index=0)

x = 70
d.text((x, 132), "PARTECIPAZIONE ATTIVA", font=f_occ, fill=(150, 160, 200))
d.rectangle([(x, 176), (x + 84, 182)], fill=ORO)
d.text((x, 214), "Non mancano", font=f_big, fill="white")
d.text((x, 276), "i cittadini attivi.", font=f_big, fill=ORO)
d.text((x, 350), "Manca che si vedano.", font=f_big, fill="white")
d.text((x, 448), "Ogni comitato riparte da zero. Il problema", font=f_sm, fill=(185, 193, 220))
d.text((x, 482), "non \u00e8 la scarsit\u00e0 di persone: \u00e8 che sono", font=f_sm, fill=(185, 193, 220))
d.text((x, 516), "invisibili le une alle altre.", font=f_sm, fill=(185, 193, 220))

img.save(dst, "JPEG", quality=90, optimize=True)
print("creato:", dst, img.size)

# --- solo i meta social puntano a questa ---
A = BASE / "mappa-cittadini-attivi.html"
t = A.read_text(encoding="utf-8")
import re
n = 0
for tag in ('property="og:image" content="', 'name="twitter:image" content="'):
    pat = re.compile(re.escape(tag) + r'[^"]*"')
    t, k = pat.subn(tag + 'https://partecipazione-attiva.it/images/cittadini-attivi-og.jpg"', t)
    n += k
A.write_text(t, encoding="utf-8")
print("meta social aggiornati:", n)
