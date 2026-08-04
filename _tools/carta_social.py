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

from PIL import Image, ImageDraw, ImageFilter

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

# Antonio e' l'unico Presidente. Dicitura voluta da Fernando, 4 agosto 2026:
# "CANDIDATO PRESIDENTE", non "candidato alla Presidenza".
CARICA = {"presidente": "CANDIDAT{a} PRESIDENTE",
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
PY_REMBG = "/opt/homebrew/Caskroom/miniforge/base/envs/iopaint/bin/python"
# ⭐ 4 agosto 2026: la pergamena non e' piu' un colore inventato da noi. E' la
#    tinta del fondo vuoto che Fernando ha scelto come base — misurata sul suo
#    file, perfettamente piatta (scarto zero su tutti e tre i canali).
#    Cosi' la figura ritagliata si posa su ESATTAMENTE lo stesso colore su cui
#    e' stata generata: nessuno stacco al bordo del ritaglio.
FONDO = (249, 233, 205)


def altezza_testa(sagoma):
    """Quanto e' alta la testa, in pixel, misurata sulla SAGOMA ritagliata.

    Senza riconoscimento del volto — nessuna build di cv2 sul Mac ha i file
    haarcascade — ma non serve: su una figura scontornata la testa e' la
    parte stretta in cima, e le spalle sono la riga dove la sagoma si allarga
    di colpo. Si scende dall'alto finche' la larghezza non supera di una volta
    e mezza quella della testa: quella riga sono le spalle, e il mento sta
    poco sopra.
    """
    m = sagoma.split()[-1].point(lambda v: 255 if v > 128 else 0)
    w, h = m.size
    righe = []
    for y in range(0, h, max(1, h // 400)):
        fila = m.crop((0, y, w, y + 1)).getbbox()
        righe.append((y, 0 if not fila else fila[2] - fila[0]))
    cima = next((y for y, l in righe if l > w * 0.02), 0)
    larghezze = [l for y, l in righe if cima <= y <= cima + (h - cima) * 0.22 and l]
    if not larghezze:
        return h * 0.25
    testa_larga = sorted(larghezze)[len(larghezze) // 2]
    for y, l in righe:
        if y > cima + h * 0.05 and l > testa_larga * 1.6:
            return (y - cima) * 1.02          # dalla cima dei capelli al mento
    return h * 0.25


def costruisci_da_figura(immagine, larghezza=1024, frazione=0.45, zoom=1.0,
                         alza=0.0, sfondo=None):
    """Ritaglia la persona dal fondo vuoto e la monta alla scala giusta.

    La misura e' la stessa delle card gia' approvate: la testa e' alta quanto
    il pannello e' largo, e il mento sta appena sopra la meta'.
    """
    from rembg import remove, new_session

    W = larghezza
    H = int(W * 3 / 2)
    bordo = int(W * frazione)

    fig = remove(Image.open(os.path.expanduser(immagine)).convert("RGBA"),
                 session=new_session("birefnet-general"))
    fig = fig.crop(fig.getbbox())
    testa = altezza_testa(fig)
    k = (bordo / testa) * zoom
    # Se alla misura di serie la figura non copre la sua meta', si allarga fino
    # a coprirla — al massimo di un terzo, o la serie non e' piu' una serie.
    k = min(k * 1.35, max(k, (W - bordo) * 1.02 / fig.width))
    fig = fig.resize((max(1, int(fig.width * k)), max(1, int(fig.height * k))),
                     Image.LANCZOS)

    tela = Image.new("RGB", (W, H), FONDO)
    if sfondo:
        s = Image.open(os.path.expanduser(sfondo)).convert("RGB")
        larg = W - bordo
        kk = max(larg / s.width, H / s.height)
        s = s.resize((int(s.width * kk), int(s.height * kk)), Image.LANCZOS)
        tela.paste(s.crop((0, 0, larg, H)), (bordo, 0))

    # il mento appena sopra meta': la testa e' alta 'bordo', quindi la cima
    # dei capelli sta a mezzo - bordo
    y = int(H * (0.48 - alza) - bordo)
    # ⛔ 4 agosto 2026: la figura DEVE arrivare al bordo di sotto. Se resta
    #    sospesa lascia una striscia di fondo vuoto sotto i piedi, e su un
    #    manifesto quella striscia si vede come un errore di montaggio.
    #    Prima si prova a scendere; se non basta perche' la foto di partenza
    #    ha poco corpo, si ingrandisce quel tanto che serve e lo si dice.
    if y + fig.height < H:
        y = H - fig.height
    if y + fig.height < H or y > H * 0.30:
        allunga = (H - y) / fig.height
        if allunga > 1:
            fig = fig.resize((int(fig.width * allunga), int(fig.height * allunga)),
                             Image.LANCZOS)
            print(f"⚠️  poco corpo nella foto: figura ingrandita del "
                  f"{(allunga - 1) * 100:.0f}% per arrivare al bordo di sotto",
                  file=sys.stderr)
    # ⛔ 4 agosto 2026: la TESTA sta tutta dentro, anche a costo di perdere un
    #    pezzo di spalla. Un orecchio o una ciocca tagliati dal bordo si notano
    #    subito e sembrano un errore; una spalla che esce dal bordo e' normale
    #    in qualunque manifesto.
    alfa = fig.split()[-1].point(lambda v: 255 if v > 128 else 0)
    fascia = alfa.crop((0, 0, fig.width, max(1, int(testa * k)))).getbbox()
    # accostata al bordo destro, con un filo di spalla che esce: la striscia
    # di fondo a destra fa sembrare la figura mozzata.
    x = W - fig.width + int(W * 0.015)
    if fascia:
        margine_t = int(W * 0.02)
        x = min(x, W - margine_t - fascia[2])          # niente testa tagliata a destra
        x = max(x, bordo + margine_t - fascia[0])      # ne' sopra il pannello
    strato = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    strato.paste(fig, (x, y))
    strato = strato.crop((bordo, 0, W, H))     # mai dentro il pannello
    tela.paste(strato, (bordo, 0), strato)
    return tela, bordo


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
    # Se alla misura di serie la figura non copre la sua meta', si allarga fino
    # a coprirla — al massimo di un terzo, o la serie non e' piu' una serie.
    k = min(k * 1.35, max(k, (W - bordo) * 1.02 / fig.width))
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))),
                   Image.LANCZOS)
    cx = (fx + fw / 2) * k
    cy = mento * k

    tela = Image.new("RGB", (W, H), FONDO)
    # il volto: al 55% della zona foto in larghezza, il mento appena sopra meta'
    x = int(bordo + (W - bordo) * 0.55 - cx)
    y = int(H * (0.48 - alza) - cy)
    tela.paste(im, (x, y))
    # il pannello si stende DOPO: cosi' non c'e' verso che la figura lo invada
    tela.paste(Image.new("RGB", (bordo, H), FONDO), (0, 0))
    return tela, bordo


