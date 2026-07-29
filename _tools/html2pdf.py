#!/usr/bin/env python3
"""
html2pdf.py — converte una pagina HTML in un PDF stampabile (A4).

PERCHE' ESISTE (trappola pagata il 29 luglio 2026)
--------------------------------------------------
Sul Mac c'e' anche `wkhtmltopdf`, ed e' comodo perche' e' un comando solo.
Ma il suo motore e' un WebKit vecchio e **si mangia lo spazio prima del
grassetto**: "per assegnare <strong>undici box</strong>" viene stampato
"per assegnarundici box", e lo spazio ricompare dopo il tag ("liberi , con").
Il difetto NON si vede controllando il testo estratto con `pdftotext`: li'
lo spazio c'e'. Si vede solo guardando la pagina. Quindi: per i documenti
che vanno al Direttivo, alle Istituzioni o alla stampa, si usa questo script.

Qui il rendering lo fa Chromium (Microsoft Edge o Brave, gia' installati sul
Mac), pilotato da Playwright: stesso motore dei browser moderni, tipografia
corretta, e il pie' di pagina con il numero di pagina.

USO
---
    python3 _tools/html2pdf.py documento.html
    python3 _tools/html2pdf.py documento.html uscita.pdf
    python3 _tools/html2pdf.py documento.html uscita.pdf --pie "Testo del piede"

Senza --pie il piede riporta solo "pag. N di M". Con --pie, il testo indicato
seguito da " · pag. N di M". Con --senza-pie, nessun piede.

L'HTML puo' fissare i propri margini con @page: vengono rispettati, tranne il
margine basso, che viene allargato quando serve spazio per il piede.
"""

import argparse
import pathlib
import sys

BROWSER_CANDIDATI = [
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]

STILE_PIEDE = (
    "font-family: Helvetica, Arial, sans-serif; font-size: 7pt; color: #888888; "
    "width: 100%; text-align: center; padding: 0 12mm;"
)


def trova_browser() -> str:
    for percorso in BROWSER_CANDIDATI:
        if pathlib.Path(percorso).exists():
            return percorso
    sys.exit(
        "Nessun browser Chromium trovato. Servono Microsoft Edge, Brave, Chrome\n"
        "o Chromium in /Applications."
    )


def converti(
    sorgente: pathlib.Path,
    destinazione: pathlib.Path,
    piede: str | None,
    lato: str = "17mm",
    alto: str = "16mm",
) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Manca Playwright. Installalo con:  pip3 install playwright")

    if piede is None:
        template_piede = "<div></div>"
        margine_basso = alto
    else:
        prefisso = f"{piede} · " if piede else ""
        template_piede = (
            f'<div style="{STILE_PIEDE}">{prefisso}'
            'pag. <span class="pageNumber"></span> di <span class="totalPages"></span>'
            "</div>"
        )
        margine_basso = "18mm"

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=trova_browser())
        pagina = browser.new_page()
        pagina.goto(sorgente.resolve().as_uri(), wait_until="load")
        pagina.emulate_media(media="print")
        pagina.pdf(
            path=str(destinazione),
            format="A4",
            print_background=True,
            prefer_css_page_size=False,
            margin={
                "top": alto,
                "bottom": margine_basso,
                "left": lato,
                "right": lato,
            },
            display_header_footer=piede is not None,
            header_template="<div></div>",
            footer_template=template_piede,
        )
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Converte un HTML in PDF A4 con Chromium (tipografia corretta)."
    )
    parser.add_argument("sorgente", help="file HTML da convertire")
    parser.add_argument("destinazione", nargs="?", help="file PDF da scrivere")
    parser.add_argument("--pie", default="", help="testo del pie' di pagina")
    parser.add_argument(
        "--senza-pie", action="store_true", help="non stampare il pie' di pagina"
    )
    parser.add_argument("--lato", default="17mm", help="margine destro e sinistro (default 17mm)")
    parser.add_argument("--alto", default="16mm", help="margine superiore (default 16mm)")
    argomenti = parser.parse_args()

    sorgente = pathlib.Path(argomenti.sorgente)
    if not sorgente.exists():
        sys.exit(f"Non trovo il file: {sorgente}")

    destinazione = (
        pathlib.Path(argomenti.destinazione)
        if argomenti.destinazione
        else sorgente.with_suffix(".pdf")
    )

    converti(
        sorgente,
        destinazione,
        None if argomenti.senza_pie else argomenti.pie,
        lato=argomenti.lato,
        alto=argomenti.alto,
    )
    print(f"Scritto: {destinazione}")


if __name__ == "__main__":
    main()
