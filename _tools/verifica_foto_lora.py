#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlla se un gruppo di foto basta per addestrare una LoRA di una persona.

Una LoRA impara TUTTO quello che si ripete nelle foto, non solo il viso: se in
dieci scatti c'e' sempre lo stesso microfono e lo stesso fondale, impara pure
quelli, e poi te li rimette dentro a ogni generazione. Per questo qui non si
contano le foto: si contano quelle **diverse fra loro** e abbastanza nitide.

    conda activate base
    python3 _tools/verifica_foto_lora.py ~/Desktop/Claude IA/04_MANIFESTI_E_CARD/FOTO_ANTONIO

Bocciature:
  PICCOLA   lato corto sotto 800 px — la LoRA impara una faccia sfocata
  MOSSA     poco contrasto sui bordi: fuori fuoco o mossa
  DOPPIONE  troppo simile a un'altra: conta per una sola
"""

import os
import sys

import numpy as np
from PIL import Image

LATO_MINIMO = 800
NITIDEZZA_MINIMA = 90.0      # varianza del laplaciano su grigio 0-255
SOMIGLIANZA_DOPPIONE = 0.93


def nitidezza(im):
    g = np.asarray(im.convert("L").resize((512, 512), Image.LANCZOS), np.float32)
    lap = (g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:] - 4 * g[1:-1, 1:-1])
    return float(lap.var())


def impronta(im):
    """Firma grossolana: serve solo a riconoscere due scatti quasi uguali."""
    g = np.asarray(im.convert("L").resize((32, 32), Image.LANCZOS), np.float32)
    g = (g - g.mean()) / (g.std() + 1e-6)
    return g.ravel()


def main():
    cartella = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1
                                  else "~/Desktop/Claude IA/04_MANIFESTI_E_CARD/FOTO_ANTONIO")
    file = sorted(f for f in os.listdir(cartella)
                  if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")))
    if not file:
        print("Nessuna foto in", cartella)
        return

    buone, impronte, esiti = [], [], []
    for f in file:
        try:
            im = Image.open(os.path.join(cartella, f))
        except Exception as e:
            esiti.append((f, "ILLEGGIBILE", str(e)[:40]))
            continue
        lato = min(im.size)
        n = nitidezza(im)
        imp = impronta(im)
        gemella = next((b for b, i in zip(buone, impronte)
                        if float(np.dot(imp, i) / imp.size) > SOMIGLIANZA_DOPPIONE), None)

        if lato < LATO_MINIMO:
            esiti.append((f, "PICCOLA", f"lato corto {lato} px, ne servono {LATO_MINIMO}"))
        elif n < NITIDEZZA_MINIMA:
            esiti.append((f, "MOSSA", f"nitidezza {n:.0f}, minimo {NITIDEZZA_MINIMA:.0f}"))
        elif gemella:
            esiti.append((f, "DOPPIONE", "quasi identica a " + gemella))
        else:
            esiti.append((f, "OK", f"{im.size[0]}x{im.size[1]}, nitidezza {n:.0f}"))
            buone.append(f)
            impronte.append(imp)

    largh = max(len(f) for f, _, _ in esiti)
    for f, esito, nota in esiti:
        print(f"{esito:11s} {f:<{largh}}  {nota}")

    print(f"\nUtilizzabili e diverse fra loro: {len(buone)} su {len(file)}")
    if len(buone) >= 12:
        print("Bastano. Si puo' addestrare.")
    elif len(buone) >= 8:
        print("Al limite: si puo' provare, ma con 12-15 viene molto meglio.")
    else:
        print(f"Non bastano: ne mancano almeno {8 - len(buone)}.")
    print("\n⚠️  Nessuna immagine GENERATA dall'IA in questa cartella: la LoRA "
          "imparerebbe il volto sbagliato.")


if __name__ == "__main__":
    main()
