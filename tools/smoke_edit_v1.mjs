/* AE-Simulator · гейт воркера редактора (крок «в-1»)
   живе доки: worker/ae-edit.js лишається суддею без запису
   запуск: node tools/smoke_edit_v1.mjs <тека збірки>
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
const ENV = { AE_EDIT_CODE: 'гейт', AE_ORIGINS: O };
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

r = await mod.fetch(post({ catalog: cat, scenarios: scen }, 'гейт', 'https://chuzhyi.example'), ENV);
is('чужий Origin не пускається', r.status === 403);

r = await mod.fetch(post({ catalog: cat, scenarios: scen }, 'не той'), ENV);
is('чужий код не пускається', r.status === 403);

r = await mod.fetch(post({ catalog: cat, scenarios: scen }), { AE_ORIGINS: O });
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

console.log('\n' + (bad ? '✗' : '✓') + ' smoke_edit_v1: ✓' + ok + ' · ✗' + bad);
process.exit(bad ? 1 : 0);
