#!/usr/bin/env python3
"""x100_composer_popover_apply_v1.py · AE-Simulator · S82 · щабель 3 · крок 3 досьє композера
живе доки: X100 не заступлено наступним index (тоді — archive/apply/)

Три заготовки → одна кнопка «Підказка фрази ▾» + popover над нею (паспорт §7 qaMode:"one").
· popover="auto" у верхньому шарі: .panel{overflow:hidden} не ріже; клік повз / Esc закривають (нативно)
· позиція — anchor positioning (top span-right, flip-block, --qa-fit для вузьких); фолбек без підтримки — JS на `toggle`
· фраза ВСТАВЛЯЄТЬСЯ в поле в позицію курсора (не відправляється, ТЗ S68 §7); «…» в кінці = допиши сам;
  баг X97 `text + '. '` («Як давно це триває?. ») знято
· кнопка неактивна при S.ended || S.waiting — перемальовка E2 на відповідь клієнта не знесе відкритий список
· набір фраз — WWHAM (для кого · симптоми · як довго · що пробували · інші ліки) + порадити + завершити;
  живе в коді E2_PHRASES — у дані окремим кроком (досьє крок 4)
· role="menu" НЕ ставимо: вимагає скриптової навігації стрілками; кнопки в групах — чесна семантика
Тінь popover `0 12px 32px #1C1E2429` — СТАВКА (паспорта нема), до device-тесту.

Вхід : AE_WORK_index_X99_v2.html (md5 9139d574ec7853f3c7c875b0c69c777c)
Запуск: python3 x100_composer_popover_apply_v1.py <вхід.html> <вихід.html>
Ідемпотентність: маркер — `const E2_PHRASES` (П94).
"""
import sys, hashlib
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
MARK = "const E2_PHRASES"
if MARK in s:
    open(dst, 'w', encoding='utf-8').write(s)
    print('вже застосовано · md5', hashlib.md5(s.encode()).hexdigest()); sys.exit(0)
if "class:'comp-isl'" not in s: sys.exit('✗ вхід без острова X99')

def rep(old, new):
    global s
    c = s.count(old)
    if c != 1: sys.exit(f'✗ якір {c}≠1: {old[:70]!r}')
    s = s.replace(old, new)

# 1 · дані фраз
rep("""const E2_STARTERS = [['Уточнити симптоми', 'Підкажіть, будь ласка, які саме симптоми'],
  ['Запропонувати супутній засіб', 'Можу запропонувати супутній засіб'],
  ['Уточнити курс', 'Уточню, будь ласка, курс лікування']];""",
"""/* X100 · фрази для popover композера. WWHAM: для кого · що турбує · як довго · що вже пробували ·
   інші ліки. Зачини, не готові відповіді — інакше тренажер розвʼязує задачу за фармацевта.
   «…» в кінці = фармацевт дописує сам. Дім у даних — окремим кроком (досьє композера, крок 4). */
const E2_PHRASES = [
  ['Розпитати', ['Підкажіть, для кого препарат?', 'Що саме турбує?', 'Як давно це триває?',
                 'Чи вже щось приймали від цього?', 'Чи приймаєте зараз інші ліки?']],
  ['Порадити',  ['Можу запропонувати до цього…', 'Щодо курсу прийому: …']],
  ['Завершити', ['Якщо за кілька днів не покращиться — зверніться до лікаря.']]];""")

# 2 · кнопка + popover + вставка
rep("""  const starters = E2_STARTERS.map(([label, text]) => {
    const b = el('button', {type:'button', onclick:() => { ta.value = text + '. ' + ta.value; st.draft = ta.value; ta.focus(); }}, [label]);
    b.disabled = S.ended; return b; });""",
"""  /* X100 · фрази — одна кнопка і popover над нею (досьє композера, крок 3) */
  const putPhrase = t => {
    const cont = t.endsWith('…'), add = cont ? t.slice(0, -1).trimEnd() + ' ' : t + ' ';
    const v = ta.value, a = ta.selectionStart ?? v.length, b = ta.selectionEnd ?? a;
    const pre = v.slice(0, a), glue = pre && !/\\s$/.test(pre) ? ' ' : '';
    ta.value = pre + glue + add + v.slice(b); st.draft = ta.value;
    const pos = (pre + glue + add).length;
    pop.hidePopover(); ta.focus(); ta.setSelectionRange(pos, pos); };
  const pop = el('div', {id:'e2-qa', popover:'auto', class:'qa-pop', ontoggle:e => {
      if(e.newState !== 'open' || CSS.supports('anchor-name', '--a')) return;
      const r = trig.getBoundingClientRect();   /* фолбек без anchor positioning */
      pop.style.left = r.left + 'px'; pop.style.top = Math.max(8, r.top - pop.offsetHeight - 8) + 'px'; }},
    E2_PHRASES.map(([title, list]) => el('div', {class:'qa-grp', role:'group', 'aria-label':title}, [
      el('div', {class:'qa-h', 'aria-hidden':'true', text:title}),
      ...list.map(t => el('button', {type:'button', class:'qa-item', onclick:() => putPhrase(t)}, [t]))])));
  const trig = el('button', {type:'button', class:'qa-trig', popovertarget:'e2-qa', disabled:S.ended || S.waiting},
    ['Підказка фрази ', el('span', {'aria-hidden':'true', text:'▾'})]);""")
rep("        el('div', {class:'quick-phrases'}, starters),\n",
    "        el('div', {class:'quick-phrases'}, [trig]), pop,\n")

# 3 · CSS — у секцію X99
rep(".v2 .well { position:relative;",
""".v2 .comp-isl .qa-trig { anchor-name:--e2qa; }
/* X100 · popover фраз. Тінь — СТАВКА (паспорта нема). --qa-fit: коли праворуч не вміщається (390px:
   виліт на 11px, заміряно headless) — по центру над якорем на всю ширину; десктоп лишається під кнопкою. */
@position-try --qa-fit { position-area:top span-all; justify-self:center; }
.v2 .qa-pop { position-anchor:--e2qa; position-area:top span-right; position-try-fallbacks:flip-block, --qa-fit; inset:auto; margin:0 0 8px; width:max-content; max-width:min(380px, calc(100vw - 24px)); max-height:min(60vh, 420px); overflow:auto; padding:6px; border:1px solid #E7E7E7; border-radius:14px; background:#fff; color:var(--anc-text); box-shadow:0 12px 32px #1C1E2429; }
.v2 .qa-pop .qa-grp + .qa-grp { margin-top:4px; padding-top:4px; border-top:1px solid #E7E7E7; }
.v2 .qa-pop .qa-h { padding:6px 10px 2px; color:var(--anc-gray); font-size:11px; font-weight:600; }
.v2 .qa-pop .qa-item { display:block; width:100%; padding:8px 10px; border:0; border-radius:8px; background:transparent; color:var(--anc-text); font-size:13px; text-align:left; cursor:pointer; }
.v2 .qa-pop .qa-item:hover { background:#1C1E240A; }
.v2 .qa-pop .qa-item:focus-visible { outline:2px solid var(--anc-blue); outline-offset:-2px; }
.v2 .well { position:relative;""")

for bad in ('E2_STARTERS', 'starters'):
    if bad in s: sys.exit('✗ лишився ' + bad)
open(dst, 'w', encoding='utf-8').write(s)
print('✓ X100 · md5', hashlib.md5(s.encode()).hexdigest())
