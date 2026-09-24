# s86_pub_stub_v2.py · детектор D2 крок 5 — публікація з острова КНОПКОЮ, на заглушках GitHub і воркера (корінь під ?a2v2)
# живе доки: D2 крок 8 (SPEC, П116) — далі в archive/stand. v1 (виклик publish() з рушія, крок 5.1) → archive/stand (S86).
# Мережа — заглушки зі станом: api.github.com віддає файли репо (sha stub-0), воркер перехоплює тіло, «комітить» його в
# заглушку (sha stub-1) і відповідає «Збережено». Нічого не пишеться. Шлях Олі: вхід → звірка сама → правки →
# «Опублікувати» без коду → смуга з полем коду → код + Enter → тост → нова правка просить звірку → «Звірити ще раз».
# Далі окремими сторінками: застаріла сторінка (stale) і чужий коміт між входом і записом (conflict); кадр смуги 1280. Сценарій: новий (поля з #2, номер 9876) · #2 фраза → 5555 ·
# настрій власний (дубль настрою — помилка правил) · #36 cats без nose (main мусить стати pain) · #21 лише назва (main мусить лишитись throat) · #43 видалено.
# Очікувано на X107: усі ✓. Негативний контроль — X106 (4254b656): кнопка вимкнена (Р1) → ✗ з першого кроку запису.
# Запуск: python3 s86_pub_stub_v2.py <корінь AE з білдом index.html>
import sys, json, re, base64, pathlib, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright
AE=pathlib.Path(sys.argv[1]).resolve(); V=[]
class Q(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*a): pass
srv=socketserver.ThreadingTCPServer(('127.0.0.1',0),functools.partial(Q, directory=str(AE))); srv.daemon_threads=True
threading.Thread(target=srv.serve_forever,daemon=True).start()
U=f'http://127.0.0.1:{srv.server_address[1]}/?a2v2'
FILE=json.loads((AE/'data/scenarios.json').read_text(encoding='utf-8'))
CORS={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'GET,POST,OPTIONS'}
CAP=[]; REPO={'data/scenarios.json':[(AE/'data/scenarios.json').read_bytes(),'stub-0'], 'data/catalog.json':[(AE/'data/catalog.json').read_bytes(),'cat-0']}
def gh(route):
  path='data/scenarios.json' if 'scenarios.json' in route.request.url else 'data/catalog.json'
  raw,sha=REPO[path]
  route.fulfill(status=200, headers=CORS, content_type='application/json',
    body=json.dumps({'sha':sha,'content':base64.b64encode(raw).decode()}))
def wk(route):
  if route.request.method=='OPTIONS': return route.fulfill(status=204, headers=CORS)
  body=json.loads(route.request.post_data); CAP.append(body)
  if route.request.headers.get('x-ae-edit-code')!='stub': return route.fulfill(status=403, headers=CORS, content_type='application/json', body=json.dumps({'text':'Код не той.'}))
  REPO['data/scenarios.json']=[json.dumps(body['scenarios'],ensure_ascii=False).encode(),'stub-1']
  route.fulfill(status=200, headers=CORS, content_type='application/json',
    body=json.dumps({'saved':'data/scenarios.json','text':'Збережено.','out':[]}))
