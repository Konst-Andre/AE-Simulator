/* AE-Simulator · смоук екрана редактора даних (крок Р-1а, S22)
   живе доки: список сценаріїв судиться локально тими самими правилами

   Предмет охорони — МАРШРУТ. Правила вже мають свій гейт (smoke_rules_v1);
   тут судиться те, що між ними й екраном: чи кожен рядок вердикту потрапив
   рівно на ту картку, про яку він сказаний, і чи не загубився дорогою.

   ⚠ МЕЖА, НАЗВАНА ВГОЛОС (12.12-є). Ін'єкції нижче правлять КОД сторінки,
   а не дані, — і це не недогляд. Дефект, який крок вилікував, живе саме в
   коді (префікс замість токена; мовчазна втрата нерозпізнаного рядка);
   ін'єкція мусить повернути той дефект, інакше вона нічого не доводить.
   Роль відомо-поганих ДАНИХ тут інша й теж обов'язкова (12.12-и): на живих
   даних правила не віддають ЖОДНОГО рядка з номером сценарію, тому
   інваріанти маршруту на них порожні й зелені ні про що. Тому гейт піднімає
   сторінку тричі: на живих даних і на двох фікстурах із відомим дефектом.

   S23 · КАРТКА СЦЕНАРІЮ (Р-1б + Р-2). Другий предмет охорони — ЧЕРНЕТКА:
   правка мусить доїхати до правил і не доїхати нікуди більше. Форма нічого
   не публікує, тому «не написав» тут — таке саме твердження, як «показав».

   ⚠ ТВЕРДЖЕННЯ БЕЗ ІНʼЄКЦІЇ, назване вголос: «вісім ознак під mood дослівно
   з AE_RULES.MOOD_SIGNS». Шлях відмови в нього справжній (копія переліку в
   index.html розійдеться, щойно зʼявиться девʼята ознака), але окремої
   інʼєкції під нього немає: ІН-Д уже ловить той самий клас дефекту на
   переліку характерів, а друга інʼєкція того ж класу дала б два твердження,
   що падають від однієї причини (12.12-ї).

   Прогін:  node tools/smoke_edit_ui_v1.js
            node tools/smoke_edit_ui_v1.js --inject=ІН-А   (маршрут префіксом)
            node tools/smoke_edit_ui_v1.js --inject=ІН-Б   (втрата рядка)
            node tools/smoke_edit_ui_v1.js --inject=ІН-В   (чернетка не доїхала до правил)
            node tools/smoke_edit_ui_v1.js --inject=ІН-Г   (межа лічильника зашита числом)
            node tools/smoke_edit_ui_v1.js --inject=ІН-Д   (перелік характерів не з носія)
            node tools/smoke_edit_ui_v1.js --inject=ІН-Е   (замок знято)
            node tools/smoke_edit_ui_v1.js --inject=ІН-Є   (адреса зашита в коді)
            node tools/smoke_edit_ui_v1.js --inject=ІН-Ж   (ключ їде сирим заголовком) */

const fs=require('fs'), path=require('path');
const {JSDOM}=require('jsdom');
/* Корінь збірки — першим аргументом, якщо він не прапорець. Без цього
   гейт прив'язаний до однієї теки й у CI не піде (борг S21 §0: решта
   смоуків саме цим і тримається поза CI). */
const pos=process.argv[2];
const BASE=(pos && !pos.startsWith('--')) ? pos : '/mnt/user-data/outputs/AE';
const arg=(process.argv.find(a=>a.startsWith('--inject='))||'').split('=')[1]||'';
let ok=0,bad=0;
const T=(n,c)=>{ c?(ok++,console.log('  ✓ '+n)):(bad++,console.log('  ✗ '+n)); };

const files={'config.json':'config.json','data/catalog.json':'data/catalog.json',
  'data/scenarios.json':'data/scenarios.json','prompts/client.md':'prompts/client.md',
  'prompts/client.parts.md':'prompts/client.parts.md','prompts/characters.md':'prompts/characters.md',
  'prompts/debrief.md':'prompts/debrief.md','prompts/judge.md':'prompts/judge.md'};

