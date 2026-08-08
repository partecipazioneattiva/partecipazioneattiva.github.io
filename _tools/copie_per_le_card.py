#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COPIE PICCOLE PER LE CARD DELLA HOME
====================================
Le card della home mostrano le immagini a 140-255 px, ma caricano gli originali
da 800-1368 px, che servono grandi nelle loro pagine. Rimpicciolire l'originale
rovinerebbe quelle pagine; usare l'originale nella card spreca un mega.

Quindi: si crea una COPIA PICCOLA accanto all'originale (stesso nome, con
"-card" prima dell'estensione) e la home usa quella. Le pagine degli articoli
continuano a usare l'originale.

MISURATO l'8 agosto 2026: 11 immagini della home, 1.245 KB, mostrate a un
quarto o un decimo della loro larghezza.

Larghezza delle copie: il doppio di come si vedono (schermi ad alta
definizione), mai sotto 300 px.

    python3 _tools/copie_per_le_card.py            # prova a vuoto
    python3 _tools/copie_per_le_card.py --applica
"""
import os, re, sys
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

# file: quanto si vede nella card della home (misurato nel browser)
CARD = {
    "ape-copertina.webp": 140,
    "pensattivo-rcauto.webp": 255,
    "pensattivo-stabilicum.webp": 140,
    "spanu-audizione-stabilicum.webp": 140,
    "insieme-napoli.webp": 255,
    "stabilicum-preferenze-bocciate-14lug2026.jpg": 140,
    "cavalleggeri-murales-esempio-1.webp": 140,
    "settembre-anticipazioni-card.jpg": 140,
    "mappa-italia.webp": 110,
}


def nome_card(n):
    base, est = os.path.splitext(n)
    return f"{base}-card{est}"


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    fatte = []
    tot_p = tot_d = 0
    for nome, visto in CARD.items():
        p = os.path.join(REPO, "images", nome)
        if not os.path.exists(p):
            print(f"  ⚠️  {nome}: non trovato")
            continue
        im = Image.open(p)
        w, h = im.size
        target = max(300, visto * 2)
        if w <= target:
            print(f"  {nome[:40]:40} gia' piccola ({w} px)")
            continue
        nc = nome_card(nome)
        pc = os.path.join(REPO, "images", nc)
        kb_p = os.path.getsize(p) // 1024
        nh = round(h * target / w)
        tot_p += kb_p
        if APPLICA:
            im2 = im.resize((target, nh), Image.LANCZOS)
            if nc.lower().endswith((".jpg", ".jpeg")):
                im2.convert("RGB").save(pc, quality=80, optimize=True, progressive=True)
            else:
                im2.save(pc, quality=80, method=6)
            kb_d = os.path.getsize(pc) // 1024
        else:
            kb_d = round(kb_p * (target / w) ** 1.7)
        tot_d += kb_d
        fatte.append((nome, nc, target, nh))
        print(f"  {nome[:40]:40} {w:5}px {kb_p:4}KB → {nc[:34]:34} {target}px {kb_d}KB")

    print(f"\n  {len(fatte)} copie · {tot_p} KB → {tot_d} KB  (risparmio {tot_p-tot_d} KB sulla home)")

    # aggiorno la home perche' usi le copie
    if fatte:
        p = os.path.join(REPO, "index.html")
        d = open(p, encoding="utf-8").read()
        n = 0
        for nome, nc, w, h in fatte:
            def sost(m):
                tag = m.group(0).replace(nome, nc)
                tag = re.sub(r'width=("?)\d+\1', f'width="{w}"', tag)
                tag = re.sub(r'height=("?)\d+\1', f'height="{h}"', tag)
                return tag
            d, k = re.subn(r"<img[^>]*images/" + re.escape(nome) + r"[^>]*>", sost, d)
            n += k
        print(f"  home: {n} tag <img> puntano alle copie piccole")
        if APPLICA:
            open(p, "w", encoding="utf-8").write(d)


if __name__ == "__main__":
    main()
