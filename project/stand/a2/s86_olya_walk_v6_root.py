# s86_olya_walk_v6_root.py · прохід «як Оля» (П115/П117) — v5 цілком + заглушка api.github.com (D2 крок 5.3: острів звіряється на вході)
# живе доки: D2 крок 8 (SPEC, П116) — далі в archive/stand; детектор кроків 5б–7 бере його ж. v5 → archive/stand (S86).
# Зміна проти v5 лише в оснастці: api.github.com віддає файли з теки білда (фіктивний sha) — детектор не ходить у мережу
# і не палить ліміт 60/год; без заглушки звірка на вході (5.3) залежала б від мережі, і пункт 30 був би лотереєю.
# Зміни проти v4 лише в оснастці: сервер усередині скрипта (S84 §5), куратор відчинений до завантаження, вхід на екран
# ascen через рушій (S.screen), глобали мокапа — адаптери острова (window.set/drawEditor/openGroups/toast/cur/st).
# Очікувано з кроку 5.3: 60 ✓ · 6 ✗ — 24–29 (дефолт групи, власник — крок 6, В-142). Інший ✗ — дефект.
# (Крок 4: 59 ✓ · 7 ✗ — 30 червоний під Р1.)
# Негативний контроль: --no-flag → острова немає → вихід 2 одразу.
# Запуск: python3 s86_olya_walk_v6_root.py <корінь AE з білдом index.html> [--no-flag]
import sys, json, re, base64, pathlib, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright
AE=pathlib.Path(sys.argv[1]).resolve(); FLAG='--no-flag' not in sys.argv; V=[]
class Q(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*a): pass
H=functools.partial(Q, directory=str(AE))
srv=socketserver.ThreadingTCPServer(('127.0.0.1',0),H); srv.daemon_threads=True
threading.Thread(target=srv.serve_forever,daemon=True).start()
U=f'http://127.0.0.1:{srv.server_address[1]}/'+('?a2v2' if FLAG else '')
def ok(n,c,note=''): V.append((n,'✓' if c else '✗',note)); 
def go(pg):
  pg.goto(U); pg.wait_for_function("typeof S!=='undefined' && S.SCEN && S.SCEN.length>0 && S.P", timeout=15000)
  pg.evaluate("S.screen='ascen'; render()")
  try: pg.wait_for_selector('#newSc', timeout=3000)
  except Exception:
    print('✗ острова A2v2 немає на', U); sys.exit(2)
  # 5.3: звірка на вході перемальовує острів — чекати її кінця, інакше клік проходу влучить у вузол, що зникне
  try: pg.wait_for_function("!pubReady() || (S.epub && S.epub.state!=='busy')", timeout=4000)
  except Exception: pass   # білд до 5.3 звірки на вході не робить
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080}); E=[]; pg.on('pageerror',lambda e:E.append(str(e)))
  pg.add_init_script("try{localStorage.setItem('ae_curator_until', String(Date.now()+36e5))}catch(_){}")
  def gh(route):
    path='data/scenarios.json' if 'scenarios.json' in route.request.url else 'data/catalog.json'
    route.fulfill(status=200, headers={'access-control-allow-origin':'*'}, content_type='application/json',
      body=json.dumps({'sha':'stub-'+path,'content':base64.b64encode((AE/path).read_bytes()).decode()}))
  pg.route(re.compile(r'^https://api\.github\.com/'), gh)
  go(pg); J=pg.evaluate
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
  # ── нові кроки S83 · v4.5 (В-118…В-126 · Н9–Н12) · П117: кожен мусить дати ✗ на v4.4 ──
  go(pg)
  TXT=lambda s: J(f"(document.querySelector({json.dumps(s)})||{{}}).textContent||''")
  def newsc():
    pg.click('#newSc'); pg.wait_for_timeout(200); return J("document.querySelector('#f-grp').value")
  def drop_new():
    pg.click('#delSc'); pg.wait_for_timeout(120)
    if J("document.querySelector('#dc').open"): pg.click('#dcYes')
    pg.wait_for_timeout(150)
  def groups_dlg():
    J("openGroups()"); pg.wait_for_timeout(150)
    return J("[...document.querySelectorAll('#dgb .grow')].map(r=>({n:r.querySelector('.in').value,def:!!r.querySelector('[type=radio]')?.checked,del:r.querySelector('.x').disabled,t:r.querySelector('.x').title}))")
  # 24 В-118 «Усі групи» → явний дефолт «Базові»
  g=newsc(); drop_new(); ok('24 В-118 новий при «Усі групи» → «Базові»', g=='Базові', g)
  # 25 В-118 дефолт видно в діалозі, рівно один
  R=groups_dlg(); D=[r['n'] for r in R if r['def']]
  ok('25 В-118 у діалозі рівно одна група ●, це «Базові»', D==['Базові'], str(D))
  # 26 В-118 порожня група-дефолт не видаляється (детектор ізольовано від «кошик неактивний, бо є сценарії»)
  J("gw.push({old:null,name:'Тест-дефолт',gone:false,def:false}); drawGroups()"); pg.wait_for_timeout(100)
  i=len(R); rb=pg.locator(f'[data-gdef="{i}"]')
  if rb.count(): rb.check(); pg.wait_for_timeout(100)
  row=J(f"(()=>{{const r=document.querySelectorAll('#dgb .grow')[{i}];return {{del:r.querySelector('.x').disabled,t:r.querySelector('.x').title}}}})()")
  ok('26 В-118 порожня група з ● — кошик неактивний, підказка «спершу позначте іншу»', row['del'] and 'позначте іншу' in row['t'], str(row))
  pg.click('#dgApply'); pg.wait_for_timeout(200); t=TXT('#toast')
  ok('27 В-118 тост називає новий дефолт', 'Тест-дефолт' in t, t)
  g=newsc(); ok('28 В-118 новий після зміни → «Тест-дефолт»', g=='Тест-дефолт', g); drop_new()
  # 29 В-118 перейменування дефолту — дефолт іде за групою
  R=groups_dlg(); k=[r['n'] for r in R].index('Тест-дефолт') if 'Тест-дефолт' in [r['n'] for r in R] else -1
  if k>=0: pg.fill(f'[data-gi="{k}"]','Тест-2'); pg.click('#dgApply'); pg.wait_for_timeout(200)
  else: J("document.querySelector('#dg').close()")
  g=newsc(); ok('29 В-118 перейменована група-дефолт лишається дефолтом', g=='Тест-2', g); drop_new()
  go(pg)
  # 30–31 В-119 / Н9 · Н10 орієнтир не бреше
  pg.click('.scenario-item[data-id="1"]'); pg.wait_for_timeout(150)
  J("set('bv', []); drawEditor()"); pg.wait_for_timeout(150)
  p0=TXT('.pot b'); pub=J("!document.querySelector('#pub').disabled")
  ok('30 В-119/Н9 порожній ідеальний набір → «—» (Н10: публікація не блокується — за задумом)', p0=='—' and pub, f'{p0} · pub={pub}')
  J("set('bv', cur(st.sel).order.slice()); drawEditor()"); pg.wait_for_timeout(150); p1=TXT('.pot b')
  ok('31 В-119 ідеальний = замовлення → «0 ₴»', p1=='0 ₴', p1)
  # 32 В-126 / Н11 чернетка + попередження → крапка warn
  J("set('bv', []); drawEditor()"); pg.wait_for_timeout(150)
  d=J("document.querySelector('.scenario-item[data-id=\"1\"] .dot').className")
  ok('32 В-126/Н11 чернетка + ⚠ → крапка warn', d.split()==['dot','warn'], d)
  go(pg)
  # 33 В-120 ЗФ-набір підписано
  pg.click('.scenario-item[data-id="1"]'); pg.wait_for_timeout(150); pg.check('[data-k=hint]'); pg.wait_for_timeout(150)
  H=J("[...document.querySelectorAll('.hset-h')].map(x=>x.textContent)")
  ok('33 В-120 набір не за правилом — «у орієнтир не входить», правило — без', len(H)==2 and 'у орієнтир не входить' in H[1] and 'не входить' not in H[0], str(H))
  pg.screenshot(path='s83_pv_1920.png', clip=J("(()=>{const r=document.querySelector('.pv').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:Math.min(r.height,1000)}})()"))
  # 34–37 по ширинах: В-121 · В-124 · В-125/Н12 · В-123
  for w,h in ((1920,1080),(1536,864),(1280,800)):
    pg.set_viewport_size({'width':w,'height':h}); pg.wait_for_timeout(200)
    ox=J("getComputedStyle(document.querySelector('.pv')).overflowX")
    ok(f'34 В-121 .pv overflow-x hidden · {w}', ox=='hidden', ox)
    gp=J("(()=>{const a=document.querySelector('#delSc').getBoundingClientRect(),b=document.querySelector('#undo').getBoundingClientRect();return {gap:Math.round(b.left-a.right),row:Math.abs(a.top-b.top)<2}})()")
    ok(f'35 В-124 розрив «Видалити» ↔ «Скасувати» ≥24px · {w}', gp['gap']>=24 or not gp['row'], str(gp))
    J("toast('Перевірка тоста')"); pg.wait_for_timeout(250); J("(m=>m.scrollTop=m.scrollHeight)(document.querySelector('.v2 main')||document.scrollingElement)"); pg.wait_for_timeout(200)
    ov=J("(()=>{const t=document.querySelector('#toast').getBoundingClientRect();return [...document.querySelectorAll('.editor .pos, .editor .in, .editor .msg')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.bottom>t.top&&r.top<t.bottom&&r.right>t.left&&r.left<t.right}).length})()")
    ok(f'36 В-125/Н12 тост унизу сторінки не накриває даних редактора · {w}', ov==0, f'перекрито {ov}')
    if w==1280: pg.screenshot(path='s83_toast_1280.png')
    J("(document.querySelector('.v2 main')||document.scrollingElement).scrollTop=0"); pg.wait_for_timeout(2600)
  pg.set_viewport_size({'width':1920,'height':1080}); pg.wait_for_timeout(200)
  bd=lambda s: J(f"(()=>{{const c=getComputedStyle(document.querySelector({json.dumps(s)}));return c.borderTopWidth+' '+c.borderTopStyle+' '+c.borderTopColor+' '+c.backgroundColor}})()")
  base_=bd('#undo'); J("openGroups()"); pg.wait_for_timeout(150); a_=bd('#dg .dg-f [data-dgcancel]')
  # 37 В-122 «i» в діалозі груп: відкривається і видно поверх діалогу
  ib=pg.locator('#dg [popovertarget=i-grp]')
  if ib.count():
    ib.click(); pg.wait_for_timeout(200)
    vis=J("(()=>{const t=document.querySelector('#i-grp');if(!t.matches(':popover-open'))return 'закрите';const r=t.getBoundingClientRect();const e=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return (t.contains(e)?'видно':'накрите')+' '+Math.round(r.width)+'×'+Math.round(r.height)+' '+(r.right<=innerWidth&&r.bottom<=innerHeight&&r.x>=0&&r.y>=0?'в екрані':'за краєм')})()")
    pg.screenshot(path='s83_grp_i_1920.png')
  else: vis='кнопки немає'
  ok('37 В-122 «i» груп відкривається, видно поверх діалогу, в екрані', vis.startswith('видно') and 'в екрані' in vis, vis)
  J("document.querySelector('#i-grp')?.hidePopover?.()"); pg.wait_for_timeout(100); pg.screenshot(path='s83_grp_dlg_1920.png'); J("document.querySelector('#dg').close()")
  J("ask('Т','т','Так',()=>{})"); pg.wait_for_timeout(150); c_=bd('#dcNo'); J("document.querySelector('#dc').close()")
  ok('38 В-123 обидва «Скасувати» в діалогах = «Скасувати» головного екрана', a_==base_ and c_==base_, f'головний {base_} · групи {a_} · підтвердж. {c_}')
  pg.locator('.ed-head').screenshot(path='s83_head_1920.png'); pg.locator('#items').screenshot(path='s83_list_1920.png')
  # заміри без вироку (відкладені вироки, щаблі 9·10) — Н13 · Н14
  pg.set_viewport_size({'width':1536,'height':864}); pg.wait_for_timeout(200)
  pg.click('.seg [data-view=pv]'); pg.wait_for_timeout(150)
  M13=J("Math.round(document.querySelector('.pv').getBoundingClientRect().width)")
  pg.click('.seg [data-view=form]'); pg.wait_for_timeout(100)
  pg.set_viewport_size({'width':1920,'height':1080}); pg.wait_for_timeout(150)
  J("set('title','Дуже довга назва сценарію, яку Оля могла б написати, коли хоче описати ситуацію повністю, з усіма подробицями клієнта і його скарг'); drawEditor()"); pg.wait_for_timeout(150)
  M14=J("Math.round(document.querySelector('.ed-head').getBoundingClientRect().height)")
  print('ЗАМІР Н13 · 1536 ширина прев’ю', M13, 'px · ЗАМІР Н14 · шапка при довгій назві', M14, 'px')
  ok('pageerror 0', not E, str(E))
  b.close()
for n,s,note in V: print(s,n,'·',note)
