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
/* jsdom не вантажить <script src>: він не має мережі, а стуб fetch тут не
   допомагає — тег іде повз fetch. Підставляємо вміст файлу самі. Це не
   милиця, а дограна частина браузера; зникне тег — підстановка не
   спрацює, AE_RULES стане undefined і твердження нижче почервоніють. */
const RULES_SRC=fs.readFileSync(path.join(BASE,'tools/ae_rules.js'),'utf8');
html=html.replace('<script src="tools/ae_rules.js"></script>',
                  '<script>'+RULES_SRC+'</script>');
/* Інʼєкція повертає ту саму ваду, яку крок лікував: збірка екрана
   нативним append, що друкує «null» текстовим вузлом. */
if(INJECT){
  html=html.replace(
    'const put = (root,...kids)=>{ for(const c of kids) if(c) root.append(c); };',
    'const put = (root,...kids)=>{ for(const c of kids) root.append(c); };');
  /* Друга вада: розбір знову пише клієнт, а не суддя. Одна ін'єкція на
     дві різні вади — щоб гейт не тримався на одному твердженні. */
  html=html.replace('if(engine.judge){','if(false){');
  /* Третя вада: втрата порту — рядок «Настрій» зникає з брифінгу.
     Саме так mood і загубився при переносі (S5 §2.8): нічого не падає,
     людина просто грає проти опору, не знаючи про нього. */
  html=html.replace("el('dt',{text:'Настрій'}), el('dd',{text:sc.mood}),", '');
  /* Четверта вада: пост-прохід згортання загублено при переносі. Рядки
     на екрані є, читаються нормально, шеврони просто зникли — рівно той
     тип втрати, що ховається сесіями (S7 §2.2). */
  html=html.replace("foldRows(briefDl,['Настрій','Ціль']);", '');
  /* Пʼята вада (6а-3): розбір форми файлу завжди каже «каталог». На екрані
     не видно нічого — панель відкривається, кнопка на місці, вердикт є.
     Ловиться тільки викликом самої функції. */
  html=html.replace("  if(Array.isArray(v.scenarios)) return 'scen';", '');
  /* Шоста: рядок джерела зник. Вердикт лишається правильним і починає
     мовчати про те, ЩО він судив, — тобто стає вердиктом ні про що. */
  html=html.replace(
    "      gateRow, fileRow, fileNote, srcLine, head, box",
    "      gateRow, fileRow, fileNote, head, box");
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
  /* Марка збірки. Друга перевірка важливіша за першу: вона ловить регрес
     «номер зашили в index.html і забули оновлювати». Порівнюємо з config,
     а не з літералом. */
  T('марка збірки видима на екрані входу', d.body.textContent.includes(S.cfg.build));
  T('марка взята з config, не зашита в код', !src.includes('Збірка '+S.cfg.build));
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
  /* Брифінг. Читаємо живу DOM: пара dt/dd, значення — з того самого
     сценарію, який зараз грається. Без цього твердження втрата рядка
     проходить тихо — так і сталось із mood у S5. */
  const dts=[...d.querySelectorAll('.brief dt')].map(x=>x.textContent);
  const dds=[...d.querySelectorAll('.brief dd')].map(x=>x.textContent);
  T('брифінг показує настрій клієнта', dds[dts.indexOf('Настрій')]===S.sc.mood);
  /* Порядок змінено свідомо (S8): «Настрій» переїхав з-під «Клієнта» у
     хвіст, до «Цілі». Це два довгі згортані рядки, і вони мусять бути
     сусідами — інакше керовані шеврони розкидані по таблиці. */
  T('настрій стоїть поряд із ціллю, у хвості брифінгу',
    dts.indexOf('Настрій')>=0 &&
    dts.indexOf('Настрій')+1===dts.indexOf('Ціль') &&
    dts.indexOf('Ціль')===dts.length-1);
  /* Згортання. Клас — на dt і dd, стан — атрибутами. Перевіряємо обидва
     рядки окремо: третя ін'єкція виносить лише «Настрій», і без окремого
     твердження про «Ціль» зняте згортання пройшло б тихо. */
  const foldDt=[...d.querySelectorAll('.brief dt.fold')].map(x=>x.textContent.trim());
  T('настрій згортається', foldDt.includes('Настрій'));
  T('ціль згортається', foldDt.includes('Ціль'));
  const goalDd=dds.length?d.querySelectorAll('.brief dd')[dts.indexOf('Ціль')]:null;
  T('ціль відкрита за замовчуванням',
    !!goalDd && goalDd.classList.contains('fold-b') && goalDd.getAttribute('data-open')==='1');
  /* ⚠ Довжина перевіряється окремо: .every на порожньому наборі істинний,
     тож без неї зникле згортання давало б зелений ✓ (1.15, пастка 4). */
  const foldEls=[...d.querySelectorAll('.brief dt.fold')];
  T('шеврон згортання — інлайновий SVG, не гліф',
    foldEls.length===2 && foldEls.every(x=>!!x.querySelector('svg.chev')));

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

  /* Було два (пояснення про ключ, технічні дані); 6а-2 додав третій —
     «Перевірка даних». Число тримається навмисно: воно ловить акордеон,
     що зʼявився повз рішення. */
  const accs=[...d.querySelectorAll('details.acc')];
  T('акордеонів три', accs.length===3);
  T('третій акордеон — «Перевірка даних»',
    accs.some(a=>a.querySelector('summary')&&a.querySelector('summary').textContent==='Перевірка даних'));
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

  /* ── ПЕРЕВІРКА ДАНИХ (6а-2) ────────────────────────────────────
     Гейт кроку — не вигляд панелі, а те, що браузер і диск судять
     ОДНАКОВО. Читаємо вихід сторінки і вихід тих самих правил на сирих
     файлах; порівнюємо повний текст, а не підсумкові числа: однакові
     числа при різному тексті — саме той декоративний ✓ (1.15, пастка 4).
     Це єдине місце, де ловиться розходження нормалізації: S.CAT віддає
     items без label, і якщо колись зʼявиться правило на label, панель
     скаже ✓ там, де командний рядок скаже ✗. */
  console.log('\n— перевірка даних судить так само, як командний рядок —');
  const rulesDisk=require(path.join(BASE,'tools/ae_rules.js'));
  const rawCat=JSON.parse(fs.readFileSync(path.join(BASE,'data/catalog.json'),'utf8'));
  const rawScn=JSON.parse(fs.readFileSync(path.join(BASE,'data/scenarios.json'),'utf8'));
  const vDisk=rulesDisk.validate(rawCat,rawScn);
  T('AE_RULES доїхали до сторінки', !!w.AE_RULES && typeof w.AE_RULES.validate==='function');
  const vPage = w.AE_RULES && w.AE_RULES.validate ? w.AE_RULES.validate(S.CAT,S.SCEN) : null;
  const flat=v=>v?v.out.map(m=>m.lvl+' '+m.msg).join('\n'):'—';
  T('вердикт сторінки збігається з вердиктом диска дослівно',
    !!vPage && flat(vPage)===flat(vDisk));
  T('числа підсумку теж збігаються',
    !!vPage && vPage.ok===vDisk.ok && vPage.warn===vDisk.warn && vPage.err===vDisk.err);

  console.log('\n— панель перевірки за кодом куратора —');
  const sums=[...d.querySelectorAll('summary')].map(x=>x.textContent);
  T('панель «Перевірка даних» є на екрані', sums.includes('Перевірка даних'));
  const codeField=[...d.querySelectorAll('input')].find(i=>i.placeholder==='код куратора');
  T('поле коду куратора є', !!codeField);
  /* ⚠ Читаємо ПАНЕЛЬ, а не d.body: body.textContent у jsdom включає текст
     самих <script>, і перша редакція цих тверджень ловила збіг у вихідному
     коді сторінки, а не на екрані. Проба, що бачить джерело, судить не те. */
  const panel=[...d.querySelectorAll('details.acc')]
    .find(a=>a.querySelector('summary') && a.querySelector('summary').textContent==='Перевірка даних');
  T('панель знайдена як елемент', !!panel);
  if(codeField && panel){
    codeField.value='не той код'; codeField.dispatchEvent(new w.Event('input'));
    click('Перевірити дані').click();
    T('чужий код не відкриває вивід', !/підсумок: ✓/.test(panel.textContent));
    codeField.value=S.cfg.curatorCode; codeField.dispatchEvent(new w.Event('input'));
    click('Перевірити дані').click();
    T('правильний код друкує підсумок',
      panel.textContent.includes('підсумок: ✓'+vDisk.ok+' · ⚠'+vDisk.warn+' · ✗'+vDisk.err));
    T('рядки вердикту видно, а не лише підсумок',
      panel.textContent.includes(vDisk.out[0].msg));

    /* ── 6а-3 ── Розбір судиться ВИКЛИКОМ продуктових функцій. Твердження,
       що дивиться лише на екран, про зламаний розбір мовчить: панель
       відкриється й покаже вердикт навіть тоді, коли форма файлу
       визначається навмання (1.15, пастка 5). */
    T('розпізнає каталог за формою',  w.classifyJson(rawCat)==='cat');
    T('розпізнає сценарії за формою', w.classifyJson(rawScn)==='scen');
    T('голий масив сценаріїв теж розпізнається',
      w.classifyJson(rawScn.scenarios||rawScn)==='scen');
    T('чужий обʼєкт не видається за дані', w.classifyJson({a:1,b:2})===null);
    T('порожній вхід не видається за дані', w.classifyJson(null)===null);

    const brokenSrc='{\n  "a": 1,\n  ,\n}';
    let jerr=null; try{ JSON.parse(brokenSrc); }catch(e){ jerr=e; }
    const jtxt=w.jsonErrorText(jerr, brokenSrc);
    T('текст помилки JSON називає рядок', /рядок 3/.test(jtxt));
    T('текст помилки JSON без англійського виводу рушія',
      !/position|Unexpected|token/i.test(jtxt));
    T('без позиції текст усе одно людський',
      /Файл не читається як JSON/.test(w.jsonErrorText(new Error('дурня'), '')));

    T('кнопка вибору файлу є в панелі',
      [...panel.querySelectorAll('button')].some(b=>b.textContent==='Вибрати файл…'));
    T('є повернення до даних застосунку',
      [...panel.querySelectorAll('button')].some(b=>b.textContent==='Дані застосунку'));
    T('поле файлу без accept — фільтр Files не глушить iCloud',
      !!panel.querySelector('input[type=file]') &&
      !panel.querySelector('input[type=file]').hasAttribute('accept'));
    T('вердикт називає джерело, яке судив',
      /Судиться: каталог — дані застосунку/.test(panel.textContent));
    /* Живий прогін самого вибору: файл кладеться в поле і подія
       відпускається так само, як її відпустив би телефон. Без цього все
       вище судить лише наявність кнопки, а не те, що вона робить. */
    const fileInput=panel.querySelector('input[type=file]');
    const catBefore=S.CAT, scenBefore=S.SCEN;
    const feed=async(name,body)=>{
      const f=new w.File([body],name,{type:'application/json'});
      Object.defineProperty(fileInput,'files',{value:[f],configurable:true});
      fileInput.dispatchEvent(new w.Event('change'));
      await new Promise(r=>setTimeout(r,120));
    };

    await feed('мій_сценарій.json', JSON.stringify({scenarios:[
      {id:'t1',grp:'g',title:'т',cats:[],main:'',order:[],open:'',who:'',mood:'',mode:''}]}));
    T('вибраний файл названий у рядку джерела',
      /сценарії — мій_сценарій\.json/.test(panel.textContent));
    T('каталог при цьому лишився застосунковим',
      /каталог — дані застосунку/.test(panel.textContent));
    T('вибраний файл НЕ потрапляє в дані застосунку',
      S.CAT===catBefore && S.SCEN===scenBefore);

    await feed('зламаний.json', '{\n  "a": 1,\n  ,\n}');
    T('зламаний JSON дає людський текст із рядком',
      /зламаний\.json/.test(panel.textContent) && /рядок 3/.test(panel.textContent));
    T('зламаний файл не витісняє попередній вибір',
      /сценарії — мій_сценарій\.json/.test(panel.textContent));

    await feed('чуже.json', JSON.stringify({a:1,b:2}));
    T('чужий файл названий по-людськи',
      /не схоже ні на каталог, ні на сценарії/.test(panel.textContent));

    [...panel.querySelectorAll('button')]
      .find(b=>b.textContent==='Дані застосунку').click();
    T('повернення до даних застосунку скидає вибір',
      /сценарії — дані застосунку/.test(panel.textContent));
  }

  /* Ряд вибору файлу закритий кодом куратора так само, як і вивід:
     перевіряється на СВІЖІЙ панелі, бо та, що вище, вже відімкнена.
     Носій береться від САМОГО поля файлу — пошук «перший div, у якому є
     кнопка» дає зовнішній accbody, а він видимий завжди. */
  {
    const fresh=w.dataCheck();
    const row=fresh.querySelector('input[type=file]').parentElement;
    T('до коду куратора рядок файлу не показаний', row.style.display==='none');
  }

  console.log(`\n✓${ok} · ✗${bad}`+(INJECT?' (inject)':''));
  process.exit(bad?1:0);
})().catch(e=>{console.error('впало:',e); process.exit(1)});
