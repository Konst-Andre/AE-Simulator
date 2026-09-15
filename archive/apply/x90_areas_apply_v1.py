#!/usr/bin/env python3
"""AE-Simulator · x90 · ОБЛАСТЬ (`area`) у кожен рядок tools/ae_rules.js
живе доки: A7 «Система» групує рядки правил за полем area (S71, крок A плану S70 §6)

Вхід/вихід:  python3 x90_areas_apply_v1.py <ae_rules.js> <вихід.js>
Ланцюг: правка йде в tools/, НЕ в HTML. Застосовувати до /home/claude/AE/tools/ae_rules.js
ДО копіювання в /mnt/user-data/outputs/AE і ДО збирання прев'ю (x70 v3 вшиває цей файл).

Механізм: змінна секції AREA, яку E/W/O дописують останнім полем.
НЕ позиційний аргумент: forEach(E) і forEach(W) передають (item, index, arr),
і в область потрапив би індекс масиву (S71, мікроскоп вісь 2).
Назва поля — area, не grp: grp уже є полем сценарію (REQ, пул рецептурних).

Маркер ідемпотентності — ВУЗОЛ (П94): lambda E з area:AREA.
Повтор на власному виході: exit 0, байт-у-байт той самий файл.
"""
import sys, pathlib

MARK = "const E=m=>{out.push({lvl:'err', msg:m, area:AREA}); err++};"

AREAS_BLOCK = """
/* ── ОБЛАСТІ ПРАВИЛ ───────────────────────────────────────────────────
   Порядок і людські підписи для екрана A7. Дім переліку — тут, поруч із
   секціями, які його ставлять; UI бере AE_RULES.AREAS і власної копії не
   тримає (12.11). Ключ рядка — поле area, не grp: grp — поле сценарію. */
const AREAS = [
  ['catalog',    'Каталог товарів'],
  ['scenarios',  'Сценарії'],
  ['characters', 'Характери і рядки mood'],
  ['potential',  'Приріст'],
  ['shift',      'Склад зміни'],
];
"""

SUBS = [
    ("];\n\nfunction validate(", "];\n" + AREAS_BLOCK + "\nfunction validate("),
    ("  const out=[]; let ok=0,warn=0,err=0;\n",
     "  const out=[]; let ok=0,warn=0,err=0;\n  let AREA=null;   // ставить кожна секція нижче; рядок без області = дефект\n"),
    ("  const E=m=>{out.push({lvl:'err', msg:m}); err++};", "  " + MARK),
    ("  const W=m=>{out.push({lvl:'warn',msg:m}); warn++};",
     "  const W=m=>{out.push({lvl:'warn',msg:m, area:AREA}); warn++};"),
    ("  const O=m=>{out.push({lvl:'ok',  msg:m}); ok++};",
     "  const O=m=>{out.push({lvl:'ok',  msg:m, area:AREA}); ok++};"),
    ("  // --- індекс товарів\n", "  AREA='catalog';\n  // --- індекс товарів\n"),
    ("  // --- сценарії\n", "  AREA='scenarios';\n  // --- сценарії\n"),
    ("  // --- характер: значення", "  AREA='characters';   // і розділ mood нижче\n  // --- характер: значення"),
    ("  // --- потенціал > 0\n", "  AREA='potential';\n  // --- потенціал > 0\n"),
    ("  // --- склад зміни:", "  AREA='shift';\n  // --- склад зміни:"),
    ("module.exports = { validate, MOOD_LIMIT, MOOD_SIGNS };",
     "module.exports = { validate, MOOD_LIMIT, MOOD_SIGNS, AREAS };"),
    ("globalThis.AE_RULES = { validate, MOOD_LIMIT, MOOD_SIGNS };",
     "globalThis.AE_RULES = { validate, MOOD_LIMIT, MOOD_SIGNS, AREAS };"),
]

def main():
    if len(sys.argv) != 3:
        print('вжиток: x90_areas_apply_v1.py <ae_rules.js> <вихід.js>'); return 2
    src = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
    dst = pathlib.Path(sys.argv[2])
    if MARK in src:
        dst.write_text(src, encoding='utf-8')
        print('  ○ вузол area:AREA уже є — без змін'); return 0
    for old, new in SUBS:
        n = src.count(old)
        if n != 1:
            print(f'  ✗ якір знайдено {n} раз(и): {old[:60]!r}'); return 3
        src = src.replace(old, new)
    # самоперевірка звіряє ВУЗОЛ (П91): присвоєння AREA у тілі = ключі AREAS, у тому ж порядку.
    # Секція без присвоєння мовчки успадкувала б попередню область (S71, ін'єкція 1).
    import re
    asg = re.findall(r"AREA='(\w+)'", src)
    keys = [k for k, _ in re.findall(r"\['(\w+)',\s*'([^']+)'\]", AREAS_BLOCK)]
    if asg != keys:
        print(f'  ✗ присвоєння {asg} ≠ AREAS {keys}'); return 4
    dst.write_text(src, encoding='utf-8')
    print(f'  ✓ застосовано {len(SUBS)} правок · області {",".join(asg)} · {len(src.encode())} б'); return 0

if __name__ == '__main__':
    sys.exit(main())
