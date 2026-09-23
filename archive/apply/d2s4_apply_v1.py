#!/usr/bin/env python3
"""d2s4_apply_v1.py · AE-Simulator · S85 · D2 крок 4 — острів A2v2 цілком за прапорцем ?a2v2 (В-143, В-144, П125)
живе доки: запечено в X104 (лежить в archive/apply/ як ланцюг)
Вхід: корінь AE (index.html X103 d50aad7b…, project/stand/a2/mock_a2v2_tpl_v4_5.html 145a9ba0…). Пише <вихід>/index.html.
Рендер мокапа v4.5 переноситься як є; власний стан мокапа замінено адаптерами рушія (S.SCEN · recOf · setDraft ·
draftFields · runRules/spreadVerdict · potential · noOf). Р1 публікація вимкнена до кроку 5 · Р2 створення/видалення —
лише в чернетці (S.edraft без бази · S.edel) · Р3 дефолт групи (радіо ●) не рендериться до кроку 6.
Кожна заміна — assert ×1. Повтор на виході = відмова (П34).
Запуск: python3 d2s4_apply_v1.py <корінь AE> <тека виходу>
"""
import sys, json, re, hashlib, pathlib
root, out = map(pathlib.Path, sys.argv[1:3]); out.mkdir(parents=True, exist_ok=True)
t = (root/'index.html').read_text(encoding='utf-8')
assert hashlib.md5(t.encode()).hexdigest().startswith('d50aad7b'), 'вхід не X103'
tpl_p = root/'project/stand/a2/mock_a2v2_tpl_v4_5.html'; tpl = tpl_p.read_text(encoding='utf-8')
assert hashlib.md5(tpl.encode()).hexdigest().startswith('145a9ba0'), 'шаблон не v4.5'

def sub(s, R):
    for a, b in R:
        n = s.count(a); assert n == 1, (n, a[:70]); s = s.replace(a, b)
    return s

# ── 1 · CSS: префікс .v2 .a2v2 (В-143 — колізії btn card err ghost num who wrap знімаються областю) ──
css = tpl.split('<style>', 1)[1].split('</style>', 1)[0]
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
def pref(sel):
    o = []
    for s in (x.strip() for x in sel.split(',')):
        if not s or s in ('html', 'body') and False: continue
        if s.startswith('.rail'): return None          # рейка — оболонки продукту
        if s in ('html',): continue
        o.append('.v2 .a2v2' if s in (':root', 'body') else '.v2 .a2v2 ' + s)
    return ','.join(o) if o else None
def scope(c):
    res, i = [], 0
    while True:
        j = c.find('{', i)
        if j < 0: break
        sel = c[i:j].strip(); d, k = 1, j + 1
        while d:
            d += {'{': 1, '}': -1}.get(c[k], 0); k += 1
        body = c[j+1:k-1]
        if sel.startswith('@'): res.append(sel + '{' + scope(body) + '}')
        else:
            p = pref(sel)
            if p: res.append(p + '{' + body.strip() + '}')
        i = k
    return '\n'.join(res)
css_scoped = scope(css)
assert '.v2 .a2v2 .btn{' in css_scoped and '.rail' not in css_scoped and ':root' not in css_scoped
css_block = ('<style id="a2v2-css">\n/* ── D2 крок 4 · острів A2v2 = CSS мокапа v4.5 під .v2 .a2v2 · d2s4_apply_v1 (генерується, руками не правити) ── */\n'
             + css_scoped +
             '\n/* господар: рейка — оболонки, не острова; лівий відступ мокапа (234 = його рейка) знято */\n'
             '.v2 .a2v2 .page{padding:4px 0 96px}\n'
             '/* Р3 · радіо дефолту групи — крок 6 (В-142); колонка лишається порожньою */\n'
             '.v2 .a2v2 .grow .gdef-none{width:18px}\n</style>\n')
a = t.index('<style id="v2-css-anc">'); b = t.index('</style>', a) + len('</style>\n')
t = t[:b] + css_block + t[b:]

# ── 2 · HTML мокапа без рейки ──
body = tpl.split('<body>', 1)[1].split('<script>', 1)[0]
html = body[body.index('<main'):].strip()
html = sub(html, [(
  'Кружечок ● — група за замовчуванням: сюди лягає новий сценарій, коли в списку обрано «Усі групи». Її не видалити — спершу позначте іншу. ', '')])
HTML = '<div class="a2v2">' + html + '</div>'

