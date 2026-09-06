#!/usr/bin/env python3
"""Build index.html (3 languages in one page) from src/.
Usage: python3 build.py            -> photos referenced as assets/photos/*.jpg (for hosting)
       python3 build.py --inline   -> photos embedded as data URIs (for the claude.ai artifact)
Photo slots are read from src/photos.json: {"hero-main": "file.jpg", "hero-small": "...", "gallery": ["...", ...]}
"""
import re, json, base64, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
INLINE = '--inline' in sys.argv
R = lambda p: open(p, encoding='utf-8').read()
head = R('src/head.html'); script = R('src/script.js')
bodies = {k: R(f'src/body-{k}.html') for k in ('vi', 'en', 'zh')}
logo_full = R('src/logo-full.b64'); logo_mark = R('src/logo-mark.b64'); fav = R('src/favicon.b64')
photos = json.load(open('src/photos.json')) if os.path.exists('src/photos.json') else {}

def photo_src(name):
    p = f'assets/photos/{name}'
    if INLINE and os.path.exists(p):
        return 'data:image/jpeg;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    return p

# ---- head: title, favicon, fonts (add Noto Sans SC for Chinese body), extra CSS ----
head = re.sub(r'<title>[^<]*</title>', '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>SunMoon Art & Education</title>', head, 1)
head = head.replace('<link rel="preconnect" href="https://fonts.googleapis.com">',
    f'<link rel="icon" type="image/png" href="{fav}">\n<link rel="preconnect" href="https://fonts.googleapis.com">', 1)
head = head.replace('&family=Noto+Serif+SC:wght@400;600&display=swap', '&family=Noto+Serif+SC:wght@400;600&family=Noto+Sans+SC:wght@400;500;600&display=swap')
extra_css = f'''
/* ---------- logo (data URI kept in CSS so the 3 language bodies stay small) ---------- */
.brand .logo{{display:block;height:56px;aspect-ratio:600/547;background:url("{logo_full}") center/contain no-repeat;transition:transform .3s ease}}
.brand:hover .logo{{transform:translateY(-1px)}}
.footer .brand-row{{display:flex;align-items:center;gap:1rem}}
.footer .logo-mark{{display:block;height:64px;aspect-ratio:400/333;background:url("{logo_mark}") center/contain no-repeat}}
/* ---------- language switch ---------- */
.langs{{display:flex;align-items:center;gap:.2rem;border:1px solid var(--line-strong);border-radius:999px;padding:.2rem}}
.langs button{{font-size:.68rem;font-weight:600;letter-spacing:.08em;padding:.35rem .6rem;border-radius:999px;color:var(--ink-2);transition:background .2s,color .2s}}
.langs button:hover{{color:var(--ink)}}
.langs button[aria-pressed="true"]{{background:var(--ink);color:var(--ivory)}}
.header .langs{{margin-left:auto}}
@media (min-width:980px){{.header .langs{{margin-left:0}}}}
.drawer .langs{{align-self:flex-start;margin-top:1.2rem}}
.drawer .langs button{{font-size:.85rem;padding:.5rem .9rem}}
/* ---------- Chinese typography ---------- */
:root[data-lang="zh"] body{{font-family:"Noto Sans SC",var(--sans)}}
:root[data-lang="zh"] h1,:root[data-lang="zh"] h2,:root[data-lang="zh"] h3,:root[data-lang="zh"] .tagline,:root[data-lang="zh"] .stack,:root[data-lang="zh"] .quote,:root[data-lang="zh"] .q{{font-family:"Noto Serif SC",var(--serif);letter-spacing:0}}
:root[data-lang="zh"] .hero h1{{font-size:clamp(2.6rem,7vw,6rem);line-height:1.08;font-weight:600}}
:root[data-lang="zh"] .h2{{font-weight:600}}
:root[data-lang="zh"] .vi{{font-family:var(--sans);font-style:normal;font-size:.86rem;letter-spacing:.06em;text-transform:uppercase}}
/* ---------- real photos ---------- */
.shot{{cursor:zoom-in}}
.shot{{background-size:cover;background-position:center;transition:transform .4s ease}}
.shot:hover{{transform:scale(1.015)}}
.shot .cap{{color:#fff;text-shadow:0 1px 8px rgba(0,0,0,.55)}}
.shot::after{{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,transparent 55%,rgba(20,16,12,.55) 100%);pointer-events:none}}
.shot::before{{display:none}}
.lightbox{{position:fixed;inset:0;z-index:100;background:rgba(20,16,12,.92);display:grid;place-items:center;padding:2rem;opacity:0;transition:opacity .25s ease;cursor:zoom-out}}
.lightbox.on{{opacity:1}}
.lightbox img{{max-width:min(100%,1400px);max-height:100%;object-fit:contain;border-radius:4px;box-shadow:0 30px 80px rgba(0,0,0,.6)}}
.lightbox .close{{position:absolute;top:1rem;right:1.2rem;color:#fff;font-size:2.2rem;line-height:1;width:44px;height:44px}}
.zalo-fab{{position:fixed;right:1.1rem;bottom:1.1rem;z-index:47;width:56px;height:56px;border-radius:50%;background:#0068FF;color:#fff;display:none;place-items:center;font-weight:700;font-size:.8rem;letter-spacing:.02em;box-shadow:0 10px 24px -8px rgba(0,104,255,.6);transition:transform .25s ease}}
.zalo-fab:hover{{transform:translateY(-3px)}}
@media (min-width:980px){{.zalo-fab{{display:grid}}}}
.float-cta .btn-zalo{{flex:0 0 auto;background:#0068FF;border-color:#0068FF;color:#fff}}
</style>'''
photo_css = ''
for name in ([photos.get('hero-main'), photos.get('hero-small')] + list(photos.get('gallery', []))):
    if name: photo_css += f'.shot[data-photo="{name.rsplit(".",1)[0]}"]{{background-image:url("{photo_src(name)}")}}\n'
