#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE IMMAGINI SI SCARICANO QUANDO SERVONO
=======================================
Aggiunge loading="lazy" alle immagini che stanno sotto la prima schermata.

MISURATO l'8 agosto 2026:
    archivio.html                29 immagini, 1 differita
    cavalleggeri-cielo-aperto    9 immagini,  1 differita
    index.html                  22 immagini,  9 differite
Su archivio.html 28 foto si scaricavano tutte all'apertura, comprese quelle
dieci schermate piu' giu' che nessuno guardera' mai.

⚠️ LE PRIME DUE IMMAGINI RESTANO SUBITO, apposta: sono quelle che si vedono
per prime, e differirle le farebbe apparire in ritardo. Differire l'immagine
piu' grande della prima schermata peggiora il caricamento invece di
migliorarlo (Lighthouse lo segnala come errore).

Il logo dell'intestazione resta sempre subito: e' in cima a ogni pagina.

    python3 _tools/immagini_differite.py            # prova a vuoto
    python3 _tools/immagini_differite.py --applica
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

SUBITO = 2          # quante immagini restano a caricamento immediato
MAI_DIFFERIRE = ("LOGO-PA.webp",)


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    tot_pag = tot_img = 0
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        tag = list(re.finditer(r"<img\b[^>]*>", d))
        if not tag:
            continue
        aggiunte = 0
        nuovo = []
        ultimo = 0
        visti = 0
        for m in tag:
            t = m.group(0)
            e_logo = any(x in t for x in MAI_DIFFERIRE)
            if not e_logo:
                visti += 1
            gia = "loading=" in t
            differisci = (not e_logo) and (visti > SUBITO) and (not gia)
            if differisci:
                t2 = t[:-1].rstrip()
                t2 += ' loading="lazy" decoding="async">'
                nuovo.append(d[ultimo:m.start()] + t2)
                ultimo = m.end()
                aggiunte += 1
        if aggiunte:
            nuovo.append(d[ultimo:])
            d2 = "".join(nuovo)
            tot_pag += 1
            tot_img += aggiunte
            print(f"  ✏️  {f[:44]:44} {aggiunte:3} immagini differite")
            if APPLICA:
                open(p, "w", encoding="utf-8").write(d2)
    print(f"\n  {tot_img} immagini in {tot_pag} pagine")
    if not APPLICA:
        print("  (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
