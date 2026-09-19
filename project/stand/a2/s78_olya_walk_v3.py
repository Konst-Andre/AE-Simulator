# s78_olya_walk_v3.py · сценарний прохід «як Оля» (П115) по D1 v4.3 (база — v2 цілком) · живе доки: A2 v2 не перенесено в X97 (D2)
# База — s77_olya_walk_v1.py цілком; змінено 2b (перенос замість обрізання), 6a (ЗФ — з підказкою, В-107), 8 (✎ ліворуч, ≤40 px).
# Запуск: python3 s78_olya_walk_v2.py <стенд.html> <корінь AE>
import sys, json, pathlib
from playwright.sync_api import sync_playwright
U='file://'+str(pathlib.Path(sys.argv[1]).resolve()); AE=pathlib.Path(sys.argv[2]); V=[]
def ok(n,c,note=''): V.append((n,'✓' if c else '✗',note)); 
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080}); E=[]; pg.on('pageerror',lambda e:E.append(str(e)))
  pg.goto(U); pg.wait_for_timeout(300); J=pg.evaluate
  # 1 створити → id 44 → лічильник → видалити → 43
  pg.click('#newSc'); pg.wait_for_timeout(200)
  ok('1a новий нагорі з ID 44', J("document.querySelector('.scenario-item .sid').textContent")=='44')
  ok('1b лічильник 44', '44' in J("document.querySelector('#health').textContent"))
  pg.fill('#f-title','Тест Олі'); ok('1c назва в списку', 'Тест Олі' in J("document.querySelector('.scenario-item.active').textContent"))
  pg.click('#delSc'); pg.wait_for_timeout(150)
  if J("document.querySelector('#dc').open"): pg.click('#dcYes')
  pg.wait_for_timeout(200); ok('1d після видалення 43', '43' in J("document.querySelector('#health').textContent"), J("document.querySelector('#health').textContent"))
  # 2 пастка: мітка в списку, у прев'ю немає, рядок не витісняє групу
  pg.click('.scenario-item[data-id="1"]'); pg.wait_for_timeout(150)
  pg.check('[data-k=trap]'); pg.check('[data-k=noSale]'); pg.wait_for_timeout(150)
  sm=J("(()=>{const s=document.querySelector('.scenario-item[data-id=\"1\"] small');return {txt:s.textContent,over:s.scrollHeight>s.clientHeight+1,lines:Math.round(s.clientHeight/parseFloat(getComputedStyle(s).lineHeight))}})()")
  ok('2a мітки в списку', 'пастка' in sm['txt'] and 'не міняти' in sm['txt'], sm['txt'])
  ok('2b група/характер не витіснені (перенос, без хвоста)', not sm['over'], f"рядків {sm['lines']}")
  ok('2c у прев\'ю немає пастки', not J("/Пастка|Не міняти чек/.test(document.querySelector('#pv').textContent)"))
  pg.locator('.scenario-item[data-id="1"]').screenshot(path='w2_list_row.png')
  pg.click('#undo'); pg.wait_for_timeout(150)
  if J("document.querySelector('#dc').open"): pg.click('#dcYes')
  pg.wait_for_timeout(150); ok('2d Скасувати знімає', not J("document.querySelector('[data-k=trap]').checked"))
  # 3 «i» на кожному прапорці
  for k in ['trap','noSale','hint','goods','recs','char','goal']:
    if not J(f"!!document.querySelector('[popovertarget=\"i-{k}\"]')"): ok(f'3 «i» {k}', False, 'кнопки немає'); continue
    pg.click(f'[popovertarget="i-{k}"]'); pg.wait_for_timeout(100)
    o=J(f"(()=>{{const t=document.querySelector('#i-{k}'),r=t.getBoundingClientRect();return {{open:t.matches(':popover-open'),inv:r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight,cb:!!document.querySelector('[data-k={k}]')?.checked}}}})()")
    pg.keyboard.press('Escape'); pg.wait_for_timeout(80)
    ok(f'3 «i» {k}', o['open'] and o['inv'] and not o['cb'] and not J(f"document.querySelector('#i-{k}').matches(':popover-open')"))
  # 4 пошук 32
  pg.fill('#q','32'); pg.wait_for_timeout(150)
  ok('4 пошук «32» → 1 рядок ID 32', J("[...document.querySelectorAll('.scenario-item .sid')].map(x=>x.textContent).join()")=='32')
  pg.fill('#q',''); pg.wait_for_timeout(100)
  # 5 група → чип
  opts=J("[...document.querySelectorAll('#f-grp option')].map(o=>o.value)"); g=[x for x in opts if x and x!='Базові'][0]
  pg.select_option('#f-grp', g); pg.wait_for_timeout(150)
  ok('5 зміна групи → чип', J("document.querySelector('#pv .badge').textContent")==g, g)
  pg.click('#undo'); pg.wait_for_timeout(100)
  if J("document.querySelector('#dc').open"): pg.click('#dcYes')
  # 6 ЗФ і підказка у прев'ю
  pg.check('[data-k=hint]'); pg.wait_for_timeout(150)
  zf=J("document.querySelector('#pv').textContent.includes('Урохолум')")
  ok('6a з підказкою ЗФ-набір видно (В-107)', zf, J("[...document.querySelectorAll('#pv .hset-h')].map(x=>x.textContent).join(' | ')"))
  cnt=J("(document.querySelector('#pv').textContent.match(/Нефролак/g)||[]).length")
  ok('6b підказка: набір рівно раз', cnt==1, f'Нефролак ×{cnt}')
  pg.locator('#pv').screenshot(path='w6_pv_hint.png'); pg.uncheck('[data-k=hint]')
  noHint=J("(document.querySelector('#pv').textContent.match(/Нефролак/g)||[]).length")
  ok('6c без підказки фармацевт набору не бачить (Б3)', noHint==0, f'Нефролак ×{noHint}')
  # 7 «+ Додати» у випадайці категорій
  ok('7 «+ Додати» не пункт списку', J("!document.querySelector('#addcat option').hidden"), 'плейсхолдер видно в списку') if False else ok('7 «+ Додати» не пункт списку', J("document.querySelector('#addcat option').hidden"), 'плейсхолдер видно в розкритому списку')
  ok('7b плейсхолдер «Додати позицію» не пункт списку', J("[...document.querySelectorAll('.add-pos')].every(x=>x.options[0].hidden)"))
  # 8 олівець
  pg.locator('#editor').screenshot(path='w8_head.png', clip=None) if False else None
  tr=J("(()=>{const t=document.querySelector('#f-title'),cs=getComputedStyle(t);return {pos:cs.backgroundPositionX,pl:parseFloat(cs.paddingLeft)}})()")
  gap=tr['pl']-9-18
  ok('8 ✎ поруч із назвою (≤40 px)', tr['pos'].startswith('9px') and 0<=gap<=40, f"✎ ліворуч, від ✎ до тексту {gap:.0f} px")
  for w,h in [(1280,800),(1536,864)]:
    pg.set_viewport_size({'width':w,'height':h}); pg.wait_for_timeout(200)
    ok(f'9 {w}: ширина документа', J("document.documentElement.scrollWidth")==w)
  pg.set_viewport_size({'width':1920,'height':1080}); pg.wait_for_timeout(200); pg.screenshot(path='w_top_1920.png', clip={'x':0,'y':0,'width':1920,'height':520})

  # ── нові кроки S78 ──
  S=json.loads((AE/'data/scenarios.json').read_text(encoding='utf-8')); S=S if isinstance(S,list) else S['scenarios']
  C=json.loads((AE/'data/catalog.json').read_text(encoding='utf-8'))['categories']; B={i['c']:i['b'] for v in C.values() for i in v['items']}
  H=[l[3:].strip() for l in (AE/'prompts/characters.md').read_text(encoding='utf-8').splitlines() if l.startswith('## ')]
  pg.fill('#q',''); pg.wait_for_timeout(100)
  # 10 орієнтир = potential() рушія на всіх сценаріях
  bad=[]
  for s_ in S:
    pg.click(f'.scenario-item[data-id="{s_["id"]}"]'); pg.wait_for_timeout(40)
    got=J("document.querySelector('#pv .pot b').textContent")
    exp='—' if s_.get('noSale') else 'до +'+format(max(1,int(__import__('math').floor(sum(B.get(c,0) for c in s_['bv'])-sum(B.get(c,0) for c in s_['order'])+0.5))),',').replace(',','\u00a0')+' ₴'
    if got!=exp: bad.append((s_['id'],got,exp))
  ok('10 орієнтир = X97 potential() · 43 сценарії', not bad, str(bad[:3]))
  # 11 однакові набори → один блок «обидва правила»; noSale → без підказки
  same=[x for x in S if sorted(x['bm'])==sorted(x['bv']) and not x.get('noSale')][0]
  pg.click(f'.scenario-item[data-id="{same["id"]}"]'); pg.check('[data-k=hint]'); pg.wait_for_timeout(120)
  hs=J("[...document.querySelectorAll('#pv .hset-h')].map(x=>x.textContent)")
  ok('11a bm=bv → один набір «обидва правила»', len(hs)==1 and 'обидва' in hs[0], f"#{same['id']}: {hs}")
  pg.click('#undo'); pg.wait_for_timeout(100)
  if J("document.querySelector('#dc').open"): pg.click('#dcYes')
  ns=[x for x in S if x.get('noSale')][0]
  pg.click(f'.scenario-item[data-id="{ns["id"]}"]'); pg.check('[data-k=hint]'); pg.wait_for_timeout(120)
  r=J("({hb:document.querySelectorAll('#pv .hintbox').length,after:document.querySelector('#pv').textContent.includes('правильна дія — не міняти')})")
  ok('11b не міняти чек: підказка без наборів, розбір «не міняти»', r['hb']==0 and r['after'], f"#{ns['id']} {r}")
  pg.click('#undo'); pg.wait_for_timeout(100)
  if J("document.querySelector('#dc').open"): pg.click('#dcYes')
  pg.click('.scenario-item[data-id="1"]'); pg.wait_for_timeout(100)
  # 12 чип групи інлайн у назві
  c=J("(()=>{const h=document.querySelector('#pv h4'),b=h.querySelector('.badge.grp');if(!b)return null;const hr=h.getBoundingClientRect(),br=b.getBoundingClientRect();return {inH4:true,dyBottom:Math.round(hr.bottom-br.bottom),dyMid:Math.round((br.top+br.bottom)/2-(hr.bottom-parseFloat(getComputedStyle(h).lineHeight)/2))}})()")
  ok('12 чип групи по центру рядка назви (Н6, |dyMid|≤2)', bool(c) and abs(c['dyMid'])<=2, str(c))
  # 13 характери = носій, порядок носія (Б4)
  ch=J("[...document.querySelectorAll('#f-ch option')].map(o=>o.textContent)")
  ok('13 характери з prompts/characters.md', ch==H, f"{len(ch)} = {len(H)}")
  # 14 назва прапорця
  ok('14 «Не міняти чек»', J("document.querySelector('[data-k=noSale]').nextElementSibling.textContent")=='Не міняти чек')
  # 15 «i» на правому краї (Н2 — очікувано ✗ до v4.3)
  pos=J("[...document.querySelectorAll('#editor .info')].map(b=>{const c=b.parentElement.getBoundingClientRect(),r=b.getBoundingClientRect();return [b.getAttribute('popovertarget'),Math.round(c.right-r.right)]})")
  vals=sorted({d for _,d in pos})
  ok('15 «i» на правому краї свого рядка (Н2)', vals==[0], str(pos))
  # 16 ✎ контраст (Н4, замір) і порожня смуга під назвою (Н7)
  k=J("(()=>{const L=h=>{const n=parseInt(h.slice(1),16),a=[n>>16,n>>8&255,n&255].map(v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4});return .2126*a[0]+.7152*a[1]+.0722*a[2]};const bg=getComputedStyle(document.querySelector('.ed-head')).backgroundColor.match(/[0-9]+/g).map(Number);const hex='#'+bg.map(v=>v.toString(16).padStart(2,'0')).join('');const st=getComputedStyle(document.querySelector('#f-title')).backgroundImage.match(/stroke='%23([0-9A-Fa-f]{6})'/);const a=L('#'+st[1]),b=L(hex);return {bg:hex,ratio:+((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2)}})()")
  ok('16a ✎ контраст ≥3:1 (WCAG 1.4.11)', k['ratio']>=3, str(k))
  mp=J("(()=>{const m=document.querySelector('#m-pub');return {hidden:m.hidden,h:m.getBoundingClientRect().height}})()")
  ok('16b прихований «Не опубліковано» не займає місця (Н7)', not (mp['hidden'] and mp['h']>0), str(mp))
  # 17 режим ≤1600: перемикач Форма / Прев'ю
  pg.set_viewport_size({'width':1536,'height':864}); pg.wait_for_timeout(200)
  f=J("({seg:getComputedStyle(document.querySelector('.seg')).display,pv:getComputedStyle(document.querySelector('.pv')).display,cards:getComputedStyle(document.querySelector('.cards')).display})")
  ok('17a ≤1600 «Форма»: перемикач є, прев\'ю сховане', f['seg']!='none' and f['pv']=='none' and f['cards']!='none', str(f))
  pg.click('.seg [data-view=pv]'); pg.wait_for_timeout(150)
  f=J("({pv:getComputedStyle(document.querySelector('.pv')).display,cards:getComputedStyle(document.querySelector('.cards')).display,sw:document.documentElement.scrollWidth,pot:!!document.querySelector('#pv .pot')})")
  ok('17b ≤1600 «Прев\'ю»: картки сховані, прев\'ю з орієнтиром, без гориз. прокрутки', f['pv']!='none' and f['cards']=='none' and f['pot'] and f['sw']==1536, str(f))
  pg.screenshot(path='w17_1536_pv.png')
  pg.fill('#f-title','Змінена назва'); pg.wait_for_timeout(100)
  ok('17c правка в «Прев\'ю» видна одразу', J("document.querySelector('#pv h4').textContent").startswith('Змінена назва'))
  pg.click('.seg [data-view=form]'); pg.wait_for_timeout(150)
  ok('17d назад у «Форму»', J("getComputedStyle(document.querySelector('.cards')).display")!='none')
  pg.click('#undo'); pg.wait_for_timeout(100)
  if J("document.querySelector('#dc').open"): pg.click('#dcYes')
  pg.set_viewport_size({'width':1280,'height':800}); pg.wait_for_timeout(150); pg.screenshot(path='w17_1280.png')
  pg.set_viewport_size({'width':1920,'height':1080}); pg.wait_for_timeout(150)
  pg.locator('.ed-head').screenshot(path='w16_head.png')

  # ── нові кроки v4.3 ──
  pg.click('.scenario-item[data-id="1"]'); pg.wait_for_timeout(120)
  pv=J("(()=>{const pv=document.querySelector('#pv'),secs=[...pv.querySelectorAll('.sec')].map(x=>x.textContent);const ask=secs.indexOf('Просить');let rows=pv.querySelectorAll('.sec')[ask].nextElementSibling;return {secs,askTxt:rows.textContent,bubblePrev:pv.querySelector('.bubble').previousElementSibling.textContent}})()")
  ok('18 Н5 «Просить» без ціни, з категорією', '₴' not in pv['askTxt'] and 'Урологія' in pv['askTxt'], pv['askTxt'])
  ok('19 Н8 «Розмова починається з» над фразою', pv['bubblePrev']=='Розмова починається з')
  tips=J("({goal:document.querySelector('#i-goal')?.textContent||'',recs:document.querySelector('#i-recs').textContent,char:document.querySelector('#i-char').textContent,goods:document.querySelector('#i-goods').textContent})")
  ok('20 Н1/Н3 тексти «i»', 'до розмови' in tips['goal'] and 'Каталоз' in tips['recs'] and '${' not in tips['recs'] and 'не бачить' not in tips['char'] and 'не створюються' in tips['goods'], tips['recs'][:80])
  g=J("(()=>{const m=document.querySelector('#mg'),sv=(m.querySelector('svg')||m).getBoundingClientRect(),f=document.querySelector('#gf');const mr=m.getBoundingClientRect(),svr=(m.querySelector('svg')||m).getBoundingClientRect();return {oneRow:Math.abs((svr.top+svr.bottom)/2-(mr.top+mr.bottom)/2)<=2,clip:m.scrollWidth>m.clientWidth||m.scrollHeight>m.clientHeight,txt:m.textContent.trim(),svg:m.querySelector('svg')?Math.round(sv.width):0,sel:Math.round(f.getBoundingClientRect().width),selOver:f.scrollWidth>f.clientWidth}})()")
  ok('21 О4 кнопка «Групи»: іконка й підпис в один рядок, без обрізання, фільтр не стиснуто', g['oneRow'] and not g['clip'] and g['txt']=='Групи' and g['svg']>=18 and g['sel']>=150, str(g))
  pg.set_viewport_size({'width':1536,'height':864}); pg.wait_for_timeout(150); pg.click('.seg [data-view=pv]'); pg.wait_for_timeout(150)
  o=J("(()=>{const s=document.querySelector('.seg').getBoundingClientRect(),v=document.querySelector('.pv').getBoundingClientRect();return {gap:Math.round(v.top-s.bottom),pvh:getComputedStyle(document.querySelector('.pv-h')).display}})()")
  ok('22 О1/О3 ≤1600 «Прев\'ю»: відступ ≤20 px, без другого заголовка', o['gap']<=20 and o['pvh']=='none', str(o))
  pg.click('.seg [data-view=form]'); pg.set_viewport_size({'width':1920,'height':1080}); pg.wait_for_timeout(150)
  ok('23 1920: заголовок прев\'ю на місці', J("getComputedStyle(document.querySelector('.pv-h')).display")!='none')
  pg.screenshot(path='v43_1920.png'); pg.locator('.filter-row').screenshot(path='v43_groups.png'); pg.locator('.ed-head').screenshot(path='v43_head.png')
  ok('pageerror 0', not E, str(E))
  b.close()
for n,s,note in V: print(s,n,'·',note)
