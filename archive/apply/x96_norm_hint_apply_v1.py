#!/usr/bin/env python3
"""x96_norm_hint_apply_v1.py · AE-Simulator · S73 · вирок В-85
живе доки: A7 «Система» не переписаний наново

Підказка дії в шапці області A7 брала рівень найгіршого рядка: будь-який ⚠ → «Перевірте…».
На чистих даних єдиний ⚠ — «товари без ціни… виправляти не треба» (норма), і шапка суперечила
рядку (S72 §0.1). Тепер: ✗ є → «Виправте…»; є ⚠ БЕЗ позначки norm → «Перевірте…»; інакше нічого.
Значок ⚠ і лічильник «1 попередження» лишаються: факт видно, дії не вимагають.
Позначку `norm` дають правила x95 (`ae_rules.js`). Правила без неї → поведінка як у X94.

Вхід: AE_WORK_index_X94_v1.html (md5 93b29b7c9a4ad003abc0b77dced91662)
Запуск: python3 x96_norm_hint_apply_v1.py <вхід.html> <вихід.html>
Ідемпотентність: маркер — ВУЗОЛ `const act =` в areaRow (П94).
"""
import sys, hashlib
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
MARK = "    const act = e ? 'err' : ms.some(m=>m.lvl==='warn'&&!m.norm) ? 'warn' : null;"
R = [
 ("    const w = ms.filter(m=>m.lvl==='warn').length, e = ms.filter(m=>m.lvl==='err').length;\n",
  "    const w = ms.filter(m=>m.lvl==='warn').length, e = ms.filter(m=>m.lvl==='err').length;\n"
  "    /* X96 · В-85: підказка дії — лише коли є що робити; ⚠-норма (norm, правила x95) дії не кличе. */\n"
  + MARK + "\n"),
 ("          HINT[worst] ? el('small',{class:'sys-hint',text:HINT[worst]}) : null])]),",
  "          act ? el('small',{class:'sys-hint',text:HINT[act]}) : null])]),"),
]
if MARK in s:
    print('  = уже застосовано (маркер-вузол act)')
else:
    for a, b in R:
        n = s.count(a)
        if n != 1: sys.exit(f'  ✗ якір знайдено {n} раз(и): {a[:60]}…')
        s = s.replace(a, b)
    print(f'  ✓ застосовано {len(R)} правки')
open(dst, 'w', encoding='utf-8').write(s)
print('вихід:', dst, '· md5', hashlib.md5(s.encode()).hexdigest())
