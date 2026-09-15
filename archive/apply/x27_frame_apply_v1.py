#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AE-Simulator · Х27 КРОК 0 «ЧЕСНИЙ КАДР» · рецепт v1
живе доки: КРОК 2 «ПУНКТИ» не дав власного стенда (тоді цей — архів)

база:   AE_X27_SIDEBAR_v7.html  md5 e89a838b5d3dd9c5ba05610eebf95096
донор:  AE_X27_SIDEBAR_v2.html  md5 91f2cb6395a6245da50c1c514b1922a1  (SETS · stub · #tip)
вихід:  AE_X27_SIDEBAR_v8.html

Що робить (вироки оператора S55):
  A  важіль «кадр» — край-в-край проти рамки стенда (дефолт край-в-край)
  B  важіль «висота панелі» — на всю / по вмісту, судиться на 6 пунктах (П56)
  C  важіль «канва острівця» — канва й головна різнились на 3,5 % і не читались
  D  blur знято цілком — мертвий за версткою, маніфест §8.7-б
  E  лік 0.3-А — фон головної у «врівень»
  F  лік 0.3-Б — дубль правила rail .side-bottom
  G  радіус .snap прив'язано до положення оболонки
  H  ширина рейки 72 — вирок В-36, компер 64/72 знято
  I  К1 копі-кнопка
  B' важіль «пунктів» 2 · 4 · 6 + «неготові» заглушки/сховані + підказки з v2
  J  важіль підпису низу

Жодного рядка продукту не змінено (В-31). Зліпок не чіпано.
"""
import hashlib
import os
import sys

SRC = "/mnt/project/AE_X27_SIDEBAR_v7.html"
DON = "/mnt/project/AE_X27_SIDEBAR_v2.html"
OUT = "/mnt/user-data/outputs/AE_X27_SIDEBAR_v8.html"

MD5_SRC = "e89a838b5d3dd9c5ba05610eebf95096"
MD5_DON = "91f2cb6395a6245da50c1c514b1922a1"

steps = []


def rep(s, old, new, tag, n=1):
    """Заміна з асертом на якір: не знайшли — падаємо голосно, не тихо."""
    c = s.count(old)
    if c != n:
        print("✗ ЯКІР НЕ ЗІЙШОВСЯ: %s — входжень %d, чекали %d" % (tag, c, n))
        print("   шукали: %r" % old[:110])
        sys.exit(2)
    steps.append(tag)
    return s.replace(old, new, n)


def md5(b):
    return hashlib.md5(b).hexdigest()


# ── 0 · база й донор ─────────────────────────────────────────────────
src = open(SRC, "rb").read()
don = open(DON, "rb").read()
if md5(src) != MD5_SRC:
    print("✗ база не та: %s замість %s" % (md5(src), MD5_SRC))
    sys.exit(2)
if md5(don) != MD5_DON:
    print("✗ донор не той: %s замість %s" % (md5(don), MD5_DON))
    sys.exit(2)
s = src.decode("utf-8")
print("✓ база v7 %s · донор v2 %s" % (MD5_SRC[:8], MD5_DON[:8]))

# ── 1 · шапка файла ──────────────────────────────────────────────────
s = rep(
    s,
    """  AE-Simulator · харнес Х27 v7 «ОБОЛОНКА + ЗЛІПОК + РЕМОНТ» · крок 1 з трьох
  живе доки: крок 2 «ПУНКТИ» не дав власного стенда (тоді цей — архів)""",
    """  AE-Simulator · харнес Х27 v8 «ЧЕСНИЙ КАДР» · крок 0 (перед кроком 2)
  живе доки: крок 2 «ПУНКТИ» не дав власного стенда (тоді цей — архів)
  v8 проти v7: рамку стенда знято з дороги (вона домальовувала четверту картку
  поверх острівця — В-34 судився наосліп) · висота панелі стала важелем і
  судиться на шести пунктах кураторського режиму (SPEC §8.2, П56) · канва
  острівця стала важелем (була на 3,5 % відмінна від головної — §8.7-г) ·
  blur знято як мертвий за версткою (§8.7-б) · підказки й заглушки перенесено
  з AE_X27_SIDEBAR_v2.html дослівно (Д-В2) · ширина рейки 72 — вирок В-36.""",
    "1 · шапка",
)

# ── 2 · A · важіль «кадр» ────────────────────────────────────────────
s = rep(
    s,
    """.stage{flex:1 1 auto;min-height:560px;overflow:hidden;border:1px solid #d6dade;border-radius:10px;background:#fff}""",
    """.stage{flex:1 1 auto;min-height:560px;overflow:hidden;border:1px solid #d6dade;border-radius:10px;background:#fff}
/* КРОК 0 · важіль «кадр». Рамка стенда (padding 14 + кант + радіус 10 + білий фон)
   домальовувала ЩЕ ОДНУ картку поверх острівця, і саме її край око читало як
   третій шар. Вирок про «бутерброд» у такому кадрі був би вироком комбінації,
   якої в продукті немає (маніфест §8.7). Дефолт — край-в-край. */
body[data-frame="edge"] .stagewrap{padding:0}
body[data-frame="edge"] .stage{border:0;border-radius:0;background:transparent}""",
    "2 · A кадр",
)

# ── 3 · токен --anc-gray-light (продукт :722, потрібен заглушкам) ────
s = rep(
    s,
    """    --anc-text-2:#4F4F4F;--anc-gray:#6E6E77;--anc-border:#E7E7E7;""",
    """    --anc-text-2:#4F4F4F;--anc-gray:#6E6E77;--anc-border:#E7E7E7;--anc-gray-light:#9B9CA1;""",
    "3 · токен gray-light",
)

# ── 4 · G · радіус зліпка за оболонкою ───────────────────────────────
s = rep(
    s,
    """.v2 .snap{display:block;height:100%;overflow:hidden;background:transparent;
          border-radius:var(--isl-radius)}""",
    """.v2 .snap{display:block;height:100%;overflow:hidden;background:transparent;border-radius:0}
/* G · у «врівень» і «лише панель» у main радіуса немає — зліпок різав кути там,
   де їх не має бути. Радіус живе тільки там, де живе кант. */
.v2[data-shell="island"] .snap{border-radius:var(--isl-radius)}""",
    "4 · G радіус зліпка",
)

# ── 5 · D · blur геть із токенів ─────────────────────────────────────
s = rep(
    s,
    """    --isl-inset:16px;
    --isl-blur:0px;
    --isl-shadow:0 3px 2px 1px #1C1E242e;""",
    """    --isl-inset:16px;
    /* --isl-blur знято в КРОЦІ 0: backdrop-filter стояв на .sidebar, а в неї
       непрозорий background. Під панеллю не проїжджає нічого — мертвий за
       версткою, маніфест §8.7-б, перший приклад у списку. */
    --isl-shadow:0 3px 2px 1px #1C1E242e;""",
    "5 · D токен blur",
)
s = rep(
    s,
    """                                  box-shadow:var(--isl-shadow);backdrop-filter:blur(var(--isl-blur))}""",
    """                                  box-shadow:var(--isl-shadow)}""",
    "5 · D blur island",
)
s = rep(
    s,
    """                                box-shadow:var(--isl-shadow);backdrop-filter:blur(var(--isl-blur))}""",
    """                                box-shadow:var(--isl-shadow)}""",
    "5 · D blur solo",
)

# ── 6 · E · лік 0.3-А ────────────────────────────────────────────────
s = rep(
    s,
    """.v2[data-shell="flush"] .shell{grid-template-columns:var(--side-w) minmax(0,1fr)}""",
    """.v2[data-shell="flush"] .shell{grid-template-columns:var(--side-w) minmax(0,1fr)}
/* E · лік 0.3-А: правила фону головної у «врівень» не існувало взагалі —
   фарбували лише island і solo, і важіль тону давав 0,00 % піксельної різниці. */
.v2[data-shell="flush"] main{background:var(--isl-main)}""",
    "6 · E лік 0.3-А",
)

# ── 7 · F · дубль правила rail (0.3-Б) ───────────────────────────────
s = rep(
    s,
    """.v2[data-mode="rail"] .side-link .lbl{display:none}
.v2[data-mode="rail"] .side-bottom{padding:12px 0 20px}
.v2[data-mode="rail"] .side-bottom button{""",
    """.v2[data-mode="rail"] .side-link .lbl{display:none}
.v2[data-mode="rail"] .side-bottom button{""",
    "7 · F дубль 0.3-Б",
)

# ── 8 · B · висота панелі + B' заглушки + підказка (з v2 дослівно) ───
s = rep(
    s,
    """.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}""",
    """.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

/* ══ 4 · КРОК 0 · висота панелі ═══════════════════════════════════════
   У продукті панель — борт вікна, і тягнутись на всю висоту правильно.
   В острівці панель — картка, і картка мусить жити по своєму вмісту.
   ⚠ П56: вирок про цю висоту виноситься на НАЙДОВШОМУ режимі — шість
   пунктів кураторського (SPEC §8.2), не на чотирьох, що стояли в стенді.
   align-self, а не align-items: інакше по вмісту скоротилась би й main. */
.v2[data-fit="content"][data-shell="island"] .sidebar,
.v2[data-fit="content"][data-shell="solo"] .sidebar{align-self:start;overflow:visible}
/* margin-top:auto притискав замок до низу — при короткій панелі тримати нічого */
.v2[data-fit="content"][data-shell="island"] .side-bottom,
.v2[data-fit="content"][data-shell="solo"] .side-bottom{margin-top:12px}

/* ══ 5 · підказка й заглушки — перенесено з AE_X27_SIDEBAR_v2.html ════
   Дослівно (Д-В2: значення копіюються з живого коду, не відтворюються).
   Тултип окремим шаром, не ::after: .sidebar має overflow:auto (:63)
   і обрізав би псевдоелемент. */
#tip{position:fixed;z-index:99;padding:5px 9px;border-radius:6px;color:#fff;background:#1C1E24;
     font:12px/1.4 system-ui,sans-serif;white-space:nowrap;pointer-events:none;opacity:0;transition:opacity .12s}
#tip.on{opacity:1}
.v2 .side-link.stub{color:var(--anc-gray-light);cursor:default}
.v2[data-stub="hidden"] .stub{display:none}""",
    "8 · B висота + B' заглушки",
)

# ── 9 · I · копі-кнопка у службовій шапці ────────────────────────────
s = rep(
    s,
    """  <button type="button" id="fMeter" aria-pressed="false">замір ▾</button>""",
    """  <button type="button" id="fMeter" aria-pressed="false">замір ▾</button>
  <button type="button" id="fCopy">копі 📋</button>""",
    "9 · I копі-кнопка",
)

# ── 10 · B' · нові важелі замість знятого blur ───────────────────────
s = rep(
    s,
    """  <div class="grp"><label>blur <output id="oB"></output></label>
    <input type="range" id="rB" min="0" max="16" step="1"></div>""",
    """  <div class="grp"><label>кадр</label><div class="row" data-ax="frame">
    <button type="button" data-v="edge">край-в-край</button>
    <button type="button" data-v="box">у рамці</button></div></div>
  <div class="grp"><label>висота панелі</label><div class="row" data-ax="fit">
    <button type="button" data-v="full">на всю</button>
    <button type="button" data-v="content">по вмісту</button></div></div>
  <div class="grp"><label>пунктів</label><div class="row" data-ax="set">
    <button type="button" data-v="2">2 живих</button>
    <button type="button" data-v="4">4 канон</button>
    <button type="button" data-v="6">6 куратор</button></div></div>
  <div class="grp"><label>неготові</label><div class="row" data-ax="stub">
    <button type="button" data-v="shown">заглушки</button>
    <button type="button" data-v="hidden">сховані</button></div></div>""",
    "10 · B' важелі",
)

# ── 11 · C · важіль канви + J · підпис низу ──────────────────────────
s = rep(
    s,
    """  <div class="grp"><label>тон · головна</label>""",
    """  <div class="grp"><label>канва острівця</label>
    <select id="tCanvas"><option value="#F6F5EE" selected>F6F5EE (нинішня)</option>
    <option value="#FFFEF6">canvas Y5</option><option value="#FFFCEC">plate Y10</option>
    <option value="#F1EFE6">тепла −2</option><option value="#EAE8DE">тепла −4</option>
    <option value="#E3E0D4">тепла −6</option><option value="#ECEFF1">холодна сіра</option></select></div>
  <div class="grp"><label>підпис низу</label>
    <select id="tDoor"><option value="Кураторський режим" selected>Кураторський режим</option>
    <option value="Куратор">Куратор</option></select></div>
  <div class="grp"><label>тон · головна</label>""",
    "11 · C канва + J підпис",
)

# ── 12 · B' · навігація будується з SETS ─────────────────────────────
s = rep(
    s,
    """      <nav class="side-links" id="nav" aria-label="АНЦ Тренажер — звичайний режим">
        <button type="button" class="side-link active" aria-current="page">
          <svg aria-hidden="true"><use href="#i-play"></use></svg><span class="lbl">Тренування</span></button>
        <button type="button" class="side-link">
          <svg aria-hidden="true"><use href="#i-doc"></use></svg><span class="lbl">Сценарії</span></button>
        <button type="button" class="side-link">
          <svg aria-hidden="true"><use href="#i-box"></use></svg><span class="lbl">Каталог</span></button>
        <button type="button" class="side-link">
          <svg aria-hidden="true"><use href="#i-bars"></use></svg><span class="lbl">Результати</span></button>
      </nav>

      <div class="side-bottom">
        <button type="button">
          <svg aria-hidden="true"><use href="#i-lock"></use></svg><span class="lbl">Кураторський режим</span></button>
      </div>""",
    """      <!-- пункти будує build() з SETS: 2 живих · 4 канон §8.1 · 6 куратор §8.2 -->
      <nav class="side-links" id="nav" aria-label="АНЦ Тренажер — звичайний режим"></nav>

      <div class="side-bottom">
        <button type="button" id="doorBtn" data-tip="Кураторський режим">
          <svg aria-hidden="true"><use href="#i-lock"></use></svg><span class="lbl" id="doorLbl">Кураторський режим</span></button>
      </div>""",
    "12 · B' навігація",
)

# ── 13 · іконки кураторських екранів (з v2 дослівно) ─────────────────
s = rep(
    s,
    """<symbol id="i-bars" viewBox="0 0 24 24"><path d="M5 20V4"/><path d="M9 20v-6M14 20V9M19 20v-9"/></symbol>
</svg>""",
    """<symbol id="i-bars" viewBox="0 0 24 24"><path d="M5 20V4"/><path d="M9 20v-6M14 20V9M19 20v-9"/></symbol>
<!-- іконки кураторських екранів — перенесено з AE_X27_SIDEBAR_v2.html дослівно -->
<symbol id="i-grid" viewBox="0 0 24 24"><rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/></symbol>
<symbol id="i-chip" viewBox="0 0 24 24"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M10 4v3M14 4v3M10 17v3M14 17v3M4 10h3M4 14h3M17 10h3M17 14h3"/></symbol>
<symbol id="i-gear" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3.2"/><path d="M12 3v2.6M12 18.4V21M3 12h2.6M18.4 12H21M5.6 5.6l1.9 1.9M16.5 16.5l1.9 1.9M18.4 5.6l-1.9 1.9M7.5 16.5l-1.9 1.9"/></symbol>
<symbol id="i-chat" viewBox="0 0 24 24"><path d="M5 5h14v11H9l-4 3V5Z"/><path d="M9 10h6"/></symbol>
</svg>
<div id="tip" role="status"></div>""",
    "13 · іконки + шар підказки",
)

# ── 14 · стан харнеса ────────────────────────────────────────────────
s = rep(
    s,
    """var state = { shell:'island', rule:'dash', mode:'expanded', elev:'1' };""",
    """var state = { shell:'island', rule:'dash', mode:'expanded', elev:'1',
              frame:'edge', fit:'full', set:'4', stub:'shown' };
/* SETS перенесено з AE_X27_SIDEBAR_v2.html дослівно (Д-В2).
   [іконка, підпис, заглушка?]  ·  2 = живе в продукті сьогодні (V2_NAV)
   4 = SPEC §8.1 звичайний режим  ·  6 = SPEC §8.2 кураторський, для Олі */
var SETS = {
  '2': [['i-play','Тренування',0],['i-box','Каталог',0]],
  '4': [['i-play','Тренування',0],['i-doc','Сценарії',1],['i-box','Каталог',0],['i-bars','Результати',1]],
  '6': [['i-grid','Дашборд',1],['i-doc','Сценарії',1],['i-box','Каталог',1],
        ['i-chip','AI / Моделі',1],['i-chat','Промпти',1],['i-gear','Система',1]]
};""",
    "14 · стан + SETS",
)

# ── 15 · apply() веде нові осі ───────────────────────────────────────
s = rep(
    s,
    """  V2.dataset.shell=state.shell; V2.dataset.rule=state.rule; V2.dataset.mode=state.mode;""",
    """  V2.dataset.shell=state.shell; V2.dataset.rule=state.rule; V2.dataset.mode=state.mode;
  V2.dataset.fit=state.fit; V2.dataset.stub=state.stub; V2.dataset.set=state.set;
  document.body.dataset.frame=state.frame;""",
    "15 · apply осі",
)
s = rep(
    s,
    """  ['shell','rule','mode','elev'].forEach(function(k){ paintRow(k, state[k]); });""",
    """  ['shell','rule','mode','elev','frame','fit','set','stub'].forEach(function(k){ paintRow(k, state[k]); });""",
    "15 · apply підсвітка",
)
s = rep(
    s,
    """  state[ax]=b.dataset.v; apply();""",
    """  state[ax]=b.dataset.v;
  if(ax==='set') build();
  apply();""",
    "15 · перебудова пунктів",
)

# ── 16 · build() + підказки — з v2 дослівно ──────────────────────────
s = rep(
    s,
    """g('logo').addEventListener('click', function(){""",
    """/* ══ пункти й підказки — перенесено з AE_X27_SIDEBAR_v2.html ═══════════════
   Заглушка = екран, якого ще немає. Вона лишається в панелі навмисно: коли
   екран приїде з макета, підключати треба буде логіку, а не панель. */
function build(){
  var set=SETS[state.set], nav=g('nav'), first=true;
  nav.replaceChildren.apply(nav, set.map(function(row){
    var b=document.createElement('button');
    b.type='button';
    b.className='side-link'+(row[2]?' stub':'')+(!row[2]&&first?' active':'');
    if(!row[2]&&first){ b.setAttribute('aria-current','page'); first=false; }
    if(row[2]) b.setAttribute('aria-disabled','true');
    b.setAttribute('aria-label', row[1]+(row[2]?' — екран ще не готовий':''));
    b.setAttribute('data-tip', row[1]+(row[2]?' · екран ще не готовий':''));
    var s=document.createElementNS('http://www.w3.org/2000/svg','svg');
    s.setAttribute('aria-hidden','true');
    var u=document.createElementNS('http://www.w3.org/2000/svg','use');
    u.setAttribute('href','#'+row[0]); s.append(u);
    var t=document.createElement('span'); t.className='lbl'; t.textContent=row[1];
    b.append(s,t); return b;
  }));
}
/* Підказка окремим шаром: у рейці підпис сховано (.lbl display:none), і без
   неї пункт втрачає не лише вигляд, а й доступне ім'я. */
function showTip(el){
  var txt=el.getAttribute('data-tip'); if(!txt) return;
  var rail = state.mode==='rail';
  if(!rail && !el.classList.contains('stub')) return;
  var r=el.getBoundingClientRect();
  g('tip').textContent=txt; g('tip').classList.add('on');
  g('tip').style.left=Math.round(r.right+8)+'px';
  g('tip').style.top=Math.round(r.top+r.height/2-g('tip').offsetHeight/2)+'px';
}
function hideTip(){ g('tip').classList.remove('on'); }
['mouseover','focusin'].forEach(function(ev){
  document.addEventListener(ev, function(e){
    var el=e.target.closest && e.target.closest('[data-tip]');
    if(el) showTip(el); else hideTip();
  });
});
['mouseout','focusout'].forEach(function(ev){ document.addEventListener(ev, hideTip); });

/* J · підпис низу: «режим» — службове слово, воно нічого не несе.
   Пара «Куратор ↔ Тренажер» — два боки однієї кнопки (SPEC §8.2). */
g('tDoor').addEventListener('change', function(){
  g('doorLbl').textContent=this.value;
  g('doorBtn').setAttribute('data-tip', this.value); measure(); });

/* I · К1 копі-кнопка. На file:// clipboard може відмовити — відмова друкується
   у стрічку, а не ковтається: важіль, що мовчки не спрацював, гірший за явний ✗. */
g('fCopy').addEventListener('click', function(){
  var v=function(p){ return getComputedStyle(V2).getPropertyValue(p).trim(); };
  var txt=['AE · Х27 v8 · стан важелів',
    'кадр='+state.frame+'  оболонка='+state.shell+'  розділювачі='+state.rule,
    'стан='+state.mode+'  висота панелі='+state.fit+'  пунктів='+state.set+'  неготові='+state.stub,
    'радіус='+v('--isl-radius')+'  відступ='+v('--isl-inset')+'  тінь='+v('--isl-shadow'),
    'канва='+v('--isl-canvas')+'  шапка='+v('--isl-head')+'  тіло='+v('--isl-surface'),
    'низ='+v('--isl-foot')+'  головна='+v('--isl-main')+'  підпис низу='+g('tDoor').value,
    'ширина рейки=72 (В-36)',
    g('meter').textContent].join('\\n');
  var done=function(ok){ g('fCopy').textContent = ok?'копі ✓':'копі ✗ (виділи стрічку)';
    setTimeout(function(){ g('fCopy').textContent='копі 📋'; }, 1800); };
  try{
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(function(){done(true);}, function(){done(fallback(txt));});
    } else done(fallback(txt));
  }catch(e){ done(false); }
});
function fallback(txt){
  try{
    var ta=document.createElement('textarea'); ta.value=txt;
    ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta);
    ta.select(); var ok=document.execCommand('copy'); ta.remove(); return ok;
  }catch(e){ return false; }
}

g('logo').addEventListener('click', function(){""",
    "16 · build + підказки + копі",
)

# ── 17 · C · прив'язка канви ─────────────────────────────────────────
s = rep(
    s,
    """[['tHead','--isl-head'],['tBody','--isl-surface'],['tFoot','--isl-foot'],['tMain','--isl-main']]""",
    """[['tHead','--isl-head'],['tBody','--isl-surface'],['tFoot','--isl-foot'],['tMain','--isl-main'],
 ['tCanvas','--isl-canvas']]""",
    "17 · C канва",
)

# ── 18 · замір: N2 обчислюється, панель друкується ───────────────────
s = rep(
    s,
    """   N2 .side-links 215    — ОБЧИСЛЕНЕ: 4×47 + 3×3 + 18""",
    """   N2 .side-links        — ОБЧИСЛЕНЕ від ВИДИМОЇ кількості: n×47 + (n−1)×3 + 18
                           (було зашито 4 — при 2 і 6 пунктах це брехало б)""",
    "18 · N2 коментар",
)
s = rep(
    s,
    """  var N1=Math.round(q('.brand').height), N2=Math.round(q('.side-links').height), N3=Math.round(q('.side-link').width);""",
    """  var N1=Math.round(q('.brand').height), N2=Math.round(q('.side-links').height), N3=Math.round(q('.side-link').width);
  var ls=V2.querySelectorAll('.side-links .side-link'), nvis=0;
  for(var k=0;k<ls.length;k++) if(getComputedStyle(ls[k]).display!=='none') nvis++;
  var N2want = nvis ? nvis*47 + (nvis-1)*3 + 18 : 0;""",
    "18 · N2 обчислення",
)
s = rep(
    s,
    """   '  N2 .side-links height '+(flush?ok(N2,215):N2+' —')+'   ОБЧИСЛЕНЕ 4×47 + 3×3 + 18\\n'+""",
    """   '  N2 .side-links height '+(flush?ok(N2,N2want):N2+' —')+'   ОБЧИСЛЕНЕ '+nvis+'×47 + '+(nvis-1)+'×3 + 18 = '+N2want+'\\n'+""",
    "18 · N2 рядок",
)
s = rep(
    s,
    """   '  .sidebar '+Math.round(sd.width)+'×'+got+'   пункт '+N3+'×'+Math.round(q('.side-link').height)+""",
    """   '  кадр '+state.frame+'   висота панелі '+state.fit+'   пунктів видимих '+nvis+' з '+state.set+'\\n'+
   '  .sidebar '+Math.round(sd.width)+'×'+got+'   пункт '+N3+'×'+Math.round(q('.side-link').height)+""",
    "18 · рядок стану",
)
# Д6 дійсний лише при висоті «на всю»: по вмісту панель навмисно коротша
s = rep(
    s,
    """   'Д6 · ПОВНА ВИСОТА       '+ok(got,want)+'   сцена '+stH+' − відступ '+inset+'×2\\n'+""",
    """   'Д6 · ПОВНА ВИСОТА       '+(state.fit==='full'?ok(got,want):got+' — (по вмісту: контроль не діє)')+
   '   сцена '+stH+' − відступ '+inset+'×2\\n'+""",
    "18 · Д6 під важіль",
)

# ── 19 · D · blur геть із JS ─────────────────────────────────────────
s = rep(
    s,
    """bind('rR','oR','--isl-radius','px'); bind('rI','oI','--isl-inset','px'); bind('rB','oB','--isl-blur','px');
g('rR').value=28; g('rI').value=16; g('rB').value=0;
V2.style.setProperty('--isl-radius','28px'); V2.style.setProperty('--isl-inset','16px'); V2.style.setProperty('--isl-blur','0px');
g('oR').textContent='28px'; g('oI').textContent='16px'; g('oB').textContent='0px';
shadow(); apply();""",
    """bind('rR','oR','--isl-radius','px'); bind('rI','oI','--isl-inset','px');
g('rR').value=28; g('rI').value=16;
V2.style.setProperty('--isl-radius','28px'); V2.style.setProperty('--isl-inset','16px');
g('oR').textContent='28px'; g('oI').textContent='16px';
build(); shadow(); apply();""",
    "19 · D blur з JS",
)

# ── 20б · K · лік переповнення сторінки (скарга оператора S55) ───────
# Заміряно: doc 1105 проти win 1080 — рівно 25 px, і саме на них замок
# ішов за нижню межу екрана. Причина: body мав min-height, тобто висоту
# НЕвизначену, і .stagewrap роздувався до змісту зліпка замість того, щоб
# ділити готову висоту. Визначена height:100dvh закриває це одним словом.
s = rep(
    s,
    """     color:#1C1E24;background:#eceff1;display:flex;flex-direction:column;min-height:100dvh}""",
    """     color:#1C1E24;background:#eceff1;display:flex;flex-direction:column;height:100dvh}""",
    "20б · K лік переповнення",
)

# ── 20 · контроль: blur не лишився ніде ──────────────────────────────
for dead in ["var(--isl-blur)", "backdrop-filter:blur", 'id="rB"', 'id="oB"', "'rB'", "'oB'"]:
    if dead in s:
        print("✗ залишок знятого важеля: %s" % dead)
        sys.exit(2)
steps.append("20 · контроль blur = 0 входжень")

out = s.encode("utf-8")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
prev = open(OUT, "rb").read() if os.path.exists(OUT) else None
open(OUT, "wb").write(out)

print("\n".join("  ✓ " + t for t in steps))
print("\nвихід: %s\n  байтів %d\n  md5 %s" % (OUT, len(out), md5(out)))
if prev is not None:
    print("  повтор: md5 %s" % ("ТОЙ САМИЙ ✓" if md5(prev) == md5(out) else "РОЗІЙШОВСЯ ✗"))
sys.exit(0)
