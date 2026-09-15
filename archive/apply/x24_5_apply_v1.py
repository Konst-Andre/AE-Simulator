#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x24_5_apply_v1.py — Х24.5 «ОДНІ ДВЕРІ».
живе доки: правку не внесено в репо AE-Simulator (фінальний пуш Олі, В-31) — тоді рецепт в архів.

Що робить (рівно одна правка, дім — index.html · function Summary() · блок .final-actions):
  знімає НИЖНЮ кнопку «До тренувань». Єдині двері виходу з E3 — верхня, у header.page-title.
  Щоб не лишити порожній div з margin-top:20px, блок .final-actions рендериться лише за retries > 0
  і несе тільки рядок «Повторні спроби: N».

Причина: device №2 (оператор, телефон, 12.09.2026) — на E3 двоє дверей «До тренувань», зверху й знизу.
CSS не чіпається: .final-actions (526) і мобільне правило (614–615) лишаються як є.

Гард (П34 · П37): повторний прогін — «вже застосовано», правок 0, exit 0, md5 не рухається.
Ланцюг: ОСТАННІМ, після x24_4_apply_v1.py.
Запуск: python3 x24_5_apply_v1.py <тека AE>
"""
import sys, os, hashlib

OLD = """      el('div', {class:'final-actions'}, [
        retries ? el('span', {style:'margin-right:auto;align-self:center;color:var(--anc-gray);font-size:13px'}, ['Повторні спроби: ', el('b', {style:'color:var(--anc-text)', text:String(retries)})]) : null,
        el('button', {type:'button', class:'secondary', onclick:toE1}, ['До тренувань'])])])]);"""

NEW = """      retries ? el('div', {class:'final-actions'}, [
        el('span', {style:'margin-right:auto;align-self:center;color:var(--anc-gray);font-size:13px'}, ['Повторні спроби: ', el('b', {style:'color:var(--anc-text)', text:String(retries)})])]) : null])]);"""


def md5(p):
    with open(p, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def main():
    if len(sys.argv) < 2:
        print('вкажіть теку AE'); return 2
    root = sys.argv[1]
    idx = os.path.join(root, 'index.html')
    if not os.path.isfile(idx):
        print('немає ' + idx); return 2
    src = open(idx, encoding='utf-8').read()

    if NEW in src:
        if OLD in src:
            print('x24_5: у файлі є І стара, І нова форма — стоп, дерево нечисте'); return 3
        print('x24_5: вже застосовано, без змін · правок 0')
        print('  md5 index.html=' + md5(idx)[:8]); return 0

    n = src.count(OLD)
    if n != 1:
        print('x24_5: чекав 1 збіг блоку .final-actions, знайшов ' + str(n) + ' — стоп'); return 3

    src = src.replace(OLD, NEW)

    # контроль: нижньої кнопки немає, верхня на місці — рівно одне «До тренувань» на весь файл
    doors = src.count("'До тренувань'")
    if doors != 1:
        print('x24_5: після правки дверей ' + str(doors) + ', чекав 1 — стоп'); return 3

    open(idx, 'w', encoding='utf-8').write(src)
    print('x24_5: застосовано · правок 1')
    print('   = П-1 нижню кнопку «До тренувань» знято (.final-actions)')
    print('   = П-2 .final-actions рендериться лише за retries > 0')
    print('   = заміряно: «До тренувань» у index.html — ' + str(doors))
    print('  md5 index.html=' + md5(idx)[:8])
    return 0


if __name__ == '__main__':
    sys.exit(main())
