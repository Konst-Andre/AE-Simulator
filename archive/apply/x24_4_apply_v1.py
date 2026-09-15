#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x24_4_apply_v1.py — Х24.4 · промах на E3 відкриває НОВУ розмову того самого замовлення.
живе доки: правки не влиті в репо AE-Simulator (В-31) — після фінального пушу рецепт іде в архів.

Застосовується ПІСЛЯ x24_3_apply_v1.py.
  python3 x24_4_apply_v1.py <тека AE>

Що робить (5 правок index.html + 1 блок тверджень у наявному tools/smoke_step2.js):
  П-1  S дістає поле e2from — звідки зайшли в E2 ('e1' | 'e3'). Дім названо коментарем на місці.
  П-2  openScenario(sc, origin) виставляє S.e2from; дефолт 'e1' обовʼязковий — exit() наступного
       замовлення кличе openScenario БЕЗ origin, і без дефолту прапорець залип би на 'e3'.
  П-3  button.slip дістає onclick → openScenario(r.sc, 'e3').
  П-4  Talk() дістає fromE3; exit() при fromE3 НЕ пише в rows і НЕ рухає shift.i — підсумок заморожений.
  П-5  Шапка E2 при fromE3: напис «назад» і напис виходу — «Повернутися до підсумку» (макет E2_BACK.e3);
       тег «Замовлення X з N» глушиться (після зміни shift.i === queue.length → друкував би «4 з 3»).
  С-1  8 тверджень + 3 інжекти (12.12) у tools/smoke_step2.js.

Гард: якщо правка вже стоїть — не дублюється; повторний прогін дає exit 0 і той самий md5 (П34 · П37).
"""
import sys, os, hashlib

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def sub(txt, old, new, name, log):
    """Заміна рівно одного входження. Гард шукає ФОРМУ коду, не слово (П36)."""
    if new in txt:
        log.append(('=', name))
        return txt, 0
    n = txt.count(old)
    if n != 1:
        raise SystemExit('✗ %s: якір трапився %d разів (треба 1)' % (name, n))
    log.append(('+', name))
    return txt.replace(old, new, 1), 1

BASE = sys.argv[1] if len(sys.argv) > 1 else '.'
IDX = os.path.join(BASE, 'index.html')
SMK = os.path.join(BASE, 'tools', 'smoke_step2.js')
for p in (IDX, SMK):
    if not os.path.isfile(p):
        raise SystemExit('✗ немає файлу: ' + p)

h = open(IDX, encoding='utf-8').read()
log, changed = [], 0

# ── П-1 · поле стану ───────────────────────────────────────────────────────
h, c = sub(h,
"  shift:null,         // {queue:[…], i:0, rows:[…]}",
"""  shift:null,         // {queue:[…], i:0, rows:[…]}
  e2from:'e1',        // Х24.4: звідки зайшли в E2. 'e1' — зі списку або по ходу зміни,
                      // 'e3' — з промаху в підсумку зміни. Керує написом «назад», написом
                      // виходу, тегом «Замовлення X з N» і тим, чи пише вихід рядок у
                      // shift.rows. Живе в S, а не локальною змінною в Talk(): вхід з
                      // промаху робить render(), і локальна змінна не пережила б його.""",
'П-1 поле S.e2from', log); changed += c

# ── П-2 · openScenario дістає origin ───────────────────────────────────────
h, c = sub(h,
"""function openScenario(sc){
  S.sc=sc;""",
"""function openScenario(sc, origin){
  S.e2from = origin || 'e1';   /* Х24.4: дефолт обовʼязковий — exit() наступного замовлення кличе без origin */
  S.sc=sc;""",
'П-2 openScenario(sc, origin)', log); changed += c

# ── П-3 · дія промаху ──────────────────────────────────────────────────────
h, c = sub(h,
"class:'slip', 'data-slip':String(r.sc.id)}",
"class:'slip', 'data-slip':String(r.sc.id), onclick:() => openScenario(r.sc, 'e3')}",
'П-3 .slip onclick', log); changed += c

# ── П-4 · fromE3 у Talk + заморожений вихід ────────────────────────────────
h, c = sub(h,
"""function Talk(){
  const sc = S.sc, st = e2State(), hist = S.history, pot = potential(sc);""",
"""function Talk(){
  const sc = S.sc, st = e2State(), hist = S.history, pot = potential(sc);
  /* Х24.4: розмова, відкрита з промаху в підсумку зміни. Підсумок заморожений —
     ця спроба не пишеться в shift.rows і не рухає shift.i; вихід веде назад на E3. */
  const fromE3 = S.e2from === 'e3';""",
'П-4а fromE3 у Talk', log); changed += c

