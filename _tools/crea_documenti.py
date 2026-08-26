#!/usr/bin/env python3
"""Genera documenti.html: indice dei PDF con estratti verbatim.

Pagefind non legge dentro i PDF: Statuto, Manifesto e Regolamenti erano
invisibili alla ricerca. L'estratto e' visibile, non nascosto: testo
nascosto per sola indicizzazione e' cloaking.

Solo PDF gia' committati: gli untracked sono bozze non pubblicate e online
darebbero 404.

    python3 _tools/crea_documenti.py
"""
import os
import re
import subprocess
import sys

BASE = '/Users/osxssd/Desktop/ARCHIVIO GENERALE/LAVORI/partecipazioneattiva/'

# (percorso, titolo, categoria, a cosa serve)
DOCUMENTI = [
    ('files/Statuto-PA.pdf', 'Statuto', 'Atto fondativo',
     "L'atto che regola l'associazione: denominazione, scopo, soci, organi, patrimonio."),
    ('files/PA_MANIFESTO_290922_DEF.pdf', 'Manifesto Politico', 'Atto fondativo',
     'La visione politica del movimento e le proposte su cui si fonda.'),
    ('documenti/APE_Assemblea_Popolare_Ecumenica_v6.8.pdf',
     'APE &mdash; Assemblea Popolare Ecumenica', 'Proposta di riforma',
     "La proposta di riforma costituzionale del movimento: articolato, allegati tecnici, obiezioni e risposte."),
    ('documenti/perche-una-mappa.pdf', 'Perch&eacute; una Mappa', 'Progetto',
     'Le ragioni della Mappa dei cittadini attivi e come funziona.'),
    ('files/Regolamento-del-Comitato-Direttivo.pdf', 'Regolamento del Comitato Direttivo',
     'Regolamento interno', 'Composizione, convocazione e funzionamento del Comitato Direttivo.'),
    ('files/Regolamento-per-le-Assemblee.pdf', 'Regolamento per le Assemblee',
     'Regolamento interno', 'Come si convocano e si svolgono le assemblee degli iscritti.'),
    ('files/Regolamento-per-le-candidature-degli-iscritti.pdf',
     'Regolamento per le candidature degli iscritti', 'Regolamento interno',
     'I criteri con cui un iscritto pu&ograve; candidarsi.'),
    ('files/Regolamento-per-le-restituzioni.pdf', 'Regolamento per le restituzioni',
     'Regolamento interno', 'Come funzionano le restituzioni degli eletti al movimento.'),
    ('files/Regolamento-Unita-Territoriali.pdf', 'Regolamento Unit&agrave; Territoriali',
     'Regolamento interno', 'Come nascono e come operano i gruppi sul territorio.'),
]

RUMORE = re.compile(
    r'^(pag\.?\s*\d+|pagina\s+\d+|\d+\s*/\s*\d+|[-–—\s]*\d+[-–—\s]*)$', re.I)


