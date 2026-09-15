/* smoke_bundle_v1_4.js — гейт превʼю AE-Simulator (похідного від index.html)
 * v1_4 (Х22.4б, S43): рамка ae_bundle_v1_3 = max(1280, вікно). W4 — вузьке вікно (jsdom 1024: 1280 і масштаб),
 *   новий W4b — вікно 1920 (ширина 1920, scale(1)); нова I9 «рамка не ширшає» ловиться лише W4b.
 *   живе доки: пуш Х22 у main. Замінює v1_3.
 * v1_3 (Х22.3в): екрана імені немає — B2 чекає лише picker; новий B5 (сховище ключа) повертає I5 у спійманий.
 *   живе доки: пуш Х22 у main.
 * v1_2 (Х20.2): рамка ПК (--desktop) — W1–W4 + C6 color-scheme + I6/I7.
 *   jsdom НЕ вантажить iframe srcdoc: вміст рамки розпаковується і
 *   судиться окремо; скрипт масштабу проганяється на самій рамці.
 *   Реальне завантаження srcdoc перевіряє тільки пристрій.
 *
 * живе доки: крок 8 SPEC §13.5 не виніс вирок (tools/ репо або архів).
 * дім: Project (вручну) разом з ae_bundle_v1_2.py.
 *
 * ВИКЛИК:  NODE_PATH=<node_modules> node smoke_bundle_v1_4.js <превʼю.html> [тека] [--inject]
 *          тека за замовчуванням: /mnt/user-data/outputs/AE
 *
 * Зовнішньої заглушки fetch тут НЕМАЄ навмисно: превʼю мусить завантажитись
 * сам, тільки своєю прокладкою. Заглушка в смоуку сховала б саме те, що
 * перевіряється.
 *
 * Межа jsdom: Response у ньому немає, тож перевіряється запасна гілка
 * прокладки (обʼєкт із json/text). Гілка з рідним Response перевіряється
 * тільки на пристрої.
 *
 * --inject: вісім інʼєкцій (I6 · I8 · I9 — лише для рамки), кожна повертає одну ваду; набори ✗ мусять бути
 * непорожні й попарно різні (12.12).
 */
const {JSDOM}=require('jsdom');
const fs=require('fs'),path=require('path'),crypto=require('crypto');

const args=process.argv.slice(2);
const INJECT=args.includes('--inject');
const pos=args.filter(a=>!a.startsWith('--'));
const PREVIEW=pos[0], BASE=pos[1]||'/mnt/user-data/outputs/AE';
if(!PREVIEW){ console.log('✗ вкажіть файл превʼю'); process.exit(1); }

