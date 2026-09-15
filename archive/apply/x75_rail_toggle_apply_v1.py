#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x75_rail_toggle_apply_v1.py — X75 «ДРУГИЙ СТАН РЕЙКИ»

Дефект, названий оператором у S65 і підтверджений грепом:
панель продукту має РІВНО ОДИН стан — розгорнутий 220 px. Згорнутий стан
(рейка 72, підпис схований) живий у стенді AE_X27_SIDEBAR_v19 і в продукт
НЕ перенесений. Це не борг анімації: сам стенд називає це своїм боргом —
:1566 «У ПРОДУКТІ дому нема: логотип там панель не перемикає (борг Х27
кроку 3)». Тобто порт панелі Х27-П2 був зупинений на півдорозі.

⚠ Це НЕ анімація і не рух Х27-К3. Тут заводиться ДРУГИЙ СТАН і важіль до
нього. Перехід — миттєвий, transition свідомо не ставимо: рух судиться
окремим щаблем черги, і змішувати два вироки в одному кадрі не можна.

Порт дослівний зі стенда (П9/П13), джерела названі по рядках:
  :237-238 --side-w 220 / 72      :239-240 бренд у рейці
  :241-242 пункт і .lbl           :243 · :251 двері й .lbl дверей
  :408 логотип — <button>         :412 .brand-text
  :1224 стан логотипа             :1348-1349 підказка вмикається в рейці
  :1406 перемикач expanded↔rail

ВІДСТУП ВІД СТЕНДА, СВІДОМИЙ (назване, не приховане):
правила рейки загорнуті в @media (min-width:981px). У стенді медіа немає —
він тільки ПК. У продукті ≤980 панель — горизонтальна смуга (:551-559),
і незагорнуте `.lbl{display:none}` знесло б підписи в смузі, до якої
важіль узагалі не дотягується (.brand там display:none).

Ідемпотентний: маркер X75-RAIL. Повтор — «0 правок», exit 0, той самий md5.
Вхід : AE_WORK_index_X27P9_v1.html   Вихід: AE_WORK_index_X27Q1_v1.html
"""
import sys, hashlib

MARK = 'X75-RAIL'

# ── А · ширина панелі стає важелем (стенд :237-238) ────────────────────────
A_OLD = """.v2 .shell { display:grid; grid-template-columns:220px minmax(0,1fr); height:100dvh; min-height:0; overflow:hidden; }"""
A_NEW = """/* X75-RAIL: ширина панелі — важіль, а не зашите число (стенд :237). Дефолт 220
   той самий, що стояв тут раніше: перехід на змінну картинку не рухає (1.18). */
.v2 { --side-w:220px; }
.v2 .shell { display:grid; grid-template-columns:var(--side-w) minmax(0,1fr); height:100dvh; min-height:0; overflow:hidden; }"""

# ── Б · стан «рейка» (стенд :238-243 · :251) ───────────────────────────────
B_OLD = """/* заглушка: пункт стоїть і підписаний, але екрана ще нема */
.v2 .side-link.stub { color:var(--anc-gray-light); cursor:default; }"""
B_NEW = """/* заглушка: пункт стоїть і підписаний, але екрана ще нема */
.v2 .side-link.stub { color:var(--anc-gray-light); cursor:default; }
/* ── X75-RAIL · ДРУГИЙ СТАН ПАНЕЛІ (порт зі стенда v19 :238-243 · :251) ──
   живе доки: рейка не дістала власного вироку device (тоді числа — в ЛОК)
   ⚠ @media — відступ від стенда: стенд тільки ПК, а тут ≤980 панель уже
   горизонтальна смуга, і схований .lbl знищив би в ній підписи.
   ⚠ transition НЕМА свідомо: плавність — окремий щабель черги (рух Х27-К3). */
