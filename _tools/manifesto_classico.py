#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manifesto elettorale PA — stile classico caldo.

E' la lingua visiva di «Insieme per Napoli»: panorama dorato, impaginazione
centrata, serif lapidario, fascia color pergamena in basso. Chiaro e luminoso,
non notturno (per la versione scura vedi `crea_manifesto.py`).

Tre pezzi in ingresso, nessuno generato qui:
  1. ritratto gia' scontornato in PNG con alfa   (--ritratto, vedi scontorna.py)
  2. panorama fotografico caldo                  (--sfondo, vedi mflux §2)
  3. logo PA                                     (--logo)

Uscita: 3308x4724 px = 70x100 cm a 120 dpi, misura da affissione, piu' le
versioni social ricomposte (non ritagliate) con --social.

⚠️ LEGGE 212/1956 art. 3: ogni manifesto di propaganda deve portare il nome del
   committente responsabile — `--committente "Nome Cognome"`. Senza, il file non
   e' affiggibile e lo strumento lo dice.
"""

import argparse
import os
import sys

from PIL import (Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont, ImageOps)

W, H = 3308, 4724

# ── colori: tutti caldi, presi dal manifesto «Insieme per Napoli» ─────────────
BRUNO_SCURO  = (58, 33, 18)      # titoli sulla pergamena
BRUNO        = (92, 56, 28)
BRUNO_TENUE  = (120, 84, 52)
PERGAMENA    = (243, 231, 205)
PERGAMENA_OMBRA = (226, 208, 172)
ORO          = (176, 124, 42)
ORO_CHIARO   = (222, 176, 92)
CREMA        = (255, 249, 235)
ROSSO_PA     = (218, 81, 52)
VERDE_PA     = (62, 145, 67)
AMBRA_CALDA  = (237, 153, 53)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FONT = os.path.expanduser("~/.cache/pa_fonts_ttf")
FONT_SISTEMA = os.path.expanduser("~/Library/Fonts")

# Il display e' Cinzel (lapidario, come nel manifesto di riferimento); i corsivi
# sono il Merriweather del sito, cosi' il manifesto e le pagine si somigliano.
LAPIDARIO = os.path.join(FONT_SISTEMA, "Cinzel-Regular.ttf")
SERIF_TESTO = os.path.join(FONT_SISTEMA, "Cormorant-Bold.ttf")


def prepara_font():
    """woff2 del sito -> ttf in cache. Due trappole gia' pagate: si prende il
    sottoinsieme `-latin` (in `-latin-ext` non c'e' l'alfabeto di base) e si
    fissa l'asse `wght`, perche' sono font variabili che partono dal peso piu'
    sottile e Pillow non applica gli assi."""
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
        from fontTools.ttLib import TTFont
        from fontTools.varLib import instancer
        for src, out, peso in da_fare:
            t = TTFont(src)
            if "fvar" in t:
                asse = {a.axisTag: a for a in t["fvar"].axes}["wght"]
                t = instancer.instantiateVariableFont(
                    t, {"wght": max(asse.minValue, min(asse.maxValue, peso))})
            t.flavor = None
            t.save(out)


def font(percorso, dim):
    if not os.path.isabs(percorso):
        percorso = os.path.join(CACHE_FONT, percorso)
    return ImageFont.truetype(percorso, max(6, int(dim)))


def larghezza(testo, fnt, sp=0):
    if not testo:
        return 0
    return sum(fnt.getlength(c) for c in testo) + sp * (len(testo) - 1)


def _origine(x, testo, fnt, sp, ancora):
    tot = larghezza(testo, fnt, sp)
    if ancora[0] == "m":
        x -= tot / 2
    elif ancora[0] == "r":
        x -= tot
    return x, tot


def scrivi(dr, xy, testo, fnt, colore, sp=0, ancora="ms", spessore=0):
    """Riga con spaziatura fra lettere (Pillow non ha il letter-spacing)."""
    x, tot = _origine(xy[0], testo, fnt, sp, ancora)
    for c in testo:
        dr.text((x, xy[1]), c, font=fnt, fill=colore, anchor="ls",
                stroke_width=spessore, stroke_fill=colore)
        x += fnt.getlength(c) + sp
    return tot


def scrivi_su_foto(tela, xy, testo, fnt, colore, sp=0, ancora="ms", spessore=0,
                   alone=(70, 42, 20), raggio=26, forza=0.72):
    """Come scrivi(), ma con un alone SFOCATO sotto: il testo chiaro deve reggere
    su un panorama che in certi punti e' altrettanto chiaro. Un contorno netto
    farebbe l'effetto adesivo — qui si stampa la scritta su un livello a parte,
    lo si sfoca e lo si posa sotto la scritta nitida."""
    strato = Image.new("L", tela.size, 0)
    ds = ImageDraw.Draw(strato)
    x, tot = _origine(xy[0], testo, fnt, sp, ancora)
    for c in testo:
        ds.text((x, xy[1]), c, font=fnt, fill=255, anchor="ls",
                stroke_width=spessore + max(2, raggio // 6), stroke_fill=255)
        x += fnt.getlength(c) + sp
    strato = strato.filter(ImageFilter.GaussianBlur(raggio)).point(
        lambda t: int(t * forza))
    tela.paste(Image.new("RGB", tela.size, alone), (0, 0), strato)
    scrivi(ImageDraw.Draw(tela), xy, testo, fnt, colore, sp, ancora, spessore)
    return tot


def adatta(testo, percorso, larg_max, dim_max, sp_rel=0.0):
    """Il corpo piu' grande (<= dim_max) con cui il testo sta in larg_max.
    Il minimo non puo' superare il massimo: sui social i corpi scendono sotto i
    20 px, e un minimo piu' alto faceva uscire il testo PIU' grande."""
    basso, alto = min(8, dim_max), int(dim_max)
    while basso < alto:
        m = (basso + alto + 1) // 2
        if larghezza(testo, font(percorso, m), m * sp_rel) <= larg_max:
            basso = m
        else:
            alto = m - 1
    return font(percorso, basso), basso


def gradiente_verticale(dim, da_y, a_y, alfa_da, alfa_a):
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
            t = t * t * (3 - 2 * t)
            v = alfa_da + (alfa_a - alfa_da) * t
        px[0, y] = int(max(0, min(255, v)))
    return m.resize((w, h))


def grana(im, forza):
    """In stampa grande le sfumature piatte del cielo si aprono a fasce."""
    import numpy as np
    rng = np.random.default_rng(7)
    dati = np.asarray(im, dtype=np.float32) + rng.normal(0.0, forza, im.size[::-1] + (1,))
    return Image.fromarray(np.clip(dati, 0, 255).astype(np.uint8))


# ────────────────────────────────────────────────────────────────── montaggio ──

def costruisci(a, W, H):
    so, sv = W / 3308.0, H / 4724.0
    o = lambda x: int(round(x * so))
    v = lambda x: int(round(x * sv))
    margine = o(190)
    cx = W // 2

    tela = Image.new("RGB", (W, H), PERGAMENA)

    # ── 1. panorama: caldo e LUMINOSO. Qui non si scurisce, si schiarisce ─────
    y_fascia = v(3560)
    sf = Image.open(a.sfondo).convert("RGB")
    lw = int(W * a.zoom)
    sf = sf.resize((lw, int(sf.height * lw / sf.width)), Image.LANCZOS)
    dx = (lw - W) // 2
    dy = int(max(0, sf.height - y_fascia) * a.fuoco)
    sf = sf.crop((dx, dy, dx + W, dy + y_fascia))

    sf = ImageEnhance.Brightness(sf).enhance(a.luce)
    sf = ImageEnhance.Contrast(sf).enhance(1.10)
    sf = ImageEnhance.Color(sf).enhance(1.10)
    sf = Image.blend(sf, Image.new("RGB", sf.size, CREMA), 0.07)   # velo di luce

    # alone chiaro dietro l'intestazione, cosi' il bruno del titolo si stacca
    sf = Image.composite(Image.new("RGB", sf.size, CREMA), sf,
                         gradiente_verticale(sf.size, 0, v(1180), 132, 0))
    # e verso il basso il panorama entra nella pergamena senza taglio netto
    sf = Image.composite(Image.new("RGB", sf.size, PERGAMENA), sf,
                         gradiente_verticale(sf.size, v(3140), y_fascia, 0, 235))

    # vignettatura calda, leggera: chiude i bordi senza incupire
    vign = Image.new("L", sf.size, 0)
    ImageDraw.Draw(vign).ellipse((-int(W * 0.30), -int(y_fascia * 0.26),
                                  int(W * 1.30), int(y_fascia * 1.26)), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(o(380))).point(
        lambda t: 255 - int(t * 0.34))
    sf = Image.composite(Image.new("RGB", sf.size, (196, 158, 108)), sf, vign)

    tela.paste(sf, (0, 0))

    # ── 2. fascia pergamena in basso ─────────────────────────────────────────
    dr = ImageDraw.Draw(tela)
    dr.rectangle((0, y_fascia, W, H), fill=PERGAMENA)
    for y, col in ((y_fascia, ORO), (y_fascia + o(12), ORO_CHIARO)):
        dr.rectangle((0, y, W, y + o(7)), fill=col)

    # ── 3. ritratto centrato, appoggiato alla fascia ─────────────────────────
    if a.scena_unica:                      # la persona e' gia' dentro lo sfondo
        return _chiudi(a, tela, ImageDraw.Draw(tela), W, H, o, v, margine, cx,
                       y_fascia)
    rit = Image.open(a.ritratto).convert("RGBA")
    rit = rit.crop(rit.split()[3].point(lambda t: 255 if t > 12 else 0).getbbox())
    largh_rit = int(W * a.larghezza_ritratto)
    rit = rit.resize((largh_rit, int(rit.height * largh_rit / rit.width)), Image.LANCZOS)
    rit = rit.filter(ImageFilter.UnsharpMask(radius=3.0, percent=62, threshold=3))

    # il ritratto viene da uno studio TV: va portato alla luce del panorama,
    # altrimenti resta un ritaglio freddo incollato sopra un tramonto
    corpo = Image.merge("RGB", rit.split()[:3])
    corpo = ImageEnhance.Brightness(corpo).enhance(1.10)
    corpo = Image.blend(corpo, Image.new("RGB", corpo.size, (255, 226, 178)), 0.10)
    rit = Image.merge("RGBA", corpo.split() + (rit.split()[3],))

    x_rit = cx - largh_rit // 2
    y_rit = y_fascia - v(330) - rit.height

    al = rit.split()[3]
    al = ImageChops.multiply(al, gradiente_verticale(
        al.size, int(rit.height * 0.79), int(rit.height * 0.995), 255, 0))
    rit.putalpha(al)

    # alone luminoso dietro le spalle: stacca la figura dal panorama
    alone = al.filter(ImageFilter.GaussianBlur(o(105))).point(lambda t: int(t * 0.40))
    tela.paste(Image.new("RGB", rit.size, (255, 238, 205)), (x_rit, y_rit), alone)
    ombra = al.filter(ImageFilter.GaussianBlur(o(38))).point(lambda t: int(t * 0.30))
    tela.paste(Image.new("RGB", rit.size, (86, 56, 30)), (x_rit + o(10), y_rit + v(18)),
               ombra)
    tela.paste(rit, (x_rit, y_rit), rit)
    dr = ImageDraw.Draw(tela)

    return _chiudi(a, tela, dr, W, H, o, v, margine, cx, y_fascia)


def _chiudi(a, tela, dr, W, H, o, v, margine, cx, y_fascia):
    so = W / 3308.0
    # ── 4. intestazione centrata: logo, marchio, riga in corsivo ─────────────
    lato_logo = o(600)
    logo = Image.open(a.logo).convert("RGBA").resize((lato_logo, lato_logo), Image.LANCZOS)
    tela.paste(logo, (cx - lato_logo // 2, v(80)), logo)

    y = v(80) + lato_logo + v(190)
    f_marchio, d_m = adatta("PARTECIPAZIONE ATTIVA", LAPIDARIO, W - 2 * margine,
                            o(196), 0.02)
    scrivi(dr, (cx, y), "PARTECIPAZIONE ATTIVA", f_marchio, BRUNO_SCURO,
           sp=d_m * 0.02, spessore=max(1, o(3)))

    y += v(96)
    f_sub, _ = adatta(a.sottotitolo, "merriweather-400-italic.ttf",
                      W - 2 * margine, o(56))
    dr.text((cx, y), a.sottotitolo, font=f_sub, fill=BRUNO, anchor="ms")

    # ── 5. sopra la fascia: occasione e nome, in chiaro sulla fotografia ─────
    f_nome, d_n = adatta(a.nome, SERIF_TESTO, W - 2 * margine, o(220), 0.01)
    scrivi_su_foto(tela, (cx, y_fascia - v(110)), a.nome, f_nome, CREMA,
                   sp=d_n * 0.01, spessore=max(1, o(2)), raggio=o(34), forza=0.82)
    dr = ImageDraw.Draw(tela)

    # ── 6. dentro la fascia: carica, valori, territori ───────────────────────
    y = y_fascia + v(250)
    f_car, d_c = adatta(a.carica.upper(), LAPIDARIO, W - 2 * margine, o(178), 0.015)
    scrivi(dr, (cx, y), a.carica.upper(), f_car, BRUNO_SCURO, sp=d_c * 0.015,
           spessore=max(1, o(3)))

    y += v(165)
    f_occ, d_o = adatta(a.occasione.upper(), LAPIDARIO, W - 2 * margine, o(88), 0.10)
    scrivi(dr, (cx, y), a.occasione.upper(), f_occ, ORO, sp=d_o * 0.10)

    y += v(140)
    f_val, d_v = adatta(a.valori.upper(), LAPIDARIO, W - 2 * margine, o(84), 0.05)
    scrivi(dr, (cx, y), a.valori.upper(), f_val, BRUNO, sp=d_v * 0.05)

    if a.territori:
        y += v(128)
        f_ter, _ = adatta(a.territori, "merriweather-400-italic.ttf",
                          W - 2 * margine, o(62))
        dr.text((cx, y), a.territori, font=f_ter, fill=BRUNO_TENUE, anchor="ms")

    # ── 7. piede ─────────────────────────────────────────────────────────────
    y_piede = H - v(250)
    dr.rectangle((0, y_piede, W, H), fill=PERGAMENA_OMBRA)
    alt_barra = max(3, o(12))
    barra = Image.new("RGB", (W, alt_barra))
    bd = ImageDraw.Draw(barra)
    for x in range(W):
        t = x / W
        da, aa, u = ((VERDE_PA, AMBRA_CALDA, t / 0.5) if t < 0.5
                     else (AMBRA_CALDA, ROSSO_PA, (t - 0.5) / 0.5))
        bd.line((x, 0, x, alt_barra),
                fill=tuple(int(da[i] + (aa[i] - da[i]) * u) for i in range(3)))
    tela.paste(barra, (0, y_piede))

    yb = y_piede + v(140)
    scrivi(dr, (margine, yb), a.sito, font(LAPIDARIO, o(58)), BRUNO_SCURO,
           sp=5 * so, ancora="ls")
    if a.committente:
        scrivi(dr, (W - margine, yb), "Committente responsabile: " + a.committente,
               font("merriweather-400.ttf", o(36)), BRUNO, sp=so, ancora="rs")

    return grana(tela, forza=3.0 * max(0.55, so))


def adatta_social(master, larg, alt):
    """Formato orizzontale: il manifesto non si ricompone, si appoggia intero."""
    k = larg / master.width
    im = master.resize((larg, int(master.height * k)), Image.LANCZOS)
    tela = Image.new("RGB", (larg, alt), PERGAMENA_OMBRA)
    tela.paste(im, (0, (alt - im.height) // 2))
    return tela


def main():
    p = argparse.ArgumentParser(description="Manifesto elettorale PA, stile classico")
    p.add_argument("--ritratto", default="")
    p.add_argument("--scena-unica", action="store_true", dest="scena_unica",
                   help="lo sfondo contiene gia' la persona: niente montaggio")
    p.add_argument("--sfondo", required=True)
    p.add_argument("--logo", default="LOGO-PA.webp")
    p.add_argument("--nome", required=True)
    p.add_argument("--carica", required=True)
    p.add_argument("--territori", default="")
    p.add_argument("--occasione", default="Elezioni comunali di Napoli · 2027")
    p.add_argument("--sottotitolo",
                   default="Libera associazione di cittadini — fondata sulla "
                           "Costituzione Italiana")
    p.add_argument("--valori",
                   default="Democrazia diretta · Trasparenza · Beni comuni")
    p.add_argument("--sito", default="partecipazione-attiva.it")
    p.add_argument("--committente", default="",
                   help="obbligatorio per l'affissione (L. 212/1956 art. 3)")
    p.add_argument("--zoom", type=float, default=1.22)
    p.add_argument("--fuoco", type=float, default=0.50,
                   help="0 = tiene il cielo, 1 = tiene il primo piano")
    p.add_argument("--luce", type=float, default=1.16,
                   help="quanto si schiarisce il panorama")
    p.add_argument("--larghezza-ritratto", type=float, default=0.48,
                   dest="larghezza_ritratto")
    p.add_argument("--uscita", required=True)
    p.add_argument("--social", action="store_true")
    a = p.parse_args()

    prepara_font()
    master = costruisci(a, W, H)
    master.save(a.uscita, dpi=(120, 120))
    print("manifesto:", a.uscita, master.size)

    if a.social:
        base = os.path.splitext(a.uscita)[0]
        for suff, (lw, lh) in {"_post": (1080, 1350), "_storia": (1080, 1920)}.items():
            costruisci(a, lw, lh).save(base + suff + ".jpg", quality=94)
            print("social:", base + suff + ".jpg", (lw, lh))
        adatta_social(master, 1200, 630).save(base + "_anteprima.jpg", quality=92)

    if not a.committente:
        print("\n⚠️  Manca il committente responsabile: questo file NON e' affiggibile.\n"
              "    Rilanciare con --committente \"Nome Cognome\" prima della stampa.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
