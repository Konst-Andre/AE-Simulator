#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x63_measure_v1.py · AE-Simulator · S61 · хід 2 «ЗАМІР СТИКУ»
Знімає з AE_X27_SIDEBAR_v18.html ЖИВІ значення (computed), а не дефолти CSS:
паспорт оператора ставить частину токенів з JS, тому читання CSS бреше.
Нічого не пише в стенд. Вихід — таблиця для плану порту.
"""
import json, sys
from playwright.sync_api import sync_playwright

SRC = "file:///mnt/user-data/outputs/AE_X27_SIDEBAR_v18.html"
WIDTHS = [1920, 1536, 1280]

TOKENS = ["--isl-main", "--isl-surface", "--isl-head", "--isl-foot",
          "--isl-canvas", "--isl-border", "--isl-border-w",
          "--isl-radius", "--isl-inset", "--isl-shadow",
          "--anc-yellow-25", "--green", "--anc-text", "--anc-text-2",
          "--side-w"]

JS = """
() => {
  const V2 = document.querySelector('.v2');
  if(!V2) return {err:'.v2 не знайдено'};
  const cs = getComputedStyle(V2);
  const tok = {};
  %TOKLIST%.forEach(t => tok[t] = cs.getPropertyValue(t).trim());

  const q = s => document.querySelector(s);
  const box = el => { if(!el) return null; const r = el.getBoundingClientRect();
    return {x:+r.x.toFixed(1), y:+r.y.toFixed(1), w:+r.width.toFixed(1), h:+r.height.toFixed(1)}; };

  const sb = q('.v2 .sidebar');
  const mn = q('.v2 .shell > main');
  const links = [...document.querySelectorAll('.v2 .side-link')];
  const act = q('.v2 .side-link.active') || links[0];
  const sbs = sb ? getComputedStyle(sb) : null;
  const acs = act ? getComputedStyle(act) : null;

  return {
    tok,
    shell: V2.getAttribute('data-shell'),
    mode:  V2.getAttribute('data-mode'),
    v2bg:  cs.backgroundColor,
    sidebar: box(sb),
    main:   box(mn),
    mainH:  mn ? +mn.getBoundingClientRect().height.toFixed(0) : null,
    sbStyle: sbs ? {bg:sbs.backgroundColor, radius:sbs.borderRadius,
                    border:sbs.borderTopWidth+' '+sbs.borderTopColor,
                    shadow:sbs.boxShadow, pad:sbs.padding} : null,
    links: links.length,
    active: act ? act.textContent.trim().slice(0,24) : null,
    actStyle: acs ? {h:+act.getBoundingClientRect().height.toFixed(1),
                     bg:acs.backgroundColor, bl:acs.borderLeftWidth+' '+acs.borderLeftColor,
                     radius:acs.borderRadius, gap:acs.gap, pad:acs.padding,
                     fw:acs.fontWeight} : null
  };
}
""".replace("%TOKLIST%", json.dumps(TOKENS))


def main():
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in WIDTHS:
            pg = b.new_page(viewport={"width": w, "height": 960})
            pg.goto(SRC)
            pg.wait_for_timeout(500)
            out[w] = pg.evaluate(JS)
            pg.close()
        b.close()

    base = out[WIDTHS[0]]
    if base.get("err"):
        print("✗ " + base["err"]); return 2

    print("=== ЖИВІ ТОКЕНИ (computed на .v2, 1920) ===")
    for k, v in base["tok"].items():
        print("  %-16s %s" % (k, v or "(порожньо)"))

    print("\n=== ОБОЛОНКА ===")
    print("  data-shell=%s · data-mode=%s · фон .v2 %s" %
          (base["shell"], base["mode"], base["v2bg"]))
    print("  панель: %s" % json.dumps(base["sbStyle"], ensure_ascii=False))

    print("\n=== ПУНКТ: активний (%s, усього %d) ===" % (base["active"], base["links"]))
    print("  %s" % json.dumps(base["actStyle"], ensure_ascii=False))

    print("\n=== ГЕОМЕТРІЯ ПО ШИРИНАХ ===")
    print("  %-7s %-28s %-28s %s" % ("ширина", "панель", "main", "висота main"))
    for w in WIDTHS:
        r = out[w]
        print("  %-7s %-28s %-28s %s" % (
            w, json.dumps(r["sidebar"]), json.dumps(r["main"]), r["mainH"]))

    # звірка сталості токенів між ширинами
    diff = [w for w in WIDTHS[1:] if out[w]["tok"] != base["tok"]]
    print("\n  токени однакові на всіх ширинах: %s" % ("НІ " + str(diff) if diff else "так"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