const MSG='Превʼю: мережа вимкнена навмисно — це знімок, не застосунок (ae_bundle_v1).';
const rd=p=>fs.readFileSync(path.join(BASE,p),'utf8');
const INDEX=rd('index.html'), RULES=rd('tools/ae_rules.js');
const sha=s=>crypto.createHash('sha256').update(Buffer.from(s,'utf8')).digest('hex');
const LITS=[...new Set([...INDEX.matchAll(/fetch\('([^']+)'\)/g)].map(m=>m[1]))];
/* Очікувані числа — з файлів цього прогону, не з памʼяті (12.1). */
const scnF=JSON.parse(rd('data/scenarios.json')).scenarios;
const catF=JSON.parse(rd('data/catalog.json')).categories;
const N_SCEN=scnF.length, N_CAT=Object.keys(catF).length;
const N_ALL=new Set(Object.values(catF).flatMap(v=>v.items.map(i=>i.c))).size;

const HEAD_RE=/\n<!--AE-BUNDLE:HEAD[\s\S]*?\/AE-BUNDLE:HEAD-->/;
const SHIM_RE=/\n?<!--AE-BUNDLE:SHIM--><script>[\s\S]*?<\/script><!--\/AE-BUNDLE:SHIM-->/;
const FRAME_RE=/<iframe id="ae-frame"[^>]*? srcdoc="([^"]*)"><\/iframe>/;
const unesc=s=>s.replace(/&quot;/g,'"').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
const esc=s=>s.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const isFrame=h=>/<!--AE-BUNDLE:FRAME/.test(h);
const unpack=h=>{ const m=h.match(FRAME_RE); return m?unesc(m[1]):''; };
const pack=(h,inner)=>h.replace(FRAME_RE,(m,x)=>m.replace(x,()=>esc(inner)));
const RULES_RE=/<!--AE-BUNDLE:RULES--><script>([\s\S]*?)<\/script><!--\/AE-BUNDLE:RULES-->/;

function snapOf(html){
  const m=html.match(/var SNAP=(\{[\s\S]*?\});var MSG=/);
  return m?JSON.parse(m[1]):null;
}

async function boot(html,url){
  const dom=new JSDOM(html,{runScripts:'dangerously',url,
    beforeParse(w){ w.scrollTo=()=>{}; w.HTMLElement.prototype.scrollIntoView=()=>{}; }});
  const w=dom.window;
  for(let i=0;i<60;i++){
    await new Promise(r=>setTimeout(r,50));
    if(w.document.querySelector('.err')) break;
    try{ if(w.eval('S.screen')) break; }catch(e){}
  }
  return w;
}

async function frameChecks(fr,t){
  const inner=unpack(fr);
  t('W1','рамка несе превʼю в iframe srcdoc (вміст — повний документ зі шапкою)',
    inner.startsWith('<!doctype html>') && /AE-BUNDLE:HEAD/.test(inner));
  t('W2','рамка: viewport device-width + color-scheme light',
    /<meta name="viewport" content="width=device-width, initial-scale=1">/.test(fr) &&
    /<meta name="color-scheme" content="light">/.test(fr));
  const b=Buffer.from(fr,'utf8').indexOf('<meta charset');
  t('W3','рамка: meta charset у перших 1024 байтах', b>=0 && b<1024);
  const d=new JSDOM(fr,{runScripts:'dangerously',url:'file:///var/mobile/AE_preview.html'});
  const w=d.window, f=w.document.getElementById('ae-frame'), s=Math.min(1,w.innerWidth/1280);
  t('W4','вузьке вікно '+w.innerWidth+': iframe 1280 px · scale('+s+') · висота = екран/масштаб',
    w.innerWidth<1280 && f && f.style.width==='1280px' && f.style.transform==='scale('+s+')' &&
    Math.abs(parseFloat(f.style.height)-w.innerHeight/s)<0.5);
  const d2=new JSDOM(fr,{runScripts:'dangerously',url:'file:///var/mobile/AE_preview.html',
    beforeParse(win){ Object.defineProperty(win,'innerWidth',{value:1920,configurable:true}); }});
  const w2=d2.window, f2=w2.document.getElementById('ae-frame');
  t('W4b','вікно 1920: iframe 1920 px · scale(1) · висота = екран (рамка ширшає разом із вікном)',
    f2 && f2.style.width==='1920px' && f2.style.transform==='scale(1)' &&
    Math.abs(parseFloat(f2.style.height)-w2.innerHeight)<0.5);
  const paper=(INDEX.match(/--paper:\s*(#[0-9A-Fa-f]{3,8})/)||[])[1];
  const bg=w.document.getElementById('ae-bg');
  const css=[...w.document.querySelectorAll('style')].map(x=>x.textContent).join('');
  t('W5','фон — власний шар і рамка кольором --paper з index.html ('+paper+'), не body',
    paper && bg && css.includes('#ae-bg{position:fixed;top:0;right:0;bottom:0;left:0;background:'+paper+'}') &&
    css.includes('background:'+paper+'}') && css.split('background:'+paper).length===3);
  return inner;
}

async function run(html){
  const R=[]; const t=(id,name,ok)=>R.push({id,name,ok:!!ok});
  if(isFrame(html)) html=await frameChecks(html,t);

  /* ── А · будова файла ─────────────────────────────────────── */
  const head=(html.match(HEAD_RE)||[''])[0];
  t('A1','шапка AE-BUNDLE:HEAD стоїть до першого <script', head && html.indexOf(head)<html.indexOf('<script'));
  t('A2','шапка каже «НЕ РЕДАГУВАТИ» і називає дім', /НЕ РЕДАГУВАТИ/.test(head) && /дім коду — index\.html/.test(head));
  t('A3','sha256 index.html у шапці = поточний index.html (превʼю не протухло)', head.includes(sha(INDEX)+'  index.html'));
  t('A4','у превʼю немає <script src', !/<script[^>]+src=/.test(html));
  t('A5','meta charset у перших 1024 байтах', Buffer.from(html,'utf8').indexOf('<meta charset')>=0 && Buffer.from(html,'utf8').indexOf('<meta charset')<1024);
  t('A6','title починається з [превʼю]', /<title>\[превʼю\] /.test(html));
  const rm=html.match(RULES_RE);
  t('A7','вшитий rules = tools/ae_rules.js байт-у-байт', rm && rm[1]===RULES);
  const back=html.replace(HEAD_RE,'').replace(SHIM_RE,'').replace('<title>[превʼю] ','<title>')
                 .replace(RULES_RE,'<script src="tools/ae_rules.js"></script>');
  t('A8','похідність: превʼю без прокладки = index.html байт-у-байт', back===INDEX);
  const snap=snapOf(html)||{};
  t('A9','кожен fetch(\'…\')-літерал index.html має місце у знімку ('+LITS.length+')', LITS.length>0 && LITS.every(p=>p in snap));
  t('A10','кожен файл знімка = файл у теці (знімок актуальний)', Object.keys(snap).length>0 && Object.keys(snap).every(p=>snap[p]===rd(p)));

  /* ── Б · запуск на двох origin ────────────────────────────── */
  for(const [tag,url] of [['https','https://preview.test/'],['file','file:///var/mobile/AE_preview.html']]){
    const w=await boot(html,url);
    const err=w.document.querySelector('.err');
    t('B1-'+tag,'boot без екрана помилки ['+url.split(':')[0]+']', !err);
    let scr=null,sc=-1,ca=-1,al=-1;
    try{ scr=w.eval('S.screen'); sc=w.eval('S.SCEN.length'); ca=w.eval('Object.keys(S.CAT).length'); al=w.eval('Object.keys(S.ALL).length'); }catch(e){}
    t('B2-'+tag,'стартовий екран picker (є: '+scr+')', scr==='picker');
    t('B3-'+tag,'сценаріїв '+sc+' = '+N_SCEN+' у файлі', sc===N_SCEN);
    t('B4-'+tag,'категорій '+ca+' · позицій '+al+' = '+N_CAT+' · '+N_ALL+' у файлі', ca===N_CAT && al===N_ALL);
    /* B5 (v1_3): до Х22.3в boot читав імʼя зі сховища, і I5 ловився стартом. Екрана імені більше немає —
       сховище тепер чіпає лише ключ моделі (кураторський екран). Перевіряємо його прямо. */
    let kv=false; try{ kv=w.eval("KEY.set('gsk_t'); const v=KEY.get(); KEY.set(''); v==='gsk_t'"); }catch(e){}
    t('B5-'+tag,'сховище живе: ключ моделі пишеться й читається', kv===true);
    if(tag==='https'){
      t('C1','window.fetch — прокладка (__aeShim)', w.fetch && w.fetch.__aeShim===true);
      const rej=async (u,o)=>{ try{ await w.fetch(u,o); return 'RESOLVED'; }catch(e){ return e.message; } };
      t('C2','чужа адреса відхилена САМЕ повідомленням прокладки', (await rej('https://example.com/x'))===MSG);
      /* адреса з файла, не зі стану сторінки: під I1 boot падає, S.cfg=null,
         і смоук упав би сам, сховавши решту тверджень (S36 §2.2) */
      const ep=JSON.parse(rd('config.json')).editEndpoint;
      t('C3','POST на editEndpoint відхилено (превʼю не публікує)', ep && (await rej(ep,{method:'POST',body:'{}'}))===MSG);
      t('C4','POST навіть на шлях зі знімка відхилено (тільки GET)', (await rej('config.json',{method:'POST'}))===MSG);
      let cats=-1; try{ cats=Object.keys((await (await w.fetch('data/catalog.json')).json()).categories).length; }catch(e){}
      t('C5','GET зі знімка віддає дані ('+cats+' категорій)', cats===N_CAT);
      const cs=w.document.querySelector('meta[name="color-scheme"]');
      t('C6','сторінка оголошує color-scheme: light (переглядач у темній темі)', cs && cs.content==='light');
    }
  }
  return R;
}

const INJ={
  I1:['файл прибрано зі знімка', h=>h.replace(/var SNAP=(\{[\s\S]*?\});var MSG=/,(m,j)=>{
        const o=JSON.parse(j); delete o['prompts/judge.md'];
        return 'var SNAP='+JSON.stringify(o).replace(/</g,'\\u003c')+';var MSG='; })],
  I2:['прокладка пропускає мережу', h=>h.replace('return Promise.reject(new Error(MSG));','return Promise.resolve(resp(""));')],
  I3:['шапку знято', h=>h.replace(HEAD_RE,'')],
  I4:['превʼю відредаговано руками', h=>h.replace('Дані не завантажились','Дані не завантажилися')],
  I5:['сховище в памʼяті знято', h=>h.replace('try{window.localStorage.getItem("__ae");}','try{}')],
  I6:['рамка без масштабу', h=>h.replace('f.style.transform="scale("+s+")";',''), 'frame'],
  I9:['рамка не ширшає (стара формула v1_2)', h=>h.replace('w=Math.max(W,iw)','w=W'), 'frame'],
  I8:['шар фону знято', h=>h.replace('<div id="ae-bg"></div>\n',''), 'frame'],
  I7:['прокладка оголошує темну схему', h=>h.replace('cs.content="light"','cs.content="dark"')],
};

function report(R,label){
  if(label) console.log('\n── '+label+' ──');
  for(const r of R) console.log((r.ok?'  ✓ ':'  ✗ ')+r.id+' · '+r.name);
  const ok=R.filter(r=>r.ok).length, bad=R.length-ok;
  console.log('─── ПІДСУМОК: ✓ '+ok+' · ✗ '+bad+' ───');
  return R.filter(r=>!r.ok).map(r=>r.id);
}

(async()=>{
  const html=fs.readFileSync(PREVIEW,'utf8');
  if(!INJECT){
    const bad=report(await run(html));
    process.exit(bad.length?1:0);
  }
  const sets={}; let fail=false;
  for(const [k,[name,f,where]] of Object.entries(INJ)){
    if(where==='frame' && !isFrame(html)){ console.log('  · '+k+' пропущено — превʼю без рамки'); continue; }
    const h= isFrame(html) && where!=='frame' ? pack(html,f(unpack(html))) : f(html);
    if(h===html){ console.log('✗ '+k+' · інʼєкція не знайшла цілі — сторож мовчить'); fail=true; continue; }
    const R=await run(h); const bad=R.filter(r=>!r.ok).map(r=>r.id);
    sets[k]=bad.join(',');
    console.log((bad.length?'  ✓ ':'  ✗ ')+k+' · '+name+' → ✗'+bad.length+(bad.length?' ['+bad.join(' ')+']':' — НЕ СПІЙМАНО'));
    if(!bad.length) fail=true;
  }
  const vals=Object.values(sets), uniq=new Set(vals).size===vals.length;
  console.log((uniq?'  ✓':'  ✗')+' набори відмов попарно різні');
  console.log('─── INJECT: '+(fail||!uniq?'✗ є непійманe':'✓ усі '+Object.keys(sets).length+' спіймано')+' ───');
  process.exit(fail||!uniq?1:0);
})();
