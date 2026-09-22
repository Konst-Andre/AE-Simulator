#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# живе доки: знахідки S80 не винесені у вироки й не стали кроками проходу (П115/П117)
# s80_freewalk_probe_v1.py <html> — ВІЛЬНИЙ ПРОХІД «як Оля»: ЗАМІРИ, не ✓/✗-кроки.
# Кожен рядок друкує ЧИСЛО або ТЕКСТ. Вироки виносить оператор.
import sys, pathlib, json
from playwright.sync_api import sync_playwright

f = pathlib.Path(sys.argv[1]).resolve()
OUT = []
def m(tag, val): OUT.append((tag, val)); print("· %-46s %s" % (tag, val), flush=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    E = []; pg.on("pageerror", lambda e: E.append(str(e)))
    J = lambda s: pg.evaluate(s)
    pg.goto(f.as_uri()); pg.wait_for_timeout(400)

    # ── З1 · новий сценарій при фільтрі «Усі групи» (база для В-118) ──
    m("З1 фільтр за замовчуванням", J("document.querySelector('#gf').value || '(Усі групи)'"))
    pg.click("#newSc"); pg.wait_for_timeout(350)
    m("З1 група нового сценарію", J("document.querySelector('#f-grp').value"))
    m("З1 перша група списку", J("document.querySelector('#f-grp').options[0].value"))

    # ── З2 · порожня назва: що бачить Оля і чи блокує публікацію ──
    pg.fill("#f-title", ""); pg.wait_for_timeout(300)
    m("З2 текст під назвою", J("document.querySelector('#m-title').textContent.trim()") or "(порожньо)")
    m("З2 «Опублікувати» disabled", J("document.querySelector('#pub').disabled"))
    m("З2 причина блоку видима", J("(()=>{const e=document.querySelector('#m-pub');return !e.hidden && e.textContent.trim().slice(0,80)})()"))
    m("З2 рядок у списку без назви", J("document.querySelector('.scenario-item b').textContent.trim()"))

    # ── З3 · дуже довга назва: чи розпирає сторінку (К10) ──
    pg.fill("#f-title", "Дуже довга назва сценарію " * 12); pg.wait_for_timeout(350)
    m("З3 scrollWidth vs innerWidth", J("[document.documentElement.scrollWidth, window.innerWidth]"))
    m("З3 висота шапки редактора, px", J("Math.round(document.querySelector('.ed-head').getBoundingClientRect().height)"))
    m("З3 висота рядка в списку, px", J("Math.round(document.querySelector('.scenario-item').getBoundingClientRect().height)"))

    # ── З4 · тост: чи накриває дані ──
    pg.fill("#f-title", "Тест тосту"); pg.wait_for_timeout(200)
    pg.click('.scenario-item[data-id="2"]'); pg.wait_for_timeout(250); pg.fill('#f-title', pg.input_value('#f-title')+' X'); pg.wait_for_timeout(200); pg.click('#undo'); pg.wait_for_timeout(250)
    m("З4 тост видимий", J("getComputedStyle(document.querySelector('#toast')).opacity"))
    m("З4 текст тосту", J("document.querySelector('#toast').textContent"))
    m("З4 перекриті елементи під тостом", J("""(()=>{
      const t=document.querySelector('#toast').getBoundingClientRect();
      if(t.width===0) return 'тост не видно';
      const hit=[];
      document.querySelectorAll('.card input,.card textarea,.card select,.pos,.chk,.set,.pot,.scenario-item').forEach(el=>{
        const r=el.getBoundingClientRect();
        if(r.width&&r.left<t.right&&r.right>t.left&&r.top<t.bottom&&r.bottom>t.top)
          hit.push((el.className||el.tagName).toString().split(' ')[0]);
      });
      return hit.length+' : '+hit.slice(0,6).join(', ');})()"""))
    m("З4 z-index тосту / sticky-шапки", J("[getComputedStyle(document.querySelector('#toast')).zIndex, getComputedStyle(document.querySelector('.ed-head')).zIndex]"))

    # ── З5 · пошук без результатів ──
    pg.wait_for_timeout(2300)
    pg.fill("#q", "ждлоапрі"); pg.wait_for_timeout(300)
    m("З5 рядків у списку", J("document.querySelectorAll('.scenario-item').length"))
    m("З5 що показано замість списку", J("(()=>{const l=document.querySelector('#items');return l.textContent.trim().slice(0,70)||'(порожньо, без підказки)'})()"))
    pg.fill("#q", ""); pg.wait_for_timeout(250)

    # ── З6 · орієнтир при порожньому замовленні ──
    pg.click(".scenario-item[data-id='1']"); pg.wait_for_timeout(300)
    m("З6 орієнтир (є позиція)", J("(document.querySelector('.pot b')||{}).textContent"))
    n0 = J("document.querySelectorAll('.pos .x').length")
    for _ in range(n0):
        if pg.locator(".pos .x").count() == 0: break
        pg.locator(".pos .x").first.click(); pg.wait_for_timeout(120)
    m("З6 орієнтир (усе прибрано)", J("(document.querySelector('.pot b')||{}).textContent"))
    m("З6 «Просить» у прев'ю", J("(()=>{const e=[...document.querySelectorAll('#pv *')].find(x=>/ПРОСИТЬ/i.test(x.textContent)&&x.children.length<3);return e?e.parentElement.textContent.replace(/\\s+/g,' ').trim().slice(0,70):'(розділу немає)'})()"))
    pg.reload(); pg.wait_for_timeout(400)

    # ── З7 · прев'ю на 1536: скільки ширини використано ──
    pg.set_viewport_size({"width": 1536, "height": 864}); pg.wait_for_timeout(250)
    pg.click(".seg [data-view=pv]"); pg.wait_for_timeout(300)
    m("З7 1536 картка прев'ю / поле, px", J("""(()=>{const c=document.querySelector('#pv>.pv-card')||document.querySelector('#pv>*'),
      p=document.querySelector('#pv');return [Math.round(c.getBoundingClientRect().width), Math.round(p.getBoundingClientRect().width)]})()"""))

    # ── З8 · probe-кроки 24·25·26 на 1536 і 1280 (чого не робили машинно) ──
    for w, h in [(1536, 864), (1280, 800)]:
        pg.set_viewport_size({"width": w, "height": h}); pg.wait_for_timeout(250)
        pg.click(".seg [data-view=form]"); pg.wait_for_timeout(250)
        m("З8 %d алфавіт фільтра" % w, J("[...document.querySelectorAll('#gf option')].slice(1).map(o=>o.textContent.split(' · ')[0])"))
        m("З8 %d алфавіт селекта групи" % w, J("[...document.querySelectorAll('#f-grp option')].map(o=>o.value).filter(v=>v&&v!=='__new')"))
        m("З8 %d кнопка «Групи» обрізана" % w, J("(()=>{const g=document.querySelector('#mg');return g.scrollWidth>g.clientWidth||g.scrollHeight>g.clientHeight})()"))
        m("З8 %d гориз. прокрутка" % w, J("document.documentElement.scrollWidth>window.innerWidth"))

    m("pageerror", "%d %s" % (len(E), E))
    b.close()
print("\nЗАМІРІВ: %d" % len(OUT))
