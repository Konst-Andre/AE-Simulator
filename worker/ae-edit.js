/* ═══════════════════════════════════════════════════════════════════
   AE-Simulator · воркер редактора — крок «в-1»: ТІЛЬКИ СУДДЯ
   живе доки: редактор не вміє писати (крок «в-2» додає коміт у репо)

   Що робить:
     1. пускає тільки свої домени (Origin) і тільки зі знанням коду редактора
     2. судить надіслані дані ТИМИ САМИМИ правилами, що ганяються на push
     3. каже українською

   Чого НЕ робить (свідомо, це крок «в-2»):
     · нічого нікуди не пише. Токена GitHub тут немає й бути не може —
       ризик збірки й ризик токена розведені по різних кроках навмисно

   ⚠ ПРАВИЛА НЕ КОПІЮЮТЬСЯ. Рядок import нижче — це не посилання на копію,
   а вказівка збирачеві вкласти сюди ТІЛО tools/ae_rules.js. Копії немає,
   тож і розійтись немає чому. Правку правил підхоплює наступний деплой.

   ⚠ ДЕФОЛТНИЙ ІМПОРТ, не іменований. tools/ae_rules.js — класичний скрипт
   із хвостом module.exports; для збирача це CommonJS, і цілий module.exports
   віддається саме дефолтним імпортом. Іменований (import {validate}) на
   CommonJS тримається на здогадці збирача про форму експорту — форма, що
   мовчки ламається при зміні збирача.

   Секрети (Cloudflare → Workers → ae-edit → Settings → Variables):
     AE_EDIT_CODE   код редактора. Encrypt. НЕ той самий, що AE_CODE:
                    право говорити з моделлю ≠ право правити дані.
     AE_ORIGINS     дозволені домени через кому, БЕЗ слеша в кінці.
                    напр: https://konst-andre.github.io

   Деплой: push у main → GitHub Actions → wrangler. Руками нічого не
   вставляється; вставлений руками код перезапише наступний push.
   ═══════════════════════════════════════════════════════════════════ */

import rules from '../tools/ae_rules.js';

/* Межа тіла. Каталог із 181 позицією важить десятки кілобайт; два мегабайти —
   це стеля з великим запасом, за якою вже не дані, а помилка або чужий запит. */
const MAX_BODY = 2 * 1024 * 1024;

function corsHeaders(request, env) {
  const origin = request.headers.get('Origin') || '';
  const allow = String(env.AE_ORIGINS || '')
    .split(',').map(s => s.trim()).filter(Boolean);
  const ok = allow.includes(origin);
  return {
    ok,
    headers: {
      'Access-Control-Allow-Origin': ok ? origin : 'null',
      'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, x-ae-edit-code',
      'Access-Control-Max-Age': '86400',
      'Vary': 'Origin'
    }
  };
}

/* Один вихід для всіх відмов: людський рядок українською, ніколи не голий
   код помилки. Те, що побачить Оля, складається тут, а не в застосунку. */
function say(status, text, cors) {
  return new Response(JSON.stringify({ ok: false, text }), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors }
  });
}

async function handle(request, env) {
  const { ok: originOk, headers: cors } = corsHeaders(request, env);

  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });

  if (!originOk) return say(403, 'Запит прийшов не з дозволеного домену.', cors);

  /* Твердження, що має спосіб почервоніти: якщо секрет не покладено, воркер
     каже це прямо, а не пускає всіх мовчки. Мовчазний дозвіл виглядав би
     як робота і був би дірою. */
  if (!env.AE_EDIT_CODE) {
    return say(500, 'Редактор не налаштований: секрет AE_EDIT_CODE не встановлено.', cors);
  }

  if (request.method === 'GET') {
    return new Response(JSON.stringify({
      ok: true,
      step: 'в-1',
      rules: typeof rules.validate === 'function' ? 'живі' : 'НЕ ЗІБРАЛИСЬ',
      writes: false
    }), { status: 200, headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors } });
  }

  if (request.method !== 'POST') return say(405, 'Такий тип запиту не приймається.', cors);

  /* Код їде заголовком у відсотковому кодуванні: кирилиця в заголовку HTTP
     інакше падає на «non ISO-8859-1 code point» — уже наступали в ae-proxy. */
  let given = request.headers.get('x-ae-edit-code') || '';
  try { given = decodeURIComponent(given); } catch (_) { /* лишаємо як прийшло */ }
  if (given !== String(env.AE_EDIT_CODE)) {
    return say(403, 'Код редактора не підходить.', cors);
  }

  const raw = await request.text();
  if (raw.length > MAX_BODY) return say(413, 'Дані завеликі для перевірки.', cors);

  let body;
  try { body = JSON.parse(raw); }
  catch (_) { return say(400, 'Надіслане не читається як JSON.', cors); }

  if (!body || (!body.catalog && !body.scenarios)) {
    return say(400, 'Не надіслано ні каталогу, ні сценаріїв.', cors);
  }

  /* ⚠ Обидва боки потрібні судді разом: правила звіряють сценарії з каталогом.
     Бік, якого не надіслали, підставити нізвідки — воркер стану не тримає. */
  if (!body.catalog || !body.scenarios) {
    return say(400, 'Судити можна тільки обидва файли разом: каталог і сценарії.', cors);
  }

  let r;
  try { r = rules.validate(body.catalog, body.scenarios); }
  catch (err) {
    return say(422, 'Дані не вдалося розібрати: ' + String(err && err.message || err), cors);
  }

  return new Response(JSON.stringify({
    ok: r.err === 0,
    ok_count: r.ok, warn: r.warn, err: r.err,
    out: r.out,
    text: r.err
      ? 'Знайдено помилок: ' + r.err + '. Дані не годяться.'
      : 'Дані в порядку.' + (r.warn ? ' Попереджень: ' + r.warn + '.' : '')
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors }
  });
}

export default { fetch: handle };
