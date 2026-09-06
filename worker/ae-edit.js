/* ═══════════════════════════════════════════════════════════════════
   AE-Simulator · воркер редактора — крок «в-2»: СУД І ЗАПИС
   живе доки: форма для Олі не готова (крок «в-3»)

   Що робить:
     1. пускає тільки зі знанням коду редактора
     2. читає з репо носії закритих переліків (див. CARRIERS)
     3. судить надіслані дані ТИМИ САМИМИ правилами, що ганяються на push,
        і ТИМ САМИМ викликом на чотири аргументи
     4. на прохання пише один файл із білого списку в репо
     5. каже українською

   ⚠ ПЕРЕВІРКИ ДОМЕНУ (Origin) ТУТ НЕМАЄ — І ЦЕ НАВМИСНО. Не повертати.
   Origin підставляє браузер, і зі скрипта на сторінці його не підробити —
   але поза браузером він набирається руками: один рядок curl пише в ньому
   що завгодно. Тобто проти будь-кого, хто вміє скрипт, охорони нуль.
   Єдиний клас атак, від якого Origin рятує по-справжньому, — чужа сторінка,
   що ходить сюди на КУКИ жертви. Куків тут немає: право правити дані
   доводиться кодом у заголовку, а чужа сторінка коду не знає. Двері вже
   в глухій стіні, замок на них нічого не додає.
   Ціна ж у цієї перевірки реальна: вона відмовляє МОВЧКИ. Порожня змінна
   виглядає точно як зламаний редактор (уже наступали: S10, цілий раунд
   діагностики), а при переїзді репо на інший акаунт домен зміниться — і
   редактор помре в руках людини, яка не має способу це зрозуміти.
   ⚠ Дзеркально: в ae-proxy Origin ЛИШАЄТЬСЯ. Там під ним порожнеча —
   AE_CODE знято, — тож він єдине, що стоїть між публічним URL і квотою
   Groq. Різна опора під перевіркою — різне рішення.

   Пише в репо через Contents API — рівно ОДИН файл за виклик, і тільки
   з білого списку нижче. Один PUT = один коміт = атомарно; напівстану
   «перший файл ліг, другий упав» не існує за конструкцією.

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
                    Це ЄДИНА охорона воркера.
     AE_GH_TOKEN    fine-grained PAT GitHub. Encrypt. Один репозиторій,
                    Contents: Read and write. Класичний repo-токен НЕ брати.
     ⚠ ОБИДВА — Encrypt (Secret), не Plain text. Plain text належить
       wrangler.toml і стирається першим же деплоєм: саме так згорів
       AE_ORIGINS (S10→S11), і воркер мовчки відмовляв усім.

   Деплой: push у main → GitHub Actions → wrangler. Руками нічого не
   вставляється; вставлений руками код перезапише наступний push.
   ═══════════════════════════════════════════════════════════════════ */

import rules from '../tools/ae_rules.js';

/* Межа тіла. Каталог із 181 позицією важить десятки кілобайт; два мегабайти —
   це стеля з великим запасом, за якою вже не дані, а помилка або чужий запит. */
const MAX_BODY = 2 * 1024 * 1024;

/* Зірочка безпечна саме тому, що охорони на Origin немає свідомо: браузер
   боїться '*' лише разом із куками, а їх тут немає — ключ їде явним
   заголовком, який чужа сторінка підставити не може. Vary більше не
   потрібен: відповідь від Origin не залежить, кешувати нема чого розділяти. */
function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, x-ae-edit-code',
    'Access-Control-Max-Age': '86400'
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

/* ═══ КУДИ ПИШЕМО ═══════════════════════════════════════════════════
   Адреса репозиторію — константа в коді, НЕ змінна оточення. Свідомо:
   кожна змінна в дашборді — окрема точка, яка вмирає мовчки (уже згорів
   AE_ORIGINS). Токен при переїзді на інший акаунт усе одно перевипускається
   руками, тож константа поруч не додає роботи, зате видима в коді.
   ⚠ МІГРАЦІЯ (крок «М»): міняти тут, разом із AE_GH_TOKEN.

   ⚠ БІЛИЙ СПИСОК — ЦЕ МЕЖА БЕЗПЕКИ, А НЕ ЗРУЧНІСТЬ. Шлях НІКОЛИ не
   приходить від клієнта. Клієнт називає бік ('catalog' | 'scenarios'),
   шлях розкладає воркер. Приймали б шлях ззовні — той, хто знає
   AE_EDIT_CODE, переписав би .github/workflows/*.yml, а це виконуваний
   код у CI, де лежить токен Cloudflare. Слабкий код редактора став би
   повним контролем над інфраструктурою. Третього значення не існує. */
