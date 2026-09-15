#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x71_curator_home_apply_v1.py — X71 «ДІМ КУРАТОРА»

живе доки: кураторські екрани (settings, escen) не переїхали в normalShell
           у самому продукті; після цього генератор — історія ланцюга.

Що робить (один крок черги S62 §5.1):
  A. заводить v2Adapt(fn) — адаптер старого екрана (fn(root)) у тіло для normalShell
  B. реєструє V2.settings і V2.escen через цей адаптер
  C. ставить у render() guard на самоперенаправлення екрана

Чому guard. Settings і ScenCard при зачиненому замку роблять
S.screen=...; render(); return — тобто ВКЛАДЕНИЙ рендер усередині рендера.
Без guard адаптер віддав би порожнє тіло, і app.append поклав би кураторську
оболонку ПОВЕРХ щойно намальованого екрана.

Ідемпотентний: повтор дає 0 правок, exit 0, той самий md5.
"""
import sys, os, re, hashlib

SRC = sys.argv[1] if len(sys.argv) > 1 else 'AE_WORK_index_X27P5_v1.html'
DST = sys.argv[2] if len(sys.argv) > 2 else 'AE_WORK_index_X27P6_v1.html'

MARK = 'X71-DIM-KURATORA'

NEW_BLOCK = """/* --- X71 - ДІМ КУРАТОРА (""" + MARK + """) --------------------------------
   Набір '6' мав механізм і не мав де показатись: кураторські екрани малювались
   старим шляхом, поза normalShell. Тепер дім є — але БЕЗ переписування самих
   екранів: старий екран приймає root і малює в нього, v2-екран повертає тіло.
   Адаптер зшиває дві форми, продукт екранів не знає.
   ⚠ Старий екран має право сам себе перенаправити (замок зачинено, запису
   немає): тоді він УЖЕ викликав render() і намалював інше. Його тіло віддавати
   не можна — воно лягло б поверх намальованого. Звіряємо S.screen до і після;
   розбіжність = null, і render() мовчки виходить.
   Підпис під пункт і зворотний бік дверей «Тренажер» — окремі кроки черги. */
function v2Adapt(fn){
  return function(){
    const want = S.screen;
    const box = el('div', {});
    fn(box);
    if(S.screen !== want) return null;
    return box;
  };
}
V2.settings = v2Adapt(Settings);
V2.escen    = v2Adapt(ScenCard);
/* --- /X71 --- */"""

OLD_RENDER = ("  if(v2){ app.append(normalShell(S.screen, v2())); "
              "railShift(); window.scrollTo(0,0); return; }")
NEW_RENDER = ("  if(v2){ const body = v2();\n"
              "    /* " + MARK + ": null = екран перенаправив сам себе, вкладений render() уже намалював */\n"
              "    if(body === null) return;\n"
              "    app.append(normalShell(S.screen, body)); "
              "railShift(); window.scrollTo(0,0); return; }")


def die(msg):
    print('ПОМИЛКА: ' + msg)
    sys.exit(1)


def main():
    if not os.path.exists(SRC):
        die('вхідного файлу немає: ' + SRC)
    src = open(SRC, encoding='utf-8').read()

    if MARK in src:
        # ідемпотентність: вхід уже оброблений
        open(DST, 'w', encoding='utf-8').write(src)
        print('0 правок — маркер ' + MARK + ' уже у вході (ідемпотентно)')
        print('md5 ' + hashlib.md5(src.encode('utf-8')).hexdigest() + '  ' + DST)
        return 0

    out = src
    edits = []

    # --- A+B: заміна коментаря «важіль без дому» на адаптер і реєстрацію ---
    # Якір беремо програмно, не дослівним рядком: у файлі сусідять два різні
    # апострофи (' та ʼ), дослівний match на них ламається.
    m = re.search(r"/\*\s*⚠ Набір '6'", out)
    if not m:
        die('не знайдено коментар «Набір 6 ... не має де показатись»')
    start = m.start()
    end = out.find('*/', start)
    if end == -1:
        die('коментар без закриття */')
    end += 2
    victim = out[start:end]
    if 'важіль без дому' not in victim:
        die('знайдений коментар не той: немає слів «важіль без дому»')
    out = out[:start] + NEW_BLOCK + out[end:]
    edits.append('A+B  коментар «важіль без дому» → v2Adapt + реєстрація ('
                 + str(len(victim)) + ' симв. знято)')

    # --- C: guard у render() ---
    n = out.count(OLD_RENDER)
    if n != 1:
        die('гілка v2 у render(): знайдено ' + str(n) + ' входжень, треба рівно 1')
    out = out.replace(OLD_RENDER, NEW_RENDER)
    edits.append('C    render(): guard на тіло null')

    # --- звірка результату ---
    for need in ['function v2Adapt(fn)', 'V2.settings = v2Adapt(Settings);',
                 'V2.escen    = v2Adapt(ScenCard);', 'if(body === null) return;']:
        if need not in out:
            die('після правки немає: ' + need)
    # два: шапка блоку A+B і коментар guard у render()
    if out.count(MARK) != 2:
        die('маркерів ' + MARK + ' має бути 2, є ' + str(out.count(MARK)))

    open(DST, 'w', encoding='utf-8').write(out)
    print('X71 · правок: ' + str(len(edits)))
    for e in edits:
        print('  · ' + e)
    print('delta ' + str(len(out) - len(src)) + ' байт')
    print('md5 ' + hashlib.md5(out.encode('utf-8')).hexdigest() + '  ' + DST)
    return 0


sys.exit(main())
