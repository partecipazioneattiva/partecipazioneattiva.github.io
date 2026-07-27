#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dà a mappa.html e azioni.html la STESSA barra di tutto il resto del sito.

Erano le due sole pagine con un'intestazione tutta loro: una barra scura
compatta con 7 voci invece di 12, senza il menu per il telefono e senza i
bottoni Iscriviti/Sostienici. Chi arrivava lì da Facebook non aveva modo di
raggiungere meta' del sito, e vedeva un sito che sembrava un altro sito.

`_tools/allinea_menu.py` le saltava apposta perche' non hanno la <nav>
standard: questo script gliela mette. Da qui in avanti le due pagine hanno la
barra normale e le prende anche allinea_menu.py, quindi questo script serve
UNA VOLTA SOLA. Resta come documentazione di cosa e' stato fatto.

Prende il modello da una pagina sana (battaglie.html), cosi' non c'e' una
seconda copia della barra da tenere aggiornata dentro questo file.

    python3 _tools/allinea_barra_strumento.py            # anteprima
    python3 _tools/allinea_barra_strumento.py --applica  # scrive
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MODELLO = BASE / "battaglie.html"

# pagina -> (inizio del blocco da sostituire, fine)
DA_SOSTITUIRE = {
    "mappa.html": ('<div class="navb"><div class="in">', "</div></div>"),
    "azioni.html": ('<div style="background:#2b2620;padding:12px 18px">', "</div>\n</div>"),
    # trovata dopo le prime due: stessa barra scura di azioni.html.
    # Ci si arriva dal bottone "Perche' una mappa" della pagina Mappa.
    "perche-la-mappa.html": ('<div style="background:#2b2620;padding:12px 18px">', "</div>\n</div>"),
}

SELETTORI = ("topbar", "navbar", "nav-logo", "nav-nome", "nav-links", "nav-cta",
             "btn-iscr", "btn-sost", "burger", "mob-menu")


def blocco_barra(modello):
    """Il markup della barra: dalla topbar fino a </nav>."""
    i = modello.find('<div data-pagefind-ignore class="topbar">')
    j = modello.find("</nav>")
    assert i > 0 and j > i, "barra non trovata nella pagina modello"
    return modello[i:j + 7]


def css_barra(modello):
    """Le regole di stile della barra, media query compresa."""
    fogli = "".join(re.findall(r"<style[^>]*>(.*?)</style>", modello, re.S))
    regole = []
    for r in re.findall(r"[^{}]*\{[^}]*\}", fogli):
        if any(s in r for s in SELETTORI):
            regole.append(r.strip())
    # la media query del telefono e' scritta a parte e va ripresa intera
    for m in re.finditer(r"@media\([^)]*\)\{(?:[^{}]*\{[^}]*\})*[^{}]*\}", fogli):
        if any(s in m.group(0) for s in SELETTORI):
            regole.append(m.group(0))
    assert regole, "nessuna regola di stile trovata"
    return "\n".join(regole)


def modale_e_script(modello):
    """La modale Sostienici e il JS che serve alla barra."""
    i = modello.find('<div data-pagefind-ignore id="modal-sostienici"')
    assert i > 0, "modale non trovata"
    # si scende e si risale coi <div>: contare i </div> a occhio taglia il blocco
    # a meta' (provato: usciva senza tre chiusure).
    profondita, j = 0, i
    for m in re.finditer(r"<div\b|</div>", modello[i:]):
        profondita += 1 if m.group(0) != "</div>" else -1
        if profondita == 0:
            j = i + m.end()
            break
    assert profondita == 0, "modale: <div> non bilanciati"
    modale = modello[i:j]
    js = ('<script>\n'
          'const burger=document.getElementById("burger"),mob=document.getElementById("mobmenu");\n'
          'burger.addEventListener("click",()=>{const e=mob.classList.toggle("on");'
          'burger.classList.toggle("open",e)});\n'
          'function chiudi(){mob.classList.remove("on");burger.classList.remove("open")}\n'
          'function apriSostienici(e){e.preventDefault();'
          'document.getElementById("modal-sostienici").style.display="flex"}\n'
          'document.addEventListener("click",function(e){'
          'if(e.target===document.getElementById("modal-sostienici"))'
          'document.getElementById("modal-sostienici").style.display="none"})\n'
          '</script>')
    return modale, js


def per_pagina(barra, pagina):
    """Segna come attiva la voce della pagina che si sta scrivendo."""
    b = barra.replace(' class="active"', '').replace(' class="active" onclick', ' onclick')
    b = b.replace(f'<a href="{pagina}">', f'<a href="{pagina}" class="active">')
    b = b.replace(f'<a href="{pagina}" onclick="chiudi()">',
                  f'<a href="{pagina}" class="active" onclick="chiudi()">')
    return b


def main():
    applica = "--applica" in sys.argv
    modello = MODELLO.read_text(encoding="utf-8")
    barra = blocco_barra(modello)
    css = css_barra(modello)
    modale, js = modale_e_script(modello)
    print(f"modello: {MODELLO.name} · barra {len(barra)} caratteri · "
          f"stile {len(css)} · modale {len(modale)}")

    for pagina, (apre, chiude) in DA_SOSTITUIRE.items():
        f = BASE / pagina
        t = f.read_text(encoding="utf-8")
        if 'class="navbar"' in t:
            print(f"  {pagina}: ha gia' la barra standard, salto")
            continue
        i = t.find(apre)
        assert i >= 0, f"{pagina}: inizio della vecchia barra non trovato"
        j = t.find(chiude, i)
        assert j > i, f"{pagina}: fine della vecchia barra non trovata"
        j += len(chiude)
        vecchia = t[i:j]
        # sicurezza: dentro il blocco tolto ci devono essere solo link di menu
        n_link = vecchia.count("<a ")
        assert 4 <= n_link <= 14, f"{pagina}: il blocco ha {n_link} link, non e' il menu"

        t = t[:i] + per_pagina(barra, pagina) + t[j:]
        t = t.replace("</head>", f"<style>\n{css}\n</style>\n</head>", 1)
        t = t.replace("</body>", f"{modale}\n{js}\n</body>", 1)

        print(f"  {pagina}: vecchia barra {len(vecchia)} caratteri ({n_link} voci) "
              f"-> barra standard (12 voci + menu telefono + Iscriviti/Sostienici)")
        if applica:
            f.write_text(t, encoding="utf-8")

    print("\nApplicato." if applica else "\nAnteprima: aggiungi --applica per scrivere.")


if __name__ == "__main__":
    main()
