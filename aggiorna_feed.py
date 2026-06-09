
import re, os
from datetime import timezone

BASE = "/Users/osxssd/Desktop/LAVORI/partecipazioneattiva"
DOMAIN = "https://partecipazione-attiva.it"

SKIP = {
    '404.html','index.html','googled83ce80b766b7708.html','privacy.html',
    'battaglie.html','territori.html','organigramma.html','napoli.html',
    'regione-campania.html','regione-lazio.html','rete-ape.html',
    'curriculum-luigi-spanu.html','parlero.html','diretta-sire.html'
}

os.chdir(BASE)
files = [f for f in os.listdir('.') if f.endswith('.html') and f not in SKIP]

articles = []
for fname in files:
    with open(fname, encoding='utf-8') as f:
        html = f.read()

    title = re.search(r'<title>([^<]+)</title>', html)
    desc  = re.search(r'meta name=description content="([^"]+)"', html)
    if not desc:
        desc = re.search(r'meta name="description" content="([^"]+)"', html)
    date  = re.search(r'"dateModified"\s*:\s*"([^"]+)"', html)
    if not date:
        date = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)

    if not title or not date:
        continue

    title_str = title.group(1).strip()
    # Rimuovi " | Partecipazione Attiva" o " | PA" dal titolo per il feed
    title_str = re.sub(r'\s*[|—]\s*(Partecipazione Attiva|PA)\s*$', '', title_str)

    desc_str = desc.group(1).strip() if desc else title_str
    date_str = date.group(1).strip()
    # Normalizza la data in formato RFC 822
    date_str = date_str[:10]  # prendi solo YYYY-MM-DD

    articles.append({
        'file': fname,
        'title': title_str,
        'desc': desc_str,
        'date': date_str,
    })

# Ordina per data decrescente, poi per nome file (stabile)
articles.sort(key=lambda a: (a['date'], a['file']), reverse=True)

def esc(s):
    return (s.replace('&','&amp;')
             .replace('<','&lt;')
             .replace('>','&gt;')
             .replace('"','&quot;'))

def to_rfc822(d):
    # d = "YYYY-MM-DD"
    from datetime import datetime
    dt = datetime.strptime(d, '%Y-%m-%d')
    days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    dow = days[dt.weekday()]
    mon = months[dt.month - 1]
    return f"{dow}, {dt.day:02d} {mon} {dt.year} 12:00:00 +0200"

items = ""
for a in articles:
    url = f"{DOMAIN}/{a['file']}"
    pub = to_rfc822(a['date'])
    items += f"""  <item>
    <title>{esc(a['title'])}</title>
    <link>{url}</link>
    <guid isPermaLink="true">{url}</guid>
    <description>{esc(a['desc'])}</description>
    <pubDate>{pub}</pubDate>
  </item>\n"""

from datetime import datetime
now = datetime.now()
last_build = to_rfc822(now.strftime('%Y-%m-%d'))

feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Partecipazione Attiva</title>
    <link>{DOMAIN}</link>
    <description>Notizie, battaglie e proposte di Partecipazione Attiva</description>
    <language>it</language>
    <atom:link href="{DOMAIN}/feed.xml" rel="self" type="application/rss+xml"/>
    <lastBuildDate>{last_build}</lastBuildDate>
{items}  </channel>
</rss>"""

out = f"{BASE}/feed.xml"
with open(out, 'w', encoding='utf-8') as f:
    f.write(feed)
print(f"✅ feed.xml aggiornato con {len(articles)} articoli")
