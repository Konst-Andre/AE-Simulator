#!/usr/bin/env python3
# ae_bundle_v1_3.py — генератор превʼю AE-Simulator
#   v1_3 (Х22.4б, S43): рамка ширшає разом із вікном — ширина = max(1280, вікно),
#          масштаб лише коли вікно вужче за 1280. Причина: device S43 на 1920 —
#          рамка 1280 займала 67 % екрана (Math.min(1,…) лише зменшував). В-24: база 1920.
#          Замінює v1_2.
#   Х20.1: --desktop через viewport — НА ПРИСТРОЇ НЕ СПРАЦЮВАЛО (переглядач
#          файлів Claude ігнорує meta viewport). Х20.2: --desktop = РАМКА.
#
# живе доки: крок 8 SPEC §13.5 (прополка носіїв) не виніс вирок —
#            у tools/ репо продукту або в архів.
# дім: Project (вручну, як SPEC §13.6) до кроку 8.
#
# ЩО РОБИТЬ. index.html продукту читає 8 файлів через fetch і один через
# <script src>. Відкритий окремо (телефон, пісочниця) він показує порожні
# екрани. Скрипт робить із нього самодостатній двійник:
#   · <script src="tools/ae_rules.js"> → вміст файлу (як smoke_ui_v1.js:21–28);
#   · першим скриптом у <head> — прокладка: знімок файлів + підміна fetch;
#     шлях зі знімка віддається як Response, будь-яка інша адреса
#     відхиляється названою помилкою. Превʼю ФІЗИЧНО не публікує правку
#     (editEndpoint пише data/*.json у репо) і не ходить до моделі;
#   · там само: якщо localStorage кидає (непрозорий origin file://), —
#     сховище в памʼяті; інакше boot() падає на «Дані не завантажились»;
#   · шапка «згенеровано, не редагувати» + sha256 входів; [превʼю] у title;
#   · прокладка оголошує color-scheme: light (у продукту meta немає, у макета
#     є; переглядач у темній темі фарбував фон сторінки чорним — Х20.2);
#   · --desktop: превʼю вкладається в iframe srcdoc шириною max(1280, вікно);
#     вужче за 1280 — ширина 1280 і масштаб під екран (телефон). У рамки власний viewport, тож медіа
#     продукту рахуються від 1280 у будь-якому переглядачі (SPEC §11.8).
#     Вміст рамки — те саме превʼю байт-у-байт; смоук розпаковує і судить його.
# Код продукту більше НЕ змінюється нічим.
#
# ДІМ КОДУ — index.html. AE_preview_* — похідне: правка в ньому = загублена
# правка (12.11). Після кожної правки index.html превʼю генерується заново.
#
# МЕЖА ДЕТЕКТОРА. Знімок збирається з fetch('…')-ЛІТЕРАЛІВ у лапках.
# Шаблонний fetch(`data/${x}`) або змінна детектор НЕ бачить — такий файл
# у превʼю не потрапить, і екран буде порожнім. Додаєш у boot() fetch не
# літералом — розшир цей детектор у тому самому ході.
#
# ВИКЛИК:  python3 ae_bundle_v1_3.py [тека_продукту] -o AE_preview_X<хід>_v<n>.html [--desktop]
#          тека за замовчуванням: /mnt/user-data/outputs/AE
# КОД ВИХОДУ: 0 — зібрано; 1 — самоперевірка впала (файл НЕ пишеться).

import argparse, datetime, hashlib, json, os, re, sys

RULES_TAG = '<script src="tools/ae_rules.js"></script>'
RULES_PATH = 'tools/ae_rules.js'
META_CHARSET = '<meta charset="utf-8">'
DESKTOP_W = 1280
MSG = 'Превʼю: мережа вимкнена навмисно — це знімок, не застосунок (ae_bundle_v1).'
FETCH_LIT = re.compile(r"fetch\('([^']+)'\)")


def fail(why):
    print('✗ ' + why)
    sys.exit(1)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def script_unsafe(t):
    r"""Стани script-data з HTML-специфікації (спрощено до того, що рвe тег).
    data --'<!--'--> escaped --'-->'--> data
    escaped --'<script[ \t\n/>]'--> double --'</script…'--> escaped · double --'-->'--> data
    '</script' у data або escaped закриває тег передчасно → небезпечно.
    Кінець тексту в стані double → закриваючий </script> не спрацює → небезпечно.
    Груба ознака «є <!--» тут бреше: ae_rules.js:115 має <!--…--> в одному
    рядку, а :250 — «<script>» у коментарі, і це безпечно."""
    low, i, st, n = t.lower(), 0, 'data', len(t)
    end = lambda j, w: low.startswith(w, j) and (j + len(w) >= n or low[j + len(w)] in ' \t\n\r\f/>')
    while i < n:
        if st in ('data', 'escaped') and end(i, '</script'):
            return 'передчасне </script у позиції %d' % i
        if st == 'data' and low.startswith('<!--', i):
            st, i = 'escaped', i + 4; continue
        if st == 'escaped' and low.startswith('-->', i):
            st, i = 'data', i + 3; continue
        if st == 'escaped' and end(i, '<script'):
            st, i = 'double', i + 7; continue
        if st == 'double' and low.startswith('-->', i):
            st, i = 'data', i + 3; continue
        if st == 'double' and end(i, '</script'):
            st, i = 'escaped', i + 8; continue
        i += 1
    return 'текст закінчується в стані double-escaped' if st == 'double' else ''


