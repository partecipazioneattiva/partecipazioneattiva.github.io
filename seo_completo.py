#!/usr/bin/env python3
# seo_completo.py - Ottimizzazione SEO completa
import re

# ============================================================
# STEP 1: Titoli e meta description ottimizzati per keyword
# ============================================================

pages = {
    'index.html': {
        'title': 'Partecipazione Attiva | Movimento Politico dei Cittadini — Napoli e Italia',
        'description': 'Partecipazione Attiva è il movimento politico dei cittadini fondato sulla Costituzione. Battaglie concrete, trasparenza, partecipazione dal basso. Unisciti a noi — primo anno gratuito.',
    },
    'battaglie.html': {
        'title': 'Battaglie per i Diritti | RC Auto Uguale per Tutti — Partecipazione Attiva',
        'description': 'Partecipazione Attiva combatte le discriminazioni territoriali sulle tariffe RC Auto. I cittadini del Sud pagano fino al 50% in più. Scopri la battaglia e sostienici.',
    },
    'napoli.html': {
        'title': 'Partecipazione Attiva Napoli | Insieme per i Cittadini Napoletani',
        'description': 'Il coordinamento napoletano di Partecipazione Attiva: Paolo Neri, Antonio Cristiano, Rosa Ugon. Iniziative, eventi e battaglie per i cittadini di Napoli.',
    },
    'parlero.html': {
        'title': 'Parlerò — Salotto Culturale Napoletano | Partecipazione Attiva',
        'description': 'Parlerò è il salotto culturale di Partecipazione Attiva: dibattiti, idee e confronto su politica, società e cultura. Condotto da Antonio Cristiano a Napoli.',
    },
    'territori.html': {
        'title': 'Gruppi Territoriali | Partecipazione Attiva in tutta Italia',
        'description': 'I gruppi territoriali di Partecipazione Attiva in tutta Italia. Trova il coordinamento nella tua città e unisciti al movimento politico dei cittadini.',
    },
    'organigramma.html': {
        'title': 'Organigramma | Chi Guida Partecipazione Attiva',
        'description': 'La struttura e le persone di Partecipazione Attiva: il Comitato Direttivo, i coordinatori territoriali e i responsabili del movimento politico dei cittadini.',
    },
    'privacy.html': {
        'title': 'Privacy Policy | Partecipazione Attiva',
        'description': 'Informativa sulla privacy e trattamento dei dati personali di Partecipazione Attiva, movimento politico dei cittadini.',
    },
}

errors = []
successes = []

