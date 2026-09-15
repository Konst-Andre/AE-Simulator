#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x91_a7areas_apply_v1.py — AE-Simulator · S71 · щабель 1, крок B: A7 «Система» — ДАШБОРД ОБЛАСТЕЙ.

живе доки: екран 'settings' групує вердикт правил за AE_RULES.AREAS (5 рядків-областей)

Вхід X89 → вихід X91. Потребує правил із x90 (поле area + AREAS); без них —
чесний рядок «правила без областей», не групування за текстом (друга копія знання).

Композиція за мокапом mockup_X21_v1 :408 (П101), рішення S71:
  · шапка без кнопки (у мокапі в page-title лише час) · час З ДАТОЮ;
  · 3 метрики: «перевірок виконано» = ok+warn+err · попередження · критичних помилок;
  · 5 рядків-областей; ОДНА вісь уваги — сортування за найгіршим станом ✗→⚠→✓,
    окремого блока «Потребує уваги» немає (вирок оператора S71);
  · підрядок — лічильник («3 перевірки · 1 попередження»), не фраза мокапу:
    «Перевірте перед публікацією» брехала б для ⚠ «норма, позиція нова»;
  · деталі — нативний <details>, рядки мовою правил, ✗→⚠→✓ усередині;
  · вибір файлу — кнопки-посилання в рядку джерела (делеговано оператором S71):
    дія змінює те, що судиться, тож стоїть поруч із назвою того, що судиться.
    Тексти кнопок «Вибрати файл…» / «Дані застосунку» — ДОСЛІВНО старі (smoke_ui_v1 :389 :391).
Логіка runRules · picked · takeFiles · classifyJson — без змін. Низ екрана (Технічне …) — крок C.

