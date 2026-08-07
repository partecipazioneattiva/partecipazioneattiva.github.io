#!/usr/bin/env python3
"""Scrive il prompt del manifesto elettorale di un candidato, gia' pronto da
incollare su Gemini / Nano Banana (aistudio.google.com).

    python3 _tools/crea_prompt_manifesto.py --candidato rosa
    python3 _tools/crea_prompt_manifesto.py --elenco

Le impostazioni delle persone NON stanno qui dentro: questo repository e'
pubblico e quelle sono descrizioni fisiche di persone reali. Stanno in
    ~/Desktop/GEMINI LAVORI/candidati_manifesto.json
accanto alle foto, e si sovrascrive il percorso con --dati.

⛔ LA REGOLA CHE QUESTO SCRIPT ESISTE PER PROTEGGERE
Nelle Municipalita' di Napoli l'istruzione di voto dipende dal RUOLO, e
sbagliarla costa voti veri:
  - Presidente  -> si vota barrando il SIMBOLO. Un segno sul solo nome del
                   candidato Presidente vale come voto a lui e NON alla lista
                   (art. 3 del Regolamento delle Municipalita'), e i seggi li
                   prende la lista: senza seggio della lista, il Presidente non
                   eletto non entra.
  - Consigliere -> serve la PREFERENZA SCRITTA: barra il simbolo e scrivi il
                   cognome. Senza il cognome scritto, zero preferenze.
Qui l'istruzione si deriva dal campo 'ruolo': non si scrive piu' a mano.
"""
import argparse
import json
import os
import sys

DATI = "~/Desktop/GEMINI LAVORI/candidati_manifesto.json"

# L'istruzione di voto, derivata dal ruolo. Non si tocca senza rileggere
# l'art. 3 del Regolamento delle Municipalita' di Napoli.
VOTO = {
    "presidente": ('"BARRA IL SIMBOLO" e "sulla scheda della Municipalita\'"',
                   "due righe piccole"),
    "consigliere": ('"BARRA IL SIMBOLO" e "e scrivi {cognome} sulla scheda"',
                    "due righe piccole, la seconda un poco piu' marcata della prima"),
}


# ── STILE CARD SOCIAL ────────────────────────────────────────────────────────
# Impaginato "spezzato": foto a destra su Napoli al tramonto, pannello di
# pergamena a sinistra. E' l'unico prompt che regge con lo stesso testo su
# Gemini e su Lumina (Fernando, 4 agosto 2026), ed e' scritto in inglese per
# questo. NON sostituisce lo stile affissione: qui il testo lo scrive il
# generatore, e in stampa 70x100 non si fa (cfr. manuale Gemini 11quinquies).
#
# ⛔ Le tre trappole gia' pagate, tutte dentro il testo qui sotto:
#    1. le virgolette CURVE del prompt vengono STAMPATE sul manifesto: il nome
#       si scrive nudo e le virgolette finiscono nel negativo;
#    2. gli accenti italiani cadono: MUNICIPALITA' si chiede lettera per
#       lettera ("the final A carrying its grave accent");
#    3. il bollino: su Gemini si genera da AI Studio, su Lumina resta e va
#       ritagliato prima di pubblicare.
# ⛔ 4 agosto 2026, due difetti visti sulle prime due prove di Luigi, e valgono
#    per tutti: (1) il pannello TAGLIAVA la figura — mezza faccia dietro la
#    pergamena, perche' il modello centra la persona su tutta la tela e poi ci
#    disegna sopra il pannello; (2) la persona guardava FUORI dal manifesto.
#    In un impaginato spezzato lo sguardo deve entrare nella pagina, verso il
#    testo: e' la regola che fa sembrare le due meta' una cosa sola.
#    Per questo qui non si dice piu' "shoulder bleeding off the right edge":
#    era proprio l'istruzione che lo spingeva verso il bordo e sotto il taglio.
POSA = ("FRAMING, and this is exact: {suo} head, measured from the top of "
        "the hair to the chin, is as tall as the parchment panel is wide, "
        "and {suo} chin sits just above the middle line of the image. This "
        "is a waist up photograph, not a close up: the face must never fill "
        "the frame. "
        "{Lui} is photographed on the RIGHT side of the frame, waist up, "
        "ENTIRELY inside the right portion: the whole head and both shoulders "
        "are visible, with a clear margin of background between the figure and "
        "the parchment panel. The panel never covers any part of the person and "
        "the person never crosses into the panel: nothing of the face, the hair "
        "or the shoulders is hidden, cut or overlapped. {Lui} is turned slightly "
        "INWARDS, towards the panel on the left, and looks straight into the "
        "camera with the head angled the same way, so that the gaze leads into "
        "the poster and never out of the right edge. There is clear space above "
        "the head.")

def posa_di(f):
    return POSA.format(Lui="She" if f else "He", suo="her" if f else "his")


