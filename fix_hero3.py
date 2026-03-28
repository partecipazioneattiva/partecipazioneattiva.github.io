with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Il problema esatto:
# 1. Dopo </div> della colonna sinistra c'è un </div> di troppo che chiude la griglia
# 2. Lo <script> RSS è fuori dalla griglia
# 3. La colonna destra <div> è fuori dalla griglia
#
# Soluzione: sostituire il blocco da "    </div>\n    </div>\n\n<script>" fino a "<div>\n    <div style="background..."
# con: "    </div>\n\n    <div>\n    <script>..." (colonna destra aperta DENTRO la griglia, script dentro)

old = '''    </div>
    </div>

<script>
async function loadHeroNews() {
  try {
    var API = 'https://api.rss2json.com/v1/api.json?rss_url=https%3A%2F%2Fwww.ilfattoquotidiano.it%2Ffeed%2F&api_key=nkozsgcqeibrbkg3xxszfahetmajwkz1ncsgntp2&count=4';
    var res = await fetch(API);
    var data = await res.json();
    if (data.status === 'ok' && data.items && data.items.length > 0) {
      var el = document.getElementById('hero-news-content');
      var html = '';
      data.items.forEach(function(item, i) {
        var date = new Date(item.pubDate).toLocaleDateString('it-IT',{day:'numeric',month:'long'});
        html += '<a href="' + item.link + '" target="_blank" rel="noopener noreferrer" style="text-decoration:none;display:block;padding:8px 0;' + (i < data.items.length-1 ? 'border-bottom:1px solid rgba(255,255,255,0.15);' : '') + '">';
        html += '<div style="font-size:.65em;color:#ffd580;margin-bottom:3px;">' + date + '</div>';
        html += '<div style="font-size:.85em;font-weight:700;color:#fff;line-height:1.3;">' + item.title + '</div>';
        html += '</a>';
      });
      html += '<a href="https://www.ilfattoquotidiano.it/" target="_blank" rel="noopener noreferrer" style="display:block;text-align:center;margin-top:10px;font-size:.72em;color:#ffd580;text-decoration:none;font-weight:700;">Tutte le notizie &#x2192;</a>';
      el.innerHTML = html;
    }
  } catch(e) { console.log('RSS error:', e); }
}
loadHeroNews();
</script>
    <div>
    <div style="background:rgba(255,255,255,0.10)'''

new = '''    </div>

    <div>
    <script>
async function loadHeroNews() {
  try {
    var API = 'https://api.rss2json.com/v1/api.json?rss_url=https%3A%2F%2Fwww.ilfattoquotidiano.it%2Ffeed%2F&api_key=nkozsgcqeibrbkg3xxszfahetmajwkz1ncsgntp2&count=4';
    var res = await fetch(API);
    var data = await res.json();
    if (data.status === 'ok' && data.items && data.items.length > 0) {
      var el = document.getElementById('hero-news-content');
      var html = '';
      data.items.forEach(function(item, i) {
        var date = new Date(item.pubDate).toLocaleDateString('it-IT',{day:'numeric',month:'long'});
        html += '<a href="' + item.link + '" target="_blank" rel="noopener noreferrer" style="text-decoration:none;display:block;padding:8px 0;' + (i < data.items.length-1 ? 'border-bottom:1px solid rgba(255,255,255,0.15);' : '') + '">';
        html += '<div style="font-size:.65em;color:#ffd580;margin-bottom:3px;">' + date + '</div>';
        html += '<div style="font-size:.85em;font-weight:700;color:#fff;line-height:1.3;">' + item.title + '</div>';
        html += '</a>';
      });
      html += '<a href="https://www.ilfattoquotidiano.it/" target="_blank" rel="noopener noreferrer" style="display:block;text-align:center;margin-top:10px;font-size:.72em;color:#ffd580;text-decoration:none;font-weight:700;">Tutte le notizie &#x2192;</a>';
      el.innerHTML = html;
    }
  } catch(e) { console.log('RSS error:', e); }
}
loadHeroNews();
</script>
    <div style="background:rgba(255,255,255,0.10)'''

if old not in content:
    print('ERRORE: stringa non trovata')
else:
    content = content.replace(old, new, 1)
    print('OK: struttura corretta')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('FATTO - file salvato')
