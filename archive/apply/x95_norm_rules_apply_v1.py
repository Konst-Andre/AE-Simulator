#!/usr/bin/env python3
"""x95_norm_rules_apply_v1.py · AE-Simulator · S73 · вирок В-85
живе доки: правила не витіснені новим ланцюгом (репо → x90 → x92 → x95)

⚠-рядок може бути НОРМОЮ («так буває, виправляти не треба»). Рівень лишається `warn`
(лічильник ⚠ читають worker/ae-edit.js :276 :311 · smoke_rules_v1 :68 · smoke_ui_v1 :344
· smoke_edit_v2 :174 — зміна рівня зрушила б їх). Натомість W несе третій аргумент —
позначку `norm`, у ТОМУ САМОМУ виклику, що й msg/say (П104).
Позначку має рівно один рядок: товари без ціни (p:null).

⚠ Пастка forEach: W ніде не йде в forEach, але n береться лише як `===true`.

Вхід: tools/ae_rules.js після x92 (md5 f0c2f35cc5c68d57989b9e3a7b5b0c4a)
Запуск: python3 x95_norm_rules_apply_v1.py <вхід.js> <вихід.js>
Ідемпотентність: маркер — ВУЗОЛ оголошення W з трьома аргументами (П94).
"""
import sys, hashlib
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
MARK = "const W=(m,t,n)=>{out.push({lvl:'warn',msg:m, say:SAY(t), norm:n===true, area:AREA}); warn++};"
R = [
 ("const W=(m,t)=>{out.push({lvl:'warn',msg:m, say:SAY(t), area:AREA}); warn++};", MARK),
 (" ще без ціни. Так буває з новими позиціями, виправляти не треба');",
  " ще без ціни. Так буває з новими позиціями, виправляти не треба',true);"),
]
if MARK in s:
    print('  = уже застосовано (маркер-вузол W/3)')
else:
    for a, b in R:
        n = s.count(a)
        if n != 1: sys.exit(f'  ✗ якір знайдено {n} раз(и): {a[:60]}…')
        s = s.replace(a, b)
    print(f'  ✓ застосовано {len(R)} правки')
open(dst, 'w', encoding='utf-8').write(s)
print('вихід:', dst, '· md5', hashlib.md5(s.encode()).hexdigest())
