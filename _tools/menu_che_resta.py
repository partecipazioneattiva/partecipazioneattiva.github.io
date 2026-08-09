#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IL MENU CHE RESTA IN ALTO, E SI STRINGE QUANDO SI SCORRE
=========================================================
9 agosto 2026.

    python3 _tools/menu_che_resta.py            # prova a vuoto
    python3 _tools/menu_che_resta.py --applica

CHIESTO DA FERNANDO: «scorrendo, il menu sparisce e per fare qualsiasi altra
scelta sono costretto a risalire». Il guadagno e' misurato: Nielsen Norman
Group rileva circa il 22% di tempo di navigazione risparmiato con una barra
sempre visibile.

DUE PEZZI, e il primo era gia' scritto:

1. RESTARE IN ALTO — bastava togliere UNA parola. La regola del menu diceva
   «position: sticky» e tre righe dopo, DENTRO LA STESSA REGOLA, «position:
   relative». In CSS vince l'ultima: lo sticky era annullato da mesi.
   Corretto in css/pa-leggibilita.css, e vale su tutte e 66 le pagine perche'
   il foglio e' condiviso.

2. STRINGERSI — questo lo fa il pezzo di codice qui sotto, ed e' il motivo
   per cui questo strumento esiste. La barra e' alta 130 px su uno schermo da
   812: il 16%. La ricerca dice di stare sotto il 10%. Appena si scorre, la
   barra si stringe (logo piu' piccolo, sottotitolo nascosto) e scende
   intorno ai 70 px. Tornando in cima si riapre.

PERCHE' UN PEZZO DI CODICE IN OGNI PAGINA E NON UN FILE SOLO: il sito non ha
un file di script condiviso, ogni pagina si porta la propria roba. Sono venti
righe: aggiungerne un file da scaricare costerebbe piu' di quanto pesa.

⚠️ Si puo' rilanciare quante volte si vuole: se il pezzo c'e' gia', salta.
"""
import os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

FIRMA = "pa-menu-che-resta"

PEZZO = """<script data-pagefind-ignore id="pa-menu-che-resta">
/* La barra del menu si stringe appena si scorre. Vedi _tools/menu_che_resta.py */
(function(){
  var b = document.querySelector('.navbar');
  if (!b) return;
  var giu = false, soglia = 60, fermo = false;
  function guarda(){
    fermo = false;
    var ora = (window.scrollY || document.documentElement.scrollTop) > soglia;
    if (ora !== giu) { giu = ora; b.classList.toggle('pa-compatta', ora); }
  }
  window.addEventListener('scroll', function(){
    if (fermo) return;                 /* non ricalcolo a ogni pixel: */
    fermo = true;                      /* una volta per fotogramma basta */
    window.requestAnimationFrame(guarda);
  }, { passive: true });
  guarda();
})();
</script>
"""


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    fatte = saltate = senza = 0
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        if "class=navbar" not in d and 'class="navbar"' not in d:
            senza += 1
            continue
        if FIRMA in d:
            saltate += 1
            continue
        i = d.rfind("</body>")
        if i == -1:
            i = len(d)
        d2 = d[:i] + PEZZO + d[i:]
        fatte += 1
        print(f"  ✏️  {f}")
        if APPLICA:
            open(p, "w", encoding="utf-8").write(d2)

    print(f"\n  {fatte} pagine · {saltate} avevano gia' il pezzo · "
          f"{senza} senza menu (pagine di passaggio: non ne hanno bisogno)")
    if not APPLICA:
        print("  (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
