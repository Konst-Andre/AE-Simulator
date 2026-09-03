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
const W = require('fs').readFileSync('worker/ae-proxy.js','utf8');
const rungRe = /effort:\s*\{\s*client:\s*'(\w+)',\s*judge:\s*'(\w+)'\s*\},\s*tokens:\s*\{\s*client:\s*(\d+),\s*judge:\s*(\d+)\s*\}/g;
const rungs = [...W.matchAll(rungRe)].map(m => ({
  ce:m[1], je:m[2], ct:+m[3], jt:+m[4] }));
A(rungs.length >= 4, `драбина розібрана: сходинок ${rungs.length}`);
A(rungs.every(r => (r.ce==='none' || r.ct>=800) && (r.je==='none' || r.jt>=800)),
  'парність effort/стеля на ВСІХ сходинках драбини: не-none вимагає >=800');
A(rungs.length>0 && rungs[0].ce==='low',
  'сходинка 0: клієнт мислить (Ж-3). Повертаєш none — повертай і стелю 700');

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