# ── QUANTE FOTO CI SONO DAVVERO ──────────────────────────────────────────────
# ⛔ 7 agosto 2026. Qui dentro era scritto "quattro" a mano, in cinque punti.
# Su Rosa le fotografie buone sono TRE: una era di un'altra donna e una era il
# doppione della stessa posa con la filigrana TikTok sopra (motivi per esteso
# in GEMINI LAVORI/Rosa/scartate/PERCHE_SCARTATE.txt). Un prompt che ne annuncia
# quattro fa cercare al generatore un'immagine che non gli ho allegato, e lui
# la inventa: e' esattamente il modo in cui il ritratto smette di somigliare.
# Adesso il numero si conta sul disco, cartella per cartella.
NUMERI = {1: "una", 2: "due", 3: "tre", 4: "quattro", 5: "cinque",
          6: "sei", 7: "sette", 8: "otto"}
INSIEME = {1: "", 2: "tutte e due", 3: "tutte e tre", 4: "tutte e quattro",
           5: "tutte e cinque", 6: "tutte e sei"}


MAX_FOTO = 4   # oltre le quattro la somiglianza non migliora piu' (LEGGIMI di
               # GEMINI LAVORI), e Gemini non ne accetta di piu' in una volta.


def elenco_foto(c, radice):
    """Le foto della persona da allegare: (etichette, nomi dei file).

    Le ETICHETTE sono sempre A1, A2, ... in fila, perche' e' l'ordine in cui si
    caricano e i nomi dei file sul generatore non arrivano: quelle di Luigi si
    chiamano A1_migliorata.jpg, ma nel prompt restano A1.
    """
    cartella = os.path.join(radice, c["cartella_foto"])
    if not os.path.isdir(cartella):
        print(f"⚠️  cartella foto non trovata: {cartella} — assumo quattro foto",
              file=sys.stderr)
        return ["A1", "A2", "A3", "A4"], ["A1", "A2", "A3", "A4"]
    nomi = sorted(os.path.splitext(f)[0] for f in os.listdir(cartella)
                  if f[:1] == "A" and f[1:2].isdigit()
                  and os.path.splitext(f)[1].lower() in (".jpg", ".jpeg", ".png"))
    if not nomi:
        sys.exit(f"⛔ nessuna foto A1, A2, ... in {cartella}")
    if len(nomi) > MAX_FOTO:
        print(f"⚠️  in {cartella} ci sono {len(nomi)} foto: se ne caricano "
              f"{MAX_FOTO} ({', '.join(nomi[:MAX_FOTO])}), le altre restano fuori.",
              file=sys.stderr)
        nomi = nomi[:MAX_FOTO]
    return [f"A{i}" for i in range(1, len(nomi) + 1)], nomi


CARICA_CARD = {
    "presidente": "CANDIDAT{a} ALLA PRESIDENZA",
    "consigliere": "CANDIDAT{a} AL CONSIGLIO",
}
VOTO_CARD = {
    "presidente": "sulla scheda della Municipalità",
    "consigliere": "e scrivi {cognome} sulla scheda",
}


