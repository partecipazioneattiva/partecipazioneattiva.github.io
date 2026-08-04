#!/usr/bin/env python3
"""Rimette il SIMBOLO VERO su un manifesto generato, con la X dell'istruzione
di voto tracciata come si deve.

    python3 _tools/sostituisci_simbolo.py --manifesto m.png --logo LOGO-PA.webp \\
        --uscita m_corretto.png

⛔ PERCHE' ESISTE (4 agosto 2026)
I generatori il logo lo RIDISEGNANO, e la X la tracciano dove capita: su due
manifesti su tre "PARTECIPAZIONE" e' uscito come "PA TECIPAZI NE", con due
lettere mangiate dai tratti. Il simbolo pero' e' l'unica cosa che l'elettore
deve ritrovare sulla scheda: una versione somigliante non serve a niente.
Qui il logo e' il FILE VERO, incollato sopra quello disegnato, e la X e'
tracciata al centro, sottile e semitrasparente, senza toccare l'anello delle
lettere.

La posizione di default e' l'angolo in basso a sinistra, dove la mettono i
nostri manifesti. Si sposta con --x --y --lato, tutti in frazioni di
larghezza/altezza della tela, cosi' valgono a qualunque misura.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROSSO_PA = (218, 81, 52)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--manifesto", required=True)
    p.add_argument("--logo", required=True)
    p.add_argument("--uscita", required=True)
    p.add_argument("--x", type=float, default=0.035, help="bordo sinistro, in frazioni di larghezza")
    p.add_argument("--y", type=float, default=0.862, help="bordo alto, in frazioni di altezza")
    p.add_argument("--lato", type=float, default=0.185, help="diametro, in frazioni di larghezza")
    p.add_argument("--copri", type=float, default=1.22,
                   help="quanto allargare la toppa che cancella il logo disegnato")
    p.add_argument("--spessore", type=float, default=0.095,
                   help="spessore dei tratti della X, in frazioni del diametro")
    p.add_argument("--opacita", type=float, default=0.95,
                   help="opacita' della X, da 0 a 1")
    p.add_argument("--senza-x", action="store_true", dest="senza_x",
                   help="incolla il logo pulito, senza tracciare la X")
    a = p.parse_args()

    m = Image.open(a.manifesto).convert("RGB")
    W, H = m.size
    lato = int(W * a.lato)
    x, y = int(W * a.x), int(H * a.y)

    # 1. la toppa. Il colore NON si prende da un angolo solo: si prende la media
    #    dell'anello che sta appena fuori dall'area da coprire. Campionando un
    #    angolo si becca il punto piu' scuro e resta un alone (visto su Paolo,
    #    4 agosto 2026: giacca grigio scura, campione (3,3,2) quasi nero).
    r = int(lato * a.copri / 2)
    cx, cy = x + lato // 2, y + lato // 2
    re = int(r * 1.30)
    box = (max(0, cx - re), max(0, cy - re), min(W, cx + re), min(H, cy + re))
    intorno = m.crop(box)
    anello = Image.new("L", intorno.size, 255)
    ImageDraw.Draw(anello).ellipse(
        (re - (cx - box[0]) + (cx - box[0]) - r, re - (cy - box[1]) + (cy - box[1]) - r,
         (cx - box[0]) + r, (cy - box[1]) + r), fill=0)
    # ⚠️ MEDIANA, non media: l'anello puo' toccare una zona di colore diverso
    #    (su Paolo prendeva anche la colonna beige e la toppa usciva schiarita).
    #    La mediana ignora la minoranza e tiene il colore dominante.
    px = [p for p, msk in zip(intorno.getdata(), anello.getdata()) if msk]
    if px:
        fondo = tuple(sorted(c[i] for c in px)[len(px) // 2] for i in range(3))
    else:
        fondo = (0, 0, 0)

    # ⚠️ La sfumatura mangia il bordo della toppa: il nucleo PIENO deve arrivare
    #    oltre i tratti da coprire, o quelli riaffiorano dove la maschera e'
    #    semitrasparente. Percio' si disegna il disco pieno e si sfuma solo il
    #    contorno, invece di sfumare tutta la toppa.
    sfuma = int(lato * 0.10)
    toppa = Image.new("RGB", (2 * r, 2 * r), fondo)
    masc = Image.new("L", (2 * r, 2 * r), 0)
    ImageDraw.Draw(masc).ellipse((sfuma, sfuma, 2 * r - 1 - sfuma, 2 * r - 1 - sfuma),
                                 fill=255)
    masc = masc.filter(ImageFilter.GaussianBlur(sfuma * 0.55))
    m.paste(toppa, (cx - r, cy - r), masc)

    # 2. il logo vero, alla misura chiesta
    logo = Image.open(a.logo).convert("RGBA").resize((lato, lato), Image.LANCZOS)
    m.paste(logo, (x, y), logo)

    # 3. la X: due tratti sottili, semitrasparenti, che restano DENTRO il
    #    disco centrale e non arrivano sull'anello dove stanno le lettere.
    if not a.senza_x:
        segno = Image.new("RGBA", (lato, lato), (0, 0, 0, 0))
        d = ImageDraw.Draw(segno)
        # ⚠️ Il 23,5% dal bordo NON si tocca: e' la misura che tiene i tratti
        #    dentro il disco e lascia libero l'anello delle lettere. Se la X e'
        #    poco evidente si aumentano SPESSORE e OPACITA', non la lunghezza:
        #    allungandola si torna a mangiare "PA" e "NE" di PARTECIPAZIONE.
        bordo = int(lato * 0.235)
        sp = max(2, int(lato * a.spessore))
        alfa = int(255 * a.opacita)
        d.line((bordo, bordo, lato - bordo, lato - bordo), fill=ROSSO_PA + (alfa,), width=sp)
        d.line((lato - bordo, bordo, bordo, lato - bordo), fill=ROSSO_PA + (alfa,), width=sp)
        m.paste(segno, (x, y), segno)

    m.save(a.uscita, dpi=(120, 120))
    print("manifesto corretto:", a.uscita, m.size)
    print(f"   simbolo: {lato}px a ({x}, {y})  ·  fondo della toppa: {fondo}")
    print("   se il simbolo non e' centrato sul suo posto, si sposta con --x --y --lato")


if __name__ == "__main__":
    main()
