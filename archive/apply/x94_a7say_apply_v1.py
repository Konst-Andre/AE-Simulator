#!/usr/bin/env python3
"""x94_a7say_apply_v1.py · AE-Simulator · крок C3 (S72)
живе доки: X94 не витіснений новим ланцюгом продукту

A7 говорить людською мовою: рядок перевірки = `say` з правил (x92); технічний `msg`
лишається лише підказкою під курсором (title) для розробника. Підказка дії — ЛИШЕ в шапці
області (погоджено оператором S72), за мокапом: ⚠ «Перевірте…» · ✗ «Виправте…».
Правила без `say` (старші за x92) показують msg — чесний відкат, не порожній рядок.
Вхід: AE_WORK_index_X93_v1.html (md5 0f3b0f4966236e3fdc06b271a5b65c53)
Запуск: python3 x94_a7say_apply_v1.py <вхід.html> <вихід.html> · маркер — вузол HINT (П94).
"""
import sys, hashlib
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
MARK = "  const HINT = {err:'Виправте перед публікацією.', warn:'Перевірте перед публікацією.'};"
R = [
("  const RANK = {err:0, warn:1, ok:2};",
 "  const RANK = {err:0, warn:1, ok:2};\n  /* X94-C3 · підказка дії лише в шапці області (S72); для ✓ — нічого, як у рядку без зауважень. */\n" + MARK),
("        el('summary',{},[ico(worst), el('div',{},[el('b',{text:label}), el('small',{text:sub})])]),",
 "        el('summary',{},[ico(worst), el('div',{},[el('b',{text:label}), el('small',{text:sub}),\n          HINT[worst] ? el('small',{class:'sys-hint',text:HINT[worst]}) : null])]),"),
("          el('span',{text:SIGN[m.lvl]}), el('span',{text:m.msg})])))",
 "          el('span',{text:SIGN[m.lvl]}), el('span',{text:m.say||m.msg, title:m.msg})])))"),
(".v2 .sys-rules .err > span:first-child { color:#b72745; }",
 ".v2 .sys-rules .err > span:first-child { color:#b72745; }\n.v2 .system-message small.sys-hint { color:#34465c; }   /* X94-C3 · підказка дії темніша за лічильник */"),
]
if MARK in s: print("= маркер X94-C3 уже є — повтор без змін")
else:
    for i,(a,b) in enumerate(R):
        n=s.count(a)
        if n!=1: sys.exit(f"✗ заміна {i}: {n} входжень: {a[:60]!r}")
        s=s.replace(a,b)
    print(f"  ✓ {len(R)} замін")
open(dst,'w',encoding='utf-8').write(s)
print("вихід:", dst, "· md5", hashlib.md5(s.encode('utf-8')).hexdigest())
