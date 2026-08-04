#!/usr/bin/env python3
"""Monta il ritratto nella meta' sinistra del manifesto. La composizione la
decidiamo noi, non il generatore.

    python3 _tools/monta_manifesto.py --ritratto paolo_scontornato.png \\
        --uscita paolo_montato.png

⛔ PERCHE' ESISTE (4 agosto 2026)
Per due manifesti di fila si e' chiesto al generatore di mettere la persona
nella meta' sinistra e lasciare vuoto il resto. Su Luigi l'ha fatto, su Paolo
l'ha ignorato e ha piazzato il ritratto in mezzo, a tutta larghezza. Fernando:
«questo va scritto in modo perfetto, non affidato al caso».

Non e' affidabile perche' non puo' esserlo: quei modelli non hanno un
posizionamento geometrico: la composizione la riscrivono a ogni tiro. La ricerca
sul campo (guida di Google Cloud, guida DeepMind, comunita' Gemini) dice tutta
la stessa cosa: la composizione non si descrive, si MOSTRA — con una tela di
partenza, con un rapporto di forma, con uno schizzo di struttura.

Il grado piu' alto di quel principio e' questo script: la composizione non si
mostra nemmeno, si FA. Al generatore si chiede solo la cosa che sa fare — un
ritratto somigliante — e la tela, la scala e la posizione le calcola qui una
formula, uguale per tutti e dieci i candidati.

COME POSIZIONA
1. Il centro del VOLTO, non del corpo: si prende la fascia alta della sagoma
   (testa e capelli, dove le spalle non arrivano ancora) e se ne misura il
   centro. Allineare sul corpo sposta il volto a ogni ritratto, perche' le
   spalle sono asimmetriche.
2. La scala si prende dall'altezza: la testa comincia a --testa dell'altezza e
   il busto scende oltre il bordo basso, tagliato dal margine come su un
   manifesto vero.
3. Se cosi' la spalla destra scavalca la meta' del foglio — dove poi va il
   testo — la scala si riduce quel tanto che basta. Meglio un volto un poco
   piu' piccolo che una spalla sotto le parole.
4. Quel che esce a SINISTRA non e' un problema: esce dal foglio, come in tutti
   i manifesti. Quel che esce a destra lo e', e non succede mai.
"""
import argparse

import numpy as np
from PIL import Image

PERGAMENA = (242, 224, 181)   # il fondo dei nostri manifesti


def centro_volto(alfa, y0, y1):
    """Centro orizzontale della sagoma nella sua fascia alta: la testa."""
    fascia = alfa[y0:y0 + int((y1 - y0) * 0.30)]
    colonne = np.nonzero(fascia.any(axis=0))[0]
    return (colonne.min() + colonne.max()) / 2


def collo(alfa, y0, y1):
    """La riga del collo: dove la sagoma e' piu' stretta fra la testa e le spalle.

    Serve a scalare sulla TESTA e non sulla figura intera. Su un manifesto
    l'unica misura che conta e' quanto e' grande il volto: le spalle escono dai
    bordi e non fanno testo. Scalando sulla figura, un ritratto con le spalle
    larghe fa venire la faccia piccola — l'errore che ha rovinato i primi
    montaggi del 4 agosto 2026.
    """
    largh = alfa.sum(axis=1).astype(float)
    a, b = y0 + int((y1 - y0) * 0.12), y0 + int((y1 - y0) * 0.55)
    fascia = largh[a:b]
    return a + int(np.argmin(fascia))


