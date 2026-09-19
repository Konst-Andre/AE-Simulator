#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# живе доки: v4.4 не змерджено в наступну версію стенда
# s79_v44_probe_v1.py <html> — три нові кроки v4.4; на v4.3 мусять дати ✗ (П117)
import sys, pathlib
from playwright.sync_api import sync_playwright

f = pathlib.Path(sys.argv[1]).resolve()
ok = bad = 0
def say(c, name, det=""):
    global ok, bad
    print(("✓ " if c else "✗ ") + name + (" · " + str(det) if det else ""))
    if c: ok += 1
    else: bad += 1

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1920, "height": 1080})
    E = []; pg.on("pageerror", lambda e: E.append(str(e)))
    pg.goto(f.as_uri()); pg.wait_for_timeout(400)

    # 24 · В-112 порядок груп у фільтрі списку — за абеткою (uk)
    opts = pg.eval_on_selector_all("#gf option", "els=>els.map(e=>e.textContent.trim())")
    gs = [o.split(" · ")[0] for o in opts if "Усі групи" not in o]
    srt = sorted(gs, key=lambda s: s.lower())
    say(gs == srt and len(gs) > 1, "24 В-112 фільтр: групи за абеткою", gs)

    # 25 · В-112 те саме в селекті «Група» редактора
    pg.click(".scenario-item"); pg.wait_for_timeout(250)
    g2 = pg.eval_on_selector_all("#f-grp option",
         "els=>els.map(e=>e.textContent.trim()).filter(t=>!t.startsWith('+'))")
    say(g2 == sorted(g2, key=lambda s: s.lower()) and len(g2) > 1,
        "25 В-112 селект «Група»: за абеткою", g2)

    # 26 · рядок номера: при наявному номері — жодного тексту, нульова висота
    found = None
    for i in range(pg.locator(".scenario-item").count()):
        pg.locator(".scenario-item").nth(i).click(); pg.wait_for_timeout(180)
        txt = pg.locator("#m-no").inner_text().strip()
        open_txt = pg.locator("#f-open").input_value()
        if any(ch.isdigit() for ch in open_txt):
            h = pg.evaluate("document.querySelector('#m-no').getBoundingClientRect().height")
            found = {"txt": txt, "h": round(h, 1)}
            break
    say(found is not None and found["txt"] == "" and found["h"] == 0,
        "26 рядок номера при номері у фразі: порожній, 0 px", found)

    say(len(E) == 0, "pageerror 0", E)
    b.close()

print("\nПІДСУМОК: %d ✓ · %d ✗" % (ok, bad))
sys.exit(0 if bad == 0 else 1)
