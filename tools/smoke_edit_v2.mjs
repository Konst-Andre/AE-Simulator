/* AE-Simulator · гейт воркера редактора (крок «в-2»)
   живе доки: worker/ae-edit.js судить і пише data/*.json
   запуск: node tools/smoke_edit_v2.mjs <тека збірки>
           (теку дає  wrangler deploy --dry-run --outdir <тека>)

   ⚠ Гейт ганяє ЗІБРАНОГО воркера, а не вихідний файл. Сенс саме в цьому:
   перевіряється, що збирач справді вклав тіло tools/ae_rules.js усередину.
   Перевірка вихідного файлу довела б лише те, що в ньому написано «import».

   ⚠ Очікуваних чисел вердикту гейт НЕ рахує сам (1.15, пастка 4): він бере
   їх із того самого tools/ae_rules.js, прогнаного окремо через ae_validate.
   Числа, вписані сюди руками, зеленіли б і на зміненому виводі.

   ⚠ Кирилицю як якір НЕ шукаємо: збирач екранує не-ASCII у \uXXXX, і пошук
   за українським рядком дає хибне падіння на цілій збірці. Якір — AE_RULES. */

import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

const dir = process.argv[2];
if (!dir) { console.error('вкажіть теку збірки'); process.exit(2); }

const file = fs.statSync(dir).isDirectory()
  ? path.join(dir, fs.readdirSync(dir).filter(f => f.endsWith('.js'))[0] || '')
  : dir;
if (!file || !fs.existsSync(file)) { console.error('збірки не знайдено в ' + dir); process.exit(2); }

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
let src = fs.readFileSync(file, 'utf8');

/* ═══ ІНʼЄКЦІЇ ═══════════════════════════════════════════════════════
   Гейт, який ніколи не червонів, доводить лише те, що він мовчить.
   Кожна інʼєкція ламає РІВНО ОДНЕ місце і мусить погасити РІВНО ОДНЕ
   твердження (12.12-д): перетин порожній, інакше це одне твердження і
   решта — прикраса (12.12-ї).
   ⚠ Чесно про межу: тут інʼєкція править ЗІБРАНИЙ КОД воркера, а не дані
   (12.12-є). Даних у цього гейта в тому сенсі немає — предмет охорони
   тут сам виклик правил і його аргументи. Якір, якого не знайдено,
   зупиняє прогін голосно; мовчазного «зеленого без інʼєкції» не буває.
   Запуск: node tools/smoke_edit_v2.mjs <тека> --inject=А */
const INJ = {
  'А': ['носій характерів не доїжджає до правил',
        'body.scenarios, chars, cfg', 'body.scenarios, void 0, cfg'],
  'Б': ['носій щаблів не доїжджає до правил',
        'body.scenarios, chars, cfg', 'body.scenarios, chars, void 0'],
  'В': ['недоступний носій перестає бути відмовою',
        'if (!c1.ok) return say(502', 'if (false && !c1.ok) return say(502'],
  'Г': ['тіло запиту підміняє носій з репо',
        'chars = c1.text;', 'chars = body.characters !== void 0 ? body.characters : c1.text;']
};
const flag = process.argv.find(a => a.startsWith('--inject'));
let loadFrom = path.resolve(file);
if (flag) {
  const key = (flag.split('=')[1] || '').trim();
  const rec = INJ[key];
  if (!rec) { console.error('інʼєкції «' + key + '» немає. Є: ' + Object.keys(INJ).join(' ')); process.exit(2); }
  const [name, from, to] = rec;
  if (!src.includes(from)) {
    console.error('якір інʼєкції не знайдено у збірці: ' + from);
    console.error('це не зелений прогін — це зламаний гейт. Читати збирача.');
    process.exit(2);
  }
  console.log('  ⇢ інʼєкція ' + key + ': ' + name);
  src = src.replace(from, to);
  loadFrom = path.join(path.dirname(loadFrom), 'inj_' + key + '_' + Date.now() + '.mjs');
  fs.writeFileSync(loadFrom, src);
}
const mod = (await import(loadFrom)).default;

