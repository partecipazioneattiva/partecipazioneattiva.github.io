#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manifesto elettorale — Partecipazione Attiva.

Compone un manifesto stampabile partendo da tre pezzi:
  1. un ritratto gia' scontornato in PNG con canale alfa  (--ritratto)
  2. uno sfondo fotografico                               (--sfondo)
  3. il logo PA                                           (--logo)

Non genera nulla: monta. Lo scontorno si fa con `scontorna.py`, lo sfondo con
mflux/Z-Image Turbo (MANUALE_IMMAGINI_PROMPT_v1.md §2).

Formato di uscita: 70x100 cm a 120 dpi = 3308 x 4724 px, misura da affissione.
Le varianti social (4:5 e 9:16) si ritagliano dallo stesso master con --social.

⚠️ LEGGE 212/1956 art. 3: ogni manifesto di propaganda deve portare il nome del
   committente responsabile. Si passa con --committente "Nome Cognome": senza,
   il manifesto esce SENZA quella riga e non e' affiggibile in campagna.

Esempio:
    python3 _tools/crea_manifesto.py \
        --ritratto  ritratto.png \
        --sfondo    sfondo.png \
        --nome      "Antonio Cristiano" \
        --carica    "Candidato alla X Municipalita' di Napoli" \
        --uscita    manifesto.png
"""

import argparse
import os
import sys

from PIL import (Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont, ImageOps)

# ─────────────────────────────────────────────────────────── misure e colori ──

W, H = 3308, 4724           # 70x100 cm @ 120 dpi, misura da affissione

NAVY_FONDO   = (6, 17, 28)
NAVY_PANNELLO= (7, 20, 33)
AMBRA        = (242, 178, 74)
AMBRA_CALDA  = (237, 153, 53)
ROSSO_PA     = (218, 81, 52)
VERDE_PA     = (62, 145, 67)
BIANCO       = (255, 255, 255)
GRIGIO_CALDO = (201, 194, 183)

DUO_OMBRA    = (7, 21, 40)
DUO_LUCE     = (247, 209, 152)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FONT = os.path.expanduser("~/.cache/pa_fonts_ttf")


def prepara_font():
    """I caratteri del sito sono woff2, che Pillow non legge: li converte in ttf
    una volta sola dentro la cache. Stessi Montserrat/Merriweather del sito, cosi'
    il manifesto e le pagine parlano con la stessa voce.

    Due trappole gia' pagate:
    1. si prende il sottoinsieme `-latin`, NON `-latin-ext`: quest'ultimo contiene
       solo i caratteri accentati rari, l'alfabeto di base non c'e' e il testo
       esce a scatolette;
    2. i woff2 di Google sono font VARIABILI con asse wght il cui valore di
       partenza e' il piu' sottile. Pillow non applica gli assi: senza fissare
       il peso, un Montserrat 900 si stampa filiforme. Qui si fissa dal nome."""
    os.makedirs(CACHE_FONT, exist_ok=True)
    sorgente = os.path.join(REPO, "fonts")
    da_fare = []
    for f in sorted(os.listdir(sorgente)):
        if not f.endswith("-latin.woff2"):
            continue
        out = os.path.join(CACHE_FONT, f.replace("-latin.woff2", ".ttf"))
        if not os.path.exists(out):
            da_fare.append((os.path.join(sorgente, f), out, int(f.split("-")[1])))
    if da_fare:
        from fontTools.ttLib import TTFont          # serve solo la prima volta
        from fontTools.varLib import instancer
        for src, out, peso in da_fare:
            t = TTFont(src)
            if "fvar" in t:
                asse = {a.axisTag: a for a in t["fvar"].axes}["wght"]
                t = instancer.instantiateVariableFont(
                    t, {"wght": max(asse.minValue, min(asse.maxValue, peso))})
            t.flavor = None
            t.save(out)


# ────────────────────────────────────────────────────────────────── utilita' ──

def font(nome, dim):
    return ImageFont.truetype(os.path.join(CACHE_FONT, nome), dim)


def larghezza(testo, fnt, spaziatura=0):
    """Larghezza reale di una riga, spaziatura fra lettere compresa."""
    if not testo:
        return 0
    tot = sum(fnt.getlength(c) for c in testo)
    return tot + spaziatura * (len(testo) - 1)


def scrivi(dr, xy, testo, fnt, colore, spaziatura=0, ancora="ls"):
    """Disegna una riga con spaziatura fra lettere. Ancora: l/c/r + s (baseline)."""
    x, y = xy
    tot = larghezza(testo, fnt, spaziatura)
    if ancora[0] == "c":
        x -= tot / 2
    elif ancora[0] == "r":
        x -= tot
    for c in testo:
        dr.text((x, y), c, font=fnt, fill=colore, anchor="l" + ancora[1])
        x += fnt.getlength(c) + spaziatura
    return tot


def adatta(testo, nome_font, larghezza_max, dim_max, spaziatura_rel=0.0, dim_min=8):
    """Il corpo piu' grande (<= dim_max) con cui il testo sta dentro larghezza_max.

    dim_min va tenuto sotto dim_max: sui formati social i corpi scendono sotto i
    20 px, e un minimo piu' alto del massimo faceva uscire un testo PIU' GRANDE
    del previsto, che scavalcava quello accanto."""
    basso, alto = min(dim_min, dim_max), dim_max
    while basso < alto:
        m = (basso + alto + 1) // 2
        f = font(nome_font, m)
        if larghezza(testo, f, m * spaziatura_rel) <= larghezza_max:
            basso = m
        else:
            alto = m - 1
    return font(nome_font, basso), basso


def gradiente_verticale(dim, da_y, a_y, alfa_da, alfa_a):
    """Maschera L: alfa_da a da_y, alfa_a ad a_y, costante fuori."""
    w, h = dim
    m = Image.new("L", (1, h))
    px = m.load()
    for y in range(h):
        if y <= da_y:
            v = alfa_da
        elif y >= a_y:
            v = alfa_a
        else:
            t = (y - da_y) / max(1, (a_y - da_y))
            t = t * t * (3 - 2 * t)          # smoothstep: niente banding
            v = alfa_da + (alfa_a - alfa_da) * t
        px[0, y] = int(max(0, min(255, v)))
    return m.resize((w, h))


def duotone(im, ombra, luce, forza=0.72):
    """Vira la foto su due colori di marca, mantenendo un po' di colore vero."""
    g = im.convert("L")
    tavola = []
    for canale in range(3):
        tavola += [int(ombra[canale] + (luce[canale] - ombra[canale]) * (i / 255))
                   for i in range(256)]
    virata = Image.merge("RGB", (g, g, g)).point(tavola)
    return Image.blend(im.convert("RGB"), virata, forza)


