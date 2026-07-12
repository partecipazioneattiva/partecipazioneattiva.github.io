from pathlib import Path
from PIL import Image

BASE = Path("/Users/luigia/SITO-PA")
src = BASE / "images" / "og-src.png"
dst = BASE / "images" / "mappa-og.jpg"

im = Image.open(src).convert("RGB")
print("originale:", im.size)

W, H = 1200, 630
r = max(W / im.width, H / im.height)
im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
left = (im.width - W) // 2
top  = (im.height - H) // 2
im = im.crop((left, top, left + W, top + H))
im.save(dst, "JPEG", quality=90, optimize=True)
print("creato:", dst, im.size)
