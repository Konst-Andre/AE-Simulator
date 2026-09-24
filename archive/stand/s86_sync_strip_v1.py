# s86_sync_strip_v1.py · детектор D2 крок 5.2 — смуга запису #m-sync і поле коду в острові (HTML/CSS), корінь під ?a2v2
# живе доки: крок 5.3 (JS показує смугу — перевірки переїдуть у s86_pub_stub як стани S.epub), далі archive/stand.
# Без JS смуга мусить бути прихована і не займати місця; примусово показана (обидва тони, код, рядки, кнопка, довгий
# текст) — у кадрі, без горизонтального переповнення, не накриває назву. Поле коду: password · autocomplete=off · без name ·
# порожнє значення в розмітці. Ширини 1920 · 1536 · 1280 (+ 760 — контейнерний запит шапки). Кадри — у поточну теку.
# Очікувано на X106: усі ✓. Негативний контроль — X105: ✗ «смуги немає» → вихід 2.
# Запуск: python3 s86_sync_strip_v1.py <корінь AE з білдом index.html>
import sys, pathlib, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright
AE=pathlib.Path(sys.argv[1]).resolve(); V=[]
class Q(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*a): pass
srv=socketserver.ThreadingTCPServer(('127.0.0.1',0),functools.partial(Q, directory=str(AE))); srv.daemon_threads=True
threading.Thread(target=srv.serve_forever,daemon=True).start()
U=f'http://127.0.0.1:{srv.server_address[1]}/?a2v2'
def ok(n,c,note=''): V.append((n,'✓' if c else '✗',note))
LONG='Файл змінився, поки картка була відкрита. Не збережено — інакше чужа правка зникла б мовчки. Перезавантажте сторінку.'
SHOW="""(tone=>{const w=document.querySelector('#m-sync'); w.hidden=false; w.dataset.tone=tone;
  document.querySelector('#m-sync-t').textContent=%r;
  document.querySelector('#m-sync-l').textContent='Розійшлись: #2 · #14 · #21 · #36 (новий) · #43 (зник) · #44 (новий)';
  document.querySelector('#m-code').hidden=false; document.querySelector('#resync').hidden=false;})""" % LONG
MEAS="""(()=>{const w=document.querySelector('#m-sync'), h=document.querySelector('.ed-head'), r=w.getBoundingClientRect(),
  ti=document.querySelector('#f-title').getBoundingClientRect(), i=document.querySelector('#f-code').getBoundingClientRect();
  return {l:r.left, r:r.right, vw:innerWidth, over:w.scrollWidth>w.clientWidth+1, hover:h.scrollWidth>h.clientWidth+1,
   hit:!(r.bottom<=ti.top||r.top>=ti.bottom), iw:i.width, bg:getComputedStyle(w).backgroundColor}})()"""
with sync_playwright() as p:
  b=p.chromium.launch(); E=[]
  for W in (1920,1536,1280,760):
    pg=b.new_page(viewport={'width':W,'height':1000}); pg.on('pageerror',lambda e:E.append(str(e)))
    pg.add_init_script("try{localStorage.setItem('ae_curator_until', String(Date.now()+36e5))}catch(_){}")
    pg.goto(U); pg.wait_for_function("typeof S!=='undefined' && S.SCEN && S.SCEN.length>0 && S.P", timeout=15000)
    J=pg.evaluate; J("S.screen='ascen'; render()"); pg.wait_for_selector('#newSc', timeout=3000)
    if not J("!!document.querySelector('#m-sync')"): print('✗ смуги #m-sync немає'); sys.exit(2)
    d=J("(()=>{const w=document.querySelector('#m-sync');return {h:w.getBoundingClientRect().height, disp:getComputedStyle(w).display}})()")
    ok(f'{W} · прихована без JS і не займає місця', d=={'h':0,'disp':'none'}, str(d))
    f=J("(()=>{const i=document.querySelector('#f-code');return {t:i.type, ac:i.getAttribute('autocomplete'), name:i.hasAttribute('name'), v:i.getAttribute('value'), lab:!!i.closest('label')}})()")
    ok(f'{W} · поле коду password · autocomplete=off · без name · без значення · з підписом', f=={'t':'password','ac':'off','name':False,'v':None,'lab':True}, str(f))
    for tone in ('bad','busy'):
      J(SHOW+"(%r)" % tone); pg.wait_for_timeout(120); m=J(MEAS)
      ok(f'{W} · {tone} у кадрі, без переповнення смуги й шапки, не накриває назву, поле ≥120px',
         m['l']>=0 and m['r']<=m['vw'] and not m['over'] and not m['hover'] and not m['hit'] and m['iw']>=120, str(m))
      if tone=='bad': ok(f'{W} · bad — тон помилки', m['bg']=='rgb(253, 244, 242)', m['bg'])
      else: ok(f'{W} · busy — нейтральний тон', m['bg']=='rgb(255, 255, 255)', m['bg'])
      pg.locator('.ed-head').screenshot(path=f's86_strip_{W}_{tone}.png')
    J("(()=>{const w=document.querySelector('#m-sync'); document.querySelector('#m-code').hidden=true; document.querySelector('#resync').hidden=true})()")
    ok(f'{W} · вкладені [hidden] справді ховають (кнопка й поле)', J("getComputedStyle(document.querySelector('#resync')).display==='none' && getComputedStyle(document.querySelector('#m-code')).display==='none'"))
    pg.close()
  ok('без помилок сторінки', not E, '; '.join(E[:2]))
  b.close()
for n,s,note in V: print(s, n, ('· '+note) if note and s=='✗' else '')
print(f"\n{sum(v[1]=='✓' for v in V)} ✓ · {sum(v[1]=='✗' for v in V)} ✗")
