#!/usr/bin/env python3
"""Porta a norma i contrasti dei colori del sito, dentro CSS e pagine.

    python3 _tools/correggi_contrasti.py            # mostra cosa cambierebbe
    python3 _tools/correggi_contrasti.py --applica  # scrive

------------------------------------------------------------------------------
v2 — 2 agosto 2026. Perche' e' servita una v2.
------------------------------------------------------------------------------
La v1 (26/07/2026) toccava SOLO quello che sta dentro <style>. Ma meta' del
sito colora con l'attributo `style=` scritto sul singolo elemento, che non ha
le graffe e quindi non veniva nemmeno guardato. pa11y, installato il
02/08/2026, ha trovato **21 difetti sulla sola home** che la v1 non vedeva.

Tutti i valori qui sotto sono **calcolati** con la formula WCAG (contrasto
minimo 4,5:1 per il testo normale), non scelti a occhio, e sono stati presi
con un margine invece che al pelo: un colore che da' 4,51 passa l'esame e
fallisce al primo ritocco del fondo.

------------------------------------------------------------------------------
Le correzioni, e perche' quelle
------------------------------------------------------------------------------
1. VERDE  #1a8f3c -> #188739       bianco sopra: 4,17 -> 4,60   (v1)
2. BIANCO SU ARANCIO, nel CSS      -> testo #2b1a00: 2,49 -> 6,74   (v1)
3. BIANCO SU ARANCIO, inline       stessa correzione, ma sugli style= (NUOVA)
4+7. OGNI COLORE DI TESTO troppo chiaro per un fondo chiaro viene scurito
     QUANTO BASTA, mantenendo la tinta (vedi `scurisci`). Non c'e' una tabella
     di colori: si calcola. Cosi' #aaa, #999, #888 e l'arancione-testo si
     sistemano tutti con la stessa regola, e domani anche quelli nuovi.
5. AMBRA #9c5b00 nel footer -> #ffb020   3,55 -> 10,42 sul footer scuro (NUOVA)
6. BLU FACEBOOK #1877f2 -> #0d6ae0 bianco sopra: 4,23 -> 5,05      (NUOVA)

L'ARANCIO DI FONDO NON SI TOCCA MAI: e' il colore del movimento. Quando fa da
fondo si cambia il testo che ci sta sopra (regole 2 e 3). Solo quando l'arancio
e' esso stesso il testo su fondo chiaro va scurito, perche' li' non c'e' altra
scelta: il fondo bianco non e' nostro da cambiare.

⚠️ QUESTO SCRIPT NON BASTA DA SOLO. Il fondo vero di un elemento spesso si
eredita e nel codice non si vede: qui si tira a indovinare. Percio' dopo ogni
esecuzione si lancia **`_tools/verifica_contrasti.py --ripristina`**, che misura
col browser pagina per pagina e riporta indietro quelle peggiorate. Il 02/08/2026
ha annullato 7 pagine su 66 — senza di lui sarebbero rimaste peggiorate.

------------------------------------------------------------------------------
La trappola che questa v2 deve evitare: IL FOOTER E' SCURO
------------------------------------------------------------------------------
`footer{background:#1a0d00}` e il grigio #aaa li' sopra e' CHIARO SU SCURO, ed
e' giusto cosi'. Scurirlo insieme agli altri avrebbe reso illeggibile tutto il
footer di 60 pagine "per migliorare l'accessibilita'". Percio':

- si calcola la luminosita' di ogni `background` dichiarato accanto al colore:
  se il fondo e' scuro, si lascia stare;
- i selettori che contengono "foot" si saltano comunque (`.footer-brand p` non
  dichiara il fondo: lo eredita);
- nell'HTML si salta tutto quello che sta da `<footer` in poi;
- `.modal-close` e' escluso a mano: non ho potuto verificare su che fondo stia,
  e non si tocca cio' che non si e' verificato.
"""
import glob
import os
import re
import sys

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '')

VERDE_VECCHIO, VERDE_NUOVO = '#1a8f3c', '#188739'
ARANCIO = 'e8900a'
TESTO_SU_ARANCIO = '#2b1a00'
GRIGIO_NUOVO = '#6b6b6b'
AMBRA_FOOTER_NUOVA = '#ffb020'
FACEBOOK_VECCHIO, FACEBOOK_NUOVO = '#1877f2', '#0d6ae0'
ARANCIO_TESTO_NUOVO = '#a35f00'

BLOCCO = re.compile(r'([^{}]+)\{([^{}]*)\}')
BIANCO = re.compile(r'color:\s*(#fff(?:fff)?|white)\b', re.I)
GRIGIO = re.compile(r'color:\s*#(?:aaa(?:aaa)?|999(?:999)?)\b', re.I)
FONDO = re.compile(r'background(?:-color)?:\s*#([0-9a-f]{3,6})\b', re.I)
SELETTORI_ESCLUSI = ('foot', '.modal-close')