let HTML=fs.readFileSync(path.join(BASE,'index.html'),'utf8');
const RULES_SRC=fs.readFileSync(path.join(BASE,'tools/ae_rules.js'),'utf8');
HTML=HTML.replace('<script src="tools/ae_rules.js"></script>','<script>'+RULES_SRC+'</script>');

/* Якір, якого не знайдено, зупиняє прогін окремим кодом: інакше ін'єкція
   мовчки не застосується, гейт позеленіє і це прочитається як доказ. */
function inject(src, anchor, replacement, name){
  if(!src.includes(anchor)){
    console.error('✗ ГЕЙТ ЗЛАМАНИЙ: якір ін\'єкції '+name+' не знайдено. Це не зелений прогін.');
    process.exit(2);
  }
  return src.replace(anchor, replacement);
}

if(arg==='ІН-А'){
  /* Повертає префіксний маршрут: рядок про #41 лягає ще й на картку #4.
     На живих даних (id 1…43) пастка не гіпотетична — вона гарантована. */
  HTML=inject(HTML,
    "    if(id!==null && ids.has(id)){",
    "    const pref=[...ids].find(x=>String(m.msg).startsWith('#'+x));\n" +
    "    if(pref!==undefined){ const id2=pref;\n" +
    "      if(!byId.has(id2)) byId.set(id2,[]);\n" +
    "      byId.get(id2).push(m); continue; }\n" +
    "    if(id!==null && ids.has(id)){", 'ІН-А');
}
if(arg==='ІН-Е'){
  /* Повертає відсутність замка: перечитаний sha більше ні з чим не
     звіряється, і правка їде поверх чужої мовчки — рівно та поведінка,
     яку S22 §1.3 назвав відсутністю обробки конфлікту. */
  HTML=inject(HTML, '  if(fresh.sha !== S.esnap.sha){',
    '  if(false){', 'ІН-Е');
}
/* ІН-Ж. Ключ їде СИРИМ, без відсоткового кодування. Дефект тихий: у
   jsdom заголовок доїде як є, і мок, що розкодовує, побачить те саме
   значення — тобто «запис пройшов». У браузері ж кирилиця в заголовку
   HTTP кидає TypeError на «non ISO-8859-1 code point», і публікація
   мовчки не відбувається. Саме тому твердження питає ще й ВИГЛЯД
   заголовка, а не лише результат. Вилучення заголовка цілком червонить
   те саме єдине твердження. */
if(arg==='ІН-Ж'){
  HTML=inject(HTML,
    "               'x-ae-edit-code':encodeURIComponent(EDITKEY.code.trim())},",
    "               'x-ae-edit-code':EDITKEY.code.trim()},", 'ІН-Ж');
}
if(arg==='ІН-Є'){
  /* Повертає зашиту адресу: звірка йде не туди, куди каже config.
     Твердження сформульоване як РІВНІСТЬ із оголошенням (12.11), тому
     ловить саме розходження, а не «схоже на GitHub». */
  HTML=inject(HTML, "  const url = S.cfg.sourceApi + path + '?ref=' +",
    "  const url = 'https://api.github.com/repos/inshyj/repo/contents/' + path + '?ref=' +", 'ІН-Є');
}
if(arg==='ІН-Б'){
  /* Повертає мовчазну втрату. Номер у повідомленні — рядок ('3'), id
     сценарію — число (3); варто ключам розійтись типом, і жоден рядок
     не знаходить своєї картки. Дефект найтихіший з можливих: сума
     сходиться (усе поїхало в «Загальні»), екран малюється цілим, усі
     43 картки кажуть «без зауважень» — тобто зламані дані виглядають
     чистішими, ніж вони є. */
  HTML=inject(HTML,
    "  const ids = new Set(SC.map(s=>String(s.id)));",
    "  const ids = new Set(SC.map(s=>s.id));", 'ІН-Б');
}

