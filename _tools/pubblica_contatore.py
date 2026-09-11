"""Pubblica il commit appena fatto da uno dei quattro script dei contatori.

I contatori (Calabria, Fuori l'Italia dalla guerra, Voto LibEguale, referendum)
scrivono tutti dentro index.html, che e' minificata su UNA riga sola. Quando
due partono nello stesso secondo — e succede di continuo: lo stesso Google
Apps Script richiama fuori-guerra e voto-libeguale insieme ogni 5 minuti — il
secondo si vede respingere il push, e un `git pull --rebase` su quella riga
unica va SEMPRE in conflitto, anche se i numeri stanno in punti diversi.

🟥 Il guasto dell'11/09/2026. Il vecchio rimedio era «abbandono il giro, il
prossimo riparte da capo». Ma il prossimo giro ripartiva insieme al gemello, e
perdeva di nuovo: Voto LibEguale e' fallito 15 volte di fila (10:11-11:21 UTC),
e per 70 minuti le sue firme non si sono aggiornate, con una email di errore a
Fernando ogni 5 minuti.

🟩 Adesso chi perde la corsa non tenta di fondere niente: butta il proprio
commit, prende la home appena pubblicata dall'altro e RIFA' TUTTO DA CAPO
(rilegge il numero, riscrive, ricommitta). Cosi' nel file finale ci sono i
numeri di tutti e due. Al massimo 3 giri, poi si ferma con errore.

⛔ Il riallineamento cancella le modifiche locali non salvate: lo fa SOLO sui
server di GitHub (variabile GITHUB_ACTIONS). Lanciato sul Mac, se il push e'
respinto si ferma e dice di fare `git pull`.
"""
import os
import random
import subprocess
import sys
import time

MASSIMO_GIRI = 3


def pubblica():
    if subprocess.run(['git', 'push', '-q', 'origin', 'main']).returncode == 0:
        return

    giro = int(os.environ.get('CONTATORE_GIRO', '1'))
    if giro >= MASSIMO_GIRI:
        print(f'  ⛔ push respinto {giro} volte di fila: guarda a mano', flush=True)
        sys.exit(1)
    if not os.environ.get('GITHUB_ACTIONS'):
        print('  ⛔ push respinto: qualcun altro ha pubblicato nel frattempo. Qui sul Mac '
              'non riallineo da solo (cancellerei le modifiche non salvate): '
              'fai git pull e rilancia', flush=True)
        sys.exit(1)

    print(f'  · push respinto: un altro contatore ha pubblicato nello stesso momento. '
          f'Riparto dalla home appena pubblicata e rifaccio il conto '
          f'(giro {giro + 1} di {MASSIMO_GIRI})', flush=True)
    subprocess.run(['git', 'fetch', '-q', 'origin', 'main'], check=True)
    subprocess.run(['git', 'reset', '-q', '--hard', 'FETCH_HEAD'], check=True)
    # i due gemelli sono partiti nello stesso secondo: un'attesa a caso evita
    # che si ritrovino di nuovo appaiati
    time.sleep(random.uniform(2, 8))
    env = dict(os.environ, CONTATORE_GIRO=str(giro + 1))
    # percorso assoluto dello script chiamante: gli script fanno os.chdir(BASE),
    # e sys.argv[0] relativo non varrebbe piu'
    script = os.path.abspath(sys.modules['__main__'].__file__)
    os.execve(sys.executable, [sys.executable, script] + sys.argv[1:], env)
