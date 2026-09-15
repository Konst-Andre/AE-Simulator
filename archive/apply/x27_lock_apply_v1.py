# x27_lock_apply_v1.py — Х27 хід А: AE_X27_SIDEBAR_v8.html → v9
#   1. канал ін'єкції CSS у shadowRoot зліпка (<style id="lv-page">, ОСТАННІМ вузлом)
#   2. важіль В-37 «сторінка»: центр 1440 | ліворуч 1440 | на всю
#   3. важіль Х28 «підзаголовок»: є | нема
#   4. К2 ЛОК-регістр (маніфест §3 п.13): data-k на кожному важелі · LEVER_LOCK ·
#      маркер біля важеля у трьох станах · покриття «ЛОК n/m», добір ЗА ОЗНАКОЮ
# живе доки: вироки Х27 не переїхали в SPEC §13.3 (тоді канон — там, а рецепт в архів)
# дім: /mnt/user-data/outputs (робоча копія сесії, 1.6/10.7)
# запуск: python3 x27_lock_apply_v1.py <v8.html> <v9.html>
#   повтор на вже готовому v9 — exit 0 без змін (П34), md5 той самий (П37)
# ШАБЛОНІВ ЗЛІПКА (snapCSS · snapSprite · snapPicker · snapCatalog) НЕ ЧІПАЄ —
# дерево продукту піднімати не треба.
import sys, os, hashlib

src = sys.argv[1] if len(sys.argv) > 1 else 'AE_X27_SIDEBAR_v8.html'
dst = sys.argv[2] if len(sys.argv) > 2 else 'AE_X27_SIDEBAR_v9.html'
s = open(src, encoding='utf-8').read()

# ── 1. data-k на 21 наявний важіль ───────────────────────────────────────────
KEYS = [
    ('<label>оболонка</label>',                        'shell'),
    ('<label>розділювачі</label>',                     'rule'),
    ('<label>стан</label>',                            'mode'),
    ('<label>тінь (elevation)</label>',                'elev'),
    ('<label>радіус <output id="oR">',                 'radius'),
    ('<label>відступ <output id="oI">',                'inset'),
    ('<label>кадр</label>',                            'frame'),
    ('<label>висота панелі</label>',                   'fit'),
    ('<label>пунктів</label>',                         'set'),
    ('<label>неготові</label>',                        'stub'),
    ('<label>тінь · Y <output id="oY">',               'shY'),
    ('<label>тінь · розмиття <output id="oBl">',       'shBlur'),
    ('<label>тінь · розхід <output id="oSp">',         'shSpread'),
    ('<label>тінь · щільність <output id="oA">',       'shAlpha'),
    ('<label>тон · шапка</label>',                     'toneHead'),
    ('<label>тон · тіло</label>',                      'toneBody'),
    ('<label>тон · низ</label>',                       'toneFoot'),
    ('<label>зліпок екрана</label>',                   'screen'),
    ('<label>канва острівця</label>',                  'canvas'),
    ('<label>підпис низу</label>',                     'door'),
    ('<label>тон · головна</label>',                   'toneMain'),
]
PAIRS = [('data-k ' + k, '<div class="grp">' + lab, '<div class="grp" data-k="' + k + '">' + lab)
         for lab, k in KEYS]

# ── 2. два нові важелі — у кінець бару ───────────────────────────────────────
NEW_LEVERS = '''  <div class="grp" data-k="page"><label>сторінка</label><div class="row" data-ax="page">
    <button type="button" data-v="center">центр 1440</button>
    <button type="button" data-v="left">ліворуч 1440</button>
    <button type="button" data-v="full">на всю</button></div></div>
  <div class="grp" data-k="sub"><label>підзаголовок</label><div class="row" data-ax="sub">
    <button type="button" data-v="shown">є</button>
    <button type="button" data-v="hidden">нема</button></div></div>
</div>

<div class="meter hid">'''
PAIRS.append(('нові важелі page/sub', '</div>\n\n<div class="meter hid">', NEW_LEVERS))

# ── 3. CSS маркера ЛОКу ──────────────────────────────────────────────────────
LK_CSS = '''.grp .lk{margin-left:6px;font:10px/1 ui-monospace,SFMono-Regular,monospace;
  letter-spacing:0;text-transform:none;white-space:nowrap}
.lk-ok{color:#1f7a3f}.lk-bad{color:#a51f37}.lk-no{color:#9aa0a6}
.v2 .side-link.stub{color:var(--anc-gray-light);cursor:default}'''
PAIRS.append(('CSS маркера', '.v2 .side-link.stub{color:var(--anc-gray-light);cursor:default}', LK_CSS))

