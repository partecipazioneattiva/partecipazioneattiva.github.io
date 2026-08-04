#!/usr/bin/env python3
"""La GRIGLIA del manifesto: dove va la persona, dove il simbolo, dove il testo.

    python3 _tools/griglia_manifesto.py --schema griglia.png
    python3 _tools/griglia_manifesto.py --verifica manifesto_generato.png

⛔ PERCHE' ESISTE (4 agosto 2026, idea di Fernando)
Al generatore si chiede UNA COSA SOLA: la persona nella meta' sinistra del
foglio. Tutto il resto — meta' destra, fascia alta, fascia bassa — e' fondo
liscio e basta. Simbolo e scritte li mettiamo noi dopo, dai file veri.

⭐ E' la seconda versione dell'idea, ed e' molto meglio della prima. Prima si
faceva disegnare un DISCO VUOTO dove sarebbe andato il simbolo, e quel disco
aveva un contorno e una tinta sua: se il simbolo non lo copriva al pixel, sul
manifesto stampato restava una linea nera o un alone chiaro. Fernando l'ha
tagliata corta: se il fondo e' liscio dappertutto, non c'e' niente da coprire e
niente da misurare. Il posto del simbolo lo decidiamo noi, ed e' sempre lo
stesso.

Le coordinate stanno qui, in un posto solo, e da qui le legge chiunque: il
prompt, lo script del testo, sostituisci_simbolo.py. Dieci candidati devono
sembrare una campagna sola.

--schema disegna la griglia vuota, quotata in centimetri: e' il disegno da
         guardare per capire, e da tenere accanto quando si scrive il prompt.
--verifica prende un manifesto appena generato, ci stampa sopra la griglia e
         dice quanto la figura invade gli spazi che dovevano restare liberi.
         Sotto il 2% si passa, sopra si rigenera: il testo non si scrive su una
         spalla.

🟩 LE MISURE SONO SCELTE NOSTRE, non norme. La sola parte imposta per legge e'
il committente (L. 212/1956 art. 3), che sta nella fascia in fondo e non si
toglie. Il diametro del disco (0,414) non e' un numero tondo per caso: e'
quello che Nano Banana ha prodotto davvero il 4 agosto 2026 sul manifesto di
Luigi, misurato con _tools/misura_vuoto.py. Chiedere una misura che il
generatore gia' produce da solo costa molto meno che imporgliene una nuova.
"""
import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Tutto in frazioni della tela (x e larghezze sulla larghezza, y e altezze
# sull'altezza), cosi' valgono a qualunque misura di stampa.
# (x0, y0, x1, y1, nome, a cosa serve)
ZONE = [
    (0.030, 0.025, 0.970, 0.095, "FASCIA ALTA",   "elezione e data"),
    (0.620, 0.120, 0.970, 0.520, "COLONNA TESTO", "nome, carica, slogan"),
    (0.620, 0.560, 0.970, 0.700, "ISTRUZIONE",    "come si vota"),
    # ⭐ IL COMMITTENTE STA IN ALTO, NON IN FONDO (4 agosto 2026). In fondo non
    #    ci sta: un ritratto a mezzo busto allarga le spalle scendendo, e sulla
    #    prova di Luigi la giacca e' arrivata a 0,88 della larghezza — si
    #    mangiava tutta la fascia bassa. Sopra il 78% dell'altezza, invece, la
    #    figura non arriva mai oltre la meta'. Non e' un ripiego: la legge
    #    (L. 212/1956 art. 3) chiede che il committente ci sia e si legga, non
    #    che stia in basso.
    (0.620, 0.720, 0.970, 0.780, "COMMITTENTE",   "committente e sito"),
]
# Il disco del simbolo: bordo sinistro, bordo alto, diametro.
# ⭐ NON e' piu' un vuoto da far disegnare (Fernando, 4 agosto 2026): il fondo e'
#    liscio dappertutto, quindi questo e' semplicemente il POSTO dove lo script
#    incolla il simbolo. Nessun contorno da coprire, nessuna tinta da misurare,
#    nessuna sorpresa: le stesse tre cifre su tutti e dieci i manifesti.
#    ø 18 cm su 70×100: si legge da lontano senza mangiarsi il ritratto. Il
#    bordo basso resta a 4 cm dal margine, come i margini di sicurezza.
DISCO = (0.045, 0.778, 0.260)
# La persona: la meta' sinistra del foglio. Oltre questa colonna non deve
# arrivare nulla della figura, o il testo finisce addosso a una spalla.
FIGURA_FINO_A = 0.540


def griglia(W, H):
    """Le zone in pixel, per una tela W x H."""
    fuori = [(int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H), n, s)
             for x0, y0, x1, y1, n, s in ZONE]
    dx, dy, d = DISCO
    disco = (int(dx * W), int(dy * H), int((dx + d) * W), int(dy * H + d * W))
    return fuori, disco


