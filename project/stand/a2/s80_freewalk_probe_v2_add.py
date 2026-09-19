#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# живе доки: знахідки З4/З6 S80 не винесені у вироки
import sys, pathlib
from playwright.sync_api import sync_playwright
f = pathlib.Path(sys.argv[1]).resolve()
def m(t, v): print("· %-44s %s" % (t, v), flush=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 800})
    J = lambda s: pg.evaluate(s)
    pg.goto(f.as_uri()); pg.wait_for_timeout(400)

    # З4' тост на 1280, у робочій зоні
    pg.click('.scenario-item[data-id="2"]'); pg.wait_for_timeout(250)
    pg.fill("#f-title", pg.input_value("#f-title") + " X"); pg.wait_for_timeout(200)
    pg.click("#undo"); pg.wait_for_timeout(250)
    m("З4' тост opacity", J("getComputedStyle(document.querySelector('#toast')).opacity"))
    m("З4' перекрито елементів", J("""(()=>{const t=document.querySelector('#toast').getBoundingClientRect();
      const hit=[];document.querySelectorAll('input,textarea,select,.pos,.set,.pot,.chk,label,b,.scenario-item').forEach(el=>{
      const r=el.getBoundingClientRect(); if(r.width&&r.height&&r.left<t.right&&r.right>t.left&&r.top<t.bottom&&r.bottom>t.top)
      hit.push((el.className&&el.className.toString().split(' ')[0])||el.tagName);});
      return hit.length+' : '+[...new Set(hit)].slice(0,8).join(', ');})()"""))
    m("З4' тост rect", J("(r=>[Math.round(r.left),Math.round(r.top),Math.round(r.width)])(document.querySelector('#toast').getBoundingClientRect())"))

    # З6' порожній ідеальний набір — що бачить Оля і що фармацевт
    pg.reload(); pg.wait_for_timeout(400)
    pg.set_viewport_size({"width": 1920, "height": 1080}); pg.wait_for_timeout(200)
    pg.click('.scenario-item[data-id="1"]'); pg.wait_for_timeout(300)
    for _ in range(12):
        if pg.locator(".set .pos .x").count() == 0: break
        pg.locator(".set .pos .x").first.click(); pg.wait_for_timeout(120)
    m("З6' позицій у наборах лишилось", J("document.querySelectorAll('.set .pos').length"))
    m("З6' орієнтир у прев'ю", J("(document.querySelector('.pot b')||{}).textContent"))
    m("З6' попередження під назвою", J("document.querySelector('#m-title').textContent.trim()") or "(нічого)")
    m("З6' причина блоку публікації", J("(()=>{const e=document.querySelector('#m-pub');return e.hidden?'(схована)':e.textContent.trim().slice(0,90)})()"))
    m("З6' «Опублікувати» disabled", J("document.querySelector('#pub').disabled"))
    m("З6' крапка стану в списку", J("document.querySelector('.scenario-item.active .dot').className+' | '+document.querySelector('.scenario-item.active .dot').title"))

    # З9 рядок номера на 1536/1280 (щілина probe 26)
    for w in (1536, 1280):
        pg.set_viewport_size({"width": w, "height": 800}); pg.wait_for_timeout(200)
        m("З9 %d рядок номера h,px" % w, J("(()=>{const e=document.querySelector('.no-line');return e?[e.textContent.trim().slice(0,40),Math.round(e.getBoundingClientRect().height)]:'(елемента немає)'})()"))
    b.close()
