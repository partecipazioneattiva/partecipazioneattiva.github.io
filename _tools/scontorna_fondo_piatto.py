#!/usr/bin/env python3
"""Scontorna una figura fotografata su fondo PIATTO, senza modelli.

    python3 _tools/scontorna_fondo_piatto.py dentro.webp fuori.png
    python3 _tools/scontorna_fondo_piatto.py dentro.webp fuori.png --tolleranza 34

⭐ 12 agosto 2026. Fratello povero di `scontorna.py`, che usa BiRefNet: quello
ha bisogno di `onnxruntime`, che l'aggiornamento di Miniforge ha portato via.
Qui non serve nessun modello, perche' il fondo lo abbiamo CHIESTO piatto nel
prompt («one single flat uniform tone, no gradient, no vignette, no cast
shadow»): si riempie a partire dai bordi e si ferma dove il colore cambia.

⛔ Funziona SOLO su fondo uniforme. Su una fotografia vera, o su uno sfondo con
panorama, mangia mezza persona. Lo strumento se ne accorge da solo: se la
sagoma che resta e' piu' del 92% o meno dell'8% della tela, si ferma e lo dice.

🟨 I punti di partenza stanno su TUTTI e quattro i bordi. Nella versione
precedente (ritratti a mezzo busto) stavano solo in alto e sui fianchi fino al
42%, perche' piu' in basso il bordo era la giacca. Qui la figura e' intera con
la sdraio e non tocca nessun bordo, quindi si parte da tutto il perimetro.

Il bordo si mangia di un pixel (`--eroni`) per togliere l'alone del vecchio
fondo, e poi si sfuma: senza la sfumatura il contorno esce seghettato.
"""
import argparse
import sys
from collections import deque

from PIL import Image, ImageFilter


def scontorna(im, tolleranza):
    """Alfa 255 sulla figura, 0 sul fondo, partendo dai quattro bordi."""
    L, A = im.size
    px = im.load()
    fondo = deque()
    visto = bytearray(L * A)

    def semi():
        for x in range(L):
            yield x, 0
            yield x, A - 1
        for y in range(A):
            yield 0, y
            yield L - 1, y

    # il colore del fondo e' la media dei quattro angoli: se sono diversi fra
    # loro il fondo non e' piatto, e lo dira' il controllo finale
    angoli = [px[0, 0], px[L - 1, 0], px[0, A - 1], px[L - 1, A - 1]]
    rif = tuple(sum(c[i] for c in angoli) // 4 for i in range(3))

    def somiglia(c):
        return (abs(c[0] - rif[0]) + abs(c[1] - rif[1]) + abs(c[2] - rif[2])) <= tolleranza * 3

    for x, y in semi():
        i = y * L + x
        if not visto[i] and somiglia(px[x, y]):
            visto[i] = 1
            fondo.append((x, y))

    while fondo:
        x, y = fondo.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < L and 0 <= ny < A:
                j = ny * L + nx
                if not visto[j] and somiglia(px[nx, ny]):
                    visto[j] = 1
                    fondo.append((nx, ny))

    # ⛔ 12 agosto 2026: le zone di fondo CHIUSE dentro la figura — fra le gambe
    #    di una sdraio, dentro il telaio — non si raggiungono partendo dai bordi,
    #    e restavano grigie sopra la sabbia. Si tolgono con lo stesso identico
    #    controllo di colore, applicato ovunque. Funziona senza mangiare la
    #    persona solo se la tolleranza e' bassa: e' lo stesso motivo per cui la
    #    camicia di lino chiaro non viene toccata.
    dati = []
    for y in range(A):
        for x in range(L):
            i = y * L + x
            dati.append(0 if (visto[i] or somiglia(px[x, y])) else 255)
    alfa = Image.new("L", (L, A))
    alfa.putdata(dati)
    return alfa, rif


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sorgente")
    p.add_argument("uscita")
    p.add_argument("--tolleranza", type=int, default=30,
                   help="quanto puo' variare il fondo prima di non essere piu' "
                        "fondo (0-255 per canale, predefinito 30)")
    p.add_argument("--eroni", type=int, default=1,
                   help="pixel di bordo da mangiare: toglie l'alone del vecchio fondo")
    p.add_argument("--sfuma", type=float, default=1.0)
    a = p.parse_args()

    im = Image.open(a.sorgente).convert("RGB")
    alfa, rif = scontorna(im, a.tolleranza)

    quanti = sum(1 for v in alfa.getdata() if v > 128)
    quota = quanti / (im.width * im.height)
    print(f"  fondo misurato: RGB{rif} · figura {quota:.0%} della tela")
    if quota > 0.92:
        sys.exit("⛔ non ha staccato quasi niente: il fondo non e' piatto, "
                 "oppure la tolleranza e' troppo bassa. Alza --tolleranza.")
    if quota < 0.08:
        sys.exit("⛔ ha mangiato la figura: la tolleranza e' troppo alta, "
                 "oppure la persona ha lo stesso colore del fondo.")

    for _ in range(a.eroni):
        alfa = alfa.filter(ImageFilter.MinFilter(3))
    alfa = alfa.filter(ImageFilter.GaussianBlur(a.sfuma))

    fuori = im.convert("RGBA")
    fuori.putalpha(alfa)
    fuori.save(a.uscita)
    print(f"  ✅ {a.uscita}  {fuori.size}")


if __name__ == "__main__":
    main()
