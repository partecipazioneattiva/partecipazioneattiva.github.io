with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# CSS per la progress bar
css = '''
  /* === SCROLL PROGRESS BAR === */
  #scroll-progress{position:fixed;top:0;left:0;width:0%;height:3px;background:linear-gradient(90deg,#8a4e00,#e8900a,#ffd580);z-index:99999;transition:width .1s linear;}
'''

# JS per aggiornare la progress bar
js = '''<script>
(function(){
  var bar = document.createElement('div');
  bar.id = 'scroll-progress';
  document.body.prepend(bar);
  window.addEventListener('scroll', function(){
    var s = document.documentElement;
    var pct = (s.scrollTop || document.body.scrollTop) / (s.scrollHeight - s.clientHeight) * 100;
    bar.style.width = pct + '%';
  }, {passive: true});
})();
</script>
'''

if 'scroll-progress' in content:
    print('SKIP: scroll progress bar già presente')
else:
    # Aggiungi CSS prima di /* === RESPONSIVE MOBILE === */
    content = content.replace(
        '  /* === RESPONSIVE MOBILE === */',
        css + '\n  /* === RESPONSIVE MOBILE === */',
        1
    )
    # Aggiungi JS prima del modal Sostienici
    content = content.replace(
        '<script>\n(function(){\n  var els = document.querySelectorAll(\'.fade-in\')',
        js + '\n<script>\n(function(){\n  var els = document.querySelectorAll(\'.fade-in\')',
        1
    )
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: scroll progress bar aggiunta')
