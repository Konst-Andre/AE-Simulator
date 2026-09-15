#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x85_chat_bg_neutral_apply_v1.py — AE-Simulator · S68 · фон розмови: A → C.

живе доки: фон .v2 .messages = нейтральний #1C1E240A

Вирок оператора на ЖИВОМУ екрані скасував вибір зі стенда: --anc-plate #FFFCEC
в повній композиції виявився надто теплим і зливався з жовтими елементами
(картка завдання, чип). Беремо запасний варіант C — нейтральне затемнення 4%
з родини #1C1E24, уже канонізованої в hover (Л-05). Кремова температура
сторінки лишається, зона розмови від неї відходить.
⚠ Бульбашка клієнта лишається --anc-border #E7E7E7: на #1C1E240A (~#F7F6EF)
вона не зливається. Стенд це показував; якщо на живому екрані інакше —
наступний крок переводить її на --isl-surface з рамкою.

ІДЕМПОТЕНТНІСТЬ (П94): маркер — вузол, що створюється: 'background:#1C1E240A;'.
"""
import hashlib, sys
SRC, DST = "AE_WORK_index_X27R1_v1.html", "AE_WORK_index_X27R2_v1.html"
MARK = "background:#1C1E240A;"
OLD = ".v2 .messages { flex:1; padding:25px 20px 16px; overflow:auto; background:var(--anc-plate); }"
NEW = ".v2 .messages { flex:1; padding:25px 20px 16px; overflow:auto; background:#1C1E240A; }"

src = open(SRC, encoding="utf-8").read()
if MARK in src:
    open(DST, "w", encoding="utf-8").write(src)
    print("· маркер X85 уже в файлі — 0 правок (ідемпотентно)")
    print(f"→ {DST}  md5 {hashlib.md5(src.encode()).hexdigest()}"); sys.exit(0)
if src.count(OLD) != 1:
    print(f"✗ якір знайдено {src.count(OLD)} разів, очікував 1"); sys.exit(1)
out = src.replace(OLD, NEW, 1)
if "var(--anc-plate)" in out.split("/* X84")[1][:600]:
    print("✗ самоперевірка: плита лишилась у вузлі розмови"); sys.exit(1)
open(DST, "w", encoding="utf-8").write(out)
print("· правок: 1  ✓ фон розмови = нейтральний 4%")
print(f"→ {DST}  md5 {hashlib.md5(out.encode()).hexdigest()}")