const cat  = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/catalog.json'), 'utf8'));
const scen = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/scenarios.json'), 'utf8'));

/* Носії закритих переліків. Воркер бере їх із репо сам; гейт бере ті самі
   з диска — інакше еталон і вердикт рахувались би на різних даних, і
   збіг чисел нічого не доводив би. */
const CH_TEXT  = fs.readFileSync(path.join(ROOT, 'prompts/characters.md'), 'utf8');
const CFG_TEXT = fs.readFileSync(path.join(ROOT, 'config.json'), 'utf8');

/* Еталон береться з правил, не з памʼяті автора гейта.
   ⚠ ЧОТИРИ АРГУМЕНТИ. На двох це порівняння теж було б зеленим — воно
   лише звіряло б два однаково знезубрені виклики. */
const require = createRequire(import.meta.url);
const want = require(path.join(ROOT, 'tools/ae_rules.js'))
  .validate(cat, scen, CH_TEXT, JSON.parse(CFG_TEXT));

const O = 'https://konst-andre.github.io';
const ENV = { AE_EDIT_CODE: 'гейт', AE_GH_TOKEN: 'ghp_гейт' };
const post = (body, code = 'гейт', origin = O) => new Request('https://x/', {
  method: 'POST',
  headers: { Origin: origin, 'x-ae-edit-code': encodeURIComponent(code) },
  body: JSON.stringify(body)
});

let ok = 0, bad = 0;
const is = (name, cond, note = '') =>
  cond ? (ok++, console.log('  ✓ ' + name + (note ? ' · ' + note : '')))
       : (bad++, console.log('  ✗ ' + name + (note ? ' · ' + note : '')));

is('тіло правил усередині збірки', src.includes('AE_RULES'));

/* ═══ ПІДМІНА GitHub ═════════════════════════════════════════════════
   Справжній GitHub у гейті не чіпається: fetch підмінений. Перевіряємо не
   «чи відповів GitHub», а що саме воркер до нього ВІДПРАВИВ — заголовки,
   sha, кодування. Це і є те, що ламається мовчки.

   ⚠ Підміна стоїть ДО першого POST, а не перед блоком запису: відколи
   воркер читає носії з репо, будь-який POST ходить у мережу. Гейт, що
   ходить у мережу, падає від чужого збою і зеленіє від чужого кешу. */
const real = globalThis.fetch;
let calls = [];
const isCarrier = u => /prompts\/characters\.md|contents\/config\.json/.test(u);
/* carrier: {status, which, chars, cfg} — чим відповідати на носії.
   `which` (regex) ламає РІВНО ОДИН носій: інакше інʼєкція, що знімає
   охорону на першому, лишалась би невидимою за охороною другого. */
const mockGH = (putStatus = 200, getStatus = 200, carrier = {}) => {
  calls = [];
  globalThis.fetch = async (url, opts = {}) => {
    const u = String(url);
    calls.push({ url: u, opts });
    const j = (o, st) => new Response(JSON.stringify(o), { status: st,
      headers: { 'Content-Type': 'application/json' } });
    if (isCarrier(u)) {
      const hit = !carrier.which || carrier.which.test(u);
      const st = hit ? (carrier.status || 200) : 200;
      if (st !== 200) return j({ message: 'no' }, st);
      const body = u.includes('characters.md')
        ? (carrier.chars !== undefined ? carrier.chars : CH_TEXT)
        : (carrier.cfg   !== undefined ? carrier.cfg   : CFG_TEXT);
      return new Response(body, { status: 200 });
    }
    if ((opts.method || 'GET') === 'GET') {
      return getStatus === 200 ? j({ sha: 'СТАРИЙ_SHA' }, 200) : j({ message: 'no' }, getStatus);
    }
    return putStatus === 200 ? j({ content: { sha: 'НОВИЙ_SHA' } }, 200) : j({ message: 'no' }, putStatus);
  };
};
const restore = () => { globalThis.fetch = real; };
const put  = () => calls.find(c => (c.opts.method || 'GET') === 'PUT');
const gets = re => calls.filter(c => (c.opts.method || 'GET') === 'GET' && re.test(c.url));