ІДЕМПОТЕНТНІСТЬ (П94): маркери — створені вузли CSS_MARK і JS_MARK.
Використання: python3 x91_a7areas_apply_v1.py <вхід.html> <вихід.html>
"""
import hashlib, sys
SRC, DST = sys.argv[1], sys.argv[2]
md5 = lambda s: hashlib.md5(s.encode()).hexdigest()

CSS_MARK = "/* X91-A7B · області */"
JS_MARK  = "/* X91-A7B · dataCheck областей */"

CSS_OLD = ".v2 .sys-files { display:flex; gap:8px; flex-wrap:wrap; margin:16px 0 6px; }\n"
CSS_NEW = CSS_MARK + """
.v2 .system-message > details { flex:1; min-width:0; }
.v2 .system-message summary { display:flex; align-items:flex-start; gap:11px; cursor:pointer; list-style:none; }
.v2 .system-message summary::-webkit-details-marker { display:none; }
.v2 .system-message summary > div { flex:1; min-width:0; }
.v2 .system-message summary::after { content:''; flex:none; width:7px; height:7px; margin:5px 4px 0 0; border-right:1.5px solid #8a99ab; border-bottom:1.5px solid #8a99ab; transform:rotate(45deg); transition:transform .15s; }
.v2 .system-message details[open] summary::after { transform:rotate(-135deg); margin-top:8px; }
.v2 .system-message summary:focus-visible { outline:2px solid var(--anc-blue, #0060a8); outline-offset:4px; border-radius:4px; }
.v2 .sys-rules { margin:12px 0 0 29px; padding:0; list-style:none; display:grid; gap:6px; font-size:13px; }
.v2 .sys-rules li { display:flex; gap:8px; color:#34465c; }
.v2 .sys-rules li > span:first-child { flex:none; width:14px; font-weight:700; }
.v2 .sys-rules .ok > span:first-child { color:#08785d; }
.v2 .sys-rules .warn > span:first-child { color:#b56e08; }
.v2 .sys-rules .err > span:first-child { color:#b72745; }
.v2 .sys-checks > .sys-src { margin:14px 0 6px; }   /* специфічніше за старе .sys-src — воно стоїть нижче */
.v2 .sys-link { padding:0; border:0; background:none; color:inherit; font:inherit; text-decoration:underline; text-underline-offset:2px; cursor:pointer; }
.v2 .sys-link:hover { color:var(--anc-text, #1C1E24); }
"""

JS_NEW = r"""function dataCheck(stamp){
  """ + JS_MARK + r"""
  /* Логіка панелі 6а — без змін: runRules() · picked · takeFiles · classifyJson.
     В-76: прогін при відкритті. Групування — ЛИШЕ за полем area з правил (x90);
     підписи й порядок — AE_RULES.AREAS. За текстом рядків не групуємо: це була б
     друга копія знання правил. */
  const sum  = el('div',{class:'system-summary'});
  const list = el('section',{class:'system-list'});
  const srcText  = el('span');
  const fileNote = el('p',{class:'sys-src sys-bad',style:'display:none'});
  const picked = {cat:null, scen:null, catName:'', scenName:''};

  const metric = (n, label, tone)=> el('article',{class:'system-metric'+(tone?' '+tone:'')},[
    el('strong',{text:String(n)}), el('small',{text:label})]);
  const RANK = {err:0, warn:1, ok:2};
  const SIGN = {ok:'✓', warn:'⚠', err:'✗'};
  /* Іконки літералами: спрайт несе лише символи, які кличе icon() (смоук X21 S6). */
  const ico = lvl => lvl==='err' ? icon('i-alert') : lvl==='warn' ? icon('i-info') : icon('i-check');
  const cls = lvl => 'system-message'+(lvl==='err'?' error':lvl==='warn'?' warning':'');
  /* Українська множина: 1 перевірка · 2–4 перевірки · 5+ перевірок (11–14 — «перевірок»). */
  const plural = (n, one, few, many)=>{ const d=n%10, h=n%100;
    return n+' '+(d===1&&h!==11 ? one : d>=2&&d<=4&&(h<12||h>14) ? few : many); };

  const areaRow = (label, ms)=>{
    const ord = [...ms].sort((a,b)=>RANK[a.lvl]-RANK[b.lvl]);
    const worst = ord[0].lvl;
    const w = ms.filter(m=>m.lvl==='warn').length, e = ms.filter(m=>m.lvl==='err').length;
    const tail = [e ? plural(e,'помилка','помилки','помилок') : '',
                  w ? plural(w,'попередження','попередження','попереджень') : ''].filter(Boolean);
    const sub = plural(ms.length,'перевірка','перевірки','перевірок') + ' · ' + (tail.length ? tail.join(' · ') : 'без зауважень');
    return el('article',{class:cls(worst)},[
      el('details',{},[
        el('summary',{},[ico(worst), el('div',{},[el('b',{text:label}), el('small',{text:sub})])]),
        el('ul',{class:'sys-rules'}, ord.map(m=> el('li',{class:m.lvl},[
          el('span',{text:SIGN[m.lvl]}), el('span',{text:m.msg})])))
      ])
    ]);
  };
  const flat = (lvl, msg)=> el('article',{class:cls(lvl)},[ico(lvl), el('div',{},[el('b',{text:msg})])]);

  const run = ()=>{
    sum.textContent=''; list.textContent='';
    if(typeof AE_RULES==='undefined' || !AE_RULES.validate){
      list.append(flat('err','Правила не завантажились: tools/ae_rules.js не прочитано.'));
      return;
    }
    srcText.textContent = 'Судиться: каталог — ' + (picked.catName || 'дані застосунку') +
                          ' · сценарії — ' + (picked.scenName || 'дані застосунку') + ' · ';
    const r = runRules(picked.cat, picked.scen);
    sum.append(metric(r.ok+r.warn+r.err,'перевірок виконано',''), metric(r.warn,'попередження','warning'),
               metric(r.err,'критичних помилок','error'));
    const AREAS = AE_RULES.AREAS || [];
    const known = new Set(AREAS.map(a=>a[0]));
    /* Рядок без області — не ховаємо і не вгадуємо: окрема група, названа чесно. */
    const groups = AREAS.map(([k,label],i)=>({label, i, ms:r.out.filter(m=>m.area===k)}))
      .filter(g=>g.ms.length);
    const orphan = r.out.filter(m=>!known.has(m.area));
    if(orphan.length) groups.push({label: AREAS.length ? 'Перевірки без області' : 'Правила без областей (потрібен x90)',
                                   i: AREAS.length, ms: orphan});
    const worstOf = g=> Math.min(...g.ms.map(m=>RANK[m.lvl]));
    groups.sort((a,b)=> worstOf(a)-worstOf(b) || a.i-b.i);
    for(const g of groups) list.append(areaRow(g.label, g.ms));
    if(stamp){ const d=new Date();
      stamp.textContent = 'Остання перевірка: ' + d.toLocaleDateString('uk-UA') + ', ' +
        d.toLocaleTimeString('uk-UA',{hour:'2-digit',minute:'2-digit'}); }
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

  /* Дія стоїть поруч із назвою того, що судиться (S71). Тексти — дослівно старі. */
  const srcLine = el('p',{class:'sys-src'},[
    srcText, fileIn,
    el('button',{class:'sys-link',type:'button',text:'Вибрати файл…',onclick:()=>fileIn.click()}),
    ' · ',
    el('button',{class:'sys-link',type:'button',text:'Дані застосунку',onclick:()=>{
      picked.cat=null; picked.scen=null; picked.catName=''; picked.scenName='';
      fileNote.style.display='none'; fileNote.textContent=''; run();
    }})
  ]);

  run();   /* В-76 */
  return el('section',{class:'sys-checks'},[sum, list, srcLine, fileNote]);
}"""

src = open(SRC, encoding='utf-8').read()
if CSS_MARK in src and JS_MARK in src:
    open(DST, 'w', encoding='utf-8').write(src)
    print('  ○ вузли X91 уже є — без змін · md5', md5(src)); sys.exit(0)
if (CSS_MARK in src) != (JS_MARK in src):
    print('  ✗ половина вузлів X91 — вхід зіпсований'); sys.exit(3)

A = "function dataCheck(stamp){"; B = "\n\n/* ── ВХІД У РЕДАКТОР"
checks = [(src.count(A) == 1, "dataCheck(stamp) один"), (src.count(B) == 1, "якір редактора один"),
          (src.count(CSS_OLD) == 1, "CSS .sys-files один")]
for ok, what in checks:
    if not ok: print('  ✗ якір:', what); sys.exit(3)
a = src.index(A); b = src.index(B, a)
out = src[:a] + JS_NEW + src[b:]
out = out.replace(CSS_OLD, CSS_NEW)

# самоперевірка звіряє ВУЗЛИ (П91)
post = [(out.count(CSS_MARK) == 1, "CSS-вузол один"), (out.count(JS_MARK) == 1, "JS-вузол один"),
        (out.count("function dataCheck(stamp){") == 1, "dataCheck один"),
        ("AE_RULES.AREAS" in out, "групування читає AREAS"),
        (out.count("text:'Вибрати файл…'") == 1 and out.count("text:'Дані застосунку'") == 1, "тексти кнопок дослівні"),
        ("перевірок пройдено" not in out, "стара мітка метрики зникла"),
        ("sys-files" not in out, "старий ряд кнопок зник")]
for ok, what in post:
    print(('  ✓ ' if ok else '  ✗ ') + what)
    if not ok: sys.exit(4)
open(DST, 'w', encoding='utf-8').write(out)
print('  вихід', DST, '· md5', md5(out))
