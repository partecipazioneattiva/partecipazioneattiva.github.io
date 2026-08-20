#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scontorno di un ritratto: toglie lo sfondo e lascia un PNG con canale alfa.

Perche' non `rembg`: sul Mac di Fernando rembg non parte piu' (importa numba,
che rifiuta NumPy 2.5). Il modello pero' e' gia' scaricato in ~/.u2net, quindi
qui si chiama direttamente con onnxruntime — nessuna dipendenza fragile.

    /opt/homebrew/Caskroom/miniforge/base/envs/comfyui/bin/python3 \
        _tools/scontorna.py ritratto.png ritratto_scontornato.png

⛔ NON con l'ambiente `base`: onnxruntime li' non c'e' (verificato il
20/08/2026, "ModuleNotFoundError: No module named 'onnxruntime'"). Ce l'hanno
`comfyui`, `iopaint`, `whisperx` e altri: si usa **comfyui**.

Modelli disponibili in ~/.u2net (--modello):
    birefnet-general   il migliore sui capelli, ~30 s        (predefinito)
    u2net_human_seg    piu' rapido, bordo piu' duro
"""

import argparse
import os

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter

MODELLI = os.path.expanduser("~/.u2net")
MEDIA = np.array([0.485, 0.456, 0.406], np.float32)
SCARTO = np.array([0.229, 0.224, 0.225], np.float32)


def maschera(im, percorso_modello, lato=1024):
    x = np.asarray(im.resize((lato, lato), Image.LANCZOS), dtype=np.float32) / 255.0
    x = ((x - MEDIA) / SCARTO).transpose(2, 0, 1)[None]
    s = ort.InferenceSession(percorso_modello, providers=["CPUExecutionProvider"])
    uscite = s.run(None, {s.get_inputs()[0].name: x})
    m = (uscite[0] if uscite[0].ndim == 4 else uscite[-1])[0, 0]
    m = 1 / (1 + np.exp(-m))
    m = (m - m.min()) / (m.max() - m.min() + 1e-8)
    return Image.fromarray((m * 255).astype(np.uint8))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("sorgente")
    p.add_argument("uscita")
    p.add_argument("--modello", default="birefnet-general")
    p.add_argument("--eroni", type=int, default=1,
                   help="pixel di bordo da mangiare: toglie l'alone del vecchio sfondo")
    p.add_argument("--sfuma", type=float, default=1.2)
    a = p.parse_args()

    im = Image.open(a.sorgente).convert("RGB")
    m = maschera(im, os.path.join(MODELLI, a.modello + ".onnx")).resize(im.size, Image.LANCZOS)

    # Il bordo eredita il colore dello sfondo vecchio (sul ritratto TV: un alone
    # verde nei capelli). Mangiarne un pixel lo elimina senza intaccare la sagoma.
    for _ in range(a.eroni):
        m = m.filter(ImageFilter.MinFilter(3))
    m = m.filter(ImageFilter.GaussianBlur(a.sfuma))

    fuori = im.convert("RGBA")
    fuori.putalpha(m)
    fuori.save(a.uscita)
    print("scontornato:", a.uscita, fuori.size)


if __name__ == "__main__":
    main()
