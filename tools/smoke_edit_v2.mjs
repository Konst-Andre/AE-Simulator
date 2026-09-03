/* AE-Simulator · гейт воркера редактора (крок «в-1»)
   живе доки: worker/ae-edit.js лишається суддею без запису
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
const src = fs.readFileSync(file, 'utf8');
const mod = (await import(path.resolve(file))).default;

const cat  = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/catalog.json'), 'utf8'));
const scen = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/scenarios.json'), 'utf8'));

/* Еталон береться з правил, не з памʼяті автора гейта. */
const require = createRequire(import.meta.url);
const want = require(path.join(ROOT, 'tools/ae_rules.js')).validate(cat, scen);

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

let r = await mod.fetch(new Request('https://x/', { headers: { Origin: O } }), ENV);
let j = await r.json();
is('GET каже, що живий', r.status === 200 && j.ok === true);
is('правила зібрались', j.rules === 'живі', j.rules);
is('запис вимкнений', j.writes === false);

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

/* ═══ ЗАПИС (крок в-2) ═══════════════════════════════════════════════
   Справжній GitHub у гейті не чіпається: fetch підмінений. Перевіряємо не
   «чи відповів GitHub», а що саме воркер до нього ВІДПРАВИВ — заголовки,
   sha, кодування. Це і є те, що ламається мовчки. */
const real = globalThis.fetch;
let calls = [];
const mockGH = (putStatus = 200, getStatus = 200) => {
  calls = [];
  globalThis.fetch = async (url, opts = {}) => {
    calls.push({ url: String(url), opts });
    const j = (o, st) => new Response(JSON.stringify(o), { status: st,
      headers: { 'Content-Type': 'application/json' } });
    if ((opts.method || 'GET') === 'GET') {
      return getStatus === 200 ? j({ sha: 'СТАРИЙ_SHA' }, 200) : j({ message: 'no' }, getStatus);
    }
    return putStatus === 200 ? j({ content: { sha: 'НОВИЙ_SHA' } }, 200) : j({ message: 'no' }, putStatus);
  };
};
const restore = () => { globalThis.fetch = real; };
const put = () => calls.find(c => (c.opts.method || 'GET') === 'PUT');

/* Без save GitHub не чіпається взагалі — інакше кожен перегляд у формі
   робив би коміт. */
mockGH();
r = await mod.fetch(post({ catalog: cat, scenarios: scen }), ENV);
is('без save — у репо не лізе', calls.length === 0);

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
is('чужий шлях відкинуто', r.status === 400 && calls.length === 0);

mockGH();
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'prompts/judge.md' }), ENV);
is('шлях поза білим списком відкинуто', r.status === 400 && calls.length === 0);

/* Помилка блокує запис. Каталог ламаємо справжньою поломкою — знімаємо
   назву позиції, це та сама помилка, яку ловлять правила на push. */
{
  const brokenCat = JSON.parse(JSON.stringify(cat));
  const cats = brokenCat.categories || brokenCat;
  const firstCat = Object.keys(cats).find(k => Array.isArray((cats[k] || {}).items) && cats[k].items.length);
  delete cats[firstCat].items[0].n;
  const w = require(path.join(ROOT, 'tools/ae_rules.js')).validate(brokenCat, scen);
  mockGH();
  r = await mod.fetch(post({ catalog: brokenCat, scenarios: scen, save: 'catalog' }), ENV);
  j = await r.json();
  is('зламані дані в репо не потрапляють',
     w.err > 0 && calls.length === 0 && j.saved === null, 'помилок у даних: ' + w.err);
}

mockGH();
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'scenarios' }),
                    { AE_EDIT_CODE: 'гейт' });
j = await r.json();
is('без токена — червоніє, а не мовчить',
   r.status === 500 && /AE_GH_TOKEN/.test(j.text) && calls.length === 0);

mockGH(409);
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'scenarios' }), ENV);
j = await r.json();
is('409 → людський рядок про чужу правку', /змінився/.test(j.text || ''), j.text);

mockGH(200, 401);
r = await mod.fetch(post({ catalog: cat, scenarios: scen, save: 'scenarios' }), ENV);
j = await r.json();
is('401 → сказано про токен, а не «щось пішло не так»', /токен/.test(j.text || ''), j.text);

restore();

console.log('\n' + (bad ? '✗' : '✓') + ' smoke_edit_v2: ✓' + ok + ' · ✗' + bad);
process.exit(bad ? 1 : 0);
