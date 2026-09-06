#!/usr/bin/env python3
"""Build the SunMoon multi-page site from src/.

  python3 build.py            -> 6 pages, photos referenced as assets/photos/*.jpg (for hosting)
  python3 build.py --inline   -> same pages, photos embedded as data URIs (one-file preview)

Content lives in src/body-{vi,en,zh}.html (one long document); this script slices it into
sections and reassembles them into pages. Never edit the generated *.html by hand.
"""
import re, json, base64, os, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
INLINE = '--inline' in sys.argv
R = lambda p: open(p, encoding='utf-8').read()
LANGS = ('vi', 'en', 'zh')

head_tpl = R('src/head.html')
script = R('src/script.js')
logo_full = R('src/logo-full.b64'); logo_mark = R('src/logo-mark.b64'); fav = R('src/favicon.b64')
photos = json.load(open('src/photos.json')) if os.path.exists('src/photos.json') else {}

def photo_src(name):
    p = f'assets/photos/{name}'
    if INLINE and os.path.exists(p):
        return 'data:image/jpeg;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    return p

# ---------------------------------------------------------------- slice source
def slice_body(b):
    """-> (header_html, {section_key: html}, tail_html)"""
    i, j = b.index('<main>'), b.index('</main>')
    header, tail = b[:i], b[j + len('</main>'):]
    out = {}
    for chunk in re.split(r'\n(?=<!-- =+ [A-Z])', b[i + len('<main>'):j]):
        if not chunk.strip():
            continue
        m = re.search(r'<section([^>]*)>', chunk)
        if not m:
            continue
        attrs = m.group(1)
        key = (re.search(r'id="([a-z]+)"', attrs) or [None, None])[1]
        if not key:
            key = re.search(r'class="(?:section )?([a-z]+)', attrs).group(1)
        out[key] = chunk.rstrip()
    return header, out, tail

BODIES = {l: slice_body(R(f'src/body-{l}.html')) for l in LANGS}

# ------------------------------------------------------------------ page model
# section key -> page it now lives on (used to rewrite in-page anchors)
HOME, ABOUT, CLASSES, PARENTS, FAQ, CONTACT = (
    'index.html', 'gioi-thieu.html', 'lop-hoc.html', 'ba-me.html', 'hoi-dap.html', 'lien-he.html')
ANCHOR_PAGE = {
    'about': ABOUT, 'approach': ABOUT, 'teachers': ABOUT,
    'programs': CLASSES, 'little': CLASSES, 'kids': CLASSES, 'hsk': CLASSES,
    'work': CLASSES, 'more': CLASSES, 'journey': CLASSES,
    'parents': PARENTS, 'stories': PARENTS, 'guide': PARENTS,
    'faq': FAQ, 'contact': CONTACT, 'trial': CONTACT,
}
NAV = [(HOME, 'home'), (ABOUT, 'about'), (CLASSES, 'classes'), (PARENTS, 'parents'),
       (FAQ, 'faq'), (CONTACT, 'contact')]