def ombra_portata(alfa, sfoca, offset, opacita):
    """Ombra morbida da un canale alfa: torna (maschera, dx, dy)."""
    o = alfa.filter(ImageFilter.GaussianBlur(sfoca))
    o = o.point(lambda v: int(v * opacita))
    return o, offset[0], offset[1]


# ────────────────────────────────────────────────────────────────── montaggio ──

def costruisci(a, W, H):
    """Monta il manifesto su una tela qualsiasi.

    Le misure sono scritte come se la tela fosse il 70x100 (3308x4724) e poi
    riscalate: `o()` per tutto cio' che segue la larghezza (corpi, margini,
    filetti), `v()` per le quote verticali. Cosi' il post 4:5 e la storia 9:16
    si RICOMPONGONO invece di essere ritagliati — ritagliando si perdevano
    l'intestazione e il piede, cioe' logo e legge."""
    so, sv = W / 3308.0, H / 4724.0
    o = lambda x: int(round(x * so))
    v = lambda x: int(round(x * sv))
    margine = o(210)

    tela = Image.new("RGB", (W, H), NAVY_FONDO)

    # ── 1. sfondo fotografico: coprente in larghezza, virato e schiacciato ────
    y_pannello = v(3300)
    sf = Image.open(a.sfondo).convert("RGB")
    # Inquadratura: si allarga oltre la tela e poi si ritaglia, cosi' --fuoco
    # alza o abbassa l'orizzonte senza rigenerare lo sfondo.
    lw = int(W * a.zoom)
    lh = int(sf.height * lw / sf.width)
    sf = sf.resize((lw, lh), Image.LANCZOS)
    dx = (lw - W) // 2
    dy = int(max(0, lh - y_pannello) * a.fuoco)
    sf = sf.crop((dx, dy, dx + W, dy + y_pannello))

    # Il tramonto sul golfo e' tutto in mezzitoni: senza una curva a S il viraggio
    # lo spappola in un grigio oliva. Prima si apre il contrasto, poi si vira.
    sf = ImageOps.autocontrast(sf, cutoff=1)
    sf = ImageEnhance.Contrast(sf).enhance(1.30)
    sf = duotone(sf, DUO_OMBRA, DUO_LUCE, forza=0.62)
    sf = ImageEnhance.Color(sf).enhance(1.12)

    # buio generale + due sfumature: sopra per l'intestazione, sotto per il pannello
    scuro = Image.new("RGB", sf.size, NAVY_FONDO)
    sf = Image.blend(sf, scuro, 0.30)
    sf = Image.composite(scuro, sf, gradiente_verticale(sf.size, 0, v(980), 205, 0))
    sf = Image.composite(Image.new("RGB", sf.size, NAVY_PANNELLO), sf,
                         gradiente_verticale(sf.size, v(2380), y_pannello, 0, 255))

    # vignettatura: tiene l'occhio al centro
    vign = Image.new("L", sf.size, 0)
    ImageDraw.Draw(vign).ellipse(
        (-int(W * 0.35), -int(y_pannello * 0.30),
         int(W * 1.35), int(y_pannello * 1.30)), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(o(420))).point(
        lambda t: 255 - int(t * 0.55))
    sf = Image.composite(Image.new("RGB", sf.size, NAVY_FONDO), sf, vign)

    tela.paste(sf, (0, 0))

    # ── 2. pannello tipografico ──────────────────────────────────────────────
    dr = ImageDraw.Draw(tela)
    dr.rectangle((0, y_pannello, W, H), fill=NAVY_PANNELLO)

    # ── 3. ritratto: destra, appoggiato al pannello, dissolto nel bordo ───────
    rit = Image.open(a.ritratto).convert("RGBA")
    caselle = rit.split()[3].point(lambda t: 255 if t > 12 else 0).getbbox()
    rit = rit.crop(caselle)

    largh_rit = int(W * 0.62)
    rit = rit.resize((largh_rit, int(rit.height * largh_rit / rit.width)), Image.LANCZOS)
    rit = rit.filter(ImageFilter.UnsharpMask(radius=3.0, percent=68, threshold=3))

    x_rit = W - margine - largh_rit + int(largh_rit * 0.06)   # sbordo a destra
    y_rit = y_pannello + v(96) - rit.height

    # dissolvenza del taglio inferiore dentro il pannello
    al = rit.split()[3]
    al = ImageChops.multiply(al, gradiente_verticale(
        al.size, int(rit.height * 0.866), int(rit.height * 0.982), 255, 0))
    rit.putalpha(al)

    om, ox, oy = ombra_portata(al, sfoca=o(46), offset=(o(-34), v(26)), opacita=0.55)
    tela.paste(Image.new("RGB", rit.size, (0, 0, 0)), (x_rit + ox, y_rit + oy), om)
    tela.paste(rit, (x_rit, y_rit), rit)

    dr = ImageDraw.Draw(tela)

    # ── 4. intestazione ──────────────────────────────────────────────────────
    lato_logo = o(300)
    logo = Image.open(a.logo).convert("RGBA").resize((lato_logo, lato_logo), Image.LANCZOS)
    tela.paste(logo, (margine, v(190)), logo)

    xt = margine + lato_logo + o(62)
    fine_marchio = xt + scrivi(dr, (xt, v(292)), "PARTECIPAZIONE ATTIVA",
                               font("montserrat-800.ttf", o(82)), BIANCO,
                               spaziatura=3.5 * so)
    dr.text((xt, v(372)), "Libera associazione di cittadini",
            font=font("merriweather-400-italic.ttf", o(42)), fill=GRIGIO_CALDO, anchor="ls")

    # La data sta nello spazio che AVANZA dopo il marchio, non in una larghezza
    # fissa: altrimenti sui formati piccoli l'arrotondamento del corpo la fa
    # crescere in proporzione e le due righe si scavalcano.
    spazio_occ = int(W - margine - fine_marchio - o(90))
    f_occ, d_occ = adatta(a.occasione.upper(), "montserrat-700.ttf", spazio_occ, o(46), 0.15)
    scrivi(dr, (W - margine, v(300)), a.occasione.upper(), f_occ, AMBRA,
           spaziatura=d_occ * 0.15, ancora="rs")
    dr.rectangle((W - margine - o(300), v(348), W - margine, v(356)), fill=AMBRA)

    # ── 5. slogan sulla colonna di sinistra ──────────────────────────────────
    # La colonna finisce dove comincia la spalla del ritratto, non prima:
    # e' quello il vincolo, non una frazione arbitraria della tela.
    col = max(o(560), x_rit + int(largh_rit * 0.06) - margine - o(70))
    righe = [r.strip() for r in a.slogan.split("|") if r.strip()]
    dim_slog = min(adatta(r, "merriweather-700.ttf", col, o(132))[1] for r in righe)
    f_slog = font("merriweather-700.ttf", dim_slog)

    xs, ys = margine, v(2060)
    y_filo = ys - int(dim_slog * 1.20)
    dr.rectangle((xs, y_filo, xs + o(180), y_filo + o(13)), fill=AMBRA)
    for riga in righe:
        dr.text((xs, ys), riga, font=f_slog, fill=BIANCO, anchor="ls")
        ys += int(dim_slog * 1.30)

    ys += v(46)
    for riga in a.valori.split("|"):
        f_val, d_val = adatta(riga.strip().upper(), "montserrat-600.ttf", col, o(50), 0.13)
        scrivi(dr, (xs, ys), riga.strip().upper(), f_val, (226, 220, 210),
               spaziatura=d_val * 0.13)
        ys += v(78)

    # ── 6. blocco nome e carica ──────────────────────────────────────────────
    utile = W - 2 * margine
    y = y_pannello + v(300)

    f_nome, dim = adatta(a.nome.upper(), "montserrat-900.ttf", utile, o(268), 0.005)
    scrivi(dr, (margine, y + dim * 0.78), a.nome.upper(), f_nome, BIANCO,
           spaziatura=dim * 0.005)
    y += int(dim * 0.78) + v(78)

    dr.rectangle((margine, y, margine + o(560), y + o(14)), fill=AMBRA)
    y += v(100)

    f_car, dim = adatta(a.carica.upper(), "montserrat-700.ttf", utile, o(92), 0.03)
    scrivi(dr, (margine, y + dim * 0.78), a.carica.upper(), f_car, AMBRA,
           spaziatura=dim * 0.03)
    y += int(dim * 0.78) + v(66)

    if a.territori:
        f_ter, dim = adatta(a.territori, "montserrat-600.ttf", utile, o(62), 0.01)
        scrivi(dr, (margine, y + dim * 0.78), a.territori, f_ter, GRIGIO_CALDO,
               spaziatura=dim * 0.01)

    # ── 7. piede ─────────────────────────────────────────────────────────────
    y_piede = H - v(250)
    alt_barra = max(4, o(18))
    barra = Image.new("RGB", (W, alt_barra))
    bd = ImageDraw.Draw(barra)
    for x in range(W):
        t = x / W
        if t < 0.5:
            u, da, aa = t / 0.5, VERDE_PA, AMBRA_CALDA
        else:
            u, da, aa = (t - 0.5) / 0.5, AMBRA_CALDA, ROSSO_PA
        bd.line((x, 0, x, alt_barra), fill=tuple(int(da[i] + (aa[i] - da[i]) * u)
                                                 for i in range(3)))
    tela.paste(barra, (0, y_piede))

    yb = y_piede + v(140)
    scrivi(dr, (margine, yb), a.sito, font("montserrat-700.ttf", o(58)), BIANCO,
           spaziatura=4 * so)

    if a.committente:
        scrivi(dr, (margine, yb + v(74)), "Committente responsabile: " + a.committente,
               font("montserrat-400.ttf", o(34)), GRIGIO_CALDO, spaziatura=so)

    if a.nota:
        scrivi(dr, (W - margine, yb + v(74)), a.nota,
               font("montserrat-400.ttf", o(32)), (128, 138, 148), spaziatura=so,
               ancora="rs")

    logo_p = Image.open(a.logo).convert("RGBA").resize((o(150), o(150)), Image.LANCZOS)
    tela.paste(logo_p, (W - margine - o(150), yb - v(108)), logo_p)

    return grana(tela, forza=3.2 * max(0.55, so))