mockGH();


let r = await mod.fetch(new Request('https://x/', { headers: { Origin: O } }), ENV);
let j = await r.json();
is('GET каже, що живий', r.status === 200 && j.ok === true);
is('правила зібрались', j.rules === 'живі', j.rules);
/* Було `writes === false` при живому записі: гейт заморозив брехню
   зеленою. Рядок стану, що суперечить коду, гірший за відсутній. */
is('GET каже про запис правду', j.writes === true);
is('GET називає носії', Array.isArray(j.carriers) && j.carriers.length === 2, String(j.carriers));

/* Твердження навмисно перевернуте (S11): охорона стоїть на коді, не на
   домені. Якщо цей рядок колись почервоніє — хтось повернув перевірку
   Origin, не прочитавши шапку воркера. Читати її, а не «лагодити» гейт. */
r = await mod.fetch(post({ catalog: cat, scenarios: scen }, 'гейт', 'https://chuzhyi.example'), ENV);
is('чужий Origin пускається — охорона не тут', r.status === 200);

is('дозвіл на читання віддається всім',
   r.headers.get('Access-Control-Allow-Origin') === '*',
   r.headers.get('Access-Control-Allow-Origin'));

r = await mod.fetch(post({ catalog: cat, scenarios: scen }, 'не той'), ENV);
is('чужий код не пускається', r.status === 403);

r = await mod.fetch(post({ catalog: cat, scenarios: scen }), {});
j = await r.json();
is('без секрета — червоніє, а не пускає', r.status === 500 && /AE_EDIT_CODE/.test(j.text));

r = await mod.fetch(post({ catalog: cat, scenarios: scen }), ENV);
j = await r.json();
is('вердикт збігається з ae_rules',
   j.ok_count === want.ok && j.warn === want.warn && j.err === want.err,
   '✓' + j.ok_count + ' · ⚠' + j.warn + ' · ✗' + j.err);
is('повідомлення українською', typeof j.text === 'string' && /[а-яїієґ]/i.test(j.text), j.text);

r = await mod.fetch(post({ catalog: cat }), ENV);
is('половина даних не судиться', r.status === 400);

r = await mod.fetch(post({}), ENV);
is('порожнє не судиться', r.status === 400);

r = await mod.fetch(new Request('https://x/', {
  method: 'POST', headers: { Origin: O, 'x-ae-edit-code': encodeURIComponent('гейт') },
  body: '{зламано'
}), ENV);
is('зламаний JSON — людський рядок', r.status === 400);

/* ═══ ЗАПИС ═══════════════════════════════════════════════════════ */

/* Без save GitHub не чіпається взагалі — інакше кожен перегляд у формі
   робив би коміт. */
mockGH();
r = await mod.fetch(post({ catalog: cat, scenarios: scen }), ENV);
/* Було `calls.length === 0`. Відколи носії читаються з репо, нуль запитів
   означав би, що носіїв не читали, — тобто це твердження почервоніло б
   саме на правильній поведінці. Судиться те, що й судилось: перегляд не
   торкається ДАНИХ і не комітить. */
is('без save — коміту немає і даних не чіпає',
   !put() && gets(/data\//).length === 0, 'запитів: ' + calls.length);

mockGH();
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'scenarios' }), ENV);
j = await r.json();
is('save: коміт стався', r.status === 200 && j.saved === 'data/scenarios.json', j.text);
is('пише саме той файл, який названо',
   !!put() && put().url === 'https://api.github.com/repos/Konst-Andre/AE-Simulator/contents/data/scenarios.json');
is('токен їде в заголовку', !!put() && /^Bearer /.test(put().opts.headers['Authorization']));
is('User-Agent є — інакше GitHub дасть 403', !!put() && !!put().opts.headers['User-Agent']);
is('sha з GET доїхав у PUT', !!put() && JSON.parse(put().opts.body).sha === 'СТАРИЙ_SHA');

