#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x77_door_twoside_apply_v1.py — X77 «ЗВОРОТНИЙ БІК ДВЕРЕЙ» (черга, щабель 1, крок 1А)

Дефект: кнопка дверей має ОДИН бік. У кураторській оболонці вона так само
підписана «Куратор» і веде в settings — тобто з кураторського режиму в
тренажер кнопкою не вийти. Пункт, яким зайшов, не є перемикачем (S65 §0.1).

Крок 1А закриває вимоги 1 і 2 вузла одним вузлом: три стани однієї кнопки.
  замкнено                       — замок · «Куратор» · розкриває поле коду
  відімкнено, звичайний режим    — замок · «Куратор» · веде в settings
  відімкнено, кураторський режим — «грати» · «Тренажер» · веде в picker

Термін замка (В-66) — крок 1Б, тут його НЕМА.

РІШЕННЯ, НАЗВАНІ В МІКРОСКОПІ S66:
· сторона рахується з РЕЖИМУ, і режим береться з аргументу `active` — того
  самого, яким судить v2Nav. Судити з S.screen означало б завести другий дім
  одного судження: сьогодні значення збігаються, розійдуться мовчки.
· нового класу НЕ заводимо: H4 рахує голі імена, ⚠2 має лишитись ⚠2.
  Сторону несуть іконка, підпис і доступне ім'я — CSS не чіпається зовсім.
· aria-label додано тому, що в рейці 72 підпис схований (`.door-t{display:none}`),
  а іконка має aria-hidden: без імені кнопка безіменна для читача екрана.
  Це чинно було й до X77 — правиться заразом, бо той самий вузол.
· кутових дужок у коментарях НЕМА свідомо: H2 рахує імена тегів текстом
  і дав би хибне ⚠ на балансі через сам коментар (12.12).