def riesegui_con_cv2():
    """cv2 non c'e' nell'interprete di sistema: si riparte con quello che ce
    l'ha, invece di chiedere a Fernando di ricordarsi un percorso."""
    if os.path.exists(PY_CV2):
        os.execv(PY_CV2, [PY_CV2] + [os.path.abspath(__file__)] + sys.argv[1:])
    sys.exit("⛔ serve OpenCV: manca anche l'ambiente iopaint.")


ROSSO_X = (198, 42, 30)
ROSSO_PA = (198, 56, 34)


def croce_sul_simbolo(tela, x, y, lato, grande=False):
    """La X che l'elettore traccia sulla scheda, disegnata sul simbolo.

    ⭐ E' l'elemento piu' classico del manifesto elettorale italiano, e il
    manuale lo dice chiaro: a trenta metri un SEGNO si capisce, una frase no.

    ⛔ La X non deve mangiare le lettere: "PARTECIPAZIONE" corre in alto dentro
    il disco e "ATTIVA" in basso. I due tratti restano nella parte centrale —
    il 62% del diametro — e passano sopra il disegno, non sopra le scritte.
    """
    strato = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(strato)
    # ⛔ Primo tentativo con braccio 0.31: la X arrivava sulla scritta e sul
    #    manifesto si leggeva "PARTECIPAZIC NE". Le lettere corrono lungo il
    #    bordo del disco, quindi i tratti restano ben dentro: 0.19 del lato,
    #    centrati un filo sotto la meta', dove c'e' il disegno delle mani.
    cx, cy = x + lato / 2, y + lato * (0.50 if grande else 0.53)
    braccio = lato * (0.46 if grande else 0.19)
    spessore = max(3, int(lato * (0.035 if grande else 0.055)))
    # due tratti tirati a mano: non partono dallo stesso punto e non sono
    # perfettamente simmetrici, se no sembra un segno stampato
    tinta = ((20, 20, 20) if grande else ROSSO_X) + (235 if grande else 205,)
    d.line([(cx - braccio, cy - braccio * 0.96), (cx + braccio * 1.04, cy + braccio)],
           fill=tinta, width=spessore)
    d.line([(cx + braccio, cy - braccio), (cx - braccio * 1.02, cy + braccio * 0.98)],
           fill=tinta, width=spessore)
    strato = strato.filter(ImageFilter.GaussianBlur(max(0.6, lato * 0.004)))
    tela.paste(strato, (0, 0), strato)


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
        ("logo", [], None, 0.50, 0, None),
        ("testo", ["PARTECIPAZIONE", "ATTIVA"], LAPIDARIO, 0.082, 0.06, BRUNO),
        ("testo", ["Libera associazione di cittadini"], ITALICO, 0.038, 0.0, BRUNO),
        ("filo", [], None, 0.34, 0, ORO),
        ("testo", [c["nome"].title(), c["cognome"].title()], SERIF_TESTO, 0.20, 0.0, BRUNO),
        ("filo", [], None, 0.34, 0, ORO),
        ("testo", [carica, "DELLA MUNICIPALITÀ 10"], NERETTO, 0.052, 0.01, BRUNO),
        ("testo", [f"{com['elezione']} 2027"], NERETTO, 0.045, 0.01, ORO_SCURO),
        # I tre valori erano usciti quando il testo lo scriveva il generatore
        # e la colonna piena lo faceva tagliare. Ora il testo e' nostro: ci
        # stanno, e sono la parte politica della card.
        ("testo", ["DEMOCRAZIA DIRETTA", "TRASPARENZA", "BENI COMUNI"],
         NERETTO, 0.048, 0.01, BRUNO),
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


