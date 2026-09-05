/* смоук кроку В — читає ВИХІД, не перераховує (1.15, пастка 4) */
const fs=require('fs'); let ok=0,bad=0;
const A=(c,m)=>{c?(ok++,console.log('✓ '+m)):(bad++,console.log('✗ '+m))};
const h=fs.readFileSync(process.argv[2]||'ae_out/index.html','utf8');
const inj=process.argv.includes('--inject');
let src=h; if(inj) src=src.replace("headers['x-ae-code'] = encodeURIComponent(NET.get())","void 0");

A(/headers\['x-ae-code'\] = encodeURIComponent/.test(src),'кодове слово йде заголовком, %-кодованим');
A(/localStorage\.getItem\('ae_net_code'\)/.test(src),'кодове слово живе в localStorage');
A(!/endpoint\.startsWith\('\/'\)/.test(src),'евристика startsWith знята');
A(/!S\.cfg\.model\.workerReady/.test(src),'стан читається з оголошення workerReady');
A(/r\.headers\.get\('x-ae-model'\)/.test(src),'модель читається з заголовка відповіді');
A(/Кодове слово мережі не підходить/.test(src),'401 без ключа більше не бреше про Groq');
A(!/needCode/.test(src),'ворота не вимагають кодового слова');
A(/r\.status===503/.test(src),'503 з воркера показується текстом воркера');

// перевірка в другий бік: у прямому режимі заголовок кодового слова НЕ шлеться
A(/if\(key\) headers\['Authorization'\][\s\S]{0,400}else if\(NET\.get\(\)\)/.test(src),
  'ключ і кодове слово взаємовиключні');
A(/decodeURIComponent/.test(require('fs').readFileSync('worker/ae-proxy.js','utf8')),
  'воркер декодує кодове слово');
A(/if \(env\.AE_CODE\) \{/.test(require('fs').readFileSync('worker/ae-proxy.js','utf8')),
  'без AE_CODE перевірки немає — кодове слово необовʼязкове');

/* ── драбина воркера: пара effort/стеля ────────────────────────────────
   Інваріант той самий, що в smoke_step2, але той стереже БРАУЗЕРНИЙ бік
   (config.json). Драбину воркера не стеріг ніхто, і після Ж-3 з'ясувалось,
   що вона мовчки лишалась на старих значеннях. Роздуми рахуються в ту саму
   стелю: effort != 'none' зі стелею < 800 обриває JSON на півслові.
   Перевіряємо ВСІ сходинки, включно з вимкненими: вимкнена сходинка
   вмикається одним словом, і в цей момент перевіряти вже пізно. */
let W = require('fs').readFileSync('worker/ae-proxy.js','utf8');
/* ІНʼЄКЦІЯ А (12.12-є: ціль — ДАНІ драбини, не код і не згадка про неї).
   Повертає сходинці qwen3.6 значення, якого її модель не приймає. Пара
   effort/стеля при цьому лишається цілою — тому червоніти має рівно одне
   твердження, про перелік дозволених значень. */
if(inj) W = W.replace("effort: { client: 'none', judge: 'none' }",
                      "effort: { client: 'low', judge: 'low' }");
/* ІНʼЄКЦІЯ Б: старт судді переїжджає на роль клієнта. Обидва старти
   лишаються на ввімкнених сходинках — червоніє тільки твердження про
   «рівно один старт на роль, і старти різні». */
if(inj) W = W.replace("first: ['judge']", "first: ['client']");

/* ІНʼЄКЦІЯ В: стеля судді повертається до тієї, на якій розбір згорів.
   Пара effort/стеля при цьому ціла (1200 >= 800) і глобальна стеля її не
   ріже — тому червоніє рівно одне твердження, про вимір. */
if(inj) W = W.replace(/judge: 2000 \}/g, "judge: 1200 }");

