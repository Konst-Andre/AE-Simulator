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
const LADDER = [
  { model: 'qwen/qwen3.8-27b',    tested: true,  reasoning_effort: 'none', reasoning_format: 'hidden' },
  { model: 'qwen/qwen3.6-27b',    tested: false, reasoning_effort: 'none', reasoning_format: 'hidden' },
  { model: 'openai/gpt-oss-120b', tested: false, reasoning_effort: 'low',  reasoning_format: 'hidden' },
  { model: 'openai/gpt-oss-20b',  tested: false, reasoning_effort: 'low',  reasoning_format: 'hidden' }
];

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
      'Access-Control-Allow-Headers': 'Content-Type, x-ae-code',
      'Access-Control-Expose-Headers': 'x-ae-model, x-ae-rung, retry-after',
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
  if (env.AE_CODE && request.headers.get('x-ae-code') !== env.AE_CODE)
    return say(401, 'Кодове слово мережі не підходить. Перевірте його в налаштуваннях.', null, cors);

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

  const base = {
    messages: msgs,
    response_format: rf,
    temperature:       clamp(inBody.temperature,       LIM.temperature,       0.7),
    top_p:             clamp(inBody.top_p,             LIM.top_p,             0.8),
    presence_penalty:  clamp(inBody.presence_penalty,  LIM.presence_penalty,  0.3),
    max_completion_tokens: Math.min(LIM.maxTokens, inBody.max_completion_tokens || 700)
  };

  const rungs = LADDER.filter(r => r.tested);
  if (!rungs.length) return say(500, 'Жодна модель не увімкнена на сервері.', null, cors);

  let lastRetry = null, lastMsg = '';

  for (let i = 0; i < rungs.length; i++) {
    const r = rungs[i];
    const body = {
      ...base,
      model: r.model,
      reasoning_effort: r.reasoning_effort,
      reasoning_format: r.reasoning_format
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
          'x-ae-rung': String(i)      // 0 = основна; >0 = резерв
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
