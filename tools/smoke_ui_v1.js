/* AE-Simulator · смоук UI-полірування (крок A/Б, 02.09.2026)
   живе доки: екран Налаштувань не перебудовано кроком Д (шестерня + куратор)

   Твердження читають ВИХІД продукту — живу DOM після рендера (1.15, пастка 4),
   а не перераховують очікуване власним виразом над тими самими даними.
   Межа чесності: jsdom НЕ рахує розкладку. Тому «ряд фільтрів в один рядок»
   і самі радіуси тут перевірити неможливо — ці два твердження є на рівні
   джерела і позначені [джерело]. Арбітр по них — iPhone, не цей файл. */
const fs=require('fs'), path=require('path');
const {JSDOM}=require('jsdom');
const BASE='/mnt/user-data/outputs/AE';
const INJECT = process.argv.includes('--inject');
let ok=0,bad=0;
const T=(n,c)=>{ c?(ok++,console.log('  ✓ '+n)):(bad++,console.log('  ✗ '+n)); };

const files={'config.json':'config.json','data/catalog.json':'data/catalog.json',
  'data/scenarios.json':'data/scenarios.json','prompts/client.md':'prompts/client.md',
  'prompts/client.parts.md':'prompts/client.parts.md','prompts/debrief.md':'prompts/debrief.md',
  'prompts/judge.md':'prompts/judge.md'};

let html=fs.readFileSync(path.join(BASE,'index.html'),'utf8');
/* Інʼєкція повертає ту саму ваду, яку крок лікував: збірка екрана
   нативним append, що друкує «null» текстовим вузлом. */
if(INJECT){
  html=html.replace(
    'const put = (root,...kids)=>{ for(const c of kids) if(c) root.append(c); };',
    'const put = (root,...kids)=>{ for(const c of kids) root.append(c); };');
  /* Друга вада: розбір знову пише клієнт, а не суддя. Одна ін'єкція на
     дві різні вади — щоб гейт не тримався на одному твердженні. */
  html=html.replace('if(engine.judge){','if(false){');
}

const dom=new JSDOM(html,{runScripts:'dangerously',url:'https://x.test/?mock=1',
  beforeParse(w){
    w.fetch=(u)=>{ const raw=fs.readFileSync(path.join(BASE,files[u]||u),'utf8');
      return Promise.resolve({json:()=>Promise.resolve(JSON.parse(raw)),
                              text:()=>Promise.resolve(raw)}); };
    w.scrollTo=()=>{};
    w.HTMLElement.prototype.scrollIntoView=()=>{};
  }});
const w=dom.window;

