#!/usr/bin/env python3
"""Analisi tecnica del sito: struttura, accessibilita', peso, link, SEO.

Non e' un'occhiata: e' una misura ripetibile. Ogni voce stampa un NUMERO e,
al massimo, tre esempi. Serve a decidere con i dati se e cosa vale la pena
rifare, e a rimisurare dopo aver messo mano.

    python3 _tools/analizza_sito.py            # riepilogo
    python3 _tools/analizza_sito.py --dettagli # tutti gli esempi, non solo tre
"""
import collections
import html.parser
import json
import os
import re
import sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
SALTA = {'template.html'}
DETT = '--dettagli' in sys.argv


def esempi(lista, n=3):
    lista = sorted(set(lista))
    if DETT or len(lista) <= n:
        return lista
    return lista[:n] + [f'... e altri {len(lista)-n}']


class Pagina(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tag = []            # (nome, attributi) di tutti i tag aperti
        self.ids = []
        self.img = []            # (src, alt_presente, alt_vuoto, lazy, width_height)
        self.link = []           # href
        self.testo_link = []     # (href, testo)
        self.intestazioni = []   # (livello, testo)
        self.lang = None
        self.title = ''
        self.meta = {}
        self.stile_incorporato = 0
        self.script_incorporato = 0
        self._in = None
        self._buf = []
        self._link_ap = None

    def handle_starttag(self, t, a):
        d = dict(a)
        self.tag.append((t, d))
        if 'id' in d:
            self.ids.append(d['id'])
        if t == 'html':
            self.lang = d.get('lang')
        elif t == 'img':
            self.img.append((d.get('src', ''), 'alt' in d, d.get('alt', '').strip() == '',
                             d.get('loading') == 'lazy',
                             ('width' in d and 'height' in d)))
        elif t == 'a' and 'href' in d:
            self.link.append(d['href'])
            self._link_ap = d['href']
            self._buf = []
        elif t in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._in = t
            self._buf = []
        elif t in ('style', 'script'):
            self._in = t
            self._buf = []
        elif t == 'meta':
            n = (d.get('name') or d.get('property') or '').lower()
            if n:
                self.meta[n] = d.get('content', '')
        elif t == 'title':
            self._in = 'title'
            self._buf = []

    def handle_endtag(self, t):
        testo = ''.join(self._buf).strip()
        if t == self._in:
            if t.startswith('h') and len(t) == 2:
                self.intestazioni.append((int(t[1]), testo[:60]))
            elif t == 'style':
                self.stile_incorporato += len(testo)
            elif t == 'script':
                self.script_incorporato += len(testo)
            elif t == 'title':
                self.title = testo
            self._in = None
            self._buf = []
        if t == 'a' and self._link_ap is not None:
            self.testo_link.append((self._link_ap, testo[:40]))
            self._link_ap = None
            self._buf = []

    def handle_data(self, d):
        self._buf.append(d)


def analizza():
    pagine = sorted(f for f in os.listdir(BASE)
                    if f.endswith('.html') and f not in SALTA)
    dati = {}
    for f in pagine:
        grezzo = open(BASE + f, encoding='utf-8', errors='replace').read()
        p = Pagina()
        try:
            p.feed(grezzo)
        except Exception as e:
            print(f'!! {f}: HTML non analizzabile ({e})')
            continue
        p.byte = len(grezzo.encode('utf-8'))
        p.grezzo = grezzo
        dati[f] = p
    return dati


def menu_di(grezzo):
    """La firma del menu: l'elenco dei link dentro <nav>, in ordine."""
    m = re.search(r'<nav[^>]*>(.*?)</nav>', grezzo, re.S | re.I)
    if not m:
        return None
    return tuple(re.findall(r'href="([^"]+)"', m.group(1)))


def main():
    dati = analizza()
    n = len(dati)
    print(f'PAGINE ANALIZZATE: {n}\n')
    print('=' * 72)
    print('1. PESO E DUPLICAZIONE')
    print('=' * 72)
    byte = {f: p.byte for f, p in dati.items()}
    tot = sum(byte.values())
    stile = sum(p.stile_incorporato for p in dati.values())
    script = sum(p.script_incorporato for p in dati.values())
    peggiori = sorted(byte.items(), key=lambda x: -x[1])[:3]
    print(f'HTML totale:            {tot/1024:.0f} KB su {n} pagine '
          f'(media {tot/n/1024:.0f} KB)')
    print(f'CSS scritto in pagina:  {stile/1024:.0f} KB '
          f'({100*stile/tot:.0f}% del totale)')
    print(f'JS scritto in pagina:   {script/1024:.0f} KB '
          f'({100*script/tot:.0f}% del totale)')
    print('pagine piu\' pesanti:    ' + ', '.join(f'{f} ({b/1024:.0f} KB)'
                                                  for f, b in peggiori))

    # Quanto del CSS in pagina e' LO STESSO su piu' pagine: e' il conto che dice
    # se conviene un unico foglio di stile scaricato una volta sola.
    blocchi = collections.Counter()
    for p in dati.values():
        for m in re.findall(r'<style[^>]*>(.*?)</style>', p.grezzo, re.S | re.I):
            blocchi[m.strip()] += 1
    ripetuto = sum(len(t) * (c - 1) for t, c in blocchi.items() if c > 1)
    print(f'CSS IDENTICO ripetuto:  {ripetuto/1024:.0f} KB '
          f'(byte che ogni visitatore riscarica a ogni pagina)')

    print('\n' + '=' * 72)
    print('2. STRUTTURA: il menu e\' allineato?')
    print('=' * 72)
    menu = collections.Counter()
    per_menu = collections.defaultdict(list)
    senza = []
    for f, p in dati.items():
        m = menu_di(p.grezzo)
        if m is None:
            senza.append(f)
        else:
            menu[m] += 1
            per_menu[m].append(f)
    print(f'versioni diverse del menu: {len(menu)}   pagine senza <nav>: {len(senza)}')
    for i, (m, c) in enumerate(menu.most_common()):
        marca = 'MAGGIORANZA' if i == 0 else 'DIVERGE'
        print(f'  [{marca:11s}] {c:2d} pagine, {len(m)} voci')
        if i > 0:
            base = set(menu.most_common(1)[0][0])
            print(f'      in piu\': {esempi(list(set(m)-base))}')
            print(f'      in meno: {esempi(list(base-set(m)))}')
            print(f'      pagine:  {esempi(per_menu[m])}')
    if senza:
        print(f'  senza <nav>: {esempi(senza)}')

    print('\n' + '=' * 72)
    print('3. ACCESSIBILITA\'')
    print('=' * 72)
    senza_alt, alt_vuoto, senza_lang, molti_h1, no_h1 = [], [], [], [], []
    salto = []
    link_vaghi = []
    id_doppi = []
    for f, p in dati.items():
        for src, ha_alt, vuoto, lazy, wh in p.img:
            if not ha_alt:
                senza_alt.append(f'{f}:{os.path.basename(src)[:28]}')
            elif vuoto:
                alt_vuoto.append(f'{f}:{os.path.basename(src)[:28]}')
        if not p.lang:
            senza_lang.append(f)
        h1 = [t for lv, t in p.intestazioni if lv == 1]
        if len(h1) > 1:
            molti_h1.append(f'{f} ({len(h1)})')
        elif not h1:
            no_h1.append(f)
        liv = [lv for lv, _ in p.intestazioni]
        for a, b in zip(liv, liv[1:]):
            if b > a + 1:
                salto.append(f'{f} (h{a}->h{b})')
                break
        for href, testo in p.testo_link:
            if testo.lower().strip(' →>»…') in ('clicca qui', 'qui', 'leggi', 'link',
                                                'continua', 'vai', 'scopri'):
                link_vaghi.append(f'{f}:"{testo}"')
        d = [k for k, c in collections.Counter(p.ids).items() if c > 1]
        if d:
            id_doppi.append(f'{f}:{",".join(d[:3])}')
    tot_img = sum(len(p.img) for p in dati.values())
    print(f'immagini totali: {tot_img}')
    print(f'  senza attributo alt:     {len(senza_alt):3d}   {esempi(senza_alt)}')
    print(f'  con alt vuoto:           {len(alt_vuoto):3d}   {esempi(alt_vuoto)}')
    print(f'pagine senza lang="it":    {len(senza_lang):3d}   {esempi(senza_lang)}')
    print(f'pagine senza h1:           {len(no_h1):3d}   {esempi(no_h1)}')
    print(f'pagine con piu\' h1:        {len(molti_h1):3d}   {esempi(molti_h1)}')
    print(f'salti di livello (h2->h4): {len(salto):3d}   {esempi(salto)}')
    print(f'link dal testo vago:       {len(link_vaghi):3d}   {esempi(link_vaghi)}')
    print(f'id duplicati in pagina:    {len(id_doppi):3d}   {esempi(id_doppi)}')

    print('\n' + '=' * 72)
    print('4. LINK E FILE MANCANTI')
    print('=' * 72)
    rotti, ancore_rotte = [], []
    esterni = collections.Counter()
    ancore_pagina = {}
    for f, p in dati.items():
        ancore_pagina[f] = set(p.ids) | set(re.findall(r'name="([^"]+)"', p.grezzo))
    for f, p in dati.items():
        for href in p.link:
            if href.startswith(('http://', 'https://')):
                esterni[re.sub(r'^https?://([^/]+).*', r'\1', href)] += 1
                continue
            if href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                if href.startswith('#') and len(href) > 1 and href[1:] not in ancore_pagina[f]:
                    ancore_rotte.append(f'{f} -> {href}')
                continue
            pulito = href.split('?')[0].split('#')[0]
            if not pulito:
                continue
            if not os.path.exists(BASE + pulito):
                rotti.append(f'{f} -> {href}')
            elif '#' in href:
                dest = href.split('#')[1]
                if pulito.endswith('.html') and dest and pulito in ancore_pagina \
                        and dest not in ancore_pagina[pulito]:
                    ancore_rotte.append(f'{f} -> {href}')
    print(f'link interni ROTTI:        {len(rotti):3d}   {esempi(rotti)}')
    print(f'ancore (#) inesistenti:    {len(ancore_rotte):3d}   {esempi(ancore_rotte)}')
    print(f'domini esterni citati:     {len(esterni):3d}   '
          f'{[d for d, _ in esterni.most_common(5)]}')

    print('\n' + '=' * 72)
    print('5. SEO / METADATI')
    print('=' * 72)
    no_desc, desc_lunga, no_canon, no_og, titolo_lungo, no_titolo = [], [], [], [], [], []
    noindex = []
    for f, p in dati.items():
        d = p.meta.get('description', '')
        if not d:
            no_desc.append(f)
        elif len(d) > 160:
            desc_lunga.append(f'{f} ({len(d)})')
        if 'rel="canonical"' not in p.grezzo:
            no_canon.append(f)
        if 'og:image' not in p.meta:
            no_og.append(f)
        if not p.title:
            no_titolo.append(f)
        elif len(p.title) > 65:
            titolo_lungo.append(f'{f} ({len(p.title)})')
        if 'noindex' in p.meta.get('robots', ''):
            noindex.append(f)
    print(f'senza meta description:    {len(no_desc):3d}   {esempi(no_desc)}')
    print(f'description oltre 160:     {len(desc_lunga):3d}   {esempi(desc_lunga)}')
    print(f'senza canonical:           {len(no_canon):3d}   {esempi(no_canon)}')
    print(f'senza og:image:            {len(no_og):3d}   {esempi(no_og)}')
    print(f'senza <title>:             {len(no_titolo):3d}   {esempi(no_titolo)}')
    print(f'title oltre 65 caratteri:  {len(titolo_lungo):3d}   {esempi(titolo_lungo)}')
    print(f'pagine noindex:            {len(noindex):3d}   {esempi(noindex)}')

    # sitemap: copre tutte le pagine pubbliche?
    sm = BASE + 'sitemap.xml'
    if os.path.exists(sm):
        dentro = set(re.findall(r'<loc>[^<]*?/([^/<]+\.html)</loc>',
                                open(sm, encoding='utf-8').read()))
        pubbliche = {f for f in dati if f not in noindex}
        print(f'sitemap: {len(dentro)} voci · mancano {len(pubbliche-dentro)} pagine '
              f'{esempi(list(pubbliche-dentro))}')
        fantasmi = [x for x in dentro if not os.path.exists(BASE + x)]
        if fantasmi:
            print(f'  sitemap punta a file inesistenti: {esempi(fantasmi)}')

    print('\n' + '=' * 72)
    print('6. IMMAGINI: peso e formato')
    print('=' * 72)
    usate = set()
    for p in dati.values():
        for src, *_ in p.img:
            usate.add(src.split('?')[0])
        usate |= set(re.findall(r'url\((?:\'|")?([^)\'"]+\.(?:jpg|jpeg|png|webp))',
                                p.grezzo, re.I))
    pesanti, formati = [], collections.Counter()
    tot_img_byte = 0
    for src in usate:
        perc = BASE + src
        if not os.path.exists(perc):
            continue
        b = os.path.getsize(perc)
        tot_img_byte += b
        formati[os.path.splitext(src)[1].lower()] += 1
        if b > 300 * 1024:
            pesanti.append(f'{src} ({b/1024:.0f} KB)')
    lazy = sum(1 for p in dati.values() for i in p.img if i[3])
    dim = sum(1 for p in dati.values() for i in p.img if i[4])
    tot_tag = sum(len(p.img) for p in dati.values())
    print(f'immagini distinte usate:   {len(usate)}  ({tot_img_byte/1024/1024:.1f} MB)')
    print(f'formati:                   {dict(formati)}')
    print(f'oltre 300 KB:              {len(pesanti):3d}   {esempi(pesanti)}')
    print(f'con loading="lazy":        {lazy}/{tot_tag}')
    print(f'con width+height dichiarati: {dim}/{tot_tag}  '
          f'(senza, la pagina "salta" mentre carica)')


if __name__ == '__main__':
    main()
