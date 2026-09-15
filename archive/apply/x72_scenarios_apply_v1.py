#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x72_scenarios_apply_v1.py — X72 «СЦЕНАРІЇ ЖИВІ»

Що робить (крок 1 черги S63 §5, вирок В-63 — реальні екрани замість старих):
  1. Заводить екран `scenarios` (E4 мокапу) під наш API: el() замість innerHTML,
     дані з S.SCEN, стан у S.e4, пагінація спільна з E6.
  2. Розв'язує колізію ключа: підпис «Сценарії» стоїть у ДВОХ наборах панелі,
     але екрани за ним різні — E4 (список для фармацевта) і A2 (правка для
     куратора). Кураторський ключ стає 'ascen' (пара до 'escen'), інакше
     кураторський пункт після цього ходу повів би Олю в звичайний режим.
     Пункт куратора при цьому лишається заглушкою — картинка не рухається
     (wsd 1.18).

Ідемпотентний: маркер X72-SCENARIOS. Повтор — «0 правок», exit 0, той самий md5.

Вхід/вихід — аргументами:
  python3 x72_scenarios_apply_v1.py <in.html> <out.html>
"""
import sys, hashlib, re

MARK = 'X72-SCENARIOS'

# ── А · кураторський ключ «Сценарії» → 'ascen' ──────────────────────────────
A_OLD = """  '6': [['dash','i-grid','Дашборд'],      ['scenarios','i-doc','Сценарії'],"""
A_NEW = """  '6': [['dash','i-grid','Дашборд'],      ['ascen','i-doc','Сценарії'],"""

# ── Б · 'ascen' — кураторський екран, тож у V2_CUR ──────────────────────────
B_OLD = """const V2_CUR = new Set(['dash','models','prompts','system','settings','escen']);"""
B_NEW = """/* X72: 'ascen' — кураторський «Сценарії» (правка, A2 мокапу). Ключ окремий від
   звичайного 'scenarios' (E4, список): підпис спільний, екрани різні. */
const V2_CUR = new Set(['dash','models','prompts','system','settings','escen','ascen']);"""

# ── В · екран E4 ────────────────────────────────────────────────────────────
C_ANCHOR = "V2.catalog = Catalog;\n"

C_BLOCK = r"""
/* ── v2 · E4 Сценарії — вітрина (X72-SCENARIOS) ──────────────────────
   Порт екрана E4 з мокапу mockup_X21_v1 (renderE4) під наш API: el()
   замість innerHTML, дані з S.SCEN, стан у S.e4.
   ⚠ ТІЛЬКИ ЧИТАННЯ, і рядок-посилання в розмову свідомо НЕ портовано:
   у мокапі `.row-link` веде в E2, а наш вихід із E2 жорстко йде в
   'picker' — двері були б однобічні (зайшов зі «Сценаріїв», вийшов у
   «Тренування»). Вхід у розмову з E4 — окремий крок черги разом із
   маршрутом повернення.
   Колонки — рівно ті поля, що в даних є: no (у 38 з 43 записів), title,
   who, grp. Номера немає — «На місці», як у мокапі.
   Пагінація і вікно сторінок — СПІЛЬНІ з E6 (E6_PAGE, pageWindow):
   другого механізму сторінок у продукті не заводимо.
   Лічильники в селекторі групи — як на E1/E6: фасетні, у межах пошуку.
   Шапка несе лише назву — Х27-П5, вирок оператора S62.
   живе доки: не портовано кураторський екран правки сценаріїв ('ascen'). */
const E4_COLS = [['no','Номер'], ['title','Назва'], ['who','Клієнт'], ['grp','Група']];
function Scenarios(){
  const st = S.e4 || (S.e4 = {term:'', grp:'', page:1});
  const all = () => S.SCEN || [];
  const byTerm = () => { const t = st.term.trim().toLowerCase();
    return all().filter(s => ((s.no ? s.no + ' ' : '') + s.title + ' ' + s.who).toLowerCase().includes(t)); };
  const rows = () => byTerm().filter(s => !st.grp || s.grp===st.grp);
  const redraw = () => fill();
  const search = el('input', {id:'e4-search', type:'search', placeholder:'Пошук сценарію…', value:st.term,
    oninput:e => { st.term = e.target.value; st.page = 1; redraw(); }});
  const grps = el('select', {id:'e4-group', 'aria-label':'Фільтр за групою',
    onchange:e => { st.grp = e.target.value; st.page = 1; redraw(); }});
  const head = el('thead', {id:'e4-head'}, [el('tr', {}, E4_COLS.map(([, label]) => el('th', {text:label})))]);
  const body = el('tbody', {id:'e4-body'});
  const foot = el('footer', {class:'table-footer', id:'e4-foot'});
  const pageBtn = (value, label, active, disabled) => el('button', {type:'button', class:active ? 'active' : '',
    'data-e4-page':value, disabled:disabled || null, onclick:() => { st.page = value; redraw(); }}, [String(label)]);
  function fill(){
    const list = rows(), pages = Math.max(1, Math.ceil(list.length / E6_PAGE));
    st.page = Math.min(Math.max(1, st.page), pages);
    const from = (st.page - 1) * E6_PAGE, part = list.slice(from, from + E6_PAGE), base = byTerm();
    grps.replaceChildren(...[['', 'Усі групи'], ...[...new Set(all().map(s => s.grp))].sort((a, b) => a.localeCompare(b, 'uk')).map(g => [g, g])]
      .map(([value, label]) => el('option', {value:value,
        text:label + ' (' + (value ? base.filter(s => s.grp===value).length : base.length) + ')'})));
    grps.value = st.grp;
    body.replaceChildren(...(part.length ? part.map(s => el('tr', {'data-e4-row':String(s.id)}, E4_COLS.map(([f]) => el('td', {'data-e4-cell':f},
        f==='no' ? [s.no ? '№ ' + s.no : el('span', {class:'e4-noplace', text:'На місці'})]
      : f==='title' ? [el('b', {text:s.title})]
      : [String(s[f] || '—')]))))
      : [el('tr', {}, [el('td', {colspan:String(E4_COLS.length),
          style:'padding:22px;color:var(--anc-gray);text-align:center', text:'Сценаріїв не знайдено'})])]));
    foot.replaceChildren(
      el('span', {text:list.length ? 'Показано ' + (from + 1) + '–' + (from + part.length) + ' з ' + list.length : 'Нічого не знайдено'}),
      el('div', {class:'pagination'}, [pageBtn(st.page - 1, '‹', false, st.page===1),
        ...pageWindow(st.page, pages).map(t => t==='…' ? el('span', {class:'page-gap', text:'…'}) : pageBtn(t, t, t===st.page, false)),
        pageBtn(st.page + 1, '›', false, st.page===pages)]));
  }
  fill();
  return el('div', {class:'page'}, [
    el('header', {class:'page-title'}, [el('div', {}, [el('h1', {text:'Сценарії'})])]),
    el('section', {class:'wide-table-card'}, [
      el('div', {class:'search-row'}, [el('label', {class:'search'}, [icon('i-search'), search]), grps]),
      el('table', {class:'regular-table'}, [head, body]),
      foot])]);
}
V2.scenarios = Scenarios;
/* ── /X72 ── */
"""

# ── Г · стан екрана в S ─────────────────────────────────────────────────────
D_OLD = """  efilter:'all', edraft:{}, escen:null,"""
D_NEW = """  efilter:'all', edraft:{}, escen:null,

  /* X72 · стан вітрини E4 «Сценарії»: пошук, група, сторінка. Живе в S, як
     S.e6 — повернення на екран не скидає фільтри (той самий урок fold/efilter). */
  e4:null,"""

# ── Ґ · CSS: підпис «На місці» замість номера ───────────────────────────────
E_OLD = """.v2 .pagination .page-gap { padding:0 1px; color:var(--anc-gray); }"""
E_NEW = """.v2 .pagination .page-gap { padding:0 1px; color:var(--anc-gray); }
/* X72 · E4: сценарій без номера — не порожня клітинка, а названа причина */
.v2 .e4-noplace { color:var(--anc-gray); }"""


def main():
    if len(sys.argv) != 3:
        print('вжиток: x72_scenarios_apply_v1.py <in.html> <out.html>'); return 2
    src, dst = sys.argv[1], sys.argv[2]
    html = open(src, encoding='utf-8').read()
    before = len(html.encode('utf-8'))

    if MARK in html:
        open(dst, 'w', encoding='utf-8').write(html)
        print('0 правок — маркер %s уже в файлі (ідемпотентність)' % MARK)
        print('md5 %s · %d б' % (hashlib.md5(html.encode('utf-8')).hexdigest(), before))
        return 0

    edits = [('А · ключ кураторського пункту → ascen', A_OLD, A_NEW),
             ('Б · ascen у V2_CUR', B_OLD, B_NEW),
             ('Г · S.e4', D_OLD, D_NEW),
             ('Ґ · CSS .e4-noplace', E_OLD, E_NEW)]
    for name, old, new in edits:
        n = html.count(old)
        if n != 1:
            print('✗ %s: якір знайдено %d разів, чекали 1' % (name, n)); return 1
        html = html.replace(old, new)
        print('✓ %s' % name)

    n = html.count(C_ANCHOR)
    if n != 1:
        print('✗ В · якір V2.catalog знайдено %d разів, чекали 1' % n); return 1
    html = html.replace(C_ANCHOR, C_ANCHOR + C_BLOCK)
    print('✓ В · екран Scenarios()')

    open(dst, 'w', encoding='utf-8').write(html)
    after = len(html.encode('utf-8'))
    print('5 правок · %+d б · md5 %s' % (after - before, hashlib.md5(html.encode('utf-8')).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
