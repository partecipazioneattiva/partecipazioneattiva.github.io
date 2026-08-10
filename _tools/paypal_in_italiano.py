#!/usr/bin/env python3
"""Il pulsante PayPal si apre in italiano — anche dal telefono.

Perche' esiste (10 agosto 2026, segnalazione di Angelo Nicotra).
Sul suo telefono la pagina di donazione mostrava «Dona a Partecipazione
Veicolo». Il nome sbagliato non veniva ne' dal sito ne' da PayPal: la pagina
arrivava in INGLESE e il traduttore automatico del telefono la ribaltava in
italiano traducendo anche il nome dell'associazione. Prova: le frasi della
schermata («Dona a», «per contribuire a coprire le commissioni») sono la
traduzione automatica dell'inglese, non l'italiano vero di PayPal
(«Invia una donazione a», «per aiutare a pagare le tariffe»).

La cura: chiedere a PayPal la pagina gia' in italiano con locale.x=it_IT.
Se arriva in italiano il traduttore non si accende e il nome resta intero.

    python3 _tools/paypal_in_italiano.py            # anteprima
    python3 _tools/paypal_in_italiano.py --applica  # scrive
"""
import re
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
VECCHIO = "https://www.paypal.com/donate/?hosted_button_id=MWQLS8ECREKCQ"
NUOVO = VECCHIO + "&amp;locale.x=it_IT"

# gia' a posto? (dentro un attributo href la & si scrive &amp;)
GIA_FATTO = re.compile(re.escape(VECCHIO) + r"&(amp;)?locale\.x=it_IT")


def main() -> int:
    applica = "--applica" in sys.argv
    toccate = 0
    totale = 0

    for pagina in sorted(RADICE.glob("*.html")):
        testo = pagina.read_text(encoding="utf-8")
        if VECCHIO not in testo:
            continue
        if GIA_FATTO.search(testo):
            continue
        quanti = testo.count(VECCHIO)
        nuovo_testo = testo.replace(VECCHIO, NUOVO)
        toccate += 1
        totale += quanti
        print(f"  {pagina.name}: {quanti} link")
        if applica:
            pagina.write_text(nuovo_testo, encoding="utf-8")

    verbo = "aggiornate" if applica else "da aggiornare"
    print(f"\n{toccate} pagine {verbo}, {totale} link in tutto.")
    if not applica and toccate:
        print("Per scrivere davvero:  python3 _tools/paypal_in_italiano.py --applica")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