L = {
 'vi': dict(nav=dict(home='Trang chủ', about='Giới thiệu', classes='Các lớp học',
                     parents='Dành cho ba mẹ', faq='Hỏi đáp', contact='Liên hệ'),
            cta='Đăng ký học thử', menu='Điều hướng chính', home_label='SunMoon Art & Education — trang chủ',
            strap='Tiếng Trung · Văn hoá · Sáng tạo · Trưởng thành',
            titles={ABOUT: ('Giới thiệu', 'Về SunMoon', 'Một trung tâm tiếng Trung được xây quanh cách trẻ thật sự học một ngôn ngữ.'),
                    CLASSES: ('Các lớp học', 'Chương trình tại SunMoon', 'Tiếng Trung theo độ tuổi, lộ trình HSK, lớp cho người lớn, cùng các lớp Toán tư duy, Tiền tiểu học và Luyện chữ đẹp.'),
                    PARENTS: ('Dành cho ba mẹ', 'Đồng hành cùng ba mẹ', 'Những câu hỏi thật, câu chuyện thật, và những điều nên biết trước khi con bắt đầu.'),
                    FAQ: ('Hỏi đáp', 'Câu hỏi thường gặp', 'Những điều ba mẹ hay hỏi SunMoon nhất.'),
                    CONTACT: ('Liên hệ', 'Đăng ký học thử', 'Kể cho SunMoon một chút về con, chúng tôi sẽ gợi ý lớp phù hợp và hẹn buổi học thử.')}),
 'en': dict(nav=dict(home='Home', about='About', classes='Classes',
                     parents='For parents', faq='FAQ', contact='Contact'),
            cta='Book a trial', menu='Primary', home_label='SunMoon Art & Education — home',
            strap='Chinese Language · Culture · Creativity · Growth',
            titles={ABOUT: ('About', 'About SunMoon', 'A Chinese language centre built around the way children actually learn a language.'),
                    CLASSES: ('Classes', 'Programmes at SunMoon', 'Chinese by age, the HSK pathway, adult classes, plus Logical Maths, Pre-Primary and Handwriting.'),
                    PARENTS: ('For parents', 'Walking with parents', 'Real questions, real stories, and what is worth knowing before your child starts.'),
                    FAQ: ('FAQ', 'Questions parents ask', 'The things parents ask us most often.'),
                    CONTACT: ('Contact', 'Book a trial class', 'Tell us a little about your child. We will suggest a programme and arrange a trial.')}),
 'zh': dict(nav=dict(home='首页', about='关于日月', classes='课程',
                     parents='家长须知', faq='常见问题', contact='联系我们'),
            cta='预约试听', menu='主导航', home_label='SunMoon Art & Education — 首页',
            strap='中文语言 · 文化 · 创造力 · 成长',
            titles={ABOUT: ('关于日月', '关于日月', '一所围绕孩子真实学习方式而建立的中文学习中心。'),
                    CLASSES: ('课程', '日月的课程', '按年龄划分的中文课、HSK 进阶之路、成人课程，以及思维数学、幼小衔接与书写练习。'),
                    PARENTS: ('家长须知', '与家长同行', '真实的问题、真实的故事，以及孩子开始学习前值得了解的事。'),
                    FAQ: ('常见问题', '家长常问的问题', '家长最常问我们的问题。'),
                    CONTACT: ('联系我们', '预约试听课', '简单介绍一下孩子，我们会推荐合适的课程并安排试听。')}),
}

PAGES = {
    HOME:    ['hero', 'about', 'homeclasses', 'why', 'inside', 'trial', 'final'],
    ABOUT:   ['about', 'approach', 'teachers', 'inside', 'final'],
    CLASSES: ['programs', 'journey', 'trial', 'final'],
    PARENTS: ['parents', 'stories', 'guide', 'trial', 'final'],
    FAQ:     ['faq', 'final'],
    CONTACT: ['contact', 'final'],
}

# ------------------------------------------------------- rewrite links & photos
def rewrite_links(html, page):
    def sub(m):
        anchor = m.group(1)
        target = ANCHOR_PAGE.get(anchor)
        if anchor == 'top' or target is None or target == page:
            return f'href="#{anchor}"'
        return f'href="{target}#{anchor}"' if anchor not in ('faq',) else f'href="{target}"'
    return re.sub(r'href="#([a-z]+)"', sub, html)

def fill_photos(html):
    if not photos:
        return html
    def shot(name, cap, cls='ph shot', extra=''):
        key = name.rsplit('.', 1)[0]
        return (f'<figure class="{cls}"{extra} data-photo="{key}" role="img" '
                f'aria-label="{cap}"><span class="cap">{cap}</span></figure>')
    m = re.search(r'<div class="ph main">.*?</div>\s*<div class="ph small">.*?</div>', html, re.S)
    if m and photos.get('hero-main'):
        cap_main = re.search(r'<div class="ph main">.*?<span class="cap">(.*?)</span>', m.group(0), re.S).group(1)
        cap_small = re.search(r'<div class="ph small">.*?<span class="cap">(.*?)</span>', m.group(0), re.S).group(1)
        rep = shot(photos['hero-main'], cap_main, 'ph main shot')
        if photos.get('hero-small'):
            rep += shot(photos['hero-small'], cap_small, 'ph small shot')
        html = html[:m.start()] + rep + html[m.end():]
    g = re.search(r'(<div class="gallery reveal">)(.*?)(</div>\s*<p class="hint">)', html, re.S)
    if g and photos.get('gallery'):
        tiles = re.findall(r'<div class="ph">.*?<span class="cap">(.*?)</span></div>', g.group(2), re.S)
        raw = re.findall(r'<div class="ph">.*?</div>', g.group(2), re.S)
        out = ''
        for i, cap in enumerate(tiles):
            out += shot(photos['gallery'][i], cap) if i < len(photos['gallery']) else raw[i]
        html = html[:g.start()] + g.group(1) + out + g.group(3) + html[g.end():]
    return html