def js_json(obj):
    # '<' → \u003c: валідно і в JSON, і в JS; жоден '</script' чи '<!--'
    # зі знімка не закриє тег і не перемкне парсер HTML.
    return json.dumps(obj, ensure_ascii=False).replace('<', '\\u003c')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?', default='/mnt/user-data/outputs/AE')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--desktop', action='store_true',
                    help='рамка max(1280, вікно); вужче — масштаб: ПК-розкладка на телефоні')
    a = ap.parse_args()

    idx_path = os.path.join(a.src, 'index.html')
    idx_b = open(idx_path, 'rb').read()
    html = idx_b.decode('utf-8')

    # ── самоперевірки входу ──────────────────────────────────────────
    if html.count(RULES_TAG) != 1:
        fail('тег %s знайдено %d разів, чекаю рівно 1' % (RULES_TAG, html.count(RULES_TAG)))
    if html.count(META_CHARSET) != 1:
        fail('%s знайдено %d разів, чекаю рівно 1' % (META_CHARSET, html.count(META_CHARSET)))
    if html.count('<title>') != 1:
        fail('<title> знайдено %d разів, чекаю рівно 1' % html.count('<title>'))
    other_src = re.findall(r'<script[^>]+src=', html)
    if len(other_src) != 1:
        fail('<script src> знайдено %d, вшивати вмію лише %s' % (len(other_src), RULES_PATH))

    paths = sorted(set(FETCH_LIT.findall(html)))
    if not paths:
        fail('жодного fetch(\'…\')-літерала — детектор або код змінились')
    snap, hashes = {}, {'index.html': sha(idx_b)}
    for p in paths:
        fp = os.path.join(a.src, p)
        if not os.path.isfile(fp):
            fail('fetch(\'%s\') є в коді, файла в теці немає — превʼю було б порожнім' % p)
        b = open(fp, 'rb').read()
        snap[p] = b.decode('utf-8')
        hashes[p] = sha(b)

    rules_b = open(os.path.join(a.src, RULES_PATH), 'rb').read()
    rules = rules_b.decode('utf-8')
    hashes[RULES_PATH] = sha(rules_b)
    why = script_unsafe(rules)
    if why:
        fail('%s не можна вшити у <script>: %s' % (RULES_PATH, why))

    # ── збирання ─────────────────────────────────────────────────────
    when = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
    head = ['<!--AE-BUNDLE:HEAD',
            '  ЗГЕНЕРОВАНО з index.html скриптом ae_bundle_v1.py · ' + when,
            '  НЕ РЕДАГУВАТИ. Правка тут = загублена правка: дім коду — index.html (12.11).',
            '  Мережа вимкнена: знімок файлів нижче, решта адрес відхиляється.',
            '  Вигляд: ' + ('ПК, рамка ≥1280 (прапорець desktop)' if a.desktop
                         else 'як у продукту'),
            '  sha256 входів:']
    head += ['    %s  %s' % (h, p) for p, h in hashes.items()]
    head.append('/AE-BUNDLE:HEAD-->')
    head_txt = '\n'.join(head)
    if '--' in head_txt[len('<!--'):-len('-->')]:
        fail('шапка містить «--» — коментар HTML зламався б')

    shim = ('<!--AE-BUNDLE:SHIM--><script>(function(){'
            'var SNAP=' + js_json(snap) + ';'
            'var MSG=' + js_json(MSG) + ';'
            'function resp(t){'
            'if(typeof Response==="function")return new Response(t,{status:200});'
            'return {ok:true,status:200,headers:{get:function(){return null;}},'
            'json:function(){return Promise.resolve(JSON.parse(t));},'
            'text:function(){return Promise.resolve(t);}};}'
            'var f=function(u,o){'
            'var k=typeof u==="string"?u:(u&&u.url)||"";'
            'var m=((o&&o.method)||"GET").toUpperCase();'
            'if(m==="GET"&&Object.prototype.hasOwnProperty.call(SNAP,k))return Promise.resolve(resp(SNAP[k]));'
            'return Promise.reject(new Error(MSG));};'
            'f.__aeShim=true;window.fetch=f;'
            'if(!document.querySelector(\'meta[name="color-scheme"]\')){'
            'var cs=document.createElement("meta");cs.name="color-scheme";cs.content="light";'
            'document.head.appendChild(cs);}'
            # Непрозорий origin (file://): звернення до localStorage кидає, boot()
            # ловить це і малює «Дані не завантажились». Підставляємо сховище в
            # памʼяті ЛИШЕ якщо справжнє кидає; де воно є — нічого не робимо.
            'try{window.localStorage.getItem("__ae");}catch(e){'
            'var m={};var mem={getItem:function(k){return Object.prototype.hasOwnProperty.call(m,k)?m[k]:null;},'
            'setItem:function(k,v){m[k]=String(v);},removeItem:function(k){delete m[k];},'
            'clear:function(){m={};},key:function(i){return Object.keys(m)[i]||null;},'
            'get length(){return Object.keys(m).length;}};'
            'Object.defineProperty(window,"localStorage",{value:mem,configurable:true});'
            'window.__aeMemStorage=true;}'
            '})();</script><!--/AE-BUNDLE:SHIM-->')

    out = html
    # шапка ПІСЛЯ meta charset: ~1 КБ хешів перед ним виштовхнули б його
    # за перші 1024 байти (самоперевірка нижче це й спіймала першим прогоном)
    out = out.replace(META_CHARSET, META_CHARSET + '\n' + head_txt + '\n' + shim, 1)
    out = out.replace('<title>', '<title>[превʼю] ', 1)
    out = out.replace(RULES_TAG,
                      '<!--AE-BUNDLE:RULES--><script>' + rules + '</script><!--/AE-BUNDLE:RULES-->', 1)

    # ── самоперевірки виходу ─────────────────────────────────────────
    ob = out.encode('utf-8')
    if ob.find(META_CHARSET.encode()) > 1024:
        fail('meta charset вийшов за перші 1024 байти — браузер може не розпізнати UTF-8')
    if re.search(r'<script[^>]+src=', out):
        fail('у превʼю лишився <script src> — телефон його не завантажить')
    if 'AE-BUNDLE:HEAD' not in out or '__aeShim' not in out:
        fail('шапка або прокладка не вставились')

    if a.desktop:
        # Переглядач файлів Claude перебиває фон html/body в обох документах
        # (device, Х20.2). Фарбуємо власний шар і саму рамку кольором --paper,
        # узятим з index.html, — не вписаним руками.
        pm = re.search(r'--paper:\s*(#[0-9A-Fa-f]{3,8})', html)
        if not pm:
            fail('--paper не знайдено в index.html — фону рамки нема звідки взяти')
        paper = pm.group(1)
        # < і > теж: інакше вкладені <script> стоять у файлі відкритим текстом і
        # валідатор бере їх за скрипти рамки (✗3 першим прогоном Х20.2)
        srcdoc = (out.replace('&', '&amp;').replace('"', '&quot;')
                     .replace('<', '&lt;').replace('>', '&gt;'))
        frame = ('<!doctype html>\n<html lang="uk">\n<head>\n<meta charset="utf-8">\n'
                 '<!--AE-BUNDLE:FRAME\n'
                 '  ЗГЕНЕРОВАНО ae_bundle_v1_3.py · ' + when + ' · НЕ РЕДАГУВАТИ.\n'
                 '  Рамка ПК: iframe = max(' + str(DESKTOP_W) + ' px, вікно); вужче — масштаб під екран.\n'
                 '  Вміст рамки = превʼю байт-у-байт (шапка з sha256 — усередині).\n'
                 '/AE-BUNDLE:FRAME-->\n'
                 '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                 '<meta name="color-scheme" content="light">\n'
                 '<title>[превʼю ПК] AE-Simulator</title>\n'
                 '<style>html,body{margin:0;height:100%;overflow:hidden}'
                 '#ae-bg{position:fixed;top:0;right:0;bottom:0;left:0;background:' + paper + '}'
                 '#ae-frame{position:relative;border:0;display:block;transform-origin:0 0;background:' + paper + '}</style>\n'
                 '</head>\n<body>\n<div id="ae-bg"></div>\n'
                 '<iframe id="ae-frame" title="AE-Simulator — превʼю ПК" srcdoc="' + srcdoc + '"></iframe>\n'
                 '<script>(function(){var W=' + str(DESKTOP_W) + ',f=document.getElementById("ae-frame");'
                 'function fit(){var iw=window.innerWidth,w=Math.max(W,iw),s=Math.min(1,iw/W);'
                 'f.style.width=w+"px";f.style.height=(window.innerHeight/s)+"px";'
                 'f.style.transform="scale("+s+")";}'
                 'fit();window.addEventListener("resize",fit);})();</script>\n'
                 '</body>\n</html>\n')
        ob = frame.encode('utf-8')
    open(a.out, 'wb').write(ob)
    print('✓ %s · %d КБ · знімок %d файлів + %s · вигляд: %s' % (
        a.out, len(ob) // 1024, len(snap), RULES_PATH, 'ПК, рамка ≥1280' if a.desktop else 'продукт'))
    for p in paths:
        print('    %s' % p)


if __name__ == '__main__':
    main()
