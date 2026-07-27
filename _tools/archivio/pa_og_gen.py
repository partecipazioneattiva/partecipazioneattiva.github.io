from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path("/Users/luigia/SITO-PA")
dst  = BASE / "images" / "mappa-og.jpg"
W, H = 1200, 630
BLU, ORO, PANNA = (13,27,75), (232,144,10), (255,253,248)

img = Image.new("RGB", (W, H), BLU)
d = ImageDraw.Draw(img)

# fascia oro a destra
d.rectangle([(500,0),(W,H)], fill=(138,78,0))
for x in range(500, W):
    q = (x-500)/(W-500)
    d.line([(x,0),(x,H)], fill=(int(138+94*q), int(78+66*q), int(0+10*q)))

# sagoma Italia a sinistra
it = Image.open(BASE/"images"/"mappa-italia.webp").convert("RGBA")
it.thumbnail((430, 540), Image.LANCZOS)
img.paste(it, (40, (H-it.height)//2), it)

F = "/System/Library/Fonts/HelveticaNeue.ttc"
f_occ = ImageFont.truetype(F, 24, index=1)
f_tit = ImageFont.truetype(F, 58, index=1)
f_sub = ImageFont.truetype(F, 30, index=0)

x = 560
d.text((x, 90), "LA MAPPA DI PARTECIPAZIONE ATTIVA", font=f_occ, fill=(255,224,160))
d.text((x, 150), "Chi siamo,", font=f_tit, fill="white")
d.text((x, 218), "dove siamo,", font=f_tit, fill="white")
d.text((x, 286), "cosa ci sta a cuore.", font=f_tit, fill=(255,240,200))
d.text((x, 390), "Cittadini e associazioni in Italia e nel mondo.", font=f_sub, fill=(255,255,255))
d.text((x, 430), "Cerca per tema o competenza e trova chi si", font=f_sub, fill=(255,255,255))
d.text((x, 470), "batte per le stesse cose vicino a te.", font=f_sub, fill=(255,255,255))
d.rectangle([(x,530),(x+300,534)], fill="white")
d.text((x, 548), "partecipazione-attiva.it/mappa", font=f_sub, fill=(255,255,255))

img.save(dst, "JPEG", quality=92, optimize=True)
print("creato:", dst, img.size)
