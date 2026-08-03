#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QR code di Partecipazione Attiva — per manifesti, volantini, banchetti.

Un QR generato qui e' un file vettoriale-per-costruzione: nessun modello
generativo, nessuna approssimazione, si scansiona sempre. (I generatori di
immagini che «disegnano» QR sono una scommessa: questo no.)

Correzione d'errore alta (H, 30%): sopporta il logo al centro, la pioggia sul
manifesto e la stampa mal registrata.

Uso:
    python3 _tools/crea_qr.py                       # iscrizione alla Mappa
    python3 _tools/crea_qr.py --url https://... --uscita qr.png
    python3 _tools/crea_qr.py --logo LOGO-PA.webp   # con il marchio al centro

⚠️ Dopo la generazione si INQUADRA COL TELEFONO prima di mandare in stampa:
   e' l'unica verifica che conta, e costa cinque secondi.
"""

import argparse
import os

import segno

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# I collegamenti buoni del sito, cosi' non si sbaglia a digitarli.
DESTINAZIONI = {
    "iscriviti": "https://partecipazione-attiva.it/#iscriviti",
    "mappa":     "https://partecipazione-attiva.it/mappa.html",
    "sito":      "https://partecipazione-attiva.it/",
    "azioni":    "https://partecipazione-attiva.it/azioni.html",
    "documenti": "https://partecipazione-attiva.it/documenti.html",
}


def segnaposto(lato, colore=(13, 27, 75)):
    """Disegna il pin della Mappa: goccia piena con il foro bianco, la sagoma
    che chiunque riconosce a colpo d'occhio. Serve a distinguere al volo il QR
    della Mappa da quello dell'iscrizione, che porta il logo."""
    from PIL import Image, ImageDraw
    s = 8                                        # si disegna in grande e si riduce
    W = H = lato * s
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)

    r = int(W * 0.34)
    cx, cy = W // 2, int(H * 0.38)
    dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=colore)     # testa
    dr.polygon([(cx - int(r * 0.80), cy + int(r * 0.60)),         # punta
                (cx + int(r * 0.80), cy + int(r * 0.60)),
                (cx, int(H * 0.95))], fill=colore)
    foro = int(r * 0.42)
    dr.ellipse((cx - foro, cy - foro, cx + foro, cy + foro), fill=(255, 255, 255, 255))
    return im.resize((lato, lato), Image.LANCZOS)


def crea(url, uscita, lato_px, logo=None, scuro="#0D1B4B", chiaro="white",
         simbolo=""):
    qr = segno.make(url, error="h")

    # bordo 4 moduli: e' il minimo dello standard, sotto quello certi lettori
    # non agganciano piu' il codice
    moduli = qr.symbol_size(scale=1, border=4)[0]
    scala = max(1, round(lato_px / moduli))

    qr.save(uscita, scale=scala, border=4, dark=scuro, light=chiaro)

    if logo or simbolo:
        from PIL import Image
        im = Image.open(uscita).convert("RGBA")
        lg = (segnaposto(int(im.width * 0.22)) if simbolo == "pin"
              else Image.open(logo).convert("RGBA"))
        lato = int(im.width * 0.22)          # oltre il 25% si perde la lettura
        lg = lg.resize((lato, int(lg.height * lato / lg.width)), Image.LANCZOS)
        pad = int(lato * 0.10)
        fondo = Image.new("RGBA", (lg.width + 2 * pad, lg.height + 2 * pad),
                          (255, 255, 255, 255))
        fondo.paste(lg, (pad, pad), lg)
        im.paste(fondo, ((im.width - fondo.width) // 2,
                         (im.height - fondo.height) // 2), fondo)
        im.convert("RGB").save(uscita)

    return uscita


def main():
    p = argparse.ArgumentParser(description="QR code di Partecipazione Attiva")
    p.add_argument("--dove", choices=sorted(DESTINAZIONI), default="iscriviti",
                   help="scorciatoia per le pagine del sito")
    p.add_argument("--url", default="", help="indirizzo libero, ha la precedenza")
    p.add_argument("--lato", type=int, default=2000, help="lato in pixel")
    p.add_argument("--logo", default="", help="logo da mettere al centro")
    p.add_argument("--simbolo", choices=("", "pin"), default="",
                   help="pin = segnaposto della Mappa al centro, al posto del logo")
    p.add_argument("--colore", default="#0D1B4B", help="colore dei moduli")
    p.add_argument("--uscita", default="")
    a = p.parse_args()

    url = a.url or DESTINAZIONI[a.dove]
    uscita = os.path.expanduser(a.uscita or f"qr_{a.dove}.png")
    logo = a.logo and (a.logo if os.path.isabs(a.logo) else os.path.join(REPO, a.logo))

    crea(url, uscita, a.lato, logo or None, a.colore, simbolo=a.simbolo)
    print("QR:", uscita, "->", url)
    print("Inquadralo col telefono PRIMA di mandarlo in stampa.")


if __name__ == "__main__":
    main()
