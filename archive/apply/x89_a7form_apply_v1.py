#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x89_a7form_apply_v1.py — AE-Simulator · S70 · щабель 1, кроки 1.2+1.3: ФОРМА A7 «Система».

живе доки: екран 'settings' малюється формою A7 мокапу (page-title · метрики · список)

Порт ФОРМИ з mockup_X21_v1.html (:39 CSS, :408 renderA7), логіка наша чинна:
  · STILL_MOCK.system (вигадка мокапу) НЕ переноситься. Метрики й рядки рахує
    runRules() — ті самі правила, що на push.
  · Рядки вердикту — мовою правил, як є (коментар панелі 6а: переказ = друга копія правил).
  · В-76: перевірка ПРОГАНЯЄТЬСЯ ПРИ ВІДКРИТТІ (запиту не коштує), кнопка
    «Перевірити дані» зникає; вибір файлу з пристрою лишається ручним.
  · Час «Остання перевірка» — момент прогону в цій сесії; персисту немає й не буде.
  · Порядок рядків: ✗ → ⚠ → ✓ (стабільне сортування, текст не чіпається).
Кроки 1.2 (CSS) і 1.3 (JS) злито одним генератором за делегуванням оператора S70:
обидва зворотні, судяться одним поглядом на новий екран.
Ключ, пін сходинки, редактор, тех. дані лишаються під «Технічне» до щабля 4 (A6).

⚠ Смоуки smoke_ui_v1 / smoke_edit_ui_v1 падають на R4 ДО рядків цієї панелі
  (екран входу / :419), тож фрази «Перевірка даних», «підсумок: ✓», «Перевірити дані»
  зникають без дельти. Оновлення тверджень — щабель 11 (виселення смоуків).

ІДЕМПОТЕНТНІСТЬ (П94): маркери — створені вузли CSS_MARK і JS_MARK.
Використання: python3 x89_a7form_apply_v1.py <вхід.html> <вихід.html>
"""
import hashlib, sys
SRC, DST = sys.argv[1], sys.argv[2]
md5 = lambda s: hashlib.md5(s.encode()).hexdigest()

CSS_MARK = ".v2 .system-summary {"
JS_MARK  = "function dataCheck(stamp){"

# ── 1.2 · CSS ────────────────────────────────────────────────────────────────
CSS_ANCHOR = ".v2 .page-title p { margin:5px 0 0; color:var(--muted); }\n"
CSS_ADD = """/* X89-A7 · A7 «Система» — порт форми з mockup_X21_v1 :39 (скоуп .v2).
   .error svg і .sys-* — наші: у мокапа не було рядка з помилкою й вибору файлу. */
