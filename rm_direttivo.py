with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        <div style="width:1px;background:rgba(255,255,255,.25);"></div>
        <div style="text-align:center;">
          <div style="font-size:2em;font-weight:900;color:#fff;line-height:1;">7</div>
          <div style="font-size:.72em;color:rgba(255,255,255,.75);text-transform:uppercase;letter-spacing:1px;margin-top:4px;">Direttivo</div>
        </div>
        <div style="width:1px;background:rgba(255,255,255,.25);"></div>
        <div style="text-align:center;">
          <div style="font-size:2em;font-weight:900;color:#fff;line-height:1;">250+</div>'''

new = '''        <div style="width:1px;background:rgba(255,255,255,.25);"></div>
        <div style="text-align:center;">
          <div style="font-size:2em;font-weight:900;color:#fff;line-height:1;">250+</div>'''

if old not in content:
    print('ERRORE: stringa non trovata')
else:
    content = content.replace(old, new, 1)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: contatore Direttivo rimosso')