def ok(n,c,note=''): V.append((n,'✓' if c else '✗',note))
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080}); E=[]; pg.on('pageerror',lambda e:E.append(str(e)))
  pg.add_init_script("try{localStorage.setItem('ae_curator_until', String(Date.now()+36e5))}catch(_){}")
  pg.route(re.compile(r'^https://api\.github\.com/'), gh)
  pg.route(re.compile(r'^https://ae-edit\.konstandre\.workers\.dev'), wk)
  pg.goto(U); pg.wait_for_function("typeof S!=='undefined' && S.SCEN && S.SCEN.length>0 && S.P", timeout=15000)
  J=pg.evaluate; J("S.screen='ascen'; render()"); pg.wait_for_selector('#newSc', timeout=3000)
  SYNC="(()=>{const w=document.querySelector('#m-sync');return w?{h:w.hidden,tone:w.dataset.tone,role:w.getAttribute('role'),t:document.querySelector('#m-sync-t').textContent,l:document.querySelector('#m-sync-l').textContent,code:!document.querySelector('#m-code').hidden,again:!document.querySelector('#resync').hidden,pub:!document.querySelector('#pub').disabled}:null})()"
  def settle(): pg.wait_for_function("S.epub && S.epub.state!=='busy'", timeout=5000); pg.wait_for_timeout(150)
  try: settle(); ok('2 звірка сама на вході = ok, смуга прихована', J("S.epub.state")=='ok' and J(SYNC)['h'], str(J(SYNC)))
  except Exception as e: ok('2 звірка сама на вході = ok, смуга прихована', False, 'звірки на вході немає')
  # новий: поля з #2, власна назва й номер
  pg.click('#newSc'); pg.wait_for_timeout(150); NEW=J("st.sel")
  J("""(()=>{const s=cur('2'); for(const k of ['grp','who','character','mood','mode','cats','order','bv','bm','goal']) set(k, JSON.parse(JSON.stringify(s[k])));
       set('title','Тест публікації'); set('mood','Тестова клієнтка тримає в руках список, читає з нього позиції й уточнює ціни.'); set('open','Добрий день, замовлення 9876, заберу сьогодні.'); drawEditor();})()""")
  pg.wait_for_timeout(150)
  pill=J("document.querySelector('#state').textContent")
  why=J("(()=>{const r=runRules(null,[recOf(st.sel)]);return r.out.filter(m=>m.lvl==='err'&&/^#/.test(m.msg)).map(m=>m.msg).join('; ')})()")
  ok('1 новий із заповненими полями не «Є проблема» (main від рушія)', 'проблема' not in pill, pill+' · recOf: '+why)
  # правки
  J("st.sel='2'; drawEditor(); set('open','5555.')")
  J("st.sel='36'; drawEditor(); set('cats', cur('36').cats.filter(c=>c!=='nose'))")
  J("st.sel='21'; drawEditor(); set('title', cur('21').title+' (правка)')")
  J("S.edel['43']=true; st.sel='1'; drawEditor()")
  J("EDITKEY.code=''")
  pub_on=J("!document.querySelector('#pub').disabled"); ok('3a «Опублікувати» активна (5 змін, без проблем)', pub_on, str(J(SYNC)))
  if pub_on: pg.click('#pub')
  try: settle()
  except Exception: pass
  sy=J(SYNC); ok('3b без коду → смуга: помилка, поле коду, кнопка жива, до воркера нічого', sy and not sy['h'] and sy['tone']=='bad' and sy['role']=='alert' and sy['code'] and sy['pub'] and not CAP, str(sy))
  if sy and sy['code']:
    pg.fill('#f-code','stub'); ok('3c поле пише в EDITKEY', J("EDITKEY.code")=='stub')
    pg.press('#f-code','Enter')
    try: settle()
    except Exception: pass
    pg.wait_for_timeout(300)
  ok('3 публікація дійшла до воркера (Enter у полі коду)', len(CAP)==1, J("S.epub&&S.epub.state+' · '+S.epub.text"))
  ok('3d успіх — тост «Збережено», смуга прихована', 'Збережено' in J("document.querySelector('#toast').textContent") and J(SYNC)['h'], J("document.querySelector('#toast').textContent"))
  if CAP:
    body=CAP[0]; sc=body['scenarios']['scenarios']; byid={str(s['id']):s for s in sc}; F={str(s['id']):s for s in FILE['scenarios']}
    ok('4 записів 43 (−#43 +новий)', len(sc)==43, str(len(sc)))
    ok('5 #43 відсутній', '43' not in byid)
    ok('6 новий — останній, з назвою', str(sc[-1]['id'])==NEW and sc[-1].get('title')=='Тест публікації', f"{sc[-1].get('id')} {sc[-1].get('title')}")
    ok('7 новий no = 9876 з фрази', byid.get(NEW,{}).get('no')==9876, str(byid.get(NEW,{}).get('no')))
    ok('8 #2 фраза 5555 → no 5555', byid['2'].get('no')==5555, str(byid['2'].get('no')))
    ok('9 #36 cats без nose → main = pain', byid['36'].get('main')=='pain', str(byid['36'].get('main')))
    ok('10 #21 лише назва → main лишився throat', byid['21'].get('main')=='throat' and byid['21']['title'].endswith('(правка)'), str(byid['21'].get('main')))
    same=[k for k in F if k not in ('2','21','36','43') and json.dumps(byid.get(k),sort_keys=True,ensure_ascii=False)==json.dumps(F[k],sort_keys=True,ensure_ascii=False)]
    ok('11 незачеплені 39 — рівно файл', len(same)==39, f'{len(same)}/39')
    bad=J("(sc=>sc.filter(s=>s.no!==noOf(s.open).no || !(s.cats||[]).includes(s.main)).map(s=>s.id))", sc)
    ok('12 у всіх no = номер фрази і main ∈ cats', not bad, str(bad))
    err=J("(sc=>{const r=runRules(null, sc); return r.out.filter(m=>m.lvl==='err').map(m=>m.msg)})", sc)
    ok('13 правила на тілі — 0 помилок (як побачить воркер)', not err, '; '.join(err[:3]))
    ok('14 примітка коміту рахує 5 (новий · 3 правки · 1 видалення)', body.get('note','').endswith(' 5'), body.get('note'))
    ok('14b код їде заголовком, не тілом', 'stub' not in json.dumps(body))
    after=J("({n:S.SCEN.length, has:S.SCEN.some(s=>String(s.id)===%r), gone:!S.SCEN.some(s=>s.id===43), d:Object.keys(S.edraft).length, e:Object.keys(S.edel).length, raw:S.RAW.scn.scenarios.length, no2:S.SCEN.find(s=>s.id===2).no})" % NEW)
    ok('15 після запису сторінка = записане (S.SCEN · S.RAW · чернетка порожня)', after=={'n':43,'has':True,'gone':True,'d':0,'e':0,'raw':43,'no2':5555}, str(after))
    ok('16 острів показує новий у списку після запису', J("!!document.querySelector('.scenario-item[data-id=\"%s\"]')" % NEW) and not J("!!document.querySelector('.scenario-item[data-id=\"43\"]')"))
  if CAP:
    J("st.sel='1'; drawEditor(); set('title', cur('1').title+' ·2')"); pg.wait_for_timeout(150); sy=J(SYNC)
    ok('18 нова правка після запису → смуга «звірте», кнопка «Звірити», публікація вимкнена', not sy['h'] and sy['tone']=='busy' and sy['again'] and not sy['pub'], str(sy))
    pg.click('#resync'); settle(); sy=J(SYNC)
    ok('19 «Звірити ще раз» → звірка з новим файлом = ok, публікація жива', J("S.epub.state")=='ok' and sy['h'] and sy['pub'], J("S.epub.state")+' '+str(sy))
  # stale: у репо не те, що на сторінці
  pg2=b.new_page(viewport={'width':1920,'height':1080}); pg2.on('pageerror',lambda e:E.append(str(e)))
  pg2.add_init_script("try{localStorage.setItem('ae_curator_until', String(Date.now()+36e5))}catch(_){}")
  alt=json.loads((AE/'data/scenarios.json').read_text(encoding='utf-8')); alt['scenarios'][0]['title']+=' (чужа правка)'
  REPO['data/scenarios.json']=[json.dumps(alt,ensure_ascii=False).encode(),'stub-9']
  pg2.route(re.compile(r'^https://api\.github\.com/'), gh); pg2.route(re.compile(r'^https://ae-edit\.konstandre\.workers\.dev'), wk)
  pg2.goto(U); pg2.wait_for_function("typeof S!=='undefined' && S.SCEN && S.SCEN.length>0 && S.P", timeout=15000)
  J2=pg2.evaluate; J2("S.screen='ascen'; render()"); pg2.wait_for_selector('#newSc', timeout=3000)
  try: pg2.wait_for_function("S.epub && S.epub.state!=='busy'", timeout=5000)
  except Exception: pass
  pg2.wait_for_timeout(150); J2("set('title', cur(st.sel).title+' x')"); pg2.wait_for_timeout(150); sy=J2(SYNC)
  ok('20 застаріла сторінка → смуга помилки + «Звірити», публікація вимкнена навіть із правкою', sy and not sy['h'] and sy['tone']=='bad' and sy['again'] and not sy['pub'] and 'НЕ те' in sy['t'], str(sy))
  # conflict: вхід звірено, потім чужий коміт
  REPO['data/scenarios.json']=[(AE/'data/scenarios.json').read_bytes(),'stub-0']
  pg2.goto(U); pg2.wait_for_function("typeof S!=='undefined' && S.SCEN && S.SCEN.length>0 && S.P", timeout=15000)
  J2("S.screen='ascen'; render()"); pg2.wait_for_selector('#newSc', timeout=3000)
  try: pg2.wait_for_function("S.epub && S.epub.state==='ok'", timeout=5000)
  except Exception: pass
  J2("EDITKEY.code='stub'; set('title', cur(st.sel).title+' y')"); pg2.wait_for_timeout(150)
  REPO['data/scenarios.json']=[json.dumps(alt,ensure_ascii=False).encode(),'stub-7']; n0=len(CAP)
  if J2("!document.querySelector('#pub').disabled"): pg2.click('#pub')
  try: pg2.wait_for_function("S.epub && S.epub.state!=='busy'", timeout=5000)
  except Exception: pass
  pg2.wait_for_timeout(150); sy=J2(SYNC)
  ok('21 чужий коміт між входом і записом → конфлікт, рядок «Розійшлись», до воркера нічого', sy and sy['tone']=='bad' and 'Розійшлись' in sy['l'] and len(CAP)==n0, str(sy))
  pg2.set_viewport_size({'width':1280,'height':900}); pg2.wait_for_timeout(200)
  m=J2("(()=>{const w=document.querySelector('#m-sync'),r=w.getBoundingClientRect();return {l:r.left,r:r.right,vw:innerWidth,over:w.scrollWidth>w.clientWidth+1}})()")
  ok('22 1280 · смуга конфлікту в кадрі, без переповнення', m['l']>=0 and m['r']<=m['vw'] and not m['over'], str(m))
  pg2.screenshot(path='s86_pub_conflict_1280.png')   # кадр вікна: скрін sticky-шапки елементом обрізається
  ok('17 без помилок сторінки', not E, '; '.join(E[:2]))
  b.close()
for n,s,note in V: print(s, n, ('· '+note) if note and s=='✗' else '')
print(f"\n{sum(v[1]=='✓' for v in V)} ✓ · {sum(v[1]=='✗' for v in V)} ✗")