/* Розбираємо сходинку цілком: модель, прапорець, старт за роллю, пара
   effort/стеля. Раніше регекс брав лише effort і tokens — і `tested` не
   бачив узагалі, тому гейт казав «сходинок 4» там, де ввімкнена була одна.
   Число оголошених і число ввімкнених — різні числа, обидва потрібні. */
const rungRe = /\{\s*model:\s*'([^']+)',\s*tested:\s*(true|false),\s*first:\s*\[([^\]]*)\],[\s\S]*?effort:\s*\{\s*client:\s*'(\w+)',\s*judge:\s*'(\w+)'\s*\},\s*tokens:\s*\{\s*client:\s*(\d+),\s*judge:\s*(\d+)\s*\}/g;
const rungs = [...W.matchAll(rungRe)].map(m => ({
  model:m[1], on:m[2]==='true',
  first:(m[3].match(/'(\w+)'/g)||[]).map(s=>s.replace(/'/g,'')),
  ce:m[4], je:m[5], ct:+m[6], jt:+m[7] }));
const on = rungs.filter(r => r.on);
A(rungs.length >= 4, `драбина розібрана: оголошено сходинок ${rungs.length}`);
A(rungs.every(r => (r.ce==='none' || r.ct>=800) && (r.je==='none' || r.jt>=800)),
  'парність effort/стеля на ВСІХ сходинках драбини: не-none вимагає >=800');
A(rungs.length>0 && rungs[0].ce==='low',
  'сходинка 0: клієнт мислить (Ж-3). Повертаєш none — повертай і стелю 700');

/* Скільки сходинок ВВІМКНЕНО. Розведення ролей вимагає щонайменше двох:
   на одній вони знову ділять хвилинне відро токенів. */
A(on.length >= 2, `драбина ввімкнена: сходинок ${on.length} із ${rungs.length}`);

/* Рівно один старт на роль, і старти різні. Одне твердження, не два:
   обидві половини падають від тієї самої причини (12.12-ї). */
const starts = {};
for(const r of rungs) for(const f of r.first) (starts[f]=starts[f]||[]).push(r.model);
A(['client','judge'].every(x => (starts[x]||[]).length===1) &&
  starts.client && starts.judge && starts.client[0]!==starts.judge[0],
  'старт за роллю: у клієнта і судді рівно по одній сходинці, і це різні моделі');
A(rungs.filter(r=>r.first.length).every(r=>r.on),
  'кожен оголошений старт стоїть на ВВІМКНЕНІЙ сходинці');

/* ── дозволені значення effort, по моделях ─────────────────────────────
   Постачальник приймає різні переліки для різних моделей і відмовляє
   кодом 400, а 400 драбиною не сходить. Тобто сходинка з чужим значенням
   не деградує, а обриває запит — і побачити це можна тільки піном або
   тут. Читаємо перелік із того самого файла: там його дім. */
const okRe = /\{\s*match:\s*\/((?:[^/\\]|\\.)+)\/,\s*values:\s*\[([^\]]*)\]/g;
const table = [...W.matchAll(okRe)].map(m => ({
  re:new RegExp(m[1]), vals:(m[2].match(/'(\w+)'/g)||[]).map(s=>s.replace(/'/g,'')) }));
A(table.length >= 3, `перелік дозволених effort розібраний: записів ${table.length}`);
const badEffort = [];
for(const r of rungs){
  const rec = table.find(t => t.re.test(r.model));
  if(!rec) continue;
  for(const v of [r.ce, r.je]) if(!rec.vals.includes(v)) badEffort.push(r.model+':'+v);
}
A(badEffort.length===0,
  'кожне значення effort належить переліку своєї моделі'+
  (badEffort.length?' — чужі: '+badEffort.join(', '):''));

/* Оголошення без споживача — не захист. Тому окремо: воркер справді
   провертає список за роллю і справді питає перелік у момент запиту. */
A(/\(r\.first \|\| \[\]\)\.includes\(role\)/.test(W),
  'воркер обирає старт саме полем first, а не порядком сходинок');
A(/if \(!effortOk\(r\.model, effort\)\)/.test(W),
  'воркер звіряє effort із переліком у циклі драбини, а не лише на словах');

/* ── стеля судді ───────────────────────────────────────────────────────
   У режимі json_schema обрізаної відповіді не буває: постачальник віддає
   400 json_validate_failed, тобто порожнечу замість розбору. Живий прогін
   уперся в 1100 і згорів, тому 1200 — доведено замало. Число нижче — не
   смак, а нижня межа з виміру. */
A(rungs.every(r => r.jt >= 2000),
  `стеля судді на всіх сходинках >= 2000 (виміряно: 1100 не вистачило)`);
const lim = +(W.match(/maxTokens:\s*(\d+)/)||[])[1];
A(lim >= Math.max(...rungs.map(r=>r.jt)),
  `глобальна стеля ${lim} не ріже рольову — інакше рольова стає прикрасою`);
A(/json_validate_failed/.test(W) && /cheap\[0\] !== effort/.test(W),
  'воркер переспитує ту саму модель найдешевшими роздумами на обрізаному JSON');

/* ── ОДНА СТЕЛЯ, ОДИН ДІМ ──────────────────────────────────────────────
   Через воркер стелю призначає драбина. Доки браузер теж називав своє
   число, воркер брав Math.min — і мовчки вигравала нижча (config 1100
   проти драбини 1200). Розходження не червоніло ніде: коментар у config
   стверджував протилежне тому, що робив код. Тому вимога тут: у режимі
   воркера цих двох полів у тілі запиту немає взагалі. */
A(/if\(key\)\{[\s\S]{0,200}body\.max_completion_tokens/.test(src),
  'стеля і роздуми йдуть у тіло ТІЛЬКИ з ключем — через воркер їх немає');

/* ── ЄДИНА КОПІЯ ПРАВИЛ (6а-1) ────────────────────────────────────
   Правила винесені в tools/ae_rules.js, щоб командний рядок, браузерна
   перевірка і редактор судили за одним набором. Ризик на роки: хтось
   вписує правило назад в обгортку, і копії розходяться мовчки — жоден
   гейт не червоніє, просто три місця починають казати різне про той
   самий файл. Читаємо ТЕКСТ обгортки, а не її поведінку. */
const wrapPath = require('path').join(require('path').dirname(process.argv[1]),'ae_validate.js');
let wrap = fs.readFileSync(wrapPath,'utf8');
if(inj) wrap = wrap.replace("const {validate}=require('./ae_rules.js');",
                            "const validate=()=>({out:[],ok:0,warn:0,err:0});  E('своє правило');");
A(/require\(['"]\.\/ae_rules\.js['"]\)/.test(wrap),
  'обгортка тягне правила з ae_rules.js, а не носить свої');
A(!/(^|[^\w.])[EWO]\(/m.test(wrap),
  'в обгортці немає власних E()/W()/O() — правил вона не відростила');
/* Те, заради чого правила виносились: ae_rules.js мусить читатись
   браузером. Один require/process/console — і 6а-2 падає на порожньому
   місці. Перевіряємо саме це, а не факт існування файлу: зниклий файл
   і так валить ae_validate.js, окреме твердження про нього ніколи б не
   почервоніло. */
let rules = fs.readFileSync(wrapPath.replace('ae_validate.js','ae_rules.js'),'utf8');
if(inj) rules = rules.replace('function validate(', "const fs=require('fs');\nfunction validate(");
A(!/\brequire\s*\(|\bprocess\.|\bconsole\./.test(rules.replace(/\/\*[\s\S]*?\*\/|\/\/.*/g,'')),
  'ae_rules.js без Node: ні require, ні process, ні console — читається браузером');

console.log(`\n✓${ok} · ✗${bad}`+(inj?' (inject)':''));
process.exit(bad?1:0);
