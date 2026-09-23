#!/usr/bin/env python3
"""d2s2_apply_v1.py · AE-Simulator · S84 · D2 крок 2 — В-103 номер замовлення = текст фрази; pickShift бере всі сценарії
живе доки: запечено в X102 (лежить в archive/apply/ як ланцюг)
Вхід: корінь index.html X101 (md5 93753f6c…). Кожна заміна — assert ×1. Повтор на виході = відмова (П34).
Запуск: python3 d2s2_apply_v1.py <index.html> <вихід.html>
"""
import sys, hashlib, pathlib
src, dst = map(pathlib.Path, sys.argv[1:3])
t = src.read_text(encoding='utf-8')
assert hashlib.md5(t.encode()).hexdigest().startswith('93753f6c'), 'вхід не X101'
NOOF = r'''/* В-103 · номер замовлення — лише текст фрази, не правило і не поле (В-101). Рушій бере його
   з «Першої фрази клієнта»: 4 цифри або 4 слова-цифри через дефіс («чотири-чотири-один-сім»).
   Порт noOf з мокапа A2 v4.5 (tpl :315) дослівно. На даних S84 — 43/43 збіг із полем no файлу.
   Поле no у файлі поки лишається (його читають правила воркера, ae_rules :98 :268); узгодження
   при публікації — D2 крок 5. */
const NO_DIG = {'нуль':0,'один':1,'одна':1,'два':2,'дві':2,'три':3,'чотири':4,"п'ять":5,'шість':6,'сім':7,'сьомий':7,'вісім':8,"дев'ять":9};
function noOf(open){
  const o = String(open||'').toLowerCase().replace(/[’ʼ]/g,"'"); const f=[];
  for (const m of o.matchAll(/(?<![\d,.])\d{4}(?!\d)/g)) f.push(+m[0]);
  for (const m of o.matchAll(/(?:[а-яіїєґ']+-){3}[а-яіїєґ']+/g)){ const p=m[0].split('-'); if(p.every(x=>x in NO_DIG)) f.push(+p.map(x=>NO_DIG[x]).join('')); }
  return { no: f[0] ?? null, many: new Set(f).size > 1 };
}
function pickShift(n){
  const NET = S.SCEN;   /* В-103: усі сценарії, і «оформлення на місці» теж — номер не фільтр */'''
R = [
 ("function pickShift(n){\n  const NET = S.SCEN.filter(x=>x.no);", NOOF),
 ("    S.SCEN=scn.scenarios;\n",
  "    /* В-103: no — з фрази. Нові обʼєкти, а не мутація: S.RAW лишається рівно файлом (звірка :loadSnap). */\n"
  "    S.SCEN=scn.scenarios.map(s=>({...s, no:noOf(s.open).no}));\n"),
 ("  return base ? (d ? {...base, ...d} : base) : (d ? {...d} : null);\n};",
  "  const r = base ? (d ? {...base, ...d} : base) : (d ? {...d} : null);\n"
  "  if(r && d && 'open' in d) r.no = noOf(r.open).no;   /* В-103: правка фрази = новий номер */\n"
  "  return r;\n};"),
]
for a, b in R:
    n = t.count(a); assert n == 1, (n, a[:60]); t = t.replace(a, b)
dst.write_text(t, encoding='utf-8')
print('вихід:', dst, '· md5', hashlib.md5(t.encode()).hexdigest())
