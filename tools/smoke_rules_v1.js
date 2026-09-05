/* AE-Simulator · смоук ПРАВИЛ даних — зуби tools/ae_rules.js
   живе доки: ae_rules.js лишається єдиним тілом правил про дані

   запуск:  node tools/smoke_rules_v1.js
            node tools/smoke_rules_v1.js --inject   (має впасти)

   ⚠ Цей смоук — єдиний, що НЕ потребує jsdom і не має зашитого BASE:
   він читає файли відносно кореня репо. Тому він єдиний із смоуків їде
   в CI (.github/workflows/perevirka.yml) поруч із ae_validate.

   ЩО ВІН ДОВОДИТЬ І ЧОГО НЕ ДОВОДИТЬ.
   Доводить: правило рядка mood має шлях падіння — на підкинутому рядку
   validate() червоніє, і червоніє САМЕ ТИМ повідомленням, не сусіднім.
   НЕ доводить: що правило виконане. Перевірка лексична, перифраз вона
   не бачить (ae_rules.js, розділ mood; wsd 12.12-и). */
const fs=require('fs'), path=require('path');
const ROOT=path.join(__dirname,'..');
const {validate}=require('./ae_rules.js');
const INJECT=process.argv.includes('--inject');

let ok=0,bad=0;
const T=(n,c)=>{ c?(ok++,console.log('  ✓ '+n)):(bad++,console.log('  ✗ '+n)); };
const J=f=>JSON.parse(fs.readFileSync(path.join(ROOT,f),'utf8'));

const CAT=J('data/catalog.json'), SCN=J('data/scenarios.json'), CFG=J('config.json');
const CH=fs.readFileSync(path.join(ROOT,'prompts/characters.md'),'utf8');

/* ⚠ Ін'єкція цілиться в ДАНІ, не в тіло правил (12.12-є). Тіло правил
   лишається тим самим об'єктом на всі прогони — інакше смоук перевіряв би
   свою підміну, а не файл, який поїде в продакшн. */
/* ⚠ Рядок ін'єкції навмисно НЕ збігається з жодним рядком секції «зуби»
   нижче: перша редакція ставила той самий текст, і одна з дев'яти перевірок
   ставала зеленою через те, що її помилка вже сиділа в базовому рівні —
   дві ін'єкції в одному прогоні гасили одна одну (12.12-ж). */
if(INJECT) SCN.scenarios[0].mood='Сьогодні тривожна.';

const base=validate(CAT,SCN,CH,CFG);
const moodMsgs=v=>v.out.filter(m=>m.lvl==='err'&&/ mood /.test(m.msg)).map(m=>m.msg);

