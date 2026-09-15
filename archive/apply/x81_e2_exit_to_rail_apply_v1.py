#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x81_e2_exit_to_rail_apply_v1.py — щабель «ШАПКА Е2», КРОК 3 (останній).

живе доки: крок 3 щабля «ШАПКА Е2» не влитий у наступний ланцюг генераторів

ЩО РОБИТЬ. Виносить кнопку виходу з шапки E2 у ліву панель.

ЧОМУ ПОТРІБЕН КАНАЛ. `sidebar(active)` не знає контексту розмови — вихід
живе в `Talk()`. Дім каналу названо (12.11): модульна змінна `V2_EXIT`
поруч із `V2_RAIL`. `Talk()` її виставляє, `normalShell()` — гасить одразу
після побудови дерева, тож вона живе рівно один рендер і на E3 не протікає.

ПІДПИС НЕ ВИГАДАНО. Коротка форма «До списку» вже живе в продукті
(`exitLabel`, гілка `!S.shift`). Для входу з E3 заведено пару «До підсумку» —
повна форма «Повернутися до підсумку» лишається підказкою в рейці 72.

⚠ У порожню панель E2 кладеться ТІЛЬКИ вихід (черга §2, щабель 1).

ІДЕМПОТЕНТНІСТЬ: повтор — «0 правок», exit 0, той самий md5.
"""
import sys, hashlib, re, pathlib

SRC = sys.argv[1] if len(sys.argv) > 1 else 'AE_WORK_index_X27Q6_v1.html'
DST = sys.argv[2] if len(sys.argv) > 2 else 'AE_WORK_index_X27Q7_v1.html'

# --- 1 · дім каналу ---
DECL_OLD = "let V2_RAIL = false;\n"
DECL_NEW = ("let V2_RAIL = false;\n"
            "/* X81 · дім каналу виходу E2 (12.11): Talk() виставляє, normalShell() гасить\n"
            "   одразу після побудови дерева — змінна живе рівно один рендер, на E3 не тече. */\n"
            "let V2_EXIT = null;\n")

# --- 2 · вузол у панелі ---
SIDE_OLD = """    /* Х23.3 · Х24.3: на E2 (game) і E3 (result) панель несе лише бренд, як макет; вихід — у шапці */
    bare ? null : el('nav',{class:'side-links','aria-label':'Звичайний режим'},links),"""
SIDE_NEW = """    /* Х23.3 · Х24.3 → X81: на E2 (game) панель несе бренд і ВИХІД; на E3 — лише бренд. */
    bare ? null : el('nav',{class:'side-links','aria-label':'Звичайний режим'},links),
    /* X81 · вихід з розмови переїхав сюди з шапки E2. У рейці 72 підпис не видно —
       повна форма живе в data-tip, як у решти пунктів (X75-RAIL). */
    (bare && V2_EXIT) ? el('nav',{class:'side-links','aria-label':'Вихід з розмови'},[
      el('button',{type:'button', class:'side-link', 'data-e2-exit':'rail',
        'data-tip':V2_EXIT.tip, onclick:V2_EXIT.go},
        [icon('i-arrow'), el('span',{class:'lbl', text:V2_EXIT.label})])]) : null,"""

# --- 3 · гасіння каналу ---
SHELL_OLD = """  return el('div',{class:'v2','data-shell':'bare','data-mode':V2_RAIL?'rail':'expanded'},
    [el('div',{class:'shell'},[sidebar(active), el('main',{},[body])])]);"""
SHELL_NEW = """  const tree = el('div',{class:'v2','data-shell':'bare','data-mode':V2_RAIL?'rail':'expanded'},
    [el('div',{class:'shell'},[sidebar(active), el('main',{},[body])])]);
  V2_EXIT = null;  /* X81: канал згорає в тому ж рендері, що й запалився */
  return tree;"""

# --- 4 · шапка: кнопки більше немає, натомість канал ---
HEAD_OLD = """  const backGo = () => { if(fromE3){ S.screen = 'result'; render(); return; }
    S.shift = null; S.screen = 'picker'; render(); };
  const appbar = el('header', {class:'appbar'}, [
    el('button', {type:'button', class:'v2-back', 'aria-label':backLabel,
      onclick:backGo}, [icon('i-arrow'), el('span', {text:backLabel})]),
    el('div', {class:'case-title'}, ["""
HEAD_NEW = """  const backGo = () => { if(fromE3){ S.screen = 'result'; render(); return; }
    S.shift = null; S.screen = 'picker'; render(); };
  /* X81: вихід переїхав у панель. Коротка форма — пара до `exitLabel`; повна
     лишається підказкою. П87: кнопки в шапці немає — немає й aria-label при ній. */
  V2_EXIT = { label: fromE3 ? 'До підсумку' : 'До списку', tip: backLabel, go: backGo };
  const appbar = el('header', {class:'appbar'}, [
    el('div', {class:'case-title'}, ["""


def main():
    src = pathlib.Path(SRC)
    if not src.exists():
        print(f"✗ немає вхідного файлу: {SRC}")
        return 2
    orig = src.read_text(encoding='utf-8')
    txt, edits = orig, 0

    # guard — унікальний вузол, що з'являється ЛИШЕ після правки (П91: маркер
    # ідемпотентності мусить бути вузлом правки, а не її якорем: DECL_OLD
    # цілком міститься в DECL_NEW, тож «old ще тут» тут нічого не доводить).
    for old, new, guard, name in ((DECL_OLD, DECL_NEW, 'let V2_EXIT = null;', 'дім каналу V2_EXIT'),
                           (SIDE_OLD, SIDE_NEW, "'data-e2-exit':'rail'", 'вузол виходу в панелі'),
                           (SHELL_OLD, SHELL_NEW, 'V2_EXIT = null;  /* X81', 'гасіння каналу в normalShell'),
                           (HEAD_OLD, HEAD_NEW, "V2_EXIT = { label: fromE3", 'зняття кнопки з шапки')):
        if guard in txt:
            continue                      # вже застосовано
        if old not in txt:
            print(f"✗ якір не знайдено: {name}")
            return 3
        if txt.count(old) != 1:
            print(f"✗ якір `{name}` — {txt.count(old)} входжень, очікував 1")
            return 3
        txt = txt.replace(old, new, 1); edits += 1

    out = pathlib.Path(DST)
    out.write_text(txt, encoding='utf-8')

    # --- самоперевірка: ВУЗЛИ, а не присутність слів (П91) ---
    chk = out.read_text(encoding='utf-8')
    ok = True

    def chk_node(cond, msg):
        nonlocal ok
        print(f"{'✓' if cond else '✗'} {msg}")
        ok &= bool(cond)

    chk_node(chk.count("let V2_EXIT = null;") == 1, "дім `V2_EXIT` оголошено рівно раз")
    chk_node(chk.count("V2_EXIT = { label: fromE3 ? 'До підсумку' : 'До списку'") == 1,
             "Talk() виставляє канал — 1 точка запалювання")
    chk_node(chk.count("V2_EXIT = null;  /* X81") == 1, "normalShell() гасить канал — 1 точка гасіння")
    chk_node(chk.count("'data-e2-exit':'rail'") == 1, "вузол виходу в панелі — 1")
    chk_node(len(re.findall(r"class:'v2-back'", chk)) == 0, "кнопки `.v2-back` в розмітці більше немає")
    chk_node("'aria-label':backLabel" not in chk, "П87: aria-label кнопки знято разом із кнопкою")
    chk_node(chk.count("const backLabel = fromE3") == 1, "`backLabel` живий — став підказкою, не сиротою")
    chk_node(chk.count("aria-label':'Вихід з розмови'") == 1, "панель виходу має доступне ім'я")

    # у панель E2 не заїхало нічого, крім виходу
    seg = chk[chk.find("function sidebar(active)"):chk.find("const RAIL_CAP")]
    chk_node(seg.count("bare && V2_EXIT") == 1, "у панель E2 кладеться РІВНО один вузол (черга §2)")
    chk_node(seg.count("bare ? null : door(active)") == 1, "двері лишились під тією ж умовою")

    # кроки 1 і 2 не з'їхали
    chk_node(chk.count(".v2 .v2-tag + .v2-tag { margin-left:6px; }") == 1, "крок 2 на місці")
    chk_node(chk.count(".v2 .case-title { min-width:0; flex:1; }") == 1, "крок 1 на місці")

    print(f"\nправок: {edits} · дельта байтів: {len(chk.encode()) - len(orig.encode()):+d}")
    print(f"{DST} · md5 {hashlib.md5(out.read_bytes()).hexdigest()}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