def prompt_figura(c, per_manifesto=False):
    """La persona SOLA su fondo vuoto: nemmeno il panorama.

    Con per_manifesto=True la figura si chiede CENTRATA e in 7:10, per la
    catena dell'affissione: scontorno, poi monta_manifesto.py che calcola scala
    e posizione, poi il testo, poi sostituisci_simbolo.py. Senza, resta la
    versione 2:3 con la figura a destra, per la card social.

    ⭐ Idea di Fernando, 4 agosto 2026, e chiude il cerchio cominciato con
    --stile ritratto. Meta fa i volti piu' veri, ma qualunque generatore
    sbaglia l'impaginazione. Su fondo uniforme non c'e' piu' niente da
    impaginare: si ritaglia la figura con rembg, la si porta alla scala
    giusta e si monta su un fondo nostro. La testa esce uguale su tutti e
    dieci perche' la misuriamo noi, non perche' l'abbiamo chiesta bene.

    ⛔ Il fondo si chiede PIATTO e senza contorni: un fondo sfumato o con
    un'ombra lascia un alone sul ritaglio, e l'alone si vede solo dopo, sul
    manifesto stampato (stessa lezione del disco vuoto, manuale 11quater).
    """
    if "card_en" not in c:
        sys.exit(f"⛔ manca il blocco 'card_en' per {c['nome'].title()}.")
    e = c["card_en"]
    f = c["genere"] == "f"
    Lui = "She" if f else "He"
    uomo = "woman" if f else "man"
    suo = "her" if f else "his"

    # ⛔ La figura si chiede CENTRATA quando serve al manifesto: il ritaglio la
    #    riposiziona comunque (monta_manifesto.py), e una figura spinta contro
    #    un bordo perde meta' dei pixel utili e rischia la spalla tagliata.
    if per_manifesto:
        tela = "Vertical studio photograph of one person on a plain empty background, 7:10."
        inquadratura = (
            f"{Lui} is photographed waist up, CENTRED in the frame, turned "
            f"slightly to {suo} right, looking straight into the camera. The "
            "whole head and both shoulders are well inside the picture, with "
            "clear space above the head and on both sides, and nothing of the "
            "figure touching or crossing the edges. This is a waist up "
            "photograph, not a close up: the head takes about one quarter of "
            "the height of the picture and the face never fills the frame.")
        fondo_meta = "Every part of the picture that is not the person is nothing but that flat colour."
        # Meta lavora su una foto per volta: la descrizione parla della "prima
        # fotografia", e quella caricata e' proprio quella. Senza questa riga
        # il modello cerca fotografie che non gli ho dato.
        riferimenti = ("Use every uploaded reference photograph together to "
                       f"rebuild the {uomo}'s face. If only one photograph is "
                       "uploaded, that one IS the first photograph the "
                       "description below refers to, and it is the only face "
                       "to work from.")
    else:
        tela = "Vertical studio photograph of one person on a plain empty background, 2:3."
        inquadratura = (
            f"{Lui} is photographed waist up, standing on the RIGHT side of the "
            f"frame, turned slightly to {suo} right, looking straight into the "
            "camera. The whole head and both shoulders are inside the picture, "
            f"with clear space above the head; {suo} arm may run out of the "
            "bottom right corner. This is a waist up photograph, not a close "
            "up: the head takes about one quarter of the height of the picture "
            "and the face never fills the frame.")
        fondo_meta = "The left half of the picture is nothing but that flat colour."
        riferimenti = ("Use every uploaded reference photograph together to "
                       f"rebuild the {uomo}'s face, not just the first one.")

    return f"""{tela}

{riferimenti} {e['aspetto']} {e['espressione']} {e['abbigliamento']} {e['divieti']}

{inquadratura}

THE BACKGROUND IS COMPLETELY EMPTY: one single flat warm cream tone, the same from edge to edge, with no scenery, no city, no sky, no sea, no furniture, no window, no wall texture, no pattern, no gradient, no vignette, no cast shadow of the person and no shadow of any kind. {fondo_meta} The outline of the person against it must be clean and sharp, with no glow, no halo and no blur around the hair and the shoulders.

Warm, even, frontal studio light on the face, natural skin texture, visible pores and lines, sharp focus on the eyes. Photorealistic, natural colours, print quality, 4K.

NEGATIVE PROMPT: background scenery, landscape, city, sea, sky, mountain, Vesuvius, room, window, wall, texture, pattern, gradient background, vignette, cast shadow, drop shadow, halo around the figure, blurred outline, text, letters, words, numbers, logo, emblem, symbol, frame, border, panel, close up, face filling the frame, oversized head, full body, profile view, looking away, multiple people, distorted face, slimmed face, smoothed skin, beautified, younger face, {e.get('negativo', '').rstrip(', ')}, extra fingers, cartoon, 3D render, cold blue tones, night, sparkle icon, AI badge, watermark"""


def prompt_ritratto(c):
    """SOLO la fotografia: niente pannello, niente testo, niente impaginazione.

    ⛔ 4 agosto 2026 — la lezione piu' cara di questa giornata. Per due volte
    il generatore ha tagliato la faccia col pannello e ha fatto la testa
    grande il doppio che sul candidato precedente. Non era il prompt: gli si
    stava chiedendo di IMPAGINARE, e un modello di immagini non impagina,
    dipinge. Qui si chiede quello che sa fare — un ritratto — e la tela la
    monta _tools/carta_social.py --ritratto, che mette il pannello, i margini
    e la scala uguali per tutti e dieci.
    """
    if "card_en" not in c:
        sys.exit(f"⛔ manca il blocco 'card_en' per {c['nome'].title()}.")
    e = c["card_en"]
    f = c["genere"] == "f"
    Lui = "She" if f else "He"
    uomo = "woman" if f else "man"
    suo = "her" if f else "his"

    return f"""Vertical photographic portrait, 2:3, warm golden hour, a single photograph and nothing else.

Use ALL the uploaded reference photographs together to rebuild the {uomo}'s face, not just the first one. {e['aspetto']} {e['espressione']} {e['abbigliamento']} {e['divieti']}

{Lui} is photographed waist up, centred in the frame, the whole head and both shoulders well inside the picture with clear space above the head and on both sides. {Lui} looks straight into the camera, the body turned slightly to {suo} right. This is a waist up portrait, not a close up: the head takes about one quarter of the height of the picture and the face never fills the frame.

Behind {'her' if f else 'him'}, Naples from above at sunset, softly out of focus: pale rooftops, the bay, Mount Vesuvius, clouds lit orange and gold. Warm light on the face from the left, natural skin texture, visible pores and lines, sharp focus on the eyes.

Photorealistic, natural colours, print quality, 4K.

NEGATIVE PROMPT: text, letters, words, numbers, captions, logo, emblem, symbol, badge, frame, border, panel, coloured band, split composition, collage, close up, face filling the frame, oversized head, head cropped, full body, profile view, looking away, multiple people, distorted face, slimmed face, smoothed skin, beautified, younger face, {e.get('negativo', '').rstrip(', ')}, extra fingers, cartoon, 3D render, cold blue tones, night, sparkle icon, AI badge, watermark"""