const REPO   = 'Konst-Andre/AE-Simulator';
const BRANCH = 'main';
const PATHS  = { catalog: 'data/catalog.json', scenarios: 'data/scenarios.json' };

/* ⚠ НОСІЇ ЗАКРИТИХ ПЕРЕЛІКІВ — ЧИТАЮТЬСЯ ТУТ, НЕ ПРИХОДЯТЬ У ТІЛІ.
   `rules.validate` бере чотири аргументи. Два останні — носії переліків
   (характери · щаблі). Без них правила не мовчать, вони кажуть ⚠ — а ⚠
   у цьому воркері свідомо НЕ блокує запис. Два розумні рішення склались
   у дірку: виклик на два аргументи робив інертними рівно ті правила, що
   охороняють `character` і рядок `mood`, і сирітський характер (✗ у CI)
   проходив сюди як ⚠. У застосунку він дає виняток на старті — білий
   екран усім, від збереження, яке сказало «Дані в порядку».
   Носії беруться З РЕПО, а не з тіла запиту: те, що надсилає клієнт,
   клієнт може й не надіслати — і перевірка знову впаде в ⚠, тепер уже
   на його розсуд. Носій, який можна не передати, — не носій.
   Недоступний носій = ВІДМОВА, однакова для перегляду і для запису:
   форма, що судить м'якше за збереження, вчить довіряти зеленому. */
const CARRIERS = { chars: 'prompts/characters.md', cfg: 'config.json' };

const GH = 'https://api.github.com/repos/' + REPO + '/contents/';

/* ⚠ btoa тут падає: український текст — не ISO-8859-1. Той самий шрам, що
   й кирилиця в заголовку HTTP. Тільки байти через TextEncoder.
   Чанками по 32 КБ: spread на 36-тисячний масив кладе стек. */
function toBase64(text) {
  const bytes = new TextEncoder().encode(text);
  let bin = '';
  for (let i = 0; i < bytes.length; i += 0x8000) {
    bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  }
  return btoa(bin);
}

function ghHeaders(token) {
  return {
    'Authorization': 'Bearer ' + token,
    /* ⚠ Без User-Agent GitHub віддає 403, який читається як «поганий токен»
       і посилає шукати проблему не там. */
    'User-Agent': 'ae-edit-worker',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
  };
}

/* Помилки GitHub перекладаються на людські рядки тут, а не в застосунку:
   те, що побачить Оля, складається в одному місці. */
function ghError(status) {
  if (status === 401 || status === 403)
    return 'Доступ до репозиторію не працює: токен прострочений або відкликаний.';
  if (status === 404)
    return 'Файл у репозиторії не знайдено. Схоже, його перейменували.';
  if (status === 409 || status === 422)
    return 'Файл змінився, поки ви його правили. Відкрийте заново і повторіть.';
  return 'Репозиторій відповів помилкою ' + status + '. Спробуйте ще раз.';
}

/* Носій береться сирим текстом (`Accept: …raw`), а не JSON-обгорткою з
   base64: правилам потрібен саме текст, і зайве декодування — зайве місце
   для мовчазної поломки на кирилиці.
   Токен додається, якщо він є. Публічний репозиторій читається й без
   нього — але без токена GitHub рахує 60 запитів на годину, тож у
   робочому режимі токен присутній і це не запасний шлях, а звичайний. */
async function carrier(path, token) {
  const head = ghHeaders(token);
  head.Accept = 'application/vnd.github.raw';
  if (!token) delete head.Authorization;
  const res = await fetch(GH + path + '?ref=' + BRANCH, { headers: head });
  if (!res.ok) return { ok: false, status: res.status };
  return { ok: true, text: await res.text() };
}

async function commit(side, dataObj, note, token) {
  const path = PATHS[side];
  const url  = GH + path;
  const head = ghHeaders(token);

  /* sha наявного файлу обовʼязковий при оновленні: без нього GitHub вважає
     запит створенням і відмовляє. Він же і є захистом від затирання чужої
     правки — розбіжність дасть 409. */
  const cur = await fetch(url + '?ref=' + BRANCH, { headers: head });
  if (!cur.ok) return { ok: false, status: cur.status, text: ghError(cur.status) };
  const sha = (await cur.json()).sha;

  /* Стабільне форматування: інакше кожен запис давав би diff на весь файл. */
  const text = JSON.stringify(dataObj, null, 2) + '\n';

  const message = 'дані з редактора: ' + path
    + (note ? '\n\n' + String(note).replace(/\s+/g, ' ').slice(0, 200) : '');

  const put = await fetch(url, {
    method: 'PUT',
    headers: { ...head, 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, content: toBase64(text), sha, branch: BRANCH })
  });
  if (!put.ok) return { ok: false, status: put.status, text: ghError(put.status) };

  const res = await put.json();
  return { ok: true, path, sha: res.content && res.content.sha };
}

