#!/usr/bin/env python3
"""Banco di prova del motore di PensAttivo: replica ESATTA del BM25 che gira
nel browser (assistente/pensattivo.js), misurata su _tools/valuta/domande_prova.json.

Perche' una replica e non una misura sul browser: qui si provano decine di
varianti dell'indice in pochi secondi. La replica e' fedele riga per riga
(stessa pulizia del testo, stesso k1/b, stessa regola delle esche): se il
numero qui cambia, cambia anche nel browser. Verificato il 26/07/2026.

VALUTARE SEMPRE A recall@1: con 3 candidati il caso azzecca il 25%.

    python3 _tools/valuta/prova_motore.py            # indice attuale
    python3 _tools/valuta/prova_motore.py --dettagli # elenca gli errori
    python3 _tools/valuta/prova_motore.py --faq FILE # prova un altro _dati/faq.json
"""
import json
import math
import re
import sys
import unicodedata

BASE = '/Users/osxssd/Desktop/ARCHIVIO GENERALE/LAVORI/partecipazioneattiva/'
K1, B = 1.5, 0.75


def pulisci(t):
    """Replica di pulisci() in pensattivo.js: minuscole, via gli accenti, via
    gli articoli elisi, solo [a-z0-9]+.

    Le elisioni vanno tolte PRIMA di spezzare le parole: "all'estero" darebbe
    il pezzo "all", che nel nostro corpus e' rarissimo e quindi pesantissimo
    (BM25 pesa le parole rare). Misurato: "quanto si paga all'anno" finiva su
    "i dati vanno all'estero". In italiano una parola corta prima
    dell'apostrofo e' sempre un articolo o una preposizione elisa."""
    t = unicodedata.normalize('NFD', (t or '').lower())
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    t = re.sub(r"\b[a-z]{1,5}['’]", ' ', t)
    return re.findall(r'[a-z0-9]+', t)


def parole(t):
    return [p for p in pulisci(t) if len(p) > 2]


class Indice:
    def __init__(self, frasi, righe):
        self.righe = righe
        self.frasi = frasi
        docs = [parole(f) for f in frasi]
        self.tf, self.df, self.lung = [], {}, []
        for d in docs:
            self.lung.append(len(d))
            c = {}
            for p in d:
                c[p] = c.get(p, 0) + 1
            self.tf.append(c)
            for p in c:
                self.df[p] = self.df.get(p, 0) + 1
        self.n = len(docs)
        self.media = (sum(self.lung) / self.n) if self.n else 1

    def idf(self, p):
        n = self.df.get(p, 0)
        return math.log(1 + (self.n - n + 0.5) / (n + 0.5))

    def cerca(self, dom):
        """Ritorna (id_migliore o None, punteggi per id). None = rifiutato."""
        qt = parole(dom)
        if not qt:
            return None, {}
        best, esca, top_faq = {}, 0.0, 0.0
        for i in range(self.n):
            s = 0.0
            for p in qt:
                f = self.tf[i].get(p)
                if not f:
                    continue
                s += self.idf(p) * f * (K1 + 1) / (
                    f + K1 * (1 - B + B * self.lung[i] / self.media))
            if s <= 0:
                continue
            rid = self.righe[i]
            if rid == '_esca':
                esca = max(esca, s)
                continue
            best[rid] = max(best.get(rid, 0.0), s)
            top_faq = max(top_faq, s)
        if not top_faq or esca >= top_faq:
            return None, best
        vinc = max(best, key=lambda k: best[k])
        return vinc, best


def costruisci(faq, esche, campi=('domanda', 'varianti'), auto=None):
    frasi, righe = [], []
    for f in faq:
        testi = []
        if 'domanda' in campi:
            testi.append(f['domanda'])
        if 'varianti' in campi:
            testi += f.get('varianti', [])
        if auto:
            testi += auto.get(f['id'], [])
        for t in testi:
            frasi.append(t)
            righe.append(f['id'])
    for e in esche:
        frasi.append(e)
        righe.append('_esca')
    return Indice(frasi, righe)


