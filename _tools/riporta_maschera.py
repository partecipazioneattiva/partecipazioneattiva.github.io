#!/usr/bin/env python3
"""Riporta la sagoma di un ritaglio PICCOLO sull'immagine GRANDE originale.

    python3 _tools/riporta_maschera.py anteprima_ritagliata.png originale.png uscita.png

⭐ 12 agosto 2026. Nasce da un caso concreto: il fondo di un ritratto e' stato
tolto con remove.bg, ma il sito senza abbonamento restituisce solo
l'**anteprima**, a un quarto dei pixel. Il ritaglio e' buono, i pixel no.

🟩 L'idea: della versione piccola non serve l'immagine, serve solo il **canale
alfa** — cioe' dove finisce la persona. Quello si ingrandisce e si applica
all'originale a piena risoluzione. Il contorno resta quello deciso dal servizio
buono, i pixel restano quelli veri. Non si inventa niente.

⛔ Funziona solo se le due immagini hanno la STESSA inquadratura: si controlla
il rapporto fra i lati e ci si ferma se non combacia, altrimenti la sagoma
finisce spostata rispetto al volto.

🟨 Il bordo ingrandito e' morbido. Si irrobustisce con una soglia e una
sfumatura di un paio di pixel: senza, resta un alone chiaro del vecchio fondo;
con una soglia troppo dura, il contorno diventa seghettato.
"""
import argparse
import sys

from PIL import Image, ImageFilter

TOLLERANZA = 0.02   # scarto ammesso fra i rapporti d'aspetto
SOGLIA = 128        # sopra = persona, sotto = fondo
SFUMATURA = 1.2     # px di sfumatura sul bordo, contro l'alone e la scaletta


def solo_la_persona(alfa):
    """Tiene solo la macchia piu' grande dell'alfa e butta i pezzi staccati.

    ⛔ 12 agosto 2026: su un ritratto scontornato era rimasto, in basso a
    sinistra, un lembo della camicia di CHI GLI STAVA ACCANTO. Il servizio di
    scontorno riconosce «persona», e li' di persone ce n'erano due.
    Un pezzo staccato dalla figura non e' mai roba nostra: si toglie.

    Riempimento a partire dai pixel pieni, con una pila esplicita: niente
    ricorsione (si supera il limite di Python su un'immagine grande) e niente
    scipy, che su questo Mac non c'e'.
    """
    L, A = alfa.size
    px = list(alfa.getdata())
    visto = bytearray(L * A)
    migliore, quanti_migliore = None, 0
    for partenza in range(L * A):
        if visto[partenza] or px[partenza] < 128:
            continue
        pila, macchia = [partenza], []
        visto[partenza] = 1
        while pila:
            i = pila.pop()
            macchia.append(i)
            x, y = i % L, i // L
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < L and 0 <= ny < A:
                    j = ny * L + nx
                    if not visto[j] and px[j] >= 128:
                        visto[j] = 1
                        pila.append(j)
        if len(macchia) > quanti_migliore:
            migliore, quanti_migliore = macchia, len(macchia)
    if migliore is None:
        return alfa, 0
    tenuti = bytearray(L * A)
    for i in migliore:
        tenuti[i] = 1
    buttati = sum(1 for i in range(L * A) if px[i] >= 128 and not tenuti[i])
    nuovo = Image.new("L", (L, A), 0)
    nuovo.putdata([px[i] if tenuti[i] else 0 for i in range(L * A)])
    return nuovo, buttati


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ritaglio", help="l'immagine piccola gia' scontornata (con alfa)")
    p.add_argument("originale", help="l'immagine grande, col fondo")
    p.add_argument("uscita")
    p.add_argument("--niente-soglia", action="store_true", dest="niente_soglia",
                   help="applica l'alfa ingrandito com'e', senza irrobustire il bordo")
    p.add_argument("--solo-la-persona", action="store_true", dest="solo_persona",
                   help="butta i pezzi STACCATI dalla figura: il lembo della "
                        "camicia di chi le stava accanto, un ramo, un oggetto. "
                        "Tiene solo la macchia piu' grande")
    a = p.parse_args()

    piccola = Image.open(a.ritaglio).convert("RGBA")
    grande = Image.open(a.originale).convert("RGBA")

    if "A" not in piccola.getbands():
        sys.exit("⛔ il ritaglio non ha il canale alfa: non e' scontornato")
    rp = piccola.width / piccola.height
    rg = grande.width / grande.height
    if abs(rp - rg) > TOLLERANZA:
        sys.exit(f"⛔ inquadrature diverse: {piccola.size} e {grande.size} "
                 f"(rapporti {rp:.3f} e {rg:.3f}). La sagoma finirebbe spostata.")

    alfa = piccola.split()[3].resize(grande.size, Image.LANCZOS)
    if not a.niente_soglia:
        alfa = alfa.point(lambda v: 255 if v > SOGLIA else 0)
    if a.solo_persona:
        alfa, buttati = solo_la_persona(alfa)
        print(f"     pezzi staccati buttati: {buttati} px")
    if not a.niente_soglia:
        alfa = alfa.filter(ImageFilter.GaussianBlur(SFUMATURA))

    fuori = grande.copy()
    fuori.putalpha(alfa)
    fuori.save(a.uscita)

    pieni = sum(1 for v in alfa.getdata() if v > 250)
    vuoti = sum(1 for v in alfa.getdata() if v < 5)
    print(f"  ✅ {a.uscita}  {fuori.size}")
    print(f"     sagoma: {pieni} px pieni, {vuoti} vuoti, "
          f"{alfa.width * alfa.height - pieni - vuoti} di sfumatura")
    print(f"     ingrandimento della sagoma: ×{grande.width / piccola.width:.2f}")


if __name__ == "__main__":
    main()
