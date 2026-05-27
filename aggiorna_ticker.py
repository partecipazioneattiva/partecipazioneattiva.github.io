#!/usr/bin/env python3
"""
Script per aggiornare il ticker dell'homepage usando il marker data-pa-section="ticker"
Uso: python3 aggiorna_ticker.py "nuovo testo del ticker"
"""

import re
import sys
from pathlib import Path

def aggiorna_ticker(nuovo_testo):
    file_path = Path("/Users/osxssd/Desktop/partecipazioneattiva/index.html")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Cerca il div con data-pa-section="ticker"
    pattern = r'(<div[^>]*data-pa-section="ticker"[^>]*>)(.*?)(</div>)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ ERRORE: Ticker non trovato (data-pa-section='ticker')")
        return False
    
    # Sostituisce il contenuto interno
    nuovo_ticker = match.group(1) + nuovo_testo + match.group(3)
    content = content[:match.start()] + nuovo_ticker + content[match.end():]
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Ticker aggiornato con successo")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 aggiorna_ticker.py \"nuovo testo\"")
        sys.exit(1)
    
    nuovo_testo = sys.argv[1]
    aggiorna_ticker(nuovo_testo)