# ── 3 · JS мокапа → тіло A2v2(root) з адаптерами рушія ──
js = tpl.split('<script>', 1)[1].split('</script>', 1)[0]
js = sub(js, [
 ('const D = /*DATA*/null;',
  "/* адаптер даних: каталог, характери (носій, Б4), правило — з рушія, не з файлу мокапа */\n"
  "const D = { cats:Object.fromEntries(Object.keys(S.CAT).map(k=>[k,{label:S.LABEL[k], items:S.CAT[k]}])),\n"
  "            chars:Object.keys(S.P.chars), rule:S.cfg.rule };"),
 ("const $ = s => document.querySelector(s);", "const $ = s => W.querySelector(s);"),
 ("const st = { pub:{}, draft:{}, del:{}, created:{}, extraGroups:[], sel:null, grp:'', q:'', view:'form', defGrp:'' };\n"
  "for (const s of D.scenarios) st.pub[s.id] = JSON.parse(JSON.stringify(s));\n"
  "st.sel = String(D.scenarios.find(s=>s.no===4417)?.id ?? D.scenarios[0].id);\n",
  "/* D2 крок 4 · власного стану мокапа немає (В-143). Дані — рушій: опубліковане = S.SCEN, правки й нові = S.edraft\n"
  "   (новий = запис без бази, recOf Р-1д), «Буде видалено» = S.edel. Стан екрана — S.a2v2. Групи-сутності — крок 6. */\n"
  "const newIds = () => Object.keys(S.edraft).filter(id=>!S.SCEN.some(s=>String(s.id)===id));\n"
  "const st = {\n"
  "  get sel(){ return S.a2v2.sel; }, set sel(v){ S.a2v2.sel=v; },\n"
  "  get grp(){ return S.a2v2.grp; }, set grp(v){ S.a2v2.grp=v; },\n"
  "  get q(){ return S.a2v2.q; },     set q(v){ S.a2v2.q=v; },\n"
  "  get view(){ return S.a2v2.view; }, set view(v){ S.a2v2.view=v; },\n"
  "  get extraGroups(){ return S.a2v2.extra; }, set extraGroups(v){ S.a2v2.extra=v; },\n"
  "  get _keepEmpty(){ return S.a2v2.keep; }, set _keepEmpty(v){ S.a2v2.keep=v; },\n"
  "  get del(){ return S.edel; },\n"
  "  get pub(){ return Object.fromEntries(S.SCEN.map(s=>[String(s.id), s])); },\n"
  "  get created(){ return Object.fromEntries(newIds().map(id=>[id, S.edraft[id]])); },\n"
  "  defGrp:''   /* Р3 · дефолт групи — крок 6 (В-142) */\n"
  "};\n"
  "{ const all = S.SCEN.map(s=>String(s.id)).concat(newIds());\n"
  "  if(S.a2v2.sel===null || !all.includes(S.a2v2.sel)) S.a2v2.sel = String((S.SCEN.find(s=>s.no===4417)||S.SCEN[0]||{}).id); }\n"),
 ("const ids = () => Object.keys(st.pub).concat(Object.keys(st.created)).filter((v,i,a)=>a.indexOf(v)===i);",
  "const ids = () => S.SCEN.map(s=>String(s.id)).concat(newIds());"),
 ("const base = id => st.pub[id] || st.created[id];",
  "const base = id => S.SCEN.find(s=>String(s.id)===id) || S.edraft[id];"),
 ("const cur = id => { const s={...base(id), ...(st.draft[id]||{})}; s.no = noOf(s.open).no; return s; };",
  "/* запис = recOf рушія (одне місце склеювання); номер — noOf рушія (В-103) */\n"
  "const cur = id => { const s={...recOf(id)}; for(const k of ['cats','order','bv','bm']) if(!Array.isArray(s[k])) s[k]=[]; s.no = noOf(s.open).no; return s; };"),
 ("const changes = id => st.created[id] ? ['новий'] : Object.keys(st.draft[id]||{}).filter(k => JSON.stringify(st.draft[id][k]) !== JSON.stringify(base(id)[k] ?? (['trap','noSale','hint'].includes(k)?false:undefined)));",
  "/* правка, що збіглась із файлом, — не правка: це вже робить setDraft рушія */\n"
  "const changes = id => st.created[id] ? ['новий'] : draftFields(id);"),
 ("st.defGrp = groupsNow().includes('Базові') ? 'Базові' : (groupsNow()[0] || '');",
  "/* Р3 · стартовий дефолт «Базові» — крок 6 (В-142) */"),
 ("function set(k, v){\n  const id=st.sel; (st.draft[id] ||= {})[k]=v;\n"
  "  if(!st.created[id] && JSON.stringify(v)===JSON.stringify(base(id)[k] ?? (['trap','noSale','hint'].includes(k)?false:undefined))) delete st.draft[id][k];\n"
  "  if(st.created[id]) { st.created[id][k]=v; delete st.draft[id][k]; }\n  pruneGroups(); paint();\n}",
  "function set(k, v){\n  /* правка — setDraft рушія; прапорець false при відсутньому ключі у файлі = не правка (як мокап) */\n"
  "  const id=st.sel, b=S.SCEN.find(s=>String(s.id)===id);\n"
  "  if(b && v===false && b[k]===undefined){ const d=S.edraft[id]; if(d){ delete d[k]; if(!Object.keys(d).length) delete S.edraft[id]; } }\n"
  "  else setDraft(id, k, v);\n  pruneGroups(); paint();\n}"),
 ("  pub.title = blockers.length ? ",
  "  /* Р1 · публікація з острова — D2 крок 5: mergeDraft поки губить нові записи (ходить лише по id файлу) */\n"
  "  pub.disabled = true;\n  pub.title = blockers.length ? "),
 ("  const potN = Math.round(bonus(s[RULE]) - bonus(s.order));\n"
  "  const potTxt = s.noSale || !s[RULE].length ? '—' : potN > 0 ? 'до +'+potN.toLocaleString('uk-UA')+' ₴' : '0 ₴';",
  "  /* орієнтир — potential() рушія (В-119), не власна арифметика */\n"
  "  const potN = s.noSale ? null : potential(s);\n"
  "  const potTxt = potN===null ? '—' : potN > 0 ? 'до +'+potN.toLocaleString('uk-UA')+' ₴' : '0 ₴';"),
 ("const btn=document.querySelector(`[popovertarget", "const btn=W.querySelector(`[popovertarget"),
 ("    return `<div class=\"grow\"><input type=\"radio\" name=\"gdef\" data-gdef=\"${i}\" ${r.def?'checked':''} aria-label=\"Група за замовчуванням: ${esc(r.name||'без назви')}\" title=\"Сюди лягають нові сценарії\">",
  "    return `<div class=\"grow\"><span class=\"gdef-none\"></span>"),
 ("● — група за замовчуванням: сюди лягає новий сценарій при «Усі групи». ", ""),
 ("    if(st.created[id]){ ask('Скасувати новий сценарій?', 'Сценарій «'+(cur(id).title||'Без назви')+'» ще не опубліковано — він зникне.', 'Прибрати', ()=>{ delete st.created[id]; delete st.draft[id]; st.sel=Object.keys(st.pub)[0];",
  "    if(st.created[id]){ ask('Скасувати новий сценарій?', 'Сценарій «'+(cur(id).title||'Без назви')+'» ще не опубліковано — він зникне.', 'Прибрати', ()=>{ delete S.edraft[id]; st.sel=String(S.SCEN[0].id);"),
 ("    delete st.draft[id]; const used=", "    delete S.edraft[id]; const used="),
 ("st.created[id] = {id:+id, no:null, title: nNew ? 'Новий сценарій '+(nNew+1) : 'Новий сценарій', grp: st.grp || st.defGrp,",
  "S.edraft[id] = {id:+id, title: nNew ? 'Новий сценарій '+(nNew+1) : 'Новий сценарій', grp: st.grp || groupsNow()[0] || '',"),
 ("\ndrawEditor();\n", "\n"),
])
# перевірки — з рушія (В-144): замінюємо тіло checks цілком
a = js.index('function checks(s){'); b = js.index('const errs = s =>')
js = js[:a] + (
  "/* В-144 · повідомлення — лише з рушія (runRules → spreadVerdict), біля поля — D3. Локальні checks мокапа не портуються. */\n"
  "let VM = null;\n"
  "const verdict = () => { if(VM) return VM; const live=ids().filter(i=>!st.del[i]); const r=runRules(null, live.map(cur));\n"
  "  return (VM = r ? spreadVerdict(r.out, new Set(live)) : {byId:new Map(), general:[]}); };\n"
  "function checks(s){ return (verdict().byId.get(String(s.id))||[]).filter(m=>m.lvl!=='ok').map(m=>({lvl:m.lvl==='err'?'e':'w', m:m.msg})); }\n"
) + js[b:]
# номер: noOf і DIG мокапа — другий дім правила; беремо noOf рушія
a = js.index("const DIG = {"); b = js.index("const cur = id =>")
js = js[:a] + "/* noOf — рушія (В-103), мокапова копія не портується */\n" + js[b:]
# вердикт скидається на кожній зміні стану
js = sub(js, [("function paint(){\n", "function paint(){\n  VM = null;\n"),
              ("function drawEditor(){\n", "function drawEditor(){\n  VM = null;\n")])
