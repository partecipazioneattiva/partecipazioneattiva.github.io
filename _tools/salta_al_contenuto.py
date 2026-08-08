#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
«SALTA AL CONTENUTO» E <main> SU TUTTE LE PAGINE
================================================
Fase 2.1 del piano esecutivo.

IL PROBLEMA, MISURATO l'8 agosto 2026: **nessuna** pagina del sito aveva il
collegamento «salta al contenuto», e solo 12 su 64 avevano un <main>.

Cosa vuol dire in pratica: chi non usa il mouse — per una disabilita', per
abitudine, o perche' usa un lettore vocale — a OGNI pagina deve ripassare le
dodici voci del menu, i due bottoni e la lente prima di arrivare al testo.
Su un sito di 64 pagine e' come rifare le scale ogni volta.

COSA FA:
  1. mette un collegamento «Salta al contenuto» come primissima cosa della
     pagina. Non si vede: compare solo a chi arriva col tasto TAB;
  2. racchiude il contenuto vero in <main id="contenuto">, cosi' il salto ha
     una destinazione e i lettori vocali sanno dov'e' il contenuto.

CONTROLLO DI SICUREZZA: dopo aver racchiuso, verifica che il titolo <h1> della
pagina sia finito DENTRO il <main>. Se non lo e', la pagina non viene scritta.

    python3 _tools/salta_al_contenuto.py            # prova a vuoto
    python3 _tools/salta_al_contenuto.py --applica
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

SALTO = '<a class="salta-contenuto" href="#contenuto">Salta al contenuto</a>'


def posizione_body(d):
    """Dove comincia il contenuto del <body> (il tag puo' anche mancare)."""
    m = re.search(r"<body[^>]*>", d)
    if m:
        return m.end()
    # senza <body>: dopo l'ultimo tag della testa
    for t in ("</head>", "</style>", "</title>"):
        i = d.rfind(t)
        if i != -1:
            return i + len(t)
    return None


def aggiungi_main(d):
    """Racchiude il contenuto fra la fine del menu e il pie' di pagina."""
    if "<main" in d:
        # c'e' gia': mi assicuro solo che abbia l'ancora
        if 'id="contenuto"' in d or "id=contenuto" in d:
            return d, "aveva gia' <main id=contenuto>"
        d2 = re.sub(r"<main\b", '<main id="contenuto"', d, count=1)
        return d2, "aggiunta l'ancora al <main> che c'era"

    i = d.find("</nav>")
    if i == -1:
        return d, None
    i += len("</nav>")
    j = d.find("<footer")
    if j == -1:
        return d, None
    if j <= i:
        return d, None
    nuovo = d[:i] + '\n<main id="contenuto">' + d[i:j] + "</main>\n" + d[j:]
    return nuovo, "contenuto racchiuso in <main>"


def h1_dentro_main(d):
    """Il titolo della pagina e' finito dentro il <main>? (controllo grezzo ma
    efficace: confronto le posizioni nel testo)"""
    m = re.search(r"<main\b", d)
    if not m:
        return None
    fine = d.find("</main>", m.end())
    h1 = re.search(r"<h1\b", d)
    if not h1:
        return True          # pagine senza h1: non ho niente da verificare
    return m.end() < h1.start() < (fine if fine != -1 else len(d))


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    fatte = saltate = bloccate = 0
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        if "<nav" not in d:
            continue
        originale = d
        note = []

        d, nota = aggiungi_main(d)
        if nota:
            note.append(nota)

        if SALTO not in d and "salta-contenuto" not in d:
            b = posizione_body(d)
            if b is None:
                print(f"  ⚠️  {f}: non trovo dove mettere il collegamento")
            else:
                d = d[:b] + "\n" + SALTO + d[b:]
                note.append("aggiunto il collegamento")

        if d == originale:
            saltate += 1
            continue

        ok = h1_dentro_main(d)
        if ok is False:
            bloccate += 1
            print(f"  ⛔ {f}: il titolo NON finisce dentro <main> — non scrivo")
            continue

        fatte += 1
        print(f"  ✏️  {f:46} {' · '.join(note)}")
        if APPLICA:
            open(p, "w", encoding="utf-8").write(d)

    print(f"\n  {fatte} pagine · {saltate} gia' a posto · {bloccate} bloccate dal controllo")
    if not APPLICA:
        print("  (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
