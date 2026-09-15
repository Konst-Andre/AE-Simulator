#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x64_passport_fix_v1.py · AE-Simulator · S61
AE_X27_SIDEBAR_v18.html -> AE_X27_SIDEBAR_v19.html

ДЕФЕКТ. У measure() :1449 `sd = q('.sidebar')`, а q() всередині measure
повертає DOMRect (нижче вживається sd.left / sd.width). На :1475 рядок
«верх рейки» викликає sd.getBoundingClientRect() — у DOMRect такого методу
немає. TypeError летить при КОЖНОМУ завантаженні стенда, вбиваючи весь
паспорт: рядок будується однією конкатенацією, тому не друкується нічого.

Гейт H1 (`node --check`) це не ловить за побудовою: синтаксис валідний,
помилка рантаймова. Заміряно Chromium, pageerror при старті v18.

ФІКС. sd.getBoundingClientRect().top -> sd.top.
Оптика не рухається (wsd 1.18): паспорт — текст, не верстка. Жодного
селектора, числа чи важеля не змінено.
"""
import sys, os, hashlib

SRC = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/AE_X27_SIDEBAR_v18.html"
DST = sys.argv[2] if len(sys.argv) > 2 else "/mnt/user-data/outputs/AE_X27_SIDEBAR_v19.html"

OLD = "Math.round(sd.getBoundingClientRect().top-V2.querySelector('.shell').getBoundingClientRect().top)"
NEW = "Math.round(sd.top-V2.querySelector('.shell').getBoundingClientRect().top)"

GUARD = "var ic=q('.side-link svg'), sd=q('.sidebar');"   # доказ, що sd — rect


def main():
    if not os.path.exists(SRC):
        print("✗ немає вхідного файла: " + SRC); return 2
    txt = open(SRC, encoding="utf-8").read()
    print("вхід : %s  md5 %s" % (os.path.basename(SRC),
                                 hashlib.md5(txt.encode("utf-8")).hexdigest()))

    if GUARD not in txt:
        print("✗ не знайдено рядка, де sd отримує rect — фікс може бути не за адресою")
        return 3

    if OLD not in txt:
        if NEW in txt:
            print("= вже пропатчено — правок нема")
            if os.path.exists(DST):
                d = open(DST, encoding="utf-8").read()
                print("вихід: md5 %s" % hashlib.md5(d.encode("utf-8")).hexdigest())
            return 0
        print("✗ якір не знайдено ні в старій, ні в новій формі"); return 4

    if txt.count(OLD) != 1:
        print("✗ якір не унікальний: %d" % txt.count(OLD)); return 5

    txt = txt.replace(OLD, NEW, 1)
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, "w", encoding="utf-8").write(txt)
    print("✓ паспорт полагоджено: sd.getBoundingClientRect().top -> sd.top")
    print("вихід: %s  md5 %s" % (os.path.basename(DST),
                                 hashlib.md5(txt.encode("utf-8")).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