@media (min-width:981px) {
  .v2[data-mode="rail"] { --side-w:72px; }
  .v2[data-mode="rail"] .brand { padding:0 0 21px; justify-content:center; }
  .v2[data-mode="rail"] .brand .brand-text { display:none; }
  .v2[data-mode="rail"] .side-link { gap:0; padding:0; justify-content:center;
      border-left-width:0; border-radius:8px; }
  .v2[data-mode="rail"] .side-link .lbl { display:none; }
  .v2[data-mode="rail"] .side-bottom button { justify-content:center; gap:0; padding:9px 0; }
  .v2[data-mode="rail"] .side-bottom .lbl { display:none; }
}"""

# ── В · важіль стану + його дім (стенд :1224 · :1406, 12.11) ───────────────
C_OLD = """function sidebar(active){"""
C_NEW = """/* ── X75-RAIL · дім важеля стану панелі (12.11) ────────────────────────
   Пам'ять модуля, як DOOR: стан панелі не лягає ні в S, ні в localStorage —
   це поза́ даними сесії. Атрибут data-mode на .v2 ставить normalShell(),
   рівно як data-shell (стенд :1219).
   Важіль — САМ ЛОГОТИП (стенд :408 · :1406), нового елемента не додаємо:
   стенд уже оголосив логотип кнопкою, а продукт лишив його простим блоком —
   це і є той борг, що закривається тут.
   ⚠ Кутових дужок у цьому коментарі нема свідомо: H2 рахує імена тегів
   текстом і дав би хибне ⚠ на балансі через сам коментар (12.12). */
let V2_RAIL = false;
function railToggle(){ V2_RAIL = !V2_RAIL; render(); }
function sidebar(active){"""

# ── Г · логотип стає кнопкою, текст бренду дістає ім'я (стенд :408 · :412) ─
D_OLD = """  return el('aside',{class:'sidebar'},[
    el('div',{class:'brand'},[
      el('div',{class:'brand-mark'},[icon('i-anc')]),
      el('div',{},[el('b',{text:'Тренажер'}), el('small',{text:'Навчання фармацевтів'})])]),"""
D_NEW = """  return el('aside',{class:'sidebar'},[
    el('div',{class:'brand'},[
      /* X75-RAIL: логотип — важіль стану панелі (стенд :408). type=button, бо
         в <aside> без type кнопка не сабмітить, але лишається неоднозначною. */
      el('button',{type:'button', class:'brand-mark', onclick:railToggle,
        'aria-expanded':String(!V2_RAIL),
        'aria-label':V2_RAIL ? 'Розгорнути панель' : 'Згорнути панель'},[icon('i-anc')]),
      el('div',{class:'brand-text'},[el('b',{text:'Тренажер'}), el('small',{text:'Навчання фармацевтів'})])]),"""

# ── Д · підпис живого пункту переїжджає в підказку, коли його не видно ─────
E_OLD = """    if(live){ a.onclick = ()=>{ S.screen = screen; render(); }; }
    else { a['aria-disabled'] = 'true';"""
E_NEW = """    if(live){ a.onclick = ()=>{ S.screen = screen; render(); };
              /* X75-RAIL: у рейці підпису не видно — він мусить жити в підказці
                 (стенд :1344). У розгорнутій панелі showTip() її не покаже. */
              a['data-tip'] = label; }
    else { a['aria-disabled'] = 'true';"""

# ── Е · підказка вмикається в рейці для ВСІХ пунктів (стенд :1348-1349) ────
F_OLD = """  if(!txt || !node.classList.contains('stub')) return;"""
F_NEW = """  /* X75-RAIL (стенд :1349): у розгорнутій панелі підказку має лише заглушка —
     підпис і так видно. У рейці підпису немає в жодного пункту, тож підказку
     дістають усі. Умова читається зі стану, не з прапорця на вузлі. */
  if(!txt) return;
  if(!V2_RAIL && !node.classList.contains('stub')) return;"""

# ── Ж · стан їде атрибутом на корінь (стенд :1219) ─────────────────────────
G_OLD = """  return el('div',{class:'v2','data-shell':'bare'},[el('div',{class:'shell'},[sidebar(active), el('main',{},[body])])]);"""
G_NEW = """  return el('div',{class:'v2','data-shell':'bare','data-mode':V2_RAIL?'rail':'expanded'},
    [el('div',{class:'shell'},[sidebar(active), el('main',{},[body])])]);"""

EDITS = [('А · --side-w важелем', A_OLD, A_NEW),
         ('Б · CSS стану rail',   B_OLD, B_NEW),
         ('В · дім важеля',       C_OLD, C_NEW),
         ('Г · логотип-кнопка',   D_OLD, D_NEW),
         ('Д · підказка живих',   E_OLD, E_NEW),
         ('Е · умова showTip',    F_OLD, F_NEW),
         ('Ж · data-mode',        G_OLD, G_NEW)]


def main():
    if len(sys.argv) != 3:
        print('вжиток: x75_rail_toggle_apply_v1.py <in.html> <out.html>')
        return 2

    html = open(sys.argv[1], encoding='utf-8').read()
    before = len(html.encode('utf-8'))

    if MARK in html:
        open(sys.argv[2], 'w', encoding='utf-8').write(html)
        print('0 правок — маркер %s уже у файлі (ідемпотентність)' % MARK)
        print('md5 %s · %d б' % (hashlib.md5(html.encode('utf-8')).hexdigest(), before))
        return 0

    if 'X74-ACATALOG' not in html:
        print('✗ вхід не той: немає маркера X74-ACATALOG (чекаю X27P9)')
        return 1

    for name, old, new in EDITS:
        n = html.count(old)
        if n != 1:
            print('✗ якір «%s» знайдено %d разів, очікував 1' % (name, n))
            return 1
        html = html.replace(old, new, 1)
        print('✓ %s' % name)

    # самоперевірка: важіль, стан і споживач кожного імені на місці
    checks = [("let V2_RAIL = false;",            'дім важеля'),
              ("onclick:railToggle",              'логотип кличе важіль'),
              ('class:\'brand-text\'',            'brand-text має споживача в CSS'),
              ('.v2[data-mode="rail"] --',        None)]
    for needle, why in checks[:3]:
        if needle not in html:
            print('✗ самоперевірка: %s' % why); return 1
    # ⚠ рахуємо ІМ'Я без крапки: у CSS воно «.brand-text», у розмітці
    # «class:'brand-text'». Перша редакція шукала «.brand-text» і давала
    # хибний ✗ на коректному результаті (wsd 1.9, вісь 2).
    if html.count('brand-text') < 2:
        print('✗ самоперевірка: brand-text названий, але без CSS-споживача (П87)'); return 1
    # ⚠ другий хибний ✗ першої редакції: split('normalShell')[2] — це НЕ тіло
    # функції, ім'я трапляється кілька разів. Звіряємо сам рядок, не позицію.
    if "'data-mode':V2_RAIL?'rail':'expanded'" not in html:
        print('✗ самоперевірка: data-mode не ставиться на корінь'); return 1

    after = len(html.encode('utf-8'))
    open(sys.argv[2], 'w', encoding='utf-8').write(html)
    print('%d правок · %+d б' % (len(EDITS), after - before))
    print('md5 %s · %d б' % (hashlib.md5(html.encode('utf-8')).hexdigest(), after))
    return 0


if __name__ == '__main__':
    sys.exit(main())
