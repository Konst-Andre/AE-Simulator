/* AE-Simulator · смоук крок 2 — живий двигун із підробленим Groq
   node smoke_step2.js            чистий прогін
   node smoke_step2.js --inject   із підкинутим дефектом (має впасти) */
const fs=require('fs'), path=require('path');
const {JSDOM}=require('jsdom');
const BASE='/mnt/user-data/outputs/AE';
const INJECT=process.argv.includes('--inject');
let ok=0,bad=0; const T=(n,c)=>{c?(ok++,console.log('  ✓ '+n)):(bad++,console.log('  ✗ '+n))};
const sent=[];   // сюди складаємо все, що застосунок відправив «у Groq»
let VALID='zipelor';   // код, який mock кладе в чек — виставляється під обраний сценарій

let html=fs.readFileSync(BASE+'/index.html','utf8');
if(INJECT) html=html.replace("return { ...r, cart: (r.cart||[]).filter(c=>pool.has(c)) };",
                             "return r;");   // ламаємо захист від чужих кодів у чеку

const local=f=>fs.readFileSync(path.join(BASE,f),'utf8');
const dom=new JSDOM(html,{runScripts:'dangerously',url:'https://x.test/',beforeParse(w){
  w.scrollTo=()=>{}; w.HTMLElement.prototype.scrollIntoView=()=>{};
  w.fetch=(u,opt)=>{
    if(!opt){ return Promise.resolve({json:()=>Promise.resolve(JSON.parse(local(u))),
                                      text:()=>Promise.resolve(local(u))}); }
    const body=JSON.parse(opt.body); sent.push({url:u,headers:opt.headers,body});
    const isDebrief = body.response_format.json_schema.name==='shift_debrief';
    const payload = isDebrief
      ? {overall:'Загалом непогано.',mistakes:['тиснули на ціну'],strengths:['почали розмову'],
         rules:['питайте про симптом'],curator:'звернути увагу на темп'}
      : {reply:'Добре, беру.', cart:[VALID,'НЕІСНУЮЧИЙ_КОД'], ended:false, endReason:'', feedback:''};
    return Promise.resolve({ok:true,status:200,json:()=>Promise.resolve(
      {choices:[{message:{content:JSON.stringify(payload)}}]})});
  };
}});
const w=dom.window;