# ── 4. state: два нові ключі + ДІМ каналу ─────────────────────────────────────────────────
PAIRS.append(('state page/sub',
    "frame:'edge', fit:'full', set:'4', stub:'shown' };",
    "frame:'edge', fit:'full', set:'4', stub:'shown',\n"
    "              page:'center', sub:'shown' };\n"
    "/* вузол каналу важелів сторінки. Оголошений ТУТ, а не в блоці нижче:\n"
    "   snapMount() кладе в нього style раніше, ніж виконається хвіст скрипта,\n"
    "   і присвоєння \"var LV = null\" у хвості затирало б його — важіль ставав\n"
    "   би мертвим мовчки (заміряно Chromium, перший прогін ходу А). */\n"
    "var LV = null;"))

# ── 5. apply(): фарбувати нові рядки + гнати CSS у тінь ──────────────────────
PAIRS.append(('apply: page/sub',
    "  ['shell','rule','mode','elev','frame','fit','set','stub'].forEach(function(k){ paintRow(k, state[k]); });\n"
    "  measure();",
    "  ['shell','rule','mode','elev','frame','fit','set','stub','page','sub']\n"
    "    .forEach(function(k){ paintRow(k, state[k]); });\n"
    "  paintPage();\n"
    "  measure();"))

# ── 6. snapMount(): канал ін'єкції ОСТАННІМ вузлом (8.7-в) ───────────────────
PAIRS.append(('канал lv-page',
    "    root.appendChild(box);\n"
    "    host.firstElementChild && host.firstElementChild.remove();",
    "    root.appendChild(box);\n"
    "    /* Х27 хід А · канал важелів сторінки. ОСТАННІМ вузлом тіні: при рівній\n"
    "       специфічності виграє останнє правило, інакше — 8.7-в «мертвий за каскадом».\n"
    "       Шаблонів зліпка не чіпає: це окремий вузол style, а не правка snapCSS. */\n"
    "    LV = document.createElement('style'); LV.id = 'lv-page';\n"
    "    root.appendChild(LV); paintPage();\n"
    "    host.firstElementChild && host.firstElementChild.remove();"))

# ── 7. блок ЛОКу + paintPage() — перед хвостом ініціалізації ─────────────────
BLOCK = r'''
/* ══ Х27 хід А · ВАЖЕЛІ СТОРІНКИ (В-37 · Х28) ════════════════════════════════
   .page живе в зліпку (:783) і в продукті (AE_WORK_index_X24_5_v1.html:457).
   Медіа-правила зліпка (:894 :926) чіпають лише padding — важіль б'є в
   max-width/margin, і селектор «.v2 .page» (0,2,0) перебиває «.page» (0,1,0)
   навіть усередині @media. Тому одного правила поза медіа досить.
   ⚠ Це стенд: у продукт число не їде, доки не стане ЛОКом і не ляже в SPEC §13.3. */
function paintPage(){
  if(!LV) return;
  var css = '';
  if(state.page==='center') css += '.v2 .page{max-width:1440px;margin-left:auto;margin-right:auto}';
  if(state.page==='left')   css += '.v2 .page{max-width:1440px;margin-left:0;margin-right:auto}';
  if(state.page==='full')   css += '.v2 .page{max-width:none;margin-left:0;margin-right:0}';
  if(state.sub==='hidden')  css += '.v2 .page-title p{display:none}';
  LV.textContent = css;
}

/* ══ Х27 К2 · ЛОК-РЕГІСТР (Lens_stagebench_manifest §3 п.13) ═════════════════
   ДІМ (12.11):
     · живе значення важеля — var state (рядки-важелі) або сам DOM-контрол;
     · КАНОН — LEVER_LOCK нижче. Другий дім канону — SPEC §13.3; п.13-в:
       запис лише в одне з двох вважається незробленим.
     · стан «рейка/розгорнуто» — state.mode → атрибут data-mode на .v2.
       У ПРОДУКТІ дому нема: логотип там панель не перемикає (борг Х27 кроку 3).
     · токени --isl-* — оголошені в .v2 у таблиці стилів цього стенда (:117–:129).
       У продукті їх теж нема; вони народжені Х27 і мусять приїхати разом із вироками.
   Чому регістр майже порожній: жоден вирок Х27 ще не записано канном. Це не
   недогляд — це рівно те, що регістр мусить показати перед переносом (п.13). */
var LEVER_LOCK = {
  set: '2'   /* V2_NAV: у продукті сьогодні два пункти (SETS, Д-В2). Дефолт стенда — 4,
                тож маркер мусить надрукувати КАНОН, а не живе число. */
};
function leverGrps(){ return document.querySelectorAll('.grp[data-k]'); }
function leverLive(grp){
  var row = grp.querySelector('[data-ax]');
  if(row) return state[row.dataset.ax];
  var el = grp.querySelector('input[type=range], select');
  return el ? el.value : null;
}
/* п.13-б: мертвий важіль не потрапляє в 📋 — інакше його число стає хибним каноном.
   ⚠ Ловиться лише прихований важіль. Повний детектор чотирьох класів §8.7
   (верстка · каскад · оптика) — БОРГ, названий, не закритий. */
function leverDead(grp){ return getComputedStyle(grp).display === 'none'; }
function lockScan(){
  var gs = leverGrps(), live = 0, locked = 0, diff = [];
  for(var i=0;i<gs.length;i++){
    var grp = gs[i], k = grp.dataset.k;
    var mark = grp.querySelector('.lk');
    if(!mark){ mark = document.createElement('span'); mark.className = 'lk';
               grp.querySelector('label').appendChild(mark); }
    var dead = leverDead(grp);
    var has  = Object.prototype.hasOwnProperty.call(LEVER_LOCK, k);
    var now  = leverLive(grp);
    if(dead){ mark.className = 'lk lk-no'; mark.textContent = '(мертвий)'; continue; }
    live++;
    if(!has){ mark.className = 'lk lk-no'; mark.textContent = 'нема ЛОКу'; continue; }
    locked++;
    if(String(now) === String(LEVER_LOCK[k])){ mark.className = 'lk lk-ok'; mark.textContent = '= ЛОК'; }
    else { mark.className = 'lk lk-bad'; mark.textContent = 'ЛОК ' + LEVER_LOCK[k];
           diff.push(k + ' (живе ' + now + ' ≠ ЛОК ' + LEVER_LOCK[k] + ')'); }
  }
  return { live: live, locked: locked, diff: diff };
}
function lockLine(){
  var r = lockScan();
  return '\nЛОК-РЕГІСТР (§3 п.13)\n' +
    '  покриття  <b class="' + (r.locked===r.live?'ok':'bad') + '">ЛОК ' + r.locked + '/' + r.live +
    ' важелів</b>   добір за ознакою data-k\n' +
    '  розбіжності  ' + (r.diff.length ? r.diff.join(' · ') : '—') + '\n';
}
'''
PAIRS.append(('блок ЛОКу', "bind('rR','oR','--isl-radius','px');", BLOCK + "\nbind('rR','oR','--isl-radius','px');"))

