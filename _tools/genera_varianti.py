#!/usr/bin/env python3
"""Genera, IN LOCALE, i modi diversi in cui un visitatore puo' scrivere ogni FAQ.

Perche': BM25 sa contare le parole, non sa che "quanto costa" e "quota annuale"
sono la stessa cosa. La letteratura del recupero informazioni chiama questa
mossa *document expansion* (doc2query, Nogueira 2019): invece di un modello
semantico da far scaricare al visitatore, si allarga l'indice con le parafrasi,
calcolate una volta qui. Costo per chi visita il sito: zero byte in piu' di
modello.

Il modello gira sul Mac (mlx, gemma-3-12b-it-4bit): nessun testo esce di qui,
nessun servizio a pagamento.

REGOLE DI ONESTA' DELLA MISURA:
- Le varianti si generano da domanda+risposta e NON dalle domande di prova:
  il banco (_tools/valuta/domande_prova.json) non entra mai nel prompt, se no
  si misura il proprio compito copiato.
- Le varianti finiscono in _dati/varianti_auto.json, separate da quelle scritte
  a mano in _dati/faq.json: il testo generato dalla macchina resta riconoscibile.
- Non vengono MAI mostrate al visitatore: servono solo a far combaciare la sua
  domanda con la FAQ giusta. Le risposte restano quelle approvate dal direttivo.

    python3 _tools/genera_varianti.py            # primo giro: parafrasi
    python3 _tools/genera_varianti.py --vicine   # secondo giro: distinguere le FAQ confinanti
    python3 _tools/genera_varianti.py --n 3      # prova su 3 FAQ

Il secondo giro (--vicine) nasce da una misura: dopo il primo giro restavano
solo confusioni fra FAQ vicine ("dove vedo i vostri video" finiva su "dove vi
vedo in tv"). Le vicine si calcolano dall'indice stesso con la prova
incrociata, NON dalle domande di prova.
"""
import json
import re
import sys
import time
import unicodedata

BASE = '/Users/osxssd/Desktop/ARCHIVIO GENERALE/LAVORI/partecipazioneattiva/'
MODELLO = 'mlx-community/gemma-3-12b-it-4bit'
USCITA = BASE + '_dati/varianti_auto.json'
QUANTE = 16

ISTRUZIONI = """Sei una persona che visita il sito del movimento Partecipazione Attiva e scrive una domanda nella casella dell'assistente.

Qui sotto c'e' una domanda frequente del sito e la risposta ufficiale.

DOMANDA: {domanda}
RISPOSTA: {risposta}

Scrivi {quante} modi DIVERSI in cui una persona potrebbe chiedere la STESSA cosa.

Regole:
- solo domande o parole chiave, MAI risposte o spiegazioni
- CAMBIA LE PAROLE: sinonimi e modi di dire diversi da quelli della domanda
  originale. Se ripeti le stesse parole non servi a niente.
- le prime {brevi} sono ricerche BREVISSIME di 2 o 4 parole, come si scrive su
  Google: niente verbi di cortesia, niente punto interrogativo
- le altre sono domande parlate corte, come le direbbe una persona anziana
- resta dentro questo argomento: non nominare altri temi del movimento
- italiano corrente, tutto minuscolo, niente numerazione, niente virgolette
- una frase per riga, nient'altro"""


CONTRASTO = """Sei una persona che visita il sito del movimento Partecipazione Attiva e scrive una domanda nella casella dell'assistente.

Questa e' la domanda frequente che ci interessa:
DOMANDA: {domanda}
RISPOSTA: {risposta}

Il sito ha anche queste ALTRE domande, che le assomigliano e che vengono confuse con lei:
{vicine}

Scrivi {quante} ricerche brevi (da 2 a 5 parole) che una persona scriverebbe per arrivare alla DOMANDA di sopra e NON alle altre.

Regole:
- usa le parole che appartengono SOLO alla domanda di sopra: quelle che le altre
  non potrebbero mai usare
- niente parole generiche che valgono per tutte (ad esempio "informazioni",
  "come funziona", "cosa fate")
- solo ricerche, MAI risposte
- italiano corrente, tutto minuscolo, niente numerazione, niente virgolette
- una per riga, nient'altro"""


def carica():
    from mlx_lm import load
    return load(MODELLO)


def genera(modello, tok, testo):
    from mlx_lm import generate
    from mlx_lm.sample_utils import make_sampler
    msg = [{'role': 'user', 'content': testo}]
    prompt = tok.apply_chat_template(msg, add_generation_prompt=True)
    return generate(modello, tok, prompt=prompt, max_tokens=700, verbose=False,
                    sampler=make_sampler(temp=0.8, top_p=0.95))


def normale(t):
    """Chiave per riconoscere i doppioni: minuscole, senza accenti ne' segni."""
    t = unicodedata.normalize('NFD', t.lower())
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return ' '.join(re.findall(r'[a-z0-9]+', t))


def ripulisci(grezzo, gia_viste):
    """Tiene solo le righe utilizzabili: niente elenchi, niente risposte."""
    fuori = []
    for r in grezzo.splitlines():
        r = r.strip()
        r = re.sub(r'^[\-\*•]\s*', '', r)
        r = re.sub(r'^\d+[\.\)]\s*', '', r)
        r = r.replace('"', '').replace('«', '').replace('»', '')
        r = r.strip(' \'`').strip()
        if not r or len(r) < 4 or len(r) > 90:
            continue
        if r.endswith(':') or r.count(',') > 3:
            continue
        n = normale(r)
        if not n or n in gia_viste:
            continue
        gia_viste.add(n)
        fuori.append(r.lower())
    return fuori