/* ── ІНʼЄКЦІЇ КАРТКИ (S23) ────────────────────────────────────────── */
if(arg==='ІН-В'){
  /* Повертає розрив між формою і правилами: картка судить ФАЙЛ, а показує
     чернетку. Дефект тихий — екран цілий, вирок правдоподібний, просто
     він про текст, якого в полі вже немає. */
  HTML=inject(HTML,
    "    const r  = runRules(null, SC);",
    "    const r  = runRules();", 'ІН-В');
}
if(arg==='ІН-Г'){
  /* Дві правки, одна причина: сторінка бере межу літералом, а правила
     тим часом кажуть інше число. Поки обидва по 90, копія непомітна —
     тому інʼєкція мусить їх розвести, інакше вона нічого не доводить. */
  HTML=inject(HTML,
    "  const LIMIT = (typeof AE_RULES!=='undefined') ? AE_RULES.MOOD_LIMIT : null;",
    "  const LIMIT = 90;", 'ІН-Г');
  HTML=inject(HTML, "const MOOD_LIMIT = 90;", "const MOOD_LIMIT = 70;", 'ІН-Г·правила');
}
if(arg==='ІН-Д'){
  /* Повертає копію закритого переліку в код сторінки (12.11-а): вибір
     заповнюється власним масивом, а не носієм. Список навмисно неповний —
     саме так копія й розходиться з носієм: тихо і не одразу. */
  HTML=inject(HTML,
    "  const chars = Object.keys(S.P.chars||{});",
    "  const chars = ['відкритий','поспішає','рахує гроші'];", 'ІН-Д');
}

/* ── фікстури ──────────────────────────────────────────────────────
   Дефект обраний так, щоб boot() його ПЕРЕЖИВ: сирітський character
   зупиняє старт застосунку виїмкою (index.html), і тоді падає все
   разом — тобто одна причина на два десятки тверджень (12.12-ї).
   Цифра й лапки в mood правилами ловляться, стартом — ні. */
const BAD_MOOD='клієнт чекав 5 хвилин і сказав «швидше»';
const mutNone = s=>s;
const mutOne  = s=>{ const c=JSON.parse(JSON.stringify(s));
  c.scenarios.find(x=>String(x.id)==='3').mood=BAD_MOOD; return c; };
const mutLong = s=>{ const c=JSON.parse(JSON.stringify(s));
  c.scenarios.find(x=>String(x.id)==='41').mood=BAD_MOOD; return c; };

/* ── МОК РЕПОЗИТОРІЮ Й ВОРКЕРА (S24) ──────────────────────────────────
   Сторінка тепер стукає у два різні місця: відносними шляхами — по свої
   файли (це GitHub Pages), повним URL — по ІСТИНУ (api.github.com) і по
   запис (воркер). Мок мусить розрізняти їх так само, як розрізняє
   браузер, інакше твердження про замок судили б вигадку.
   gh.shaSeq — черга відбитків для data/scenarios.json: перший видається
   на звірці при вході, наступний — на перечитуванні перед записом. Різні
   значення = файл змінили під відкритою карткою.
   gh.failRead — відмова читання (403 по ліміту 60/год виглядає саме так). */
/* ⚠ КИРИЛИЦЕЮ СВІДОМО. Латинський код проїхав би і сирим заголовком —
   тобто гейт зеленів би на дефекті, який на пристрої дає TypeError
   «non ISO-8859-1 code point» і мовчазну відмову запису. Мова коду тут
   і є перевіркою. */