extra_css = extra_css.replace('</style>', photo_css + '</style>')
# drop the old logo/zalo css block that index.html carried, keep everything else
head = re.sub(r'\.brand img\.logo\{.*?\.float-cta \.btn-zalo\{[^}]*\}\n', '', head, flags=re.S)
head = head.replace('</style>', extra_css, 1)

SWITCH = '<div class="langs" role="group" aria-label="Language"><button type="button" data-lang="vi" lang="vi">VI</button><button type="button" data-lang="en" lang="en">EN</button><button type="button" data-lang="zh" lang="zh">中文</button></div>'

def fill_photos(b, lang):
    """Replace placeholder blocks with real photos where src/photos.json provides them."""
    if not photos: return b
    def shot(name, cap, cls='ph shot', extra=''):
        key = name.rsplit('.', 1)[0]
        return f'<figure class="{cls}"{extra} data-photo="{key}" role="img" aria-label="{cap}"><span class="cap">{cap}</span></figure>'
    # hero main + small
    m = re.search(r'<div class="ph main">.*?</div>\s*<div class="ph small">.*?</div>', b, re.S)
    if m and photos.get('hero-main'):
        cap_main = re.search(r'<div class="ph main">.*?<span class="cap">(.*?)</span>', m.group(0), re.S).group(1)
        cap_small = re.search(r'<div class="ph small">.*?<span class="cap">(.*?)</span>', m.group(0), re.S).group(1)
        rep = shot(photos['hero-main'], cap_main, 'ph main shot')
        if photos.get('hero-small'): rep += shot(photos['hero-small'], cap_small, 'ph small shot')
        b = b[:m.start()] + rep + b[m.end():]
    # gallery
    g = re.search(r'(<div class="gallery reveal">)(.*?)(</div>\s*<p class="hint">)', b, re.S)
    if g and photos.get('gallery'):
        tiles = re.findall(r'<div class="ph">.*?<span class="cap">(.*?)</span></div>', g.group(2), re.S)
        out = ''
        for i, cap in enumerate(tiles):
            if i < len(photos['gallery']): out += shot(photos['gallery'][i], cap)
            else: out += re.findall(r'<div class="ph">.*?</div>', g.group(2), re.S)[i]
        b = b[:g.start()] + g.group(1) + out + g.group(3) + b[g.end():]
    return b

def prep(b, lang):
    b = b.replace('</nav>', '</nav>\n    ' + SWITCH, 1)
    b = b.replace('<p class="fine">', SWITCH + '\n  <p class="fine">', 1)
    b = fill_photos(b, lang)
    return b

vi = prep(bodies['vi'], 'vi'); en = prep(bodies['en'], 'en'); zh = prep(bodies['zh'], 'zh')
out = (head + '\n\n<div id="app">\n' + vi + '\n</div>\n'
       + '<template id="tpl-vi">\n' + vi + '\n</template>\n'
       + '<template id="tpl-en">\n' + en + '\n</template>\n'
       + '<template id="tpl-zh">\n' + zh + '\n</template>\n\n' + script)
open('index.html', 'w', encoding='utf-8').write(out)
print('index.html', len(out), 'bytes', '(inline photos)' if INLINE else '(assets/photos paths)')
