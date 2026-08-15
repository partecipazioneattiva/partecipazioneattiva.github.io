#!/usr/bin/env python3
"""Manifesto elettorale DA STRADA: alto contrasto, volto grande, slogan.

Nasce il 12 agosto 2026 perche' il modello «classico» (`manifesto_classico.py
--laterale`) e' elegante, e sul muro l'eleganza non si vede. Giudizio di
Fernando sul primo montaggio: «sembra il santino di un morto».

Le regole applicate qui vengono dalla ricerca del 12 agosto (fonti nella
specifica, 00_SPEC/specifica_accettazione.md sezione C-bis):

  · mezzo busto o primo piano, MAI figura intera;
  · il volto e' l'elemento dominante;
  · sguardo frontale, sorriso leggero;
  · colori accesi ad alto contrasto col grigio della citta';
  · gerarchia: volto > nome > carica > slogan;
  · slogan di 3-7 parole, concreto;
  · niente recapiti;
  · prova dei 30 metri: si deve capire CHI SEI e COSA FAI.

    python3 _tools/manifesto_strada.py \
        --ritratto volto_scontornato.png \
        --nome ANTONIO --cognome CRISTIANO \
        --carica "CANDIDATO PRESIDENTE" \
        --luogo "MUNICIPALITA' 10" \
        --territori "Bagnoli · Fuorigrotta · Agnano · Cavalleggeri d'Aosta" \
        --slogan "IL QUARTIERE DECIDE" \
        --voto "BARRA IL SIMBOLO" \
        --elezione "COMUNALI DI NAPOLI · PRIMAVERA 2027" \
        --committente "Mario Rossi" \
        --uscita manifesto.png

⛔ Il ritratto deve essere gia' SCONTORNATO (PNG con trasparenza).
⛔ Il committente responsabile e' obbligatorio per l'affissione (L. 212/1956 art. 3).
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

CAR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caratteri')
NERO = (26, 15, 4)
ARANCIO = (232, 144, 10)
ORO = (255, 213, 128)
BIANCO = (255, 255, 255)
BRUNO = (92, 50, 0)

W, H = 3308, 4724                      # 70x100 cm a 120 dpi


def f(nome, misura):
    return ImageFont.truetype(os.path.join(CAR, nome), int(misura))


def largo(d, testo, font, sp=0):
    if not sp:
        return d.textlength(testo, font=font)
    return sum(d.textlength(c, font=font) + sp for c in testo) - sp


def adatta(d, testo, nome_font, larghezza, dim_max, sp=0.0):
    """Il carattere piu' grande che ci sta nella larghezza data."""
    dim = dim_max
    while dim > 20:
        fnt = f(nome_font, dim)
        if largo(d, testo, fnt, sp * dim) <= larghezza:
            return fnt, dim
        dim -= 6
    return f(nome_font, 20), 20


def scrivi(d, xy, testo, font, colore, sp=0.0, ancora='la'):
    if not sp:
        d.text(xy, testo, font=font, fill=colore, anchor=ancora)
        return
    x, y = xy
    tot = largo(d, testo, font, sp)
    if ancora[0] == 'm':
        x -= tot / 2
    elif ancora[0] == 'r':
        x -= tot
    for c in testo:
        d.text((x, y), c, font=font, fill=colore, anchor='l' + ancora[1])
        x += d.textlength(c, font=font) + sp