const EDIT_CODE = 'ключ редактора';
const b64 = s => Buffer.from(s,'utf8').toString('base64');
function mount(mutate, gh={}){
  const log={reads:[], posts:[]};
  const shaQ=(gh.shaSeq||[]).slice();
  const dom=new JSDOM(HTML,{runScripts:'dangerously',url:'https://x.test/?mock=1',
    beforeParse(w){
      w.TextDecoder=TextDecoder;
      w.fetch=(u,opt)=>{
        if(typeof u==='string' && u.startsWith('http')){
          if(opt && opt.method==='POST'){
            const hdr = (opt.headers||{})['x-ae-edit-code'];
            log.posts.push({url:u, body:JSON.parse(opt.body), code:hdr});
            /* Звіряємо ЗІ ЗНАЧЕННЯМ, а не «заголовок є». Воркер порівнює з
               секретом (ae-edit.js:227); мок, якому досить будь-якого
               заголовка, не мав би як зіграти неправильний код — а саме
               його людина й набере першим. */
            let given = hdr || '';
            try{ given = decodeURIComponent(given); }catch(_){ }
            if(given !== EDIT_CODE) return Promise.resolve({ok:false,status:403,
              json:()=>Promise.resolve({ok:false,text:'Код редактора не підходить.'})});
            /* ⚠ МОК МУСИТЬ УМІТИ ВІДМОВЛЯТИ (S24 §4.3). Мок, який на будь-який
               POST каже «Збережено», доводить, що дорога існує, — але не те,
               що по ній проїдуть: рівно так ✓37 співіснували з відмовою на
               першому ж натисканні на пристрої. Відмова тут — тими самими
               словами й тим самим кодом, що в ae-edit.js:227. */
            return Promise.resolve({ok:true,status:200,json:()=>Promise.resolve(
              {ok:true,err:0,warn:0,out:[],saved:'data/scenarios.json',text:'Збережено.'})});
          }
          log.reads.push(u);
          if(gh.failRead) return Promise.resolve({ok:false,status:403});
          const scn=u.includes('scenarios');
          const name=scn?'data/scenarios.json':'data/catalog.json';
          const raw=fs.readFileSync(path.join(BASE,name),'utf8');
          const sha=scn?(shaQ.length?shaQ.shift():'sha-scn'):'sha-cat';
          return Promise.resolve({ok:true,status:200,
            json:()=>Promise.resolve({sha,encoding:'base64',content:b64(raw)})});
        }
        const raw=fs.readFileSync(path.join(BASE,files[u]||u),'utf8');
        const val = u==='data/scenarios.json' ? mutate(JSON.parse(raw)) : null;
        return Promise.resolve({
          json:()=>Promise.resolve(val!==null?val:JSON.parse(raw)),
          text:()=>Promise.resolve(raw)}); };
      w.scrollTo=()=>{};
      w.HTMLElement.prototype.scrollIntoView=()=>{};
    }});
  dom.window.__gh=log;
  return dom.window;
}

/* Екран відкривається ТИМ САМИМ шляхом, що й у людини: через двері.
   Виставити S.screen='edit' зсередини гейта означало б перевірити
   малювання і не перевірити вхід. */
async function openEditor(w, useDoor){
  await new Promise(r=>setTimeout(r,300));
  const d=w.document;
  const click=t=>[...d.querySelectorAll('button')].find(b=>b.textContent.trim()===t);
  const inp=d.querySelectorAll('.field input');
  inp[0].value='Оля Тест'; inp[0].dispatchEvent(new w.Event('input'));
  inp[1].value='67';       inp[1].dispatchEvent(new w.Event('input'));
  click('Далі').click();
  click('Налаштування').click();
  /* Видимість читається обчисленим стилем, а не наявністю кнопки в DOM:
     кнопка в дереві є завжди — питання лише в тому, чи її показано. */
  const visible=()=>{ const b=click('Відкрити редактор');
    return !!b && w.getComputedStyle(b.parentElement).display!=='none'; };
  const door={};
  door.hiddenBefore = !visible();
  const codeField=[...d.querySelectorAll('input')]
    .find(i=>i.getAttribute('placeholder')==='код куратора');
  door.badCode = (()=>{ codeField.value='не той код';
    codeField.dispatchEvent(new w.Event('input'));
    click('Перевірити дані').click();
    return !visible(); })();
  codeField.value=w.S.cfg.curatorCode; codeField.dispatchEvent(new w.Event('input'));
  click('Перевірити дані').click();
  door.shownAfter = visible();
  const btn=click('Відкрити редактор');
  if(useDoor && btn) btn.click();
  return {d, click, door};
}

/* Розкладка, порахована ГЕЙТОМ незалежно від сторінки: якби вона бралась
   тим самим виразом, твердження порівнювало б дві однакові дірки. */
function expected(w){
  const S=w.S;
  const r=w.eval('runRules()');
  const ids=new Set(S.SCEN.map(s=>String(s.id)));
  const byId={}, general=[];
  for(const m of r.out){
    const mm=/^#(\S+)\s/.exec(m.msg+' ');
    const id=mm?mm[1]:null;
    if(id!==null && ids.has(id)){ (byId[id]=byId[id]||[]).push(m); }
    else general.push(m);
  }
  return {r, byId, general};
}

/* Стан картки читається з ВИХОДУ — з тексту в DOM, а не з внутрішніх
   структур сторінки. Внутрішню структуру можна порахувати правильно й
   намалювати не те. */
