#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x24_3_apply_v1.py — Х24.3 «підключити E3».
живе доки: фінальний пуш Олі (В-31); у конвеєрі рецептів — ПІСЛЯ x24_2_apply_v1.py

Що робить (5 правок, усі ідемпотентні):
  index.html
    П-1  V2.result = Summary;            (за зразком V2.game = Talk, 1324)
    П-2  коментар шапки Х24.2: «НЕ підключено» → «Підключено Х24.3»
    П-3  sidebar(): const bare = game || result  →  В-43, панель E3 несе лише бренд
  tools/smoke_step2.js
    П-4  міграція твердження «розбір відмалювався»: d.body → вузол секції E3 (П24)
    П-5  4 нових твердження + 4 інжекти під них (В-32: новий файл смоука НЕ заводиться)

Повтор: нічого не міняє, друкує «вже застосовано» і виходить 0 (П34 · П37).
"""
import sys, os, hashlib

BASE = sys.argv[1] if len(sys.argv) > 1 else 'AE'
IDX  = os.path.join(BASE, 'index.html')
SMK  = os.path.join(BASE, 'tools', 'smoke_step2.js')

def rd(p):
    with open(p, encoding='utf-8') as f: return f.read()
def wr(p, t):
    with open(p, 'w', encoding='utf-8') as f: f.write(t)

def sub(text, old, new, label, done_mark):
    """Повертає (text, стан): 'зроблено' | 'вже' | падає, якщо якоря немає."""
    if done_mark in text:
        return text, 'вже'
    if text.count(old) != 1:
        sys.exit('✗ x24_3: якір «%s» знайдено %d разів (треба 1)' % (label, text.count(old)))
    return text.replace(old, new), 'зроблено'

# ─────────────────────────── index.html ───────────────────────────
idx = rd(IDX)
st = {}

# П-2 — шапка блоку Х24.2 (робимо ПЕРШОЮ: П-1 дописує маркер у кінець блоку)
idx, st['П-2 коментар'] = sub(
    idx,
    "/* ── Х24.2 · E3 «Підсумок зміни» — Summary(), НЕ підключено (П12; V2.result ставить Х24.3) ──",
    "/* ── Х24.2 · E3 «Підсумок зміни» — Summary(). Підключено Х24.3: V2.result = Summary (у кінці блоку) ──",
    'коментар Х24.2',
    "Підключено Х24.3: V2.result = Summary")

# П-1 — підключення
idx, st['П-1 V2.result'] = sub(
    idx,
    "}\n/* ── /Х24.2 ── */",
    "}\nV2.result = Summary;\n/* ── /Х24.2 ── */",
    'кінець блоку Х24.2',
    "V2.result = Summary;")

# П-3 — В-43: бренд-лише панель на E2 і E3
idx, st['П-3 В-43 панель'] = sub(
    idx,
    "function sidebar(active){\n  const links = V2_NAV",
    "function sidebar(active){\n"
    "  /* Х24.3 · В-43: панель несе ЛИШЕ бренд на E2 (game) і E3 (result). На обох екранах\n"
    "     вихід живе в шапці; на E3 другі двері збоку знищили б незбережений підсумок. */\n"
    "  const bare = active==='game' || active==='result';\n"
    "  const links = V2_NAV",
    'початок sidebar()',
    "const bare = active==='game' || active==='result';")

if st['П-3 В-43 панель'] == 'зроблено':
    old_nav = ("    /* Х23.3: на E2 (game) панель несе лише бренд, як макет «Тренування_in»; вихід — «назад» у шапці */\n"
               "    active==='game' ? null : el('nav',{class:'side-links','aria-label':'Звичайний режим'},links),\n"
               "    /* низ панелі — двері Х22.4 (§8.1: вхід у кураторський режим під замком) */ active==='game' ? null : door()]);")
    new_nav = ("    /* Х23.3 · Х24.3: на E2 (game) і E3 (result) панель несе лише бренд, як макет; вихід — у шапці */\n"
               "    bare ? null : el('nav',{class:'side-links','aria-label':'Звичайний режим'},links),\n"
               "    /* низ панелі — двері Х22.4 (§8.1: вхід у кураторський режим під замком) */ bare ? null : door()]);")
    if idx.count(old_nav) != 1:
        sys.exit('✗ x24_3: тіло sidebar() не збіглося дослівно')
    idx = idx.replace(old_nav, new_nav)

# ─────────────────────────── smoke_step2.js ───────────────────────────
smk = rd(SMK)

# П-5а — інжекти (кладемо поруч із рештою інжектів html, перед `const local=f=>{`)
INJ = """/* ── Х24.3 · інжекти під твердження E3 (12.12) ────────────────────────
   Вісім–одинадцять: кожен ламає рівно один механізм підсумку зміни. */
/* 8: В-43 — повертаємо панелі E3 навігацію й двері (другі двері виходу). */
if(INJECT) html=html.replace("  const bare = active==='game' || active==='result';",
                             "  const bare = active==='game';");
/* 9: розбір перестає бути «раз на зміну» — знімаємо мітку {st:'wait'}, якою
   гард !sh.debrief закривається ВІДРАЗУ, ще до відповіді. Без мітки кожен
   рендер до приходу відповіді шле новий платний запит (дефект старого Result).
   Ламаємо саме мітку, а не сам гард: знятий гард дає нескінченну петлю
   запит → render() у .then → запит, і смоук не завершується взагалі. */
