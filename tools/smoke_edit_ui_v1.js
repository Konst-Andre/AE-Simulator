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

   Прогін:  node tools/smoke_edit_ui_v1.js
            node tools/smoke_edit_ui_v1.js --inject=ІН-А   (маршрут префіксом)
            node tools/smoke_edit_ui_v1.js --inject=ІН-Б   (втрата рядка) */

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
if(arg==='ІН-Б'){
  /* Повертає мовчазну втрату. Номер у повідомленні — рядок ('3'), id
     сценарію — число (3); варто ключам розійтись типом, і жоден рядок
     не знаходить своєї картки. Дефект найтихіший з можливих: сума
     сходиться (усе поїхало в «Загальні»), екран малюється цілим, усі
     43 картки кажуть «без зауважень» — тобто зламані дані виглядають
     чистішими, ніж вони є. */
  HTML=inject(HTML,
    "  const ids = new Set(S.SCEN.map(s=>String(s.id)));",
    "  const ids = new Set(S.SCEN.map(s=>s.id));", 'ІН-Б');
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

function mount(mutate){
  const dom=new JSDOM(HTML,{runScripts:'dangerously',url:'https://x.test/?mock=1',
    beforeParse(w){
      w.fetch=(u)=>{ const raw=fs.readFileSync(path.join(BASE,files[u]||u),'utf8');
        const val = u==='data/scenarios.json' ? mutate(JSON.parse(raw)) : null;
        return Promise.resolve({
          json:()=>Promise.resolve(val!==null?val:JSON.parse(raw)),
          text:()=>Promise.resolve(raw)}); };
      w.scrollTo=()=>{};
      w.HTMLElement.prototype.scrollIntoView=()=>{};
    }});
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

  console.log('\n— єдина точка виклику правил —');
  const src=fs.readFileSync(path.join(BASE,'index.html'),'utf8');
  T('AE_RULES.validate викликається на сторінці рівно один раз',
    (src.match(/AE_RULES\.validate\(/g)||[]).length===1);

  console.log('\n'+(bad?'✗':'✓')+' підсумок: ✓'+ok+' · ✗'+bad);
  process.exit(bad?1:0);
})();
