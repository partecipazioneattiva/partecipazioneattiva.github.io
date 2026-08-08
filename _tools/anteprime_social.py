#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE ANTEPRIME QUANDO SI CONDIVIDE UN LINK
========================================
Genera per ogni pagina l'immagine 1200x630 che Facebook, WhatsApp, Telegram e
gli altri mostrano quando qualcuno condivide il collegamento.

PERCHE' CONTA PIU' DELLA SEO, PER QUESTO SITO
MISURATO su Search Console l'8 agosto 2026: da Google arrivano 154 clic in
dodici mesi, 1,7 al giorno. La gente arriva da Facebook e WhatsApp. Quindi la
vera "vetrina" del sito non e' la pagina dei risultati di Google: e' la scheda
che compare quando un iscritto incolla il link in un gruppo.

IL DIFETTO TROVATO: 35 pagine su 64 avevano un'immagine di anteprima piu'
piccola del minimo. Molte usavano il logo a 400x400.
La documentazione di Facebook e' esplicita: **sotto i 600x315 non mostra la
scheda grande, mostra un francobollo** accanto a due righe di testo. La misura
consigliata e' 1200x630 (rapporto 1,91:1), quella che funziona su tutte le
piattaforme.

COSA GENERA: una scheda con la grafica del movimento — sfondo arancione, logo
tondo, il titolo della pagina nel carattere del sito, il nome del movimento in
basso. Un file per pagina, in images/anteprime/.

    python3 _tools/anteprime_social.py            # prova a vuoto
    python3 _tools/anteprime_social.py --applica
"""
import os, re, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv
DEST = os.path.join(REPO, "images", "anteprime")
# i caratteri del sito, convertiti da woff2 a ttf una volta sola per poterli
# disegnare dentro le immagini (i woff2 il generatore non li sa leggere)
CARATTERI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caratteri")

L, H = 1200, 630
MIN_OK = (600, 315)          # sotto questa misura Facebook fa il francobollo


def font(nome, dim):
    p = os.path.join(CARATTERI, nome + ".ttf")
    if os.path.exists(p):
        return ImageFont.truetype(p, dim)
    for alt in ("/System/Library/Fonts/Supplemental/Georgia.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if os.path.exists(alt):
            return ImageFont.truetype(alt, dim)
    return ImageFont.load_default()


def titolo_di(f):
    """Il titolo per l'anteprima. IN QUEST'ORDINE, e c'e' un motivo:
       1. og:title  — e' proprio il titolo pensato per la condivisione
       2. <title>   — il titolo della pagina
       3. <h1>      — solo se mancano gli altri
    Provato l'8 agosto 2026: rcauto.html riusa l'intestazione della pagina
    Battaglie, quindi il suo primo <h1> dice «Le Nostre Battaglie». Partendo
    dall'h1 l'anteprima dell'RC Auto sarebbe uscita col titolo sbagliato."""
    d = open(os.path.join(REPO, f), encoding="utf-8").read()
    m = re.search(r'<meta[^>]*property=["\']?og:title["\']?[^>]*content=["\']([^"\']+)', d)
    if not m:
        m = re.search(r"<title>(.*?)</title>", d, re.S)
    if not m:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", d, re.S)
    t = re.sub(r"<[^>]+>", "", m.group(1)) if m else f
    t = (t.replace("&mdash;", "—").replace("&rsquo;", "’").replace("&nbsp;", " ")
          .replace("&egrave;", "è").replace("&agrave;", "à").replace("&eacute;", "é")
          .replace("&ograve;", "ò").replace("&ugrave;", "ù").replace("&#8217;", "’")
          .replace("&amp;", "&"))
    # via il nome del movimento in coda: nell'anteprima c'e' gia', sopra e sotto.
    # Vale sia con la barra sia col trattino: «Le Nostre Battaglie - Partecipazione
    # Attiva» sprecava due righe su tre per ripetere il nome.
    t = re.sub(r"\s*[|\u2013\u2014-]\s*(PA|Partecipazione Attiva)\b.*$", "", t).strip()
    return re.sub(r"\s+", " ", t)


def serve_anteprima(f, d):
    """Vero se questa pagina ha un'anteprima assente o troppo piccola."""
    m = re.search(r'<meta[^>]*property=["\']?og:image["\']?[^>]*content=["\']([^"\']*)', d)
    if not m:
        return True, "manca"
    loc = m.group(1).split("/")[-1]
    # cerco il file OVUNQUE nel sito: la prima versione guardava solo in
    # images/ e dava "non trovato" a immagini che stavano in
    # images/organigramma/. Errore mio, trovato l'8 agosto 2026.
    trovato = None
    for radice, _, files in os.walk(os.path.join(REPO, "images")):
        if loc in files:
            trovato = os.path.join(radice, loc); break
    if trovato is None and os.path.exists(os.path.join(REPO, loc)):
        trovato = os.path.join(REPO, loc)
    for p in ([trovato] if trovato else []):
        if os.path.exists(p):
            try:
                w, h = Image.open(p).size
            except Exception:
                return True, "illeggibile"
            if w < MIN_OK[0] or h < MIN_OK[1]:
                return True, f"{w}x{h} troppo piccola"
            return False, f"{w}x{h} ok"
    return True, "file non trovato"