# ------------------------------------------------------------------ page chrome
def nav_html(lang, page):
    t = L[lang]
    out = []
    for href, key in NAV:
        here = ' class="is-here" aria-current="page"' if href == page else ''
        out.append('<a href="%s"%s>%s</a>' % (href, here, t['nav'][key]))
    return '\n      '.join(out)

SWITCH = ('<div class="langs" role="group" aria-label="Language">'
          '<button type="button" data-lang="vi" lang="vi">VI</button>'
          '<button type="button" data-lang="en" lang="en">EN</button>'
          '<button type="button" data-lang="zh" lang="zh">中文</button></div>')

def chrome(lang, page):
    t = L[lang]
    header = f'''<header class="header" id="top">
  <div class="wrap">
    <a class="brand" href="{HOME}" aria-label="{t['home_label']}"><span class="logo" role="img" aria-label="SunMoon Art &amp; Education"></span></a>
    <nav class="nav" aria-label="{t['menu']}">
      {nav_html(lang, page)}
    </nav>
    {SWITCH}
    <a class="btn btn-primary cta-desktop" href="{CONTACT}#trial">{t['cta']}</a>
    <button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="drawer"><span></span></button>
  </div>
</header>
<div class="drawer" id="drawer">
  {''.join(f'<a class="item" href="{href}">{t["nav"][key]}</a>' for href, key in NAV)}
  <a class="btn btn-primary" href="{CONTACT}#trial">{t['cta']}</a>
  {SWITCH}
  <p class="fine">{t['strap']}</p>
</div>'''
    return header

def page_head(lang, page):
    t = L[lang]
    if page == HOME:
        return ''
    eyebrow, title, lede = t['titles'][page]
    return f'''<section class="pagehead">
  <div class="wrap">
    <p class="eyebrow"><span class="sc">日月</span> {eyebrow}</p>
    <h1 class="h2">{title}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>'''

def footer_for(lang, page):
    _, _, tail = BODIES[lang]
    tail = rewrite_links(tail, page)
    # footer "Explore" list -> real page links
    t = L[lang]
    items = ''.join(f'<li><a href="{href}">{t["nav"][key]}</a></li>' for href, key in NAV if href != page) \
            or ''.join(f'<li><a href="{href}">{t["nav"][key]}</a></li>' for href, key in NAV)
    tail = re.sub(r'(<h4>[^<]*</h4>\s*)<ul>.*?</ul>', lambda m: m.group(1) + f'<ul>{items}</ul>', tail, count=1, flags=re.S)
    return tail

def home_classes(lang):
    return R(f'src/homeclasses-{lang}.html')

# --------------------------------------------------------------------- assemble
extra_css_tpl = R('src/pages.css') if os.path.exists('src/pages.css') else ''

