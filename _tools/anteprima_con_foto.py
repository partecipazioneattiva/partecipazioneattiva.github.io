#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L'ANTEPRIMA DI CONDIVISIONE CON LA FACCIA DI CHI FIRMA
======================================================
Genera la scheda 1200x630 che Facebook e WhatsApp mostrano quando qualcuno
incolla il link, mettendoci dentro la FOTOGRAFIA della persona che firma la
pagina, e la aggancia ai tre posti che contano: og:image, twitter:image e il
campo "image" del dato strutturato JSON-LD.

⭐ PERCHE' ESISTE, ACCANTO A anteprime_social.py (10 agosto 2026)
anteprime_social.py disegna una scheda di solo testo su fondo arancione: va
benissimo per una pagina di sezione, ma non per un articolo che UNA PERSONA
porta all'attenzione. Il 10 agosto la pagina delle riflessioni della prof.ssa
Trucco, firmata dal portavoce Luigi Spanu, mostrava su Facebook l'immagine del
PensAttivo: l'aveva ereditata dal tema Stabilicum. La faccia di chi firma e' il
motivo per cui un iscritto si ferma a leggere in un gruppo: va nella scheda.

⛔ IL RITAGLIO SI GUARDA, NON SI INDOVINA. Le foto dei dirigenti in images/
spesso NON sono fotografie nude: sono manifesti verticali gia' composti, con il
nome stampato sotto e l'intestazione sopra. Ritagliando a occhio ci finisce
mezza scritta. Si passa --ritaglio con le coordinate misurate sull'originale
(sinistra,alto,destra,basso) e si guarda il file prodotto prima di applicarlo.

    python3 _tools/anteprima_con_foto.py \
        --pagina stabilicum-intelligibilita-trucco-agosto2026.html \
        --foto images/spanu-audizione-stabilicum.webp \
        --ritaglio 172,200,727,960 \
        --occhiello "LUIGI SPANU PORTA ALL'ATTENZIONE" \
        --titolo "Si puo' votare una legge che non si riesce a capire?" \
        --sottotitolo "Le riflessioni della prof.ssa Lara Trucco sullo Stabilicum"
        # e --applica per scrivere davvero

