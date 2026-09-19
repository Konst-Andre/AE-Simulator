#!/usr/bin/env python3
"""v42_apply_v1.py · AE-Simulator · S78 · D1 v4.2 — шаблон mock_a2v2_tpl_v4.html → mock_a2v2_tpl_v4_2.html
живе доки: вирок D1 v4.2 не перенесено в продукт ходом D2 (після — в архів)
План: AE_D1v4_FINDINGS_v2.md розд. И (погоджено оператором, S77).
Запуск: python3 v42_apply_v1.py   (поруч mock_a2v2_tpl_v4.html 3eb2b85e…)
Кожна заміна — рівно один збіг, інакше assert. Детермінований (П34).
"""
import pathlib, hashlib
here = pathlib.Path(__file__).parent
src = (here/'mock_a2v2_tpl_v4.html').read_text(encoding='utf-8')
assert hashlib.md5(src.encode()).hexdigest().startswith('3eb2b85e'), 'база не v4 (3eb2b85e)'
t = src

def rep(old, new, n=1):
    global t
    c = t.count(old); assert c == n, f'якір ×{c} (очікувано {n}): {old[:60]!r}'
    t = t.replace(old, new)

# ── Ж2b · мітки в списку не витісняють групу й характер: до 2 рядків, без обрізання
rep('.scenario-item small{display:block;margin-top:3px;color:var(--anc-gray);font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
    '.scenario-item small{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:3px;color:var(--anc-gray);font-size:11px;line-height:1.35}')

# ── Ж8 · ✎ ліворуч від назви — завжди біля тексту
rep('no-repeat right 10px top 14px;padding-right:34px;', 'no-repeat left 10px top 14px;padding-left:34px;')

# ── Ж7 · плейсхолдер не пункт розкритого списку
rep('<option value="">+ Додати</option>', '<option value="" hidden>+ Додати</option>')
rep('<option value="">${s.cats.length', '<option value="" hidden>${s.cats.length')

# ── «Не міняти чек» — назва прапорця (текст «i» лишається)
rep('<span>Правильно — не міняти чек</span>', '<span>Не міняти чек</span>')
rep('aria-label="Що таке «Правильно — не міняти чек»"', 'aria-label="Що таке «Не міняти чек»"')
rep('<b>Правильно — не міняти чек</b>', '<b>Не міняти чек</b>')

# ── «i» Підказка — механіка
rep('Перед першою фразою фармацевт бачить ідеальний набір і скільки на ньому можна заробити. Для новачків і розбору складних випадків.',
    'Без підказки фармацевт бачить лише орієнтир у гривнях. З підказкою — ще й обидва набори до першої фрази.')

# ── В-108 · «i» джерела даних: Товари · Рекомендації · Характер
I = lambda tid, aria, head, body: (f'<button type="button" class="info" popovertarget="{tid}" aria-label="{aria}" aria-expanded="false">i</button>'
                                   f'</h3><div class="tip" id="{tid}" popover><b>{head}</b>{body}</div>')
rep('<h3><span class="ic">🧾</span>Товари</h3>',
    '<h3><span class="ic">🧾</span>Товари' + I('i-goods', 'Звідки товари', 'Товари',
      'Категорії й позиції — з Каталогу. Нова категорія — розділ «Каталог».'))
rep('<h3><span class="ic">⭐</span>Рекомендації</h3>',
    '<h3><span class="ic">⭐</span>Рекомендації' + I('i-recs', 'Звідки рекомендації', 'Рекомендації',
      'Лише позиції з категорій сценарію. ВТМ — ідеально, ЗФ — теж добре; орієнтир — за ВТМ.'))
rep('<label for="f-ch">Характер</label>',
    '<div class="lab"><label for="f-ch">Характер</label><button type="button" class="info" popovertarget="i-char" aria-label="Звідки характери" aria-expanded="false">i</button></div>'
    '<div class="tip" id="i-char" popover><b>Характер</b>З бібліотеки характерів, розділ «Промпти». Клієнт отримує опис, суддя — типову помилку.</div>')

# ── Б3 + В-105 + В-107 · прев'ю «До розмови» за рушієм (X97:1541–1554, :1973)
rep('.badges{display:flex;gap:6px;flex-wrap:wrap}\n', '')
rep('.badge.grp{background:var(--anc-yellow-25);color:var(--anc-text-2);max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
    '.badge.grp{display:inline-block;vertical-align:3px;margin-left:6px;background:var(--anc-yellow-25);color:var(--anc-text-2);max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}')
