from datetime import date

today = date.today().strftime('%Y-%m-%d')

sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://partecipazioneattiva.github.io/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://partecipazioneattiva.github.io/napoli.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://partecipazioneattiva.github.io/battaglie.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://partecipazioneattiva.github.io/parlero.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://partecipazioneattiva.github.io/territori.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://partecipazioneattiva.github.io/organigramma.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://partecipazioneattiva.github.io/privacy.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
</urlset>'''

with open('sitemap.xml', 'w', encoding='utf-8') as f:
    f.write(sitemap)
print('OK: sitemap.xml creata')