def valuta(indice, prove, dettagli=False):
    tema_ok = tema_tot = fuori_ok = fuori_tot = 0
    errori = []
    for p in prove:
        vinc, punteggi = indice.cerca(p['q'])
        atteso = p.get('atteso')
        if atteso is None:
            fuori_tot += 1
            if vinc is None:
                fuori_ok += 1
            else:
                errori.append(('FUORI TEMA accettata', p['q'], vinc, '-'))
        else:
            tema_tot += 1
            if vinc == atteso:
                tema_ok += 1
            else:
                errori.append(('sbagliata', p['q'], vinc or 'RIFIUTATA', atteso))
    if dettagli:
        for tipo, q, avuto, atteso in errori:
            print(f'  [{tipo}] "{q}"\n      dato: {avuto}   atteso: {atteso}')
    return tema_ok, tema_tot, fuori_ok, fuori_tot


def incrociata(indice, frasi, faq):
    """Misura indipendente dal banco: ogni frase dell'indice, TOLTA da se'
    stessa, deve ritrovare la propria FAQ. 900 punti di misura invece di 38, e
    non c'e' modo di imbrogliare: le domande non le ho scelte io.

    Serve a vedere le FAQ che si rubano le domande a vicenda, che e' il modo in
    cui l'allargamento dell'indice puo' peggiorare le cose senza che il banco
    da 38 domande se ne accorga."""
    nome = {f['id']: f['domanda'] for f in faq}
    sbagli, rubati = {}, {}
    tot = ok = 0
    for i, testo in enumerate(frasi):
        mio = indice.righe[i]
        if mio == '_esca':
            continue
        tot += 1
        qt = parole(testo)
        best = {}
        for j in range(indice.n):
            if j == i:
                continue
            s = 0.0
            for p in qt:
                f = indice.tf[j].get(p)
                if not f:
                    continue
                s += indice.idf(p) * f * (K1 + 1) / (
                    f + K1 * (1 - B + B * indice.lung[j] / indice.media))
            if s > 0:
                rid = indice.righe[j]
                best[rid] = max(best.get(rid, 0.0), s)
        vinc = max(best, key=lambda k: best[k]) if best else None
        if vinc == mio:
            ok += 1
        else:
            sbagli[mio] = sbagli.get(mio, 0) + 1
            if vinc:
                rubati[vinc] = rubati.get(vinc, 0) + 1
    print(f'\nProva incrociata: {ok}/{tot} frasi ritrovano la propria FAQ '
          f'({100*ok/tot:.0f}%)')
    print('\nFAQ che si fanno rubare piu\' domande:')
    for k, v in sorted(sbagli.items(), key=lambda x: -x[1])[:8]:
        print(f'  {v:3d} perse   {k:24s} {nome.get(k, "")[:44]}')
    print('\nFAQ che rubano di piu\':')
    for k, v in sorted(rubati.items(), key=lambda x: -x[1])[:8]:
        et = 'ESCA' if k == '_esca' else nome.get(k, '')[:44]
        print(f'  {v:3d} rubate  {k:24s} {et}')
    return ok, tot


def riga(nome, r):
    t_ok, t_tot, f_ok, f_tot = r
    tot, su = t_ok + f_ok, t_tot + f_tot
    print(f'{nome:38s} in tema {t_ok:2d}/{t_tot}   fuori tema {f_ok}/{f_tot}   '
          f'TOTALE {tot}/{su} ({100*tot/su:.0f}%)')


def main():
    perc = BASE + '_dati/faq.json'
    if '--faq' in sys.argv:
        perc = sys.argv[sys.argv.index('--faq') + 1]
    dati = json.load(open(perc, encoding='utf-8'))
    esche = json.load(open(BASE + '_dati/esche.json', encoding='utf-8'))['esche']
    prove = json.load(open(BASE + '_tools/valuta/domande_prova.json',
                           encoding='utf-8'))['prove']
    faq = [f for f in dati['faq'] if f.get('approvato')]

    auto = None
    if '--auto' in sys.argv:
        auto = json.load(open(BASE + '_dati/varianti_auto.json',
                              encoding='utf-8'))['varianti']

    ind = costruisci(faq, esche, auto=auto)
    print(f'{len(faq)} FAQ · {ind.n} frasi indicizzate ({len(esche)} esche) · '
          f'{len(prove)} domande di prova\n')
    nome = 'BM25 + varianti generate' if auto else 'BM25 (domanda + varianti)'
    riga(nome, valuta(ind, prove, '--dettagli' in sys.argv))
    if '--solo-domande' in sys.argv:
        riga('BM25 (solo domanda)',
             valuta(costruisci(faq, esche, ('domanda',)), prove))
    if '--incrociata' in sys.argv:
        incrociata(ind, ind.frasi, faq)


if __name__ == '__main__':
    main()
