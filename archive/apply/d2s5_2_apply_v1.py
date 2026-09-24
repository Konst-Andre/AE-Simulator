#!/usr/bin/env python3
"""d2s5_2_apply_v1.py · AE-Simulator · S86 · D2 крок 5.2 — HTML/CSS острова: смуга стану публікації + поле коду
живе доки: запечено в X106 (лежить в archive/apply/ як ланцюг)
Вхід: корінь AE (index.html X105 e9aae4d6…). Пише <вихід>/index.html.
· #m-sync — дія в потоці задачі (actionable inline, Carbon): стан запису S.epub (busy · stale · fail · conflict · code)
  лишається на екрані, доки не зроблено дію; успіх — тостом (5.3). Окремо від #m-pub: той — проблеми ДАНИХ, цей — ЗАПИСУ.
· поле коду #f-code усередині смуги: type=password, autocomplete=off, БЕЗ name (iOS Keychain — як старий редактор :3819);
  значення в розмітку НЕ пишеться (секрет не йде в innerHTML) — 5.3 ставить .value з EDITKEY.
· усе приховане ([hidden]); JS, що показує, — крок 5.3. Кожна заміна — assert ×1. Повтор на виході = відмова (П34).
Запуск: python3 d2s5_2_apply_v1.py <корінь AE> <тека виходу>
"""
import sys, hashlib, pathlib
root, out = map(pathlib.Path, sys.argv[1:3]); out.mkdir(parents=True, exist_ok=True)
t = (root/'index.html').read_text(encoding='utf-8')
assert hashlib.md5(t.encode()).hexdigest().startswith('e9aae4d6'), 'вхід не X105'

def sub(s, R):
    for a, b in R:
        n = s.count(a); assert n == 1, (n, a[:70]); s = s.replace(a, b)
    return s

CSS_A = ".v2 .a2v2 .pub-why button{border:0;background:none;padding:0;color:var(--anc-blue);font:inherit;font-weight:700;text-decoration:underline;flex:none}"
CSS = CSS_A + """
/* D2 крок 5.2 · смуга запису: тон bad — червона (як pub-why), busy — нейтральна; переноситься, не ріже текст */
.v2 .a2v2 .pub-sync{grid-column:1 / -1;display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;min-width:0;padding:8px 10px;border:1px solid #E9B8AC;border-radius:9px;background:var(--loss-5);color:var(--loss);font-size:12.5px;line-height:1.4}
.v2 .a2v2 .pub-sync[data-tone="busy"]{border-color:var(--anc-border);background:#fff;color:var(--anc-gray)}
.v2 .a2v2 .pub-sync .t{flex:1 1 320px;min-width:0;overflow-wrap:anywhere}
.v2 .a2v2 .pub-sync .lines{flex:1 1 100%;min-width:0;color:var(--anc-text-2);overflow-wrap:anywhere}
.v2 .a2v2 .pub-sync .lines:empty{display:none}
.v2 .a2v2 .pub-sync .code{display:flex;align-items:center;gap:8px;flex:0 1 320px;min-width:0;color:var(--anc-text);font-weight:600}
.v2 .a2v2 .pub-sync .code>span{white-space:nowrap}
.v2 .a2v2 .pub-sync .code .in{flex:1 1 auto;min-width:0;padding:6px 10px;font-weight:400}
.v2 .a2v2 .pub-sync .btn{min-height:32px;padding:0 12px;flex:none}
/* [hidden] — ОСТАННІМ: .code і .btn мають ту саму вагу й display, і правило вище за текстом програвало б */
.v2 .a2v2 .pub-sync[hidden],.v2 .a2v2 .pub-sync [hidden]{display:none}"""

HTML_A = '<div class="pub-why" id="m-pub" hidden></div>'
HTML = HTML_A + """
    <div class="pub-sync" id="m-sync" role="status" aria-live="polite" data-tone="bad" hidden><span class="t" id="m-sync-t"></span><div class="lines" id="m-sync-l"></div><label class="code" id="m-code" hidden><span>Код редактора</span><input class="in" type="password" id="f-code" autocomplete="off" placeholder="ключ запису" aria-describedby="m-sync-t"></label><button type="button" class="btn" id="resync" hidden>Звірити ще раз</button></div>"""

t = sub(t, [(CSS_A, CSS), (HTML_A, HTML)])
(out/'index.html').write_text(t, encoding='utf-8')
print('index.html', hashlib.md5(t.encode()).hexdigest())
