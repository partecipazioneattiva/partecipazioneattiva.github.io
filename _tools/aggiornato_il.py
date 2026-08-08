#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
«AGGIORNATO IL…» SULLE BATTAGLIE
================================
Fase 3.3 del piano esecutivo.

PERCHE' COSI' E NON CON GLI «STATI»
Nel piano avevo proposto un sistema di stati (attiva / in attesa / conclusa).
La revisione ha fatto notare — giustamente — che uno stato e' una promessa di
manutenzione permanente: una battaglia ferma da otto mesi con su scritto
«attiva» fa piu' danno del silenzio. Un movimento piccolo non la regge.

Questo invece non promette niente e non mente mai: dice quando e' uscito
l'ultimo articolo su quella battaglia. Il lettore ne trae le sue conclusioni.

⚠️ LA DATA NON SI PRENDE DAL NOME DEL FILE.
Provato l'8 agosto 2026: ricorso-rosatellum-cassazione-ottobre2026.html
sembrava di ottobre, ma «ottobre» e' la data dell'UDIENZA — l'articolo e' stato
pubblicato il 20 giugno. Il nome del file racconta di cosa parla, non quando e'
uscito.

E nemmeno dalla data dell'ultima modifica: l'8 agosto 2026 sono state toccate
tutte le pagine del sito per lavori di grafica, e direbbero tutte «8 agosto».

Si usa la data in cui l'articolo e' stato AGGIUNTO al sito (git), che e' la
pubblicazione vera e che nessuna modifica successiva sposta.

    python3 _tools/aggiornato_il.py            # prova a vuoto
    python3 _tools/aggiornato_il.py --applica
"""
import datetime, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

MESI = {1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile", 5: "maggio",
        6: "giugno", 7: "luglio", 8: "agosto", 9: "settembre", 10: "ottobre",
        11: "novembre", 12: "dicembre"}

# pagina della battaglia : come si riconoscono i suoi articoli
BATTAGLIE = {
    "rcauto.html": r"^rcauto",
    "sanitapubblica.html": r"sanita|crosetto",
    "stabilicum.html": r"^stabilicum|^preferenze-stabilicum|^ricorso-rosatellum|^legge-elettorale",
}

MARCA = "bat-aggiornata"


def pubblicato(f):
    """Quando l'articolo e' stato aggiunto al sito."""
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%at", "--", f],
                         capture_output=True, text=True, cwd=REPO).stdout.split()
    return int(out[-1]) if out else None


def ultima(regola):
    voci = []
    for f in sorted(os.listdir(REPO)):
        if f.endswith(".html") and re.search(regola, f):
            t = pubblicato(f)
            if t:
                voci.append((t, f))
    if not voci:
        return None, None, 0
    t, f = max(voci)
    return datetime.datetime.fromtimestamp(t), f, len(voci)


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    p = os.path.join(REPO, "battaglie.html")
    d = open(p, encoding="utf-8").read()
    if MARCA in d:
        d = re.sub(r'<div class="' + MARCA + r'">.*?</div>', "", d, flags=re.S)
        print("  (tolte le righe di prima, le riscrivo aggiornate)")

    n = 0
    for pagina, regola in BATTAGLIE.items():
        dt, f, quanti = ultima(regola)
        if not dt:
            print(f"  ⚠️  {pagina}: nessun articolo trovato")
            continue
        testo = (f'<div class="{MARCA}">🕘 Ultimo aggiornamento: '
                 f'{dt.day} {MESI[dt.month]} {dt.year} · {quanti} articoli pubblicati</div>')
        # va subito prima del bottone «Leggi la battaglia» di quella scheda
        ancora = f'<a href="{pagina}" class="btn-leggi"'
        i = d.find(ancora)
        if i == -1:
            print(f"  ⚠️  {pagina}: non trovo la sua scheda")
            continue
        d = d[:i] + testo + d[i:]
        n += 1
        print(f"  ✏️  {pagina:22} → {dt.day} {MESI[dt.month]} {dt.year} · {quanti} articoli "
              f"(il piu' recente: {f[:40]})")

    if APPLICA:
        open(p, "w", encoding="utf-8").write(d)
        print(f"\n  {n} battaglie aggiornate")
    else:
        print(f"\n  {n} battaglie · (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
