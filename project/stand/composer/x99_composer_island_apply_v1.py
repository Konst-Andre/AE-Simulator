#!/usr/bin/env python3
"""x99_composer_island_apply_v1.py · AE-Simulator · S82 · щабель 3 · крок 1–2 досьє композера
живе доки: X99 не заступлено наступним index (тоді — archive/apply/)

Композер E2 стає островом. Числа — паспорт досьє §7 + вироки §8 (В-127…В-133, стик шапки),
вирок В-134 (S82): підпис «Enter — відправити» під островом прибрано.
· підлога `.composer` #1C1E240A, шва нема (В-127, В-69) · острів `.comp-isl` r28 · pad14 · без рамки (В-128)
  · тінь одним шаром 0 12 82 28 #008ecc 28% (В-130, В-132)
· втоплене поле `.well` r14 · #E7E7E7 · #1C1E24 3% (В-129) · кнопка всередині, 46×42 r12
· фокус глибиною `:focus-within` (В-131 — СТАВКА до device-тесту)
· гліф `#i-send` — стрілка вгору (В-133) · стик шапки both + hdLine 0 — лише `.dialogue`
· три заготовки в острові з токенами паспорта (28px, r12, #d1d1d1) — до popover (крок 3)
Селектори звужено: `.v2 textarea`, `.v2 .panel-head`, `.v2 .send` НЕ чіпаються (спільні).

Вхід : AE_WORK_index_X97_v1.html (md5 386394e6b2c7b57254712781f7438f46)
Запуск: python3 x99_composer_island_apply_v1.py <вхід.html> <вихід.html>
Ідемпотентність: маркер — `class:'comp-isl'` (П94): повтор на X99 → exit 0, файл без змін.
"""
import sys, hashlib
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
MARK = "class:'comp-isl'"
if MARK in s:
    open(dst, 'w', encoding='utf-8').write(s)
    print('вже застосовано · md5', hashlib.md5(s.encode()).hexdigest()); sys.exit(0)

def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: sys.exit(f'✗ якір {c}≠{n}: {old[:70]!r}')
    s = s.replace(old, new)

# 1 · підлога (В-127) — на місці старого правила; шов знято
rep(".v2 .composer { padding:0 19px 18px; border-top:1px solid var(--anc-border); background:#fff; }\n",
    ".v2 .composer { padding:14px 19px 16px; background:#1C1E240A; }\n")
# 2 · мертві після ходу: ряд поля і підпис (В-134)
rep(".v2 .composer-row { display:flex; gap:10px; }\n", "")
rep(".v2 .composer-note { display:flex; justify-content:flex-end; padding-top:9px; color:var(--anc-gray); font-size:11px; }\n",
    """/* ── X99 · КОМПОЗЕР-ОСТРІВ · досьє композера §7 паспорт + §8 вироки (S81), В-134 (S82) ──
   живе доки: device-тест 1920·1536·1280 не канонізував числа (тоді досьє видаляється, П123)
   Селектори навмисно вужчі за спільні `.v2 textarea` / `.v2 .panel-head` / `.v2 .send`. */
.v2 .comp-isl { --comp-isl-r:28px; padding:14px; border-radius:var(--comp-isl-r); background:#fff; box-shadow:0 12px 82px 28px #008ecc47; }
.v2 .comp-isl .quick-phrases { gap:8px; padding:0 0 10px; }
.v2 .comp-isl .quick-phrases button { min-height:28px; padding:0 12px; border:1px solid #d1d1d1; border-radius:12px; background:#fff; color:var(--anc-text); font-size:12px; font-weight:600; }
.v2 .well { position:relative; border:1px solid #E7E7E7; border-radius:14px; background:#1C1E2408; box-shadow:inset 0 0 4px 0 #0000001A, inset 0 -1px 0 0 #FFFFFFB3; }
/* В-131 · фокус глибиною, без кольору — СТАВКА */
.v2 .well:focus-within { border-color:#1C1E244D; box-shadow:inset 0 0 4px 0 #00000029, inset 0 -1px 0 0 #FFFFFFB3; }
.v2 .well textarea { display:block; width:100%; flex:none; min-height:72px; max-height:220px; field-sizing:content; overflow-y:auto; resize:none; padding:12px 68px 12px 14px; border:0; border-radius:14px; outline:none; background:transparent; line-height:1.45; }
.v2 .well textarea:disabled { background:transparent; color:var(--anc-gray); }
.v2 .well .send { position:absolute; right:14px; bottom:14px; width:46px; height:42px; border-radius:12px; background:var(--anc-yellow); box-shadow:0 3px 3px #1C1E243D; }
.v2 .well .send:disabled { background:var(--anc-border); color:var(--anc-gray-light); }
.v2 .well .send svg { width:23px; height:23px; }
/* стик шапки: both + hdLine 0 — лише розмова */
.v2 .dialogue .panel-head { position:relative; z-index:2; border-bottom:0; box-shadow:0 4px 8px -2px #1C1E241A; }
.v2 .dialogue .messages { box-shadow:inset 0 3px 5px -1px #1C1E241F; }
/* ── /X99 ── */
""")
# 3 · мобільна гілка
rep("  .v2 .composer { padding:0 12px 12px; }\n", "  .v2 .composer { padding:10px 12px 12px; }\n")
rep("  .v2 .composer-note { display:none; }\n", "")
# 4 · гліф (В-133)
rep('<symbol id="i-send" viewBox="0 0 24 24"><path d="m3 3 18 9-18 9 3-9-3-9Z"/><path d="M6 12h15"/></symbol>',
    '<symbol id="i-send" viewBox="0 0 24 24"><path d="M12 19V5"/><path d="M5.5 11.5 12 5l6.5 6.5"/></symbol>')
# 5 · розмітка
i = s.index("    el('div', {class:'composer'}, [\n      el('div', {class:'quick-phrases'}, starters),")
j = s.index("])])]);\n", i) + len("])])]);\n")
if s.count("el('div', {class:'composer-note'}") != 1: sys.exit('✗ composer-note')
s = s[:i] + ("    el('div', {class:'composer'}, [\n"
             "      el('div', {class:'comp-isl'}, [\n"
             "        el('div', {class:'quick-phrases'}, starters),\n"
             "        el('div', {class:'well'}, [ta, send])])])]);\n") + s[j:]
for bad in ('composer-row', 'composer-note'):
    if bad in s: sys.exit('✗ лишився ' + bad)
open(dst, 'w', encoding='utf-8').write(s)
print('✓ X99 · md5', hashlib.md5(s.encode()).hexdigest())
