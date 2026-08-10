#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIENTE SBORDI SUI TELEFONI PICCOLI (320 px)
===========================================
9 agosto 2026.

COME SONO SALTATI FUORI. Angelo Nicotra segnala che sulla pagina dell'APE il
testo esce in colonna, una lettera per riga. Correggendo quello ho passato al
setaccio TUTTE le 66 pagine a 320, 375 e 414 px — cosa che non avevo mai fatto
sotto i 375 — e sono venuti fuori altri cinque sbordi laterali che non c'entrano
niente con la segnalazione.

TRE CAUSE DIVERSE, e vanno curate diversamente. La lezione e' quella:
non esiste «la regola che sistema gli sbordi».

1. TABELLE DI DATI (diritto-alla-casa, sanitapubblica)
   Una tabella non si restringe sotto la larghezza minima del suo contenuto:
   e' fatta cosi', e nessuna regola CSS la convince. La si mette dentro un
   riquadro che scorre di lato: la pagina resta ferma, la tabella si sfoglia.
   NON si tocca legge-elettorale-giusta.html: le sue tabelle hanno gia' un
   trattamento per telefono e passano la prova. Non si aggiusta cio' che
   funziona.

2. IMMAGINE CON MISURA FISSA (astensionismo)
   `max-width: 340px` vuol dire «al massimo 340», ma su uno schermo da 320 con
   i margini restano 272: 340 sborda lo stesso. Serve `min(340px, 100%)`,
   cioe' «al massimo 340 MA MAI piu' larga del posto che c'e'».

3. GRIGLIE «LEGGI ANCHE» A DUE COLONNE (mappa, rcauto, sanitapubblica, stabilicum)
   `1fr 1fr` non vuol dire «meta' e meta'»: vuol dire «una parte per uno, ma
   mai piu' strette del loro contenuto». Con un titolo lungo dentro, le colonne
   si allargano e spingono fuori la pagina. `minmax(0, 1fr)` toglie quel
   vincolo. Stesso difetto gia' corretto ieri su altre griglie, sfuggito qui
   perche' scritto dentro il tag invece che nel foglio di stile.

    python3 _tools/niente_sbordi_a_320.py            # prova a vuoto
    python3 _tools/niente_sbordi_a_320.py --applica
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

# 1. le tabelle da mettere in un riquadro che scorre
TABELLE = ["diritto-alla-casa.html", "sanitapubblica.html", "stabilicum.html",
           "ape.html", "astensionismo-comunali2026.html",
           "stabilicum-intelligibilita-trucco-agosto2026.html"]
# legge-elettorale-giusta.html NON c'e': le sue tabelle hanno gia' un
# trattamento per telefono (l'intestazione nascosta) e passano la prova.
# Non si aggiusta cio' che funziona.

# 3. le griglie a due colonne che non si restringono
GRIGLIA_VECCHIA = "grid-template-columns:1fr 1fr;gap:12px"
GRIGLIA_NUOVA = "grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px"


def scorrevole(d):
    """Mette ogni <table> dentro un riquadro che scorre di lato."""
    if "pa-tab-scorre" in d:
        return d, 0
    n = 0

    def avvolgi(m):
        nonlocal n
        n += 1
        return '<div class="pa-tab-scorre">' + m.group(0) + "</div>"

    d = re.sub(r"<table[^>]*>.*?</table>", avvolgi, d, flags=re.S)
    return d, n


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    tocc = 0

    # ---- 1. tabelle
    for f in TABELLE:
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        d2, n = scorrevole(d)
        if n:
            print(f"  ✏️  {f:34} {n} tabelle messe in un riquadro che scorre")
            tocc += 1
            if APPLICA:
                open(p, "w", encoding="utf-8").write(d2)
        else:
            print(f"  ·   {f:34} gia' a posto")

    # ---- 2. immagine con misura fissa
    p = os.path.join(REPO, "astensionismo.html")
    d = open(p, encoding="utf-8").read()
    v = ".pensattivo-img{display:block;max-width:340px;"
    n = ".pensattivo-img{display:block;max-width:min(340px,100%);"
    if d.count(v) == 1:
        print(f"  ✏️  {'astensionismo.html':34} immagine: max-width 340px -> min(340px,100%)")
        tocc += 1
        if APPLICA:
            open(p, "w", encoding="utf-8").write(d.replace(v, n))
    else:
        print(f"  ·   {'astensionismo.html':34} gia' a posto")

    # ---- 3. griglie a due colonne
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        c = d.count(GRIGLIA_VECCHIA)
        if not c:
            continue
        print(f"  ✏️  {f:34} {c} griglia/e «Leggi anche» che ora si restringono")
        tocc += 1
        if APPLICA:
            open(p, "w", encoding="utf-8").write(d.replace(GRIGLIA_VECCHIA, GRIGLIA_NUOVA))

    print(f"\n  {tocc} file toccati")
    if not APPLICA:
        print("  (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
