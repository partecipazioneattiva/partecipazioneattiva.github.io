#!/usr/bin/env python3
"""Ricostruisce una card dell'organigramma partendo dal ritratto vero.

    python3 _tools/card_organigramma.py ritratto.webp uscita.webp \
        --nome "STEFANO FRANCESCO PIVA" --carica "MEMBRO DEL DIRETTIVO"

⭐ 12 agosto 2026, e nasce da un errore pagato in diretta.

⛔ COSA NON FUNZIONA: incollare una testa dentro la card esistente. Provato,
pubblicato e ritirato nella stessa sera. Ingrandendo si vedeva la sagoma della
testa vecchia sotto quella nuova, la testa era sbilanciata rispetto a spalle
che erano di un altro, e il collo non c'era. Non e' un problema di sfumatura:
il corpo, la luce e le proporzioni appartengono alla fotografia di sotto.

🟩 COSA FUNZIONA: si ricostruisce. Il ritratto vero fa da fondo, e sopra ci
scriviamo noi intestazione, nome, carica e valori, con i nostri caratteri. Il
testo esce nitido, con gli accenti giusti, e la card di chiunque si rifa'
cambiando due parole sulla riga di comando.

Il simbolo e' il file vero, non disegnato: `_tools/simbolo/logo_pa.png`
oppure `--logo <percorso>`.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

CAR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caratteri")
LOGO = os.path.expanduser("~/Desktop/ARCHIVIO GENERALE/Claude IA/04_MANIFESTI_E_CARD/GEMINI LAVORI/Amilcare/prescelte/logo_pa.png")

LARGO, ALTO = 500, 750
ORO = (214, 168, 92)
CREMA = (247, 245, 246)
GRIGIO = (196, 190, 184)

TESTATA = "PARTECIPAZIONE ATTIVA"
SOTTOTESTATA = "Libera associazione di cittadini — fondata sulla Costituzione Italiana"
VALORI = "DEMOCRAZIA DIRETTA. TRASPARENZA. BENI COMUNI."
ARTICOLO = "La sovranità appartiene al popolo – art. 1 Costituzione Italiana"


def car(nome, punti):
    return ImageFont.truetype(os.path.join(CAR, nome), punti)


def sta_dentro(d, testo, fnt, larghezza):
    return d.textlength(testo, font=fnt) <= larghezza


def adatta(d, testo, nome_car, punti, larghezza):
    """Rimpicciolisce finche' la riga ci sta: ⛔ il testo non si taglia mai."""
    while punti > 8:
        fnt = car(nome_car, punti)
        if sta_dentro(d, testo, fnt, larghezza):
            return fnt
        punti -= 1
    return car(nome_car, 8)