# ── 8. measure(): зазор ліворуч/праворуч + рядок ЛОКу ────────────────────────
PAIRS.append(('замір зазору',
    "  var ok=function(v,t){ return '<b class=\"'+(v===t?'ok':'bad')+'\">'",
    "  /* П52/П57: важіль сторінки судиться ПІКСЕЛЯМИ того місця, куди воно йде,\n"
    "     а не оголошенням. Ліворуч — від правого краю рейки до краю .page. */\n"
    "  var pgL='—', pgR='—', hostEl=g('snapHost');\n"
    "  if(hostEl && hostEl.shadowRoot){\n"
    "    var pg=hostEl.shadowRoot.querySelector('.v2 .page'), mn=V2.querySelector('main');\n"
    "    if(pg && mn){ var pr=pg.getBoundingClientRect(), mr=mn.getBoundingClientRect();\n"
    "      pgL=Math.round(pr.left-sd.right); pgR=Math.round(mr.right-pr.right); }\n"
    "  }\n"
    "  var ok=function(v,t){ return '<b class=\"'+(v===t?'ok':'bad')+'\">'"))
PAIRS.append(('рядок заміру',
    "   '   тінь '+getComputedStyle(V2).getPropertyValue('--isl-shadow').trim()\n   + snapLine();",
    "   '   тінь '+getComputedStyle(V2).getPropertyValue('--isl-shadow').trim()+'\\n'+\n"
    "   '  сторінка '+state.page+'   зазор рейка→контент '+pgL+' px   праворуч '+pgR+' px'+\n"
    "   '   підзаголовок '+state.sub+'\\n'\n"
    "   + lockLine() + snapLine();"))

# ── 9. копі 📋 · марка версії ────────────────────────────────────────────────
PAIRS.append(('копі: сторінка',
    "    'ширина рейки=72 (В-36)',",
    "    'ширина рейки=72 (В-36)',\n"
    "    'сторінка='+state.page+'  підзаголовок='+state.sub,"))
PAIRS.append(('марка копі', "'AE · Х27 v8 · стан важелів'", "'AE · Х27 v9 · стан важелів'"))
PAIRS.append(('title', '<title>AE · Х27 v7 · ОБОЛОНКА + ЗЛІПОК</title>',
                       '<title>AE · Х27 v9 · ОБОЛОНКА + ЗЛІПОК + ЛОК</title>'))

# ── застосування ─────────────────────────────────────────────────────────────
done = [(new in s) for _, old, new in PAIRS]
if all(done):
    if not os.path.exists(dst) or open(dst, encoding='utf-8').read() != s:
        open(dst, 'w', encoding='utf-8').write(s)
    print('уже застосовано — без змін ·', dst, hashlib.md5(s.encode('utf-8')).hexdigest())
    sys.exit(0)
assert not any(done), ('часткове застосування', [p[0] for p, d in zip(PAIRS, done) if d])
for name, old, new in PAIRS:
    assert s.count(old) == 1, ('«було» не рівно раз', name, s.count(old))
    s = s.replace(old, new, 1)
open(dst, 'w', encoding='utf-8').write(s)
print('застосовано', len(PAIRS), 'правок →', dst, hashlib.md5(s.encode('utf-8')).hexdigest())