def prompt_card_vuota(c):
    """La card SENZA testo: solo il ritratto e il pannello vuoto.

    ⭐ 4 agosto 2026, idea di Fernando. Due vantaggi, e nessuno dei due e' un
    trucco: al generatore si chiede una FOTOGRAFIA, quindi non c'e' nessun
    contenuto elettorale da valutare (Meta rifiuta i manifesti per policy,
    cfr. manuale Gemini 11ter); e il testo scritto in locale esce nitido,
    identico su tutti i candidati e con gli accenti giusti, invece che
    reinventato a ogni generazione.

    ⛔ Il vuoto NON deve avere contorni, righe o segnaposto: se il nostro
    testo non li copre al pixel, sull'immagine finita resta il segno. Stessa
    lezione del disco del simbolo (manuale 11quater). L'unica misura che si
    chiede e' la frazione di larghezza del pannello, e sul generato si
    RIMISURA sempre: non esce mai identica due volte.
    """
    if "card_en" not in c:
        sys.exit(f"⛔ manca il blocco 'card_en' per {c['nome'].title()}.")
    e = c["card_en"]
    f = c["genere"] == "f"
    Lui = "She" if f else "He"
    uomo = "woman" if f else "man"
    POSA = posa_di(f)

    return f"""Vertical editorial photograph, 2:3, warm golden hour, split composition: photograph on the right, plain empty panel on the left.

Use ALL the uploaded reference photographs together to rebuild the {uomo}'s face, not just the first one. {e['aspetto']} {e['espressione']} {e['abbigliamento']} {e['divieti']} {POSA} Behind {'her' if f else 'him'}, Naples from above at sunset: pale rooftops, the bay, Mount Vesuvius, clouds lit orange and gold. Warm light on the face from the left, natural skin texture, visible pores and lines, sharp focus on the eyes.

The LEFT HALF is a plain warm parchment panel: one flat cream tone with a soft golden glow, smooth and COMPLETELY EMPTY. It covers the left 45 per cent of the width and runs from the top edge to the bottom edge, separated from the photograph by a single straight vertical division. Inside that panel there is absolutely nothing: no text, no letters, no numbers, no logo, no emblem, no symbol, no rules, no lines, no frame, no border, no ornament, no placeholder, no shadow and no texture. It is empty on purpose and it must stay empty.

Photorealistic, natural colours, print quality, 4K.

NEGATIVE PROMPT: text, letters, words, numbers, captions, titles, signature, logo, emblem, symbol, badge, ornament, decoration, gold rules, lines on the panel, frame, border, paper texture, grain, stains, shadow over the panel, gradient on the panel, {uomo} on the left, panel on the right, figure cut by the panel, face half hidden, person behind the panel, cropped face, subject turned outwards, subject looking away from the panel, subject pressed against the right edge, centred composition, full body, profile view, looking away, multiple people, distorted face, slimmed face, smoothed skin, beautified, younger face, {e.get('negativo', '').rstrip(', ')}, extra fingers, cartoon, 3D render, cold blue tones, night, sparkle icon, AI badge, watermark"""