# публікація: крок 5
a = js.index("  if(t.id==='pub'){"); b = js.index("  if(t.id==='newSc'){")
js = js[:a] + "  if(t.id==='pub'){ return; }   /* Р1 · крок 5 */\n" + js[b:]
# події — на корінь острова, не на document (4 спливні + toggle capture)
assert js.count('document.addEventListener(') == 5; js = js.replace('document.addEventListener(', 'W.addEventListener(')
n = js.count('document.querySelectorAll('); assert n == 3, n; js = js.replace('document.querySelectorAll(', 'W.querySelectorAll(')
assert 'st.draft' not in js and 'D.scenarios' not in js and 'document.querySelector(' not in js, 'лишився стан або документ мокапа'

fn = ("/* D2 крок 4 · A2 «Сценарії» v2 — острів мокапа v4.5 цілком за ?a2v2 (В-143 Branch by Abstraction · В-144 · П125).\n"
      "   Рендер перенесено як є (DOM пройдений 66 ✓, S83); стан — рушія. Події — на корені острова (W), не на document:\n"
      "   інакше ловили б E1/E2. Глобали для детектора (s85_olya_walk_v5_root) — лише тут, лише під прапорцем.\n"
      "   живе доки: крок 7 перемкне V2.ascen, старі Editor/ScenCard — до щабля 11. */\n"
      "const A2V2_HTML = " + json.dumps(HTML, ensure_ascii=False) + ";\n"
      "function A2v2(root){\n"
      "  if(!CURATOR.open){ S.screen='settings'; render(); return; }\n"
      "  const W = el('div',{}); W.innerHTML = A2V2_HTML; const W0 = W.firstElementChild; root.append(W0);\n"
      "  (function(W){\n" + js + "\n  drawEditor();\n"
      "  Object.assign(window, {set, drawEditor, openGroups, drawGroups, ask, toast, cur, st});\n"
      "  Object.defineProperty(window, 'gw', {configurable:true, get:()=>gw, set:v=>{gw=v;}});\n"
      "  })(W0);\n}\n")