def estratto(pdf, max_char=900):
    """Estratto verbatim dal PDF, ripulito dalle intestazioni di pagina."""
    r = subprocess.run(['pdftotext', '-enc', 'UTF-8', BASE + pdf, '-'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    righe = []
    for l in r.stdout.splitlines():
        l = l.strip()
        if not l or RUMORE.match(l):
            continue
        if re.match(r'^[A-ZÀÈÉÌÒÙ\s]{3,40}\s+Pag\.?\s', l):   # "STATUTO  Pag. 1 di 25"
            l = re.sub(r'\s*Pag\.?\s.*$', '', l)
            if not l:
                continue
        righe.append(l)
    testo = re.sub(r'\s+', ' ', ' '.join(righe)).strip()
    if len(testo) <= max_char:
        return testo
    taglio = testo[:max_char]
    p = max(taglio.rfind('. '), taglio.rfind('? '), taglio.rfind('! '))
    return (taglio[:p + 1] if p > max_char * 0.5 else taglio.rsplit(' ', 1)[0]) + ' […]'


def pubblicato(pdf):
    return subprocess.run(['git', 'ls-files', '--error-unmatch', pdf],
                          cwd=BASE, capture_output=True).returncode == 0


CSS = '''
.doc-card{background:#fff;border:1px solid #f0e6d3;border-left:5px solid #e8900a;border-radius:14px;padding:24px 26px;margin-bottom:20px}
.doc-card h3{font-family:merriweather,serif;font-size:1.16em;color:#8a4e00;margin-bottom:8px;line-height:1.35}
.doc-meta{display:flex;align-items:center;gap:12px;margin-bottom:10px;flex-wrap:wrap}
.doc-cat{background:#e8900a;color:#fff;font-size:.64em;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;padding:4px 12px;border-radius:50px}
.doc-peso{font-size:.76em;color:#9c5b00;font-weight:700}
.doc-serve{font-family:merriweather,serif;color:#444;line-height:1.7;margin-bottom:14px}
.doc-estratto{background:#fffaf2;border-left:3px solid #e8c98a;border-radius:0 8px 8px 0;padding:14px 18px;margin-bottom:16px}
.doc-estratto p{font-family:merriweather,serif;font-size:.87em;color:#5a5a5a;line-height:1.75;margin:0}
.doc-estratto .et{display:block;font-family:montserrat,sans-serif;font-size:.66em;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;color:#b07500;margin-bottom:7px}
.doc-scarica{display:inline-block;background:#e8900a;color:#fff;padding:11px 24px;border-radius:50px;text-decoration:none;font-weight:900;font-size:.86em}
.doc-scarica:hover{background:#c77607}
'''


def main():
    shell = open(BASE + 'proposte.html', encoding='utf-8').read()
    n = shell.find('</nav>')
    f = shell.find('<footer')
    assert n > 0 and f > n, 'confini della pagina modello non trovati'
    testa, coda = shell[:n + len('</nav>')], shell[f:]

    corpo = ['''
<div class="tv-hero">
  <div class="badge">&#128196; Trasparenza</div>
  <h1>Documenti ufficiali</h1>
  <p>Statuto, Manifesto e regolamenti interni di Partecipazione Attiva. Di ogni documento pubblichiamo un estratto testuale, cos&igrave; sai cosa c&rsquo;&egrave; dentro prima di scaricarlo &mdash; ed &egrave; ricercabile dalla ricerca del sito.</p>
</div>

<div class="tv-wrap">
  <div class="tv-section">
    <div class="tv-section-head"><h2>Tutti i documenti</h2><span>Testi integrali in PDF</span></div>
''']

    fatti, saltati = 0, []
    for pdf, titolo, cat, serve in DOCUMENTI:
        if not os.path.exists(BASE + pdf):
            saltati.append((pdf, 'file assente'))
            continue
        if not pubblicato(pdf):
            saltati.append((pdf, 'non committato: sarebbe un 404'))
            continue
        est = estratto(pdf)
        if not est:
            saltati.append((pdf, 'estrazione fallita'))
            continue
        kb = os.path.getsize(BASE + pdf) // 1024
        corpo.append(f'''    <article class="doc-card">
      <div class="doc-meta"><span class="doc-cat">{cat}</span><span class="doc-peso">PDF &middot; {kb} KB</span></div>
      <h3>{titolo}</h3>
      <p class="doc-serve">{serve}</p>
      <div class="doc-estratto"><span class="et">Estratto dal documento</span><p>{est}</p></div>
      <a class="doc-scarica" href="{pdf}" target="_blank" rel="noopener">Scarica il PDF &darr;</a>
    </article>
''')
        fatti += 1

    corpo.append('''  </div>
</div>

''')

    testa = testa.replace('</style>', CSS + '</style>', 1)

    # I meta arrivano dalla pagina modello (proposte.html): vanno riscritti tutti,
    # non solo il <title>. Lasciarli invariati significherebbe pubblicare una
    # pagina che dichiara ai motori di essere proposte.html.
    T = 'Documenti ufficiali — Partecipazione Attiva'
    D = ('Statuto, Manifesto e regolamenti interni di Partecipazione Attiva, '
         'con un estratto testuale di ogni documento.')
    U = 'https://partecipazione-attiva.it/documenti.html'
    for pat, new in [
        (r'<title>[^<]*</title>', f'<title>{T}</title>'),
        (r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{D}"'),
        (r'<meta property="og:title" content="[^"]*"', f'<meta property="og:title" content="{T}"'),
        (r'<meta property="og:description" content="[^"]*"', f'<meta property="og:description" content="{D}"'),
        (r'<meta property="og:url" content="[^"]*"', f'<meta property="og:url" content="{U}"'),
        (r'<link rel="canonical" href="[^"]*"', f'<link rel="canonical" href="{U}"'),
        (r'<link rel="alternate" hreflang="it" href="[^"]*"',
         f'<link rel="alternate" hreflang="it" href="{U}"'),
    ]:
        testa, k = re.subn(pat, new, testa, count=1)
        assert k == 1, f'meta non trovato o duplicato: {pat}'

    html = testa + ''.join(corpo) + coda
    # Niente split su </head>: queste pagine sono minificate e il tag non c'e'.
    # Si controllano direttamente i meta che devono puntare a documenti.html.
    for campo in ('og:url" content=', 'canonical" href=', 'hreflang="it" href='):
        i = html.find(campo)
        assert i > 0 and 'documenti.html' in html[i:i + 90], f'meta non riscritto: {campo}'
    open(BASE + 'documenti.html', 'w', encoding='utf-8').write(html)

    print(f'documenti.html creata: {fatti} documenti, {len(html)} byte')
    for p, perche in saltati:
        print(f'   saltato  {p:52} {perche}')


if __name__ == '__main__':
    main()