def luminosita(esa):
    """Luminosita' relativa WCAG di un colore esadecimale (0 = nero, 1 = bianco)."""
    esa = esa.lstrip('#')
    if len(esa) == 3:
        esa = ''.join(c * 2 for c in esa)
    if len(esa) != 6:
        return 1.0
    canali = []
    for i in (0, 2, 4):
        c = int(esa[i:i + 2], 16) / 255
        canali.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return .2126 * canali[0] + .7152 * canali[1] + .0722 * canali[2]


def fondo_scuro(dichiarazioni):
    """Vero se accanto al colore c'e' un fondo scuro dichiarato: li' non si tocca."""
    return any(luminosita(m.group(1)) < .4 for m in FONDO.finditer(dichiarazioni))


def contrasto(a, b):
    l1, l2 = sorted((luminosita(a), luminosita(b)), reverse=True)
    return (l1 + .05) / (l2 + .05)


def scurisci(esa, obiettivo=5.2):
    """Scurisce un colore MANTENENDONE LA TINTA finche' non regge su fondo bianco.

    Si moltiplicano i tre canali per lo stesso fattore: il rapporto fra rosso,
    verde e blu non cambia, quindi l'arancione resta arancione e il grigio resta
    grigio — diventano solo piu' scuri. E' la correzione minima che passa: si
    scende a passi dell'1% e ci si ferma appena l'esame e' superato.

    L'obiettivo e' 5,2 e non 4,5 perche' i fondi del sito non sono bianchi: le
    card sono #fafafa e diverse fasce sono crema (#fff7e9). Misurato: puntare a
    4,8 su bianco lascia 4,39 sul crema, cioe' sotto la soglia. 5,2 su bianco
    regge anche li'.
    """
    esa = esa.lstrip('#')
    if len(esa) == 3:
        esa = ''.join(c * 2 for c in esa)
    r, g, b = (int(esa[i:i + 2], 16) for i in (0, 2, 4))
    fattore = 1.0
    for _ in range(100):
        prova = '#%02x%02x%02x' % (int(r * fattore), int(g * fattore), int(b * fattore))
        if contrasto(prova, '#ffffff') >= obiettivo:
            return prova
        fattore -= .01
    return '#333333'


COLORE = re.compile(r'color:\s*(#[0-9a-f]{3,6})\b', re.I)


def schiarisci_o_lascia(dichiarazioni):
    """Scurisce ogni `color:` troppo chiaro per un fondo chiaro. Regole 4 e 7.

    NON si toccano:
    - i colori quasi bianchi (luminosita' > 0,62): sono fatti apposta per stare
      su fondo scuro, scurirli li renderebbe invisibili. E' l'errore che
      cancellerebbe il footer di 60 pagine;
    - i colori gia' abbastanza scuri (luminosita' < 0,18): passano gia';
    - tutto cio' che sta accanto a un fondo scuro dichiarato.
    """
    if fondo_scuro(dichiarazioni):
        return dichiarazioni, []
    cambiati = []

    def uno(m):
        vecchio = m.group(1)
        lum = luminosita(vecchio)
        if not (.18 < lum < .62):
            return m.group(0)
        if contrasto(vecchio, '#ffffff') >= 4.5:
            return m.group(0)
        nuovo = scurisci(vecchio)
        cambiati.append((vecchio, nuovo))
        return 'color:' + nuovo

    return COLORE.sub(uno, dichiarazioni), cambiati


def sistema_blocco(m):
    """Un blocco 'selettore{dichiarazioni}': applica le regole 2, 4 e 7."""
    sel, dich = m.group(1), m.group(2)
    basso = sel.lower()
    prima = dich

    # (2) fondo arancione pieno + testo bianco -> testo marrone scuro.
    # I gradienti no: ".article-hero" va dal marrone #8a4e00 all'arancione e per
    # quasi tutta la sua area il bianco e' leggibile. Scurirlo avrebbe rovinato
    # le testate di 42 articoli per un difetto che li' non c'e'.
    if re.search(r'background(?:-color)?:\s*#' + ARANCIO + r'\s*[;}]?', dich, re.I) and BIANCO.search(dich):
        dich = BIANCO.sub('color:' + TESTO_SU_ARANCIO, dich)
        sistema_blocco.contati.append(('arancio', sel.strip()[:44]))

    if not any(e in basso for e in SELETTORI_ESCLUSI):
        # (4 e 7) ogni colore di testo troppo chiaro per un fondo chiaro
        dich, cambi = schiarisci_o_lascia(dich)
        if cambi:
            sistema_blocco.contati.append(('colore', sel.strip()[:44]))

    return sel + '{' + dich + '}'


def lavora_css(testo):
    sistema_blocco.contati = []
    testo, n_verde = re.subn(VERDE_VECCHIO, VERDE_NUOVO, testo, flags=re.I)
    testo = BLOCCO.sub(sistema_blocco, testo)
    return testo, n_verde, list(sistema_blocco.contati)


