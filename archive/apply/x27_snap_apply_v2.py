#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x27_snap_apply_v2 — AE-Simulator · Х27 · S54 крок 1б «ЗЛІПОК + РЕМОНТ»
живе доки: стенд Х27 не отримав наступної редакції (тоді рецепт — архів)

Що робить: бере AE_X27_SIDEBAR_v5.html і вкладає в головну зону стенда
СТАТИЧНИЙ ЗЛІПОК реальних екранів продукту (picker · catalog), знятий
рушієм із піднятого дерева. Ізоляція — shadow DOM: жодне правило продукту
не може дотягтись до острівця й мовчки скасувати В-33.

Вхід : AE_X27_SIDEBAR_v5.html (Project) + snap.json (вивід snap.js)
Вихід: AE_X27_SIDEBAR_v6.html
Ідемпотентність: повторний прогін дає той самий md5 (П34 · П37).
"""
import json, sys, hashlib, re, os

SRC   = '/mnt/project/AE_X27_SIDEBAR_v5.html'
SNAP  = '/home/claude/snap.json'
DST   = '/mnt/user-data/outputs/AE_X27_SIDEBAR_v7.html'

BASE_MD5 = '4c1a6a64468ee514b4ca37cd9b8bbed3'   # index.html піднятого дерева

def die(m):
    print('ПРОВАЛ:', m); sys.exit(1)

SHADOW_FIX = (
"\n/* == ПРАВКА СТЕНДА, не продукту (S54) ==============================\n"
"   Обгортка .v2 у тіні непрозора (.v2{background:var(--canvas)}) і накривала\n"
"   тон головної зони: при трьох значеннях --isl-main мінялось 0,01 % пікселів.\n"
"   Прозора обгортка повертає важелю видимість. */\n"
".v2{background:transparent}\n")

html = open(SRC, encoding='utf-8').read()
d    = json.load(open(SNAP, encoding='utf-8'))

# ── 1. CSS продукту: :root → :host (рівно одне входження, перевірено грепом) ──
css_parts, root_hits = [], 0
for c in d['css']:
    t = c['t']
    n = t.count(':root')
    root_hits += n
    if n:
        t = t.replace(':root', ':host', 1)
    css_parts.append('/* ── блок продукту: %s ── */\n%s' % (c['id'], t))
if root_hits != 1:
    die(':root входжень %d, очікувалось 1 — заміна стала неоднозначною' % root_hits)
CSS = '\n'.join(css_parts) + SHADOW_FIX

# ── 2. корінь зліпка мусить бути <main> ──
for k in ('picker', 'catalog'):
    if not d[k].lstrip().startswith('<main'):
        die('зліпок %s не починається з <main>' % k)

# ── 3. розмітка: заповнювач стає ЗАПАСНИМ вмістом хоста ──
OLD_MAIN = '''    <main><div class="fill">
      <h1>Тренування</h1><p>Заповнювач сусідньої зони — лише форма й щільність (П48).</p>
      <div class="cards">
        <div class="ph"></div><div class="ph"></div><div class="ph"></div>
        <div class="ph"></div><div class="ph"></div><div class="ph"></div>
      </div>
    </div></main>'''
NEW_MAIN = '''    <main><div class="snap" id="snapHost"><div class="fill">
      <h1>Тренування</h1><p>Зліпок НЕ змонтовано — це запасний заповнювач (П48). Дивись стрічку заміру.</p>
      <div class="cards">
        <div class="ph"></div><div class="ph"></div><div class="ph"></div>
        <div class="ph"></div><div class="ph"></div><div class="ph"></div>
      </div>
    </div></div></main>'''
if html.count(OLD_MAIN) != 1:
    die('заповнювач v5 не знайдено дослівно (шукано 1, знайдено %d)' % html.count(OLD_MAIN))
html = html.replace(OLD_MAIN, NEW_MAIN)

# ── 4. CSS хоста. Хост НЕ фарбує нічого: тон головної лишається за --isl-main,
#      інакше важіль tMain помер би за каскадом (§8.7-в). ──
HOST_CSS = '''
/* ══ 2б · зліпок реального екрана (П50) ══════════════════════════════════
   Хост прозорий навмисне: тон головної зони лишається за важелем --isl-main.
   Ізоляція — shadow DOM, не префікси: правило продукту фізично не дотягнеться
   до острівця (В-33) і не скасує його мовчки. */
.v2 .snap{display:block;height:100%;overflow:hidden;background:transparent;
          border-radius:var(--isl-radius)}
'''
OLD_FILL_ANCHOR = '.v2 .fill .ph{height:146px;border:1px solid var(--line);border-radius:12px;background:#fff}'
if html.count(OLD_FILL_ANCHOR) != 1:
    die('якір CSS заповнювача не знайдено')
html = html.replace(OLD_FILL_ANCHOR, OLD_FILL_ANCHOR + '\n' + HOST_CSS.strip())

# ── 5. важіль вибору екрана ──
OLD_LEVER = '''  <div class="grp"><label>тон · головна</label>'''
NEW_LEVER = '''  <div class="grp"><label>зліпок екрана</label>
    <select id="tScreen"><option value="picker" selected>Тренування (сценарії)</option>
    <option value="catalog">Каталог</option></select></div>
  <div class="grp"><label>тон · головна</label>'''
if html.count(OLD_LEVER) != 1:
    die('якір важеля tMain не знайдено')
html = html.replace(OLD_LEVER, NEW_LEVER)

# ── 6. лотки зліпка ──
TPL = ('\n<template id="snapCSS"><style>%s</style></template>\n'
       '<template id="snapSprite">%s</template>\n'
       '<template id="snapPicker">%s</template>\n'
       '<template id="snapCatalog">%s</template>\n'
       % (CSS, d['sprite'], d['picker'], d['catalog']))
if html.count('\n<script>') < 1:
    die('не знайдено <script> для вставки лотків')
html = html.replace('\n<script>', TPL + '\n<script>', 1)

# ── 7. монтаж + детектори ──
JS = r'''
/* ══ зліпок реального екрана · S54 крок 1 (П50) ═══════════════════════════
   Ізоляція shadow DOM. Обгортка .v2 всередині тіні обов'язкова: усі правила
   продукту писані як ".v2 …", а зовнішній .v2 крізь межу тіні не видно. */
var SNAP = {ok:false, why:'не запускалось', screen:'picker'};
function snapMount(name){
  var host = g('snapHost'); if(!host) { SNAP.why='немає хоста'; return; }
  try{
    var root = host.shadowRoot || host.attachShadow({mode:'open'});
    var tplCSS = g('snapCSS'), tplSpr = g('snapSprite'), tpl = g('snap'+name.charAt(0).toUpperCase()+name.slice(1));
    if(!tplCSS || !tpl){ SNAP.why='немає лотка'; return; }
    root.innerHTML = '';
    root.appendChild(tplCSS.content.cloneNode(true));
    root.appendChild(tplSpr.content.cloneNode(true));
    var box = document.createElement('div'); box.className = 'v2';
    box.appendChild(tpl.content.cloneNode(true));
    root.appendChild(box);
    host.firstElementChild && host.firstElementChild.remove();   /* геть запасний заповнювач */
    SNAP.ok = !!root.querySelector('.v2 .page'); SNAP.screen = name;
    SNAP.why = SNAP.ok ? 'ok' : 'лоток порожній';
  }catch(e){ SNAP.why = 'shadow: ' + e.message; }
}
function snapChecks(){
  var host = g('snapHost'), main = V2.querySelector('main'), shell = V2.querySelector('.shell');
  var r = [];
  r.push(['зліпок змонтовано', SNAP.ok, SNAP.why]);
  /* правило продукту НЕ дістає за межі тіні: поза shadow вузлів зліпка немає */
  r.push(['витоку за межі тіні немає', document.querySelector('.scenario-item')===null
          && document.querySelector('.page')===null, 'поза тінню']);
  /* важіль tMain живий (не мертвий за каскадом, §8.7-в): фарба main == вибране */
  var want = g('tMain').value, got = getComputedStyle(main).backgroundColor;
  r.push(['важіль тону живий', hex(got)===want.toUpperCase(), got]);
  /* хост нічого не фарбує — інакше він вирішував би тон замість важеля (П50) */
  var hb = getComputedStyle(host).backgroundColor;
  r.push(['хост прозорий', hb==='rgba(0, 0, 0, 0)' || hb==='transparent', hb]);
  /* П45 · третє число ОБЧИСЛЕНЕ, не скопійоване з правила, яке ми переносили */
  var inset = parseFloat(getComputedStyle(V2).getPropertyValue('--isl-inset')) || 0;
  var bw    = Math.round(parseFloat(getComputedStyle(main).borderTopWidth)) || 0;
  var want2 = shell.clientHeight - inset*2 - bw*2, got2 = main.clientHeight;
  r.push(['висота main = сцена − відступ×2 − кант×2', Math.abs(want2-got2)<=1, got2+' / '+want2]);
  return r;
}
function hex(rgb){ var m=rgb.match(/\d+/g); if(!m) return rgb;
  return '#'+m.slice(0,3).map(function(x){return ('0'+(+x).toString(16)).slice(-2);}).join('').toUpperCase(); }
'''
OLD_LOGO = "g('logo').addEventListener('click', function(){"
if html.count(OLD_LOGO) != 1:
    die('якір JS (logo) не знайдено')
html = html.replace(OLD_LOGO, JS.strip() + '\n' + OLD_LOGO)

BOOT = r'''
g('tScreen').addEventListener('change', function(){ snapMount(this.value); measure(); });
snapMount('picker');
'''
OLD_BOOT = "['rY','rBl','rSp','rA'].forEach"
if html.count(OLD_BOOT) != 1:
    die('якір JS (boot) не знайдено')
html = html.replace(OLD_BOOT, BOOT.strip() + '\n' + OLD_BOOT)

# ── 10. третє положення осі оболонки: острівець лише під панеллю ──
OLD_ROW = '    <button type="button" data-v="island">острівець</button></div></div>'
NEW_ROW = ('    <button type="button" data-v="island">острівець</button>\n'
           '    <button type="button" data-v="solo">лише панель</button></div></div>')
if html.count(OLD_ROW) != 1:
    die('ряд осі оболонки не знайдено')
html = html.replace(OLD_ROW, NEW_ROW)

SOLO_CSS = (
"/* == вісь оболонки · третє положення «лише панель» (S54) ==============\n"
"   Питання оператора: чому головна зона стала другою карткою, всередині\n"
"   якої лежать ще картки. У продукті main власного фону НЕ має — фарбує\n"
"   .v2. Це положення знімає з main кант, радіус і тінь, лишаючи острівцем\n"
"   саму панель: рівнів глибини два замість трьох. */\n"
'.v2[data-shell="solo"] .shell{background:var(--isl-canvas);padding:var(--isl-inset);\n'
"                              gap:var(--isl-inset);grid-template-columns:var(--side-w) minmax(0,1fr)}\n"
'.v2[data-shell="solo"] .sidebar{border:var(--isl-border-w) solid var(--isl-border);\n'
"                                border-radius:var(--isl-radius);background:var(--isl-surface);\n"
"                                box-shadow:var(--isl-shadow);backdrop-filter:blur(var(--isl-blur))}\n"
'.v2[data-shell="solo"] main{border:0;border-radius:0;background:var(--isl-main);box-shadow:none}'
)
ANCHOR_SOLO = '.v2[data-shell="flush"] .shell{grid-template-columns:var(--side-w) minmax(0,1fr)}'
if html.count(ANCHOR_SOLO) != 1:
    die('якір осі оболонки (flush) не знайдено')
html = html.replace(ANCHOR_SOLO, ANCHOR_SOLO + '\n' + SOLO_CSS)

OLD_WANT = "var want = state.shell==='island' ? stH-2*inset : stH;"
NEW_WANT = "var want = state.shell!=='flush' ? stH-2*inset : stH;"
if html.count(OLD_WANT) != 1:
    die('обчислення висоти панелі не знайдено')
html = html.replace(OLD_WANT, NEW_WANT)

# ── 11. заливка низу доходить до краю панелі (дефект S54: лишалось 20px) ──
OLD_FOOT = '.v2 .side-bottom{background:var(--isl-foot);margin:auto -8px 0;padding:12px 10px 0;'
NEW_FOOT = '.v2 .side-bottom{background:var(--isl-foot);margin:auto -8px -20px;padding:12px 10px 20px;'
if html.count(OLD_FOOT) != 1:
    die('правило заливки низу не знайдено')
html = html.replace(OLD_FOOT, NEW_FOOT)
OLD_RAIL = '.v2[data-mode="rail"] .side-bottom{padding:12px 0 0}'
NEW_RAIL = '.v2[data-mode="rail"] .side-bottom{padding:12px 0 20px}'
# ⚠ у v5 це правило записано ДВІЧІ (:108 і :136) — правимо обидва входження
if html.count(OLD_RAIL) != 2:
    die('правило заливки низу (рейка): очікувалось 2 входження, знайдено %d' % html.count(OLD_RAIL))
html = html.replace(OLD_RAIL, NEW_RAIL)

# ── 12. драбина тінтів Y15 · Y20 · Y25 у чотири селектори тону ──
#   обчислено від канонічного жовтого брендбука #FFE241
#   (Pantone P 4-7 C · RGB 255 226 65 · стор.12): tint(p)=255-(255-c)*p.
#   Y5=#FFFEF6 (теперішній canvas) · Y10=#FFFCEC (теперішній plate) ·
#   Y25=#FFF8D0 (= --anc-yellow-25 продукту).
LADDER = [('#FFFBE2', 'Y15'), ('#FFF9D9', 'Y20'), ('#FFF8D0', 'Y25')]
added = 0
for sel in ('tHead', 'tBody', 'tFoot', 'tMain'):
    a = html.find('id="%s"' % sel)
    if a < 0:
        die('селектор %s не знайдено' % sel)
    b = html.find('</select>', a)
    if b < 0:
        die('у %s не закрито список' % sel)
    block, ins = html[a:b], ''
    for val, lab in LADDER:
        if val.lower() not in block.lower():          # Y25 уже стоїть у tHead як yellow-25
            ins += '<option value="%s">%s</option>' % (val, lab)
            added += 1
    html = html[:b] + ins + html[b:]
if added != 3 + 3 + 3 + 3 - 1:                        # мінус той Y25, що вже був у tHead
    die('драбина: вставлено %d опцій, очікувалось 11' % added)

# ── 13. детектор тону: судимо ВИДИМІСТЬ, не оголошення (Д-И) ──
OLD_DET = """  /* важіль tMain живий (не мертвий за каскадом, §8.7-в): фарба main == вибране */
  var want = g('tMain').value, got = getComputedStyle(main).backgroundColor;
  r.push(['важіль тону живий', hex(got)===want.toUpperCase(), got]);"""
NEW_DET = """  /* Попередня редакція питала getComputedStyle(main) і світила зелене на
     важелі, якого око не бачило: обгортка зліпка його накривала (Д-И). */
  var want = g('tMain').value, got = getComputedStyle(main).backgroundColor;
  r.push(['важіль тону оголошений', hex(got)===want.toUpperCase(), got]);
  var vis = toneVisible(main);
  r.push(['тон видно на екрані', vis > 0, vis.toFixed(1) + ' % площі головної']);"""
if html.count(OLD_DET) != 1:
    die('детектор тону не знайдено')
html = html.replace(OLD_DET, NEW_DET)

TONEVIS = """
/* Частка площі головної зони, де тон реально проступає: сітка проб, у кожній
   спускаємось у тінь і йдемо вгору предками — якщо хоч один непрозорий, точка
   закрита. Рахуємо DOM-ом, без канви: стенд мусить жити з file://. */
