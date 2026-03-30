with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Trova inizio e fine del ticker
start = content.find('<div style="background:#c0392b;color:#fff;padding:9px 0')
# Cerca il tag </div> che chiude il wrapper esterno dopo @keyframes
end = content.find('@keyframes ticker', start)
end = content.find('</div>', end) + len('</div>')

print("START:", start)
print("END:", end)
print("ESTRATTO:", repr(content[start:end][-100:]))
