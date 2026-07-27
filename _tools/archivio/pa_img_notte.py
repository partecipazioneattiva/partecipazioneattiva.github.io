import shutil, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path("/Users/luigia/SITO-PA")
DL = Path("/Users/luigia/Downloads")

# 1) locandina -> webp verticale (card + articolo)
loc = Image.open(DL / "evento.jpeg").convert("RGB")
print("locandina originale:", loc.size)
out = BASE / "images" / "notte-democrazia.webp"
l = loc.copy()
l.thumbnail((900, 1200), Image.LANCZOS)
l.save(out, "WEBP", quality=88, method=6)
print("creato:", out, l.size)

# 2) volantino -> webp (immagine dentro l'articolo)
vol = Image.open(DL / "evento1.jpeg").convert("RGB")
print("volantino originale:", vol.size)
out2 = BASE / "images" / "volantino-melonellum.webp"
v = vol.copy()
v.thumbnail((1400, 1000), Image.LANCZOS)
v.save(out2, "WEBP", quality=86, method=6)
print("creato:", out2, v.size)

# 3) OG orizzontale 1200x630 dalla locandina (per Facebook)
W, H = 1200, 630
og = Image.new("RGB", (W, H), (18, 22, 30))

# sfondo: locandina sfocata, riempie tutto
bg = loc.copy()
r = max(W / bg.width, H / bg.height)
bg = bg.resize((round(bg.width * r), round(bg.height * r)), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2,
              (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
bg = bg.filter(ImageFilter.GaussianBlur(18))
og.paste(Image.blend(og, bg, 0.45), (0, 0))

# locandina intera a destra, nitida
card = loc.copy()
card.thumbnail((int(H * 0.86 * loc.width / loc.height), int(H * 0.86)), Image.LANCZOS)
og.paste(card, (W - card.width - 60, (H - card.height) // 2))

d = ImageDraw.Draw(og)
F = "/System/Library/Fonts/HelveticaNeue.ttc"
f_occ = ImageFont.truetype(F, 22, index=1)
f_big = ImageFont.truetype(F, 50, index=1)
f_sm = ImageFont.truetype(F, 26, index=0)

x = 66
d.text((x, 138), "PARTECIPAZIONE ATTIVA", font=f_occ, fill=(200, 60, 60))
d.rectangle([(x, 182), (x + 80, 187)], fill=(200, 60, 60))
d.text((x, 220), "Stasera siamo", font=f_big, fill="white")
d.text((x, 278), "a Montecitorio", font=f_big, fill="white")
d.text((x, 372), "Notte della Democrazia", font=f_sm, fill=(235, 235, 235))
d.text((x, 410), "Marted\u00ec 14 luglio, dalle 18.00", font=f_sm, fill=(190, 190, 190))
d.text((x, 448), "Roma, Piazza Montecitorio", font=f_sm, fill=(190, 190, 190))

og.save(BASE / "images" / "notte-democrazia-og.jpg", "JPEG", quality=90, optimize=True)
print("creato: notte-democrazia-og.jpg", og.size)