(async()=>{
  await new Promise(r=>setTimeout(r,300));
  const d=w.document, S=w.S;
  const src=html;
  const click=t=>[...d.querySelectorAll('button')].find(b=>b.textContent.trim()===t);

  console.log('\n— вхід у список —');
  const inp=d.querySelectorAll('.field input');
  inp[0].value='Оля Тест'; inp[0].dispatchEvent(new w.Event('input'));
  inp[1].value='67'; inp[1].dispatchEvent(new w.Event('input'));
  click('Далі').click();
  T('екран списку відкрився', S.screen==='picker');

  console.log('\n— «null» на екрані —');
  /* Читаємо вихід: чи є в дереві застосунку голий текстовий вузол «null».
     Не «чи є в коді put» — саме чи надрукувалось. */
  const strayNull = (root)=>{
    const walk=d.createTreeWalker(root, w.NodeFilter.SHOW_TEXT);
    let n; while((n=walk.nextNode())) if(n.nodeValue.trim()==='null') return true;
    return false;
  };
  T('на списку немає тексту «null»', !strayNull(d.getElementById('app')));

  console.log('\n— картка й фільтри —');
  T('картки на місці', d.querySelectorAll('.card').length===43);
  T('чипів фільтрів 7', d.querySelectorAll('.tabs button').length===7);
  T('[джерело] ряд фільтрів не переносить', /\.tabs\{[^}]*flex-wrap:nowrap/.test(src));
  T('[джерело] край ряду згасає маскою', /\.tabs\{[\s\S]{0,900}mask-image:linear-gradient\(90deg/.test(src));
  T('[джерело] радіус узятий шкалою, літералів 3px немає',
    /--r-lg:\s*16px/.test(src) && !/border-radius:3px/.test(src));
  T('[джерело] прес є на картці, чипі, кнопці й «назад»',
    /\.card:active\{transform:scale/.test(src) && /\.tabs button:active\{transform:scale/.test(src)
    && /\.btn:active\{transform:scale/.test(src) && /\.back:active\{transform:scale/.test(src));
  T('[джерело] :active увімкнено слухачем дотику (iOS)',
    /addEventListener\('touchstart'/.test(src));

  T('[джерело] снапу на ряді фільтрів немає (інерція iOS)',
    !/scroll-snap-type/.test(src) && !/scroll-snap-align/.test(src));

  console.log('\n— шапка й панель розмови —');
  d.querySelector('.card').click();
  T('шапка — дві сходинки', !!d.querySelector('.top .toprow') && !!d.querySelector('.top .toptitle'));
  T('заголовок сценарію в своєму рядку',
    d.querySelector('.toptitle').textContent===S.sc.title);
  const chat=d.querySelector('.chat');
  T('панель розмови існує', !!chat);
  T('репліки лежать усередині панелі', !!chat && !!chat.querySelector('.log .turn'));
  T('поле вводу лежить усередині панелі', !!chat && !!chat.querySelector('.say textarea'));
  T('кнопка «Сказати» лежить усередині панелі',
    !!chat && [...chat.querySelectorAll('button')].some(b=>b.textContent.trim()==='Сказати'));
  T('підказка видима, доки розмови немає',
    !!chat && !chat.querySelector('.chat-hint').classList.contains('hide'));
  T('[джерело] фон панелі темніший за сторінку', /--chat:#E7ECE8/.test(src));
  T('[джерело] крапки «клієнт друкує» є', /\.dots i\{/.test(src) && /S\.waiting/.test(src));

  /* Переповнення по горизонталі. jsdom розкладки не має, тому б'ємо
     в дві причини, які її створювали: колонку з min-width:auto і
     дитину, ширшу за батька. */
  T('[джерело] мобільна колонка має min-width 0',
    /@media\(max-width:880px\)\{\.stage\{grid-template-columns:minmax\(0,1fr\)\}\}/.test(src));
  T('[джерело] відʼємних полів усередині панелі немає',
    !/\.say\{[^}]*margin:0 -12px/.test(src) && !!d.querySelector('.chat > .chat-body'));
  T('[джерело] довгий токен переноситься в бульбашці', /overflow-wrap:anywhere/.test(src));

  console.log('\n— розмова до кінця (заглушка) —');
  const ta=d.querySelector('.say textarea');
  const say=[...d.querySelectorAll('.say button')][0];
  for(let i=0;i<5;i++){
    ta.value='репліка '+i; ta.dispatchEvent(new w.Event('input'));
    say.click(); await new Promise(r=>setTimeout(r,400));
  }
  T('розмову завершено', S.ended===true);
  T('розбір має власний вигляд, не бульбашку клієнта',
    !!d.querySelector('.turn.review') && !d.querySelector('.turn.review').classList.contains('client'));
  T('поле вводу заглушене після завершення', ta.disabled===true);
  T('кнопка «Сказати» заглушена після завершення', say.disabled===true);
  T('поле каже, чому воно не працює', ta.placeholder==='Розмову завершено');
  T('підказку прибрано після завершення',
    d.querySelector('.chat-hint').classList.contains('hide'));

  console.log('\n— суддя окремо від клієнта —');
  const wk=fs.readFileSync(path.join(BASE,'worker/ae-proxy.js'),'utf8');
  const cfg=JSON.parse(fs.readFileSync(path.join(BASE,'config.json'),'utf8'));
  T('розбір прийшов від судді, не від клієнта', /Заглушка судді/.test(d.body.textContent));
  T('шапка розбору несе числа', /РОЗБІР · приріст/.test(d.querySelector('.review .who').textContent));
  T('фраза «варто було сказати» рендериться', !!d.querySelector('.review .phrase'));
  T('схема судді оголошена', !!cfg.schemas.judge && cfg.schemas.judge.strict===true);
  T('[джерело] роль їде заголовком x-ae-role', /headers\['x-ae-role'\] = role/.test(src));
  T('[джерело] суддя кличеться з роллю judge',
    /S\.cfg\.schemas\.judge, 'judge'\)/.test(src));
  T('[джерело] обрив по стелі має свій текст', /finish_reason/.test(src) && /не влізла/.test(src));
  T('воркер має профілі ролей', /effort: \{ client:/.test(wk) && /ROLES = \['client', 'judge'\]/.test(wk));
  T('воркер бере стелю з профілю ролі', /r\.tokens\[role\]/.test(wk));
  T('CORS пропускає x-ae-role', /Allow-Headers[^\n]*x-ae-role/.test(wk));
  T('невідома роль падає в client, а не в помилку',
    /ROLES\.includes\(roleHdr\) \? roleHdr : 'client'/.test(wk));

  console.log('\n— пройти ще раз —');
  const retry=[...d.querySelectorAll('button')].find(b=>b.textContent.trim()==='Пройти ще раз');
  T('кнопка «Пройти ще раз» зʼявилась', !!retry && !retry.classList.contains('hide'));
  retry.click();
  T('стрічка очистилась до першої репліки', d.querySelectorAll('.log .turn').length===1);
  T('розмова знову жива', S.ended===false);
  T('поле вводу знову працює', ta.disabled===false);
  T('чек повернувся до початкового замовлення',
    JSON.stringify(S.cart)===JSON.stringify(S.sc.order));
  T('спроба порахована', S.attempt===2);
  T('розбір і фраза скинуті', S.feedback==='' && S.phrase==='');
  T('кнопки кінця сховані', retry.classList.contains('hide'));

  S.screen='picker'; w.render();

  console.log('\n— кнопка «назад» —');
  d.querySelector('.card').click();
  T('відкрився сценарій', S.screen==='game');
  const back=d.querySelector('.back');
  T('кнопка «назад» є', !!back);
  T('усередині шеврон-SVG, а не символ ←', !!back && !!back.querySelector('svg') && !/←/.test(back.textContent));
  T('підпис лишився словами', !!back && /до списку/.test(back.textContent));
  back.click();
  T('повернулись у список', S.screen==='picker');

  console.log('\n— Налаштування —');
  click('Налаштування').click();
  T('екран налаштувань', S.screen==='settings');
  const txt=d.getElementById('app').textContent;
  T('блоку кодового слова немає', !/Кодове слово мережі/.test(txt));
  T('поля кодового слова немає',
    ![...d.querySelectorAll('input')].some(i=>i.placeholder==='порожньо = не потрібне'));
  T('кнопки «Зберегти кодове слово» немає', !click('Зберегти кодове слово'));
  T('константа NET у коді лишилась', /localStorage\.getItem\('ae_net_code'\)/.test(src));

  const accs=[...d.querySelectorAll('details.acc')];
  T('акордеонів два', accs.length===2);
  T('пояснення про ключ лежить усередині акордеона',
    accs.some(a=>/console\.groq\.com/.test(a.textContent)));
  T('технічна таблиця лежить усередині акордеона',
    accs.some(a=>/Правило оцінки/.test(a.textContent)));
  T('акордеони згорнуті за замовчуванням', accs.every(a=>!a.open));

  console.log('\n— «Стерти ключ» чистить СВОЄ поле —');
  const keyField=[...d.querySelectorAll('input')].find(i=>i.placeholder==='gsk_…');
  keyField.value='gsk_test123'; keyField.dispatchEvent(new w.Event('input'));
  click('Стерти ключ').click();
  T('поле ключа порожнє', keyField.value==='');
  T('ключ прибрано зі сховища', !w.localStorage.getItem('ae_groq_key'));
  T('імʼя користувача не постраждало', !!w.localStorage.getItem('ae_me'));

  console.log(`\n✓${ok} · ✗${bad}`+(INJECT?' (inject)':''));
  process.exit(bad?1:0);
})().catch(e=>{console.error('впало:',e); process.exit(1)});
