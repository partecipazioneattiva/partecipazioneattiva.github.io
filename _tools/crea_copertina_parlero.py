#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copertina del podcast "Parlero" — 3000x3000 JPG.

Si lancia UNA VOLTA SOLA: la copertina non cambia a ogni puntata.

    python3 _tools/crea_copertina_parlero.py

Perche' 3000x3000 e JPG: Apple Podcasts rifiuta sotto 1400x1400 e vuole
JPG o PNG in RGB (niente WebP, niente CMYK, niente trasparenza). Spotify
legge lo stesso file.

⚠️ Nessun volto sulla copertina, per scelta: l'autorizzazione di Antonio
Cristiano copre la voce, non l'immagine. Copertina tipografica.

I caratteri del sito sono woff2 (fonts/): qui si convertono al volo in
TTF con fontTools, senza scrivere niente su disco.
"""
import io, os, sys

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(BASE, 'fonts')
USCITA = os.path.join(BASE, 'images', 'parlero-podcast-cover.jpg')

LATO = 3000
SCURO = (26, 16, 5)
OCRA = (232, 144, 10)
CREMA = (255, 248, 238)


def carattere(nome, px, peso=None):
    """Un woff2 di fonts/ come font PIL, convertito in memoria.

    ⚠️ I Montserrat e i Merriweather di `fonts/` sono **font variabili**
    (asse wght 100→900) e il file e' lo stesso per tutti i pesi: dentro
    `montserrat-900-latin.woff2` c'e' Montserrat **Thin**, default 100.
    Sul sito va bene — il descrittore font-weight della @font-face fissa
    l'asse — ma PIL, se non glielo si dice, disegna l'istanza di default.
    Il 01/08/2026 la prima copertina e' uscita con un titolo sottilissimo
    per questo. Quindi: `peso` va passato, e si applica sull'asse.
    """
    percorso = os.path.join(FONTS, nome)
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(percorso)
        variabile = 'fvar' in f
        buf = io.BytesIO()
        f.flags = 0
        f.save(buf)
        buf.seek(0)
        font = ImageFont.truetype(buf, px)
        if peso and variabile:
            font.set_variation_by_axes([float(peso)])
        return font
    except Exception as e:
        # Ripiego sui caratteri di sistema: la copertina esce lo stesso,
        # con un disegno leggermente diverso. Meglio di un errore.
        print(f'  (woff2 non convertito: {e} — uso un carattere di sistema)')
        for alt in ('/System/Library/Fonts/Supplemental/Futura.ttc',
                    '/System/Library/Fonts/Helvetica.ttc'):
            if os.path.exists(alt):
                return ImageFont.truetype(alt, px)
        return ImageFont.load_default()


def centra(d, testo, font, y, colore, spaziatura=0):
    """Scrive `testo` centrato in orizzontale. spaziatura = crenatura extra."""
    if spaziatura:
        larghezze = [d.textlength(c, font=font) for c in testo]
        totale = sum(larghezze) + spaziatura * (len(testo) - 1)
        x = (LATO - totale) / 2
        for c, w in zip(testo, larghezze):
            d.text((x, y), c, font=font, fill=colore)
            x += w + spaziatura
        return totale
    w = d.textlength(testo, font=font)
    d.text(((LATO - w) / 2, y), testo, font=font, fill=colore)
    return w


def main():
    img = Image.new('RGB', (LATO, LATO), SCURO)
    d = ImageDraw.Draw(img)

    # Fondo: schiarita calda in alto a sinistra, come un faro di studio.
    for i in range(LATO):
        t = i / LATO
        c = (int(26 + 32 * (1 - t)), int(16 + 20 * (1 - t)), int(5 + 6 * (1 - t)))
        d.line([(0, i), (LATO, i)], fill=c)

    # Banda ocra in alto: e' la firma visiva della pagina Parlero (#e8900a).
    d.rectangle([0, 0, LATO, 34], fill=OCRA)

    f_tit = carattere('montserrat-900-latin.woff2', 560, peso=900)
    f_sub = carattere('merriweather-400-italic-latin.woff2', 122)
    f_occ = carattere('montserrat-900-latin.woff2', 78, peso=700)
    f_pie = carattere('montserrat-600-latin.woff2', 74, peso=600)
    # ⛔ Niente virgolette caporali giganti dietro al titolo: provate due
    # volte il 01/08/2026 e scartate. "PARLERO" a corpo 560 occupa tutta
    # la larghezza, ai lati non resta spazio, e le caporali schiacciate
    # contro i bordi si leggono come galloni militari. La composizione
    # regge da sola: titolo, filetto, sottotitolo.

    # Occhiello
    centra(d, 'PARTECIPAZIONE ATTIVA WEBTV', f_occ, 1060, (176, 132, 70),
           spaziatura=12)

    centra(d, 'PARLERÒ', f_tit, 1220, CREMA, spaziatura=-14)

    # Filetto ocra sotto il titolo
    d.rectangle([(LATO - 760) / 2, 1930, (LATO + 760) / 2, 1946], fill=OCRA)

    centra(d, 'il commento di Antonio Cristiano', f_sub, 2050, (232, 214, 188))
    centra(d, 'Napoli, e quello che da Napoli si vede', f_sub, 2200, (156, 134, 106))

    centra(d, 'NUOVA PUNTATA OGNI SETTIMANA', f_pie, 2680, OCRA, spaziatura=12)

    img.save(USCITA, 'JPEG', quality=90, optimize=True, subsampling=0)
    kb = os.path.getsize(USCITA) // 1024
    print(f'✅ {USCITA}  {LATO}x{LATO}  {kb} KB')


if __name__ == '__main__':
    sys.exit(main())
