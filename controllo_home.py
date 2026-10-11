#!/opt/homebrew/bin/python3
"""Controllo della HOME come la vede il visitatore (11/10/2026) — dopo il bug delle card doppie del 10/10.

Non guarda il codice: apre la pagina in un browser vero (Playwright), aspetta che lo script del feed APE
compili le card, e controlla il RISULTATO. E' il metodo che consigliano gli esperti (smoke test sul sito
servito, non regex sul sorgente).
    controllo_home.py              -> prova index.html di questa cartella, servita in locale
    controllo_home.py --url URL    -> prova il sito vero (es. https://partecipazione-attiva.it/)
Esce con codice 1 e dice cosa non va; 0 se tutto torna.
"""
import argparse, functools, http.server, os, re, socketserver, sys, threading
from playwright.sync_api import sync_playwright

QUI = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('--url'); args = ap.parse_args()

srv = None
if args.url:
    url = args.url
else:
    class Muto(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k): pass
    handler = functools.partial(Muto, directory=QUI)
    srv = socketserver.TCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{srv.server_address[1]}/index.html'

JS = """() => [...document.querySelectorAll('a[data-pa-section=homepage-card]')].map(a => {
  const h = a.querySelector('h3');
  return {href: a.getAttribute('href'), titolo: h ? h.textContent.trim() : '', feed: a.classList.contains('pa-apec'),
          badge: /Ultimo aggiornamento/.test(a.textContent), pin: a.hasAttribute('data-pa-pin'),
          data: (a.textContent.match(/(\\d{1,2}) (GENNAIO|FEBBRAIO|MARZO|APRILE|MAGGIO|GIUGNO|LUGLIO|AGOSTO|SETTEMBRE|OTTOBRE|NOVEMBRE|DICEMBRE) (\\d{4})/i) || [''])[0]};
})"""

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    errori_js = []
    pg.on('pageerror', lambda e: errori_js.append(str(e)))
    pg.goto(url, wait_until='networkidle')
    pg.wait_for_timeout(3000)            # il feed APE si scarica dopo il caricamento
    card = pg.evaluate(JS); b.close()
if srv: srv.shutdown()

err = []
if not card: err.append('nessuna card trovata nella home')
href = [c['href'] for c in card]
doppie = sorted({h for h in href if href.count(h) > 1})
if doppie: err.append('card DOPPIE (stesso link): ' + ', '.join(doppie))
tit = [c['titolo'] for c in card if c['titolo']]
tdoppi = sorted({t for t in tit if tit.count(t) > 1})
if tdoppi: err.append('titoli DOPPI: ' + '; '.join(t[:50] for t in tdoppi))
feed = [c for c in card if c['feed']]
if len(feed) > 2: err.append(f'le card del feed APE sono {len(feed)}, il massimo e\' 2')
if sum(c['badge'] for c in card if not c['pin']) > 1: err.append('piu\' di un badge «Ultimo aggiornamento» fra le card non fissate')
if errori_js: err.append('errori JavaScript nella pagina: ' + ' | '.join(errori_js)[:200])

print(f'{url}: {len(card)} card, {len(feed)} dal feed APE, {sum(c["badge"] for c in card)} badge')
for c in card[:6]: print('  ', ('[BADGE] ' if c['badge'] else '') + (c['titolo'] or c['href'])[:60], '|', c['data'])
if err:
    print('CONTROLLO HOME FALLITO:'); [print('  -', e) for e in err]; sys.exit(1)
print('CONTROLLO HOME OK')