def scrivi(tela, xy, testo, fnt, colore, ancora="mm", ombra=3):
    if ombra:
        velo = Image.new("RGBA", tela.size, (0, 0, 0, 0))
        ImageDraw.Draw(velo).text(xy, testo, font=fnt, fill=(0, 0, 0, 190), anchor=ancora)
        tela.alpha_composite(velo.filter(ImageFilter.GaussianBlur(ombra)))
    ImageDraw.Draw(tela).text(xy, testo, font=fnt, fill=colore, anchor=ancora)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ritratto")
    p.add_argument("uscita")
    p.add_argument("--nome", required=True)
    p.add_argument("--carica", required=True)
    p.add_argument("--sotto", default="Partecipazione Attiva")
    p.add_argument("--logo", default=LOGO)
    p.add_argument("--alto", type=float, default=0.0,
                   help="sposta il ritratto in alto o in basso, in frazioni "
                        "dell'altezza (positivo = piu' in basso)")
    p.add_argument("--zoom", type=float, default=1.0)
    a = p.parse_args()

    # ── il ritratto NON si ritaglia per riempire ─────────────────────────────
    # ⛔ Riempiendo la card con un primo piano si ottiene una faccia gigante
    #    tagliata ai bordi: il ritratto in giacca e' inquadrato stretto, la card
    #    e' alta e magra. Si appoggia il ritratto alla misura giusta e il resto
    #    della tela e' fondo scuro, preso dal ritratto stesso: cosi' non c'e'
    #    nessuna giunzione di colore.
    r = Image.open(a.ritratto).convert("RGBA")
    fondo_rgb = r.convert("RGB").getpixel((6, 6))
    tela = Image.new("RGBA", (LARGO, ALTO), fondo_rgb + (255,))
    s = (a.zoom * LARGO * 1.02) / r.width
    r = r.resize((int(r.width * s), int(r.height * s)), Image.LANCZOS)
    px = (LARGO - r.width) // 2
    py = int(ALTO * (0.055 + a.alto))
    # i bordi del ritratto si sfumano nel fondo, o si vede il rettangolo
    m = Image.new("L", r.size, 0)
    ImageDraw.Draw(m).rectangle((int(r.width * 0.02), 0,
                                 int(r.width * 0.98), r.height), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(r.width * 0.03))
    tela.paste(r, (px, py), m)

    # vignettatura: scurisce i bordi e fa staccare il testo dal fondo
    v = Image.new("L", (LARGO, ALTO), 0)
    ImageDraw.Draw(v).ellipse((-LARGO * 0.35, -ALTO * 0.25,
                               LARGO * 1.35, ALTO * 1.15), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(90))
    tela = Image.composite(tela, Image.new("RGBA", tela.size, (10, 8, 7, 255)), v)

    # bande scure in alto e in basso, dove va il testo
    for cima, fondo, forza in ((0, int(ALTO * 0.16), 205), (int(ALTO * 0.62), ALTO, 225)):
        b = Image.new("L", (LARGO, ALTO), 0)
        ImageDraw.Draw(b).rectangle((0, cima, LARGO, fondo), fill=forza)
        b = b.filter(ImageFilter.GaussianBlur(ALTO * 0.035))
        tela = Image.composite(Image.new("RGBA", tela.size, (8, 6, 5, 255)), tela, b)

    # il simbolo vero, grande e trasparente, in alto a destra
    if os.path.exists(a.logo):
        logo = Image.open(a.logo).convert("RGBA")
        # ⛔ 12 agosto 2026: il simbolo dev'essere DIETRO la persona. Disegnarlo
        #    dopo lo mette davanti e gli copre la spalla; disegnarlo prima non
        #    serve, perche' il ritratto non e' scontornato e lo ricopre tutto.
        #    Si risolve con una maschera di LUMINOSITA': il simbolo compare solo
        #    dove sotto c'e' fondo scuro, e sparisce dove c'e' la persona.
        lato = int(LARGO * 0.46)
        logo = logo.resize((lato, lato), Image.LANCZOS)
        px, py = int(LARGO * 0.62), int(ALTO * 0.105)
        sotto = tela.convert("L").crop((px, py, px + lato, py + lato))
        # scuro (fondo) -> 255 ; chiaro (viso, camicia) -> 0
        dietro = sotto.point(lambda v: 255 if v < 46 else (0 if v > 82 else
                                                          int(255 * (82 - v) / 36)))
        dietro = dietro.filter(ImageFilter.GaussianBlur(lato * 0.02))
        alfa = logo.split()[3].point(lambda v: int(v * 0.55))
        alfa = Image.composite(alfa, Image.new("L", alfa.size, 0), dietro)
        logo.putalpha(alfa)
        tela.alpha_composite(logo, (px, py))

    d = ImageDraw.Draw(tela)
    M = int(LARGO * 0.06)          # margine
    L = LARGO - 2 * M              # larghezza utile

    scrivi(tela, (LARGO // 2, int(ALTO * 0.048)), TESTATA,
           adatta(d, TESTATA, "merriweather-700-latin.ttf", 30, L), ORO)
    scrivi(tela, (LARGO // 2, int(ALTO * 0.087)), SOTTOTESTATA,
           adatta(d, SOTTOTESTATA, "montserrat-400-latin.ttf", 11, L), GRIGIO, ombra=2)

    scrivi(tela, (LARGO // 2, int(ALTO * 0.735)), a.nome,
           adatta(d, a.nome, "merriweather-700-latin.ttf", 30, L), CREMA)
    scrivi(tela, (LARGO // 2, int(ALTO * 0.784)), f"— {a.carica} —",
           adatta(d, f"— {a.carica} —", "montserrat-700-latin.ttf", 15, L), ORO)
    scrivi(tela, (LARGO // 2, int(ALTO * 0.820)), a.sotto,
           adatta(d, a.sotto, "montserrat-400-latin.ttf", 15, L), GRIGIO, ombra=2)

    ImageDraw.Draw(tela).line((M * 2, int(ALTO * 0.862), LARGO - M * 2, int(ALTO * 0.862)),
                              fill=(120, 96, 58, 200), width=1)
    scrivi(tela, (LARGO // 2, int(ALTO * 0.897)), VALORI,
           adatta(d, VALORI, "montserrat-700-latin.ttf", 13, L), CREMA, ombra=2)
    scrivi(tela, (LARGO // 2, int(ALTO * 0.933)), ARTICOLO,
           adatta(d, ARTICOLO, "montserrat-400-latin.ttf", 10, L), GRIGIO, ombra=2)

    tela.convert("RGB").save(a.uscita, "WEBP", quality=90, method=6)
    print(f"  ✅ {a.uscita}  {LARGO}x{ALTO}  "
          f"{os.path.getsize(a.uscita) // 1024} KB")


if __name__ == "__main__":
    main()
