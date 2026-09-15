#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x62_apply_v1.py  ·  AE-Simulator  ·  S61
AE_X27_SIDEBAR_v17.html  ->  AE_X27_SIDEBAR_v18.html

Одна дія, нульова оптика: добити адресу дому канону важелів.
x60_apply_v1.py виправив §13.3 -> §14 ЛИШЕ в шапці блоку Л-РЕГІСТР (:1559-1564).
Греп S61 показав, що стара адреса вціліла ще у двох коментарях:
  :1488  «доки не стане ЛОКом і не ляже в SPEC §13.3»
  :1687  «LEVER_LOCK + SPEC §13.3»
Це той самий дефект П73 у тому самому файлі — коментар як намір, а не стан.

НЕ чіпає :1561 — там §13.3 згадано ПО ДІЛУ (історія виправлення).
Правка суто коментарна: жодного селектора, числа чи важеля (wsd 1.18 — оптика
не може зрушити за побудовою).
"""
import sys, os, hashlib

SRC = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project/AE_X27_SIDEBAR_v17.html"
DST = sys.argv[2] if len(sys.argv) > 2 else "/mnt/user-data/outputs/AE_X27_SIDEBAR_v18.html"

PATCHES = [
    ("не їде, доки не стане ЛОКом і не ляже в SPEC §13.3.",
     "не їде, доки не стане ЛОКом і не ляже в SPEC §14."),
    ("LEVER_LOCK + SPEC §13.3, і регістр далі чесно показує",
     "LEVER_LOCK + SPEC §14, і регістр далі чесно показує"),
]
KEEP = "До v15 тут стояв SPEC §13.3"   # історія — не чіпати


def main():
    if not os.path.exists(SRC):
        print("✗ немає вхідного файла: " + SRC)
        return 2
    with open(SRC, encoding="utf-8") as f:
        txt = f.read()
    print("вхід : %s  md5 %s" % (os.path.basename(SRC),
                                 hashlib.md5(txt.encode("utf-8")).hexdigest()))

    todo, done = [], []
    for old, new in PATCHES:
        n_old, n_new = txt.count(old), txt.count(new)
        if n_new and not n_old:
            done.append(new[:38] + "…")
            continue
        if n_old != 1:
            print("✗ якір не унікальний (%d): %s" % (n_old, old[:50]))
            return 3
        txt = txt.replace(old, new, 1)
        todo.append(new[:38] + "…")

    if KEEP not in txt:
        print("✗ історичне згадування §13.3 (:1561) зникло — правка завелика")
        return 4

    if not todo:
        print("= вже пропатчено — правок нема")
        if os.path.exists(DST):
            with open(DST, encoding="utf-8") as f:
                print("вихід: md5 %s" % hashlib.md5(f.read().encode("utf-8")).hexdigest())
        return 0

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    with open(DST, "w", encoding="utf-8") as f:
        f.write(txt)
    print("✓ виправлено адрес: %d" % len(todo))
    for t in todo:
        print("   · " + t)
    print("вихід: %s  md5 %s" % (os.path.basename(DST),
                                 hashlib.md5(txt.encode("utf-8")).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