h, c = sub(h,
"""    if(S.shift){
      S.shift.rows.push({sc, delta:bonusOf(S.cart) - bonusOf(sc.order), pot, fb:S.feedback, tries:S.attempt});""",
"""    if(fromE3){ S.screen = 'result'; render(); return; }   /* Х24.4: підсумок заморожений */
    if(S.shift){
      S.shift.rows.push({sc, delta:bonusOf(S.cart) - bonusOf(sc.order), pot, fb:S.feedback, tries:S.attempt});""",
'П-4б exit() не пише в rows', log); changed += c

# ── П-5 · шапка E2 ─────────────────────────────────────────────────────────
h, c = sub(h,
"""  if(S.shift) tags.push(el('span', {class:'v2-tag', text:'Замовлення ' + (S.shift.i + 1) + ' з ' + S.shift.queue.length}));
  const exitLabel = !S.shift ? 'До списку' : S.shift.i + 1 < S.shift.queue.length ? 'Наступне замовлення' : 'До підсумку зміни';
  const appbar = el('header', {class:'appbar'}, [
    el('button', {type:'button', class:'v2-back', 'aria-label':'Повернутися до списку',
      onclick:() => { S.shift = null; S.screen = 'picker'; render(); }}, [icon('i-arrow'), el('span', {text:'Повернутися до списку'})]),""",
"""  /* Х24.4: після зміни shift.i === queue.length, тож тег надрукував би «Замовлення 4 з 3» — глушимо. */
  if(S.shift && !fromE3) tags.push(el('span', {class:'v2-tag', text:'Замовлення ' + (S.shift.i + 1) + ' з ' + S.shift.queue.length}));
  const exitLabel = fromE3 ? 'Повернутися до підсумку'
    : !S.shift ? 'До списку' : S.shift.i + 1 < S.shift.queue.length ? 'Наступне замовлення' : 'До підсумку зміни';
  /* Х24.4: напис «назад» іде за входом — макет E2_BACK.e3. Обидві двері ведуть на E3:
     старий обробник робив S.shift = null і знищив би підсумок, до якого ми повертаємось. */
  const backLabel = fromE3 ? 'Повернутися до підсумку' : 'Повернутися до списку';
  const backGo = () => { if(fromE3){ S.screen = 'result'; render(); return; }
    S.shift = null; S.screen = 'picker'; render(); };
  const appbar = el('header', {class:'appbar'}, [
    el('button', {type:'button', class:'v2-back', 'aria-label':backLabel,
      onclick:backGo}, [icon('i-arrow'), el('span', {text:backLabel})]),""",
'П-5 шапка E2 (напис + двері + тег)', log); changed += c

if changed:
    open(IDX, 'w', encoding='utf-8').write(h)

# ── С-1 · твердження та інжекти у НАЯВНОМУ смоуку (В-32) ───────────────────
s = open(SMK, encoding='utf-8').read()
sc1, sc2 = 0, 0

INJ = """
/* ── Х24.4 · інжекти під твердження «промах → нова розмова» (12.12) ───────
   Статичні, до boot: асинхронних гардів не торкаються, петлі з П38 тут немає. */
/* 12: вхід із промаху губить своє походження — усе, що тримається на fromE3,
   зʼїжджає на поведінку звичайної розмови зміни. */
if(INJECT) html=html.replace("  S.e2from = origin || 'e1';", "  S.e2from = 'e1';");
/* 13: знято ранній вихід — спроба з промаху дописується в rows, і підсумок,
   який людина щойно читала, змінюється під нею. */
if(INJECT) html=html.replace("    if(fromE3){ S.screen = 'result'; render(); return; }", "");
/* 14: двері «назад» знову обнуляють зміну — повернення з промаху знищує підсумок. */
if(INJECT) html=html.replace("  const backGo = () => { if(fromE3){ S.screen = 'result'; render(); return; }", "  const backGo = () => {");
/* 15: промах веде НЕ в те замовлення. Навігація лишається живою навмисно —
   мертвий клік замаскував би інжекти 12–14 (вони спостерігаються лише на E2). */
if(INJECT) html=html.replace("onclick:() => openScenario(r.sc, 'e3')",
                             "onclick:() => openScenario(Object.assign({}, r.sc, {id:r.sc.id+'-wrong'}), 'e3')");
"""
ANCHOR_INJ = 'if(INJECT) html=html.replace("scored = rows.filter(r=>!r.sc.noSale)", "scored = rows");\n'
if "Х24.4 · інжекти" not in s:
    if s.count(ANCHOR_INJ) != 1:
        raise SystemExit('✗ С-1: якір інжектів трапився %d разів' % s.count(ANCHOR_INJ))
    s = s.replace(ANCHOR_INJ, ANCHOR_INJ + INJ, 1)
    sc1 = 1
    log.append(('+', 'С-1а 3 інжекти'))
