/* ═══════════════════════════════════════════════════════════════════
   AE-Simulator · проксі до Groq
   живе доки: доки застосунок ходить у модель не напряму

   Що робить:
     1. пускає тільки свої домени (Origin) і тільки зі знанням кодового слова
     2. ховає ключ Groq — він у секретах, у браузер не потрапляє
     3. складає тіло запиту САМ: модель і межі бере звідси, не з браузера
     4. драбина моделей — квота вичерпана або модель зникла → наступна сходинка
     5. каже українською, коли не може відповісти

   Чого НЕ робить (свідомо):
     · не рахує запити — на free tier стелю тримає сам Groq, дубль не додає захисту
     · не тримає стану — ні KV, ні лічильників. Це крок 5 (Куратор)

   Секрети (Cloudflare → Settings → Variables):
     GROQ_KEY     ключ Groq. Encrypt.
     AE_CODE      кодове слово мережі, одне на всіх. Encrypt.
     AE_ORIGINS   дозволені домени через кому, БЕЗ слеша в кінці. Plain text.
                  напр: https://konst-andre.github.io,https://ae.pages.dev

   Деплой: Cloudflare → Workers → Create → Edit code → вставити цей файл.
   Після переїзду на Pages: покласти як functions/api/chat.js і замінити
   останній блок на:  export const onRequestPost = c => handle(c.request, c.env);
   ═══════════════════════════════════════════════════════════════════ */

/* ── ДРАБИНА ──────────────────────────────────────────────────────────
   Порядок: спершу найближчі за поведінкою, потім найстійкіші.
   Preview-моделі Groq знімає з коротким попередженням — тому дві останні
   сходинки Production, вони і є страховка від зникнення, а не від квоти.

   tested: false = сходинка ВИМКНЕНА. Вмикати тільки після живого прогону
   сценарію на ній: неперевірена сходинка не рятує, а мовчки підміняє
   продукт іншим (клієнт може заговорити російською, і це виглядатиме
   як робота, а не як поломка).
   ─────────────────────────────────────────────────────────────────── */
/* ДВІ РОЛІ, ДВА ПРОФІЛІ.
   Клієнту роздуми потрібні, але дешеві. Спершу тут стояв 'none' — гіпотеза
   була, що жива людина відповідає рефлекторно і швидкість робить її схожою
   на людину. Живий прогін (крок Ж-3) показав протилежне: без роздумів клієнт
   не зважує аргумент фармацевта, а просто тримає позицію. З 'low' відповіді
   стали помітно доречнішими, тому сходинка 0 переведена на 'low'.
   Суддя робить іншу роботу: звіряє, що сталось, із числами. Тому effort і
   стеля токенів залежать від ролі, яку браузер називає заголовком x-ae-role.

   ⚠ ПАРА ОБОВ'ЯЗКОВА: роздуми рахуються в ту саму стелю, тому будь-який
   effort, крім 'none', вимагає tokens >= 800. Розірвеш пару — JSON обірветься
   на півслові, і людина побачить «відповідь не читається» замість репліки.
   Це стереже smoke_step3 по ВСІХ сходинках, не лише активній.

   `reasoning_format:'hidden'` мислення НЕ вимикає — він лише не повертає
   ланцюжок у відповіді. Вимикає його саме effort 'none'.
   qwen3.8-27b приймає none | default | low | medium | high.
   gpt-oss приймає лише low | medium | high — 'none' там неможливий,
   тому в цих сходинок клієнтський профіль стоїть на 'low'.

   Роль приходить ІЗ БРАУЗЕРА, але значення бере воркер зі свого списку:
   чужий запит не може попросити 'high' і вигребти квоту роздумами. */
const LADDER = [
  { model: 'qwen/qwen3.8-27b',    tested: true,  reasoning_format: 'hidden',
    effort: { client: 'low',  judge: 'low' },    tokens: { client: 800, judge: 1100 } },
  { model: 'qwen/qwen3.6-27b',    tested: false, reasoning_format: 'hidden',
    effort: { client: 'none', judge: 'default' },tokens: { client: 700, judge: 1100 } },
  { model: 'openai/gpt-oss-120b', tested: false, reasoning_format: 'hidden',
    effort: { client: 'low',  judge: 'medium' }, tokens: { client: 800, judge: 1200 } },
  { model: 'openai/gpt-oss-20b',  tested: false, reasoning_format: 'hidden',
    effort: { client: 'low',  judge: 'medium' }, tokens: { client: 800, judge: 1200 } }
];

/* Список ролей закритий. Невідома роль — це клієнт, а не помилка:
   старий браузер заголовка не шле взагалі, і має працювати далі. */
const ROLES = ['client', 'judge'];

const GROQ = 'https://api.groq.com/openai/v1/chat/completions';

/* Межі. Браузер може просити м'якші значення, але не жорсткіші за ці —
   інакше чужий запит виставить max_completion_tokens 65536 і вигребе
   добову норму токенів за десяток викликів. */
const LIM = {
  maxTokens: 1200,
  msgs: 40,
  chars: 60000,
  temperature: [0, 1.2],
  top_p: [0.1, 1],
  presence_penalty: [-0.5, 1.0]
};

const clamp = (v, [lo, hi], dflt) =>
  (typeof v === 'number' && isFinite(v)) ? Math.min(hi, Math.max(lo, v)) : dflt;