for filename, meta in pages.items():
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Aggiorna o inserisci <title>
        new_title = f'<title>{meta["title"]}</title>'
        if re.search(r'<title>.*?</title>', content):
            content = re.sub(r'<title>.*?</title>', new_title, content)
        else:
            content = content.replace('</head>', f'  {new_title}\n</head>', 1)

        # Aggiorna o inserisci meta description
        new_desc = f'<meta name="description" content="{meta["description"]}">'
        if re.search(r'<meta name="description"[^>]*>', content):
            content = re.sub(r'<meta name="description"[^>]*>', new_desc, content)
        else:
            content = content.replace('<title>', f'{new_desc}\n  <title>', 1)

        # Aggiungi meta keywords se non presente
        if 'partecipazione attiva' not in filename or True:
            kw_map = {
                'index.html': 'partecipazione attiva, movimento politico, cittadini, napoli, italia, politica dal basso',
                'battaglie.html': 'rc auto napoli, discriminazioni territoriali, tariffe assicurazione, partecipazione attiva battaglie',
                'napoli.html': 'partecipazione attiva napoli, paolo neri, antonio cristiano, rosa ugon, politica napoli',
                'parlero.html': 'parlero salotto culturale napoli, antonio cristiano, dibattiti politici napoli',
                'territori.html': 'partecipazione attiva territori, gruppi locali, movimento politico italia',
                'organigramma.html': 'partecipazione attiva organigramma, direttivo, coordinatori, struttura movimento',
                'privacy.html': 'privacy policy partecipazione attiva',
            }
            kw = kw_map.get(filename, '')
            new_kw = f'<meta name="keywords" content="{kw}">'
            if not re.search(r'<meta name="keywords"', content):
                content = content.replace('<meta name="description"', f'{new_kw}\n  <meta name="description"', 1)

        # Aggiungi canonical se non presente
        canonical_map = {
            'index.html': 'https://partecipazioneattiva.github.io/',
            'battaglie.html': 'https://partecipazioneattiva.github.io/battaglie.html',
            'napoli.html': 'https://partecipazioneattiva.github.io/napoli.html',
            'parlero.html': 'https://partecipazioneattiva.github.io/parlero.html',
            'territori.html': 'https://partecipazioneattiva.github.io/territori.html',
            'organigramma.html': 'https://partecipazioneattiva.github.io/organigramma.html',
            'privacy.html': 'https://partecipazioneattiva.github.io/privacy.html',
        }
        canonical = canonical_map.get(filename, '')
        if canonical and '<link rel="canonical"' not in content:
            content = content.replace('</head>', f'  <link rel="canonical" href="{canonical}">\n</head>', 1)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        successes.append(f'OK: {filename}')

    except FileNotFoundError:
        errors.append(f'SKIP: {filename} non trovato')
    except Exception as e:
        errors.append(f'ERRORE {filename}: {e}')

for s in successes:
    print(s)
for e in errors:
    print(e)

# ============================================================
# STEP 2: FAQPage Schema.org su battaglie.html
# ============================================================

faq_schema = '''
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Perché i residenti del Sud pagano di più per la RC Auto?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Le compagnie assicurative applicano tariffe più alte nelle province del Sud Italia, inclusa Napoli, basandosi su statistiche di sinistrosità storiche. Partecipazione Attiva ritiene questa pratica discriminatoria e contraria al principio di uguaglianza dei cittadini."
      }
    },
    {
      "@type": "Question",
      "name": "Quanto pagano in più i napoletani per l'RC Auto rispetto al Nord?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Secondo i dati IVASS, i residenti di Napoli possono pagare fino al 50% in più rispetto ai residenti di città del Nord Italia per la stessa automobile e lo stesso profilo assicurativo."
      }
    },
    {
      "@type": "Question",
      "name": "Come posso sostenere la battaglia di Partecipazione Attiva sull'RC Auto?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Puoi iscriverti a Partecipazione Attiva (primo anno gratuito), condividere la nostra petizione sui social, seguirci su Facebook e YouTube per restare aggiornato sugli sviluppi della battaglia."
      }
    },
    {
      "@type": "Question",
      "name": "Cos'è Partecipazione Attiva?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Partecipazione Attiva è un movimento politico dei cittadini fondato sulla Costituzione Italiana. Nasce per dare voce ai cittadini attraverso battaglie concrete, trasparenza e partecipazione dal basso. Il primo anno di iscrizione è completamente gratuito."
      }
    }
  ]
}
</script>'''

try:
    with open('battaglie.html', 'r', encoding='utf-8') as f:
        content = f.read()

    if 'FAQPage' not in content:
        content = content.replace('</head>', faq_schema + '\n</head>', 1)
        with open('battaglie.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print('OK: FAQPage Schema.org aggiunto a battaglie.html')
    else:
        print('SKIP: FAQPage già presente in battaglie.html')
except Exception as e:
    print(f'ERRORE FAQPage: {e}')

# ============================================================
# STEP 3: Alt text ottimizzati per SEO su index.html
# ============================================================

alt_fixes = {
    'alt="PensAttivo RC Auto"': 'alt="RC Auto discriminazioni territoriali Napoli — Partecipazione Attiva"',
    'alt="Insieme per Napoli"': 'alt="Insieme per Napoli — Partecipazione Attiva coordinamento napoletano"',
    'alt="Paolo Neri"': 'alt="Paolo Neri — Partecipazione Attiva Napoli coordinatore"',
    'alt="Antonio Cristiano"': 'alt="Antonio Cristiano — Partecipazione Attiva Napoli Parlerò salotto culturale"',
    'alt="Rosa Ugon"': 'alt="Rosa Ugon — Partecipazione Attiva Napoli"',
    'alt="Logo PA"': 'alt="Logo Partecipazione Attiva — Movimento Politico dei Cittadini"',
    'alt="Logo"': 'alt="Partecipazione Attiva — Movimento Politico"',
}

try:
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    count = 0
    for old, new in alt_fixes.items():
        if old in content:
            content = content.replace(old, new)
            count += 1

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'OK: {count} alt text ottimizzati in index.html')
except Exception as e:
    print(f'ERRORE alt text: {e}')

