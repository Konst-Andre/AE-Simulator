#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x29v_apply_v1.py — AE · Х29-в · рецепт AE_X27_SIDEBAR_v12.html -> v14

живе доки: тінь острівців не записана в LEVER_LOCK + SPEC §13.3 (тоді — архів)

ЧОМУ НЕ v13
  v13 ніс Х29-б (шапка острівцем · контекст-1 ширша · стеля на колонку).
  Оператор на device відхилив усі три (В-44, S58). v14 = v12 + САМА ТІЛЬКИ
  секція В (тінь) + паспорт. Рецепт x29b_apply_v1.py лишається відтворюваним
  записом відхиленого варіанта — його НЕ видаляємо (П59: те, чого немає в
  Project, невідтворюване).

ЩО РОБИТЬ
  В   · --isl-shadow поширюється на всі острівці зліпка: контекст-1, контекст-2,
        метрики, підсумок, каталог, двері. ⚠ .toast і .primary НЕ чіпає.
  П64 · стартова позиція = паспорт оператора з чату 13.09.2026:
        кути=лише до контенту · радіус 28 · відступ 0 · тінь 0 1px 5px 1px #1C1E242e.

⚠ ШАБЛОНІВ ЗЛІПКА НЕ ЧІПАЄ (snapCSS :424-1145 та ін.). Уся CSS їде через
  <style id="lv-page"> — останній вузол shadowRoot. Дерево продукту не піднімаємо.

ІДЕМПОТЕНТНИЙ: повтор дає exit 0, конвеєра не друкує, md5 не змінює (П34·П37).
"""
import hashlib, io, os, sys

SRC = 'AE_X27_SIDEBAR_v12.html'
DST = 'AE_X27_SIDEBAR_v14.html'
SRC_MD5 = '5420320a12ea227835b3723050cec2d2'

EDITS = [

 ('В · тінь на всі острівці',
  "function paintPage(){\n  if(!LV) return;\n  var css = '';\n",
  "function paintPage(){\n  if(!LV) return;\n  var css = '';\n"
  "  /* ══ Х29-в · ТІНЬ НА ВСІ ОСТРІВЦІ (S58) ══════════════════════════════\n"
  "     Грепнуто у v12: --isl-shadow жив лише на .sidebar/.head/main, а картки\n"
  "     зліпка носили вшите «0 6px 22px #1C1E2410» — число з часів, коли вони\n"
  "     лежали на канві острівця. Канви в bare немає, і важіль тіні керував не\n"
  "     всім, що око читає як острівець. Правила вшиті в snapCSS (:794 :876\n"
  "     :912 :920 :940 :1053) — шаблон чіпати не можна, тому перебиваємо\n"
  "     останнім вузлом тіні при РІВНІЙ специфічності (.door-card має 0,3,0).\n"
  "     ⚠ .toast і .primary НЕ острівці — їхня тінь лишається своя. */\n"
  "  css += '.v2 .panel,.v2 .scenario-list,.v2 .scenario-detail,.v2 .metric,'\n"
  "       + '.v2 .summary-section,.v2 .wide-table-card{box-shadow:var(--isl-shadow)}'\n"
  "       + '.v2 .door.is-open .door-card{box-shadow:var(--isl-shadow)}';\n"),

 ('В · кути за паспортом',
  "              corners:'all' };",
  "              corners:'right' };"),

 ('П64 · радіус 28 · відступ 0',
  "g('rR').value=24; g('rI').value=24;\n"
  "V2.style.setProperty('--isl-radius','24px'); V2.style.setProperty('--isl-inset','24px');\n"
  "g('oR').textContent='24px'; g('oI').textContent='24px';",
  "g('rR').value=28; g('rI').value=0;\n"
  "V2.style.setProperty('--isl-radius','28px'); V2.style.setProperty('--isl-inset','0px');\n"
  "g('oR').textContent='28px'; g('oI').textContent='0px';"),

 ('П64 · тінь 0 1px 5px 1px #1C1E242e',
  "g('rY').value=5; g('rBl').value=12; g('rSp').value=0; g('rA').value=5;",
  "g('rY').value=1; g('rBl').value=5; g('rSp').value=1; g('rA').value=18;"),

 ('П64 · паспорт друкує свою версію',
  "var txt=['AE · Х27 v11 · стан важелів',",
  "var txt=['AE · Х27 v14 · стан важелів',"),
]


def main():
    if not os.path.exists(SRC):
        print('✗ немає бази ' + SRC); return 2
    src = io.open(SRC, encoding='utf-8').read()
    got = hashlib.md5(src.encode('utf-8')).hexdigest()
    if got != SRC_MD5:
        print('✗ md5 бази не той: ' + got + ' ≠ ' + SRC_MD5); return 2

    base = io.open(DST, encoding='utf-8').read() if os.path.exists(DST) else src
    out, applied, already = base, [], []
    for tag, old, new in EDITS:
        if new in out:
            already.append(tag); continue
        if out.count(old) != 1:
            print('✗ якір «' + tag + '»: збігів ' + str(out.count(old)) + ', треба 1'); return 2
        out = out.replace(old, new, 1); applied.append(tag)

    io.open(DST, 'w', encoding='utf-8').write(out)
    if applied:
        print('конвеєр v12 → v14')
        for t in applied: print('  + ' + t)
    else:
        print('вже застосовано, ' + str(len(already)) + ' правок на місці — файл не змінено')
    print('md5 ' + DST + ' = ' + hashlib.md5(out.encode('utf-8')).hexdigest())
    return 0


if __name__ == '__main__':
    sys.exit(main())