def build_head(lang, page):
    t = L[lang]
    h = head_tpl
    title = 'SunMoon Art & Education' if page == HOME else f'{t["titles"][page][1]} · SunMoon'
    h = re.sub(r'<title>[^<]*</title>',
               f'<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{title}</title>', h, 1)
    h = h.replace('<link rel="preconnect" href="https://fonts.googleapis.com">',
                  f'<link rel="icon" type="image/png" href="{fav}">\n<link rel="preconnect" href="https://fonts.googleapis.com">', 1)
    css = f'''
.brand .logo{{display:block;height:56px;aspect-ratio:600/547;background:url("{logo_full}") center/contain no-repeat;transition:transform .3s ease}}
.brand:hover .logo{{transform:translateY(-1px)}}
.footer .brand-row{{display:flex;align-items:center;gap:1rem}}
.footer .logo-mark{{display:block;height:64px;aspect-ratio:400/333;background:url("{logo_mark}") center/contain no-repeat}}
.langs{{display:flex;align-items:center;gap:.2rem;border:1px solid var(--line-strong);border-radius:999px;padding:.2rem}}
.langs button{{font-size:.68rem;font-weight:600;letter-spacing:.08em;padding:.35rem .6rem;border-radius:999px;color:var(--ink-2);transition:background .2s,color .2s}}
.langs button:hover{{color:var(--ink)}}
.langs button[aria-pressed="true"]{{background:var(--ink);color:var(--ivory)}}
.header .langs{{margin-left:auto}}
@media (min-width:1120px){{.header .langs{{margin-left:0}}}}
.drawer .langs{{align-self:flex-start;margin-top:1.2rem}}
.drawer .langs button{{font-size:.85rem;padding:.5rem .9rem}}
.nav a.is-here{{color:var(--ink)}}
.nav a.is-here::after{{transform:scaleX(1)}}
.pagehead{{padding-block:clamp(2.5rem,6vw,4.5rem) clamp(1.5rem,3vw,2.5rem);border-bottom:1px solid var(--line)}}
.pagehead .h2{{margin-top:.8rem}}
.pagehead .lede{{margin-top:1.2rem}}
.pagehead + .section{{padding-top:clamp(3rem,6vw,4.5rem)}}
.homeclasses .grid{{display:grid;gap:1px;background:var(--line);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;margin-top:2.5rem}}
@media (min-width:640px){{.homeclasses .grid{{grid-template-columns:1fr 1fr}}}}
@media (min-width:1000px){{.homeclasses .grid{{grid-template-columns:repeat(4,1fr)}}}}
.hc{{background:var(--ivory);padding:1.6rem 1.4rem;display:flex;flex-direction:column;gap:.5rem;min-height:11rem;transition:background .3s ease}}
.hc:hover{{background:var(--ivory-2)}}
.hc .age{{font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3);font-weight:600}}
.hc h3{{font-size:1.35rem;line-height:1.1}}
.hc p{{font-size:.94rem;color:var(--ink-2);line-height:1.5}}
.hc .sc{{margin-top:auto;color:var(--vermilion);font-size:1.1rem}}
.homeclasses .more-link{{margin-top:2rem;display:inline-flex}}
:root[data-lang="zh"] .pagehead .h2{{font-weight:600}}
</style>'''
    h = re.sub(r'\.brand img\.logo\{.*?\.float-cta \.btn-zalo\{[^}]*\}\n', '', h, flags=re.S)
    photo_css = ''
    for name in ([v for k, v in photos.items() if k != 'gallery'] + list(photos.get('gallery', []))):
        if name:
            photo_css += f'.shot[data-photo="{name.rsplit(".",1)[0]}"]{{background-image:url("{photo_src(name)}")}}\n'
    return h.replace('</style>', css.replace('</style>', photo_css + '</style>'), 1)

def build_page(page):
    per_lang = {}
    for lang in LANGS:
        _, sec, _ = BODIES[lang]
        parts = [chrome(lang, page), '<main>', page_head(lang, page)]
        for key in PAGES[page]:
            html = home_classes(lang) if key == 'homeclasses' else sec[key]
            if page != HOME and key == 'about':
                html = html.replace('<section class="section intro" id="about">',
                                    '<section class="section intro no-top" id="about">')
            parts.append(rewrite_links(fill_photos(html), page))
        parts += ['</main>', footer_for(lang, page)]
        per_lang[lang] = '\n'.join(p for p in parts if p)
    head = build_head('vi', page)
    titles = {l: ('SunMoon Art & Education' if page == HOME else f'{L[l]["titles"][page][1]} · SunMoon') for l in LANGS}
    head += '\n<script>window.PAGE_TITLES=' + json.dumps(titles, ensure_ascii=False) + ';</script>'
    out = (head + '\n\n<div id="app">\n' + per_lang['vi'] + '\n</div>\n'
           + ''.join(f'<template id="tpl-{l}">\n{per_lang[l]}\n</template>\n' for l in LANGS)
           + '\n' + script)
    open(page, 'w', encoding='utf-8').write(out)
    return len(out)

total = 0
for page in PAGES:
    n = build_page(page); total += n
    print(f'{page:16} {n:>9,} bytes')
print(f'{"total":16} {total:>9,} bytes', '(inline photos)' if INLINE else '(assets/photos paths)')
