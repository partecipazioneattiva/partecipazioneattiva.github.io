#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scrive il testo della card social sul PANNELLO VUOTO generato dall'IA.

    python3 _tools/carta_social.py --immagine ~/Desktop/rosa_vuota.png \
        --candidato rosa

⭐ PERCHE' IL TESTO NON LO SCRIVE PIU' IL GENERATORE (4 agosto 2026)
Il 4 agosto la riga della carica e' sparita da una card generata: quando la
colonna e' piena il modello non rimpicciolisce, TAGLIA, e taglia in mezzo —
dove stanno la carica e l'istruzione di voto. In piu' perde gli accenti
(MUNICIPALITA senza la A grave) e stampa le virgolette che trova nel prompt.
Qui il testo e' vettoriale, identico su tutti i candidati, con gli accenti
giusti, e la carica e l'istruzione di voto si derivano dal RUOLO come in
crea_prompt_manifesto.py: sbagliarle costa voti veri.

All'IA si chiede solo la fotografia:
    python3 _tools/crea_prompt_manifesto.py --candidato rosa --stile card-vuota

⛔ IL BORDO DEL PANNELLO SI MISURA, NON SI INDOVINA. Al generatore chiediamo
il 45% della larghezza e lui ne fa quello che vuole (sulla prima prova di Rosa
e' uscito il 50%). Qui si misura sul file vero, colonna per colonna, e con
--bordo si forza a mano se la misura sbaglia.
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifesto_classico import (adatta, font, larghezza, prepara_font,  # noqa: E402
                                scrivi, LAPIDARIO, SERIF_TESTO)

DATI = "~/Desktop/GEMINI LAVORI/candidati_manifesto.json"
LAVORI = "~/Desktop/GEMINI LAVORI"
ITALICO = "merriweather-400-italic.ttf"

BRUNO = (58, 36, 20)
ORO = (166, 124, 47)

CARICA = {"presidente": "CANDIDAT{a} ALLA PRESIDENZA",
          "consigliere": "CANDIDAT{a} AL CONSIGLIO"}
VOTO = {"presidente": "sulla scheda della Municipalità",
        "consigliere": "e scrivi {cognome} sulla scheda"}


def misura_pannello(im):
    """Larghezza del pannello vuoto, in pixel.

    ⛔ Prima prova, sbagliata: confrontare ogni colonna con il colore del bordo
    sinistro. Sulla card di Rosa il pannello aveva una velatura dorata che
    scurisce di qualche punto, e la misura si fermava a 8 px su 848.
    Quello che distingue davvero le due meta' non e' il COLORE ma la
    VARIAZIONE: la pergamena e' liscia (scarto quadratico medio quasi zero
    lungo la colonna), il panorama no. Qui si cerca la prima colonna
    "mossa", e se ne pretendono alcune di fila per non cadere su un artefatto.
    """
    px = im.convert("L")
    w, h = px.size
    passo = max(1, h // 120)

    def mosso(x):
        col = [px.getpixel((x, y)) for y in range(0, h, passo)]
        media = sum(col) / len(col)
        return (sum((v - media) ** 2 for v in col) / len(col)) ** 0.5

    liscio = sorted(mosso(x) for x in range(2, max(6, w // 20)))
    soglia = max(6.0, 4 * liscio[len(liscio) // 2] + 3)
    di_fila = 0
    for x in range(w // 20, w):
        if mosso(x) > soglia:
            di_fila += 1
            if di_fila >= 4:
                return x - 3, soglia
        else:
            di_fila = 0
    return w // 2, soglia


def blocchi(c, com):
    """I dieci blocchi del prompt, nello stesso ordine.

    Ogni voce e' un GRUPPO: (tipo, [righe], font, corpo_max_rel, spaziatura,
    colore). Le righe di uno stesso gruppo prendono lo STESSO corpo — quello
    della piu' lunga — se no "ATTIVA" esce grande il doppio di
    "PARTECIPAZIONE" solo perche' e' piu' corta.
    """
    f = c["genere"] == "f"
    carica = CARICA[c["ruolo"]].format(a="A" if f else "O")
    voto = VOTO[c["ruolo"]].format(cognome=c["cognome"])
    return [
        ("logo", [], None, 0.52, 0, None),
        ("testo", ["PARTECIPAZIONE", "ATTIVA"], LAPIDARIO, 0.088, 0.06, BRUNO),
        ("filo", [], None, 0.34, 0, ORO),
        ("testo", [c["nome"].title(), c["cognome"].title()], SERIF_TESTO, 0.20, 0.0, BRUNO),
        ("filo", [], None, 0.34, 0, ORO),
        ("testo", [carica, "DELLA MUNICIPALITÀ 10"], LAPIDARIO, 0.058, 0.02, BRUNO),
        ("testo", [f"{com['elezione']} 2027"], LAPIDARIO, 0.050, 0.02, ORO),
        ("testo", [com["territorio_card"]], ITALICO, 0.046, 0.0, BRUNO),
        ("testo", ["BARRA IL SIMBOLO"], LAPIDARIO, 0.066, 0.03, BRUNO),
        ("testo", [voto], ITALICO, 0.046, 0.0, BRUNO),
        ("testo", [com["sito"]], LAPIDARIO, 0.034, 0.05, BRUNO),
        ("testo", [f"Committente responsabile: {com['committente']}"], ITALICO,
         0.030, 0.0, BRUNO),
    ]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--immagine", required=True, help="la card generata col pannello VUOTO")
    p.add_argument("--candidato", required=True, help="chiave nel JSON (es. rosa)")
    p.add_argument("--dati", default=DATI)
    p.add_argument("--logo", help="il simbolo vero (default: logo_pa.png della sua cartella)")
    p.add_argument("--bordo", type=float,
                   help="frazione di larghezza del pannello, se la misura sbaglia (es. 0.5)")
    p.add_argument("--margine", type=float, default=0.09,
                   help="margine interno del pannello, in frazione della sua larghezza")
    p.add_argument("--uscita", help="file di uscita (default: <immagine>_card.jpg)")
    a = p.parse_args()

    percorso = os.path.expanduser(a.dati)
    if not os.path.exists(percorso):
        sys.exit(f"⛔ impostazioni non trovate: {percorso}")
    d = json.load(open(percorso, encoding="utf-8"))
    k = a.candidato.lower()
    if k not in d["candidati"]:
        sys.exit(f"⛔ '{k}' non c'e'. Disponibili: {', '.join(d['candidati'])}")
    c, com = d["candidati"][k], d["_comuni"]
    if "[" in com["committente"]:
        print("⚠️  il committente e' ancora un segnaposto: obbligatorio per legge "
              "prima di pubblicare (L. 212/1956 art. 3).", file=sys.stderr)

    prepara_font()
    im = Image.open(os.path.expanduser(a.immagine)).convert("RGB")
    W, H = im.size
    bordo, soglia = misura_pannello(im)
    if a.bordo:
        bordo = int(W * a.bordo)
    print(f"pannello: {bordo} px su {W} ({bordo / W:.3f} della larghezza), "
          f"soglia {soglia:.1f}", file=sys.stderr)
    if bordo < W * 0.25:
        sys.exit("⛔ pannello troppo stretto: o l'immagine non e' quella vuota, "
                 "o la misura ha sbagliato. Forzarla con --bordo 0.45")

    logo = a.logo or os.path.join(os.path.expanduser(LAVORI),
                                  c["cartella_foto"].split("/")[1], "logo_pa.png")
    logo = os.path.expanduser(logo)
    if not os.path.exists(logo):
        sys.exit(f"⛔ simbolo non trovato: {logo}")

    margine = int(bordo * a.margine)
    largh = bordo - 2 * margine
    x0 = margine

    # Prima passata: corpo e altezza di ogni gruppo. Le righe di un gruppo
    # condividono il corpo della piu' lunga.
    voci = []
    for tipo, righe, f_font, rel, sp_rel, colore in blocchi(c, com):
        if tipo == "logo":
            voci.append((tipo, [], None, 0, int(largh * rel), colore))
        elif tipo == "filo":
            voci.append((tipo, [], None, 0, max(2, int(W * 0.0028)), colore))
        else:
            corpo = min(adatta(r, f_font, largh, W * rel, sp_rel)[1] for r in righe)
            fnt = font(f_font, corpo)
            # Il nome e' grande: alla stessa interlinea relativa delle righe
            # piccole le due righe si staccherebbero come due blocchi diversi.
            passo = int(corpo * (1.06 if corpo > W * 0.10 else 1.22))
            # L'altezza del gruppo comprende la discendente dell'ultima riga:
            # senza, il filo d'oro si posa sulla "p" di Spanu.
            voci.append((tipo, righe, (fnt, corpo * sp_rel, passo),
                         corpo, passo * (len(righe) - 1) + int(corpo * 1.32),
                         colore))

    alto = sum(v[4] for v in voci)
    vuoto = H - 2 * int(H * 0.055) - alto
    if vuoto < 0:
        sys.exit("⛔ il testo non ci sta: pannello troppo stretto o immagine bassa.")
    # Lo spazio avanzato non si distribuisce uguale: attorno al logo e ai fili
    # ci vuole aria, fra due gruppi di seguito molto meno.
    pesi = []
    for i, v in enumerate(voci[:-1]):
        succ = voci[i + 1]
        pesi.append(1.7 if v[0] in ("logo", "filo") or succ[0] == "filo" else 1.0)
    tot = sum(pesi) or 1

    dr = ImageDraw.Draw(im)
    y = int(H * 0.055)
    for i, (tipo, righe, dati_font, corpo, h, colore) in enumerate(voci):
        if tipo == "logo":
            sim = Image.open(logo).convert("RGBA").resize((h, h), Image.LANCZOS)
            im.paste(sim, (x0, y), sim)
        elif tipo == "filo":
            dr.rectangle([x0, y, x0 + int(largh * 0.34), y + h], fill=colore)
        else:
            fnt, sp, passo = dati_font
            for j, r in enumerate(righe):
                scrivi(dr, (x0, y + passo * j + corpo), r, fnt, colore, sp,
                       ancora="ls")
        y += h
        if i < len(pesi):
            y += vuoto * pesi[i] / tot

    uscita = a.uscita or os.path.splitext(os.path.expanduser(a.immagine))[0] + "_card.jpg"
    im.save(uscita, quality=94, subsampling=0, optimize=True, progressive=True)
    print(f"scritto: {uscita}")


if __name__ == "__main__":
    main()
