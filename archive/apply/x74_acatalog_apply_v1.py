#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x74_acatalog_apply_v1.py — X74 «КАТАЛОГ НЕ ТУДИ»

Щабель 1 черги (AE_Simulator_CHERGA.md), дефект S64 §0.1.

Пункт «Каталог» у наборі куратора ('6') ніс ключ 'catalog' — а це E6,
вітрина ТІЛЬКИ ДЛЯ ЧИТАННЯ для фармацевта. За SPEC у куратора там A3
(правка позицій). Оля натиснула б «Каталог» і опинилась би в екрані
звичайного режиму. Це другий примірник дефекту, названого П86:
спільний підпис у двох режимах = ДВА ключі, а не один.

Лікування — те саме й так само дешеве, що й для «Сценаріїв» (X72):
ключ 'acatalog' (пара до 'ascen'), у V2_CUR, екрана НЕ пишемо —
пункт лишається заглушкою, бо живість рахується з V2 (П80).

⚠ Картинка ЗРУШИТЬ: у куратора «Каталог» був живим, стане заглушкою.
Це не порушення wsd 1.18: знімається брехливий маршрут, і незрушена
картинка означала б, що дефект лишився. Оголошено наперед, щоб
device-раунд не сплутав цей зсув із чужою правкою.

Ідемпотентний: маркер X74-ACATALOG. Повтор — «0 правок», exit 0, той самий md5.
Вхід : AE_WORK_index_X27P8_v1.html   Вихід: AE_WORK_index_X27P9_v1.html
"""
import sys, hashlib

MARK = 'X74-ACATALOG'

# ── А · кураторський ключ «Каталог» → 'acatalog' ───────────────────────────
# Якір — ДВА рядки набору '6': один рядок ['catalog',...] трапляється тричі
# (набори '2', '4', '6'), і сам по собі не унікальний.
A_OLD = """  '6': [['dash','i-grid','Дашборд'],      ['ascen','i-doc','Сценарії'],
        ['catalog','i-box','Каталог'],    ['models','i-chip','AI / Моделі'],"""
A_NEW = """  '6': [['dash','i-grid','Дашборд'],      ['ascen','i-doc','Сценарії'],
        ['acatalog','i-box','Каталог'],   ['models','i-chip','AI / Моделі'],"""

# ── Б · 'acatalog' — кураторський екран, тож у V2_CUR ──────────────────────
B_OLD = """/* X72: 'ascen' — кураторський «Сценарії» (правка, A2 мокапу). Ключ окремий від
   звичайного 'scenarios' (E4, список): підпис спільний, екрани різні. */
const V2_CUR = new Set(['dash','models','prompts','system','settings','escen','ascen']);"""
B_NEW = """/* X72: 'ascen' — кураторський «Сценарії» (правка, A2 мокапу). Ключ окремий від
   звичайного 'scenarios' (E4, список): підпис спільний, екрани різні.
   X74-ACATALOG: те саме для «Каталогу». 'catalog' — E6, вітрина фармацевта
   тільки для читання; у куратора за SPEC A3 (правка позицій), ключ 'acatalog'.
   Обидва кураторські пункти — заглушки, поки немає екранів (живість з V2, П80). */
const V2_CUR = new Set(['dash','models','prompts','system','settings','escen','ascen','acatalog']);"""


def main():
    if len(sys.argv) != 3:
        print('вжиток: x74_acatalog_apply_v1.py <in.html> <out.html>')
        return 2

    html = open(sys.argv[1], encoding='utf-8').read()
    before = len(html.encode('utf-8'))

    if MARK in html:
        open(sys.argv[2], 'w', encoding='utf-8').write(html)
        print('0 правок — маркер %s уже у файлі (ідемпотентність)' % MARK)
        print('md5 %s · %d б' % (hashlib.md5(html.encode('utf-8')).hexdigest(), before))
        return 0

    if 'X73-NO-NUMBER' not in html:
        print('✗ вхід не той: немає маркера X73-NO-NUMBER (чекаю X27P8)')
        return 1

    edits = 0
    for name, old, new in (('А · набір 6', A_OLD, A_NEW), ('Б · V2_CUR', B_OLD, B_NEW)):
        n = html.count(old)
        if n != 1:
            print('✗ якір «%s» знайдено %d разів, очікував 1' % (name, n))
            return 1
        html = html.replace(old, new, 1)
        edits += 1
        print('✓ %s' % name)

    # самоперевірка: ключ у наборі і в множині, старого маршруту куратора немає
    if html.count("['acatalog','i-box','Каталог']") != 1:
        print('✗ самоперевірка: пункт acatalog не єдиний'); return 1
    if "'ascen','acatalog'" not in html:
        print('✗ самоперевірка: acatalog не потрапив у V2_CUR'); return 1

    after = len(html.encode('utf-8'))
    open(sys.argv[2], 'w', encoding='utf-8').write(html)
    print('%d правки · %+d б' % (edits, after - before))
    print('md5 %s · %d б' % (hashlib.md5(html.encode('utf-8')).hexdigest(), after))
    return 0


if __name__ == '__main__':
    sys.exit(main())
