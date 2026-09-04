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
/* Третій інжект: знімаємо зріз блоку «для клієнта» — parseChars бере запис
   цілком. Носій при цьому цілий, поле в даних ціле, промпт збирається без
   жодної помилки; у нього просто починає текти рядок ризику. Це найтихіший
   із можливих дефектів характеру, тому він і відтворюється. */
if(INJECT) html=html.replace(
  "    const forClient = slice(m[2],'для клієнта');",
  "    const forClient = m[2].trim();");
/* Пʼятий інжект, дзеркало третього з іншого боку носія: знімаємо зріз
   блоку «ризик». Запис іде в судді цілком, разом з описом «для клієнта»,
   тобто приціл судді підмінюється текстом, написаним для клієнта.
   Міряється на РОЗІБРАНОМУ (S.P.risks), недосяжно для шостого інжекта,
   який ламає підстановку. */
if(INJECT) html=html.replace(
  "    const risk      = slice(m[2],'ризик');",
  "    const risk      = m[2].trim();");
/* Шостий інжект: губимо ключ risk у fill() судді. Носій прочитано,
   розібрано на два зрізи, звірено з даними — і половина нікуди не
   передана. Міряється на ЗІБРАНОМУ промпті судді. */
if(INJECT) html=html.replace("    character: sc.character, risk: S.P.risks[sc.character],\n", "    character: sc.character,\n");
/* Четвертий інжект: губимо ключ у fill(). Дзеркальна половина: носій
   прочитано, розібрано, звірено з даними — і нікуди не передано. */
if(INJECT) html=html.replace("    character: S.P.chars[sc.character],\n", "");

