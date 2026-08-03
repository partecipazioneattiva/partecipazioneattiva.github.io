#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Card social con il QR — l'immagine che gli iscritti scaricano e pubblicano.

Un QR nudo dentro un feed non funziona: nessuno sa cos'e' e nessuno lo
inquadra. Serve un'immagine che si capisca in un secondo mentre si scorre —
logo, una frase, il codice, l'indirizzo — e che sia gia' nel formato giusto
per il posto dove va.

    python3 _tools/crea_card_qr.py                    # post 1:1 e storia 9:16
    python3 _tools/crea_card_qr.py --dove mappa
    python3 _tools/crea_card_qr.py --titolo "..." --sotto "..."

I caratteri sono quelli del sito (cache ~/.cache/pa_fonts_ttf, preparata da
manifesto_classico.py): cosi' le card e le pagine parlano con la stessa voce.
"""

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crea_qr import DESTINAZIONI, crea as crea_qr           # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FONT = os.path.expanduser("~/.cache/pa_fonts_ttf")

BLU    = (13, 27, 75)
AMBRA  = (232, 144, 10)
BIANCO = (255, 255, 255)
CHIARO = (222, 228, 240)

TESTI = {
    "iscriviti": ("Iscriviti a Partecipazione Attiva",
                  "Il primo anno è gratuito. Inquadra il codice."),
    "mappa":     ("Mettiti sulla Mappa",
                  "I cittadini attivi esistono. Inquadra e fatti vedere."),
    "azioni":    ("Le azioni di Partecipazione Attiva",
                  "Guarda cosa stiamo facendo. Inquadra il codice."),
    "documenti": ("I documenti di Partecipazione Attiva",
                  "Statuto, regolamenti, proposte. Inquadra il codice."),
    "sito":      ("Partecipazione Attiva",
                  "Una libera associazione di cittadini. Inquadra il codice."),
}


def font(nome, dim):
    p = os.path.join(CACHE_FONT, nome)
    if not os.path.exists(p):                     # la cache la prepara il manifesto
        from manifesto_classico import prepara_font
        prepara_font()
    return ImageFont.truetype(p, int(dim))


def a_capo(dr, testo, fnt, larg):
    righe, cur = [], ""
    for parola in testo.split():
        prova = (cur + " " + parola).strip()
        if dr.textlength(prova, font=fnt) <= larg:
            cur = prova
        else:
            righe.append(cur)
            cur = parola
    if cur:
        righe.append(cur)
    return righe


def card(W, H, qr_png, titolo, sotto, sito="partecipazione-attiva.it"):
    tela = Image.new("RGB", (W, H), BLU)
    dr = ImageDraw.Draw(tela)
    k = W / 1080.0
    m = int(80 * k)

    # banda ambra in alto: si riconosce nel feed prima ancora di leggere
    dr.rectangle((0, 0, W, int(18 * k)), fill=AMBRA)

    y = int(70 * k)
    logo = Image.open(os.path.join(REPO, "LOGO-PA.webp")).convert("RGBA")
    lato = int(150 * k)
    logo = logo.resize((lato, lato), Image.LANCZOS)
    tela.paste(logo, (m, y), logo)

    f_marchio = font("montserrat-700.ttf", 40 * k)
    dr.text((m + lato + int(28 * k), y + lato // 2), "PARTECIPAZIONE ATTIVA",
            font=f_marchio, fill=BIANCO, anchor="lm")

    y += lato + int(70 * k)
    f_tit = font("montserrat-700.ttf", 78 * k)
    righe = a_capo(dr, titolo, f_tit, W - 2 * m)
    if len(righe) > 2:                                  # titolo lungo: si rimpicciolisce
        f_tit = font("montserrat-700.ttf", 62 * k)
        righe = a_capo(dr, titolo, f_tit, W - 2 * m)
    for r in righe:
        dr.text((m, y), r, font=f_tit, fill=BIANCO)
        y += int(f_tit.size * 1.18)

    y += int(18 * k)
    f_sot = font("merriweather-400.ttf", 36 * k)
    for r in a_capo(dr, sotto, f_sot, W - 2 * m):
        dr.text((m, y), r, font=f_sot, fill=CHIARO)
        y += int(f_sot.size * 1.45)

    # il QR: su fondo bianco pieno, grande. Sotto, l'indirizzo per chi non inquadra
    f_sito = font("montserrat-700.ttf", 34 * k)
    alt_sito = int(f_sito.size * 1.6)
    spazio = H - y - int(70 * k) - alt_sito
    # nelle storie c'e' molta altezza: il codice cresce invece di lasciare vuoto
    tetto = int((760 if H > W * 1.4 else 620) * k)
    lato_qr = max(int(320 * k), min(tetto, spazio - int(60 * k)))

    qr = Image.open(qr_png).convert("RGB").resize((lato_qr, lato_qr), Image.LANCZOS)
    pad = int(26 * k)
    box = Image.new("RGB", (lato_qr + 2 * pad, lato_qr + 2 * pad), BIANCO)
    box.paste(qr, (pad, pad))
    bx = (W - box.width) // 2
    by = y + max(int(30 * k), (spazio - box.height) // 2)
    tela.paste(box, (bx, by))

    dr.text((W // 2, by + box.height + int(46 * k)), sito, font=f_sito,
            fill=AMBRA, anchor="ma")
    return tela


def main():
    p = argparse.ArgumentParser(description="Card social con QR")
    p.add_argument("--dove", choices=sorted(DESTINAZIONI), default="iscriviti")
    p.add_argument("--titolo", default="")
    p.add_argument("--sotto", default="")
    p.add_argument("--cartella", default=".")
    p.add_argument("--prefisso", default="")
    a = p.parse_args()

    titolo = a.titolo or TESTI[a.dove][0]
    sotto = a.sotto or TESTI[a.dove][1]
    cart = os.path.expanduser(a.cartella)
    os.makedirs(cart, exist_ok=True)
    pref = a.prefisso or f"card-{a.dove}"

    tmp = os.path.join(cart, f"_qr_{a.dove}.png")
    simbolo = "pin" if a.dove == "mappa" else ""
    logo = None if simbolo else os.path.join(REPO, "LOGO-PA.webp")
    crea_qr(DESTINAZIONI[a.dove], tmp, 1400, logo, simbolo=simbolo)

    for suff, (W, H) in {"post": (1080, 1080), "storia": (1080, 1920)}.items():
        out = os.path.join(cart, f"{pref}-{suff}.jpg")
        card(W, H, tmp, titolo, sotto).save(out, quality=92)
        print("card:", out, (W, H))
    os.remove(tmp)


if __name__ == "__main__":
    main()