function toneVisible(main){
  var host = g('snapHost'); if(!host || !host.shadowRoot) return 100;
  var sr = host.shadowRoot, b = main.getBoundingClientRect(), open = 0, all = 0;
  for(var i=1;i<40;i++) for(var j=1;j<25;j++){
    var x = b.left + b.width*i/40, y = b.top + b.height*j/25; all++;
    var n = sr.elementFromPoint(x,y), covered = false;
    while(n && n !== sr){
      var bg = getComputedStyle(n).backgroundColor;
      if(bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent'){ covered = true; break; }
      n = n.parentElement;
    }
    if(!covered) open++;
  }
  return all ? 100*open/all : 0;
}
"""
html = html.replace(OLD_LOGO, TONEVIS.strip() + '\n' + OLD_LOGO)

# ── 8. шапка: провенанс (Д-В2) + «живе доки» (wsd 1.8) ──
OLD_HEAD = '''  AE-Simulator · харнес Х27 v3 «ОБОЛОНКА» · крок 1 з трьох
  живе доки: крок 2 «ПУНКТИ» не дав власного стенда (тоді цей — архів)'''
NEW_HEAD = '''  AE-Simulator · харнес Х27 v7 «ОБОЛОНКА + ЗЛІПОК + РЕМОНТ» · крок 1 з трьох
  живе доки: крок 2 «ПУНКТИ» не дав власного стенда (тоді цей — архів)
  база: AE/index.html md5 %s (дерево S53 §5, ланцюг із дев'яти рецептів);
        зліпок = outerHTML вузла «.v2 .shell > main», екрани picker + catalog,
        знято Chromium 1920×1080, 12.09.2026; CSS продукту — чотири теги «style»
        дослівно, єдина правка ":root" -> ":host" (одне входження, грепом).
  Зліпок нічого не вирішує (П50): власних кольорів, тіней і тонів не вносить,
  хост прозорий, тон головної зони лишається за важелем --isl-main.''' % BASE_MD5
if html.count(OLD_HEAD) != 1:
    die('шапка v5 не знайдена дослівно')
html = html.replace(OLD_HEAD, NEW_HEAD)
html = html.replace('<title>AE · Х27 v3 · ОБОЛОНКА</title>',
                    '<title>AE · Х27 v7 · ОБОЛОНКА + ЗЛІПОК</title>')

# ── 9. п'ять перевірок зліпка — у СТРІЧКУ на екрані, не в консоль (§3-п.12) ──
OLD_TAIL = """   тінь '+getComputedStyle(V2).getPropertyValue('--isl-shadow').trim();"""
NEW_TAIL = """   тінь '+getComputedStyle(V2).getPropertyValue('--isl-shadow').trim()
   + snapLine();"""
if html.count(OLD_TAIL) != 1:
    die('хвіст стрічки заміру не знайдено')
html = html.replace(OLD_TAIL, NEW_TAIL)

SNAPLINE = r'''
function snapLine(){
  var r = snapChecks(), s = '\nЗЛІПОК · екран ' + SNAP.screen + '\n';
  r.forEach(function(x){
    s += '  <b class="' + (x[1]?'ok':'bad') + '">' + (x[1]?'✓':'✗') + '</b> ' + x[0] +
         '   <span style="opacity:.65">' + x[2] + '</span>\n'; });
  return s;
}
'''
html = html.replace(OLD_LOGO, SNAPLINE.strip() + '\n' + OLD_LOGO)

os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, 'w', encoding='utf-8').write(html)
print('  %s' % DST)
print('  байт: %d · md5 %s' % (len(html.encode()), hashlib.md5(html.encode()).hexdigest()))
