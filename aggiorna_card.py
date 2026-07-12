#!/usr/bin/env python3
"""
Script per aggiungere/modificare card nell'homepage usando marker.
Uso: python3 aggiorna_card.py --aggiungi "URL" "titolo" "autore" "data" "foto"
"""

import re
import sys
from pathlib import Path

def aggiungi_card(url, titolo, autore, data, foto, ruolo):
    file_path = Path("/Users/luigia/SITO-PA/index.html")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Cerca la prima card con data-pa-section="homepage-card" (per posizionarsi)
    # le card con data-pa-pin restano sempre in cima: si inserisce dopo di esse
    pattern = r'<a(?![^>]*data-pa-pin)[^>]*data-pa-section="homepage-card"[^>]*>.*?</a>'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ ERRORE: Nessuna card trovata con data-pa-section='homepage-card'")
        return False
    
    # Costruisce la nuova card (semplificata, da adattare)
    nuova_card = f'''<a href="{url}" data-pa-section="homepage-card" style="display:flex;align-items:stretch;border-radius:16px;overflow:hidden;background:rgba(255,255,255,.12);border:2px solid #ffd580;text-decoration:none;margin-bottom:14px;min-height:180px">
      <img src="{foto}" alt="{autore}" style="width:130px;min-height:180px;object-fit:cover;object-position:top center;flex-shrink:0;display:block">
      <div style="padding:14px 16px;display:flex;flex-direction:column;justify-content:center">
        <div style="display:inline-block;background:#ffd580;color:#8a4e00;font-size:.55em;font-weight:900;letter-spacing:1px;text-transform:uppercase;padding:3px 10px;border-radius:50px;margin-bottom:8px">{data}</div>
        <div style="font-size:.68em;color:rgba(255,255,255,.7);margin-bottom:6px">{autore} — {ruolo}</div>
        <div style="font-family:merriweather,serif;font-size:.88em;color:#fff;font-weight:700;line-height:1.4;margin-bottom:10px">{titolo}</div>
        <div style="font-size:.75em;color:#ffd580;font-weight:700">Leggi l'articolo →</div>
      </div>
    </a>'''
    
    # Inserisce la nuova card PRIMA della prima card esistente
    content = content[:match.start()] + nuova_card + "\n" + content[match.start():]
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Card aggiunta con successo")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Uso: python3 aggiorna_card.py --aggiungi URL titolo autore data foto ruolo")
        sys.exit(1)
    
    if sys.argv[1] == "--aggiungi":
        aggiungi_card(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
