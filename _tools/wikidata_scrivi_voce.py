#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scrive le dichiarazioni sulla voce Wikidata di Partecipazione Attiva.

Perche' esiste: le modifiche a Wikidata non si possono fare dal browser che uso
io (il dominio e' fuori dalla mia portata, e nel browser interno l'account non e'
connesso). La via ufficiale per farle fare a uno script e' **Special:BotPasswords**:
Wikidata genera una password separata, limitata ai permessi scelti e revocabile
da sola, che non e' la password dell'account.

    https://www.wikidata.org/wiki/Special:BotPasswords

LE CREDENZIALI NON STANNO QUI DENTRO. Questo repository e' pubblico. Stanno in un
file fuori dal repository, che scrive Fernando e che nessun altro legge:

    ~/Desktop/ARCHIVIO GENERALE/LAVORI/_MANUALI_CLAUDE/ACCESSO_WIKIDATA.txt

Uso:
    python3 _tools/wikidata_scrivi_voce.py --prova   # mostra cosa scriverebbe
    python3 _tools/wikidata_scrivi_voce.py           # scrive davvero
"""
import json
import os
import re
import sys

try:
    import requests
except ImportError:
    sys.exit("Manca la libreria requests: python3 -m pip install requests")

VOCE = 'Q140733310'
API = 'https://www.wikidata.org/w/api.php'
UA = 'PartecipazioneAttiva-script/1.0 (https://partecipazione-attiva.it/; webmaster.partecipazione.attiva@gmail.com)'
CONFIG = os.path.expanduser('~/Desktop/ARCHIVIO GENERALE/LAVORI/_MANUALI_CLAUDE/ACCESSO_WIKIDATA.txt')
OGGI = '+2026-07-28T00:00:00Z'
PROVA = '--prova' in sys.argv

CALENDARIO = 'http://www.wikidata.org/entity/Q1985727'
FONTE_ARTICOLO21 = ('https://www.articolo21.org/2026/07/gia-pronti-decine-di-ricorsi-'
                    'contro-la-legge-elettorale-ci-sara-una-grande-mobilitazione-'
                    'clima-simile-al-referendum/')
FONTE_RADIORADICALE = ('https://www.radioradicale.it/scheda/793958/nuova-legge-elettorale-'
                       'ultimo-atto-di-una-deriva-antidemocratica-gli-italiani-al-bivio')


def elemento(qid):
    return {'value': {'entity-type': 'item', 'id': qid}, 'type': 'wikibase-entityid'}


def testo(s):
    return {'value': s, 'type': 'string'}


def data(iso, precisione):
    return {'value': {'time': iso, 'timezone': 0, 'before': 0, 'after': 0,
                      'precision': precisione, 'calendarmodel': CALENDARIO},
            'type': 'time'}


def riferimento(url):
    """Una fonte: l'indirizzo (P854) piu' la data in cui l'abbiamo consultata (P813)."""
    return {'snaks': {
        'P854': [{'snaktype': 'value', 'property': 'P854', 'datavalue': testo(url)}],
        'P813': [{'snaktype': 'value', 'property': 'P813', 'datavalue': data(OGGI, 11)}],
    }}


def dichiarazione(prop, valore, fonti=()):
    d = {'mainsnak': {'snaktype': 'value', 'property': prop, 'datavalue': valore},
         'type': 'statement', 'rank': 'normal'}
    if fonti:
        d['references'] = [riferimento(u) for u in fonti]
    return d


DATI = {
    'labels': {'en': {'language': 'en', 'value': 'Partecipazione Attiva'}},
    'descriptions': {'en': {'language': 'en',
                            'value': 'Italian civic political movement founded in 2021'}},
    'claims': [
        dichiarazione('P31', elemento('Q2738074'),
                      [FONTE_ARTICOLO21, FONTE_RADIORADICALE]),   # movimento politico
        dichiarazione('P31', elemento('Q48204')),                 # associazione
        dichiarazione('P17', elemento('Q38')),                    # Italia
        dichiarazione('P571', data('+2021-00-00T00:00:00Z', 9)),  # fondazione: 2021
        dichiarazione('P856', testo('https://partecipazione-attiva.it/')),
        dichiarazione('P159', elemento('Q2634')),                 # sede: Napoli
        dichiarazione('P2013', testo('PartecipazioneAttiva21')),  # Facebook
        dichiarazione('P2397', testo('UC8ItFAjkb61SwpyuSA5xIpw')),  # canale YouTube
        dichiarazione('P7085', testo('partecipazione.at')),       # TikTok
    ],
}

RIASSUNTO = ('dati anagrafici del movimento di cui faccio parte, '
             'con fonti di stampa indipendenti')