def costruisci(a):
    im = Image.new('RGB', (W, H), NERO)
    d = ImageDraw.Draw(im)
    M = int(W * 0.055)
    utile = W - 2 * M

    # ── fondo: bagliore caldo dietro la testa, cosi' il volto stacca ─────────
    bagl = Image.new('L', (W, H), 0)
    ImageDraw.Draw(bagl).ellipse((int(W * 0.02), int(-H * 0.06),
                                  int(W * 0.98), int(H * 0.62)), fill=255)
    bagl = bagl.filter(ImageFilter.GaussianBlur(int(W * 0.10)))
    im = Image.composite(Image.new('RGB', (W, H), (120, 62, 4)), im, bagl)
    d = ImageDraw.Draw(im)

    # ── 1. fascia alta: elezione e data, arancione pieno ─────────────────────
    h_top = int(H * 0.062)
    d.rectangle((0, 0, W, h_top), fill=ARANCIO)
    fnt, dim = adatta(d, a.elezione.upper(), 'montserrat-900-latin.ttf',
                      utile - int(h_top * 1.25), int(h_top * 0.46), sp=0.05)
    scrivi(d, (W - M, h_top / 2), a.elezione.upper(), fnt, NERO, sp=dim * 0.05, ancora='rm')
    if a.logo and os.path.exists(a.logo):
        lato = int(h_top * 0.86)
        logo = Image.open(a.logo).convert('RGBA').resize((lato, lato), Image.LANCZOS)
        im.paste(logo, (M, int((h_top - lato) / 2)), logo)

    # ── 2. il volto, grande: e' l'elemento dominante ─────────────────────────
    y_banda = int(H * 0.585)                     # dove comincia il blocco testo
    rit = Image.open(a.ritratto).convert('RGBA')
    rit = rit.crop(rit.split()[3].point(lambda t: 255 if t > 12 else 0).getbbox())
    alt_rit = int((y_banda - h_top) * 1.16)      # sborda un po' sotto la banda
    rit = rit.resize((int(rit.width * alt_rit / rit.height), alt_rit), Image.LANCZOS)
    if rit.width > int(W * 0.92):
        k = int(W * 0.92) / rit.width
        rit = rit.resize((int(rit.width * k), int(rit.height * k)), Image.LANCZOS)
    rit = rit.filter(ImageFilter.UnsharpMask(radius=3, percent=70, threshold=3))
    x_rit = int((W - rit.width) / 2)
    y_rit = h_top + int((y_banda - h_top) - rit.height * 0.86)

    al = rit.split()[3]
    ombra = al.filter(ImageFilter.GaussianBlur(int(W * 0.012))).point(lambda t: int(t * 0.55))
    im.paste(Image.new('RGB', rit.size, (12, 6, 0)), (x_rit + int(W * 0.006),
                                                      y_rit + int(H * 0.006)), ombra)
    im.paste(rit, (x_rit, y_rit), rit)
    d = ImageDraw.Draw(im)

    # ── 3. blocco basso: nome, carica, slogan, voto ──────────────────────────
    #    Si MISURA prima e si disegna dopo: al primo giro (12 agosto) lo slogan
    #    finiva tagliato e la pillola del voto usciva dal foglio.
    d.rectangle((0, y_banda, W, H), fill=NERO)
    disponibile = (H - int(H * 0.062)) - y_banda - int(H * 0.030)

    def blocco(s):
        """Restituisce (altezza_totale, disegna) alla scala s."""
        voci = []
        alt = 0
        def agg(testo, font_nome, frazione, colore, sp=0.0, dopo=1.15, ancora='ma'):
            nonlocal alt
            fnt, dim = adatta(d, testo, font_nome, utile, int(H * frazione * s), sp=sp)
            voci.append((testo, fnt, dim, colore, sp, ancora))
            alt += int(dim * dopo)
            return dim
        agg(a.nome.upper(), 'montserrat-900-latin.ttf', 0.072, BIANCO, dopo=1.02)
        agg(a.cognome.upper(), 'montserrat-900-latin.ttf', 0.100, ARANCIO, dopo=1.30)
        carica = f'{a.carica.upper()} · {a.luogo.upper()}' if a.luogo else a.carica.upper()
        agg(carica, 'montserrat-700-latin.ttf', 0.029, ORO, sp=0.03, dopo=1.95)
        if a.territori:
            agg(a.territori, 'merriweather-700-latin.ttf', 0.021, (196, 178, 152), dopo=2.15)
        agg(a.slogan.upper(), 'montserrat-900-latin.ttf', 0.058, BIANCO, dopo=1.55)

        fnt_v, dim_v = adatta(d, a.voto.upper(), 'montserrat-900-latin.ttf',
                              int(utile * 0.80), int(H * 0.035 * s), sp=0.04)
        h_pill = dim_v * 2.1
        alt += int(h_pill)
        dim_v2 = 0
        fnt_v2 = None
        if a.voto2:
            fnt_v2, dim_v2 = adatta(d, a.voto2, 'merriweather-700-latin.ttf',
                                    utile, int(H * 0.020 * s))
            alt += int(h_pill * 0.35 + dim_v2)

        def disegna(y):
            for testo, fnt, dim, colore, sp, ancora in voci:
                scrivi(d, (W / 2, y), testo, fnt, colore, sp=dim * sp, ancora=ancora)
                y += int(dim * (1.02 if testo == a.nome.upper() else
                                1.30 if testo == a.cognome.upper() else
                                1.95 if colore == ORO else
                                2.15 if colore == (196, 178, 152) else 1.55))
            lp = largo(d, a.voto.upper(), fnt_v, dim_v * 0.04) + dim_v * 1.9
            xp = (W - lp) / 2
            d.rounded_rectangle((xp, y, xp + lp, y + h_pill), h_pill / 2, fill=BIANCO)
            scrivi(d, (W / 2, y + h_pill / 2), a.voto.upper(), fnt_v, NERO,
                   sp=dim_v * 0.04, ancora='mm')
            if fnt_v2:
                y += int(h_pill * 1.35)
                scrivi(d, (W / 2, y), a.voto2, fnt_v2, (196, 178, 152), ancora='ma')
        return alt, disegna

    s = 1.0
    while s > 0.4:
        alt, disegna = blocco(s)
        if alt <= disponibile:
            break
        s -= 0.04
    disegna(y_banda + int((disponibile - alt) * 0.42) + int(H * 0.018))

    # ── 4. piede: tricolore, sito, committente ───────────────────────────────
    hp = int(H * 0.007)
    y0 = H - int(H * 0.052)
    for i, c in enumerate([(0, 140, 69), (255, 255, 255), (205, 33, 42)]):
        d.rectangle((i * W / 3, y0, (i + 1) * W / 3, y0 + hp), fill=c)
    fnt = f('montserrat-700-latin.ttf', int(H * 0.017))
    d.text((M, y0 + hp + int(H * 0.011)), a.sito, font=fnt, fill=ORO)
    fnt = f('montserrat-400-latin.ttf', int(H * 0.0125))
    d.text((W - M, y0 + hp + int(H * 0.013)),
           f'Committente responsabile: {a.committente}', font=fnt,
           fill=(150, 135, 118), anchor='ra')
    return im


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--ritratto', required=True, help='PNG gia\' scontornato')
    p.add_argument('--nome', required=True)
    p.add_argument('--cognome', required=True)
    p.add_argument('--carica', required=True)
    p.add_argument('--luogo', default='')
    p.add_argument('--territori', default='')
    p.add_argument('--slogan', required=True, help='3-7 parole')
    p.add_argument('--voto', required=True)
    p.add_argument('--voto2', default='')
    p.add_argument('--elezione', required=True)
    p.add_argument('--sito', default='partecipazione-attiva.it')
    p.add_argument('--committente', required=True,
                   help='obbligatorio per l\'affissione (L. 212/1956 art. 3)')
    p.add_argument('--logo', default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'LOGO-PA.webp'))
    p.add_argument('--uscita', required=True)
    a = p.parse_args()

    n = len(a.slogan.split())
    if not 3 <= n <= 7:
        print(f'⚠️  lo slogan ha {n} parole: la regola dice 3-7')

    im = costruisci(a)
    im.save(a.uscita)
    ant = a.uscita.replace('.png', '_anteprima.png')
    im.resize((im.width // 4, im.height // 4), Image.LANCZOS).save(ant)
    print(f'  ✅ {a.uscita}  {im.size}  (70x100 cm a 120 dpi)')
    print(f'  👁  {ant}')
