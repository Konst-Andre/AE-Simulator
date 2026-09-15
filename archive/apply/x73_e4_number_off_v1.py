#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x73_e4_number_off_v1.py — X73 «НОМЕР НЕ ТУТ»

Вирок оператора В-64 (device S64, планшет): колонка «Номер» з E4 знімається.
Номер замовлення — реквізит ІНТЕРНЕТ-ЗАМОВЛЕННЯ, яким клієнт відкриває розмову.
Він живе у першій фразі клієнта і в картці розмови, а не у вітрині списку:
там він нічого не розрізняє (у 5 з 43 записів його взагалі немає) і займає
першу, найпомітнішу колонку. На E1 оператор його вже зняв раніше — E4
приводиться до тієї самої межі.

Наслідки, зняті разом із колонкою (інакше лишились би мертві важелі):
  · гілка клітинки 'no' і підпис «На місці»;
  · CSS .v2 .e4-noplace — єдиний споживач зник;
  · номер у полі пошуку: шукати за тим, чого на екрані немає, — брехня.

Ідемпотентний: маркер X73-NO-NUMBER. Повтор — «0 правок», exit 0, той самий md5.
Вхід : AE_WORK_index_X27P7_v1.html   Вихід: AE_WORK_index_X27P8_v1.html
"""
import sys, hashlib

MARK = 'X73-NO-NUMBER'

A_OLD = """const E4_COLS = [['no','Номер'], ['title','Назва'], ['who','Клієнт'], ['grp','Група']];"""
A_NEW = """/* X73-NO-NUMBER · В-64: номер замовлення — реквізит розмови, не вітрини.
   Колонки лишаються ті, що справді розрізняють сценарії між собою. */
const E4_COLS = [['title','Назва'], ['who','Клієнт'], ['grp','Група']];"""

B_OLD = """    return all().filter(s => ((s.no ? s.no + ' ' : '') + s.title + ' ' + s.who).toLowerCase().includes(t)); };"""
B_NEW = """    return all().filter(s => (s.title + ' ' + s.who).toLowerCase().includes(t)); };"""

C_OLD = """        f==='no' ? [s.no ? '№ ' + s.no : el('span', {class:'e4-noplace', text:'На місці'})]
      : f==='title' ? [el('b', {text:s.title})]"""
C_NEW = """        f==='title' ? [el('b', {text:s.title})]"""

D_OLD = """/* X72 · E4: сценарій без номера — не порожня клітинка, а названа причина */
.v2 .e4-noplace { color:var(--anc-gray); }
"""
D_NEW = ""

E_OLD = """   Колонки — рівно ті поля, що в даних є: no (у 38 з 43 записів), title,
   who, grp. Номера немає — «На місці», як у мокапі."""
E_NEW = """   Колонки — title, who, grp. Колонки «Номер» тут НЕМА (В-64, X73): номер
   замовлення живе у першій фразі клієнта і в картці розмови."""


def main():
    if len(sys.argv) != 3:
        print('вжиток: x73_e4_number_off_v1.py <in.html> <out.html>'); return 2
    html = open(sys.argv[1], encoding='utf-8').read()
    before = len(html.encode('utf-8'))

    if MARK in html:
        open(sys.argv[2], 'w', encoding='utf-8').write(html)
        print('0 правок — маркер %s уже в файлі (ідемпотентність)' % MARK)
        print('md5 %s · %d б' % (hashlib.md5(html.encode('utf-8')).hexdigest(), before))
        return 0

    if 'X72-SCENARIOS' not in html:
        print('✗ вхід не має X72 — X73 застосовується поверх X72'); return 1

    for name, old, new in [('А · E4_COLS без «Номер»', A_OLD, A_NEW),
                           ('Б · пошук без номера', B_OLD, B_NEW),
                           ('В · гілка клітинки no', C_OLD, C_NEW),
                           ('Г · CSS .e4-noplace (мертвий)', D_OLD, D_NEW),
                           ('Ґ · паспорт блоку', E_OLD, E_NEW)]:
        n = html.count(old)
        if n != 1:
            print('✗ %s: якір знайдено %d разів, чекали 1' % (name, n)); return 1
        html = html.replace(old, new)
        print('✓ %s' % name)

    open(sys.argv[2], 'w', encoding='utf-8').write(html)
    after = len(html.encode('utf-8'))
    print('5 правок · %+d б · md5 %s' % (after - before, hashlib.md5(html.encode('utf-8')).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
