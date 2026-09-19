#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# живе доки: шаблон v4.4 не замінено наступною версією
# v44_apply_v1.py — tpl v4.3 (11a072ca) -> tpl v4.4
# S79 · В-112 (алфавіт груп) · В-113 (порожня група переживає «Опублікувати») · рядок номера лише ⚠
import hashlib, sys, pathlib

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "mock_a2v2_tpl_v4_3.html")
DST = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "mock_a2v2_tpl_v4_4.html")
BASE_MD5 = "11a072cadb64ea13dc158f8aa188b632"

t = SRC.read_text(encoding="utf-8")
h = hashlib.md5(t.encode("utf-8")).hexdigest()
assert h == BASE_MD5, "base md5 не той: %s != %s" % (h, BASE_MD5)

def one(old, new, tag):
    global t
    n = t.count(old)
    assert n == 1, "%s: входжень %d, треба 1" % (tag, n)
    t = t.replace(old, new)
    print("  ✓", tag)

# --- 1. Рядок номера: лише ⚠ (В-101/В-103 — номер живе у фразі, підтверджувати нічого) ---
one(
 """  $('#m-no').innerHTML = (s.no
      ? `<span>Номер замовлення з фрази: <b>${s.no}</b> · інтернет-замовлення</span>`
      : `<span>Номера у фразі немає — оформлення на касі · у «Зміну» не потрапляє, лише окреме тренування</span>`)""",
 """  /* S79 · рядок номера — лише ⚠: підтвердження того, що Оля щойно написала, знято;
     лишається наслідок (сценарій не потрапляє у «Зміну») і два справжні попередження */
  $('#m-no').innerHTML = (s.no
      ? ``
      : `<span class="w">⚠ Номера у фразі немає — оформлення на касі · у «Зміну» не потрапляє, лише окреме тренування</span>`)""",
 "1 · рядок номера лише ⚠")

# --- 1b. Порожній рядок номера не займає місця ---
one(
 ".no-line .w{color:var(--warn)}",
 ".no-line .w{color:var(--warn)}\n.no-line:empty{display:none}",
 "1b · .no-line:empty")

# --- 2. В-112 · порядок груп за алфавітом (uk), скрізь ---
one(
 "for (const x of st.extraGroups) if(!g.includes(x)) g.push(x); return g; };",
 "for (const x of st.extraGroups) if(!g.includes(x)) g.push(x);\n  /* В-112 · порядок груп — за абеткою скрізь; локаль uk, інакше Є та І їдуть у хвіст */\n  return g.sort((a,b)=>a.localeCompare(b,'uk')); };",
 "2 · В-112 алфавіт груп")

# --- 3. В-113 · порожня група переживає «Опублікувати» ---
one(
 "    st._keepEmpty=[]; st.extraGroups=[]; drawEditor();",
 "    /* В-113 · порожня група переживає «Опублікувати»: тека, створена в діалозі, живе,\n       доки Оля не видалить її там само. Скидання _keepEmpty/extraGroups тут прибрано. */\n    drawEditor();",
 "3 · В-113 порожня група живе")

DST.write_text(t, encoding="utf-8")
print("вихід:", DST.name, "· md5", hashlib.md5(t.encode("utf-8")).hexdigest())
