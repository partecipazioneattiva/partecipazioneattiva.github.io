content = open('index.html','r').read()
old = '<iframe src="https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2FPartecipazioneAttiva21%2F&tabs=timeline&width=500&height=700&small_header=false&adapt_container_width=true&hide_cover=false&show_facepile=true&locale=it_IT" width="100%" height="700" style="border:none;overflow:hidden;" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share" loading="lazy"></iframe>'
new = '<!-- Elfsight Facebook Feed | Untitled Facebook Feed -->\n<script src="https://elfsightcdn.com/platform.js" async></script>\n<div class="elfsight-app-e4e52e54-837f-441a-9053-c10c9d89595d" data-elfsight-app-lazy></div>'
if old in content:
    content = content.replace(old, new)
    open('index.html','w').write(content)
    print('FATTO')
else:
    print('NON TROVATO')
