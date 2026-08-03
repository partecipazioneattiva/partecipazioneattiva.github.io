#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepara una cartella per ogni persona con il logo PA e le sue FOTO VERE,
pronte da caricare sui generatori (Gemini, Meta AI, Lumina).

    python3 _tools/prepara_cartelle_candidati.py \
        --origine "/Volumes/2 TB /DESKTOP SSD ESTERNO/SORA PA " \
        --uscita  ~/Desktop/"GEMINI LAVORI" \
        --logo    ~/Desktop/"GEMINI LAVORI"/Antonio/logo_pa.png

Le cartelle di origine si chiamano «Sora <Nome>» e sono piene di immagini
GENERATE mescolate alle fotografie. Qui si tengono solo le seconde.

Come si riconosce una generata, senza aprirla: il nome. Sora, Gemini e gli altri
salvano con schemi fissi (`Image Generation`, `remix`, `simple_compose`, la data
e ora piu' un identificativo lungo). E' un filtro sui nomi, quindi va sempre
verificato a occhio prima di usare le foto — ma toglie il 90% del lavoro.

⚠️ Perche' conta: se si da' in pasto al generatore un volto gia' inventato, lui
   reinventa sopra l'invenzione. La somiglianza si perde a ogni passaggio.
"""

import argparse
import os
import re
import shutil

from PIL import Image

# Schemi di nome tipici dei file generati.
GENERATE = re.compile(
    r"image[ _]generation|remix|simple[ _]compose|_fixed|avatar|"
    r"diverse expressions|ritratto video|^\d{8}_\d{4}_",
    re.IGNORECASE)

# Non sono fotografie della persona anche se stanno nella sua cartella:
# il logo (lo stesso file ricorre in TUTTE le cartelle), manifesti gia' composti,
# banner e copertine.
NON_FOTO = re.compile(
    r"472571345_1123555719558041|logo|banner|manifesto|volantino|copertina|"
    r"^voto|\bist\b|parlero",
    re.IGNORECASE)

ESTENSIONI = (".jpg", ".jpeg", ".png", ".webp", ".heic")


def utile(percorso, lato_minimo):
    try:
        with Image.open(percorso) as im:
            w, h = im.size
    except Exception:
        return None
    if min(w, h) < lato_minimo:
        return None
    return w, h


def impronta(percorso):
    """Firma grossolana per scartare i doppioni (copie, ritagli identici)."""
    import numpy as np
    with Image.open(percorso) as im:
        g = np.asarray(im.convert("L").resize((16, 16), Image.LANCZOS), np.float32)
    g = (g - g.mean()) / (g.std() + 1e-6)
    return g.ravel()


def main():
    import numpy as np
    p = argparse.ArgumentParser()
    p.add_argument("--origine", required=True)
    p.add_argument("--uscita", required=True)
    p.add_argument("--logo", required=True)
    p.add_argument("--prefisso", default="Sora ",
                   help="come iniziano le cartelle delle persone")
    p.add_argument("--lato-minimo", type=int, default=600, dest="lato_minimo")
    p.add_argument("--quante", type=int, default=8,
                   help="quante foto tenere per persona, dalla piu' grande")
    p.add_argument("--salta", default="PENSATTIVO",
                   help="nomi da ignorare, separati da virgola")
    p.add_argument("--applica", action="store_true",
                   help="senza questo mostra solo cosa farebbe")
    a = p.parse_args()

    origine = os.path.expanduser(a.origine)
    uscita = os.path.expanduser(a.uscita)
    salta = [s.strip().lower() for s in a.salta.split(",") if s.strip()]

    for voce in sorted(os.listdir(origine)):
        cartella = os.path.join(origine, voce)
        if not os.path.isdir(cartella) or not voce.startswith(a.prefisso):
            continue
        nome = voce[len(a.prefisso):].strip()
        if not nome or nome.lower() in salta:
            continue

        candidate = []
        for f in sorted(os.listdir(cartella)):
            if f.startswith(".") or not f.lower().endswith(ESTENSIONI):
                continue
            if GENERATE.search(f) or NON_FOTO.search(f):
                continue
            src = os.path.join(cartella, f)
            m = utile(src, a.lato_minimo)
            if m:
                candidate.append((m[0] * m[1], m, src, f))

        candidate.sort(reverse=True)

        # Il logo si intrufola anche con nomi innocui (`4.png`). Lo si riconosce
        # dall'immagine: si confronta ogni candidata con il logo vero.
        imp_logo = impronta(os.path.expanduser(a.logo))
        candidate = [c for c in candidate
                     if float(np.dot(impronta(c[2]), imp_logo) / imp_logo.size) < 0.90]

        tenute, impronte = [], []
        for _, misure, src, f in candidate:
            imp = impronta(src)
            if any(float(np.dot(imp, i) / imp.size) > 0.93 for i in impronte):
                continue
            tenute.append((misure, src, f))
            impronte.append(imp)
            if len(tenute) >= a.quante:
                break

        print(f"\n{nome}: {len(tenute)} foto tenute su {len(candidate)} candidate")
        dest = os.path.join(uscita, nome)
        for misure, src, f in tenute:
            base = re.sub(r"[^a-z0-9]+", "_", os.path.splitext(f)[0].lower()).strip("_")[:28]
            out = f"{nome.lower()}_{base}_{misure[0]}x{misure[1]}{os.path.splitext(f)[1].lower()}"
            print(f"   {misure[0]}x{misure[1]:<5} {f}")
            if a.applica:
                os.makedirs(dest, exist_ok=True)
                shutil.copy2(src, os.path.join(dest, out))
        if a.applica and tenute:
            shutil.copy2(os.path.expanduser(a.logo), os.path.join(dest, "logo_pa.png"))

    if not a.applica:
        print("\n(prova a vuoto: rilanciare con --applica per copiare davvero)")


if __name__ == "__main__":
    main()