async function handle(request, env) {
  const cors = corsHeaders();

  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });

  /* Твердження, що має спосіб почервоніти: якщо секрет не покладено, воркер
     каже це прямо, а не пускає всіх мовчки. Мовчазний дозвіл виглядав би
     як робота і був би дірою. */
  if (!env.AE_EDIT_CODE) {
    return say(500, 'Редактор не налаштований: секрет AE_EDIT_CODE не встановлено.', cors);
  }

  if (request.method === 'GET') {
    return new Response(JSON.stringify({
      ok: true,
      step: 'в-2',
      rules: typeof rules.validate === 'function' ? 'живі' : 'НЕ ЗІБРАЛИСЬ',
      /* ⚠ Було `writes: false` при живому записі — рядок стану, що каже
         неправду, гірший за відсутній: гейт заморозив брехню зеленою
         (12.11-в, ознака «коментар стверджує, що це не працює»). */
      writes: true,
      carriers: [CARRIERS.chars, CARRIERS.cfg]
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

  /* ⚠ Носії читаються ДО суду і однаково для перегляду й запису.
     `body.characters` / `body.config`, якщо вони колись приїдуть у тілі,
     тут свідомо не читаються: див. коментар до CARRIERS. */
  let chars, cfg;
  {
    const [c1, c2] = await Promise.all([
      carrier(CARRIERS.chars, env.AE_GH_TOKEN),
      carrier(CARRIERS.cfg,   env.AE_GH_TOKEN)
    ]).catch(() => [{ ok: false, status: 0 }, { ok: false, status: 0 }]);
    if (!c1.ok) return say(502, 'Не вдалося прочитати перелік характерів із '
      + 'репозиторію (' + CARRIERS.chars + '). Без нього судити не можна.', cors);
    if (!c2.ok) return say(502, 'Не вдалося прочитати налаштування із '
      + 'репозиторію (' + CARRIERS.cfg + '). Без них судити не можна.', cors);
    chars = c1.text;
    try { cfg = JSON.parse(c2.text); }
    catch (_) { return say(502, 'Налаштування в репозиторії не читаються як JSON.', cors); }
  }

  let r;
  try { r = rules.validate(body.catalog, body.scenarios, chars, cfg); }
  catch (err) {
    return say(422, 'Дані не вдалося розібрати: ' + String(err && err.message || err), cors);
  }

  const verdict = {
    ok: r.err === 0,
    ok_count: r.ok, warn: r.warn, err: r.err,
    out: r.out,
    saved: null
  };

  /* ═══ ЗАПИС ═══════════════════════════════════════════════════════
     Немає save — поведінка кроку в-1: тільки суд. Це не сумісність
     заради сумісності: попередній перегляд без запису потрібен формі. */
  const side = body.save;
  if (side) {
    if (side !== 'catalog' && side !== 'scenarios') {
      return say(400, 'Зберігати можна тільки каталог або сценарії.', cors);
    }
    /* ⚠ Помилка блокує запис, попередження — ні. Помилка означає, що дані
       зламані для застосунку; попередження — що вони незручні, але робочі.
       Впертись у стіну через кому не там людина не повинна. */
    if (r.err > 0) {
      verdict.text = 'Знайдено помилок: ' + r.err + '. Не збережено.';
      return new Response(JSON.stringify(verdict), {
        status: 200, headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors }
      });
    }
    if (!env.AE_GH_TOKEN) {
      return say(500, 'Редактор не налаштований: секрет AE_GH_TOKEN не встановлено.', cors);
    }
    let done;
    try { done = await commit(side, body[side], body.note, env.AE_GH_TOKEN); }
    catch (e) { return say(502, 'Не вдалося достукатись до репозиторію.', cors); }
    if (!done.ok) return say(done.status === 404 ? 404 : 409, done.text, cors);
    verdict.saved = done.path;
  }

  verdict.text = r.err
    ? 'Знайдено помилок: ' + r.err + '. Дані не годяться.'
    : (verdict.saved ? 'Збережено. ' : 'Дані в порядку.')
      + (r.warn ? ' Попереджень: ' + r.warn + '.' : '');

  return new Response(JSON.stringify(verdict), {
    status: 200,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors }
  });
}

export default { fetch: handle };
