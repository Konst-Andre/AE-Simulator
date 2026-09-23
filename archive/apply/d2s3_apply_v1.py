#!/usr/bin/env python3
"""d2s3_apply_v1.py · AE-Simulator · S84 · D2 крок 3 — В-107 суддя бачить обидва набори; одне правило «який набір ідеальний»
живе доки: запечено в X103 (лежить в archive/apply/ як ланцюг)
Вхід: корінь AE (index.html X102 d145ac74…, prompts/judge.md). Пише <вихід>/index.html і <вихід>/judge.md.
Кожна заміна — assert ×1. Повтор на виході = відмова (П34).
Запуск: python3 d2s3_apply_v1.py <корінь AE> <тека виходу>
"""
import sys, hashlib, pathlib
root, out = map(pathlib.Path, sys.argv[1:3]); out.mkdir(parents=True, exist_ok=True)
t = (root/'index.html').read_text(encoding='utf-8'); j = (root/'prompts/judge.md').read_text(encoding='utf-8')
assert hashlib.md5(t.encode()).hexdigest().startswith('d145ac74'), 'вхід не X102'
def sub(s, R):
    for a, b in R:
        n = s.count(a); assert n == 1, (n, a[:60]); s = s.replace(a, b)
    return s
t = sub(t, [
 ("const idealOf = sc => S.cfg.rule==='vtm' ? (sc.bv||[]) : (sc.bm||[]);",
  "/* В-107 · два набори — одне правило. Який набір ідеальний, вирішує config.rule (vtm → bv, stm → bm);\n"
  "   другий — «теж добрий»: не помилка, але в орієнтир не входить (В-120). Раніше правило жило двічі —\n"
  "   тут (запас bm) і в buildJudge (запас bv); для невідомого rule вони розходились. Запас — ВТМ, як у мокапі A2. */\n"
  "const setsOf = sc => S.cfg.rule==='stm'\n"
  "  ? {best:sc.bm||[], alt:sc.bv||[], bestLab:'ЗФ',  altLab:'ВТМ'}\n"
  "  : {best:sc.bv||[], alt:sc.bm||[], bestLab:'ВТМ', altLab:'ЗФ'};\n"
  "const idealOf = sc => setsOf(sc).best;"),
 ("  const ideal = (S.cfg.rule==='stm' ? sc.bm : sc.bv) || [];\n", "  const sets = setsOf(sc), pot = potential(sc);   /* В-107 · В-119 */\n"),
 ("pot: (potential(sc) ?? '—'),   /* В-119: judge.md пише «{{pot}} ₴» — формулювання для «—» → крок 3 */",
  "pot: pot===null ? 'не задано — ідеального набору в сценарії немає' : pot+' ₴',"),
 ("    idealList: nameOf(ideal),\n",
  "    idealList: nameOf(sets.best), idealLab: sets.bestLab,\n    altList: nameOf(sets.alt), altLab: sets.altLab,\n"),
])
j = sub(j, [
 ("Орієнтир цього сценарію: {{pot}} ₴.\nІдеальний чек: {{idealList}}.\n",
  "Орієнтир цього сценарію: {{pot}}.\nІдеальний чек ({{idealLab}}): {{idealList}}.\n"
  "Теж добрий чек ({{altLab}}): {{altList}}. Зібрати його — не помилка, але орієнтир і приріст рахуються тільки за ідеальним.\n"),
 ("проти орієнтира {{pot}} ₴ —", "проти орієнтира {{pot}} —"),
])
(out/'index.html').write_text(t, encoding='utf-8'); (out/'judge.md').write_text(j, encoding='utf-8')
for f in ('index.html','judge.md'): print(f, hashlib.md5((out/f).read_bytes()).hexdigest())
