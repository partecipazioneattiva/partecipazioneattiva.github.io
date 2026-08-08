#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRIGLIE CHE RIMPICCIOLISCONO
============================
Corregge le griglie che si rifiutano di stringersi sugli schermi piccoli e
fanno sfondare la pagina di lato.

    minmax(300px, 1fr)  →  minmax(min(300px, 100%), 1fr)

Cosa vuol dire: "la colonna non scende sotto 300 px, MA non supera mai la
larghezza del contenitore". Senza il "min(...)" la colonna resta a 300 px anche
in uno schermo che di posto ne ha 288, e la pagina scorre di lato.

MISURATO l'8 agosto 2026: era la causa dei 12 px di sfondamento residuo a
320 px sulla home, dopo aver corretto il min-width delle griglie.

    python3 _tools/griglie_che_rimpiccioliscono.py            # prova a vuoto
    python3 _tools/griglie_che_rimpiccioliscono.py --applica  # scrive
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

# minmax(280px,1fr) ma NON minmax(min(280px,100%),1fr) gia' corretto
RE = re.compile(r"minmax\(\s*(\d+)px\s*,\s*([^)]+)\)")


def sistema(testo):
    n = [0]

    def sost(m):
        px, resto = m.group(1), m.group(2).strip()
        n[0] += 1
        return f"minmax(min({px}px,100%),{resto})"

    return RE.sub(sost, testo), n[0]


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    tot_file = tot_sost = 0
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        nuovo, n = sistema(d)
        if n:
            tot_file += 1
            tot_sost += n
            print(f"  {f:52} {n} griglia/e")
            if APPLICA:
                open(p, "w", encoding="utf-8").write(nuovo)
    # anche i fogli di stile
    for sub in ("css",):
        d_ = os.path.join(REPO, sub)
        if not os.path.isdir(d_):
            continue
        for f in sorted(os.listdir(d_)):
            if not f.endswith(".css"):
                continue
            p = os.path.join(d_, f)
            d = open(p, encoding="utf-8").read()
            nuovo, n = sistema(d)
            if n:
                tot_file += 1
                tot_sost += n
                print(f"  {sub}/{f:47} {n} griglia/e")
                if APPLICA:
                    open(p, "w", encoding="utf-8").write(nuovo)
    print(f"\n  {tot_sost} griglie in {tot_file} file")
    if not APPLICA:
        print("  (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