def vicine_di(faq, quante=3):
    """Per ogni FAQ, le FAQ che le rubano piu' domande nell'indice attuale.
    Si misura sull'indice (prova incrociata), mai sulle domande di prova."""
    sys.path.insert(0, BASE + '_tools')
    sys.path.insert(0, BASE + '_tools/valuta')
    from prova_motore import costruisci, parole
    from pota_varianti import vincitore

    esche = json.load(open(BASE + '_dati/esche.json', encoding='utf-8'))['esche']
    auto = {}
    try:
        auto = json.load(open(USCITA, encoding='utf-8'))['varianti']
    except FileNotFoundError:
        pass
    ind = costruisci(faq, esche, auto=auto)

    ladri = {f['id']: {} for f in faq}
    for i, testo in enumerate(ind.frasi):
        mio = ind.righe[i]
        if mio == '_esca':
            continue
        v = vincitore(ind, i, parole(testo))
        if v and v != mio and v != '_esca':
            ladri[mio][v] = ladri[mio].get(v, 0) + 1
    return {k: [x for x, _ in sorted(v.items(), key=lambda y: -y[1])[:quante]]
            for k, v in ladri.items()}, auto


def secondo_giro(faq, dati):
    """Genera le ricerche che distinguono ogni FAQ dalle sue confinanti."""
    print('calcolo le FAQ che si confondono fra loro ...', flush=True)
    vicine, auto = vicine_di(faq)
    testo_di = {f['id']: f['domanda'] for f in dati['faq']}

    print(f'carico {MODELLO} ...', flush=True)
    t0 = time.time()
    modello, tok = carica()
    print(f'caricato in {time.time()-t0:.0f}s', flush=True)

    nuove = 0
    for i, f in enumerate(faq, 1):
        vs = vicine.get(f['id'], [])
        if not vs:
            print(f'[{i:2d}/{len(faq)}] {f["id"]:28s} nessuna confinante, salto',
                  flush=True)
            continue
        viste = ({normale(f['domanda'])} | {normale(v) for v in f.get('varianti', [])}
                 | {normale(v) for v in auto.get(f['id'], [])})
        grezzo = genera(modello, tok, CONTRASTO.format(
            domanda=f['domanda'], risposta=f['risposta'], quante=10,
            vicine='\n'.join('- ' + testo_di[v] for v in vs)))
        righe = ripulisci(grezzo, viste)
        auto.setdefault(f['id'], []).extend(righe)
        nuove += len(righe)
        print(f'[{i:2d}/{len(faq)}] {f["id"]:28s} +{len(righe):2d}  '
              f'(vicine: {", ".join(vs)})', flush=True)

    blob = json.load(open(USCITA, encoding='utf-8'))
    blob['varianti'] = auto
    blob['_secondo_giro'] = ('aggiunte ricerche che distinguono ogni FAQ dalle '
                             'confinanti, calcolate con la prova incrociata')
    with open(USCITA, 'w', encoding='utf-8') as g:
        json.dump(blob, g, ensure_ascii=False, indent=1)
    tot = sum(len(v) for v in auto.values())
    print(f'\n+{nuove} varianti di contrasto: ora {tot} in totale '
          f'({time.time()-t0:.0f}s)')


def main():
    limite = int(sys.argv[sys.argv.index('--n') + 1]) if '--n' in sys.argv else None
    contrasto = '--vicine' in sys.argv
    dati = json.load(open(BASE + '_dati/faq.json', encoding='utf-8'))
    faq = [f for f in dati['faq'] if f.get('approvato')]
    if limite:
        faq = faq[:limite]

    if contrasto:
        return secondo_giro(faq, dati)

    print(f'carico {MODELLO} ...', flush=True)
    t0 = time.time()
    modello, tok = carica()
    print(f'caricato in {time.time()-t0:.0f}s', flush=True)

    fuori = {}
    for i, f in enumerate(faq, 1):
        # i doppioni si contano dentro la singola FAQ, non fra FAQ diverse:
        # due FAQ possono legittimamente essere raggiunte dalla stessa parola.
        viste = {normale(f['domanda'])} | {normale(v) for v in f.get('varianti', [])}
        t = time.time()
        grezzo = genera(modello, tok, ISTRUZIONI.format(
            domanda=f['domanda'], risposta=f['risposta'], quante=QUANTE,
            brevi=QUANTE // 2))
        righe = ripulisci(grezzo, viste)
        fuori[f['id']] = righe
        print(f'[{i:2d}/{len(faq)}] {f["id"]:28s} {len(righe):2d} varianti  '
              f'({time.time()-t:.0f}s)', flush=True)

    with open(USCITA, 'w', encoding='utf-8') as g:
        json.dump({
            '_nota': 'Varianti generate in locale da genera_varianti.py per far '
                     'combaciare le domande dei visitatori con le FAQ. NON sono '
                     'testo pubblicato: non vengono mai mostrate, servono solo '
                     'all\'indice di ricerca.',
            '_modello': MODELLO,
            'varianti': fuori,
        }, g, ensure_ascii=False, indent=1)
    tot = sum(len(v) for v in fuori.values())
    print(f'\nscritto _dati/varianti_auto.json: {tot} varianti su {len(faq)} FAQ '
          f'({tot/len(faq):.1f} a testa) in {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
