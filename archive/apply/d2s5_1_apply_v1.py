#!/usr/bin/env python3
"""d2s5_1_apply_v1.py · AE-Simulator · S86 · D2 крок 5.1 — рушій: що саме їде у файл (S85 §0.1, В-151)
живе доки: запечено в X105 (лежить в archive/apply/ як ланцюг)
Вхід: корінь AE (index.html X104 51bd05df…). Пише <вихід>/index.html.
· recOut(id) — один дім «запис, як він ляже у файл»: recOf + no з фрази (В-103) + main (В-151: чинний, якщо в cats,
  інакше cats[0]). Правлені записи накладаються на СВІЖИЙ файл через outRec, як і раніше Object.assign.
· mergeDraft: видалені (S.edel) випадають, правлені → outRec, нові (S.edraft без бази) — у кінець масиву.
· verdict() острова — на recOut: острів перевіряє рівно те, що перевірить воркер.
· після підтвердженого запису: S.RAW.scn = записане тіло, S.SCEN = scenOf(те саме), S.edraft/S.edel скинуто.
UI не змінюється; Р1 (кнопка острова) лишається до 5.3. Кожна заміна — assert ×1. Повтор на виході = відмова (П34).
Запуск: python3 d2s5_1_apply_v1.py <корінь AE> <тека виходу>
"""
import sys, hashlib, pathlib
root, out = map(pathlib.Path, sys.argv[1:3]); out.mkdir(parents=True, exist_ok=True)
t = (root/'index.html').read_text(encoding='utf-8')
assert hashlib.md5(t.encode()).hexdigest().startswith('51bd05df'), 'вхід не X104'

def sub(s, R):
    for a, b in R:
        n = s.count(a); assert n == 1, (n, a[:70]); s = s.replace(a, b)
    return s

R = [
# ── 1 · recOut поруч із recOf ──
("const scenAll = () => S.SCEN.map(s=>recOf(String(s.id)));",
"""/* D2 крок 5.1 · В-151 · ЯК ЗАПИС ЛЯЖЕ У ФАЙЛ — один дім. Публікація пише outRec, острів судить recOut:
   що бачать правила на екрані, те саме побачить воркер. no — з фрази (В-103: правила воркера читають no з
   файлу, ae_rules :98 :268). main — чинний, якщо він є в cats, інакше перша категорія (В-96: у формі поля
   немає). Не «завжди cats[0]», як мокап: у 3 записах файлу (#21 #36 #42) main інший, і правка назви мовчки
   зсунула б mainCat судді. */
const outRec = r => {
  r.no = noOf(r.open).no;
  const c = Array.isArray(r.cats) ? r.cats : [];
  if(!c.includes(r.main)) r.main = c[0] || '';
  return r;
};
const recOut = id => { const r = recOf(id); return r ? outRec(JSON.parse(JSON.stringify(r))) : null; };
const scenAll = () => S.SCEN.map(s=>recOf(String(s.id)));"""),
# ── 2 · mergeDraft: нові й видалені ──
("""const mergeDraft = base => {
  const out = JSON.parse(JSON.stringify(base));
  const arr = out.scenarios || out;
  for(const rec of arr){
    const d = S.edraft[String(rec.id)];
    if(d) Object.assign(rec, d);
  }
  return out;
};""",
"""/* D2 крок 5.1: видалені (S.edel) випадають · правлені → outRec поверх свіжого · нові (правка без бази, Р-1д)
   — у кінець. Незачеплені записи лишаються рівно файлом. Форма запису — жорстке видалення: відновлення дає
   git (кожна публікація — коміт); прапорець deleted довелось би фільтрувати в кожному читачі масиву. */
const mergeDraft = base => {
  const out = JSON.parse(JSON.stringify(base));
  const arr = out.scenarios || out, have = new Set(arr.map(r=>String(r.id)));
  const next = [];
  for(const rec of arr){
    const id = String(rec.id), d = S.edraft[id];
    if(S.edel[id]) continue;
    next.push(d ? outRec({...rec, ...JSON.parse(JSON.stringify(d))}) : rec);
  }
  for(const id of Object.keys(S.edraft))
    if(!have.has(id) && !S.edel[id]) next.push(outRec(JSON.parse(JSON.stringify(S.edraft[id]))));
  if(out.scenarios){ out.scenarios = next; return out; }
  return next;
};"""),
# ── 3 · publish: тіло один раз, лічильник з видаленими ──
("""  const n = Object.keys(S.edraft).length;
  let res, j;""",
"""  const n = new Set(Object.keys(S.edraft).concat(Object.keys(S.edel))).size;
  const next = mergeDraft(fresh.obj);
  let res, j;"""),
("body:JSON.stringify({catalog:S.esnap.cat, scenarios:mergeDraft(fresh.obj),",
 "body:JSON.stringify({catalog:S.esnap.cat, scenarios:next,"),
# ── 4 · після підтвердженого запису локальна правда = записане ──
("""  S.edraft = {};
  S.epub = {state:'ok', text:(j.text||'Збережено.')
    + ' Сторінка ще показує стару версію: GitHub Pages оновиться за хвилину-дві.'};""",
"""  /* D2 крок 5.1: воркер підтвердив запис саме цього тіла — воно й стає даними сторінки. Інакше до оновлення
     Pages нові зникли б, видалені повернулись, правки відкотились: публікація виглядала б невдалою. */
  S.RAW.scn = next; S.SCEN = scenOf(next);
  S.edraft = {}; S.edel = {};
  S.epub = {state:'ok', text:(j.text||'Збережено.')
    + ' Тут уже нова версія; після перезавантаження GitHub Pages покаже її за хвилину-дві.'};"""),
# ── 5 · один рядок побудови S.SCEN ──
("    S.SCEN=scn.scenarios.map(s=>({...s, no:noOf(s.open).no}));",
 "    S.SCEN=scenOf(scn);"),
("function pickShift(n){",
"""/* В-103 · S.SCEN з файлу — нові обʼєкти, S.RAW лишається рівно файлом. Один рядок на старт і на публікацію. */
function scenOf(scn){ return scn.scenarios.map(s=>({...s, no:noOf(s.open).no})); }
function pickShift(n){"""),
# ── 6 · острів судить те, що поїде у файл ──
("const r=runRules(null, live.map(cur));",
 "const r=runRules(null, live.map(recOut));   /* 5.1 · В-151: судимо те, що поїде у файл */"),
]
t = sub(t, R)
(out/'index.html').write_text(t, encoding='utf-8')
print('index.html', hashlib.md5(t.encode()).hexdigest())
