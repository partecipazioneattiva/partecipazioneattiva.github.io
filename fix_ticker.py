with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

vecchio = 'background:#c0392b;color:#fff;text-align:center;padding:10px 24px;font-family:montserrat,sans-serif;font-size:.82em;font-weight:700;letter-spacing:.5px;z-index:1000">✊ <strong>BATTAGLIA IN CORSO:</strong> RC Auto — basta discriminazioni territoriali. Napoli guida la lotta.'

if vecchio in content:
    nuovo = 'background:#c0392b;color:#fff;padding:9px 0;font-family:montserrat,sans-serif;font-size:.82em;font-weight:700;letter-spacing:.5px;z-index:1000;overflow:hidden;white-space:nowrap"><div style="display:inline-block;animation:ticker 30s linear infinite">✊ <strong>BATTAGLIA IN CORSO:</strong> RC Auto — basta discriminazioni territoriali &nbsp;&nbsp;•&nbsp;&nbsp; ✊ <strong>BATTAGLIA IN CORSO:</strong> Salute in Vendita — il collasso della sanità pubblica &nbsp;&nbsp;•&nbsp;&nbsp; ✊ <strong>BATTAGLIA IN CORSO:</strong> RC Auto — basta discriminazioni territoriali &nbsp;&nbsp;•&nbsp;&nbsp; ✊ <strong>BATTAGLIA IN CORSO:</strong> Salute in Vendita — il collasso della sanità pubblica &nbsp;&nbsp;•&nbsp;&nbsp;</div><style>@keyframes ticker{0%{transform:translateX(100vw)}100%{transform:translateX(-100%)}}</style'
    content = content.replace(vecchio, nuovo, 1)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK - ticker aggiunto")
else:
    print("ERRORE - testo non trovato")
    # Stampa il contesto per debug
    idx = content.find('BATTAGLIA IN CORSO')
    if idx > 0:
        print(repr(content[idx-80:idx+120]))