.v2 .admin-page { max-width:1500px; }
.v2 .page-title .sys-stamp { color:#6e8096; white-space:nowrap; }
.v2 .system-summary { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:15px; }
.v2 .system-metric { padding:16px; border:1px solid var(--line); border-radius:10px; background:#fff; box-shadow:0 6px 22px #263a5010; }
.v2 .system-metric strong { display:block; font-size:25px; letter-spacing:-.04em; }
.v2 .system-metric small { color:#6e8096; }
.v2 .system-metric.warning strong { color:#a96504; }
.v2 .system-metric.error strong { color:#b72745; }
.v2 .system-list { display:grid; gap:10px; }
.v2 .system-message { display:flex; align-items:flex-start; gap:11px; padding:15px; border:1px solid #e1e8ee; border-radius:9px; background:#fff; }
.v2 .system-message svg { flex:none; color:#08785d; }
.v2 .system-message.warning svg { color:#b56e08; }
.v2 .system-message.error svg { color:#b72745; }
.v2 .system-message b { display:block; font-size:13px; }
.v2 .system-message small { display:block; margin-top:3px; color:#71839a; }
.v2 .sys-files { display:flex; gap:8px; flex-wrap:wrap; margin:16px 0 6px; }
.v2 .sys-src { margin:0 0 6px; color:var(--soft); font-size:12px; }
.v2 .sys-bad { color:var(--loss); }
.v2 .sys-h { margin:32px 0 10px; font-size:17px; }
/* /X89-A7 */
"""

# ── 1.3 · JS: шапка Settings ─────────────────────────────────────────────────
SET_START = "function Settings(root){"
PUT_OPEN  = "  put(root,\n    el('div',{class:'top'},[\n"          # 4 входження у файлі — шукаємо ПІСЛЯ SET_START (3.11)
PUT_END   = "/* ── ПАНЕЛЬ ПЕРЕВІРКИ ДАНИХ (6а)"
PUT_MD5   = "a47eab351a1cfa85654a9f1436be1695"
OLD_HEAD = ("  put(root,\n    el('div',{class:'top'},[\n"
            "      el('div',{class:'toprow'},[backBtn('назад',()=>{S.screen='picker';render()})]),\n"
            "      el('h2',{class:'toptitle',text:'Налаштування'})\n    ]),\n"
            "    el('h1',{class:'lede',text:'Технічне'}),\n")
NEW_HEAD = ("  /* X89-A7: форма A7 мокапу. Час прогону пише dataCheck — у шапку сторінки. */\n"
            "  const stamp = el('small',{class:'sys-stamp'});\n"
            "  put(root, el('div',{class:'page admin-page'},[\n"
            "    el('header',{class:'page-title'},[\n"
            "      el('div',{},[el('h1',{text:'Система'}), el('p',{text:'Стан автоматичних перевірок'})]),\n"
            "      stamp\n    ]),\n"
            "    dataCheck(stamp),\n"
            "    el('h2',{class:'sys-h',text:'Технічне'}),\n")
OLD_DC_CALL = "    status,\n    dataCheck(),\n    editEntry(),\n"
NEW_DC_CALL = "    status,\n    editEntry(),\n"
OLD_TAIL = "      ])\n    ])\n  );\n}\n\n"
NEW_TAIL = "      ])\n    ])\n  ]));\n}\n\n"

# ── 1.3 · JS: dataCheck ──────────────────────────────────────────────────────
DC_START = "function dataCheck(){"
DC_END   = "/* ── ВХІД У РЕДАКТОР"
DC_MD5   = "e002f73fde5f23bf493e9b812d85f810"
DC_NEW = r"""function dataCheck(stamp){
  /* X89-A7 · ФОРМА A7 (мокап :408), ЛОГІКА ПАНЕЛІ 6а — без змін:
     runRules() · picked · takeFiles · classifyJson лишаються тими самими.
     В-76: прогін при відкритті — правила судять уже завантажені дані й
     запиту не коштують, тож кнопка тільки додавала клік. */
  const sum  = el('div',{class:'system-summary'});
  const list = el('section',{class:'system-list'});
  const srcLine  = el('p',{class:'sys-src'});
  const fileNote = el('p',{class:'sys-src sys-bad',style:'display:none'});
  /* Вибране людиною. Порожнє поле = бік береться з застосунку. */
  const picked = {cat:null, scen:null, catName:'', scenName:''};

  const metric = (n, label, tone)=> el('article',{class:'system-metric'+(tone?' '+tone:'')},[
    el('strong',{text:String(n)}), el('small',{text:label})]);
  const HINT = {err:'Виправте до публікації.', warn:'Перевірте перед публікацією.',
                ok:'Перевірка пройшла без дій з вашого боку.'};
  /* Іконки літералами: спрайт несе лише символи, які кличе icon() (смоук X21 S6). */
  const row = (lvl, msg)=> el('article',{class:'system-message'+(lvl==='err'?' error':lvl==='warn'?' warning':'')},[
    lvl==='err' ? icon('i-alert') : lvl==='warn' ? icon('i-info') : icon('i-check'),
    el('div',{},[el('b',{text:msg}), el('small',{text:HINT[lvl]})])]);

  const run = ()=>{
    sum.textContent=''; list.textContent='';
    if(typeof AE_RULES==='undefined' || !AE_RULES.validate){
      list.append(row('err','Правила не завантажились: tools/ae_rules.js не прочитано.'));
      return;
    }
    /* Джерело називається ЗАВЖДИ, навіть коли файл не вибирали. Вердикт
       без імені того, що судилось, читається як вердикт про застосунок. */
    srcLine.textContent = 'Судиться: каталог — ' + (picked.catName || 'дані застосунку') +
                          ' · сценарії — ' + (picked.scenName || 'дані застосунку');
    /* ⚠ ЧОТИРИ АРГУМЕНТИ, не два — носій характерів і config беруться з
       застосунку всередині runRules(), навіть коли дані підсунуті файлом. */
    const r = runRules(picked.cat, picked.scen);
    sum.append(metric(r.ok,'перевірок пройдено',''), metric(r.warn,'попередження','warning'),
               metric(r.err,'критичних помилок','error'));
    /* Порядок ✗ → ⚠ → ✓: стабільне сортування, текст рядків — мовою правил, як є. */
    const ORDER = {err:0, warn:1, ok:2};
    for(const m of [...r.out].sort((a,b)=>ORDER[a.lvl]-ORDER[b.lvl])) list.append(row(m.lvl, m.msg));
    if(stamp) stamp.textContent = 'Остання перевірка: ' +
      new Date().toLocaleTimeString('uk-UA',{hour:'2-digit',minute:'2-digit'});
  };

  /* ⚠ accept НЕ ставимо. У Files на iPhone фільтр за типом глушить файли,
     що лежать в iCloud. Тип усе одно перевіряється розбором, тобто надійніше. */
  const fileIn = el('input',{type:'file',multiple:true,style:'display:none',
    onchange:e=>takeFiles(e.target.files)});

  const takeFiles = async (list_)=>{
    const files=[...list_];
    /* Скидання значення: без нього повторний вибір ТОГО САМОГО файлу
       події не дає, і виправлений файл виглядає як невиправлений. */
    fileIn.value='';
    if(!files.length) return;
    const bad=[];
    for(const f of files){
      let src='';
      try{ src = await readFileText(f); }
      catch(_){ bad.push(f.name+' — файл не прочитався з пристрою.'); continue; }
      let v;
      try{ v = JSON.parse(src); }
      catch(err){ bad.push(f.name+' — '+jsonErrorText(err, src)); continue; }
      const kind = classifyJson(v);
      if(!kind){ bad.push(f.name+' — не схоже ні на каталог, ні на сценарії.'); continue; }
      if(kind==='cat'){ picked.cat=v; picked.catName=f.name; }
      else            { picked.scen=v; picked.scenName=f.name; }
    }
    fileNote.style.display = bad.length ? '' : 'none';
    fileNote.textContent = bad.join('  ·  ');
    run();
  };

  const fileRow = el('div',{class:'sys-files'},[
    fileIn,
    el('button',{class:'btn ghost',text:'Вибрати файл…',onclick:()=>fileIn.click()}),
    el('button',{class:'btn ghost',text:'Дані застосунку',onclick:()=>{
      picked.cat=null; picked.scen=null; picked.catName=''; picked.scenName='';
      fileNote.style.display='none'; fileNote.textContent=''; run();
    }})
  ]);

  run();   /* В-76 */
  return el('section',{class:'sys-checks'},[sum, list, fileRow, fileNote, srcLine]);
}

"""

src = open(SRC, encoding="utf-8").read()
has_css, has_js = CSS_MARK in src, JS_MARK in src
if has_css and has_js:
    open(DST, "w", encoding="utf-8").write(src)
    print("· маркери X89 уже в файлі — 0 правок (ідемпотентно)")
    print(f"→ {DST}  md5 {md5(src)}"); sys.exit(0)
if has_css != has_js:
    print(f"✗ половинний стан: CSS={has_css} JS={has_js}"); sys.exit(1)

out = src
# CSS
if out.count(CSS_ANCHOR) != 1:
    print(f"✗ якір CSS: {out.count(CSS_ANCHOR)} входжень"); sys.exit(1)
out = out.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_ADD, 1)

# Settings
st = out.index(SET_START)
a = out.index(PUT_OPEN, st); b = out.index(PUT_END)
if not (st < a < b):
    print("✗ межі блока put(Settings) не в порядку"); sys.exit(1)
blk = out[a:b]
if md5(blk) != PUT_MD5:
    print(f"✗ блок put(Settings) змінився: md5 {md5(blk)}"); sys.exit(1)
for old in (OLD_HEAD, OLD_DC_CALL):
    if blk.count(old) != 1:
        print(f"✗ у блоці Settings якір не унікальний: {old[:40]!r}"); sys.exit(1)
if not blk.endswith(OLD_TAIL):
    print("✗ хвіст блока Settings не збігся"); sys.exit(1)
nb = blk.replace(OLD_HEAD, NEW_HEAD, 1).replace(OLD_DC_CALL, NEW_DC_CALL, 1)
nb = nb[:-len(OLD_TAIL)] + NEW_TAIL
out = out[:a] + nb + out[b:]

# dataCheck
c = out.index(DC_START); d = out.index(DC_END)
if md5(out[c:d]) != DC_MD5:
    print(f"✗ тіло dataCheck змінилось: md5 {md5(out[c:d])}"); sys.exit(1)
out = out[:c] + DC_NEW + out[d:]

# самоперевірка звіряє вузли (П91)
checks = [
    (out.count(CSS_MARK) == 1, "CSS-вузол один"),
    (out.count(JS_MARK) == 1 and "function dataCheck(){" not in out, "dataCheck один, нового підпису"),
    (out.count("dataCheck(stamp),") == 1 and out.count("dataCheck(") == 2, "виклик dataCheck рівно один"),
    ("'Перевірити дані'" not in out, "кнопки прогону немає (В-76)"),
    (out.count("el('h1',{text:'Система'})") == 1, "шапка A7"),
    ("text:'Налаштування'})\n    ]),\n    el('h1',{class:'lede'" not in out, "стара шапка Settings прибрана"),
    (out.count("function classifyJson") == 1 and out.count("function runRules") == 1, "логіка 6а на місці"),
]
for ok, name in checks:
    if not ok:
        print(f"✗ самоперевірка: {name}"); sys.exit(1)
open(DST, "w", encoding="utf-8").write(out)
print(f"· правок: 4 вузли (CSS · шапка Settings · виклик · dataCheck)  ✓ самоперевірок {len(checks)}")
print(f"→ {DST}  md5 {md5(out)}")