def grana(im, forza=3.2):
    """Grana finissima su tutta la tela. In stampa grande le sfumature piatte del
    cielo si aprono a fasce (banding): un filo di rumore le rompe."""
    import numpy as np
    rng = np.random.default_rng(7)
    rumore = rng.normal(0.0, forza, im.size[::-1] + (1,))
    dati = np.asarray(im, dtype=np.float32) + rumore
    return Image.fromarray(np.clip(dati, 0, 255).astype(np.uint8))


def adatta_social(master, larg, alt, fuoco=0.5):
    """Versione social. Se il formato e' piu' stretto del manifesto si ritaglia in
    verticale; se e' piu' alto NON si ritaglia di lato — si perderebbe il cognome —
    ma si appoggia il manifesto intero su fondo di marca."""
    r_master = master.width / master.height
    if larg / alt >= r_master:
        k = max(larg / master.width, alt / master.height)
        im = master.resize((int(master.width * k), int(master.height * k)), Image.LANCZOS)
        x = (im.width - larg) // 2
        y = int((im.height - alt) * fuoco)
        return im.crop((x, y, x + larg, y + alt))

    k = larg / master.width
    im = master.resize((larg, int(master.height * k)), Image.LANCZOS)
    tela = Image.new("RGB", (larg, alt), NAVY_PANNELLO)
    tela.paste(im, (0, (alt - im.height) // 2))
    return tela


def main():
    p = argparse.ArgumentParser(description="Manifesto elettorale PA")
    p.add_argument("--ritratto", required=True)
    p.add_argument("--sfondo", required=True)
    p.add_argument("--logo", default="LOGO-PA.webp")
    p.add_argument("--nome", required=True)
    p.add_argument("--carica", required=True)
    p.add_argument("--territori", default="")
    p.add_argument("--occasione", default="Elezioni comunali di Napoli · 2027")
    p.add_argument("--slogan", default="Partiamo|dal quartiere.")
    p.add_argument("--valori", default="Democrazia diretta|Trasparenza|Beni comuni")
    p.add_argument("--sito", default="partecipazione-attiva.it")
    p.add_argument("--zoom", type=float, default=1.30,
                   help="quanto lo sfondo esce dalla tela prima del ritaglio")
    p.add_argument("--fuoco", type=float, default=0.72,
                   help="0 = tiene il cielo, 1 = tiene il primo piano")
    p.add_argument("--committente", default="",
                   help="obbligatorio per l'affissione (L. 212/1956 art. 3)")
    p.add_argument("--nota", default="")
    p.add_argument("--uscita", required=True)
    p.add_argument("--social", action="store_true",
                   help="produce anche 1080x1350 e 1080x1920")
    a = p.parse_args()

    prepara_font()
    master = costruisci(a, W, H)
    master.save(a.uscita, dpi=(120, 120))
    print("manifesto:", a.uscita, master.size)

    if a.social:
        base = os.path.splitext(a.uscita)[0]
        for suff, (lw, lh) in {"_post": (1080, 1350),
                               "_storia": (1080, 1920)}.items():
            costruisci(a, lw, lh).save(base + suff + ".jpg", quality=94)
            print("social:", base + suff + ".jpg", (lw, lh))
        # L'anteprima dei link e' orizzontale: qui il manifesto non si ricompone,
        # si appoggia intero sul fondo di marca.
        adatta_social(master, 1200, 630).save(base + "_anteprima.jpg", quality=92)

    if not a.committente:
        print("\n⚠️  Manca il committente responsabile: questo file NON e' affiggibile.\n"
              "    Rilanciare con --committente \"Nome Cognome\" prima della stampa.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