def prompt_card(c, com, valori=False):
    if "card_en" not in c:
        sys.exit(f"⛔ manca il blocco 'card_en' per {c['nome'].title()}: la "
                 f"descrizione del volto in inglese si scrive guardando le sue "
                 f"foto vere, non si traduce a occhi chiusi.")
    e = c["card_en"]
    f = c["genere"] == "f"
    Lui = "She" if f else "He"
    uomo = "woman" if f else "man"
    carica = CARICA_CARD[c["ruolo"]].format(a="A" if f else "O")
    voto = VOTO_CARD[c["ruolo"]].format(cognome=c["cognome"])
    POSA = posa_di(f)

    # ⛔ 4 agosto 2026: la riga della CARICA era sparita dal generato. Non e'
    #    un difetto del motore: l'elenco era troppo lungo (dodici blocchi) e
    #    quando la colonna non ci sta, il generatore non rimpicciolisce, TAGLIA
    #    — e taglia in mezzo, dove stanno carica e istruzione di voto.
    #    Rimedio: elenco NUMERATO e corto, e il conteggio chiesto esplicitamente
    #    alla fine. Sono usciti "Libera associazione di cittadini" e i tre
    #    valori (--valori li rimette, ma allora qualcosa d'altro va tolto).
    blocchi = [
        "the uploaded circular emblem, reproduced unchanged, with the words PARTECIPAZIONE and ATTIVA inside it fully legible",
        "two lines of large letterspaced capitals: PARTECIPAZIONE and ATTIVA",
        "a short gold rule",
        f"the name, the largest lettering of the panel, on two lines, with no quotation marks and no punctuation of any kind around it: {c['nome'].title()} and {c['cognome'].title()}",
        "a second gold rule",
        f"two lines of capitals: {carica} and DELLA MUNICIPALITÀ 10, with the final A of MUNICIPALITÀ carrying its grave accent",
        f"one line of gold capitals: {com['elezione']} 2027",
        f"one italic line: {com['territorio_card']}",
        f"two small lines, the first in bold capitals, BARRA IL SIMBOLO, the second in italic, {voto}",
        f"the smallest lettering of the whole poster, on two lines: {com['sito']} and Committente responsabile: {com['committente']}",
    ]
    if valori:
        blocchi.insert(7, "three short lines of capitals: DEMOCRAZIA DIRETTA, TRASPARENZA, BENI COMUNI")
    elenco = "\n".join(f"{i}. {b};" for i, b in enumerate(blocchi, 1)).rstrip(";") + "."
    quanti = len(blocchi)
    # I due blocchi che spariscono per primi, e senza i quali la card non serve
    # a niente: la carica e l'istruzione di voto.
    n_carica = next(i for i, b in enumerate(blocchi, 1) if b.startswith("two lines of capitals"))
    n_voto = next(i for i, b in enumerate(blocchi, 1) if "BARRA IL SIMBOLO" in b)

    return f"""Vertical civic poster, 2:3, warm golden hour, split layout: photograph right, text left.

Use ALL the uploaded reference photographs together to rebuild the {uomo}'s face, not just the first one. {e['aspetto']} {e['espressione']} {e['abbigliamento']} {e['divieti']} {POSA} Behind {'her' if f else 'him'}, Naples from above at sunset: pale rooftops, the bay, Mount Vesuvius, clouds lit orange and gold. Warm light on the face from the left, natural skin texture, visible pores and lines.

The LEFT HALF is a plain warm parchment panel, divided from the photo by a thin vertical gold rule, with all text left aligned in dark brown engraved serif. It carries EXACTLY {quanti} blocks, all of them, in this order from top to bottom, spread over the full height of the panel:

{elenco}

⛔ All {quanti} blocks must be present. If they do not fit, reduce the size of the lettering and tighten the spacing: never drop a block, never shorten or summarise a line, never merge two blocks into one. Blocks {n_carica} and {n_voto} are the ones that get lost, and a poster without them is useless.

The text is Italian and every line must be reproduced exactly as written above, spelled correctly, with Italian accents and apostrophes intact: MUNICIPALITÀ carries the grave accent on the final A, d'Aosta carries the apostrophe. Each line appears once only. Do not add titles, labels, headings, addresses, phone numbers, extra slogans, or any word that is not in the list. Do not put quotation marks, brackets or dashes around the name.

Palette: amber, terracotta, cream, gold, deep brown. High contrast between the dark brown lettering and the parchment panel. Photorealistic, sharp correctly spelled lettering, print quality, 4K.

Before delivering, count the blocks on the finished panel: there must be {quanti}, in this order, none missing. Then read the whole text again: no repeated, misspelled or invented words, no missing accents, no line cut off or covered by the figure.

NEGATIVE PROMPT: {uomo} on the left, text on the right, centred layout, figure cut by the panel, face half hidden, person behind the panel, subject turned outwards, quotation marks around the name, MUNICIPALITA without the accent, missing accents, altered or redrawn logo, illegible logo lettering, distorted face, slimmed face, smoothed skin, beautified, younger face, {e.get('negativo', '').rstrip(', ')}, extra fingers, cartoon, 3D render, cold blue tones, night, gibberish text, misspelled text, duplicated lines, sparkle icon, AI badge, watermark, signature, flags, other party symbols"""