BIANCO = (255, 255, 255)
# I colori sono quelli del simbolo, non del partito che c'era prima.
AMBRA_PA = (237, 153, 53)
VERDE_PA = (62, 145, 67)
VERDE_SCURO = (35, 96, 45)


def fascia(tela, y0, y1, da, a):
    """Fascia a gradiente orizzontale, coi colori del simbolo."""
    h = y1 - y0
    striscia = Image.new("RGB", (tela.width, 1))
    px = striscia.load()
    for x in range(tela.width):
        t = x / max(1, tela.width - 1)
        px[x, 0] = tuple(int(da[i] + (a[i] - da[i]) * t) for i in range(3))
    tela.paste(striscia.resize((tela.width, h), Image.BILINEAR), (0, y0))


def componi_campagna(figura, c, com, logo, presidente=None):
    """Il santino elettorale quadrato, coi colori nostri.

    ⭐ Ricavato dal santino vero di Antonio (regionali Campania 2025), ma
    ripreso nella tavolozza del simbolo: rosso e ambra in alto, verde in
    basso. Il blu del santino originale e' del partito che c'era prima, non
    nostro.

    L'ordine e' quello che l'elettore riconosce come istruzione di voto, e
    nessuno dei pezzi e' decorativo:
      1. fascia in alto: elezione e data;
      2. VOTA;
      3. il SIMBOLO con la X sopra — il gesto, non la frase;
      4. E SCRIVI + cognome (solo consiglieri: sul Presidente la preferenza
         scritta non porta voti alla lista);
      5. lo slogan del movimento e il territorio, che riempiono la colonna;
      6. fascia in basso: il candidato Presidente della lista.
    """
    L = 1080
    tela = Image.new("RGB", (L, L), BIANCO)
    dr = ImageDraw.Draw(tela)
    alta = int(L * 0.145)
    bassa = int(L * 0.115)

    fascia(tela, 0, alta, ROSSO_PA, AMBRA_PA)
    f1, c1 = adatta(com["elezione"], NERETTO, L * 0.92, alta * 0.44, 0.008)
    scrivi(dr, (L / 2, alta * 0.50), com["elezione"], f1, BIANCO, c1 * 0.008, "ms")
    data = com.get("data", "PRIMAVERA 2027")
    f2, c2 = adatta(data, NERETTO, L * 0.8, alta * 0.34, 0.01)
    scrivi(dr, (L / 2, alta * 0.90), data, f2, BIANCO, c2 * 0.01, "ms")

    # la figura riempie la sua meta': il vuoto IN MEZZO si nota piu' di quello
    # ai bordi, quindi si allarga fino a coprirla e il corpo esce dal basso.
    fig = figura.crop(figura.getbbox())
    utile = L - alta - bassa
    # ⛔ 4 agosto 2026: con il tetto sulla testa la figura di Paolo restava
    #    piu' corta dell'altezza utile, e spingerla in basso apriva una
    #    striscia bianca SOPRA la testa. Fra le due, riempire vince: la figura
    #    copre sempre tutta l'altezza fra le due fasce, e in larghezza si
    #    allarga fin dove serve, ma non oltre una volta e mezza — se no un
    #    ritratto stretto diventa un primo piano.
    k_h = utile / fig.height
    k = max(k_h, min((L * 0.60) / fig.width, k_h * 1.5))
    fig = fig.resize((max(1, int(fig.width * k)), max(1, int(fig.height * k))),
                     Image.LANCZOS)
    alfa = fig.split()[-1].point(lambda v: 255 if v > 128 else 0)
    banda = alfa.crop((0, 0, fig.width, max(1, int(fig.height * 0.30)))).getbbox()
    x = L - fig.width + int(L * 0.015)
    if banda:
        x = min(x, L - int(L * 0.02) - banda[2])
    # se il corpo finisce prima della fascia in basso resta una lingua di
    # bianco sotto i piedi: si scende finche' non la tocca.
    y_fig = alta
    strato = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    strato.paste(fig, (x, y_fig))
    strato = strato.crop((int(L * 0.40), 0, L, L))
    tela.paste(strato, (int(L * 0.40), 0), strato)

    # la colonna: si misura prima e si stringe tutta insieme se non ci sta,
    # invece di perdere l'ultima riga.
    x0 = int(L * 0.05)
    largo = int(L * 0.34)
    y0 = alta + int(L * 0.035)
    disponibile = (L - bassa - int(L * 0.02)) - y0

    if c["ruolo"] == "consigliere":
        righe = [("E SCRIVI", NERETTO, 0.058), (c["nome"], NERETTO, 0.052),
                 (c["cognome"], NERETTO, 0.080)]
    else:
        righe = [(c["nome"], NERETTO, 0.052), (c["cognome"], NERETTO, 0.080),
                 ("CANDIDATO PRESIDENTE", NERETTO, 0.034)]
    coda = [(com.get("slogan", "IL QUARTIERE DECIDE"), NERETTO, 0.044, VERDE_PA),
            ("MUNICIPALITÀ 10", NERETTO, 0.036, BRUNO),
            (com["territorio_card"].split(" - Agnano")[0], NERETTO_MEDIO, 0.026, BRUNO),
            ("Agnano" + com["territorio_card"].split(" - Agnano")[1],
             NERETTO_MEDIO, 0.026, BRUNO)]

    def _alto(f):
        h = adatta("VOTA", NERETTO, largo, L * 0.082 * f, 0.02)[1] * 1.5
        h += int(largo * 0.98 * f) * 1.04
        for t, fo, d in righe:
            h += adatta(t, fo, largo, L * d * f, 0.01)[1] * 1.28
        h += L * 0.02 * f
        for t, fo, d, _ in coda:
            h += adatta(t, fo, largo, L * d * f, 0.01)[1] * 1.30
        return h

    fatt = 1.0
    while fatt > 0.45 and _alto(fatt) > disponibile:
        fatt -= 0.03

    y = y0
    fv, cv = adatta("VOTA", NERETTO, largo, L * 0.082 * fatt, 0.02)
    scrivi(dr, (x0, y + cv), "VOTA", fv, BRUNO, cv * 0.02, "ls")
    y += int(cv * 1.5)

    lato = int(largo * 0.98 * fatt)
    sim = Image.open(logo).convert("RGBA").resize((lato, lato), Image.LANCZOS)
    tela.paste(sim, (x0, y), sim)
    croce_sul_simbolo(tela, x0, y, lato, grande=True)
    y += int(lato * 1.04)

    for t, fo, d in righe:
        ft, ct = adatta(t, fo, largo, L * d * fatt, 0.01)
        scrivi(dr, (x0, y + ct), t, ft, BRUNO, ct * 0.01, "ls")
        y += int(ct * 1.28)
    y += int(L * 0.02 * fatt)
    for t, fo, d, col in coda:
        ft, ct = adatta(t, fo, largo, L * d * fatt, 0.01)
        scrivi(dr, (x0, y + ct), t, ft, col, ct * 0.01, "ls")
        y += int(ct * 1.30)

    fascia(tela, L - bassa, L, VERDE_PA, VERDE_SCURO)
    testo = (f"CON {presidente} PRESIDENTE"
             if presidente and c["ruolo"] == "consigliere"
             else f"{com['sito']}")
    ff, cf = adatta(testo, NERETTO, L * 0.90, bassa * 0.42, 0.01)
    scrivi(dr, (L / 2, L - bassa * 0.46), testo, ff, BIANCO, cf * 0.01, "ms")
    comm = f"Committente responsabile: {com['committente']}"
    fq, cq = adatta(comm, NERETTO_MEDIO, L * 0.9, bassa * 0.22)
    scrivi(dr, (L / 2, L - bassa * 0.14), comm, fq, BIANCO, 0, "ms")
    return tela