t = sub(t, [
 ("  root.append(el('div',{class:'a2'},[listCol, formCol, prevCol]));\n}\nV2.settings",
  "  root.append(el('div',{class:'a2'},[listCol, formCol, prevCol]));\n}\n" + fn + "V2.settings"),
 ("V2.ascen    = v2Adapt(A2Scen);   /* X97-C1 · A2 · В-83 знято для ascen */",
  "V2.ascen    = v2Adapt(root => (A2V2 ? A2v2 : A2Scen)(root));   /* X97-C1 · A2 · В-83 знято для ascen · D2 крок 4: ?a2v2 → острів; дефолт перемикає крок 7 */"),
 ("const STEP = new URLSearchParams(location.search).has('step');\n",
  "const STEP = new URLSearchParams(location.search).has('step');\n\n"
  "/* D2 крок 4 · ?a2v2 — острів A2 v2 замість A2Scen (В-143). Службова адреса оператора, Оля її не бачить;\n"
  "   живе доки: крок 7 (перемикання V2.ascen). */\n"
  "const A2V2 = new URLSearchParams(location.search).has('a2v2');\n"),
 ("  efilter:'all', edraft:{}, escen:null,\n",
  "  efilter:'all', edraft:{}, escen:null,\n"
  "  /* D2 крок 4 · edel — «Буде видалено» до публікації (у файл — крок 5); a2v2 — стан екрана острова A2v2:\n"
  "     обраний, група-фільтр, пошук, вигляд ≤1600, порожні групи сесії (групи-сутності — крок 6). */\n"
  "  edel:{}, a2v2:{sel:null, grp:'', q:'', view:'form', extra:[], keep:[]},\n"),
])
(out/'index.html').write_text(t, encoding='utf-8')
print('index.html', hashlib.md5(t.encode()).hexdigest(), len(t.encode()))
