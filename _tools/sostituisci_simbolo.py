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

🟩 IL SEGNO E' ROSSO SU TUTTI I MANIFESTI — deciso da Fernando il 4 agosto 2026.
Il confronto a tre (nera, nera con contorno, rossa) sul manifesto di Paolo aveva
mostrato che sulla giacca scura il nero sparisce fuori dal simbolo, mentre su
Antonio e Rosa — fondo pergamena — il nero si sarebbe visto benissimo ed e'
piu' fedele alla matita copiativa. La scelta e' comunque il rosso per tutti:
dieci manifesti devono sembrare una campagna sola, e un segno che cambia colore
da candidato a candidato smette di essere un segno e diventa decorazione.
⛔ Non "ottimizzare" il colore manifesto per manifesto: e' gia' stato valutato.
"""
import argparse
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROSSO_PA    = (218, 81, 52)
NERO_MATITA = (38, 34, 44)   # il nero-bluastro della matita copiativa


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
    p.add_argument("--colore", choices=("rosso", "nero"), default="rosso",
                   help="rosso = la scelta di PA, uguale su tutti i manifesti "
                        "(default); nero = il segno della matita copiativa, "
                        "ma sparisce sui fondi scuri")
    p.add_argument("--contorno", action="store_true",
                   help="filo chiaro attorno ai tratti: serve col nero su fondo scuro")
    p.add_argument("--sborda", type=float, default=0.10,
                   help="quanto il segno esce dal simbolo, in frazioni del diametro")
    p.add_argument("--velo", type=float, default=0.42,
                   help="quanto si attenua il tratto sull'anello delle lettere (0-1)")
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
        # Il segno esce dal simbolo, come lo traccia una mano sulla scheda. Ma
        # dove attraversa l'ANELLO DELLE LETTERE il tratto si attenua: cosi'
        # sborda e "PARTECIPAZIONE" resta leggibile. Tenere la X corta dentro
        # il disco la rendeva timida; allungarla piena mangiava due lettere.
        sb = int(lato * a.sborda)
        L = lato + 2 * sb
        segno = Image.new("RGBA", (L, L), (0, 0, 0, 0))
        d = ImageDraw.Draw(segno)
        sp = max(2, int(lato * a.spessore))
        colore = NERO_MATITA if a.colore == "nero" else ROSSO_PA
        alfa = int(255 * a.opacita)
        # ⚠️ Con il segno NERO, la parte che sborda finisce sul fondo scuro del
        #    manifesto e sparisce — proprio il pezzo che doveva vedersi. Un filo
        #    di contorno chiaro lo stacca dal fondo senza togliergli il
        #    carattere di matita. Sul rosso non serve.
        if a.contorno:
            spc = sp + max(2, int(lato * 0.030))
            for p0, p1 in (((0, 0), (L - 1, L - 1)), ((L - 1, 0), (0, L - 1))):
                d.line(p0 + p1, fill=(250, 244, 226, 190), width=spc)
        d.line((0, 0, L - 1, L - 1), fill=colore + (alfa,), width=sp)
        d.line((L - 1, 0, 0, L - 1), fill=colore + (alfa,), width=sp)

        # attenuazione sull'anello delle parole (dal 74% al 102% del raggio)
        fatt = Image.new("L", (L, L), 255)
        df = ImageDraw.Draw(fatt)
        R = lato / 2.0
        c = L / 2.0
        df.ellipse((c - R * 1.02, c - R * 1.02, c + R * 1.02, c + R * 1.02),
                   fill=int(255 * a.velo))
        df.ellipse((c - R * 0.74, c - R * 0.74, c + R * 0.74, c + R * 0.74), fill=255)
        fatt = fatt.filter(ImageFilter.GaussianBlur(max(1, int(lato * 0.02))))
        segno.putalpha(ImageChops.multiply(segno.split()[3], fatt))

        m.paste(segno, (x - sb, y - sb), segno)

    m.save(a.uscita, dpi=(120, 120))
    print("manifesto corretto:", a.uscita, m.size)
    print(f"   simbolo: {lato}px a ({x}, {y})  ·  fondo della toppa: {fondo}")
    print("   se il simbolo non e' centrato sul suo posto, si sposta con --x --y --lato")


if __name__ == "__main__":
    main()