def quota(cm_l, cm_h, x0, y0, x1, y1):
    return "%.0f×%.0f cm, a %.0f cm da sinistra e %.0f dall'alto" % (
        (x1 - x0) * cm_l, (y1 - y0) * cm_h, x0 * cm_l, y0 * cm_h)


def schema(uscita, W, H, cm_l, cm_h):
    im = Image.new("RGB", (W, H), (242, 224, 181))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 20)
        fp = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 15)
    except OSError:
        f = fp = ImageFont.load_default()

    # la meta' della persona
    d.rectangle([0, 0, int(FIGURA_FINO_A * W), H - 1], fill=(214, 204, 186))
    # sotto la fascia alta, o le due scritte si accavallano
    d.text((20, int(0.13 * H)), "QUI LA PERSONA", font=f, fill=(90, 80, 60))
    d.text((20, int(0.13 * H) + 26),
           "ritratto di chiunque:\nl'unica cosa che cambia\nda un manifesto all'altro",
           font=fp, fill=(110, 100, 80))

    zone, disco = griglia(W, H)
    for x0, y0, x1, y1, nome, uso in zone:
        d.rectangle([x0, y0, x1, y1], fill=(252, 246, 230), outline=(180, 60, 40), width=3)
        d.text((x0 + 10, y0 + 8), nome, font=f, fill=(180, 60, 40))
        d.text((x0 + 10, y0 + 32), uso, font=fp, fill=(140, 120, 90))
        d.text((x0 + 10, y1 - 24),
               quota(cm_l, cm_h, x0 / W, y0 / H, x1 / W, y1 / H), font=fp, fill=(150, 130, 100))

    # tratteggiato, non pieno: qui il generatore non deve lasciare nessun vuoto,
    # e' solo il posto dove lo script incolla il simbolo vero
    d.ellipse(disco, outline=(30, 90, 180), width=3)
    cx = (disco[0] + disco[2]) // 2
    cy = (disco[1] + disco[3]) // 2
    d.text((cx - 62, cy - 22), "IL SIMBOLO", font=f, fill=(30, 90, 180))
    d.text((cx - 62, cy + 2), "lo incolliamo noi\nø %.0f cm" % (DISCO[2] * cm_l),
           font=fp, fill=(30, 90, 180))
    im.save(uscita)
    print("schema: %s (%d × %d px, carta %g × %g cm)" % (uscita, W, H, cm_l, cm_h))
    for x0, y0, x1, y1, nome, uso in zone:
        print("  %-14s %s  — %s" % (nome, quota(cm_l, cm_h, x0/W, y0/H, x1/W, y1/H), uso))
    print("  %-14s ø %.0f cm, a %.1f cm da sinistra e %.1f dall'alto  — il simbolo"
          % ("DISCO", DISCO[2]*cm_l, DISCO[0]*cm_l, DISCO[1]*cm_h))