# ============================================================
# STEP 4: Open Graph tags su tutte le pagine (social sharing)
# ============================================================

og_data = {
    'index.html': {
        'og_title': 'Partecipazione Attiva | Movimento Politico dei Cittadini',
        'og_description': 'Libera associazione di cittadini per una politica trasparente e partecipata. Unisciti — primo anno gratuito.',
        'og_image': 'https://partecipazioneattiva.github.io/LOGO-PA.webp',
    },
    'battaglie.html': {
        'og_title': 'Battaglie per i Diritti | RC Auto Uguale per Tutti',
        'og_description': 'I cittadini del Sud pagano fino al 50% in più di RC Auto. Partecipazione Attiva combatte questa discriminazione.',
        'og_image': 'https://partecipazioneattiva.github.io/images/pensattivo-rcauto.webp',
    },
    'napoli.html': {
        'og_title': 'Partecipazione Attiva Napoli',
        'og_description': 'Il coordinamento napoletano di Partecipazione Attiva. Insieme per i cittadini di Napoli.',
        'og_image': 'https://partecipazioneattiva.github.io/images/insieme-napoli.webp',
    },
    'parlero.html': {
        'og_title': 'Parlerò — Salotto Culturale Napoletano',
        'og_description': 'Dibattiti, idee e confronto su politica, società e cultura. Condotto da Antonio Cristiano.',
        'og_image': 'https://partecipazioneattiva.github.io/LOGO-PA.webp',
    },
    'territori.html': {
        'og_title': 'Gruppi Territoriali | Partecipazione Attiva',
        'og_description': 'Trova il coordinamento di Partecipazione Attiva nella tua città.',
        'og_image': 'https://partecipazioneattiva.github.io/LOGO-PA.webp',
    },
    'organigramma.html': {
        'og_title': 'Chi Guida Partecipazione Attiva | Organigramma',
        'og_description': 'Il Comitato Direttivo e i coordinatori di Partecipazione Attiva.',
        'og_image': 'https://partecipazioneattiva.github.io/LOGO-PA.webp',
    },
}

for filename, og in og_data.items():
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'og:title' not in content:
            og_block = f'''  <meta property="og:type" content="website">
  <meta property="og:url" content="https://partecipazioneattiva.github.io/{filename if filename != 'index.html' else ''}">
  <meta property="og:title" content="{og['og_title']}">
  <meta property="og:description" content="{og['og_description']}">
  <meta property="og:image" content="{og['og_image']}">
  <meta property="og:locale" content="it_IT">
  <meta property="og:site_name" content="Partecipazione Attiva">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{og['og_title']}">
  <meta name="twitter:description" content="{og['og_description']}">'''
            content = content.replace('</head>', og_block + '\n</head>', 1)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'OK: Open Graph aggiunto a {filename}')
        else:
            print(f'SKIP: Open Graph già presente in {filename}')

    except FileNotFoundError:
        print(f'SKIP: {filename} non trovato')
    except Exception as e:
        print(f'ERRORE OG {filename}: {e}')

print('\n=== SEO COMPLETO TERMINATO ===')