else:
    log.append(('=', 'С-1а 3 інжекти'))

TESTS = """
  /* ── Х24.4 · промах відкриває нову розмову того самого замовлення ─────
     Фікстура своя: у попередній жодного промаху немає (delta ≥ 0), а .slip
     береться саме з rows. i === queue.length — зміна вже завершена, як і на
     справжньому E3. Кожне твердження друкує заміряне, а не памʼять (П39). */
  console.log('\\n— E3 · промах → нова розмова (Х24.4) —');
  const scB = Object.assign({}, sc, {id:sc.id+'-b', title:'Друге замовлення'});
  const shX = {queue:[sc,scB], i:2, debrief:{st:'ok',d:{overall:'x',mistakes:[],strengths:[],rules:[]}},
               rows:[{sc,delta:-7,pot:20,fb:'ок',tries:1},{sc:scB,delta:3,pot:20,fb:'ок',tries:1}]};
  S.shift = shX; S.screen='result'; w.render();
  const slipBtn = d.querySelector('.v2 .slips button.slip');
  const rowsBefore = shX.rows.length, iBefore = shX.i, dbBeforeX = dbCount();
  T('промахів на E3 — кнопок '+d.querySelectorAll('.v2 .slips button.slip').length,
    !!slipBtn && slipBtn.getAttribute('data-slip')===String(sc.id));
  if(slipBtn) slipBtn.click();
  T('клік по промаху відкриває E2 того самого замовлення — екран «'+S.screen+'»',
    S.screen==='game' && S.sc && S.sc.id===sc.id);
  const backSpan = d.querySelector('.v2 .appbar .v2-back span');
  const backLbl = backSpan ? backSpan.textContent : '—';
  T('вхід з E3: двері «назад» — заміряно «'+backLbl+'»', backLbl==='Повернутися до підсумку');
  const tagTxt = [].map.call(d.querySelectorAll('.v2 .case-title .v2-tag'), t=>t.textContent).join(' · ');
  T('вхід з E3: тег замовлення глушиться — заміряно «'+tagTxt+'»', !/Замовлення/.test(tagTxt));
  S.ended = true; w.render();
  const exitBtn = d.querySelector('.v2 [data-e2-end=\\"exit\\"]');
  T('вхід з E3: вихід — заміряно «'+(exitBtn?exitBtn.textContent:'—')+'»',
    !!exitBtn && exitBtn.textContent==='Повернутися до підсумку');
  if(exitBtn) exitBtn.click();
  T('вихід повертає на E3, зміна не обнулена — екран «'+S.screen+'»',
    S.screen==='result' && S.shift===shX);
  T('підсумок заморожений: рядків було '+rowsBefore+', стало '+shX.rows.length+', i='+shX.i,
    shX.rows.length===rowsBefore && shX.i===iBefore);
  await new Promise(r=>setTimeout(r,50));
  T('розбір не перезамовлений: запитів '+(dbCount()-dbBeforeX), dbCount()-dbBeforeX===0);
  /* Двері «назад» — окремо від дверей виходу: у них був власний обробник із S.shift = null. */
  S.ended = false;
  const slip2 = d.querySelector('.v2 .slips button.slip');
  if(slip2) slip2.click();
  const back2 = d.querySelector('.v2 .appbar .v2-back');
  if(back2) back2.click();
  T('двері «назад» з промаху ведуть на E3, а не в список — екран «'+S.screen+'»',
    S.screen==='result' && S.shift===shX);
"""
ANCHOR_T = "  T('відсоток рахується поза «не міняти» — заміряно '+pctTxt, pctTxt==='50%');\n"
if 'Х24.4 · промах відкриває' not in s:
    if s.count(ANCHOR_T) != 1:
        raise SystemExit('✗ С-1: якір тверджень трапився %d разів' % s.count(ANCHOR_T))
    s = s.replace(ANCHOR_T, ANCHOR_T + TESTS, 1)
    sc2 = 1
    log.append(('+', 'С-1б 9 тверджень'))
else:
    log.append(('=', 'С-1б 9 тверджень'))

if sc1 or sc2:
    open(SMK, 'w', encoding='utf-8').write(s)

total = changed + sc1 + sc2
print('x24_4: ' + ('застосовано' if total else 'вже застосовано, без змін') + ' · правок %d' % total)
for mark, name in log:
    print('   %s %s' % (mark, name))
print('  md5 index.html=%s · smoke_step2.js=%s' % (md5(IDX)[:8], md5(SMK)[:8]))
