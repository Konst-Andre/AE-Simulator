# s83_v45_touch_v1.py · дотик до 9 вироків v4.5 (не прохід П115 — той наступним ходом) · живе доки: хід 2 S83
import sys, pathlib
from playwright.sync_api import sync_playwright
U='file://'+str(pathlib.Path(sys.argv[1]).resolve())
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080}); E=[]; pg.on('pageerror',lambda e:E.append(str(e)))
  pg.goto(U); pg.wait_for_timeout(300); J=pg.evaluate; out={}
  pg.click('#newSc'); pg.wait_for_timeout(200)
  out['118a новий при «Усі групи» →']=J("document.querySelector('#f-grp').value")
  pg.click('#delSc'); pg.wait_for_timeout(100)
  if J("document.querySelector('#dc').open"): pg.click('#dcYes')
  pg.wait_for_timeout(150)
  pg.select_option('#f-grp','__new'); pg.wait_for_timeout(200)
  out['122 «i» у діалозі']=J("!!document.querySelector('#dg [popovertarget=i-grp]')")
  out['123 Скасувати в діалозі — клас']=J("document.querySelector('#dg [data-dgcancel]:not([aria-label])').className")
  rows=J("[...document.querySelectorAll('#dgb .grow')].map(r=>({n:r.querySelector('.in').value,def:r.querySelector('[type=radio]').checked,del:r.querySelector('.x').disabled}))")
  out['118b дефолт у діалозі']=[r for r in rows if r['def']]
  # позначаю «Антибіотики» дефолтом, прибираю порожній новий рядок
  i=[r['n'] for r in rows].index('Антибіотики'); pg.check(f'[data-gdef="{i}"]'); pg.wait_for_timeout(100)
  out['118c кошик «Базові» після зміни дефолту (5+ сценаріїв → має лишитись disabled)']=J("[...document.querySelectorAll('#dgb .grow')].find(r=>r.querySelector('.in').value==='Базові').querySelector('.x').disabled")
  J("document.querySelectorAll('#dgb .grow').forEach(r=>{if(!r.querySelector('.in').value) r.querySelector('.x').click()})"); pg.wait_for_timeout(100)
  pg.click('#dgApply'); pg.wait_for_timeout(200)
  out['118d тост']=J("document.querySelector('#toast').textContent")
  pg.click('#newSc'); pg.wait_for_timeout(200)
  out['118e новий після зміни →']=J("document.querySelector('#f-grp').value")
  # 119: новий сценарій без наборів
  out['119a орієнтир порожній набір']=J("document.querySelector('.pot b').textContent")
  pg.click('.scenario-item[data-id=\"1\"]'); pg.wait_for_timeout(150)
  out['119b орієнтир сц.1']=J("document.querySelector('.pot b').textContent")
  pg.check('[data-k=hint]'); pg.wait_for_timeout(150)
  out['120 підписи наборів']=J("[...document.querySelectorAll('.hset-h')].map(x=>x.textContent)")
  out['121 .pv overflow-x']=J("getComputedStyle(document.querySelector('.pv')).overflowX")
  out['124 margin #delSc']=J("getComputedStyle(document.querySelector('#delSc')).marginRight")
  out['125 низ .page']=J("getComputedStyle(document.querySelector('#page')||document.querySelector('.page')).paddingBottom")
  out['123 Скасувати в підтвердженні']=J("document.querySelector('#dcNo').className")
  # 126: сц.1 має чернетку (hint) — додаю попередження? дивлюсь крапки
  out['126 крапки (стан → к-сть)']=J("(()=>{const m={};document.querySelectorAll('.scenario-item .dot').forEach(d=>{const k=d.className.replace('dot','').trim()||'—';m[k]=(m[k]||0)+1});return m})()")
  out['помилки сторінки']=E
  for k,v in out.items(): print(k,':',v)