def sistema_inline(m):
    """Un attributo style= scritto sul singolo elemento (regole 3, 4, 7)."""
    apri, dich, chiudi = m.group(1), m.group(2), m.group(3)
    if fondo_scuro(dich):
        # unica eccezione: il fondo arancione, che e' chiaro ma vuole testo scuro
        if not re.search(r'background(?:-color)?:\s*#' + ARANCIO, dich, re.I):
            return m.group(0)
    prima = dich
    if re.search(r'background(?:-color)?:\s*#' + ARANCIO, dich, re.I) and BIANCO.search(dich):
        dich = BIANCO.sub('color:' + TESTO_SU_ARANCIO, dich)          # (3)
    else:
        dich, _cambi = schiarisci_o_lascia(dich)                      # (4 e 7)
    if dich != prima:
        sistema_inline.contati += 1
    return apri + dich + chiudi


# style="..."  oppure  style=...  (il nostro HTML e' minificato, spesso senza virgolette)
INLINE = re.compile(r'(style=")([^"]*)(")|(style=)([^\s">]+)()')


def sistema_inline_qualsiasi(m):
    if m.group(1) is not None:
        return sistema_inline(re.match(r'(style=")([^"]*)(")', m.group(0)))
    return sistema_inline(re.match(r'(style=)([^\s">]+)()', m.group(0)))


def lavora_html(testo):
    """Sul documento intero: stili inline, verde, Facebook. Il footer si salta."""
    taglio = testo.find('<footer')
    corpo, coda = (testo[:taglio], testo[taglio:]) if taglio > 0 else (testo, '')

    sistema_inline.contati = 0
    corpo = INLINE.sub(sistema_inline_qualsiasi, corpo)
    n_inline = sistema_inline.contati

    # (5) l'ambra scura scritta a mano dentro il footer, su fondo #1a0d00
    coda, n_ambra = re.subn(r'color:\s*#9c5b00\b', 'color:' + AMBRA_FOOTER_NUOVA, coda, flags=re.I)

    testo = corpo + coda
    testo, n_verde = re.subn(VERDE_VECCHIO, VERDE_NUOVO, testo, flags=re.I)   # (1)
    testo, n_fb = re.subn(FACEBOOK_VECCHIO, FACEBOOK_NUOVO, testo, flags=re.I)  # (6)
    return testo, n_inline, n_ambra, n_verde, n_fb


def main():
    applica = '--applica' in sys.argv
    conti = dict(css_arancio=0, css_colore=0,
                 inline=0, ambra=0, verde=0, facebook=0)
    selettori, file_toccati = [], 0

    for perc in sorted(glob.glob(BASE + 'css/*.css') + glob.glob(BASE + '*.html')):
        originale = open(perc, encoding='utf-8').read()

        if perc.endswith('.html'):
            nuovo = originale
            pezzi = []
            for m in re.finditer(r'(<style[^>]*>)(.*?)(</style>)', originale, re.S):
                corretto, _, sel = lavora_css(m.group(2))
                pezzi.append((m.start(2), m.end(2), corretto))
                selettori += sel
                for tipo, _s in sel:
                    conti['css_' + tipo] += 1
            for inizio, fine, corretto in reversed(pezzi):
                nuovo = nuovo[:inizio] + corretto + nuovo[fine:]
            nuovo, n_in, n_am, n_ve, n_fb = lavora_html(nuovo)
            conti['inline'] += n_in
            conti['ambra'] += n_am
            conti['verde'] += n_ve
            conti['facebook'] += n_fb
        else:
            nuovo, n_ve, sel = lavora_css(originale)
            conti['verde'] += n_ve
            selettori += sel

        if nuovo != originale:
            file_toccati += 1
            if applica:
                open(perc, 'w', encoding='utf-8').write(nuovo)

    print(f"1. verde  #1a8f3c -> {VERDE_NUOVO}          {conti['verde']:4d}")
    print(f"2. bianco -> {TESTO_SU_ARANCIO} su arancio (CSS)  {conti['css_arancio']:4d} regole")
    print(f"3. stili inline corretti                {conti['inline']:4d} elementi")
    print(f"4+7. colori troppo chiari scuriti (CSS) {conti['css_colore']:4d} regole")
    print(f"5. ambra footer -> {AMBRA_FOOTER_NUOVA}        {conti['ambra']:4d}")
    print(f"6. facebook -> {FACEBOOK_NUOVO}           {conti['facebook']:4d}")
    print(f"\nfile toccati: {file_toccati}")
    if selettori:
        esempi = sorted({s for _t, s in selettori})[:6]
        print('  regole cambiate, ad esempio: ' + ', '.join(esempi))
    if not applica:
        print('\n(prova a vuoto: rilancia con --applica)')


if __name__ == '__main__':
    main()
