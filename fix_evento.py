import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;">'

banner = '''<div style="background:rgba(255,255,255,0.10);border-left:3px solid #ffd580;border-radius:8px;padding:9px 14px;margin-bottom:14px;display:flex;align-items:center;gap:10px;"><span style="font-size:.7em;background:#e8900a;color:#fff;font-weight:900;letter-spacing:1px;text-transform:uppercase;padding:3px 9px;border-radius:50px;white-space:nowrap;">&#128197; Prossimo evento</span><span style="font-size:.78em;color:#fff;font-weight:600;line-height:1.3;">Presentazione pubblica a <strong style="color:#ffd580;">Bagnoli, Napoli</strong> &mdash; data da confermare, seguici su Facebook</span></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;">'''

new_content = content.replace(old, banner, 1)

if new_content == content:
    print('ERRORE: stringa non trovata')
else:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('OK: banner inserito')
