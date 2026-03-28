content = open('index.html','r').read()

# 1. Cambia testo bottone
old1 = 'Iscriviti ora</a>'
new1 = 'Iscriviti — è gratis</a>'
if old1 in content:
    content = content.replace(old1, new1)
    print('✅ Bottone aggiornato')
else:
    print('❌ Bottone NON trovato')

# 2. Aggiungi contatori numerici dopo i bottoni hero
old2 = '        <a href="#chisiamo" style="background:transparent;color:#fff;padding:13px 30px;border-radius:50px;text-decoration:none;font-weight:700;font-size:.9em;border:2px solid rgba(255,255,255,.7);">Chi siamo</a>'
new2 = '''        <a href="#chisiamo" style="background:transparent;color:#fff;padding:13px 30px;border-radius:50px;text-decoration:none;font-weight:700;font-size:.9em;border:2px solid rgba(255,255,255,.7);">Chi siamo</a>
      </div>
      <div style="display:flex;gap:32px;margin-top:36px;flex-wrap:wrap;">
        <div style="text-align:center;">
          <div style="font-size:2em;font-weight:900;color:#fff;line-height:1;">2.680</div>
          <div style="font-size:.72em;color:rgba(255,255,255,.75);text-transform:uppercase;letter-spacing:1px;margin-top:4px;">Follower</div>
        </div>
        <div style="width:1px;background:rgba(255,255,255,.25);"></div>
        <div style="text-align:center;">
          <div style="font-size:2em;font-weight:900;color:#fff;line-height:1;">4</div>
          <div style="font-size:.72em;color:rgba(255,255,255,.75);text-transform:uppercase;letter-spacing:1px;margin-top:4px;">Territori</div>
        </div>
        <div style="width:1px;background:rgba(255,255,255,.25);"></div>
        <div style="text-align:center;">
          <div style="font-size:2em;font-weight:900;color:#fff;line-height:1;">9</div>
          <div style="font-size:.72em;color:rgba(255,255,255,.75);text-transform:uppercase;letter-spacing:1px;margin-top:4px;">Direttivo</div>
        </div>
        <div style="width:1px;background:rgba(255,255,255,.25);"></div>
        <div style="text-align:center;">
          <div style="font-size:2em;font-weight:900;color:#fff;line-height:1;">250+</div>
          <div style="font-size:.72em;color:rgba(255,255,255,.75);text-transform:uppercase;letter-spacing:1px;margin-top:4px;">Gruppo Napoli</div>
        </div>
      </div>
      <div style="display:none;">'''

if old2 in content:
    content = content.replace(old2, new2)
    print('✅ Contatori aggiunti')
else:
    print('❌ Contatori: testo NON trovato')

open('index.html','w').write(content)
