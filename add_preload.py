with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

preload = '''<link rel="preload" as="image" href="images/pensattivo-rcauto.webp" type="image/webp">
<link rel="preload" as="image" href="images/insieme-napoli.webp" type="image/webp">
'''

if 'preload' in content and 'pensattivo-rcauto.webp' in content:
    print('SKIP: preload già presente')
else:
    # Inserisci dopo il tag canonical
    content = content.replace(
        '<link rel="canonical"',
        preload + '<link rel="canonical"',
        1
    )
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: preload immagini hero aggiunto')