Senza --titolo prende l'og:title della pagina.
"""
import argparse
import os
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARATTERI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caratteri")
DEST = os.path.join(REPO, "images", "anteprime")

L, H = 1200, 630
FOTO_L = 470                 # la colonna della fotografia, a destra
SFUMA = 150                  # quanto la foto sfuma dentro il fondo, a sinistra


def font(nome, dim):
    p = os.path.join(CARATTERI, nome + ".ttf")
    if os.path.exists(p):
        return ImageFont.truetype(p, dim)
    return ImageFont.load_default()


def titolo_della_pagina(html):
    m = re.search(r'<meta[^>]*property=["\']?og:title["\']?[^>]*content=["\']([^"\']+)', html)
    if not m:
        m = re.search(r"<title>(.*?)</title>", html, re.S)
    t = re.sub(r"<[^>]+>", "", m.group(1)) if m else ""
    for a, b in (("&mdash;", "—"), ("&rsquo;", "’"), ("&nbsp;", " "), ("&egrave;", "è"),
                 ("&agrave;", "à"), ("&eacute;", "é"), ("&ograve;", "ò"), ("&ugrave;", "ù"),
                 ("&#8217;", "’"), ("&amp;", "&"), ("&laquo;", "«"), ("&raquo;", "»")):
        t = t.replace(a, b)
    t = re.sub(r"\s*[|–—-]\s*(PA|Partecipazione Attiva)\b.*$", "", t)
    return re.sub(r"\s+", " ", t).strip()


def disegna(foto, ritaglio, occhiello, titolo, sottotitolo, dove):
    im = Image.new("RGB", (L, H), "#8a4e00")
    dr = ImageDraw.Draw(im)
    # la sfumatura del sito, la stessa di anteprime_social.py
    for y in range(H):
        k = y / H
        dr.line([(0, y), (L, y)],
                fill=(int(0x8a + (0xe8 - 0x8a) * k),
                      int(0x4e + (0x90 - 0x4e) * k),
                      int(0x00 + (0x0a - 0x00) * k)))

    # ---- la fotografia, colonna di destra, sfumata a sinistra
    ph = Image.open(os.path.join(REPO, foto)).convert("RGB")
    if ritaglio:
        ph = ph.crop(ritaglio)
    # riempio la colonna senza deformare: scalo sul lato piu' stretto e taglio
    k = max(FOTO_L / ph.width, H / ph.height)
    ph = ph.resize((max(1, round(ph.width * k)), max(1, round(ph.height * k))), Image.LANCZOS)
    sx = (ph.width - FOTO_L) // 2
    sy = (ph.height - H) // 2
    ph = ph.crop((sx, sy, sx + FOTO_L, sy + H))
    maschera = Image.new("L", (FOTO_L, H), 255)
    dm = ImageDraw.Draw(maschera)
    for x in range(SFUMA):                      # bordo sinistro che si dissolve
        dm.line([(x, 0), (x, H)], fill=int(255 * (x / SFUMA) ** 1.5))
    im.paste(ph, (L - FOTO_L, 0), maschera)

    # ---- logo tondo in alto a sinistra
    logo_p = os.path.join(REPO, "LOGO-PA.webp")
    if os.path.exists(logo_p):
        lg = Image.open(logo_p).convert("RGBA").resize((120, 120), Image.LANCZOS)
        mk = Image.new("L", (120, 120), 0)
        ImageDraw.Draw(mk).ellipse((0, 0, 119, 119), fill=255)
        im.paste(lg, (66, 54), mk)
    dr.text((202, 76), "PARTECIPAZIONE ATTIVA", font=font("montserrat-900-latin", 27), fill="white")
    dr.text((202, 112), "MOVIMENTO POPOLARE DEI CITTADINI ITALIANI",
            font=font("montserrat-400-latin", 17), fill=(255, 228, 190))

    testo_l = L - FOTO_L - 20                   # la colonna del testo, a sinistra
    y = 228

    if occhiello:
        # ⛔ l'oro chiaro sull'arancione non ha contrasto: l'occhiello e il
        #    sottotitolo si scrivono bianchi, con un'ombra sotto. Misurato il
        #    10/08/2026 sulla prima prova, dove sparivano nel fondo.
        f_occ = font("montserrat-700-latin", 20)
        dr.text((73, y + 2), occhiello, font=f_occ, fill=(96, 46, 0))
        dr.text((72, y), occhiello, font=f_occ, fill="white")
        dr.line([(72, y + 32), (72 + 90, y + 32)], fill=(255, 214, 140), width=3)
        y += 56

    dim = 44 if len(titolo) < 70 else (38 if len(titolo) < 100 else 33)
    f_tit = font("merriweather-700-latin", dim)
    righe = textwrap.wrap(titolo, width=int((testo_l - 72) / (dim * 0.50)))[:5]
    passo = int(dim * 1.30)
    for r in righe:
        dr.text((74, y + 2), r, font=f_tit, fill=(88, 42, 0))
        dr.text((72, y), r, font=f_tit, fill="white")
        y += passo

    if sottotitolo:
        y += 12
        f_sub = font("montserrat-400-latin", 21)
        for r in textwrap.wrap(sottotitolo, width=int((testo_l - 72) / (21 * 0.55)))[:3]:
            dr.text((73, y + 2), r, font=f_sub, fill=(96, 46, 0))
            dr.text((72, y), r, font=f_sub, fill="white")
            y += 29

    dr.text((72, H - 78), "partecipazione-attiva.it",
            font=font("montserrat-900-latin", 27), fill="white")
    dr.rectangle([(0, H - 14), (L, H)], fill="#ffd580")

    os.makedirs(os.path.dirname(dove), exist_ok=True)
    im.save(dove, quality=88, optimize=True)
    return os.path.getsize(dove) // 1024


def aggancia(pagina, url):
    """og:image, twitter:image e il campo image del JSON-LD: tutti e tre.
    Facebook legge og:image, ma il JSON-LD lasciato indietro rimette in giro
    l'immagine vecchia attraverso Google e l'anteprima della ricerca."""
    p = os.path.join(REPO, pagina)
    d = open(p, encoding="utf-8").read()
    prima = d
    d = re.sub(r'(property=["\']?og:image["\']?[^>]*content=["\'])[^"\']*',
               lambda m: m.group(1) + url, d)
    d = re.sub(r'(name=["\']?twitter:image["\']?[^>]*content=["\'])[^"\']*',
               lambda m: m.group(1) + url, d)
    d = re.sub(r'("image"\s*:\s*")[^"]*', lambda m: m.group(1) + url, d)
    if d != prima:
        open(p, "w", encoding="utf-8").write(d)
    return d != prima


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pagina", required=True)
    ap.add_argument("--foto", required=True)
    ap.add_argument("--ritaglio", default="", help="sinistra,alto,destra,basso sull'originale")
    ap.add_argument("--occhiello", default="")
    ap.add_argument("--titolo", default="")
    ap.add_argument("--sottotitolo", default="")
    ap.add_argument("--applica", action="store_true")
    a = ap.parse_args()

    html = open(os.path.join(REPO, a.pagina), encoding="utf-8").read()
    titolo = a.titolo or titolo_della_pagina(html)
    ritaglio = tuple(int(x) for x in a.ritaglio.split(",")) if a.ritaglio else None

    nome = a.pagina.replace(".html", "") + "-anteprima.jpg"
    dove = os.path.join(DEST if a.applica else os.environ.get("TMPDIR", "/tmp"), nome)
    kb = disegna(a.foto, ritaglio, a.occhiello, titolo, a.sottotitolo, dove)

    print(f"  🖼  {dove}  ({kb} KB)")
    if a.applica:
        url = "https://partecipazione-attiva.it/images/anteprime/" + nome
        print("  🔗 agganciata alla pagina" if aggancia(a.pagina, url)
              else "  ⚠️  nessun campo immagine trovato nella pagina")
    else:
        print("  (prova a vuoto: guarda il file, poi rilancia con --applica)")


if __name__ == "__main__":
    main()