/* Головна пастка кроку: btoa на кирилиці. Перевіряємо зворотним ходом —
   розкодували те, що реально пішло в GitHub, і звірили з оригіналом. */
{
  const sent = JSON.parse(put().opts.body).content;
  const back = new TextDecoder().decode(
    Uint8Array.from(atob(sent), ch => ch.charCodeAt(0)));
  let same = false;
  try { same = JSON.stringify(JSON.parse(back)) === JSON.stringify(scen); } catch (_) {}
  is('кирилиця вижила в base64', same);
}

/* Білий список: межа безпеки, а не зручність. */
mockGH();
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: '.github/workflows/deploy-edit.yml' }), ENV);
/* ⚠ Раніше тут стояло calls.length === 0. Відколи носії читаються з репо,
   нуль запитів означав би, що носіїв не читали. Предмет твердження той
   самий: чужий шлях не доходить до ДАНИХ і не комітить. */
is('чужий шлях відкинуто', r.status === 400 && !put() && gets(/data\//).length === 0);

mockGH();
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'prompts/judge.md' }), ENV);
is('шлях поза білим списком відкинуто', r.status === 400 && !put() && gets(/data\//).length === 0);

/* Помилка блокує запис. Каталог ламаємо справжньою поломкою — знімаємо
   назву позиції, це та сама помилка, яку ловлять правила на push. */
{
  const brokenCat = JSON.parse(JSON.stringify(cat));
  const cats = brokenCat.categories || brokenCat;
  const firstCat = Object.keys(cats).find(k => Array.isArray((cats[k] || {}).items) && cats[k].items.length);
  delete cats[firstCat].items[0].n;
  const w = require(path.join(ROOT, 'tools/ae_rules.js'))
    .validate(brokenCat, scen, CH_TEXT, JSON.parse(CFG_TEXT));
  mockGH();
  r = await mod.fetch(post({ catalog: brokenCat, scenarios: scen, save: 'catalog' }), ENV);
  j = await r.json();
  is('зламані дані в репо не потрапляють',
     w.err > 0 && !put() && j.saved === null, 'помилок у даних: ' + w.err);
}

mockGH();
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'scenarios' }),
                    { AE_EDIT_CODE: 'гейт' });
j = await r.json();
is('без токена — червоніє, а не мовчить',
   r.status === 500 && /AE_GH_TOKEN/.test(j.text) && !put());

mockGH(409);
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'scenarios' }), ENV);
j = await r.json();
is('409 → людський рядок про чужу правку', /змінився/.test(j.text || ''), j.text);

mockGH(200, 401);
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'scenarios' }), ENV);
j = await r.json();
is('401 → сказано про токен, а не «щось пішло не так»', /токен/.test(j.text || ''), j.text);

/* ═══ НОСІЇ ЗАКРИТИХ ПЕРЕЛІКІВ ══════════════════════════════════════
   Дірка, заради якої писався цей блок: виклик правил на ДВА аргументи.
   Правила на двох не мовчать — вони кажуть ⚠, а ⚠ у цьому воркері
   свідомо не блокує запис. Разом це робило інертними рівно ті перевірки,
   що охороняють `character` і рядок `mood`. Вердикт лишався зеленим. */

mockGH();
r = await mod.fetch(post({ catalog: cat, scenarios: scen }), ENV);
is('носії читаються з репо, обидва',
   gets(/characters\.md/).length === 1 && gets(/contents\/config\.json/).length === 1,
   'characters: ' + gets(/characters\.md/).length + ' · config: ' + gets(/contents\/config\.json/).length);

/* Носій, який можна прислати в тілі, — це носій, який можна НЕ прислати. */
mockGH();
r = await mod.fetch(post({ catalog: cat, scenarios: scen,
                          characters: '## вигаданий\n### ризик\nніякий\n' }), ENV);
