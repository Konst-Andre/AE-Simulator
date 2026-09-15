# x25_2a_apply_v1.py · Х25.2а «БЕЙДЖ + БЕЗ НОМЕРА» (S48)
# живе доки: фінальний пуш (В-31); у рецепті дерева — ОСТАННІМ, після x25_apply_v2.py
# Вирок оператора S48: бейдж типу — у рядку назви (варіант А, compare AE_X25_2a_badge_compare_v1);
# номер замовлення не показується фармацевту ніде (список · картка · шапка E2 · пошук).
# Поле `no` у даних, pickShift, промпт клієнта (with_number), розбір, кураторські екрани — не чіпаються.
# П15: правки — названим списком [назва, було, стало], кожна рівно один збіг.
# Стани — по файлу окремо: «було» → застосувати · «стало» → без змін · змішано всередині файлу → падіння до запису.
import os, sys

JS = [  # index.html
 ('J1 список E1 · номер', "        el('span', {class:'scenario-no', text:s.no ? '#'+s.no : 'На місці'}),\n", ''),
 ('J2+J3 картка E1 · номер і бейдж',
  "      el('div', {class:'case-no', text:s.no ? '#'+s.no : 'Оформлення на місці'}),\n"
  "      el('div', {class:'detail-heading'}, [el('div', {}, [el('h2', {text:s.title}),\n"
  "        el('div', {class:'tags'}, [s.noSale || s.trap ? status(s) : el('span', {class:'v2-tag', text:s.grp})])])]),",
  "      el('div', {class:'detail-heading'}, [el('div', {}, [el('h2', {text:s.title}),\n"
  "        el('div', {class:'tags'}, [status(s)])])]),"),
 ('J4 пошук E1', "((s.no ? '#'+s.no : '') + ' ' + s.title + ' ' + s.who", "(s.title + ' ' + s.who"),
 ('J5 шапка E2', "el('h1', {}, [sc.title + ' ', el('span', {class:'tags', text:sc.no ? '#' + sc.no : 'На місці'})]),",
  "el('h1', {text:sc.title}),"),
]
CSS_ANCHOR = '/* ── /Х23.4 ── */\n</style>'
CSS = ('/* ── Х25.2а · бейдж у рядку назви + без номера (вирок оператора S48, compare А) ──\n'
       '   живе доки: макет не отримав це відхилення (тоді — у порт, П9/П13)\n'
       '   C1: номер з рядка списку прибрано (J1) — сітка 3 колонки → 2.\n'
       '   C2: назва inline, бейдж їде за останнім словом; display бейджа не задаємо — мобільне display:none лишається.\n'
       '   C3: у картці бейдж = status(s) (той самий, що в списку), розмір — як колишній .v2-tag (12 px). */\n'
       '.v2 .scenario-item { grid-template-columns:minmax(0,1fr) auto; }\n'
       '.v2 .scenario-detail .detail-heading h2 { display:inline; }\n'
       '.v2 .scenario-detail .detail-heading .tags { margin-left:12px; vertical-align:4px; }\n'
       '.v2 .scenario-detail .detail-heading .scenario-status { padding:4px 8px; border-radius:6px; font-size:12px; }\n'
       '/* ── /Х25.2а ── */\n')
SMOKE = [  # tools/smoke_ui_v1.js — міграція твердження (В-32) + інʼєкція, що мусить його звалити
 ('S1 твердження h1 = назва', "d.querySelector('.case-title h1').textContent.startsWith(S.sc.title));",
  "d.querySelector('.case-title h1').textContent===S.sc.title); /* Х25.2а: номера в шапці немає */"),
 ('S1 інʼєкція · номер повернувся в h1',
  "                    \"  learn(rung, model){\\n    return;\");\n}",
  "                    \"  learn(rung, model){\\n    return;\");\n"
  "  /* Восьма (Х25.2а): номер замовлення повертається в шапку E2 — падає рівно «заголовок сценарію — у h1». */\n"
  "  html=html.replace(\"el('h1', {text:sc.title}),\", \"el('h1', {text:sc.title + ' #0000'}),\");\n}"),
]

def state(txt, pairs, label):
    # пара «стало»: new рівно раз (вставка, де old ⊂ new, теж так судиться — П15); видалення: old 0 разів
    done=[(txt.count(n)==1) if n else (txt.count(o)==0) for _,o,n in pairs]
    todo=[txt.count(o)==1 and not (n and txt.count(n)) for _,o,n in pairs]
    if all(done): return 'new'
    if all(todo): return 'old'
    bad=[p[0] for p,d,t in zip(pairs,done,todo) if not (d or t)] or [p[0] for p,d in zip(pairs,done) if d]
    raise AssertionError(label+': змішаний стан або «було» не рівно раз: '+', '.join(bad))

def apply(txt, pairs):
    for name,o,n in pairs: txt=txt.replace(o,n,1)
    return txt

def main(root):
    fi=os.path.join(root,'index.html'); fs=os.path.join(root,'tools','smoke_ui_v1.js')
    h=open(fi,encoding='utf-8').read(); s=open(fs,encoding='utf-8').read()
    assert h.count('<style id="v2-css-own">')==1 and h.count(CSS_ANCHOR)==1, 'якір CSS не рівно раз'
    sh=state(h,JS,'index.html'); ss=state(s,SMOKE,'smoke_ui')
    cssin=h.count('/* ── Х25.2а ·')
    assert (sh=='new')==(cssin==1) and cssin in (0,1), 'CSS-блок Х25.2а не узгоджений з JS'
    # кожен файл — окремо: у рецепті від AE_WORK index уже «стало», а смоуки приходять з репо «було»
    if sh=='new' and ss=='new':
        print('x25_2a: вже застосовано, без змін · JS 0 · CSS 0 · смоук 0'); return
    if sh=='old':
        h=apply(h,JS); h=h.replace(CSS_ANCHOR, CSS+CSS_ANCHOR,1)
        for bad in ("class:'scenario-no'","class:'case-no'","'#'+s.no","'#' + sc.no","v2-tag', text:s.grp"):
            assert bad not in h, 'показ номера/старий бейдж лишився: '+bad
        assert h.count('/* ── Х25.2а ·')==1 and h.count('/* ── /Х25.2а ── */')==1
        assert "sc.no" in h and "withNumber" in h and "S.SCEN.filter(x=>x.no)" in h, 'логіку номера зачепило'
    assert h.count("el('h1', {text:sc.title}),")==1, 'ціль інʼєкції S1 не рівно раз (П25)'
    if ss=='old': s=apply(s,SMOKE)
    if sh=='old': open(fi,'w',encoding='utf-8').write(h)
    if ss=='old': open(fs,'w',encoding='utf-8').write(s)
    print('x25_2a: index %s · смоук %s' % ('застосовано (JS %d · CSS 1 блок)' % len(JS) if sh=='old' else 'без змін',
                                           'застосовано (%d)' % len(SMOKE) if ss=='old' else 'без змін'))

if __name__=='__main__': main(sys.argv[1] if len(sys.argv)>1 else '.')