(async()=>{
  await new Promise(r=>setTimeout(r,350));
  const d=w.document, S=w.S;

  console.log('\n— промпти прочитано —');
  T('client.md завантажено', S.P.client.length>1000);
  T('коментарі <!-- --> зняті', !S.P.client.includes('<!--'));
  T('debrief.md завантажено', S.P.debrief.length>500);
  T('numLine з номером розпаковано', /номер \{\{no\}\}/.test(S.P.withNumber));
  T('numLine без номера розпаковано', /Номера ще немає/.test(S.P.withoutNumber));
  T('двигун живий, не заглушка', w.ENGINE.name.startsWith('Groq'));

  console.log('\n— системний промпт збирається —');
  const sc=S.SCEN.find(x=>x.no && x.cats.length===1);
  const sys=w.buildSystem(sc);
  T('плейсхолдерів не лишилось', !/\{\{\w+\}\}/.test(sys));
  T('характер клієнта підставлено', sys.includes(sc.who) && sys.includes(sc.mood));
  T('перша репліка підставлена', sys.includes(sc.open));
  T('номер замовлення підставлено', sys.includes(String(sc.no)));
  const pool=sc.cats.flatMap(k=>S.CAT[k]);
  T('асортимент категорії у промпті ('+pool.length+' поз.)', pool.every(i=>sys.includes(i.c+' | '+i.n)));
  const alien=Object.values(S.ALL).find(i=>!pool.includes(i));
  T('чужого асортименту в промпті немає', !sys.includes(alien.c+' | '+alien.n));
  T('орієнтир приросту у промпті', sys.includes('близько '+((()=>{
      const b=sc.order.reduce((a,c)=>a+S.ALL[c].b,0), v=sc.bv.reduce((a,c)=>a+S.ALL[c].b,0);
      return Math.max(1,Math.round(v-b));})())+' ₴'));

  console.log('\n— ключ —');
  w.KEY.set('gsk_test123');
  T('ключ зберігся', w.KEY.get()==='gsk_test123');

  console.log('\n— виклик моделі —');
  S.me={name:'Тест',pharmacy:'67'}; S.screen='picker'; w.render();
  VALID = S.CAT[sc.cats[0]].find(i=>!sc.order.includes(i.c)).c;
  const iCard=S.SCEN.findIndex(x=>x.id===sc.id);
  d.querySelectorAll('.card')[iCard].click();
  const ta=d.querySelector('.say textarea');
  ta.value='Добрий день! Бачу, у вас горло. Підкажу дещо дієвіше.';
  ta.dispatchEvent(new w.Event('input'));
  [...d.querySelectorAll('.btn')].find(b=>b.textContent==='Сказати').click();
  await new Promise(r=>setTimeout(r,300));

  const req=sent[sent.length-1];
  T('пішов запит на Groq', /api\.groq\.com/.test(req.url));
  T('ключ у заголовку Authorization', req.headers.Authorization==='Bearer gsk_test123');
  T('модель із config', req.body.model===S.cfg.model.name);
  /* Крок Ж-3: клієнту дали роздуми (none -> low), щоб перевірити, чи він узагалі
     реагує на аргумент. Три перевірки замість однієї шпильки:
       1) значення взагалі існує в API Qwen;
       2) ПАРНІСТЬ — роздуми рахуються в ту саму стелю токенів, тому будь-який
          effort, крім none, вимагає стелі >= 800. Це правило переживе будь-який
          підсумок експерименту;
       3) поточний канон. Повертаючи клієнта на none — повернути й цей рядок,
          інакше гейт мовчки перестане ловити випадкову зміну. */
  const eff = req.body.reasoning_effort;
  T('reasoning_effort зі списку API', ['none','default','low','medium','high'].includes(eff));
  T('парність effort/стеля: не-none вимагає >=800',
    eff==='none' || req.body.max_completion_tokens>=800);
  T('поточний канон клієнта = low (Ж-3)', eff==='low');
  T('reasoning_format = hidden', req.body.reasoning_format==='hidden');
  T('response_format — json_schema', req.body.response_format.type==='json_schema');
  T('схема strict', req.body.response_format.json_schema.strict===true);
  T('промпт пішов роллю system', req.body.messages[0].role==='system');
  T('репліка фармацевта пішла роллю user', req.body.messages[1].content.includes('дієвіше'));
  T('заборонених параметрів немає', !('top_k' in req.body) && !('min_p' in req.body));

  console.log('\n— захист від чужого коду в чеку —');
  T('відповідь клієнта в лозі', /Добре, беру/.test(d.querySelector('.log').textContent));
  T('НЕІСНУЮЧИЙ_КОД відфільтровано', !S.cart.includes('НЕІСНУЮЧИЙ_КОД'));
  T('валідний код «'+VALID+'» лишився', S.cart.includes(VALID));

  console.log('\n— розбір зміни —');
  S.shift={queue:[sc],i:0,rows:[{sc,delta:12.3,pot:20,fb:'ок'}]};
  S.screen='result'; w.render();
  await new Promise(r=>setTimeout(r,300));
  const dr=sent[sent.length-1];
  T('другий запит — розбір', dr.body.response_format.json_schema.name==='shift_debrief');
  T('дані зміни пішли в промпт', dr.body.messages[0].content.includes(sc.title));
  T('розбір відмалювався', /Загалом непогано/.test(d.body.textContent));
  T('нотатка куратору збережена', S.shift.curatorNote==='звернути увагу на темп');

  /* ── В-1а · межа знань у промптах оцінювання ──────────────────────────
   Дефект В-1: суддя приписав препарату парацетамол, якого там немає.
   Причина була не в моделі, а в дозволі: заборони не існувало ні в
   judge.md, ні в debrief.md. Шпилька тримає саме межу, а не формулювання:
   інжект підміняє її на чорний список тем, і перевірка «прив'язана до
   тексту, а не до теми» падає — бо після В-1б (діюча речовина в каталозі)
   чорний список забороняв би те, що ми самі дали. */
{
  const rd = f => fs.readFileSync(path.join(BASE, f), 'utf8');
  let J = rd('prompts/judge.md'), D = rd('prompts/debrief.md');
  if (INJECT) J = J.replace('Доки їх немає в цьому тексті', 'Ніколи');
  T('judge.md: межа знань оголошена', /Межа знань/.test(J));
  T('judge.md: межа прив\'язана до тексту, а не до теми (переживе В-1б)',
    /Доки їх немає в цьому тексті/.test(J));
  T('judge.md: глибина аргументу обмежена групою', /та сама група/.test(J));
  T('debrief.md: та сама межа', /Межа знань/.test(D) && /не називай і не здогадуйся/.test(D));

  /* В-1б-труба. Дві половини безглузді поодинці: плейсхолдер без ключа
     поїде в модель літералом «{{catalog}}», ключ без плейсхолдера — нікуди.
     Тому обидві сторони шпильки, і межа мусить згадувати список асортименту,
     інакше вона суперечить тому, що модель бачить на очі. */
  let HX = html;
  if (INJECT) HX = HX.replace(/catalog: poolOf\(sc\)[^\n]*\n/, '');
  T('judge.md: плейсхолдер асортименту на місці', /\{\{catalog\}\}/.test(J));
  T('fill() судді передає catalog', /catalog: poolOf\(sc\)/.test(HX));
  T('межа знань згадує список асортименту', /список асортименту/.test(J));
}

console.log('\n'+(bad?'✗':'✓')+' підсумок: ✓'+ok+' · ✗'+bad+(INJECT?'  [inject: очікуємо ✗]':''));
  process.exit(bad?1:0);
})().catch(e=>{console.error('ПАДІННЯ:',e.message);process.exit(2)});
