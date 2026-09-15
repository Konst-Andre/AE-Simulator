#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x88_a7key_apply_v1.py — AE-Simulator · S70 · щабель 1, крок 1.1: ключ пункту «Система».

живе доки: пункт «Система» набору '6' несе ключ екрана 'settings'

Набір '6' ніс 'system', а двері й шість писарів стану ведуть у 'settings'
(:1076 :1097 :2890 :2995 :3102 :3569). V2.system не існує → пункт малювався
.stub, а живий екран не мав active у рейці. Вирок оператора S70 — варіант А:
міняємо ключ у наборі, писарів НЕ чіпаємо (П99: інваріант стану не рвемо;
smoke_ui_v1:256 чекає S.screen==='settings').
Мертвий 'system' у V2_CUR прибирається тим самим кроком.
⚠ :2193 {role:'system'} — роль повідомлення API, до рейки стосунку не має.

ІДЕМПОТЕНТНІСТЬ (П94): маркер — створений вузол ['settings','i-gear','Система'].
Використання: python3 x88_a7key_apply_v1.py <вхід.html> <вихід.html>
"""
import hashlib, sys
SRC, DST = sys.argv[1], sys.argv[2]
MARK = "['settings','i-gear','Система']"
EDITS = [
    ("['prompts','i-chat','Промпти'],   ['system','i-gear','Система']]",
     "['prompts','i-chat','Промпти'],   ['settings','i-gear','Система']]"),
    ("const V2_CUR = new Set(['dash','models','prompts','system','settings','escen','ascen','acatalog']);",
     "const V2_CUR = new Set(['dash','models','prompts','settings','escen','ascen','acatalog']);"),
]
API_ROLE = "{role:'system', content: buildSystem(sc)}"

src = open(SRC, encoding="utf-8").read()
md5 = lambda s: hashlib.md5(s.encode()).hexdigest()
if MARK in src:
    open(DST, "w", encoding="utf-8").write(src)
    print("· маркер X88 уже в файлі — 0 правок (ідемпотентно)")
    print(f"→ {DST}  md5 {md5(src)}"); sys.exit(0)
out = src
for old, new in EDITS:
    n = out.count(old)
    if n != 1:
        print(f"✗ якір знайдено {n} разів, очікував 1: {old[:60]}…"); sys.exit(1)
    out = out.replace(old, new, 1)
# самоперевірка звіряє вузли (П91)
if out.count(MARK) != 1:
    print("✗ самоперевірка: вузол набору не створено"); sys.exit(1)
if "'system'" in out.replace(API_ROLE, ""):
    print("✗ самоперевірка: ключ 'system' лишився поза роллю API"); sys.exit(1)
if out.count(API_ROLE) != 1:
    print("✗ самоперевірка: роль API зачеплено"); sys.exit(1)
open(DST, "w", encoding="utf-8").write(out)
print(f"· правок: {len(EDITS)}  ✓ «Система» → 'settings' · V2_CUR без мертвого 'system'")
print(f"→ {DST}  md5 {md5(out)}")