def leggi_credenziali():
    if not os.path.isfile(CONFIG):
        sys.exit(f"""
Manca il file delle credenziali:
    {CONFIG}

Come si prepara (una volta sola):
 1. vai su https://www.wikidata.org/wiki/Special:BotPasswords
 2. crea un accesso chiamato  scriptPA
 3. spunta SOLO il permesso "Modifica pagine esistenti"
 4. Wikidata mostra un nome tipo  Partecipazione Attiva@scriptPA  e una password lunga
 5. crea quel file di testo con dentro due righe:

    utente = Partecipazione Attiva@scriptPA
    password = LA-PASSWORD-LUNGA-CHE-TI-HA-DATO

Quella password non va incollata in chat: la legge solo questo script.
""")
    conf = {}
    for riga in open(CONFIG, encoding='utf-8'):
        riga = riga.strip()
        if not riga or riga.startswith('#') or '=' not in riga:
            continue
        k, v = riga.split('=', 1)
        conf[k.strip().lower()] = v.strip()
    for campo in ('utente', 'password'):
        if not conf.get(campo):
            sys.exit(f"Nel file {CONFIG} manca la riga «{campo} = ...»")
    if '@' not in conf['utente']:
        sys.exit("L'utente deve essere del tipo «NomeAccount@nomeScript» "
                 "(quello che mostra Special:BotPasswords), non il nome semplice.")
    return conf


def entra(sessione, conf):
    r = sessione.get(API, params={'action': 'query', 'meta': 'tokens',
                                  'type': 'login', 'format': 'json'}, timeout=30)
    r.raise_for_status()
    token = r.json()['query']['tokens']['logintoken']
    r = sessione.post(API, data={'action': 'login', 'lgname': conf['utente'],
                                 'lgpassword': conf['password'], 'lgtoken': token,
                                 'format': 'json'}, timeout=30)
    r.raise_for_status()
    esito = r.json().get('login', {})
    if esito.get('result') != 'Success':
        sys.exit(f"Accesso rifiutato: {esito.get('result')} — {esito.get('reason','')}\n"
                 f"Controlla nome e password in {CONFIG}, oppure rigenera l'accesso "
                 f"su Special:BotPasswords.")
    return esito.get('lgusername')


def stato_voce(sessione):
    r = sessione.get(API, params={'action': 'wbgetentities', 'ids': VOCE,
                                  'format': 'json'}, timeout=30)
    r.raise_for_status()
    e = r.json()['entities'][VOCE]
    return {
        'etichetta_it': e.get('labels', {}).get('it', {}).get('value'),
        'etichetta_en': e.get('labels', {}).get('en', {}).get('value'),
        'dichiarazioni': sum(len(v) for v in e.get('claims', {}).values()),
        'proprieta': sorted(e.get('claims', {}).keys()),
    }


def main():
    print(f"Voce: {VOCE}")
    print(f"Dichiarazioni da scrivere: {len(DATI['claims'])}")
    for c in DATI['claims']:
        p = c['mainsnak']['property']
        v = c['mainsnak']['datavalue']['value']
        v = v.get('id') if isinstance(v, dict) and 'id' in v else (
            v.get('time') if isinstance(v, dict) else v)
        fonti = len(c.get('references', []))
        print(f"  {p:6} -> {v}" + (f"   ({fonti} fonti)" if fonti else ''))

    if PROVA:
        print("\nProva a vuoto: niente e' stato inviato.")
        print("Payload valido:", bool(json.dumps(DATI)))
        return

    conf = leggi_credenziali()
    s = requests.Session()
    s.headers['User-Agent'] = UA

    prima = stato_voce(s)
    print(f"\nPrima: {prima['dichiarazioni']} dichiarazioni, "
          f"etichetta inglese: {prima['etichetta_en']!r}")

    utente = entra(s, conf)
    print(f"Connesso come: {utente}")

    r = s.get(API, params={'action': 'query', 'meta': 'tokens', 'format': 'json'},
              timeout=30)
    r.raise_for_status()
    csrf = r.json()['query']['tokens']['csrftoken']

    r = s.post(API, data={'action': 'wbeditentity', 'id': VOCE,
                          'data': json.dumps(DATI, ensure_ascii=False),
                          'summary': RIASSUNTO, 'token': csrf,
                          'maxlag': '5', 'bot': '0', 'format': 'json'}, timeout=60)
    r.raise_for_status()
    risposta = r.json()
    if 'error' in risposta:
        sys.exit(f"Wikidata ha rifiutato: {risposta['error'].get('code')} — "
                 f"{risposta['error'].get('info')}")

    dopo = stato_voce(s)
    print(f"\nDopo: {dopo['dichiarazioni']} dichiarazioni")
    print("Proprieta' presenti:", ' '.join(dopo['proprieta']))
    print(f"Etichetta inglese: {dopo['etichetta_en']!r}")
    print(f"\nVoce: https://www.wikidata.org/wiki/{VOCE}")


if __name__ == '__main__':
    main()