def verifica(percorso, uscita, cm_l, cm_h):
    im = Image.open(percorso).convert("RGB")
    a = np.array(im).astype(int)
    H, W, _ = a.shape
    # ⭐ Il fondo si RILEVA, non si presume (4 agosto 2026). Tarato su un
    #    intervallo fisso di pergamena, il controllo dava tutto occupato appena
    #    il generatore virava la tinta sul rosato — e un falso allarme che
    #    manda a rigenerare un manifesto buono costa piu' di uno mancato.
    #    Il fondo e' semplicemente il colore piu' diffuso della meta' destra,
    #    dove per costruzione non c'e' nessuno.
    destra = a[:, int(0.75 * W):].reshape(-1, 3)
    tinta = np.median(destra, axis=0)
    roba = np.abs(a - tinta).sum(axis=2) > 30

    zone, disco = griglia(W, H)
    print("manifesto %s — %d × %d px" % (percorso, W, H))
    tutto_bene = True
    for x0, y0, x1, y1, nome, _ in zone:
        fetta = roba[y0:y1, x0:x1]
        sporco = fetta.mean()
        segno = "✅" if sporco < 0.02 else "❌"
        if sporco >= 0.02:
            tutto_bene = False
        print("  %s %-14s occupato per il %.1f%%" % (segno, nome, sporco * 100))

    # La figura deve stare nella sua meta' SOLO all'altezza in cui si scrive.
    # Piu' in basso puo' allargarsi quanto vuole: un mezzo busto apre le spalle
    # scendendo, e sotto l'ultima zona non da' fastidio a nessuno.
    fin_qui = int(max(y1 for _, _, _, y1, _, _ in ZONE) * H)
    oltre = roba[:fin_qui, int(FIGURA_FINO_A * W):]
    colonne = np.nonzero(oltre.any(axis=0))[0]
    if len(colonne):
        fin_dove = (int(FIGURA_FINO_A * W) + colonne.max()) / W
        segno = "✅" if fin_dove < 0.60 else "❌"
        if fin_dove >= 0.60:
            tutto_bene = False
        print("  %s FIGURA         all'altezza delle scritte arriva a %.2f della "
              "larghezza (%.1f cm); il limite e' %.2f"
              % (segno, fin_dove, fin_dove * cm_l, FIGURA_FINO_A))
    else:
        print("  ✅ FIGURA         resta nella sua meta' dove si scrive")
    # sotto, solo per saperlo
    sotto = roba[fin_qui:, int(FIGURA_FINO_A * W):]
    giu = np.nonzero(sotto.any(axis=0))[0]
    if len(giu):
        print("     (piu' in basso le spalle arrivano a %.2f: non da' fastidio)"
              % ((int(FIGURA_FINO_A * W) + giu.max()) / W))

    # anteprima con la griglia stampata sopra
    sopra = im.convert("RGBA")
    velo = Image.new("RGBA", sopra.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(velo)
    for x0, y0, x1, y1, nome, _ in zone:
        d.rectangle([x0, y0, x1, y1], fill=(180, 60, 40, 60), outline=(180, 60, 40, 220), width=3)
    d.ellipse(disco, outline=(30, 90, 180, 220), width=4)
    Image.alpha_composite(sopra, velo).convert("RGB").save(uscita)
    print("  controllo a vista: %s" % uscita)
    print("\n%s" % ("tutto libero: si puo' scrivere" if tutto_bene else
                    "qualcosa invade i vuoti: rigenerare, o spostare le zone"))
    return 0 if tutto_bene else 1


def tela_guida(uscita, W, H):
    """La TELA GUIDA da caricare su Gemini insieme alle foto.

    ⛔ PERCHE' (4 agosto 2026). Chiedere a parole «la persona nella meta'
    sinistra» non funziona: su Luigi ha obbedito, su Paolo ha piazzato il
    ritratto in mezzo a tutta larghezza, stesso prompt. Le guide di Google non
    hanno nessun comando di posizionamento — l'unica leva documentata sulla
    struttura e' «usa l'immagine allegata come struttura».

    Quindi la composizione si CARICA. Questa tela ha il foglio gia' nel formato
    giusto, il fondo gia' del colore giusto, e una sagoma grigia di testa e
    spalle esattamente dove e quanto grande deve venire la persona. Al modello
    resta una richiesta sola, e facile: sostituisci il grigio con il ritratto.

    Il grigio (128,128,128) e' scelto perche' non esiste da nessun'altra parte
    nel manifesto: «sostituisci la sagoma grigia» non puo' voler dire altro.
    """
    im = Image.new("RGB", (W, H), (242, 224, 181))
    d = ImageDraw.Draw(im)
    grigio = (128, 128, 128)
    cx = 0.27 * W                       # asse del volto
    # testa: dal 10% al 40% dell'altezza
    ty0, ty1 = 0.10 * H, 0.40 * H
    tw = 0.115 * W                      # semilarghezza della testa
    d.ellipse([cx - tw, ty0, cx + tw, ty1], fill=grigio)
    # collo
    d.rectangle([cx - tw * 0.42, ty1 - tw * 0.30, cx + tw * 0.42, ty1 + tw * 0.55],
                fill=grigio)
    # spalle e busto: si aprono scendendo, escono dal bordo sinistro e sono
    # tagliate dal margine basso. A destra si fermano alla meta' del foglio.
    d.polygon([(cx - tw * 1.15, ty1 + tw * 0.30), (cx + tw * 1.15, ty1 + tw * 0.30),
               (0.540 * W, 0.62 * H), (0.540 * W, H), (-0.10 * W, H),
               (-0.10 * W, 0.62 * H)], fill=grigio)
    im.save(uscita)
    print("tela guida: %s (%d × %d)" % (uscita, W, H))
    print("  la sagoma grigia dice al generatore dove va la persona e quanto")
    print("  grande: volto sull'asse a 0,27 della larghezza, testa dal 10%% al")
    print("  40%% dell'altezza, spalle che non superano mai la meta' del foglio.")


def main():
    p = argparse.ArgumentParser(description="La griglia del manifesto")
    p.add_argument("--schema", help="disegna la griglia vuota in questo file")
    p.add_argument("--tela-guida", dest="tela_guida",
                   help="la tela da caricare su Gemini insieme alle foto")
    p.add_argument("--verifica", help="controlla un manifesto generato")
    p.add_argument("--uscita", default="controllo_griglia.png",
                   help="dove salvare l'anteprima di --verifica")
    p.add_argument("--tela", default="864x1232", help="px dello schema")
    p.add_argument("--carta", default="70x100", help="cm del foglio stampato")
    a = p.parse_args()
    cm_l, cm_h = (float(v) for v in a.carta.lower().split("x"))
    if a.schema:
        W, H = (int(v) for v in a.tela.lower().split("x"))
        schema(a.schema, W, H, cm_l, cm_h)
        return 0
    if a.tela_guida:
        W, H = (int(v) for v in a.tela.lower().split("x"))
        tela_guida(a.tela_guida, W, H)
        return 0
    if a.verifica:
        return verifica(a.verifica, a.uscita, cm_l, cm_h)
    p.error("serve --schema o --verifica")


if __name__ == "__main__":
    raise SystemExit(main())