function generalOf(d){
  return [...d.querySelectorAll('#app > .acc > .accbody > .tapeline')].map(x=>x.textContent);
}
function cardsOf(d){
  const out={};
  for(const c of d.querySelectorAll('.ecard')){
    const id=(c.querySelector('.ord').textContent.match(/^#(\S+)/)||[,''])[1];
    const det=c.querySelector('details');
    const lines=det?[...det.querySelectorAll('.tapeline')].map(x=>x.textContent):[];
    out[id]={badge:c.querySelector('.est').textContent, lines};
  }
  return out;
}

(async()=>{
  console.log('\n— двері й вхід (живі дані) —');
  const wA=mount(mutNone);
  const A=await openEditor(wA, true);
  T('до коду входу в редактор немає', A.door.hiddenBefore);
  T('хибний код входу не відмикає', A.door.badCode);
  T('після коду куратора вхід зʼявляється без перемальовування екрана', A.door.shownAfter);
  T('кнопка відкриває екран редактора', wA.S.screen==='edit');
  T('екран редактора має шапку у дві сходинки',
    !!A.d.querySelector('.top .toprow') && !!A.d.querySelector('.top .toptitle'));

  const eA=expected(wA), cA=cardsOf(A.d);
  T('карток стільки ж, скільки сценаріїв',
    Object.keys(cA).length===wA.S.SCEN.length);
  T('на живих даних жодна картка не червона',
    Object.values(cA).every(c=>!c.badge.includes('✗')));
  /* Головне твердження про чесність напису: «без зауважень» ≠ «✓ від
     правил». Якщо напис колись стане галочкою, зелений почне означати
     доказ, якого правила не давали. */
  T('чиста картка каже «без зауважень», а не ✓',
    Object.values(cA).every(c=>!c.badge.includes('✗') && !c.badge.includes('⚠')
      ? c.badge.trim()==='без зауважень' : true));
  T('усі агрегатні рядки лежать у «Загальних», не на картках',
    eA.general.length===eA.r.out.length && Object.keys(eA.byId).length===0);

  console.log('\n— маршрут: дефект в одному сценарії —');
  const wB=mount(mutOne);
  const B=await openEditor(wB, true);
  const eB=expected(wB), cB=cardsOf(B.d);
  T('фікстура справді дає рядки з номером', Object.keys(eB.byId).length>0);
  /* Позитивне твердження маршруту, одне на обидві половини факту:
     і що картка почервоніла, і що під нею рівно те, що сказано про неї.
     Двома окремими вони падали б від однієї причини (12.12-ї). */
  T('картка #3 показує ✗ і несе рівно ті рядки, що правила сказали про #3',
    (cB['3']||{badge:'',lines:[]}).badge.includes('✗') &&
    cB['3'].lines.length===(eB.byId['3']||[]).length &&
    cB['3'].lines.every(t=>t.includes('#3 ')));
  T('сусідня картка #4 лишається чистою',
    (cB['4']||{badge:''}).badge.trim()==='без зауважень');
  /* Сума береться цілком з ЕКРАНА: картки плюс «Загальні». Якби друга
     половина бралась із розрахунку гейта, твердження падало б від будь-
     якого зсуву маршруту й дублювало те, що вище. Тут предмет інший —
     ЗНИКНЕННЯ: рядок, який не потрапив нікуди. */
  T('сума рядків на екрані = кількість рядків вердикту',
    Object.values(cB).reduce((a,c)=>a+c.lines.length,0) + generalOf(B.d).length
      === eB.r.out.length);

  console.log('\n— маршрут: номер-подовження (#4 проти #41) —');
  const wC=mount(mutLong);
  const C=await openEditor(wC, true);
  const eC=expected(wC), cC=cardsOf(C.d);
  T('фікстура зачепила саме #41', (eC.byId['41']||[]).length>0);
  /* Твердження свідомо ЗАПЕРЕЧНЕ: воно каже тільки «на чужій картці
     цього рядка немає». Якби воно ще й вимагало рядок на своїй картці,
     то падало б і від втрати маршруту — тобто дублювало б твердження
     фікстури #3 і стало б його прикрасою. */
  T('рядок про #41 не лежить на жодній чужій картці',
    Object.entries(cC).every(([id,c])=>id==='41' || !c.lines.some(t=>t.includes('#41 '))));
  /* Заперечне і теж лише про своє: чи не роздвоївся рядок. Порожній
     екран проходить його справедливо — зникнення судиться сумою вище. */
  T('жоден рядок не показаний на двох картках одразу', (()=>{
    const all=Object.values(cC).flatMap(c=>c.lines);
    return new Set(all).size===all.length; })());
  T('сума рядків на екрані = кількість рядків вердикту (фікстура #41)',
    Object.values(cC).reduce((a,c)=>a+c.lines.length,0) + generalOf(C.d).length
      === eC.r.out.length);

  console.log('\n— картка сценарію: поля, підказка, чернетка —');
  const wD=mount(mutNone);
  const D=await openEditor(wD, true);
  const dd=D.d;
  const cardOf = id => [...dd.querySelectorAll('.ecard')]
    .find(c=>c.querySelector('.ord').textContent.startsWith('#'+id+' '));
  /* Вхід у поля — тим самим жестом, що й у людини: кнопкою на картці. */
  [...cardOf('3').querySelectorAll('button')].find(b=>b.textContent.trim()==='Правити').click();
  T('кнопка на картці відкриває поля саме цього сценарію',
    wD.S.screen==='escen' && wD.S.escen==='3' &&
    dd.querySelector('.toptitle').textContent.startsWith('#3 '));

  const labOf = name => [...dd.querySelectorAll('.field')]
    .find(f=>f.querySelector('.flab b') && f.querySelector('.flab b').textContent===name);
  const moodField = labOf('Настрій дня (mood)');
  const moodTa = moodField && moodField.querySelector('textarea');

  const SIGNS = wD.eval('AE_RULES.MOOD_SIGNS');
  const shown = [...moodField.querySelectorAll('.ehint li')].map(x=>x.textContent);
  T('ознаки під полем mood — дослівно ті, що каже AE_RULES',
    shown.length===SIGNS.length && shown.every((t,i)=>t===SIGNS[i]));
  /* Читається ВИХІД — текст лічильника, а не змінна сторінки: число можна
     порахувати правильно і намалювати інше. */
  T('лічильник називає межу, яку каже AE_RULES',
    moodField.querySelector('.ecount').textContent.trim()
      === String(wD.S.SCEN.find(s=>String(s.id)==='3').mood.length)+' / '+wD.eval('AE_RULES.MOOD_LIMIT'));
  const chOpts=[...labOf('Характер').querySelectorAll('option')].map(o=>o.value);
  const carrier=Object.keys(wD.S.P.chars);
  T('перелік у виборі характеру — рівно ключі носія',
    chOpts.length===carrier.length && carrier.every(c=>chOpts.includes(c)));
  T('до правки картка каже «без зауважень», а не ✓',
    dd.querySelector('.everd .eline').textContent.startsWith('Без зауважень'));

  const lsBefore = wD.localStorage.length;
  const moodBefore = wD.S.SCEN.find(s=>String(s.id)==='3').mood;
  moodTa.value='клієнт чекав 5 хвилин';
  moodTa.dispatchEvent(new wD.window.Event('input'));
  /* Головне твердження чернетки: правка доїхала до ПРАВИЛ. Твердження про
     значок у списку (нижче) читає той самий стан, але іншого споживача —
     тому воно не прикраса цього, а окрема адреса. */
  T('правка mood змінює вирок під полем',
    [...dd.querySelectorAll('.everd .tapeline')].some(x=>x.textContent.includes('#3 mood')));
  T('правка не пише в localStorage', wD.localStorage.length===lsBefore);
  T('правка не мутує завантажені дані',
    wD.S.SCEN.find(s=>String(s.id)==='3').mood===moodBefore);

  /* Значок чернетки читається на НЕВІДФІЛЬТРОВАНОМУ списку. Спершу
     звузити список фільтром, а потім шукати в ньому картку — означало б
     поставити це твердження в залежність від маршруту вердикту: під
     ІН-Б відфільтрований список порожній, і твердження падало б удруге
     від чужої причини (12.12-ї). */
  [...dd.querySelectorAll('.back')][0].click();
  T('картка списку позначена чернеткою',
    !!cardOf('3') && [...cardOf('3').querySelectorAll('.echip')]
      .some(x=>x.textContent.startsWith('чернетка')));

  /* Фільтр — стан екрана, а не локальна змінна функції. Перевіряється
     найдешевшим перемальовуванням (вихід і повернення через двері), а не
     входом у картку: вхід залежав би від того, чи фільтр щось показав. */
  const chipErr=()=>[...dd.querySelectorAll('.tabs button')].find(b=>b.textContent.startsWith('✗'));
  chipErr().click();
  [...dd.querySelectorAll('.back')][0].click();
  D.click('Відкрити редактор').click();
  T('фільтр списку переживає перемальовування екрана',
    chipErr().getAttribute('aria-pressed')==='true');

  console.log('\n— публікація: адреса, замок, тіло запиту —');
  const tick=()=>new Promise(r=>setTimeout(r,60));
  /* Спільна дорога для всіх трьох прогонів: увійти, змінити mood, вийти
     до списку. Публікація живе в списку, бо пише файл цілком, а не картку. */
  const withDraft = async gh => {
    const w=mount(mutNone,gh); const E=await openEditor(w,true); const d=E.d;
    const card = id => [...d.querySelectorAll('.ecard')]
      .find(c=>c.querySelector('.ord').textContent.startsWith('#'+id+' '));
    [...card('3').querySelectorAll('button')].find(b=>b.textContent.trim()==='Правити').click();
    const ta=[...d.querySelectorAll('.field')]
      .find(f=>f.querySelector('.flab b')&&f.querySelector('.flab b').textContent==='Настрій дня (mood)')
      .querySelector('textarea');
    ta.value='клієнт чекав 5 хвилин'; ta.dispatchEvent(new w.window.Event('input'));
    [...d.querySelectorAll('.back')][0].click();
    await tick();
    return {w,d,
      pub:()=>[...d.querySelectorAll('button')]
        .find(b=>b.textContent.startsWith('Опублікувати')),
      /* Поле шукається в смузі публікації, а не по порядку інпутів на
         екрані: порядок елементів не має керувати гейтом (той самий шрам,
         що з «Стерти ключ» на першому інпуті). */
      keyIn:()=>d.querySelector('.pubbar .field input'),
      key(v){ const i=this.keyIn(); i.value=v; i.dispatchEvent(new w.window.Event('input')); }};
  };

  const P=await withDraft({});
  /* Рівність із оголошенням, а не «схоже на github»: зразок у гейті був
     би третьою копією адреси (12.11). */
  T('звірка стукає рівно за адресою з config.json',
    P.w.__gh.reads.length>=2 &&
    P.w.__gh.reads.every(u=>u.startsWith(P.w.S.cfg.sourceApi)));
  T('на зеленій звірці кнопка публікації зʼявляється', !!P.pub());

  /* ── КЛЮЧ ДО ВОРКЕРА (Р-1в-2) ─────────────────────────────────────
     Код редактора — не код куратора. Перший відмикає екран і лежить у
     публічному config.json; другий відмикає запис і не лежить ніде. */
  T('поле коду редактора стоїть у смузі й назване іншим ключем',
    !!P.keyIn() && P.keyIn().type==='password' &&
    [...P.d.querySelectorAll('.pubbar')].some(x=>/НЕ код куратора/.test(x.textContent)));

  /* Порожній код зупиняє ДО мережі: запит без ключа воркер відхилить
     однаково, але перечитування вже витратить один із 60 запитів на годину. */
  const readsWas = P.w.__gh.reads.length;
  P.pub().click(); await tick();
  T('без коду запису не відбувається, ліміт не витрачено, причина названа',
    P.w.__gh.posts.length===0 && P.w.__gh.reads.length===readsWas &&
    [...P.d.querySelectorAll('.publine')].some(x=>x.textContent.includes('Введіть код редактора')));

  P.key(EDIT_CODE);
  /* Дім ключа — памʼять вкладки. Диск телефона переживає власника. */
  T('код редактора не лягає в localStorage', (()=>{
    const ls=P.w.localStorage;
    for(let i=0;i<ls.length;i++)
      if(String(ls.getItem(ls.key(i))).includes(EDIT_CODE)) return false;
    return true; })());

  P.pub().click(); await tick();
  const body=(P.w.__gh.posts[0]||{}).body;
  T('запис пішов рівно один раз і рівно за адресою з config.json',
    P.w.__gh.posts.length===1 && P.w.__gh.posts[0].url===P.w.S.cfg.editEndpoint);
  /* Воркер судить обидва боки разом і пише те, що надіслали, ЦІЛИМ файлом:
     обгортка, загублена по дорозі, зникла б із репозиторію. */
  T('у тілі — обидва боки, бік запису названий',
    !!body && body.save==='scenarios' && !!body.catalog && !!body.scenarios);
  T('файл іде цілим: обгортка version уціліла',
    !!body && body.scenarios.version===JSON.parse(
      fs.readFileSync(path.join(BASE,'data/scenarios.json'),'utf8')).version);
  T('чернетка доїхала в тіло запиту',
    !!body && (body.scenarios.scenarios.find(s=>String(s.id)==='3')||{}).mood
      ==='клієнт чекав 5 хвилин');
  /* Одне твердження на обидві половини одного факту (12.12-ї): і що ключ
     доїхав у тому вигляді, який воркер уміє прочитати, і що запис по ньому
     пройшов. Двома окремими вони падають від однієї причини й читаються
     як два дефекти — рівно та пастка, яку показала ІН-Е. */
  T('код їде заголовком у відсотковому кодуванні, і запис по ньому проходить',
    (P.w.__gh.posts[0]||{}).code !== EDIT_CODE &&
    decodeURIComponent((P.w.__gh.posts[0]||{}).code||'') === EDIT_CODE &&
    Object.keys(P.w.S.edraft).length===0);

  /* Відмова воркера по коду — не «збій»: звірка від неправильного коду не
     псується. Тому екран лишає поле й кнопку запису й НЕ пропонує звіряти
     ще раз: зайва перезвірка палить ліміт 60/год, з якого живе замок. */
  const R=await withDraft({}); R.key('не той ключ'); R.pub().click(); await tick();
  T('відмова по коду лишає поле й кнопку запису, а не кнопку перезвірки',
    !!R.keyIn() && !!R.pub() &&
    ![...R.d.querySelectorAll('button')].some(b=>b.textContent.trim()==='Звірити ще раз') &&
    [...R.d.querySelectorAll('.publine')].some(x=>x.textContent.includes('Код редактора не підходить')));

  /* ЗАМОК. Файл підмінили між входом і кнопкою — запис не мусить статись
     узагалі, а не «статись і поскаржитись». */
  const L=await withDraft({shaSeq:['sha-1','sha-2']});
  /* ⚠ Код набирається ПРАВИЛЬНИЙ. Без нього запис зупинив би сторож
     порожнього ключа, і твердження про замок зеленіло б від чужої
     причини — найгірший вид зеленого. */
  if(L.keyIn()) L.key(EDIT_CODE);
  const lockBtn=L.pub(); if(lockBtn) lockBtn.click(); await tick();
  /* Одне твердження на обидві половини одного факту: і що запису не було,
     і що людині сказали чому. Двома окремими вони падають від однієї
     причини й читаються як два дефекти (12.12-ї) — ІН-Е це показала. */
  T('розбіжність відбитка зупиняє запис і названа на екрані',
    L.w.__gh.posts.length===0 &&
    [...L.d.querySelectorAll('.publine')].some(x=>x.textContent.includes('Не збережено')));

  /* Відмова читання = зупинка. «Не змогли звірити» не має права
     виглядати як «збіглось». */
  const F=await withDraft({failRead:true});
  T('відмова читання не дає кнопки публікації й названа на екрані',
    !F.pub() &&
    [...F.d.querySelectorAll('.publine')].some(x=>x.textContent.includes('зупинена')));

  console.log('\n— єдина точка виклику правил —');
  const src=fs.readFileSync(path.join(BASE,'index.html'),'utf8');
  T('AE_RULES.validate викликається на сторінці рівно один раз',
    (src.match(/AE_RULES\.validate\(/g)||[]).length===1);

  console.log('\n'+(bad?'✗':'✓')+' підсумок: ✓'+ok+' · ✗'+bad);
  process.exit(bad?1:0);
})();
