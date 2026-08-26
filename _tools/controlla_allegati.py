#!/usr/bin/env python3
"""Controlla che ogni file linkato dalle pagine esista E sia committato.

Nasce il 26/07/2026: diritto-alla-casa.html era online da giorni con 4 vignette
rotte, il PDF della proposta che dava 404 e og:image inesistente. I 6 file
c'erano sul Mac ma non erano mai stati committati, e git status era sepolto
sotto decine di file non tracciati.

Due modi di rompere una pagina, entrambi controllati qui:
  MANCA    il file non esiste nemmeno sul Mac (link sbagliato o refuso)
  NON SU GITHUB  il file c'e' in locale ma non e' committato: online da' 404

    python3 _tools/controlla_allegati.py

Esce con codice 1 se trova qualcosa: cosi' si puo' mettere in un hook di push.
"""
import os
import re
import subprocess
import sys

BASE = '/Users/osxssd/Desktop/ARCHIVIO GENERALE/LAVORI/partecipazioneattiva/'

# template.html e' il GOLD: i suoi placeholder non sono link reali.
SALTA_PAGINE = {'template.html'}

# Attributi che puntano a file locali.
ATTR = re.compile(
    r'(?:src|href|poster|data-src)\s*=\s*["\']?([^"\'>\s]+)', re.I)
# og:image e twitter:image usano URL assoluti del dominio.
META = re.compile(
    r'<meta[^>]+(?:property|name)\s*=\s*["\'](?:og:image|twitter:image)["\']'
    r'[^>]+content\s*=\s*["\']([^"\']+)', re.I)

DOMINI = ('https://partecipazione-attiva.it/', 'https://www.partecipazione-attiva.it/')


def locale(url):
    """Restituisce il path relativo se il riferimento e' un file del sito."""
    for d in DOMINI:
        if url.startswith(d):
            url = url[len(d):]
            break
    else:
        if re.match(r'^(https?:|mailto:|tel:|data:|javascript:|#|//)', url, re.I):
            return None
    url = url.split('#')[0].split('?')[0]
    if not url or url.endswith('/'):
        return None
    return url.lstrip('/')


def main():
    tracciati = set(subprocess.run(
        ['git', '-C', BASE, 'ls-files'],
        capture_output=True, text=True).stdout.splitlines())

    problemi = []
    for pagina in sorted(f for f in os.listdir(BASE) if f.endswith('.html')):
        if pagina in SALTA_PAGINE:
            continue
        # Solo le pagine gia' online possono essere rotte per i visitatori.
        online = pagina in tracciati
        with open(BASE + pagina, encoding='utf-8', errors='ignore') as f:
            html = f.read()

        for url in set(ATTR.findall(html)) | set(META.findall(html)):
            # Falso allarme gia' pagato (26/08/2026): dentro una stringa
            # JavaScript le virgolette sono protette da una barra rovesciata
            # (d.innerHTML='<iframe src=\'...\'>'), e l'espressione qui sopra
            # ne ricava un "file" chiamato \ . Su
            # settembre-2026-appuntamenti.html segnalava un allegato mancante
            # che non e' mai esistito. Uno strumento che grida al lupo insegna
            # a ignorarlo: meglio saltarli.
            if url.startswith('\\'):
                continue
            rel = locale(url)
            if rel is None or rel.endswith('.html'):
                continue
            if not os.path.exists(BASE + rel):
                problemi.append((pagina, rel, 'MANCA', online))
            elif rel not in tracciati:
                problemi.append((pagina, rel, 'NON SU GITHUB', online))

    if not problemi:
        print('Tutti gli allegati esistono e sono committati.')
        return 0

    problemi.sort(key=lambda p: (not p[3], p[0], p[1]))
    print(f'{len(problemi)} allegati da sistemare:\n')
    for pagina, rel, come, online in problemi:
        urgenza = 'PAGINA ONLINE' if online else 'pagina non pubblicata'
        print(f'  [{come:13}] {rel:52} <- {pagina}  ({urgenza})')
    print('\nI file "NON SU GITHUB" si sistemano con git add; i "MANCA" sono')
    print('link sbagliati o file mai creati: va corretto il link o creato il file.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
