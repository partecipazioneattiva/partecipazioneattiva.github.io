#!/usr/bin/env python3
"""Toglie la stellina dell'app Gemini dal ritratto madre.

    python3 _tools/togli_stellina.py in.png out.png
    python3 _tools/togli_stellina.py in.png out.png --angolo alto-destra

⭐ 12 agosto 2026. Nasce perche' l'app Gemini stampa una stellina sulle
immagini dei piani gratuito e AI Pro, e da noi si genera dall'app.
(aistudio.google.com non la mette, ma non e' la strada che usiamo.)

🟩 COME LA TROVA, invece di indovinare
La prima versione copriva un quadrato fisso nell'angolo. Su un ritratto (12
agosto) quel quadrato conteneva insieme il fondo chiaro e la spalla scura, la misura
del colore non aveva senso e lo strumento si e' fermato — giustamente, ma senza
concludere. Adesso la stellina si CERCA: e' un gruppetto di pixel piu' chiari
del loro intorno, e si trova confrontando l'immagine con la sua mediana.
Si copre solo il suo riquadro, allargato di poco.

🟩 PERCHE' SI PUO' COPRIRE SENZA ROVINARE NIENTE
Nel ritratto madre il fondo e' chiesto piatto e uniforme, e la stellina cade
in un angolo, lontano dalla persona. Qui non si ricostruisce niente: si rimette
il colore che c'e' tutto intorno, MISURATO su una cornice attorno al riquadro.

⛔ Se attorno alla stellina il colore NON e' uniforme — un bordo, una spalla,
una texture — lo strumento si FERMA e lo dice, invece di lasciare una toppa
che si vedra' solo dopo, sul manifesto stampato. In quel caso: si ritaglia
l'angolo, oppure ci si ricorda che scontornando la figura quell'angolo sparisce
da solo.

⚠️ Questo toglie il segno VISIBILE, non la marcatura invisibile che Google
mette dentro il file (SynthID): l'immagine resta riconoscibile come generata,
ed e' giusto cosi'. Che il materiale sia fatto con l'IA si dichiara.
"""
import argparse
import sys

import numpy as np
from PIL import Image, ImageFilter, ImageStat

QUADRANTE = 0.86    # dove cercare: l'ultimo 14% del lato, dal lato dell'angolo.
                    # ⛔ 12 agosto: col 30% la ricerca prendeva i capelli e la
                    # spalla, e il riquadro diventava mezzo ritratto.
CONTRASTO = 16      # quanto piu' chiara del suo intorno dev'essere la stellina
MARGINE = 8         # px di margine attorno al riquadro trovato
MASSIMO = 0.12      # oltre il 12% del lato corto non e' la stellina
CORNICE = 12        # px di cornice su cui si misura il colore del fondo
SOGLIA = 8.0        # scarto massimo ammesso sulla cornice (0-255)

ANGOLI = ("basso-destra", "basso-sinistra", "alto-destra", "alto-sinistra")


def cerca(im, angolo):
    """Il riquadro della stellina, o None: pixel piu' chiari del loro intorno."""
    g = im.convert("L")
    L, A = g.size
    scarto = (np.asarray(g).astype(int)
              - np.asarray(g.filter(ImageFilter.MedianFilter(9))).astype(int))
    x0 = 0 if "sinistra" in angolo else int(L * QUADRANTE)
    x1 = int(L * (1 - QUADRANTE)) if "sinistra" in angolo else L
    y0 = 0 if "alto" in angolo else int(A * QUADRANTE)
    y1 = int(A * (1 - QUADRANTE)) if "alto" in angolo else A
    ys, xs = np.where(scarto[y0:y1, x0:x1] > CONTRASTO)
    if len(xs) < 20:
        return None
    box = (max(0, x0 + xs.min() - MARGINE), max(0, y0 + ys.min() - MARGINE),
           min(L, x0 + xs.max() + 1 + MARGINE), min(A, y0 + ys.max() + 1 + MARGINE))
    # La stellina e' piccola. Se il riquadro viene grande, non e' lei: e'
    # dettaglio vero (capelli, un bordo) e coprirlo sarebbe un danno.
    tetto = min(L, A) * MASSIMO
    if box[2] - box[0] > tetto or box[3] - box[1] > tetto:
        print(f"  ⚠️  trovato un gruppo chiaro {box[2]-box[0]}x{box[3]-box[1]} px: "
              f"troppo grande per essere la stellina, non tocco niente")
        return None
    return box


def fondo(im, box):
    """Colore medio e variazione della cornice attorno al riquadro."""
    x0, y0, x1, y1 = box
    L, A = im.size
    fuori = im.crop((max(0, x0 - CORNICE), max(0, y0 - CORNICE),
                     min(L, x1 + CORNICE), min(A, y1 + CORNICE))).copy()
    fuori.paste((0, 0, 0), (CORNICE, CORNICE,
                            fuori.width - CORNICE, fuori.height - CORNICE))
    pixel = [p for p in list(fuori.getdata()) if p != (0, 0, 0)]
    if not pixel:
        sys.exit("⛔ cornice di controllo vuota")
    piatta = Image.new("RGB", (len(pixel), 1))
    piatta.putdata(pixel)
    st = ImageStat.Stat(piatta)
    return tuple(int(v) for v in st.mean), max(st.stddev)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ingresso")
    p.add_argument("uscita")
    p.add_argument("--angolo", choices=ANGOLI, default="basso-destra")
    p.add_argument("--forza", action="store_true",
                   help="copre anche se il fondo non e' uniforme (lascia una toppa)")
    p.add_argument("--ritaglia", action="store_true",
                   help="invece di coprire, TAGLIA la striscia che contiene la "
                        "stellina. E' la via onesta quando il fondo intorno non "
                        "e' uniforme: non si inventa un pixel, si tolgono quelli "
                        "che ci sono. Sul ritratto madre, inquadrato dal petto in "
                        "su con margine, qualche punto percentuale in meno non "
                        "toglie niente")
    a = p.parse_args()

    im = Image.open(a.ingresso).convert("RGB")
    box = cerca(im, a.angolo)
    if box is None:
        print(f"  nessuna stellina trovata in {a.angolo}: copio l'originale")
        im.save(a.uscita)
        return

    if a.ritaglia:
        L, A = im.size
        if "basso" in a.angolo:
            tagliata = im.crop((0, 0, L, box[1]))
            quanto = f"{A - box[1]} px dal basso ({(A - box[1]) / A:.0%})"
        else:
            tagliata = im.crop((0, box[3], L, A))
            quanto = f"{box[3]} px dall'alto ({box[3] / A:.0%})"
        tagliata.save(a.uscita)
        print(f"  ✅ {a.uscita} — tolti {quanto}, la stellina non c'e' piu'")
        print(f"     {im.size} → {tagliata.size}")
        return

    colore, scarto = fondo(im, box)
    print(f"  stellina trovata: {box[2]-box[0]}x{box[3]-box[1]} px in {box[:2]}")
    print(f"  fondo intorno: RGB{colore}, variazione {scarto:.1f}")
    if scarto > SOGLIA and not a.forza:
        sys.exit(f"⛔ attorno alla stellina il fondo NON e' uniforme "
                 f"(variazione {scarto:.1f} > {SOGLIA}): una toppa si vedrebbe. "
                 f"Ritaglia l'angolo, oppure lascia stare — scontornando la "
                 f"figura quell'angolo sparisce da solo.")

    im.paste(colore, box)
    im.save(a.uscita)
    print(f"  ✅ {a.uscita} — stellina coperta col colore del fondo")


if __name__ == "__main__":
    main()
