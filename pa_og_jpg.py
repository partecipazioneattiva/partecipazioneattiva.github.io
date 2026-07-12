from pathlib import Path
from PIL import Image

BASE = Path("/Users/luigia/SITO-PA")
src = BASE / "images" / "mappa-italia.webp"
dst = BASE / "images" / "mappa-og.jpg"

im = Image.open(src).convert("RGB")
print("originale:", im.size)

# canvas 1200x630, immagine centrata senza deformarla
W, H = 1200, 630
im.thumbnail((W, H), Image.LANCZOS)
canvas = Image.new("RGB", (W, H), (255, 253, 248))
canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
canvas.save(dst, "JPEG", quality=88, optimize=True)
print("creato:", dst, canvas.size)

# aggiorna il tag og:image in mappa.html
f = BASE / "mappa.html"
t = f.read_text(encoding="utf-8")
vecchio = 'content="https://partecipazione-attiva.it/images/mappa-italia.webp"'
nuovo   = 'content="https://partecipazione-attiva.it/images/mappa-og.jpg"'
if vecchio in t:
    t = t.replace(vecchio, nuovo)
    print("og:image aggiornato")
else:
    print("ATTENZIONE: og:image non trovato, controllare a mano")

# aggiunge i tag mancanti che FB usa
extra = ('<meta property="og:type" content="website">\n'
         '<meta property="og:url" content="https://partecipazione-attiva.it/mappa.html">\n'
         '<meta property="og:image:width" content="1200">\n'
         '<meta property="og:image:height" content="630">\n'
         '<meta name="twitter:card" content="summary_large_image">\n')
if 'og:image:width' not in t:
    t = t.replace(nuovo + '>', nuovo + '>\n' + extra.rstrip(), 1)

f.write_text(t, encoding="utf-8")
print("OK - mappa.html aggiornata")
