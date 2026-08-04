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
# ⛔ 4 agosto 2026, appunto di Fernando sulla card di Luigi: «tolto il nome le
#    altre sono quasi illeggibili». Cinzel e' un lapidario sottile e molto
#    spaziato: bello grande, illeggibile piccolo. Le righe che servono a votare
#    — carica, istruzione, committente — passano a un neretto (Montserrat 700,
#    lo stesso del sito) e crescono di un quarto. Cinzel resta solo dove e'
#    identita': PARTECIPAZIONE ATTIVA.
NERETTO = "montserrat-700.ttf"
NERETTO_MEDIO = "montserrat-600.ttf"

BRUNO = (58, 36, 20)
ORO = (166, 124, 47)
# L'oro chiaro sulla pergamena non ha contrasto: per il testo si usa piu' scuro,
# e l'oro chiaro resta ai fili, dove non deve leggersi ma decorare.
ORO_SCURO = (139, 96, 26)

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


# ⚠️ Nell'ambiente `iopaint` cv2 c'e' ma e' una build ridotta, senza
#    CascadeClassifier. Quello completo sta in `comfyui`: verificato il 4
#    agosto 2026, e non si scopre finche' non lo si chiama.
PY_CV2 = "/opt/homebrew/Caskroom/miniforge/base/envs/comfyui/bin/python"


def costruisci_base(ritratto, larghezza=1024, frazione=0.45, zoom=1.0, alza=0.0):
    """Dalla FOTOGRAFIA sola alla tela impaginata: pannello a sinistra, foto a
    destra, testa alla misura giusta.

    ⛔ 4 agosto 2026 — LA CAUSA A MONTE. Per due volte il generatore ha
    tagliato la faccia col pannello e ha fatto la testa grande il doppio che
    su Rosa. Non e' il prompt: a un modello di immagini si stava chiedendo
    un'IMPAGINAZIONE, e lui non impagina, dipinge. Gli si chiede solo il
    ritratto; il pannello, i margini e la scala li mettiamo noi, uguali per
    tutti e dieci i candidati.

    Le due misure, prese da Rosa che era venuta giusta:
      - la testa (cima dei capelli -> mento) e' alta quanto il pannello e' largo;
      - il mento sta appena sopra la meta' dell'immagine.
    """
    import cv2  # sta solo nell'ambiente iopaint: vedi riesegui_con_cv2()
    import numpy as np

    im = Image.open(os.path.expanduser(ritratto)).convert("RGB")
    W = larghezza
    H = int(W * 3 / 2)
    bordo = int(W * frazione)

    grigio = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
    # ⚠️ 4 agosto 2026: nessuna delle build di cv2 sul Mac porta i file
    #    haarcascade (cv2.data esiste ma la cartella e' vuota). Se non ci sono,
    #    non si scarica niente: si passa da --immagine sulla card gia'
    #    composta, che e' la strada che funziona.
    xml = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    if not os.path.exists(xml):
        sys.exit("⛔ OpenCV senza i file di riconoscimento volti: questa strada "
                 "e' chiusa. Usare --immagine sulla card gia' impaginata "
                 "(Meta AI la compone correttamente).")
    facce = cv2.CascadeClassifier(xml).detectMultiScale(grigio, 1.1, 5,
                                                        minSize=(60, 60))
    if len(facce) == 0:
        sys.exit("⛔ nessun volto trovato nella fotografia: si posiziona a mano "
                 "con --zoom e --alza, oppure si rigenera il ritratto.")
    fx, fy, fw, fh = max(facce, key=lambda f: f[2] * f[3])
    # Il riquadro di Haar prende dalle sopracciglia al mento: la testa intera
    # e' circa una volta e mezza tanto, e il mento sta al suo bordo basso.
    testa = fh * 1.5
    mento = fy + fh * 1.05

    k = (bordo / testa) * zoom
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))),
                   Image.LANCZOS)
    cx = (fx + fw / 2) * k
    cy = mento * k

    tela = Image.new("RGB", (W, H), (247, 239, 220))
    # il volto: al 55% della zona foto in larghezza, il mento appena sopra meta'
    x = int(bordo + (W - bordo) * 0.55 - cx)
    y = int(H * (0.48 - alza) - cy)
    tela.paste(im, (x, y))
    # il pannello si stende DOPO: cosi' non c'e' verso che la figura lo invada
    tela.paste(Image.new("RGB", (bordo, H), (247, 239, 220)), (0, 0))
    return tela, bordo


