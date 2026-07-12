from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

# --- 1) CSS ---
css_anchor = ".vuoto{text-align:center;color:#8a8175;padding:24px;font-size:.95em}"
css_new = (".vuoto{text-align:center;color:#8a8175;padding:24px;font-size:.95em}\n"
".bcont{margin-top:10px;background:#fff3e0;color:var(--br);border:1px solid var(--bd);border-radius:50px;"
"padding:6px 15px;font-family:Montserrat,sans-serif;font-size:.78em;font-weight:700;cursor:pointer}\n"
".bcont:hover{background:var(--ar);color:#fff;border-color:var(--ar)}\n"
"#mod{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:2000;display:none;align-items:center;justify-content:center;padding:18px}\n"
"#mod.on{display:flex}\n"
"#mod .in{background:#fff;border-radius:14px;max-width:520px;width:100%;padding:26px;max-height:90vh;overflow-y:auto}\n"
"#mod h3{font-family:Montserrat,sans-serif;color:var(--br);margin:0 0 6px}\n"
"#mod .chiudi{float:right;background:0;border:0;font-size:1.5em;cursor:pointer;color:#8a8175;line-height:1}")

if ".bcont{" in t:
    print("CSS gia' presente")
elif css_anchor in t:
    t = t.replace(css_anchor, css_new, 1)
    print("CSS bottone + modale aggiunto")
else:
    raise SystemExit("STOP: ancora CSS non trovata")

# --- 2) bottone dentro la scheda ---
old = ("    + (r.sito_web?'<div style=\"margin-top:8px\"><a href=\"'+esc(r.sito_web)+'\" target=\"_blank\" "
       "rel=\"noopener nofollow\" style=\"font-size:.85em\">'+esc(r.sito_web)+'</a></div>':'')\n    + '</div>';")
new = ("    + (r.sito_web?'<div style=\"margin-top:8px\"><a href=\"'+esc(r.sito_web)+'\" target=\"_blank\" "
       "rel=\"noopener nofollow\" style=\"font-size:.85em\">'+esc(r.sito_web)+'</a></div>':'')\n"
       "    + '<button class=\"bcont\" onclick=\"event.stopPropagation();apriContatto(\\''+r.id+'\\',\\''"
       "+esc(r.etichetta).replace(/'/g,\"&#39;\")+'\\')\">Contatta</button>'\n    + '</div>';")

if "apriContatto" in t:
    print("bottone gia' presente")
elif old in t:
    t = t.replace(old, new, 1)
    print("bottone 'Contatta' aggiunto alle schede")
else:
    raise SystemExit("STOP: chiusura scheda non trovata")

# --- 3) modale + JS prima di </body> ---
modale = """
<div id="mod" onclick="if(event.target.id==='mod')chiudiContatto()">
  <div class="in">
    <button class="chiudi" onclick="chiudiContatto()">&times;</button>
    <h3>Contatta <span id="m_chi"></span></h3>
    <p class="hint" style="margin:0 0 16px">Il messaggio arriva a lei/lui. <b>Il tuo indirizzo resta nascosto</b>: lo vedr&agrave; solo se accetta il contatto.</p>
    <div class="riga">
      <label for="m_email">La tua email (devi essere gi&agrave; sulla mappa) *</label>
      <input type="email" id="m_email" placeholder="quella con cui ti sei iscritto">
    </div>
    <div class="riga">
      <label for="m_testo">Il tuo messaggio *</label>
      <textarea id="m_testo" placeholder="Presentati: di cosa ti occupi, perch&eacute; lo contatti..."></textarea>
      <div class="hint">Da 20 a 1000 caratteri.</div>
    </div>
    <button class="btn" id="m_invia">Invia la richiesta</button>
    <div class="msg" id="m_msg"></div>
  </div>
</div>
<script>
var C_ERR = {
  non_iscritto:'Questa email non risulta sulla mappa. Devi essere iscritto per contattare gli altri.',
  email_non_confermata:'Devi prima confermare la tua email (controlla la posta).',
  in_attesa_approvazione:'La tua iscrizione &egrave; ancora in attesa.',
  troppe_richieste:'Hai gi&agrave; inviato 3 richieste oggi. Riprova domani.',
  bloccato:'Questa persona ha scelto di non ricevere tuoi messaggi.',
  stesso_utente:'Non puoi scrivere a te stesso.',
  destinatario_non_valido:'Scheda non pi&ugrave; disponibile.',
  messaggio_lunghezza:'Il messaggio deve stare fra 20 e 1000 caratteri.',
  dati_mancanti:'Compila tutti i campi.'
};
var C_ID = null;
function apriContatto(id, chi){
  C_ID = id;
  document.getElementById('m_chi').textContent = chi;
  document.getElementById('m_msg').className = 'msg';
  document.getElementById('m_msg').innerHTML = '';
  document.getElementById('mod').classList.add('on');
}
function chiudiContatto(){ document.getElementById('mod').classList.remove('on'); }
document.getElementById('m_invia').onclick = function(){
  var btn = this, msg = document.getElementById('m_msg');
  var email = document.getElementById('m_email').value.trim();
  var testo = document.getElementById('m_testo').value.trim();
  function ko(t){ msg.className='msg ko'; msg.innerHTML=t; btn.disabled=false; btn.textContent='Invia la richiesta'; }
  if(!email) return ko('Scrivi la tua email.');
  if(testo.length < 20) return ko('Il messaggio &egrave; troppo breve: almeno 20 caratteri.');
  btn.disabled = true; btn.textContent = 'Invio...';
  fetch(SB_URL + '/functions/v1/presenta', {
    method:'POST',
    headers:{'Content-Type':'application/json', apikey:SB_KEY, Authorization:'Bearer '+SB_KEY},
    body: JSON.stringify({email:email, destinatario_id:C_ID, messaggio:testo})
  })
  .then(function(r){ return r.json().then(function(j){ return {ok:r.ok, j:j}; }); })
  .then(function(res){
    if(!res.ok) return ko(C_ERR[res.j.errore] || 'Si &egrave; verificato un problema.');
    msg.className = 'msg ok';
    msg.innerHTML = '<b>Richiesta inviata.</b> Se accetta, riceverai la sua email e potrete parlarvi direttamente.';
    btn.disabled = true; btn.textContent = 'Inviata';
    document.getElementById('m_testo').value = '';
  })
  .catch(function(){ ko('Non raggiungibile. Riprova.'); });
};
</script>
"""

if 'id="mod"' not in t:
    t = t.replace("</body>", modale + "</body>", 1)
    print("modale + JS aggiunti")

F.write_text(t, encoding="utf-8")
print("OK")