function corsHeaders(origin, env) {
  const allow = String(env.AE_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
  const ok = origin && allow.includes(origin);
  return {
    ok,
    headers: {
      'Access-Control-Allow-Origin': ok ? origin : 'null',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, x-ae-code, x-ae-role',
      'Access-Control-Expose-Headers': 'x-ae-model, x-ae-rung, x-ae-role, retry-after',
      'Access-Control-Max-Age': '86400',
      'Vary': 'Origin'
    }
  };
}

const say = (status, text, extra, cors) => new Response(
  JSON.stringify({ error: { message: text } }),
  { status, headers: { 'Content-Type': 'application/json', ...cors, ...(extra || {}) } }
);

async function handle(request, env) {
  const origin = request.headers.get('Origin');
  const { ok, headers: cors } = corsHeaders(origin, env);

  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
  if (request.method !== 'POST')    return say(405, 'Тільки POST.', null, cors);

  /* Origin. Той самий домен — Origin може не прийти зовсім (Pages Functions),
     тоді пускаємо: same-origin запит уже під нашим контролем. */
  if (origin && !ok) return say(403, 'Запит із чужого домену.', null, cors);

  if (!env.GROQ_KEY) return say(500, 'Ключ моделі не налаштований на сервері.', null, cors);
  /* Кодове слово. Якщо змінної AE_CODE немає — перевірки немає взагалі.
     Браузер шле слово %-кодованим (заголовки HTTP несуть тільки латиницю),
     тому декодуємо перед звіркою. */
  if (env.AE_CODE) {
    let got = request.headers.get('x-ae-code') || '';
    try { got = decodeURIComponent(got); } catch { /* лишаємо як є */ }
    if (got !== env.AE_CODE)
      return say(401, 'Кодове слово мережі не підходить. Перевірте його в налаштуваннях.', null, cors);
  }

  let inBody;
  try { inBody = await request.json(); }
  catch { return say(400, 'Запит не читається.', null, cors); }

  const msgs = inBody && inBody.messages;
  if (!Array.isArray(msgs) || !msgs.length) return say(400, 'Порожній запит.', null, cors);
  if (msgs.length > LIM.msgs)              return say(413, 'Розмова задовга.', null, cors);
  if (JSON.stringify(msgs).length > LIM.chars) return say(413, 'Розмова задовга.', null, cors);

  const rf = inBody.response_format;
  if (!rf || rf.type !== 'json_schema')
    return say(400, 'Запит без схеми відповіді не приймається.', null, cors);

  const roleHdr = request.headers.get('x-ae-role') || '';
  const role = ROLES.includes(roleHdr) ? roleHdr : 'client';

  const base = {
    messages: msgs,
    response_format: rf,
    temperature:       clamp(inBody.temperature,       LIM.temperature,       0.7),
    top_p:             clamp(inBody.top_p,             LIM.top_p,             0.8),
    presence_penalty:  clamp(inBody.presence_penalty,  LIM.presence_penalty,  0.3)
  };

  const rungs = LADDER.filter(r => r.tested);
  if (!rungs.length) return say(500, 'Жодна модель не увімкнена на сервері.', null, cors);

  let lastRetry = null, lastMsg = '';

  for (let i = 0; i < rungs.length; i++) {
    const r = rungs[i];
    /* Стелю токенів беремо з профілю ролі, але браузер може попросити
       МЕНШЕ — більше ні. Роздуми рахуються в цю саму стелю, тому в судді
       вона вища: інакше JSON обірветься на півслові й людина побачить
       «відповідь не читається» замість розбору. */
    const roleCap = r.tokens[role];
    const asked   = inBody.max_completion_tokens;
    const body = {
      ...base,
      model: r.model,
      reasoning_effort: r.effort[role],
      reasoning_format: r.reasoning_format,
      max_completion_tokens: Math.min(LIM.maxTokens, roleCap,
        (typeof asked === 'number' && asked > 0) ? asked : roleCap)
    };

    let res;
    try {
      res = await fetch(GROQ, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + env.GROQ_KEY },
        body: JSON.stringify(body)
      });
    } catch (e) {
      lastMsg = 'мережа: ' + e.message;
      continue;                       // мережа лягла — пробуємо наступну
    }

    const text = await res.text();

    if (res.ok) {
      return new Response(text, {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          ...cors,
          'x-ae-model': r.model,
          'x-ae-rung': String(i),     // 0 = основна; >0 = резерв
          'x-ae-role': role           // яку роль воркер розпізнав
        }
      });
    }

    /* Далі по драбині йдемо ТІЛЬКИ на квоті й недоступності.
       Помилка змісту (400 — крива схема, задовгий промпт) на всіх моделях
       буде та сама: прокрутити її через драбину означає вигребти квоту
       вчетверо за один баг. Тому — віддаємо одразу. */
    const step = res.status === 429 || res.status >= 500 ||
                 (res.status === 404 && /model|decommission|not.?found/i.test(text));

    lastMsg = text.slice(0, 300);
    if (res.status === 429) lastRetry = res.headers.get('retry-after');

    if (!step) {
      return new Response(text, {
        status: res.status,
        headers: { 'Content-Type': 'application/json', ...cors, 'x-ae-model': r.model }
      });
    }
  }

  return say(
    503,
    lastRetry
      ? 'Денна норма звернень до моделі вичерпана. Спробуйте пізніше' +
        (lastRetry > 90 ? ' — приблизно за ' + Math.ceil(lastRetry / 60) + ' хв.' : '.')
      : 'Модель зараз недоступна. Спробуйте за кілька хвилин.',
    lastRetry ? { 'retry-after': lastRetry } : null,
    cors
  );
}

export default { fetch: handle };
