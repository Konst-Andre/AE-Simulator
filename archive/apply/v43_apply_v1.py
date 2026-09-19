#!/usr/bin/env python3
"""v43_apply_v1.py · AE-Simulator · S78 · D1 v4.3 — mock_a2v2_tpl_v4_2.html → mock_a2v2_tpl_v4_3.html
живе доки: вирок D1 v4.3 не перенесено в продукт ходом D2 (після — в архів)
План: AE_D1v4_FINDINGS_v3.md розд. Н (Н1–Н8, погоджено S78) + М (О1, О3 — дешево, О2 не робимо) + О4 (кнопка груп).
Запуск: python3 v43_apply_v1.py   (поруч mock_a2v2_tpl_v4_2.html 5aade181…)
Кожна заміна — рівно один збіг, інакше assert. Детермінований (П34).
"""
import pathlib, hashlib
here = pathlib.Path(__file__).parent
t = (here/'mock_a2v2_tpl_v4_2.html').read_text(encoding='utf-8')
assert hashlib.md5(t.encode()).hexdigest().startswith('5aade181'), 'база не v4.2 (5aade181)'

def rep(old, new, n=1):
    global t
    c = t.count(old); assert c == n, f'якір ×{c} (очікувано {n}): {old[:70]!r}'
    t = t.replace(old, new)

# ── Н1 · «i» біля «Мета розмови»
rep('<label for="f-goal">Мета розмови</label>',
    '<div class="lab"><label for="f-goal">Мета розмови</label><button type="button" class="info" popovertarget="i-goal" aria-label="Хто бачить мету розмови" aria-expanded="false">i</button></div>'
    '<div class="tip" id="i-goal" popover><b>Мета розмови</b>Фармацевт бачить це до розмови — не пишіть сюди правильну відповідь.</div>')

# ── Н2 · «i» у шапках карток — на правий край, як у полів і прапорців
rep('.card h3 .ic{', '.card h3 .info{margin-left:auto}\n.card h3 .ic{')

# ── Н3 · тексти «i» джерел (ВТМ/ЗФ — з правила мережі RULE)
rep('Категорії й позиції — з Каталогу. Нова категорія — розділ «Каталог».',
    'Категорії й позиції тут не створюються — ви обираєте з готового Каталогу. Нова категорія, позиція чи ціна — розділ «Каталог».')
rep('Лише позиції з категорій сценарію. ВТМ — ідеально, ЗФ — теж добре; орієнтир — за ВТМ.',
    "Обираєте з позицій категорій цього сценарію (картка «Товари»). ${RULE==='bv'?'ВТМ':'ЗФ'} — найкращий набір, ${RULE==='bv'?'ЗФ':'ВТМ'} — теж добрий. "
    "Орієнтир у гривнях фармацевт бачить за ${RULE==='bv'?'ВТМ':'ЗФ'}. Бракує позиції — додайте її в «Каталозі».")
rep('З бібліотеки характерів, розділ «Промпти». Клієнт отримує опис, суддя — типову помилку.',
    'Як клієнт поводиться в розмові: що його відкриває, на що закривається. Обирається з 9 готових. '
    'Суддя знає, де з таким клієнтом найчастіше помиляються. Змінити опис — розділ «Промпти».')

# ── Н4 · ✎ біля назви: контраст ≥3:1 (#6E6E77 = --anc-gray), 18 px
rep("width='16' height='16' fill='none' stroke='%239B9CA1'", "width='18' height='18' viewBox='0 0 16 16' fill='none' stroke='%236E6E77'")
rep('no-repeat left 10px top 14px;padding-left:34px;', 'no-repeat left 9px top 13px;padding-left:36px;')

# ── Н5 · «Просить» у прев'ю — назва + категорія, без ціни (X97:1549–1551)
rep("${s.order.map(c=>row(c, money(ITEM[c]?.p))).join('')",
    "${s.order.map(c=>`<div class=\"pos\"><span class=\"wrap\">${esc(ITEM[c]?.n||c)}</span><span class=\"v cat\">${esc(D.cats[ITEM[c]?.cat]?.label||'')}</span></div>`).join('')")
rep('.pv .pos{', '.pv .pos .cat{color:var(--anc-gray);font-size:11.5px;text-align:right}\n.pv .pos{')

# ── Н6 · чип групи по центру рядка назви
rep('.badge.grp{display:inline-block;vertical-align:3px;', '.badge.grp{display:inline-block;vertical-align:middle;')

# ── Н7 · прихований «Не опубліковано» не займає місця
rep('.pub-why{grid-column:1 / -1;', '.pub-why[hidden]{display:none}\n.pub-why{grid-column:1 / -1;')

# ── Н8 · фраза клієнта — вже початок розмови
rep('<div class="bubble wrap">${esc(s.open)}</div>',
    '<div class="sec">Розмова починається з</div>\n    <div class="bubble wrap">${esc(s.open)}</div>')

# ── О1 · ≤1600 «Прев'ю»: список займає 2 рядки сітки й роздуває перший — зайве віддаємо другому · О3 · без другого заголовка
rep('  .page[data-view=pv] .editor .cards{display:none}\n',
    '  .page[data-view=pv] .editor .cards{display:none}\n'
    '  .page{grid-template-rows:auto 1fr} .page[data-view=pv]{row-gap:0}\n'
    '  .pv-h{display:none}\n')

# ── О4 · кнопка керування групами: іконка папки + підпис замість дрібного ✎
rep('.filter-row{display:grid;grid-template-columns:minmax(0,1fr) 40px;gap:8px}',
    '.filter-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px}\n'
    '.icon-btn.grp-btn{display:inline-flex;align-items:center;gap:6px;width:auto;padding:0 12px;font-size:13px;font-weight:600;color:var(--anc-text-2)}\n'
    '.grp-btn svg{width:18px;height:18px;flex:none}')
a = t.index('<button class="icon-btn" id="mg"'); b = t.index('</button>', a) + len('</button>')
t = t[:a] + ('<button class="icon-btn grp-btn" id="mg" title="Керувати групами: створити, перейменувати, видалити" aria-label="Керувати групами">'
             '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M3 7.5A1.5 1.5 0 0 1 4.5 6H9l2 2h8.5A1.5 1.5 0 0 1 21 9.5v8A1.5 1.5 0 0 1 19.5 19h-15A1.5 1.5 0 0 1 3 17.5z"/></svg>Групи</button>') + t[b:]

dst = here/'mock_a2v2_tpl_v4_3.html'
dst.write_text(t, encoding='utf-8')
print('шаблон:', dst.name, '· md5', hashlib.md5(t.encode()).hexdigest())
