#!/usr/bin/env python3
"""d2s1_apply_v1.py · AE-Simulator · S84 · D2 крок 1 — В-119 орієнтир не бреше (рушій + споживачі)
живе доки: запечено в X101 (лежить в archive/apply/ як ланцюг)
Вхід: корінь index.html X100 (md5 72c8cca1…). Кожна заміна — assert ×1. Повтор на виході = відмова (П34).
Запуск: python3 d2s1_apply_v1.py <index.html> <вихід.html>
"""
import sys, hashlib, pathlib
src, dst = map(pathlib.Path, sys.argv[1:3])
t = src.read_text(encoding='utf-8')
assert 'В-119' not in t, 'крок уже застосовано'
R = [
 # рушій: одне число, три стани — null (набору немає) · 0 · N
 ("const potential = sc => Math.max(1, Math.round(bonusOf(idealOf(sc)) - bonusOf(sc.order)));",
  "/* В-119 · орієнтир не бреше: Math.max(1,…) знято. Порожній ідеальний набір → null («—»),\n"
  "   приріст ≤0 → чесний 0. Округлення до цілої гривні лишається. Суми зміни беруть null як 0. */\n"
  "const potential = sc => { const ideal = idealOf(sc);\n"
  "  return ideal.length ? Math.max(0, Math.round(bonusOf(ideal) - bonusOf(sc.order))) : null; };\n"
  "const potLabel = p => p===null ? '—' : p + ' ₴';"),
 ("const e1Pot = sc => sc.noSale ? null : 'до +' + uah(potential(sc)) + ' ₴';",
  "const e1Pot = sc => { if(sc.noSale) return null; const p = potential(sc);   /* В-119 */\n"
  "  return p===null ? '—' : p>0 ? 'до +' + uah(p) + ' ₴' : '0 ₴'; };"),
 ("'РОЗБІР · приріст ' + uah(d0) + ' з ' + pot + ' ₴'",
  "'РОЗБІР · приріст ' + uah(d0) + ' з ' + potLabel(pot)"),
 ("const pot = scored.reduce((a,r)=>a+r.pot,0)||1;",
  "const pot = scored.reduce((a,r)=>a+(r.pot||0),0)||1;"),
 ("pot: potential(sc),", "pot: (potential(sc) ?? '—'),   /* В-119: judge.md пише «{{pot}} ₴» — формулювання для «—» → крок 3 */"),
 ("'Це заглушка розбору. Орієнтир — приріст близько '+potential(sc)+' ₴.'",
  "'Це заглушка розбору. Орієнтир — приріст близько '+potLabel(potential(sc))+'.'"),
 ("' ₴ з орієнтира '+potential(sc)+' ₴.'", "' ₴ з орієнтира '+potLabel(potential(sc))+'.'"),
 ("' ₴ з орієнтира '+r.pot+' ₴. '", "' ₴ з орієнтира '+potLabel(r.pot)+'. '"),
 ("' поз. · орієнтир '+potential(s)+' ₴'", "' поз. · орієнтир '+potLabel(potential(s))"),
 ("'РОЗБІР · приріст '+uah(d0)+' з '+pot+' ₴'", "'РОЗБІР · приріст '+uah(d0)+' з '+potLabel(pot)"),
 ("el('span',{class:'num',text:pot+' ₴'})", "el('span',{class:'num',text:potLabel(pot)})"),
 ("const pot=scored.reduce((a,r)=>a+r.pot,0)||1;", "const pot=scored.reduce((a,r)=>a+(r.pot||0),0)||1;"),
]
for a, b in R:
    n = t.count(a); assert n == 1, (n, a[:60]); t = t.replace(a, b)
dst.write_text(t, encoding='utf-8')
print('вихід:', dst, '· md5', hashlib.md5(t.encode()).hexdigest())