def riesegui_con_cv2():
    """cv2 non c'e' nell'interprete di sistema: si riparte con quello che ce
    l'ha, invece di chiedere a Fernando di ricordarsi un percorso."""
    if os.path.exists(PY_CV2):
        os.execv(PY_CV2, [PY_CV2] + [os.path.abspath(__file__)] + sys.argv[1:])
    sys.exit("⛔ serve OpenCV: manca anche l'ambiente iopaint.")


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
        ("testo", [carica, "DELLA MUNICIPALITÀ 10"], NERETTO, 0.052, 0.01, BRUNO),
        ("testo", [f"{com['elezione']} 2027"], NERETTO, 0.045, 0.01, ORO_SCURO),
        # Su una riga sola i quattro quartieri costringono a un corpo minuscolo:
        # spezzati in due, la stessa larghezza permette il doppio del corpo.
        ("testo", [com["territorio_card"].split(" - Agnano")[0].strip(),
          "Agnano" + com["territorio_card"].split(" - Agnano")[1]],
         NERETTO_MEDIO, 0.040, 0.0, BRUNO),
        ("testo", ["BARRA IL SIMBOLO"], NERETTO, 0.062, 0.02, BRUNO),
        ("testo", [voto], NERETTO_MEDIO, 0.046, 0.0, BRUNO),
        ("testo", [com["sito"]], NERETTO_MEDIO, 0.034, 0.02, BRUNO),
        ("testo", [f"Committente responsabile: {com['committente']}"],
         NERETTO_MEDIO, 0.028, 0.0, BRUNO),
    ]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--immagine", help="una card gia' generata CON il pannello vuoto")
    p.add_argument("--ritratto", help="la sola FOTOGRAFIA del candidato: pannello, "
                                      "scala e posizione li calcola questo script "
                                      "(consigliato)")
    p.add_argument("--zoom", type=float, default=1.0,
                   help="ritocco della grandezza della testa (1.0 = misura di Rosa)")
    p.add_argument("--alza", type=float, default=0.0,
                   help="alza (+) o abbassa (-) la figura, in frazione di altezza")
    p.add_argument("--candidato", required=True, help="chiave nel JSON (es. rosa)")
    p.add_argument("--dati", default=DATI)
    p.add_argument("--logo", help="il simbolo vero (default: logo_pa.png della sua cartella)")
    p.add_argument("--bordo", type=float,
                   help="frazione di larghezza del pannello, se la misura sbaglia (es. 0.5)")
    p.add_argument("--margine", type=float, default=0.09,
                   help="margine interno del pannello, in frazione della sua larghezza")
    p.add_argument("--uscita",
                   help="file di uscita (default: ~/Desktop/<candidato>_card.jpg — "
                        "i risultati finiti si lasciano sempre in Scrivania)")
    a = p.parse_args()
    if not a.immagine and not a.ritratto:
        sys.exit("⛔ serve --ritratto (la fotografia) oppure --immagine (la card "
                 "gia' impaginata col pannello vuoto)")

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
    if a.ritratto:
        try:
            import cv2
            cv2.CascadeClassifier  # la build ridotta non ce l'ha
        except (ModuleNotFoundError, AttributeError):
            riesegui_con_cv2()
        im, bordo = costruisci_base(a.ritratto, frazione=a.bordo or 0.45,
                                    zoom=a.zoom, alza=a.alza)
        W, H = im.size
        print(f"tela costruita: {W}x{H}, pannello {bordo} px "
              f"({bordo / W:.3f}), testa alta quanto il pannello e' largo",
              file=sys.stderr)
    else:
        im = Image.open(os.path.expanduser(a.immagine)).convert("RGB")
        W, H = im.size
        bordo, soglia = misura_pannello(im)
        if a.bordo:
            bordo = int(W * a.bordo)
        print(f"pannello: {bordo} px su {W} ({bordo / W:.3f} della larghezza), "
              f"soglia {soglia:.1f}", file=sys.stderr)
        if bordo < W * 0.25:
            sys.exit("⛔ pannello troppo stretto: o l'immagine non e' quella "
                     "vuota, o la misura ha sbagliato. Forzarla con --bordo 0.45")

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

    # ⭐ Regola di Fernando: il finito si trova sempre in Scrivania, non
    #    accanto al file di partenza e non in una cartella di lavoro.
    uscita = os.path.expanduser(a.uscita or f"~/Desktop/{k}_card.jpg")
    im.save(uscita, quality=94, subsampling=0, optimize=True, progressive=True)
    print(f"scritto: {uscita}")


if __name__ == "__main__":
    main()
