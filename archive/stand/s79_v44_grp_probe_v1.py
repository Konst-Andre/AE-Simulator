#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# живе доки: v4.4 не змерджено в наступну версію стенда
# s79_v44_grp_probe_v1.py <html> — В-113: нова порожня група переживає «Опублікувати»
import sys, pathlib
from playwright.sync_api import sync_playwright

f = pathlib.Path(sys.argv[1]).resolve()
NAME = "Тестова тека"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1920, "height": 1080})
    E = []; pg.on("pageerror", lambda e: E.append(str(e)))
    pg.goto(f.as_uri()); pg.wait_for_timeout(400)

    # щоб «Опублікувати» став активним, потрібна чернетка
    pg.click(".scenario-item"); pg.wait_for_timeout(250)
    pg.fill("#f-title", pg.input_value("#f-title") + " ·")
    pg.wait_for_timeout(250)

    pg.click(".grp-btn"); pg.wait_for_timeout(250)
    pg.click("#dgAdd"); pg.wait_for_timeout(200)
    rows = pg.locator("#dg input")
    rows.nth(rows.count() - 1).fill(NAME)
    pg.click("#dgApply"); pg.wait_for_timeout(300)

    before = pg.eval_on_selector_all("#gf option", "els=>els.map(e=>e.textContent.split(' · ')[0].trim())")
    pg.click("#pub"); pg.wait_for_timeout(500)
    after = pg.eval_on_selector_all("#gf option", "els=>els.map(e=>e.textContent.split(' · ')[0].trim())")

    ok = NAME in before and NAME in after
    print(("✓ " if ok else "✗ ") + "27 В-113 порожня група переживає «Опублікувати» · до: %s · після: %s"
          % (NAME in before, NAME in after))
    print(("✓ " if not E else "✗ ") + "pageerror %d · %s" % (len(E), E))
    pg.screenshot(path="v44_after_pub.png", clip={"x": 0, "y": 0, "width": 900, "height": 620})
    b.close()
sys.exit(0 if ok and not E else 1)
