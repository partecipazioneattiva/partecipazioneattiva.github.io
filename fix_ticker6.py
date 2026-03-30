with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('<div style="background:#c0392b;color:#fff;padding:9px 0')
end = content.find('</style></div>', start) + len('</style></div>')

print("START:", start)
print("END:", end)
print("ESTRATTO FINE:", repr(content[end-50:end+50]))
