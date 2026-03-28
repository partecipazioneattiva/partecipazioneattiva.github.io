with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old1 = 'height:220px;object-fit:cover;object-position:top;display:block;">'
new1 = 'width:100%;display:block;">'

old2 = 'height:220px;object-fit:cover;object-position:top;display:block;">'
new2 = 'width:100%;display:block;">'

html = html.replace(old1, new1)
html = html.replace(old2, new2)

# rimuovi anche width:100% duplicato
html = html.replace('style="width:100%;width:100%;display:block;">', 'style="width:100%;display:block;">')

print("OK")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Salvato")
