#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x69_titles_apply_v1.py — AE-Simulator · «ШАПКИ БЕЗ ПІДПИСІВ» (вирок S62)

живе доки: шапки екранів не перебудовані Х28

Вхід : AE_WORK_index_X27P4_v1.html   md5 b186a15fccfe76818bd463bb22fc4c59
Вихід: AE_WORK_index_X27P5_v1.html

ТРИ ПРАВКИ (маркер кожної — з унікального тіла вставки, П76):
  1. E1: шапка тільки «Тренування»          маркер: Х27-П5 · шапка E1
  2. E6: шапка тільки «Каталог»             маркер: Х27-П5 · шапка E6
  3. двері: другий рядок знято              маркер: Х27-П5 · двері

⚠ E3 «Підсумок зміни» НЕ чіпаю: його другий рядок несе ДАНІ («Завершено
  розмов: N»), а не пояснення. Вирок оператора називав Тренування й Каталог.
⚠ Вирівнювання підпису дверей по іконці окремої правки не потребує:
  .door-head уже має align-items:center (:633), з одним рядком центр сам.
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('AE_WORK_index_X27P4_v1.html')
DST = pathlib.Path('AE_WORK_index_X27P5_v1.html')
SRC_MD5 = 'b186a15fccfe76818bd463bb22fc4c59'

OLD_1 = """      el('div', {}, [el('h1', {text:'Тренування'}),
        el('p', {text:'Оберіть замовлення або почніть зміну з ' + (E1_GEN[n] || n) + ' розмов'})]),"""
NEW_1 = """      /* Х27-П5 · шапка E1: екран несе ЛИШЕ свою назву (вирок оператора S62).
         Пояснювальний підпис знято — екран називає себе сам. */
      el('div', {}, [el('h1', {text:'Тренування'})]),"""
MK_1 = 'Х27-П5 · шапка E1'

OLD_2 = """    el('header', {class:'page-title'}, [el('div', {}, [el('h1', {text:'Каталог'}), el('p', {text:'Асортимент: що є, почім і що дає бонус'})])]),"""
NEW_2 = """    /* Х27-П5 · шапка E6: лише назва (вирок оператора S62) */
    el('header', {class:'page-title'}, [el('div', {}, [el('h1', {text:'Каталог'})])]),"""
MK_2 = 'Х27-П5 · шапка E6'

OLD_3 = """     el('span', {class:'door-t'}, [el('b', {text:'Куратор'}),
       el('small', {text:unlocked ? 'відімкнено' : 'відкривається кодом'})])]);"""
NEW_3 = """     /* Х27-П5 · двері: один рядок. Стан «відімкнено/кодом» і так видно —
        замок відкривається полем коду просто під кнопкою. */
     el('span', {class:'door-t'}, [el('b', {text:'Куратор'})])]);"""
MK_3 = 'Х27-П5 · двері'

EDITS = [('1. шапка E1', MK_1, OLD_1, NEW_1),
         ('2. шапка E6', MK_2, OLD_2, NEW_2),
         ('3. двері — один рядок', MK_3, OLD_3, NEW_3)]


def main() -> int:
    raw = SRC.read_bytes(); md5 = hashlib.md5(raw).hexdigest()
    print(f'вхід : {SRC} · md5 {md5}' + ('  ✓' if md5 == SRC_MD5 else '  ⚠ інший вхід'))
    t = raw.decode('utf-8'); done = 0
    for name, mark, old, new in EDITS:
        if mark in t: print(f'  {name} — вже було'); continue
        if t.count(old) != 1:
            print(f'  ✗ {name}: якір знайдено {t.count(old)} разів'); return 2
        t = t.replace(old, new, 1); done += 1; print(f'  {name} — внесено')
    out = t.encode('utf-8'); DST.write_bytes(out)
    print(f'вихід: {DST} · md5 {hashlib.md5(out).hexdigest()} · правок: {done}')
    for needle, want, what in [('відкривається кодом', 0, 'решток підпису дверей'),
                               ('Оберіть замовлення', 0, 'решток підпису E1'),
                               ('Асортимент: що є', 0, 'решток підпису E6'),
                               ('door-input', 1, 'поле коду куратора — МУСИТЬ лишитись'),
                               ('DOOR.show', 3, 'око «показати код» — МУСИТЬ лишитись')]:
        got = t.count(needle)
        ok = (got == 0) if want == 0 else (got >= want)
        print(f'  · {what}: {got}' + ('  ✓' if ok else '  ⚠ НЕ СХОДИТЬСЯ'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