Ідемпотентний: маркер X77-DOOR2. Повтор — «0 правок», exit 0, той самий md5.
Вхід : AE_WORK_index_X27Q2_v1.html   Вихід: AE_WORK_index_X27Q3_v1.html
"""
import sys, hashlib

MARK = 'X77-DOOR2'

# ── А · сторона обчислюється, маршрут виходу (вимоги 1 і 2) ────────────────
A_OLD = """function door(){
  const unlocked = CURATOR.open, open = DOOR.open && !unlocked;
  const head = el('button', {type:'button', class:'door-head', 'data-v2-door':'head',
      'aria-expanded':unlocked ? null : String(open),
      onclick:()=>{
        if(unlocked){ S.screen = 'settings'; render(); return; }"""
A_NEW = """function door(active){
  const unlocked = CURATOR.open, open = DOOR.open && !unlocked;
  /* ── X77-DOOR2 · ЗВОРОТНИЙ БІК (черга, щабель 1 · S65 §0.1) ──────────
     Три стани однієї кнопки, нового вузла немає. Сторона рахується з
     РЕЖИМУ, а режим береться з `active` — того самого аргументу, яким
     судить v2Nav. Другий дім одного судження (S.screen тут) сьогодні дав
     би те саме значення і розійшовся б мовчки рівно тоді, коли аргументи
     зміняться. Мікроскоп S66, вісь 4.
     живе доки: кураторський режим має вхід через ці двері. */
  const exit = unlocked && V2_CUR.has(active);
  const cap  = exit ? 'Тренажер' : 'Куратор';
  const head = el('button', {type:'button', class:'door-head', 'data-v2-door':'head',
      'aria-expanded':unlocked ? null : String(open),
      /* У рейці 72 підпис схований, а іконка несе aria-hidden — без цього
         імені кнопка безіменна для читача екрана. Чинне було й до X77. */
      'aria-label':cap,
      onclick:()=>{
        if(exit){ S.screen = 'picker'; render(); return; }
        if(unlocked){ S.screen = 'settings'; render(); return; }"""

# ── Б · іконка сторони (плитка й розмір не міняються: обидві 0 0 24 24) ────
B_OLD = """    [el('span', {class:'door-tile'}, [icon('i-lock')]),"""
B_NEW = """    [el('span', {class:'door-tile'}, [icon(exit ? 'i-play' : 'i-lock')]),"""

# ── В · підпис сторони + прибирання застарілого коментаря ─────────────────
C_OLD = """     /* SPEC §8.2 · стенд :1366: «режим» — службове слово, воно нічого не несе.
        Пара «Куратор ↔ Тренажер» — два боки однієї кнопки. Зворотний бік
        живе в кураторській оболонці, якої ще нема. */"""
C_NEW = """     /* SPEC §8.2 · стенд :1366: «режим» — службове слово, воно нічого не несе.
        Пара «Куратор ↔ Тренажер» — два боки однієї кнопки. Зворотний бік
        живий з X77: сторона обчислена вище. */"""

D_OLD = """el('b', {text:'Куратор'})"""
D_NEW = """el('b', {text:cap})"""

# ── Г · виклик отримує режим (єдиний виклик, :1132) ───────────────────────
E_OLD = """bare ? null : door()]);"""
E_NEW = """bare ? null : door(active)]);"""

EDITS = [('А · сторона й маршрут виходу', A_OLD, A_NEW),
         ('Б · іконка сторони',           B_OLD, B_NEW),
         ('В · коментар застарів',        C_OLD, C_NEW),
         ('Г · підпис сторони',           D_OLD, D_NEW),
         ('Д · виклик бере режим',        E_OLD, E_NEW)]


def main():
    if len(sys.argv) != 3:
        print('вжиток: x77_door_twoside_apply_v1.py <in.html> <out.html>')
        return 2

    html = open(sys.argv[1], encoding='utf-8').read()
    before = len(html.encode('utf-8'))

    if MARK in html:
        open(sys.argv[2], 'w', encoding='utf-8').write(html)
        print('0 правок — маркер %s уже у файлі (ідемпотентність)' % MARK)
        print('md5 %s · %d б' % (hashlib.md5(html.encode('utf-8')).hexdigest(), before))
        return 0

    if 'X76-RAIL-FIX' not in html:
        print('✗ вхід не той: немає маркера X76-RAIL-FIX (чекаю X27Q2)')
        return 1

    for name, old, new in EDITS:
        n = html.count(old)
        if n != 1:
            print('✗ якір «%s» знайдено %d разів, очікував 1' % (name, n))
            return 1
        html = html.replace(old, new)

    # ── самоперевірка · вісь 2 мікроскопа: жодна з цих перевірок не сміє
    #    дати ✗ на КОРЕКТНОМУ результаті. Рахуємо факти, не позиції.
    if html.count('door()') != 0:
        print('✗ самоперевірка: лишився виклик дверей без режиму'); return 1
    if html.count('door(active') != 2:
        print('✗ самоперевірка: оголошення й виклик не зійшлись на аргументі'); return 1
    if 'V2_CUR.has(active)' not in html:
        print('✗ самоперевірка: сторона не рахується з режиму'); return 1
    if "icon(exit ? 'i-play' : 'i-lock')" not in html:
        print('✗ самоперевірка: іконка сторони не перемикається'); return 1
    if html.count("text:cap") != 1 or "'aria-label':cap" not in html:
        print('✗ самоперевірка: підпис і доступне ім\'я не з однієї сторони'); return 1
    # ⚠ хибний ✗ першої редакції (вісь 2): шукали «'Куратор'» у тілі дверей —
    # але саме там він і мусить бути, в обчисленні сторони. Звіряти треба
    # ВУЗОЛ підпису, а не присутність слова.
    if "text:'Куратор'" in html:
        print('✗ самоперевірка: підпис лишився зашитим літералом'); return 1
    # П89, бік цілі: жодного нового імені класу не заведено
    for cls in ('door-head', 'door-tile', 'door-t', 'side-bottom'):
        if html.count(cls) < 2:
            print('✗ самоперевірка: %s втратив споживача' % cls); return 1

    after = len(html.encode('utf-8'))
    open(sys.argv[2], 'w', encoding='utf-8').write(html)
    print('%d правок · %+d б' % (len(EDITS), after - before))
    print('md5 %s · %d б' % (hashlib.md5(html.encode('utf-8')).hexdigest(), after))
    return 0


if __name__ == '__main__':
    sys.exit(main())