j = await r.json();
/* Судиться ПРЕДМЕТ, а не числа: числа тут повторювали б сусіднє
   твердження «вердикт збігається з ae_rules» і падали б від тієї самої
   причини (12.12-ї). Носій із тіла містить один вигаданий характер —
   якби воркер його взяв, усі 43 сценарії стали б сирітськими. */
is('тіло не підміняє носій з репо',
   !j.out.some(m => m.lvl === 'err' && /характеру/.test(m.msg)),
   'помилок про характер: ' + j.out.filter(m => /характеру/.test(m.msg)).length);

/* Сирітський характер: у CI це ✗, і в застосунку це виняток на старті —
   білий екран усім. Через редактор він проходив як ⚠, тобто зберігався. */
{
  const s2 = JSON.parse(JSON.stringify(scen));
  const arr = s2.scenarios || s2;
  arr[0].character = 'характер_якого_немає_в_носії';
  mockGH();
  r = await mod.fetch(post({ catalog: cat, scenarios: s2, save: 'scenarios' }), ENV);
  j = await r.json();
  is('сирітський character не потрапляє в репо',
     j.err > 0 && j.saved === null && !put()
     && j.out.some(m => m.lvl === 'err' && /характеру/.test(m.msg)),
     'помилок: ' + j.err);
}

/* Рядок mood: усе, заради чого робились S17 і S18. Носій щаблів — config. */
{
  const s3 = JSON.parse(JSON.stringify(scen));
  const arr = s3.scenarios || s3;
  const firstChar = (CH_TEXT.match(/\n## (.+)/) || [, ''])[1].trim();
  arr[0].mood = firstChar + ' сьогодні зранку поспішає';
  mockGH();
  r = await mod.fetch(post({ catalog: cat, scenarios: s3, save: 'scenarios' }), ENV);
  j = await r.json();
  is('рядок mood судиться носіями, а не на віру',
     j.err > 0 && j.saved === null && !put()
     && j.out.some(m => m.lvl === 'err' && /mood/.test(m.msg)),
     'носій дав назву: «' + firstChar + '»');
}

/* Другий носій — окремий перелік і окреме твердження: щаблі живуть у
   config.json, характери в characters.md, і зникнення одного не мусить
   ховатись за перевіркою другого. */
{
  const s4 = JSON.parse(JSON.stringify(scen));
  const arr = s4.scenarios || s4;
  const cfgObj = JSON.parse(CFG_TEXT);
  const STEPS = cfgObj.schemas.turn.schema.properties.step.enum;
  arr[0].mood = 'сьогодні тримається як ' + STEPS[0] + ' від самого ранку';
  mockGH();
  r = await mod.fetch(post({ catalog: cat, scenarios: s4, save: 'scenarios' }), ENV);
  j = await r.json();
  is('носій щаблів має зуби в шляху запису',
     j.err > 0 && j.saved === null && !put()
     && j.out.some(m => m.lvl === 'err' && /щабля/.test(m.msg)),
     'носій дав щабель: «' + STEPS[0] + '»');
}

/* Недоступний носій — відмова, а не мовчазне послаблення правил. */
mockGH(200, 200, { status: 404, which: /characters\.md/ });
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'scenarios' }), ENV);
j = await r.json();
is('носій недоступний — відмова, а не м\'якший суд',
   r.status === 502 && !put() && gets(/data\//).length === 0, j.text);

/* Форма, що судить м\'якше за збереження, вчить довіряти зеленому. */
{
  mockGH();
  r = await mod.fetch(post({ catalog: cat, scenarios: scen }), ENV);
  const preview = await r.json();
  mockGH();
  r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'scenarios' }), ENV);
  const saved = await r.json();
  is('перегляд і запис судять однаково',
     preview.ok_count === saved.ok_count && preview.warn === saved.warn
     && preview.err === saved.err);
}

restore();

console.log('\n' + (bad ? '✗' : '✓') + ' smoke_edit_v2: ✓' + ok + ' · ✗' + bad);
process.exit(bad ? 1 : 0);
