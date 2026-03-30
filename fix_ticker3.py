with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

testo = '✊ <strong>BATTAGLIA IN CORSO:</strong> RC Auto — basta discriminazioni territoriali &nbsp;&nbsp;•&nbsp;&nbsp; ✊ <strong>BATTAGLIA IN CORSO:</strong> Salute in Vendita — il collasso della sanità pubblica &nbsp;&nbsp;•&nbsp;&nbsp; 📰 <strong>SEGUI:</strong> Stabilicum — la nuova legge elettorale &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'

nuovo = '<div style="background:#c0392b;color:#fff;padding:9px 0;font-family:montserrat,sans-serif;font-size:.82em;font-weight:700;letter-spacing:.5px;z-index:1000;overflow:hidden;white-space:nowrap"><div style="display:flex;width:max-content;animation:ticker 55s linear infinite"><div style="display:inline-block;white-space:nowrap;padding-right:60px">' + testo + '</div><div style="display:inline-block;white-space:nowrap;padding-right:60px" aria-hidden="true">' + testo + '</div><div style="display:inline-block;white-space:nowrap;padding-right:60px" aria-hidden="true">' + testo + '</div></div><style>@keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-33.333%)}}</style></div>'

import re
old_pattern = r'<div style="background:#c0392b;color:#fff;padding:9px 0.*?</style></div>'
result = re.sub(old_pattern, nuovo, content, flags=re.DOTALL)

if result != content:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(result)
    print("OK - ticker sostituito")
else:
    print("ERRORE - pattern non trovato")
