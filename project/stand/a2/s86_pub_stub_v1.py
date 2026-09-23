# s86_pub_stub_v1.py · детектор D2 крок 5.1 — що саме їде у файл при публікації (В-151), на КОРЕНІ під ?a2v2
# живе доки: D2 крок 8 (SPEC, П116) — далі в archive/stand; кроки 5.2–5.3 беруть його ж (публікацію кличе кнопка).
# Мережа — заглушки: api.github.com віддає файли репо з фіктивним sha (звірка loadSnap = 'ok'), воркер перехоплює тіло
# і відповідає «Збережено». Нічого не пишеться. Сценарій: новий (поля з #2, номер 9876) · #2 фраза → 5555 ·
# настрій власний (дубль настрою — помилка правил) · #36 cats без nose (main мусить стати pain) · #21 лише назва (main мусить лишитись throat) · #43 видалено.
# Очікувано на X105: усі ✓. Негативний контроль — X104 (51bd05df): ✗ на новому, видаленому, main і стані після запису.
# Запуск: python3 s86_pub_stub_v1.py <корінь AE з білдом index.html>
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
CAP=[]
def gh(route):
  path='data/scenarios.json' if 'scenarios.json' in route.request.url else 'data/catalog.json'
  route.fulfill(status=200, headers=CORS, content_type='application/json',
    body=json.dumps({'sha':'stub-'+path,'content':base64.b64encode((AE/path).read_bytes()).decode()}))
def wk(route):
  if route.request.method=='OPTIONS': return route.fulfill(status=204, headers=CORS)
  CAP.append(json.loads(route.request.post_data))
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
  J("EDITKEY.code='stub'"); J("loadSnap()"); pg.wait_for_function("S.epub && S.epub.state!=='busy'", timeout=5000)
  ok('2 звірка на заглушці = ok', J("S.epub.state")=='ok', J("S.epub.state+' · '+S.epub.text"))
  J("publish()"); pg.wait_for_function("S.epub && S.epub.state!=='busy'", timeout=5000); pg.wait_for_timeout(300)
  ok('3 публікація дійшла до воркера', len(CAP)==1, J("S.epub.state+' · '+S.epub.text"))
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
    after=J("({n:S.SCEN.length, has:S.SCEN.some(s=>String(s.id)===%r), gone:!S.SCEN.some(s=>s.id===43), d:Object.keys(S.edraft).length, e:Object.keys(S.edel).length, raw:S.RAW.scn.scenarios.length, no2:S.SCEN.find(s=>s.id===2).no})" % NEW)
    ok('15 після запису сторінка = записане (S.SCEN · S.RAW · чернетка порожня)', after=={'n':43,'has':True,'gone':True,'d':0,'e':0,'raw':43,'no2':5555}, str(after))
    ok('16 острів показує новий у списку після запису', J("!!document.querySelector('.scenario-item[data-id=\"%s\"]')" % NEW) and not J("!!document.querySelector('.scenario-item[data-id=\"43\"]')"))
  ok('17 без помилок сторінки', not E, '; '.join(E[:2]))
  b.close()
for n,s,note in V: print(s, n, ('· '+note) if note and s=='✗' else '')
print(f"\n{sum(v[1]=='✓' for v in V)} ✓ · {sum(v[1]=='✗' for v in V)} ✗")
