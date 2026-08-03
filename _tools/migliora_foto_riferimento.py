#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migliora le foto piccole da usare come RIFERIMENTO sui generatori (Meta AI,
Gemini, Lumina): le ingrandisce e le pulisce senza toccare il volto.

    conda activate iopaint
    iopaint start --model lama --device mps --port 8080 \
        --enable-realesrgan --realesrgan-device mps
    python3 _tools/migliora_foto_riferimento.py "~/Desktop/GEMINI LAVORI"

Gli originali non si toccano mai: le migliorate finiscono in `migliorate/`
dentro ogni cartella.

⛔ PERCHE' NON SI USANO GFPGAN E RESTOREFORMER (misurato il 3 agosto 2026)
   Sono «restauratori di volti»: ricostruiscono la faccia pescando da un
   archivio di visi imparato. Provati sulla foto del gazebo di Antonio, tutti e
   due hanno **cambiato gli occhi e il sorriso** — a lui erano scuri e
   socchiusi, sono diventati piu' chiari e aperti, e RestoreFormer gli ha
   aperto la bocca mostrando i denti.
   Su una persona vera e' inaccettabile: il riferimento serve proprio a tenere
   il suo viso, e quello glielo cambia prima ancora di cominciare.
   La letteratura lo dice da anni — «generate artificial spectacles ...
   hallucinates facial features» — e qui l'abbiamo visto sulla nostra foto.

✅ RealESRGAN invece ingrandisce e pulisce senza inventare: occhi, bocca ed
   espressione restano gli stessi. E' l'unico che si usa qui.
"""

import argparse
import base64
import io
import os
import sys

import requests
from PIL import Image, ImageFilter

SERVER = "http://127.0.0.1:8080/api/v1"
ESTENSIONI = (".jpg", ".jpeg", ".png", ".webp")


def acceso():
    try:
        r = requests.get(SERVER + "/server-config", timeout=3)
        return "RealESRGAN" in r.text
    except Exception:
        return False


def ingrandisci(percorso, scala):
    r = requests.post(SERVER + "/run_plugin_gen_image", timeout=900, json={
        "name": "RealESRGAN",
        "image": base64.b64encode(open(percorso, "rb").read()).decode(),
        "scale": scala})
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cartella", help="cartella con le sottocartelle delle persone")
    p.add_argument("--soglia", type=int, default=900,
                   help="si migliorano solo le foto sotto questo lato corto")
    p.add_argument("--obiettivo", type=int, default=1200,
                   help="lato corto a cui puntare")
    a = p.parse_args()

    if not acceso():
        print("Server IOPaint spento o senza RealESRGAN. Avviarlo con:\n"
              "  conda activate iopaint && iopaint start --model lama --device mps \\\n"
              "      --port 8080 --enable-realesrgan --realesrgan-device mps",
              file=sys.stderr)
        sys.exit(1)

    radice = os.path.expanduser(a.cartella)
    for persona in sorted(os.listdir(radice)):
        d = os.path.join(radice, persona)
        if not os.path.isdir(d) or persona == "migliorate":
            continue
        dest = os.path.join(d, "migliorate")
        fatte = 0
        for f in sorted(os.listdir(d)):
            if not f.lower().endswith(ESTENSIONI) or "logo_pa" in f or f.startswith("_"):
                continue
            src = os.path.join(d, f)
            with Image.open(src) as im:
                lato = min(im.size)
            if lato >= a.soglia:
                continue
            scala = min(4.0, max(2.0, round(a.obiettivo / lato, 1)))
            grande = ingrandisci(src, scala)
            # Un filo di contrasto locale: RealESRGAN lascia il risultato
            # leggermente molle, e un riferimento molle da' un volto molle.
            grande = grande.filter(ImageFilter.UnsharpMask(radius=2, percent=45, threshold=3))
            os.makedirs(dest, exist_ok=True)
            out = os.path.join(dest, os.path.splitext(f)[0] + f"_x{scala:g}.png")
            grande.save(out)
            print(f"{persona:<10} {lato:>4} px -> {min(grande.size):>4} px   {f}")
            fatte += 1
        if fatte:
            print(f"{persona}: {fatte} migliorate\n")


if __name__ == "__main__":
    main()
