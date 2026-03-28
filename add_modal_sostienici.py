import re

pagine = ['index.html', 'napoli.html', 'parlero.html', 'territori.html', 'organigramma.html', 'battaglie.html', 'privacy.html']

modal_html = '''
<!-- MODAL SOSTIENICI -->
<div id="modal-sostienici" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:9999;align-items:center;justify-content:center;">
  <div style="background:#fff;border-radius:16px;padding:36px;max-width:480px;width:90%;position:relative;box-shadow:0 8px 40px rgba(0,0,0,0.2);">
    <button onclick="document.getElementById('modal-sostienici').style.display='none'" style="position:absolute;top:14px;right:18px;background:none;border:none;font-size:1.4em;cursor:pointer;color:#888;">✕</button>
    <div style="text-align:center;margin-bottom:20px;">
      <img src="LOGO-PA.png" alt="Logo PA" style="height:60px;">
    </div>
    <h2 style="font-family:'Merriweather',serif;color:#8a4e00;font-size:1.2em;margin-bottom:6px;text-align:center;">Sostieni Partecipazione Attiva</h2>
    <p style="color:#666;font-size:.85em;text-align:center;margin-bottom:24px;">Ogni contributo ci aiuta a portare avanti le nostre battaglie.</p>

    <div style="background:#fff8ee;border-radius:12px;padding:18px;margin-bottom:16px;border:1.5px solid #e8900a;">
      <div style="font-weight:700;color:#8a4e00;font-size:.85em;margin-bottom:10px;">🏦 Bonifico Bancario</div>
      <div style="font-size:.8em;color:#444;line-height:1.8;">
        <strong>Intestato a:</strong> Daniele Tandura (Tesoriere P.A.)<br>
        <strong>IBAN:</strong> IT70A0366901600557449712670<br>
        <strong>SWIFT:</strong> REVOITM2<br>
        <strong>Causale:</strong> Iscrizione/Rinnovo/Donazione progetto politico
      </div>
    </div>

    <a href="https://www.paypal.com/donate/?hosted_button_id=MWQLS8ECREKCQ" target="_blank" rel="noopener noreferrer" style="display:block;background:#009cde;color:#fff;text-align:center;padding:13px;border-radius:50px;text-decoration:none;font-weight:700;font-size:.92em;margin-bottom:10px;">💙 Dona con PayPal</a>
    <p style="font-size:.72em;color:#999;text-align:center;">Causale: Iscrizione/Rinnovo/Donazione progetto politico</p>
  </div>
</div>
<script>
function apriSostienici(e){e.preventDefault();var m=document.getElementById('modal-sostienici');m.style.display='flex';}
document.addEventListener('click',function(e){if(e.target===document.getElementById('modal-sostienici'))document.getElementById('modal-sostienici').style.display='none';});
</script>
'''

for filename in pagine:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Sostituisci bottone Sostienici desktop (navbar)
    old1 = 'href="mailto:partecipazioneattiva21@gmail.com?subject=Donazione" class="btn-sost"'
    new1 = 'href="#" onclick="apriSostienici(event)" class="btn-sost"'

    # Sostituisci bottone Sostienici mobile menu
    old2 = 'href="mailto:partecipazioneattiva21@gmail.com?subject=Donazione" onclick="chiudi()" style="background:#e8900a;color:#fff;text-align:center;font-weight:900;"'
    new2 = 'href="#" onclick="chiudi();apriSostienici(event)" style="background:#e8900a;color:#fff;text-align:center;font-weight:900;"'

    modified = False
    if old1 in content:
        content = content.replace(old1, new1)
        modified = True

    if old2 in content:
        content = content.replace(old2, new2)
        modified = True

    # Aggiungi il modal prima di </body>
    if '</body>' in content and 'modal-sostienici' not in content:
        content = content.replace('</body>', modal_html + '\n</body>')
        modified = True

    if modified:
        # Fix percorso logo per pagine che non sono in root
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK: {filename}')
    else:
        print(f'SKIP: {filename}')

print('FATTO')