console.log('\n— чинні дані —');
T('носії прочитані, характерів дев\u02bcять', /## /.test(CH) && Object.keys(CFG.schemas.turn.schema.properties.step.enum).length===5);
/* Твердження, яке валить --inject. Решта тверджень нижче міряють ДЕЛЬТУ
   до цього рівня, тому вони переживають ін'єкцію — і це навмисно:
   впасти має рівно одне (12.12-д). */
T('на чинних даних правило mood не має жодного ✗', moodMsgs(base).length===0);
/* Твердження про ІНВАРІАНТ, не про стан: ✓-рядок є тоді і тільки тоді,
   коли червоних немає. Написане як «рядок надрукований», воно падало б
   разом із твердженням вище — тобто не мало б власного шляху падіння
   і лише подвоювало б той самий факт. Так воно ловить свій дефект:
   зелений підсумок, надрукований попри знайдені помилки. */
T('✓-рядок про mood є рівно тоді, коли ✗ немає',
  base.out.some(m=>m.lvl==='ok'&&/^рядки mood за правилом/.test(m.msg)) === (moodMsgs(base).length===0));
T('mood звірений з обома носіями',
  base.out.filter(m=>m.lvl==='ok'&&/^mood звірений з переліком/.test(m.msg)).length===2);

console.log('\n— носій приходить аргументом, копії в коді немає (12.11-а) —');
const src=fs.readFileSync(path.join(ROOT,'tools/ae_rules.js'),'utf8').toLowerCase();
const names=[...CH.replace(/<!--[\s\S]*?-->/g,'').matchAll(/^## (.+)$/gm)].map(m=>m[1].trim());
const steps=CFG.schemas.turn.schema.properties.step.enum;
T('жодної назви характеру в тілі правил', !names.some(n=>src.includes(n.toLowerCase())));
T('жодної назви щабля в тілі правил',     !steps.some(s=>src.includes(s.toLowerCase())));
const noChars=validate(CAT,SCN,null,CFG), noCfg=validate(CAT,SCN,CH,null);
T('без носія характерів — ⚠ вголос, не мовчазний пропуск',
  noChars.out.some(m=>m.lvl==='warn'&&/mood не звірений з назвами характерів/.test(m.msg)));
T('без config — ⚠ вголос про щаблі',
  noCfg.out.some(m=>m.lvl==='warn'&&/mood не звірений з назвами щаблів/.test(m.msg)));
T('виклик на два аргументи не падає (сторінка і воркер кличуть так)',
  (()=>{ try{ const r=validate(CAT,SCN); return r.warn>=2; }catch(e){ return false; } })());

console.log('\n— зуби правила: девʼять ін\u02bcєкцій у дані, кожна ізольовано —');
/* Кожен прогін бере СВОЮ глибоку копію даних і міняє РІВНО ОДИН рядок
   (12.12-ж). Дві правки в одному прогоні гасили б твердження одна одної:
   зайва помилка від першої зробила б підрахунок другої зеленим випадково. */
const shot=(name, mood, want, n)=>{
  const copy=JSON.parse(JSON.stringify(SCN));
  copy.scenarios[0].mood=mood;
  const got=moodMsgs(validate(CAT,copy,CH,CFG));
  const fresh=got.filter(m=>!moodMsgs(base).includes(m));
  const hit=fresh.filter(m=>want.test(m));
  T(name+' → ✗ саме про це ('+fresh.length+' нових, чекали '+n+')',
    hit.length>0 && fresh.length===n);
  if(!(hit.length>0&&fresh.length===n)) fresh.forEach(m=>console.log('      · '+m));
};

shot('довжина понад межу',
  'Ааааааа бббббб вввввв гггггг дддддд ееееее жжжжжж зззззз ииииии ккккккк ллллллл мммммм ннннн.',
  /довжина \d+ > 90/, 1);
shot('пряма мова в лапках',
  'Мовчить, потім «ммммм».', /пряма мова в лапках/, 1);
shot('цифра в рядку',
  'Прийшла о 7 ранку.', /цифра в рядку/, 1);
shot('межа знань клієнта',
  'Питає про приріст.', /межа знань/, 1);
/* Дві ін'єкції замість однієї: перевірка має дві гілки, і одна з них
   могла б мовчати непоміченою. Перша дає назву дослівно, як у носії;
   друга — ту саму назву в іншій формі, і зловити її може тільки корінь. */
shot('назва характеру дослівно як у носії',
  'Дуже ' + names[1].toLowerCase() + '.', /назва характеру/, 1);
shot('назва характеру в іншій формі — ловить лише корінь',
  'Дуже поспішала сьогодні.', /корінь назви характеру/, 1);
shot('назва щабля уголос',
  'Насторожена, мовчить.', /назва щабля/, 1);
shot('повтор того, що клієнт скаже сам',
  'Стримана, ' + (SCN.scenarios[0].open.match(/[а-яїієґ\u02bc']{6,}/i)||['ххххххх'])[0].toLowerCase() + '.',
  /повторює open/, 1);
/* Восьма: дослівний дубль. Тут очікуємо ДВІ помилки, і це не послаблення —
   однаковий рядок неминуче дає і «дубль», і попарний перетин слів. Число
   названо, а не підігнано: якби воно було 1, це означало б, що попарна
   перевірка мовчить. */
shot('дослівний дубль сусіднього рядка',
  SCN.scenarios[1].mood, /дослівний дубль/, 2);

console.log('\n'+(bad?'✗':'✓')+' підсумок: ✓'+ok+' · ✗'+bad+(INJECT?'   [inject: чекаємо рівно ✗1 — «на чинних даних правило mood не має жодного ✗»]':''));
process.exit(bad?1:0);
