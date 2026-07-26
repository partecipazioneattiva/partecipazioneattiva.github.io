#!/usr/bin/env python3
"""Lente in navbar -> overlay Pagefind, su tutte le pagine.

Prima: ricerca su 11 pagine su 65, come <div id="search"> DOPO il footer,
sempre aperto (invisibile). Altre 12 caricavano CSS+JS senza inizializzarla.

Il pulsante va PRIMA del burger, non dentro .nav-cta: quel contenitore e'
display:none sotto i 900px e la lente sparirebbe su mobile.

    python3 _tools/aggiungi_ricerca.py [--applica]
"""
import glob
import re
import shutil
import sys
from datetime import datetime

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'

# mappa.html e azioni.html hanno una barra scura tutta loro (pagine-strumento):
# stessa esclusione di _tools/allinea_menu.py, la loro barra si aggiorna a parte.
SALTA = {'template.html', 'conferma.html', 'cancella.html', 'contatto.html',
         'mappa.html', 'azioni.html'}

# ---------------------------------------------------------------- markup

BOTTONE = (
    '<button class="pa-cerca-btn" data-pa-cerca="1" data-pagefind-ignore type="button" '
    'onclick="paApriCerca()" aria-label="Cerca nel sito" title="Cerca nel sito">'
    '<svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" '
    'stroke-width="2.4" stroke-linecap="round"><circle cx="11" cy="11" r="7"></circle>'
    '<line x1="16.5" y1="16.5" x2="21" y2="21"></line></svg></button>'
)

BLOCCO = '''<!--PA-CERCA-->
<style>
.pa-cerca-btn{display:flex;align-items:center;justify-content:center;width:42px;height:42px;flex-shrink:0;margin-left:10px;background:0 0;border:2px solid #e8900a;border-radius:50%;color:#9c5b00;cursor:pointer;transition:all .2s;align-self:center}
.pa-cerca-btn:hover{background:#e8900a;color:#fff;transform:scale(1.06)}
.pa-cerca-ov{display:none;position:fixed;inset:0;z-index:100000;background:rgba(26,13,0,.72);backdrop-filter:blur(3px);padding:80px 20px 20px;overflow-y:auto}
.pa-cerca-ov.on{display:block}
.pa-cerca-box{max-width:680px;margin:0 auto;background:#fff;border-radius:18px;padding:28px 26px 32px;box-shadow:0 24px 70px rgba(0,0,0,.45);position:relative;animation:paCercaIn .22s ease}
@keyframes paCercaIn{from{opacity:0;transform:translateY(-14px)}to{opacity:1;transform:translateY(0)}}
.pa-cerca-box h2{font-family:montserrat,sans-serif;font-size:1.15em;font-weight:900;color:#8a4e00;margin:0 0 4px;padding-right:40px}
.pa-cerca-box .pa-cerca-sub{font-family:merriweather,serif;font-size:.82em;color:#777;margin:0 0 18px}
.pa-cerca-x{position:absolute;top:16px;right:18px;width:34px;height:34px;border:0;border-radius:50%;background:#f4f4f4;color:#8a4e00;font-size:1.3em;line-height:1;cursor:pointer;transition:all .2s}
.pa-cerca-x:hover{background:#e8900a;color:#fff}
.pa-cerca-att{font-family:merriweather,serif;color:#888;font-size:.86em;text-align:center;padding:18px 0}
#pa-cerca-ui{--pagefind-ui-primary:#8a4e00;--pagefind-ui-text:#333;--pagefind-ui-background:#fff;--pagefind-ui-border:#e6d8c2;--pagefind-ui-tag:#fff3e0;--pagefind-ui-border-width:2px;--pagefind-ui-border-radius:10px;--pagefind-ui-font:montserrat,sans-serif;--pagefind-ui-scale:.9}
#pa-cerca-ui .pagefind-ui__result-title a{color:#8a4e00;font-weight:800}
#pa-cerca-ui .pagefind-ui__result-excerpt{font-family:merriweather,serif;color:#555;line-height:1.6}
#pa-cerca-ui mark{background:#ffe9c2;color:#8a4e00;font-weight:700;padding:0 2px;border-radius:3px}
@media(max-width:900px){.pa-cerca-btn{margin-left:auto}.pa-cerca-ov{padding:60px 12px 12px}.pa-cerca-box{padding:24px 18px 26px}}
</style>
<div class="pa-cerca-ov" id="pa-cerca-ov" data-pagefind-ignore role="dialog" aria-modal="true" aria-label="Cerca nel sito">
<div class="pa-cerca-box">
<button class="pa-cerca-x" type="button" onclick="paChiudiCerca()" aria-label="Chiudi la ricerca">&times;</button>
<h2>Cerca nel sito</h2>
<p class="pa-cerca-sub">Articoli, battaglie, documenti e video di Partecipazione Attiva.</p>
<div id="pa-cerca-ui"><p class="pa-cerca-att">Sto preparando la ricerca&hellip;</p></div>
</div></div>
<script>
var paCercaPronta=false;
function paApriCerca(){
  var ov=document.getElementById('pa-cerca-ov');
  ov.classList.add('on');document.body.style.overflow='hidden';
  if(paCercaPronta){var i=ov.querySelector('input');if(i)i.focus();return}
  paCercaPronta=true;
  var css=document.createElement('link');css.rel='stylesheet';css.href='/pagefind/pagefind-ui.css';
  document.head.appendChild(css);
  var js=document.createElement('script');js.src='/pagefind/pagefind-ui.js';
  js.onload=function(){
    document.getElementById('pa-cerca-ui').innerHTML='';
    new PagefindUI({element:'#pa-cerca-ui',showImages:false,showSubResults:true,pageSize:6,
      placeholder:'Cerca una parola, un tema, un nome\\u2026',
      translations:{placeholder:'Cerca una parola, un tema, un nome\\u2026',
        zero_results:'Nessun risultato per "[SEARCH_TERM]"',
        many_results:'[COUNT] risultati per "[SEARCH_TERM]"',
        one_result:'1 risultato per "[SEARCH_TERM]"',
        searching:'Sto cercando\\u2026',
        load_more:'Mostra altri risultati',
        clear_search:'Cancella',
        alt_search:'Nessun risultato per "[SEARCH_TERM]". Mostro invece i risultati per "[DIFFERENT_TERM]"',
        search_suggestion:'Nessun risultato per "[SEARCH_TERM]". Prova con una di queste ricerche:'}});
    setTimeout(function(){var i=ov.querySelector('input');if(i)i.focus()},120);
  };
  js.onerror=function(){document.getElementById('pa-cerca-ui').innerHTML='<p class="pa-cerca-att">Ricerca non disponibile in questo momento.</p>'};
  document.head.appendChild(js);
}
function paChiudiCerca(){document.getElementById('pa-cerca-ov').classList.remove('on');document.body.style.overflow=''}
document.addEventListener('keydown',function(e){if(e.key==='Escape')paChiudiCerca()});
document.addEventListener('click',function(e){if(e.target&&e.target.id==='pa-cerca-ov')paChiudiCerca()});
</script>
<!--/PA-CERCA-->
'''