const local=f=>{
  let t=fs.readFileSync(path.join(BASE,f),'utf8');
  /* Інжект під твердження «орієнтира в промпті клієнта немає»: підкидаємо
     назад рядок, який зняв Р1. Ламаємо саме текст промпта, а не перевірку —
     buildSystem досі передає ключ pot, тому вікно {{pot}} заповниться, і
     дефект відтвориться один в один. */
  if(INJECT && f.indexOf('client.md')>=0 && f.indexOf('parts')<0)
    t += '\nОрієнтир для цього сценарію — приріст близько {{pot}} ₴.\n';
  /* Другий інжект: виймаємо step зі списку required схеми turn. Саме ця
     половина губиться найлегше — поле лишається в properties, виглядає
     присутнім, а strict-режим без required його не вимагає, і модель
     мовчки перестає його віддавати. */
  /* Сьомий інжект: зносимо з промпта судді розділ критеріїв. Найтихіший
     дефект словника: промпт збереться, суддя відповість, і оцінюватиме
     знову «на враження» — рівно тим, від чого крок 2б і рятує. Ламаємо
     текст, що доїжджає в застосунок, а не файл на диску: гейт ганяє
     артефакт, який поїде (12.12). Ціль — заголовок з нового рядка, а не
     згадка назви: перша редакція цього інжекта збігалася з коментарем у
     шапці й зносила півфайла разом зі СЦЕНАРІЄМ і вікнами. Червоне було,
     але не з тієї причини, яка перевіряється. */
  if(INJECT && f.indexOf('judge.md')>=0)
    t = t.replace(/\nЗА ЧИМ ОЦІНЮВАТИ\n[\s\S]*?(?=\nЯк оцінювати)/, '\n');
  if(INJECT && f.indexOf('config.json')>=0)
    t = t.replace(/,\s*"step"\s*\n(\s*)\]/, '\n$1]');
  return t;
};
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
      : {reply:'Добре, беру.', cart:[VALID,'НЕІСНУЮЧИЙ_КОД'], ended:false, endReason:'', feedback:'', step:'цікавиться'};
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
  /* Ім'я цього твердження змінене у 2а-III. Доти воно звалось «характер
     клієнта підставлено», а міряло who+mood. Після появи поля `character`
     одне слово означало б два різні предмети, і розходження між ними
     проходило б непоміченим. */
  T('хто і настрій підставлені', sys.includes(sc.who) && sys.includes(sc.mood));
  T('перша репліка підставлена', sys.includes(sc.open));
  T('номер замовлення підставлено', sys.includes(String(sc.no)));
  const pool=sc.cats.flatMap(k=>S.CAT[k]);
  T('асортимент категорії у промпті ('+pool.length+' поз.)', pool.every(i=>sys.includes(i.c+' | '+i.n)));
  const alien=Object.values(S.ALL).find(i=>!pool.includes(i));
  T('чужого асортименту в промпті немає', !sys.includes(alien.c+' | '+alien.n));
  /* ── Р1 (S12 §1.3) · клієнт більше не суддя ───────────────────────────
     Це твердження ІНВЕРТОВАНЕ. Доти воно вимагало, щоб орієнтир приросту
     БУВ у системному промпті клієнта, — тобто гейт кодував рівно той
     дефект, який Р1 знімає: клієнт судив розмову за числом, якого не мав
     бачити. Тримаємо не формулювання «близько N ₴», а межу знань: жодної
     гривні в промпті клієнта. Символ ₴ не може прийти ні з даних (перевірено:
     назв позицій, who/mood/mode/open із гривнею — нуль; у goal вона є, але
     goal у клієнта не заходить), ні з client.parts.md. Отже поява гривні
     означає рівно одне — її вписали назад у текст промпта. */
  T('орієнтира приросту в промпті клієнта немає',
    !/₴/.test(sys) && !/орієнтир/i.test(sys) && !/приріст/i.test(sys));

  /* ── Р2 · щабель відкритості ────────────────────────────────────────
     Три половини, безглузді поодинці: слово в схемі, слово в промпті,
     слово в історії. Схема без промпта дасть модель, що вигадує щабель
     навмання; промпт без схеми — поле, яке strict не пропустить; обидва
     без третьої — рух, якого ніде не видно, тобто рівно те, від чого Р2
     і мав позбавити. */
  const turnSchema = S.cfg.schemas.turn.schema;
  T('схема turn знає поле step', !!turnSchema.properties.step);
  T('step у required, а не лише в properties',
    (turnSchema.required||[]).indexOf('step')>=0);
  T('щаблів рівно пʼять', (turnSchema.properties.step.enum||[]).length===5);
  T('усі пʼять щаблів названі в промпті клієнта',
    (turnSchema.properties.step.enum||[]).every(s=>sys.includes(s)));
  T('щабель не тече в репліку', /не пояснюється вголос/.test(sys));

  /* ── Р4 · характер клієнта (2а-III) ──────────────────────────────────
     Носій, дані і промпт — три половини, безглузді поодинці. Носій без
     поля в даних нікому не адресований; поле без носія дає порожній
     характер; обидва без підстановки — текст, який модель не побачить.
     Рахуємо ПІСЛЯ розбору (12.12-г): заголовків у файлі може бути скільки
     завгодно, у промпт піде рівно те, що пережило regex. */
  const CH = fs.readFileSync(path.join(BASE,'prompts/characters.md'),'utf8');
  const declared = (CH.match(/\n## /g)||[]).length;
  T('носій розібрано, записів девʼять', Object.keys(S.P.chars).length===9);
  T('розібрано рівно стільки, скільки оголошено ('+declared+')',
    Object.keys(S.P.chars).length===declared);
  T('усі 43 сценарії мають character', S.SCEN.every(s=>!!s.character));
  T('кожен character має запис у носії',
    S.SCEN.every(s=>!!S.P.chars[s.character]));
  const dist={};
  for(const s of S.SCEN) dist[s.character]=(dist[s.character]||0)+1;
  T('розподіл збігається з бібліотекою §5 (6·4·5·3·4·9·6·3·3)',
    JSON.stringify(Object.values(dist).sort((a,b)=>a-b))==='[3,3,3,4,4,5,6,6,9]');

  /* Межа знань клієнта, друга по рахунку після гривні. Носій — єдиний файл,
     де поруч лежить текст ДЛЯ моделі і текст ПРО модель. Рядок «ризик»
     описує типову помилку фармацевта з цим характером; потрапивши в промпт,
     він скаже клієнтові, чого від нього чекають, — і клієнт перестане бути
     тим, кого відтворює. Тримаємо не формулювання, а факт відсутності. */
  const risk = (CH.match(new RegExp('## '+sc.character+'[\\s\\S]*?### ризик\\s*([\\s\\S]*?)(?=\\n## |$)'))||[,''])[1].trim();
  const riskHead = risk.split('\n')[0];
  const block = S.P.chars[sc.character];
  T('рядок ризику з носія прочитався ('+risk.length+' симв.)', risk.length>40);
  /* Міряємо РОЗІБРАНИЙ блок, а не зібраний промпт. У промпті це твердження
     не має шляху до падіння тоді, коли підстановку зламано окремо: характеру
     там немає взагалі, і «ризику немає» виходить істинним порожньо. Два
     дефекти маскували б один одного, а гейт світився б зеленим на обох. */
  T('розібраний блок не несе рядка ризику', !block.includes(riskHead));
  T('розібраний блок не несе заголовків носія', !/### (для клієнта|ризик)/.test(block));
  T('розібраний блок не несе кодів словника',
    !/\bХ-\d/.test(block) && !/\bА-\d/.test(block) && !/\bМ-\d/.test(block));
  T('характер потрапив у системний промпт', sys.includes(block));
  T('ризику в зібраному промпті немає', !sys.includes(riskHead));

  /* ── 2б · суддя: словник як критерії + характер як приціл ────────────
     Три артефакти, і твердження розкладені по них навмисно (12.12-д):
     розбір носія міряється на S.P.risks, шаблон промпта — на S.P.judge,
     підстановка — на зібраному buildJudge(). Інакше інжект, що ламає
     підстановку, прибирає предмет, який міряє твердження про розбір,
     і те стає істинним порожньо. */
  console.log('\n— суддя: словник і характер —');
  const risks = S.P.risks;
  T('носій розібрано на ризики, записів девʼять', Object.keys(risks).length===9);
  T('ризиків розібрано стільки ж, скільки описів',
    Object.keys(risks).length===Object.keys(S.P.chars).length);
  const rBlock = risks[sc.character];
  T('розібраний ризик не несе заголовків носія', !/### (для клієнта|ризик)/.test(rBlock));
  T('розібраний ризик не несе опису «для клієнта»',
    !rBlock.includes(S.P.chars[sc.character].split('\n')[0]));

  /* Шаблон судді. Міряємо S.P.judge — те, що поїде у fill, а не файл із
     диска: між ними стоїть stripComments, і саме після нього промпт стає
     тим артефактом, який побачить модель. */
  const CODE=/\n[МХА]-\d+ · /g;
  const jCodes=(S.P.judge.match(CODE)||[]).length;
  T('у шаблоні судді всі 29 пунктів словника ('+jCodes+')', jCodes===29);
  T('шаблон судді має вікно характеру', /\{\{character\}\}/.test(S.P.judge));
  T('шаблон судді має вікно ризику', /\{\{risk\}\}/.test(S.P.judge));
  T('шаблон судді забороняє коди у відповіді', /Кодів у відповіді не вживай/.test(S.P.judge));
  /* Р-2: назва характеру — закритий перелік, і його єдиний дім — носій.
     Копія назви в промпті розійшлася б із носієм рівно тоді, коли запис
     перейменують (12.11-а). Перевірка на всіх девʼятьох, не на одному. */
  T('назв характерів у тексті промпта судді немає',
    Object.keys(S.P.chars).every(n=>!S.P.judge.includes(n)));
  /* Дзеркало: клієнт кодів не бачить узагалі — ні з носія, ні з промпта. */
  T('у промпті клієнта кодів словника немає',
    !/\bХ-\d/.test(sys) && !/\bА-\d/.test(sys) && !/\bМ-\d/.test(sys));

  /* Зібраний промпт судді. Сценарій беремо той самий, плюс окремо —
     «поступливий»: на ньому стоять пастки, і саме там порожній приціл
     коштує найдорожче. */
  const jp = w.buildJudge(sc, [{role:'user',content:'Може, візьмете ще щось?'},
                               {role:'assistant',content:'Давайте.'}], sc.order);
  T('плейсхолдерів у промпті судді не лишилось', !/\{\{[^}]*\}\}/.test(jp));
  T('назва характеру підставлена в промпт судді', jp.includes('Характер клієнта: '+sc.character));
  T('рядок ризику підставлений у промпт судді', jp.includes(rBlock.split('\n')[0]));
  T('опис «для клієнта» в промпт судді не протік',
    !jp.includes(S.P.chars[sc.character].split('\n')[0]));
  T('критеріїв у зібраному промпті судді 29', (jp.match(CODE)||[]).length===29);
  const trap = S.SCEN.find(x=>x.character==='поступливий');
  const jt = w.buildJudge(trap, [{role:'assistant',content:'Добре, беру.'}], trap.order);
  T('на «поступливому» приціл судді не порожній',
    jt.includes(risks['поступливий'].split('\n')[0]));

  T('ae_rules вимагає поле character',
    /const REQ=\[[^\]]*'character'/.test(fs.readFileSync(path.join(BASE,'tools/ae_rules.js'),'utf8')));

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
