#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMMAGINI SU MISURA
==================
Rimpicciolisce le immagini che sono molto piu' grandi di come si vedono.

⚠️ REGOLA DI SICUREZZA: la misura di riferimento e' quanto l'immagine si vede
DAVVERO, misurata nel browser su TUTTE le pagine che la usano — non su un
campione. Un'immagine che sembra sovradimensionata sulla home puo' servire
grande in un articolo: e' successo con spanu-audizione-stabilicum.webp, larga
1024 px e usata a 732 in una pagina, che stavo per rimpicciolire a 280.

Si conserva il DOPPIO della misura massima, per gli schermi ad alta definizione,
e mai meno di 320 px.

MISURATO l'8 agosto 2026: la home scaricava 1.650 KB di immagini, l'81% del
peso della pagina. Ogni immagine era da 3 a 10 volte piu' grande del necessario.

    python3 _tools/immagini_su_misura.py            # prova a vuoto
    python3 _tools/immagini_su_misura.py --applica
"""
import os, sys
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv
MINIMO = 320

# nome: quanto si vede al massimo, misurato su TUTTE le pagine che lo usano
DA_RIDURRE = {
    "stefano-piva-direttivo.webp": 130,
    "paolo-neri-direttivo.webp": 130,
    "notte-democrazia.webp": 140,
    "cavalleggeri-murales-esempio-1.webp": 342,
    "cavalleggeri-murales-esempio-2.webp": 342,
    "pensattivo-astensionismo.webp": 340,
    "pensattivo-hero.webp": 300,
}


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    print(f"{'file':40} {'da':>12} {'a':>12} {'KB':>14}")
    tot_prima = tot_dopo = 0
    for nome, visto in DA_RIDURRE.items():
        p = os.path.join(REPO, "images", nome)
        if not os.path.exists(p):
            print(f"  ⚠️  {nome}: non trovato")
            continue
        im = Image.open(p)
        w, h = im.size
        target = max(MINIMO, visto * 2)
        if w <= target:
            print(f"  {nome[:38]:38} gia' a misura ({w} px)")
            continue
        kb_prima = os.path.getsize(p) // 1024
        nuovo_h = round(h * target / w)
        tot_prima += kb_prima
        if APPLICA:
            im2 = im.convert("RGB") if im.mode in ("P", "RGBA") and nome.endswith(".jpg") else im
            im2 = im2.resize((target, nuovo_h), Image.LANCZOS)
            im2.save(p, quality=82, method=6)
            kb_dopo = os.path.getsize(p) // 1024
        else:
            kb_dopo = round(kb_prima * (target / w) ** 1.7)   # stima
        tot_dopo += kb_dopo
        print(f"  {nome[:38]:38} {w:5}x{h:<6} {target:5}x{nuovo_h:<6} {kb_prima:5} → {kb_dopo:<5}")
    print(f"\n  totale: {tot_prima} KB → {tot_dopo} KB  (risparmio {tot_prima-tot_dopo} KB)")
    if not APPLICA:
        print("  (i KB dopo sono una stima; rilancia con --applica per i valori veri)")


if __name__ == "__main__":
    main()