def blocchi_classico(c, com):
    """L'impaginato dei manifesti elettorali veri, quelli da affissione.

    Ricavato dai due portati da Fernando il 4 agosto (Salini, europee 2024;
    Bulbi, politiche 2022) e gia' scritto in PROMPT_MANIFESTO.txt:
      - la DATA e' grande e sta in ALTO, non in fondo;
      - "VOTA" e il cognome sono le righe che si leggono da lontano;
      - l'istruzione di voto e' un SEGNO sul simbolo, non una frase;
      - i valori e il sottotitolo qui non ci sono: a trenta metri non si
        leggono e rubano spazio alle tre righe che contano.
    """
    f = c["genere"] == "f"
    carica = CARICA[c["ruolo"]].format(a="A" if f else "O")
    voto = VOTO[c["ruolo"]].format(cognome=c["cognome"])
    return [
        ("testo", [com["elezione"]], NERETTO, 0.040, 0.02, BRUNO),
        ("testo", ["PRIMAVERA 2027"], NERETTO, 0.075, 0.01, ROSSO_PA),
        ("testo", ["VOTA"], LAPIDARIO, 0.105, 0.06, BRUNO),
        ("testo", [c["nome"].title(), c["cognome"].title()], SERIF_TESTO, 0.22, 0.0, BRUNO),
        ("testo", [carica, "DELLA MUNICIPALITÀ 10"], NERETTO, 0.048, 0.01, BRUNO),
        ("logo", [], None, 0.46, 0, None),
        ("testo", ["BARRA IL SIMBOLO"], NERETTO, 0.068, 0.02, BRUNO),
        ("testo", [voto], NERETTO_MEDIO, 0.046, 0.0, BRUNO),
        ("testo", [f"Committente responsabile: {com['committente']}"],
         NERETTO_MEDIO, 0.028, 0.0, BRUNO),
    ]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--immagine", help="una card gia' generata CON il pannello vuoto")
    p.add_argument("--figura", help="la persona su FONDO VUOTO: si ritaglia, si "
                                    "porta alla scala di tutti e si monta "
                                    "(strada migliore)")
    p.add_argument("--campagna", action="store_true",
                   help="il santino elettorale quadrato: fascia rossa in alto, "
                        "VOTA, simbolo barrato, E SCRIVI + cognome, fascia in "
                        "basso col Presidente della lista")
    p.add_argument("--classico", action="store_true",
                   help="l'impaginato dei manifesti da affissione: data grande in "
                        "alto, VOTA, il segno sul simbolo. Senza sottotitolo e "
                        "senza i tre valori, che a trenta metri non si leggono")
    p.add_argument("--senza-croce", action="store_true", dest="senza_croce",
                   help="non traccia la X rossa sul simbolo")
    p.add_argument("--sfondo", help="immagine di fondo per la meta' destra "
                                    "(default: pergamena piatta)")
    p.add_argument("--ritratto", help="la sola FOTOGRAFIA del candidato: pannello, "
                                      "scala e posizione li calcola questo script "
                                      "(consigliato)")
    p.add_argument("--zoom", type=float, default=0.65,
                   help="grandezza della testa. 0.65 e' la misura di serie scelta "
                        "il 4 agosto 2026 sul confronto a tre: si vede il torace "
                        "e la figura sta comoda nella sua meta'")
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
    if not (a.immagine or a.ritratto or a.figura):
        sys.exit("⛔ serve --figura (persona su fondo vuoto), --ritratto (la "
                 "fotografia) oppure --immagine (la card gia' impaginata)")

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
    if a.figura:
        try:
            import rembg  # noqa: F401
        except ModuleNotFoundError:
            if os.path.exists(PY_REMBG):
                os.execv(PY_REMBG, [PY_REMBG, os.path.abspath(__file__)] + sys.argv[1:])
            sys.exit("⛔ serve rembg (ambiente iopaint).")
        im, bordo = costruisci_da_figura(a.figura, frazione=a.bordo or 0.45,
                                         zoom=a.zoom, alza=a.alza, sfondo=a.sfondo)
        W, H = im.size
        print(f"tela: {W}x{H}, pannello {bordo} px, figura ritagliata e portata "
              f"alla scala comune", file=sys.stderr)
    elif a.ritratto:
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

    # Il simbolo e' lo stesso per tutti: se nella cartella del candidato non
    # c'e', si prende quello di un altro invece di fermare il lavoro.
    cartella = os.path.join(os.path.expanduser(LAVORI),
                            c["cartella_foto"].split("/")[1])
    candidati = [a.logo, os.path.join(cartella, "logo_pa.png"),
                 os.path.join(cartella, "prescelte", "B.png"),
                 os.path.join(cartella, "prescelte", "b.png"),
                 os.path.join(os.path.expanduser(LAVORI), "Rosa", "logo_pa.png")]
    logo = next((os.path.expanduser(x) for x in candidati
                 if x and os.path.exists(os.path.expanduser(x))), None)
    if not logo:
        sys.exit(f"⛔ simbolo non trovato in {cartella}")

    if a.campagna:
        from rembg import remove, new_session
        fig = remove(Image.open(os.path.expanduser(a.figura or a.immagine)).convert("RGBA"),
                     session=new_session("birefnet-general"))
        pres = next((f"{v['nome']} {v['cognome']}" for v in d["candidati"].values()
                     if v["ruolo"] == "presidente"), None)
        tela = componi_campagna(fig, c, com, logo, pres)
        uscita = os.path.expanduser(a.uscita or f"~/Desktop/{k}_santino.jpg")
        tela.save(uscita, quality=94, subsampling=0, optimize=True, progressive=True)
        print(f"scritto: {uscita}")
        return

    margine = int(bordo * a.margine)
    largh = bordo - 2 * margine
    x0 = margine

    # Prima passata: corpo e altezza di ogni gruppo. Le righe di un gruppo
    # condividono il corpo della piu' lunga.
    voci = []
    schema = blocchi_classico(c, com) if a.classico else blocchi(c, com)
    for tipo, righe, f_font, rel, sp_rel, colore in schema:
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
        y = int(y)          # lo spazio avanzato si distribuisce in frazioni
        if tipo == "logo":
            sim = Image.open(logo).convert("RGBA").resize((h, h), Image.LANCZOS)
            im.paste(sim, (x0, y), sim)
            if not a.senza_croce:
                croce_sul_simbolo(im, x0, y, h)
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