if(INJECT) html=html.replace("    sh.debrief = {st:'wait'};", "");
/* 10: знято гард чужої зміни — відповідь, що прийшла після виходу зі зміни,
   лягає у вже покинутий S.shift. */
if(INJECT) html=html.replace("engineLive.debrief(rows).then(d => { if(S.shift !== sh) return;",
                             "engineLive.debrief(rows).then(d => {");
/* 11: «не міняти» повертається у знаменник відсотка — орієнтир роздувається,
   виконання падає (50 % → 14 % на фікстурі нижче). */
if(INJECT) html=html.replace("scored = rows.filter(r=>!r.sc.noSale)", "scored = rows");

const local=f=>{"""

smk, st['П-5а інжекти'] = sub(smk, "const local=f=>{", INJ, 'початок local()', "Х24.3 · інжекти під твердження E3")

# П-4 — міграція «розбір відмалювався» у вузол секції E3 (П24)
smk, st['П-4 міграція'] = sub(
    smk,
    "  T('розбір відмалювався', /Загалом непогано/.test(d.body.textContent));",
    "  /* Х24.3 (П24): міряємо у вузлі секції E3, не в body — інакше твердження\n"
    "     тримається на будь-якому тексті сторінки, не на розборі. */\n"
    "  const e3 = d.querySelector('.v2 main .summary-wrap');\n"
    "  const e3Review = e3 && e3.querySelectorAll('.summary-section')[1];\n"
    "  T('розбір відмалювався у секції E3', !!e3Review && /Загалом непогано/.test(e3Review.textContent));",
    'твердження «розбір відмалювався»',
    "розбір відмалювався у секції E3")

# П-5б — нові твердження після блоку «розбір зміни»
NEW = """  T('нотатка куратору збережена', S.shift.curatorNote==='звернути увагу на темп');

  /* ── Х24.3 · E3 підключено (V2.result = Summary) ────────────────────── */
  console.log('\\n— E3 · підсумок зміни (Х24.3) —');
  T('В-43: на E3 панель несе лише бренд — ні навігації, ні дверей',
    !!d.querySelector('.v2 .sidebar .brand') && !d.querySelector('.v2 .side-links') && !d.querySelector('.v2 .door'));

  /* Раз на зміну: беремо СВІЖУ зміну (у попередньої розбір уже прийшов) і
     малюємо E3 тричі синхронно, до відповіді. Мітка {st:'wait'} мусить
     закрити гард уже на першому рендері. */
  const dbCount = () => sent.filter(x=>x.body.response_format.json_schema.name==='shift_debrief').length;
  const dbBefore = dbCount();
  S.shift = {queue:[sc],i:0,rows:[{sc,delta:12.3,pot:20,fb:'ок'}]};
  S.screen='result'; w.render(); w.render(); w.render();
  await new Promise(r=>setTimeout(r,300));
  T('розбір замовляється раз на зміну: 3 рендери — запитів '+(dbCount()-dbBefore), dbCount()-dbBefore===1);

  /* Пізня відповідь чужої зміни: підміняємо S.shift синхронно, ДО того як
     мікрозадача .then встигне спрацювати. Покинута зміна мусить лишитись 'wait'. */
  const shOld = {queue:[sc],i:0,rows:[{sc,delta:5,pot:20,fb:'ок'}]};
  S.shift = shOld; S.screen='result'; w.render();
  S.shift = {queue:[sc],i:0,rows:[{sc,delta:5,pot:20,fb:'ок'}]};
  await new Promise(r=>setTimeout(r,300));
  T('пізня відповідь чужої зміни відкинута', !!shOld.debrief && shOld.debrief.st==='wait');

  /* Відсоток: «не міняти» — поза орієнтиром. 10 з 20 = 50 %; якщо noSale
     повертається у знаменник, виходить 10 з 70 = 14 %. */
  const scNo = Object.assign({}, sc, {noSale:true, id:sc.id+'-nosale'});
  S.shift = {queue:[sc],i:0, debrief:{st:'ok',d:{overall:'x',mistakes:[],strengths:[],rules:[]}},
             rows:[{sc,delta:10,pot:20,fb:'ок'},{sc:scNo,delta:0,pot:50,fb:'ок'}]};
  S.screen='result'; w.render();
  const pctTxt = (d.querySelector('.v2 .summary-grid .metric.accent strong')||{}).textContent;
  T('відсоток рахується поза «не міняти» — заміряно '+pctTxt, pctTxt==='50%');
"""

smk, st['П-5б твердження'] = sub(
    smk,
    "  T('нотатка куратору збережена', S.shift.curatorNote==='звернути увагу на темп');\n",
    NEW,
    'твердження «нотатка куратору»',
    "E3 · підсумок зміни (Х24.3)")

# ─────────────────────────── запис ───────────────────────────
changed = [k for k, v in st.items() if v == 'зроблено']
if changed:
    wr(IDX, idx); wr(SMK, smk)
    print('x24_3: застосовано — ' + ' · '.join(changed))
else:
    print('x24_3: вже застосовано, без змін · правок 0')
print('  md5 index.html=%s · smoke_step2.js=%s' % (
    hashlib.md5(rd(IDX).encode()).hexdigest()[:8],
    hashlib.md5(rd(SMK).encode()).hexdigest()[:8]))