rep('.pv .hintbox{border:1px dashed var(--anc-positive);border-radius:10px;padding:8px 10px;display:grid;gap:6px;background:#fff}',
    '.pv .hintbox{border:1px dashed var(--anc-positive);border-radius:10px;padding:8px 10px;display:grid;gap:10px;background:#fff}\n'
    '.hset{display:grid;gap:4px}\n'
    '.hset-h{font-size:12px;color:var(--anc-gray)} .hset-h b{color:var(--vtm)} .hset.zf .hset-h b{color:var(--zf)}\n'
    '.pot{display:flex;justify-content:space-between;align-items:baseline;gap:8px;padding:8px 10px;border-radius:10px;background:var(--anc-positive-10)}\n'
    '.pot small{font-size:11.5px;color:var(--anc-gray)} .pot b{font-size:15px;color:var(--anc-positive)}')

a = t.index('function drawPreview(s){'); b = t.index('/* ── «i»: віконце біля кнопки')
assert t.count('function drawPreview(s){') == 1
t = t[:a] + r'''function drawPreview(s){
  /* v4.2 · Б3: лише те, що фармацевт бачить у рушії до розмови (X97:1541–1554).
     Орієнтир = potential() рушія: max(1, round(бонус ідеального − бонус замовлення)) (X97:1973).
     Набори — тільки з підказкою (В-107: ідеальний за правилом мережі + «теж добре»). */
  const ALT = RULE==='bv' ? 'bm' : 'bv', LAB = {bv:'ВТМ', bm:'ЗФ'}, CLS = {bv:'vtm', bm:'zf'};
  const ini=(s.who||'?').trim()[0]||'?';
  const row = (c, v) => `<div class="pos"><span class="wrap">${esc(ITEM[c]?.n||c)}</span><span class="v num">${v}</span></div>`;
  const pot = Math.max(1, Math.round(bonus(s[RULE]) - bonus(s.order)));
  const same = JSON.stringify([...s.bv].sort()) === JSON.stringify([...s.bm].sort());
  const hset = (k, head, tag) => { const d = bonus(s[k]) - bonus(s.order);
    return `<div class="hset ${CLS[k]}"><div class="hset-h"><b>${head}</b> · ${tag}</div>
      <div class="rows">${s[k].map(c=>row(c,'+'+money(ITEM[c]?.b))).join('') || '<span class="empty">Набір не задано</span>'}</div>
      <div class="sum"><span>до замовлення</span><b class="num">${d>=0?'+':''}${money(d)}</b></div></div>`; };
  $('#pv').innerHTML = `
    <h4 class="wrap">${esc(s.title||'Без назви')}<span class="badge grp" title="${esc(s.grp)}">${esc(s.grp)}</span></h4>
    <div class="who"><div class="ava">${esc(ini)}</div><div><b class="wrap">${esc(s.who)}</b><span class="wrap">${esc(s.character)}</span></div></div>
    <div class="mood wrap">${esc(s.mood)}</div>
    <div class="sit wrap">${esc(s.mode)}</div>
    <div class="bubble wrap">${esc(s.open)}</div>
    <div class="sec">Просить</div>
    <div class="rows">${s.order.map(c=>row(c, money(ITEM[c]?.p))).join('') || '<span class="empty">Нічого не називає — вільний вибір</span>'}</div>
    <div class="sec">Що тренуємо</div>
    <div class="goal wrap">${esc(s.goal)}</div>
    <div class="pot"><small>Орієнтир розмови</small><b class="num">${s.noSale ? '—' : 'до +'+pot.toLocaleString('uk-UA')+' ₴'}</b></div>
    ${s.hint && !s.noSale ? `<div class="hintbox"><div class="sec">Підказка</div>${same
        ? hset(RULE, 'ВТМ · ЗФ', 'обидва правила')
        : hset(RULE, LAB[RULE], 'ідеально') + hset(ALT, LAB[ALT], 'теж добре')}</div>` : ''}
    <div class="sec sep">Після розмови</div>
    <div class="goal">${s.noSale ? 'Розбір: правильна дія — не міняти' : 'Розбір — приріст з орієнтира'}</div>`;
}

''' + t[b:]

assert 'Відкриється в розборі' not in t
dst = here/'mock_a2v2_tpl_v4_2.html'
dst.write_text(t, encoding='utf-8')
print('шаблон:', dst.name, '· md5', hashlib.md5(t.encode()).hexdigest())