def prompt(c, com, senza_simbolo=False):
    f = c["genere"] == "f"
    art = "la persona di cui"
    migliorare = "migliorarla" if f else "migliorarlo"
    pr = "la" if f else "lo"          # pronome, per le concordanze
    riga7, modo7 = VOTO[c["ruolo"]]
    riga7 = riga7.format(cognome=c["cognome"])

    # ⛔ Il logo NON si fa disegnare al generatore quando si puo' evitare: lo
    #    ridisegna e ci traccia sopra una X che mangia le lettere. Con
    #    --senza-simbolo l'angolo resta vuoto e il simbolo VERO lo incolla
    #    _tools/sostituisci_simbolo.py. Provato il 4 agosto 2026: rattoppare
    #    un simbolo gia' disegnato su un fondo eterogeneo lascia un alone.
    # Le foto si contano, non si danno per quattro: vedi elenco_foto().
    foto = c.get("_foto") or ["A1", "A2", "A3", "A4"]
    n = len(foto)
    elenco = ", ".join(foto)
    intervallo = foto[0] if n == 1 else f"{foto[0]}-{foto[-1]}"
    if n == 1:
        riga_a = (f"IMMAGINE {foto[0]} - una fotografia di {c['nome'].title()}, "
                  f"{art} sto preparando il materiale e di cui ho il consenso: "
                  "e' la fonte del suo ritratto.")
    else:
        riga_a = (f"IMMAGINI {elenco} - {NUMERI[n]} fotografie della stessa "
                  f"persona, {c['nome'].title()}, {art} sto preparando il "
                  "materiale e di cui ho il consenso: sono la fonte del suo "
                  f"ritratto. Usale {INSIEME[n]} insieme per ricostruire il "
                  "viso, non solo la prima.")

    if senza_simbolo:
        quante, ruoli = NUMERI[n + 1], "due"
        riga_b = ""
        # Qui il logo non e' allegato: dire "simboli di partiti diversi da
        # quello allegato" contraddice la richiesta del disco vuoto.
        escludi_simboli = "simboli e loghi di qualunque genere"
        # ⭐ Lo spazio si lascia CIRCOLARE, non quadrato (Fernando, 4 agosto
        #    2026): il logo e' un disco, e un riquadro quadrato lascia sempre
        #    quattro angoli da rifilare a mano dopo l'incollaggio.
        blocco_simbolo = (
            "In basso a sinistra, sopra la figura, lascia una ZONA VUOTA "
            "CIRCOLARE, un disco largo circa un terzo della larghezza del "
            "manifesto, alla stessa altezza delle due righe del punto 7. Dentro "
            "quel cerchio non c'e' assolutamente nulla: solo il fondo pergamena, "
            "liscio e uniforme, senza bordi, senza cornice, senza ombra e senza "
            "contorno che ne segni il perimetro. Non disegnare nessun logo, "
            "nessun simbolo, nessuna X, nessun segnaposto: quello spazio lo "
            "riempio io dopo, e qualunque cosa tu ci metta va cancellata.")
    else:
        quante, ruoli = NUMERI[n + 2], "tre"
        escludi_simboli = "simboli di partiti diversi da quello allegato"
        riga_b = ("IMMAGINE B - il logo dell'associazione: riproducilo "
                  "fedelmente, senza ridisegnarlo e senza cambiarne i colori.\n")
        blocco_simbolo = (
            "In basso a sinistra, sopra la figura, il logo dell'immagine B "
            "riprodotto intero e perfettamente leggibile. Sopra il logo, due soli "
            "tratti sottili incrociati a formare una X, tracciati a mano con un "
            "pennarello rosso semitrasparente, come il segno che l'elettore fa "
            "sulla scheda.\nLa X non deve coprire nessuna lettera: le parole "
            "\"PARTECIPAZIONE\" e \"ATTIVA\" devono restare leggibili per intero. "
            "I tratti sono sottili, passano sopra la parte centrale del disegno e "
            "non sopra le scritte.\nIl logo sta alla stessa altezza delle due "
            "righe del punto 7.")

    # ⛔ I nomi propri si compitano lettera per lettera: e' l'unico modo per cui
    #    il generatore non li reinventa. Su Luigi aveva scritto "Bariianoraina
    #    ungnoli" al posto di "Bagnoli"; sul logo "PA TECIPAZI NE".
    propri = [c["cognome"]] + [w for w in c["territorio"].replace("e ", "").split()
                               if len(w) > 3]
    compitato = "; ".join(f"{w} si scrive {'-'.join(w.upper())}" for w in propri)

    return f"""Ti allego {quante} immagini, con {ruoli} ruoli diversi.
{riga_a}
{riga_b}IMMAGINE C - uno schema di impaginazione muto: i rettangoli grigi indicano soltanto dove va ogni elemento e quanto e' grande, e corrispondono nell'ordine dall'alto in basso all'elenco che trovi sotto. Non riprodurre i rettangoli, non riprodurne i colori, non scrivere parole che non siano nell'elenco.

Canvas: {com['canvas']}, risoluzione massima disponibile.

Crea un manifesto elettorale italiano da affissione, di quelli che si leggono a trenta metri di distanza: pochissimi elementi, molto grandi, ad alto contrasto.

IMPAGINAZIONE D'INSIEME: un fondo solo, chiaro e caldo, colore pergamena con una velatura dorata. {c['nome'].title()} e' ritagliat{'a' if f else 'o'} sul fondo, occupa la meta' sinistra e va da sopra fino al bordo inferiore, senza cornici e senza fasce che dividano la tela. Tutto il testo sta nella meta' destra, allineato a sinistra, e non copre mai il viso.

IL VOLTO E' L'ELEMENTO DOMINANTE. Ritrai {c['nome'].title()} esattamente come appare nelle fotografie {intervallo}, senza {migliorare} in nessun modo. Il criterio non e' che sia un bel ritratto: e' che chi {pr} conosce {pr} riconosca per strada.
Riporta fedelmente questi tratti, che nelle fotografie ci sono e che i ritratti generati tendono a cancellare: {c['tratti']}
{c['espressione']}
E' un ritratto posato per un manifesto, quindi la persona e' curata: capelli pettinati e in ordine, ma con il loro volume e il loro movimento naturale, non appiattiti e non ridisegnati.
{c['divieti']}
Inquadratura a mezzo busto, frontale, sguardo dritto nell'obiettivo. {c['abbigliamento']} {c['da_togliere']} Luce calda e frontale sul volto, nessuna ombra dura sugli occhi.

⛔ IL TESTO DEL MANIFESTO — da riprodurre ALLA LETTERA
Quelle che seguono sono le UNICHE parole che compaiono nel manifesto. Ogni riga va copiata carattere per carattere, esattamente come e' scritta qui, una volta sola. Il testo e' in italiano, in caratteri lapidari senza grazie, molto marcati, colore bruno scurissimo, e le righe stanno in quest'ordine dall'alto in basso:

1. in alto, grande: "{com['elezione']}"
2. subito sotto, piu' grande ancora e nel rosso caldo di accento: "{com['data']}"
3. piu' in basso, staccato e ben visibile: "{com['slogan']}"
4. subito sotto, di corpo medio: "{c['nome']}"
5. sotto, la riga piu' grande di tutto il manifesto dopo il volto: "{c['cognome']}"
6. piu' piccolo: "{c['carica']} · {c['territorio']}"
7. in fondo, {modo7}: {riga7}

{blocco_simbolo}

Sul bordo sinistro della tela, scritta in verticale e nel corpo piu' piccolo di tutto il manifesto: "Committente responsabile: {com['committente']}".

⛔ COME SI COPIA IL TESTO — la parte in cui si sbaglia sempre
Non tradurre, non abbreviare, non spezzare le parole con trattini, non ripeterle, non aggiungere articoli, preposizioni, titoli, etichette, intestazioni, indirizzi, numeri di telefono, siti, slogan o parole di alcun genere che non siano nell'elenco.
⛔ SE UNA RIGA NON CI STA NELLO SPAZIO, RIDUCI IL CORPO DEI CARATTERI O MANDA A CAPO: non accorciare, non riassumere e non riscrivere le parole. Una riga piu' piccola e' corretta, una riga storpiata rende il manifesto inutilizzabile.
I nomi propri sono la cosa che si sbaglia di piu': {compitato}. Rileggili sul manifesto finito e confrontali lettera per lettera con questa riga.

Colori: {com['colori']}. Il contrasto fra testo e fondo deve essere alto: in strada i toni delicati spariscono.
Prima di consegnare rileggi tutto il testo lettera per lettera, confrontandolo con l'elenco qui sopra: ogni riga deve essere identica, senza parole ripetute, storpiate o inventate. ⛔ Attenzione ai nomi di luogo: si scrivono soltanto "Bagnoli" e "Fuorigrotta", e non devono comparire altre parole che gli somigliano. Accenti e apostrofi corretti, nessuna riga tagliata o coperta dalla figura.
Escludi: titoli ed etichette non richiesti, fasce che dividono la tela in due, figura intera, ripresa di profilo, foto di gruppo, paesaggio nitido, aspetto da cartone animato, resa CGI, pelle di plastica, levigatura eccessiva del viso, bandiere, {escludi_simboli}, firme, filigrane, scritte di social network, nomi utente."""


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--candidato", help="chiave del candidato (es. rosa)")
    p.add_argument("--elenco", action="store_true", help="elenca i candidati salvati")
    p.add_argument("--dati", default=DATI, help=f"file delle impostazioni (default: {DATI})")
    p.add_argument("--senza-simbolo", action="store_true", dest="senza_simbolo",
                   help="l'angolo del simbolo resta VUOTO: il logo vero lo incolla "
                        "poi _tools/sostituisci_simbolo.py (consigliato)")
    p.add_argument("--stile", choices=["affissione", "card", "card-vuota", "ritratto", "figura"],
                   default="affissione",
                   help="affissione = manifesto 70x100 in italiano (default); "
                        "card = card social 2:3 in inglese, foto a destra e "
                        "pergamena a sinistra (Gemini e Lumina); "
                        "card-vuota = la stessa card ma SENZA testo, solo il "
                        "ritratto e il pannello vuoto: il testo si scrive dopo "
                        "in locale, e al generatore si chiede una fotografia")
    p.add_argument("--per-manifesto", action="store_true", dest="per_manifesto",
                   help="stile figura: figura CENTRATA in 7:10 per la catena "
                        "dell'affissione (scontorno, monta_manifesto.py, testo, "
                        "simbolo) invece del 2:3 con la figura a destra")
    p.add_argument("--valori", action="store_true",
                   help="stile card: rimette le tre righe DEMOCRAZIA DIRETTA / "
                        "TRASPARENZA / BENI COMUNI. Allunga l'elenco, e con la "
                        "colonna piena il generatore taglia: si usa solo se si "
                        "toglie qualcos'altro")
    p.add_argument("--uscita", help="scrive il prompt su file invece che a schermo")
    a = p.parse_args()

    percorso = os.path.expanduser(a.dati)
    if not os.path.exists(percorso):
        sys.exit(f"⛔ impostazioni non trovate: {percorso}")
    d = json.load(open(percorso, encoding="utf-8"))
    cand, com = d["candidati"], d["_comuni"]

    if a.elenco or not a.candidato:
        print(f"Candidati salvati in {a.dati}:\n")
        for k, c in cand.items():
            print(f"  {k:<12} {c['nome']} {c['cognome']:<12} {c['ruolo']:<12} "
                  f"→ {'barra il simbolo' if c['ruolo'] == 'presidente' else 'scrivi il cognome'}")
            if c.get("note"):
                print(f"               {c['nome'].title()}: {c['note']}")
        if not a.candidato:
            print("\nUsare --candidato <chiave> per generare il prompt.")
        return

    k = a.candidato.lower()
    if k not in cand:
        sys.exit(f"⛔ '{k}' non c'e'. Disponibili: {', '.join(cand)}")
    c = cand[k]
    # Le foto si contano sul disco: il prompt non deve mai annunciare
    # un'immagine che non gli allego (vedi elenco_foto).
    c["_foto"], file_foto = elenco_foto(c, os.path.dirname(os.path.dirname(percorso)))
    foto, nf = ", ".join(file_foto), len(file_foto)
    quante_foto = f"{foto} ({NUMERI[nf]} foto)" if nf != 1 else f"{foto} (una foto)"
    if a.stile == "card":
        testo = prompt_card(c, com, a.valori)
    elif a.stile == "card-vuota":
        testo = prompt_card_vuota(c)
    elif a.stile == "ritratto":
        testo = prompt_ritratto(c)
    elif a.stile == "figura":
        testo = prompt_figura(c, a.per_manifesto)
    else:
        testo = prompt(c, com, a.senza_simbolo)

    if a.uscita:
        open(os.path.expanduser(a.uscita), "w", encoding="utf-8").write(testo + "\n")
        print(f"scritto: {a.uscita}")
    else:
        print(testo)

    print(f"\n─── allegati, da {c['cartella_foto']}/ ───", file=sys.stderr)
    if a.stile == "figura":
        print("  SOLO le foto della persona. Il fondo esce vuoto: la figura si "
              "ritaglia e si monta in locale.", file=sys.stderr)
        if a.per_manifesto:
            print("  ⚠️  Meta AI lavora su UNA foto per volta: si carica la A1.",
                  file=sys.stderr)
            print(f"  poi: _tools/scontorna.py · _tools/monta_manifesto.py · "
                  "il testo · _tools/sostituisci_simbolo.py", file=sys.stderr)
        else:
            print(f"  poi: _tools/carta_social.py --figura <immagine> --candidato {k}",
                  file=sys.stderr)
    elif a.stile == "ritratto":
        print(f"  SOLO {foto} — niente logo, niente schema, niente "
              "pannello: qui si chiede una fotografia e basta.", file=sys.stderr)
        print("  poi: _tools/carta_social.py --ritratto <foto> --candidato "
              f"{k} monta pannello, scala e testo.", file=sys.stderr)
    elif a.stile == "card-vuota":
        # Niente logo e niente schema: si chiede una fotografia, e tutto il
        # resto lo scrive _tools/ dopo, sul file vero.
        print(f"  SOLO {quante_foto} della persona — niente logo, niente schema",
              file=sys.stderr)
        print("  poi: il testo e il simbolo si montano in locale sul pannello "
              "vuoto, rimisurando il bordo sul file generato.", file=sys.stderr)
    elif a.stile == "card":
        # Lo schema muto qui non serve: la posizione di ogni riga sta scritta
        # nel prompt, e un'immagine in piu' e' solo un'occasione per copiarne
        # i rettangoli (Fernando, 4 agosto 2026).
        print(f"  {quante_foto} · B (logo) — NIENTE schema C", file=sys.stderr)
        print("  ⚠️  Gemini: generare da aistudio.google.com, mai dall'app "
              "(stellina). Lumina: il bollino AI resta, va ritagliato.",
              file=sys.stderr)
        print("  ⚠️  Il committente va scritto per esteso PRIMA di pubblicare.",
              file=sys.stderr)
    elif a.senza_simbolo:
        print(f"  {quante_foto} · c (schema muto) — NIENTE logo", file=sys.stderr)
        print("  poi: _tools/sostituisci_simbolo.py per incollare il simbolo vero",
              file=sys.stderr)
    else:
        print(f"  {quante_foto} · B (logo) · c (schema muto)", file=sys.stderr)
    if c.get("note"):
        print(f"⚠️  {c['note']}", file=sys.stderr)


if __name__ == "__main__":
    main()