def disegna(titolo, dove):
    im = Image.new("RGB", (L, H), "#8a4e00")
    dr = ImageDraw.Draw(im)
    # sfumatura come quella del sito
    for y in range(H):
        k = y / H
        dr.line([(0, y), (L, y)],
                fill=(int(0x8a + (0xe8 - 0x8a) * k),
                      int(0x4e + (0x90 - 0x4e) * k),
                      int(0x00 + (0x0a - 0x00) * k)))
    # logo tondo
    logo_p = os.path.join(REPO, "LOGO-PA.webp")
    if os.path.exists(logo_p):
        lg = Image.open(logo_p).convert("RGBA").resize((150, 150), Image.LANCZOS)
        mask = Image.new("L", (150, 150), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 149, 149), fill=255)
        im.paste(lg, (72, 62), mask)

    # una velatura scura in basso: senza, il dominio si perdeva nell'arancione
    velo = Image.new("RGBA", (L, 210), (0, 0, 0, 0))
    dv = ImageDraw.Draw(velo)
    for y in range(210):
        dv.line([(0, y), (L, y)], fill=(60, 30, 0, int(150 * (y / 210) ** 1.4)))
    im.paste(velo, (0, H - 210), velo)

    # occhiello — bianco pieno, si legge
    f_occ = font("montserrat-700-latin", 24)
    dr.text((248, 102), "MOVIMENTO POPOLARE DEI CITTADINI ITALIANI",
            font=f_occ, fill="white")

    # titolo, centrato in verticale nello spazio che resta
    dim = 62 if len(titolo) < 58 else (52 if len(titolo) < 92 else 44)
    f_tit = font("merriweather-700-latin", dim)
    righe = textwrap.wrap(titolo, width=int(1150 / (dim * 0.52)))[:4]
    passo = int(dim * 1.26)
    alto, basso = 250, H - 130
    y = alto + max(0, ((basso - alto) - passo * len(righe)) // 2)
    for r in righe:
        dr.text((74, y + 2), r, font=f_tit, fill=(90, 45, 0))     # ombra leggera
        dr.text((72, y), r, font=f_tit, fill="white")
        y += passo

    # firma in basso, sopra la velatura
    f_pie = font("montserrat-900-latin", 29)
    dr.text((72, H - 80), "partecipazione-attiva.it", font=f_pie, fill="white")
    dr.rectangle([(0, H - 14), (L, H)], fill="#ffd580")

    im.save(dove, quality=88, optimize=True)
    return os.path.getsize(dove) // 1024


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    if APPLICA:
        os.makedirs(DEST, exist_ok=True)
    fatte = gia = 0
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        if f.startswith("google") or f == "template.html":
            continue
        d = open(os.path.join(REPO, f), encoding="utf-8").read()
        if "<nav" not in d and "og:" not in d:
            continue
        serve, perche = serve_anteprima(f, d)
        if not serve:
            gia += 1
            continue
        t = titolo_di(f)
        nome = f.replace(".html", "") + "-anteprima.jpg"
        fatte += 1
        kb = ""
        if APPLICA:
            kb = f"  {disegna(t, os.path.join(DEST, nome))} KB"
            # aggancio l'anteprima nella pagina
            url = "https://partecipazione-attiva.it/images/anteprime/" + nome
            if re.search(r'property=["\']?og:image["\']?', d):
                d = re.sub(r'(<meta[^>]*property=["\']?og:image["\']?[^>]*content=["\'])[^"\']*',
                           lambda m: m.group(1) + url, d, count=1)
            else:
                d = d.replace("</title>", f'</title><meta property="og:image" content="{url}">', 1)
            # e la misura, che aiuta le anteprime a comparire subito
            if "og:image:width" not in d:
                d = d.replace(f'content="{url}">',
                              f'content="{url}"><meta property="og:image:width" content="1200">'
                              f'<meta property="og:image:height" content="630">', 1)
            if "twitter:card" not in d:
                d = d.replace("</title>", '</title><meta name="twitter:card" content="summary_large_image">', 1)
            open(os.path.join(REPO, f), "w", encoding="utf-8").write(d)
        print(f"  🖼  {f[:40]:40} [{perche[:18]:18}] {t[:44]}{kb}")
    print(f"\n  {fatte} anteprime da generare · {gia} pagine gia' a posto")
    if not APPLICA:
        print("  (rilancia con --applica per generarle)")


if __name__ == "__main__":
    main()
