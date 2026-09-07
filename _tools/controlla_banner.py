#!/usr/bin/env python3
"""Controlla i banner in evidenza della home (i riquadri `pa-invito`).

Nessuno script li tocca: pubblica_articolo.py aggiorna card, ticker, sitemap e
feed, ma i banner sono scritti a mano dentro index.html. Restano quindi fermi
mentre il sito va avanti, e quando contengono una data la sbagliano da soli.

Segnala tre cose:
  1. il banner punta a una pagina che non esiste piu';
  2. il banner nomina una data ormai passata (il caso che scade in silenzio);
  3. la pagina puntata non e' piu' fra le card della home ne' e' recente.

Uscita 1 se c'e' almeno una segnalazione, cosi' si puo' mettere in una
verifica automatica. Regola di Fernando, 7 settembre 2026: «quando c'e' un
aggiornamento aggiorni anche questo banner».
"""
import os
import re
import sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.join(BASE, 'index.html')
MESI = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio',
        'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']


def pulisci(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    for a, b in [('&rsquo;', '’'), ('&egrave;', 'e'), ('&eacute;', 'e'),
                 ('&agrave;', 'a'), ('&ograve;', 'o'), ('&mdash;', '-'),
                 ('&ndash;', '-'), ('&amp;', '&'), ('&nbsp;', ' ')]:
        t = t.replace(a, b)
    return re.sub(r'\s+', ' ', t).strip()


def date_nel_testo(t, oggi):
    """Date esplicite (7 settembre) e giorni sciolti agganciati al mese vicino.

    «l'Aula il 9 settembre e il voto finale atteso il 15»: il 15 non porta il
    mese, ma e' lo stesso una data — ed e' proprio quella che marcisce.
    """
    trovate = []
    for m in re.finditer(r'\b(\d{1,2})\s+(' + '|'.join(MESI) + r')\b', t, re.I):
        giorno, mese = int(m.group(1)), MESI.index(m.group(2).lower()) + 1
        trovate.append((date(oggi.year, mese, giorno), m.group(0), m.end()))
    for m in re.finditer(r'\b(?:il|entro|dal|al)\s+(\d{1,2})\b(?!\s*(?:' + '|'.join(MESI) + r'))', t, re.I):
        giorno = int(m.group(1))
        if not 1 <= giorno <= 31:
            continue
        vicine = [d for d in trovate if d[2] < m.start()]
        if not vicine:
            continue
        mese = max(vicine, key=lambda d: d[2])[0].month
        try:
            trovate.append((date(oggi.year, mese, giorno), m.group(0), m.end()))
        except ValueError:
            pass
    return [(d, t) for d, t, _ in trovate]


def controlla(oggi=None):
    oggi = oggi or date.today()
    home = open(HOME, encoding='utf-8').read()
    banner = re.findall(
        r'<a class=?"?pa-invito"?\s+href="([^"]+)"[^>]*>(.*?)</a>', home, re.S)
    if not banner:
        print('nessun banner pa-invito nella home')
        return 0

    segnalazioni = 0
    print(f'{len(banner)} banner in evidenza nella home — oggi {oggi:%d/%m/%Y}\n')
    for href, dentro in banner:
        titolo = pulisci(re.search(r'<b>(.*?)</b>', dentro, re.S).group(1)) if re.search(r'<b>', dentro) else '(senza titolo)'
        testo = pulisci(re.search(r'<p>(.*?)</p>', dentro, re.S).group(1)) if re.search(r'<p>', dentro) else ''
        print(f'  → {href}')
        print(f'    {titolo}')

        if not os.path.exists(os.path.join(BASE, href.split('#')[0])):
            print('    ⛔ la pagina non esiste piu\'')
            segnalazioni += 1

        scadute = [(d, s) for d, s in date_nel_testo(titolo + ' ' + testo, oggi) if d < oggi]
        for d, s in scadute:
            print(f'    ⚠ «{s}» e\' gia\' passato ({d:%d/%m}): il banner dice una cosa non piu\' vera')
            segnalazioni += 1

        if href not in home.split('pa-invito')[-1] and f'href="{href}"' not in home.replace(f'class=pa-invito href="{href}"', '', 1):
            print('    · in home compare solo nel banner, non fra le card')
        print()

    if segnalazioni:
        print(f'{segnalazioni} segnalazione/i — il banner va riscritto a mano in index.html')
        return 1
    print('nessuna segnalazione: i banner reggono')
    return 0


if __name__ == '__main__':
    sys.exit(controlla())