def main():
    p = argparse.ArgumentParser(description="Monta il ritratto sul manifesto")
    p.add_argument("--ritratto", required=True, help="PNG scontornato, con alfa")
    p.add_argument("--uscita", required=True)
    p.add_argument("--tela", default="1400x2000", help="px del manifesto (7:10)")
    p.add_argument("--fondo", default=None, help="colore R,G,B; default pergamena")
    p.add_argument("--testa", type=float, default=0.06,
                   help="a che altezza comincia la testa, in frazioni")
    p.add_argument("--testa-alta", dest="testa_alta", type=float, default=0.30,
                   help="quanto e' alta la TESTA rispetto al foglio")
    p.add_argument("--volto", type=float, default=0.27,
                   help="dove cade il centro del volto, in frazioni di larghezza")
    p.add_argument("--prolunga", action="store_true",
                   help="allunga il busto fino al bordo ripetendo l'ultima riga. "
                        "⚠️ su una giacca a fantasia lascia una colonna di righe "
                        "stirate: si usa solo su tessuti lisci e scuri, o si "
                        "cambia foto con una a figura piu' intera")
    p.add_argument("--meta", type=float, default=0.54,
                   help="oltre questa colonna la figura non deve arrivare")
    a = p.parse_args()

    W, H = (int(v) for v in a.tela.lower().split("x"))
    fondo = tuple(int(v) for v in a.fondo.split(",")) if a.fondo else PERGAMENA

    rit = Image.open(a.ritratto).convert("RGBA")
    alfa = np.array(rit)[:, :, 3] > 16
    ys, xs = np.nonzero(alfa)
    if not len(ys):
        print("❌ il ritratto e' tutto trasparente")
        return 1
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    cv = centro_volto(alfa, y0, y1)

    # 1) la scala si prende dalla TESTA: e' l'unica misura che conta su un
    #    manifesto. Le spalle escono dai bordi e non danno fastidio.
    yc = collo(alfa, y0, y1)
    k = a.testa_alta * H / max(yc - y0, 1)
    # 2) se la spalla destra scavalca la meta', si riduce quel tanto che basta
    destra = (x1 - cv) * k                     # quanto sporge a destra del volto
    massimo = a.meta * W - a.volto * W         # quanto spazio c'e'
    if destra > massimo:
        k *= massimo / destra
        print("  scala ridotta a %.2f: con quella piena la spalla destra "
              "arrivava a %.2f della larghezza" % (k, (a.volto * W + destra) / W))

    larg = int(round((x1 - x0 + 1) * k))
    alt = int(round((y1 - y0 + 1) * k))
    figura = rit.crop((x0, y0, x1 + 1, y1 + 1)).resize((larg, alt), Image.LANCZOS)

    # 3) il volto va dove diciamo noi; la testa comincia a --testa
    dx = int(round(a.volto * W - (cv - x0) * k))
    dy = int(round(a.testa * H))

    tela = Image.new("RGBA", (W, H), fondo + (255,))
    # ⭐ IL BUSTO SI PROLUNGA FINO AL BORDO (4 agosto 2026). Le fotografie vere
    #    sono quasi sempre tagliate al petto: scalate sulla testa, il busto
    #    finisce a mezzo foglio e la persona sembra sospesa. L'ultima riga della
    #    sagoma — giacca e camicia — si ripete fino al margine basso: il tessuto
    #    e' verticale, e il prolungamento non si vede. E' la stessa cosa che fa
    #    il margine quando taglia un ritratto scattato piu' lungo.
    if a.prolunga and dy + alt < H:
        coda = figura.crop((0, alt - 1, larg, alt)).resize(
            (larg, H - dy - alt + 1), Image.NEAREST)
        figura_lunga = Image.new("RGBA", (larg, H - dy), (0, 0, 0, 0))
        figura_lunga.paste(figura, (0, 0))
        figura_lunga.paste(coda, (0, alt - 1))
        figura = figura_lunga
        alt = H - dy
    tela.alpha_composite(figura, (dx, dy))
    tela.convert("RGB").save(a.uscita)

    fin_dove = (dx + larg) / W
    print("montato: %s (%d × %d)" % (a.uscita, W, H))
    print("  volto al %.2f della larghezza, testa al %.2f dell'altezza"
          % (a.volto, a.testa))
    print("  la figura arriva a %.2f a destra (limite %.2f) e a %.2f a sinistra"
          % (fin_dove, a.meta, dx / W))
    if dx < 0:
        print("  esce dal bordo sinistro: e' voluto, il foglio taglia le spalle")

    # ⚠️ Il busto deve arrivare al bordo basso, tagliato dal margine. Se resta
    #    corto vuol dire che la scala e' stata ridotta molto, e la scala si
    #    riduce solo per un motivo: il ritratto e' largo e frontale, un mezzo
    #    busto che in mezza colonna non ci sta senza rimpicciolire la testa.
    #    Non e' un difetto del montaggio, e' la forma del ritratto: si rigenera
    #    stretto, e la forma la impone il RAPPORTO della tela, non le parole.
    if dy + alt < H * 0.98:
        print("\n⚠️  la figura si ferma al %.2f dell'altezza invece di arrivare in"
              " fondo." % ((dy + alt) / H))
        print("    Il ritratto e' troppo largo per una mezza colonna: cosi' il")
        print("    volto viene piccolo. Rigeneralo in formato VERTICALE STRETTO")
        print("    (rapporto 1:2), dove l'inquadratura stretta e' obbligata dalla")
        print("    forma della tela e non dipende da come e' scritto il prompt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
