#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x76_rail_regress_fix_v1.py — X76 «РЕЙКА БЕЗ КАНТУ»

Device-фідбек оператора по X27Q1 (ПК). Два дефекти, обидва — регреси X75,
жоден не був видимий гейтам.

Д-1 · КАНТ І ПРОПОРЦІЯ ЛОГОТИПА.
X75 перетворив логотип із блока на <button> і НЕ приніс правило, яке в
стенді жило саме заради цього: AE_X27_SIDEBAR_v19 :254
    .v2 .brand-mark{cursor:pointer;border:0;padding:0}
Без нього кнопка дістала браузерний border (на круглій плитці читається як
півеліпс канту) і браузерний padding (стиснув внутрішню площу, а svg
рахується як 75 % від неї — звідси менші «долоньки»).
⚠ Це ДЗЕРКАЛО П87: правило, що народилось разом із важелем, мусить
приїжджати разом із ним так само, як зникає разом із ним.

Д-2 · ПІДПИС «КУРАТОР» НЕ ЗНИКАЄ В РЕЙЦІ.
X75 приніс зі стенда два правила по `.side-bottom`. У продукті класу
`.side-bottom` НЕМА В РОЗМІТЦІ ВЗАГАЛІ (грепнуто: 0 входжень у JS —
він живе тільки в CSS із порту макета). Двері продукту: `.door` →
`.door-head` → `.door-t b`. Тобто обидва правила мертві від народження,
а справжній підпис не ховав ніхто.
Лікування — ті самі два правила, але по іменах, які в продукті існують.

⚠ Підложка замка `.door-tile` у рейці ЛИШАЄТЬСЯ свідомо: у рейці вона —
єдине, що відрізняє двері від пунктів меню, які там теж самі іконки.
Питання винесене оператору окремим предметом device-раунду, вироку не має.

Ідемпотентний: маркер X76-RAIL-FIX. Повтор — «0 правок», exit 0, той самий md5.
Вхід : AE_WORK_index_X27Q1_v1.html   Вихід: AE_WORK_index_X27Q2_v1.html
"""
import sys, hashlib

MARK = 'X76-RAIL-FIX'

# ── Д-1 · пропущений рядок стенда :254 ─────────────────────────────────────
A_OLD = """   ⚠ transition НЕМА свідомо: плавність — окремий щабель черги (рух Х27-К3). */
@media (min-width:981px) {"""
A_NEW = """   ⚠ transition НЕМА свідомо: плавність — окремий щабель черги (рух Х27-К3). */
/* X76-RAIL-FIX · Д-1 · стенд :254. X75 зробив логотип кнопкою і забув оце.
   Браузерна кнопка приносить власні border і padding: перший малює кант по
   круглій плитці, другий стискає площу, від якої svg бере свої 75 %.
   Правило поза @media: кнопкою логотип лишається на будь-якій ширині. */
.v2 .brand-mark { cursor:pointer; border:0; padding:0; }
@media (min-width:981px) {"""

# ── Д-2 · мертві правила по .side-bottom → реальні імена дверей ────────────
B_OLD = """  .v2[data-mode="rail"] .side-bottom button { justify-content:center; gap:0; padding:9px 0; }
  .v2[data-mode="rail"] .side-bottom .lbl { display:none; }"""
B_NEW = """  /* X76-RAIL-FIX · Д-2 · порт X75 цілив у `.side-bottom`, якого в розмітці
     продукту не існує (0 входжень у JS). Двері тут: .door > .door-head >
     .door-t. Підложка .door-tile у рейці лишається — див. шапку файла. */
  .v2[data-mode="rail"] .door .door-head { justify-content:center; gap:0; padding:8px 0; }
  .v2[data-mode="rail"] .door .door-t { display:none; }"""

EDITS = [('Д-1 · brand-mark без канту', A_OLD, A_NEW),
         ('Д-2 · підпис дверей у рейці', B_OLD, B_NEW)]


def main():
    if len(sys.argv) != 3:
        print('вжиток: x76_rail_regress_fix_v1.py <in.html> <out.html>')
        return 2

    html = open(sys.argv[1], encoding='utf-8').read()
    before = len(html.encode('utf-8'))

    if MARK in html:
        open(sys.argv[2], 'w', encoding='utf-8').write(html)
        print('0 правок — маркер %s уже у файлі (ідемпотентність)' % MARK)
        print('md5 %s · %d б' % (hashlib.md5(html.encode('utf-8')).hexdigest(), before))
        return 0

    if 'X75-RAIL' not in html:
        print('✗ вхід не той: немає маркера X75-RAIL (чекаю X27Q1)')
        return 1

    for name, old, new in EDITS:
        n = html.count(old)
        if n != 1:
            print('✗ якір «%s» знайдено %d разів, очікував 1' % (name, n))
            return 1
        html = html.replace(old, new, 1)
        print('✓ %s' % name)

    # самоперевірка: мертвих правил по .side-bottom у стані rail не лишилось
    if 'data-mode="rail"] .side-bottom' in html:
        print('✗ самоперевірка: лишилось правило rail по неіснуючому .side-bottom'); return 1
    if '.v2 .brand-mark { cursor:pointer; border:0; padding:0; }' not in html:
        print('✗ самоперевірка: правило :254 не приїхало'); return 1
    if '.v2[data-mode="rail"] .door .door-t { display:none; }' not in html:
        print('✗ самоперевірка: підпис дверей у рейці не ховається'); return 1

    after = len(html.encode('utf-8'))
    open(sys.argv[2], 'w', encoding='utf-8').write(html)
    print('%d правки · %+d б' % (len(EDITS), after - before))
    print('md5 %s · %d б' % (hashlib.md5(html.encode('utf-8')).hexdigest(), after))
    return 0


if __name__ == '__main__':
    sys.exit(main())
