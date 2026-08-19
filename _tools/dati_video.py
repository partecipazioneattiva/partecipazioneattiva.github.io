#!/usr/bin/env python3
"""Mette il dato strutturato VideoObject sui video incorporati nelle pagine.

Il problema, letto nella Search Console il 19/08/2026: «Video — 0 indicizzati,
8 non indicizzati». Google trovava gli otto video incorporati da YouTube ma non
li faceva entrare in ricerca, perche' nessuna pagina del sito diceva, in forma
leggibile da una macchina, che cosa fossero: titolo, durata, data di
pubblicazione, miniatura. Nel sito non c'era un solo VideoObject.

Titolo, data e durata NON si scrivono a mano: si leggono da YouTube e si
tengono in _tools/video_youtube.json, cosi' la seconda esecuzione non ripassa
dalla rete. La descrizione e' la prima frase di quella scritta sotto al video
su YouTube — e' testo nostro, non inventato qui.

    python3 _tools/dati_video.py            # mostra
    python3 _tools/dati_video.py --applica  # scrive
    python3 _tools/dati_video.py --rileggi  # rilegge da YouTube anche cio' che e' in cache
"""
import glob
import json
import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
CACHE = os.path.dirname(os.path.abspath(__file__)) + '/video_youtube.json'
SITO = 'https://partecipazione-attiva.it/'

INIZIO = '<!-- VIDEO-DATI:inizio -->'
FINE = '<!-- VIDEO-DATI:fine -->'
EMBED = re.compile(r'youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{11})')


def durata_iso(secondi):
    s = int(secondi)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    fuori = 'PT'
    if h:
        fuori += '%dH' % h
    if m:
        fuori += '%dM' % m
    if s or not (h or m):
        fuori += '%dS' % s
    return fuori


def da_youtube(vid):
    pag = subprocess.run(
        ['curl', '-sL', '--max-time', '30', '-A', 'Mozilla/5.0',
         'https://www.youtube.com/watch?v=' + vid],
        capture_output=True, text=True).stdout

    def primo(pat):
        m = re.search(pat, pag)
        return m.group(1) if m else ''

    titolo = primo(r'<meta name="title" content="([^"]*)"')
    if not titolo:
        return None
    desc = primo(r'"shortDescription":"((?:[^"\\]|\\.)*)"')
    desc = desc.encode().decode('unicode_escape') if desc else ''
    # Una frase basta: la descrizione lunga di YouTube ha link e hashtag.
    desc = re.split(r'(?<=[.!?])\s|\n', desc.strip())[0][:300].strip()
    return {
        'name': titolo,
        'description': desc or titolo,
        'uploadDate': primo(r'"uploadDate":"([^"]*)"'),
        'duration': durata_iso(primo(r'"lengthSeconds":"(\d+)"') or 0),
        'thumbnailUrl': miniatura(vid),
    }


def miniatura(vid):
    """La miniatura piu' grande che esiste davvero.

    maxresdefault non c'e' per tutti i video: sul filmato lungo
    dell'assemblea del 6 giugno 2026 risponde 404, e una miniatura che non
    si apre fa scartare l'intero dato strutturato. Si prova a scendere.
    """
    for taglia in ('maxresdefault', 'sddefault', 'hqdefault', 'mqdefault'):
        url = 'https://i.ytimg.com/vi/%s/%s.jpg' % (vid, taglia)
        codice = subprocess.run(
            ['curl', '-s', '-o', os.devnull, '-w', '%{http_code}', '--max-time', '15', url],
            capture_output=True, text=True).stdout.strip()
        if codice == '200':
            return url
    return 'https://i.ytimg.com/vi/%s/hqdefault.jpg' % vid


def cache():
    if os.path.exists(CACHE):
        return json.load(open(CACHE, encoding='utf-8'))
    return {}


def blocco(pagina, video, dati):
    """Un solo script con tutti i video della pagina."""
    oggetti = []
    for vid in video:
        d = dati[vid]
        oggetti.append({
            '@context': 'https://schema.org',
            '@type': 'VideoObject',
            'name': d['name'],
            'description': d['description'],
            'thumbnailUrl': d.get('thumbnailUrl') or 'https://i.ytimg.com/vi/%s/hqdefault.jpg' % vid,
            'uploadDate': d['uploadDate'],
            'duration': d['duration'],
            'embedUrl': 'https://www.youtube.com/embed/' + vid,
            'contentUrl': 'https://www.youtube.com/watch?v=' + vid,
            # Per esteso, non come rimando: un @id che vive solo nella home
            # Google non lo risolve dalle altre pagine.
            'publisher': {
                '@type': 'Organization',
                '@id': SITO + '#org',
                'name': 'Partecipazione Attiva',
                'url': SITO,
                'logo': {'@type': 'ImageObject', 'url': SITO + 'LOGO-PA.webp'},
            },
        })
    corpo = '\n'.join(
        '<script type="application/ld+json">%s</script>' % json.dumps(o, ensure_ascii=False)
        for o in oggetti)
    return INIZIO + '\n' + corpo + '\n' + FINE


def main():
    dati = {} if '--rileggi' in sys.argv else cache()
    pagine = {}
    for perc in sorted(glob.glob(BASE + '*.html')):
        nome = os.path.basename(perc)
        testo = open(perc, encoding='utf-8', errors='ignore').read()
        rob = re.search(r'name=["\']?robots["\']?[^>]*content=["\']?([^">]*)', testo)
        if rob and 'noindex' in rob.group(1):
            continue
        # dedup mantenendo l'ordine di apparizione
        video = list(dict.fromkeys(EMBED.findall(testo)))
        if video:
            pagine[nome] = video

    mancanti = {v for vs in pagine.values() for v in vs} - set(dati)
    for vid in sorted(mancanti):
        print('   🌐 leggo da YouTube:', vid)
        d = da_youtube(vid)
        if not d or not d['uploadDate']:
            print('      ⚠️  niente dati: lo salto (nessun dato inventato)')
            continue
        dati[vid] = d
    if mancanti:
        json.dump(dati, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    tocchi = 0
    for nome, video in pagine.items():
        video = [v for v in video if v in dati]
        if not video:
            continue
        perc = BASE + nome
        testo = open(perc, encoding='utf-8').read()
        nuovo = blocco(nome, video, dati)
        if INIZIO in testo:
            vecchio = re.search(re.escape(INIZIO) + r'.*?' + re.escape(FINE), testo, re.S).group(0)
            if vecchio == nuovo:
                continue
            testo2 = testo.replace(vecchio, nuovo)
            verbo = 'aggiornato'
        else:
            if '</body>' not in testo:
                print('   ⚠️  %s non ha </body>: saltata' % nome)
                continue
            testo2 = testo.replace('</body>', nuovo + '\n</body>', 1)
            verbo = 'aggiunto'
        tocchi += 1
        print('   🎬 %-50s %s %d video' % (nome, verbo, len(video)))
        for v in video:
            print('        %s  %s  %s' % (dati[v]['uploadDate'][:10], dati[v]['duration'],
                                          dati[v]['name'][:56]))
        if '--applica' in sys.argv:
            open(perc, 'w', encoding='utf-8').write(testo2)

    if not tocchi:
        print('   ✅ dati video gia\' a posto')
    elif '--applica' in sys.argv:
        print('   ✅ scritte %d pagine' % tocchi)
    else:
        print('   ℹ️  prova a vuoto: rilancia con --applica per scrivere')


if __name__ == '__main__':
    main()