# ---------------------------------------------------------------- pulizia

def pulisci(s):
    """Toglie il vecchio impianto di ricerca e un eventuale blocco precedente."""
    n = 0
    # blocco generato da questo stesso script (idempotenza)
    s2, k = re.subn(r'<!--PA-CERCA-->.*?<!--/PA-CERCA-->\s*', '', s, flags=re.S)
    s, n = s2, n + k
    s2, k = re.subn(r'<button class="pa-cerca-btn".*?</button>', '', s, flags=re.S)
    s, n = s2, n + k
    # vecchio contenitore in fondo alla pagina + init
    s2, k = re.subn(r'<div id=["\']?search["\']?[^>]*>\s*</div>\s*', '', s, flags=re.S)
    s, n = s2, n + k
    s2, k = re.subn(r'<script>\s*window\.addEventListener\(["\']DOMContentLoaded["\'].*?PagefindUI.*?</script>\s*',
                    '', s, flags=re.S)
    s, n = s2, n + k
    # asset nell'head: ora si caricano al primo clic
    s2, k = re.subn(r'<link [^>]*href=["\']?/pagefind/pagefind-ui\.css["\']?[^>]*>', '', s)
    s, n = s2, n + k
    s2, k = re.subn(r'<script [^>]*src=["\']?/pagefind/pagefind-ui\.js["\']?[^>]*>\s*</script>', '', s)
    s, n = s2, n + k
    return s, n


def main():
    applica = '--applica' in sys.argv
    marca = datetime.now().strftime('%Y%m%d_%H%M%S')
    fatti, saltati = [], []

    for path in sorted(glob.glob(BASE + '*.html')):
        f = path.rsplit('/', 1)[1]
        if f in SALTA or f.startswith('google'):
            saltati.append((f, 'esclusa'))
            continue

        orig = open(path, encoding='utf-8').read()
        s, ripuliti = pulisci(orig)

        # 1. pulsante lente: prima del burger (resta visibile su mobile).
        #    Ripiego su </nav> per le navbar piu' vecchie che il burger non ce l'hanno
        #    (sanitapubblica.html, pensattivo-rapporti.html).
        m = re.search(r'<button class=["\']?burger["\']?', s)
        if not m:
            m = re.search(r'</nav>', s)
        if not m:
            saltati.append((f, 'niente navbar: pagina fuori struttura'))
            continue
        s = s[:m.start()] + BOTTONE + s[m.start():]

        # 2. overlay + script: prima di </body>
        i = s.rfind('</body>')
        if i < 0:
            saltati.append((f, 'niente </body>'))
            continue
        s = s[:i] + BLOCCO + s[i:]

        if s != orig:
            if applica:
                shutil.copy(path, f'/tmp/{f}.{marca}.bak')
                open(path, 'w', encoding='utf-8').write(s)
            fatti.append((f, ripuliti))

    print(f'pagine con la lente: {len(fatti)}')
    puliti = [x for x in fatti if x[1]]
    print(f'   di cui ripulite dal vecchio impianto: {len(puliti)}')
    if saltati:
        print(f'\npagine saltate: {len(saltati)}')
        for f, perche in saltati:
            print(f'   {f:44} {perche}')
    if not applica:
        print('\nANTEPRIMA. Rilancia con --applica per scrivere.')


if __name__ == '__main__':
    main()
