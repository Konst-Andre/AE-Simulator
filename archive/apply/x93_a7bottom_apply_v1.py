#!/usr/bin/env python3
"""x93_a7bottom_apply_v1.py · AE-Simulator · крок C1 (S72)
живе доки: X93 не витіснений новим ланцюгом продукту (або порт A2/A6 не прибрав тимчасові доми)

A7 «Система» = композиція мокапу: шапка · метрики · області. Під списком НІЧОГО (П101).
Старий низ роз'їжджається по своїх ключах (варіант 1, погоджено оператором S72):
  · сходинка драбини · ключ Groq · технічні дані → Models() на ключі `models` (живе доки: порт A6)
  · редактор даних → Editor() на ключі `ascen` (живе доки: порт A2)
  · «Судиться…» · «Вибрати файл…» · «Дані застосунку» → геть (В-82)
classifyJson / jsonErrorText / readFileText НЕ видаляються: smoke_ui_v1 :372–386 кличе їх
напряму, щабель 11 ЧЕРГИ забороняє чіпати гейт дельти до виселення смоуків.

Вхід: AE_WORK_index_X91_v1.html (md5 bd708e9948ad48ccb0c5591f089b23cc)
Запуск: python3 x93_a7bottom_apply_v1.py <вхід.html> <вихід.html>
Ідемпотентність: маркер — ВУЗОЛ реєстрації V2.models (П94); повтор = копія без змін, exit 0.
"""
import sys, re, hashlib

src_path, out_path = sys.argv[1], sys.argv[2]
s = open(src_path, encoding='utf-8').read()
MARK = "V2.models   = v2Adapt(Models);"

def rep(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        sys.exit(f"✗ {label}: очікував 1 входження, знайшов {n}")
    s = s.replace(old, new)
    print(f"  ✓ {label}")

if MARK in s:
    print("= маркер X93-C1 уже є — повтор без змін")
else:
    # 1 · CSS старого низу A7 — мертвий
    rep(""".v2 .sys-checks > .sys-src { margin:14px 0 6px; }   /* специфічніше за старе .sys-src — воно стоїть нижче */
.v2 .sys-link { padding:0; border:0; background:none; color:inherit; font:inherit; text-decoration:underline; text-underline-offset:2px; cursor:pointer; }
.v2 .sys-link:hover { color:var(--anc-text, #1C1E24); }
.v2 .sys-src { margin:0 0 6px; color:var(--soft); font-size:12px; }
.v2 .sys-bad { color:var(--loss); }
.v2 .sys-h { margin:32px 0 10px; font-size:17px; }
""", """/* X93-C1: .sys-src · .sys-link · .sys-bad · .sys-h — геть разом зі старим низом A7 (В-82). */
""", "CSS старого низу A7")

    # 2 · Settings → Models (тимчасовий дім) + новий Settings = лише мокап
    rep("""function Settings(root){
  /* Х22.4: налаштування (ключ, модель, редактор) — кураторські (В-27), тож лише за дверима. */
  if(!CURATOR.open){ S.screen='picker'; render(); return; }""",
"""function Settings(root){
  /* X93-C1 · A7 «Система» = композиція мокапу: шапка · метрики · області. Під списком
     НІЧОГО (П101). Старий низ роз'їхався по своїх ключах: сходинка, ключ і технічні
     дані → Models (`models`), редактор → Editor (`ascen`). Вибору файлу немає (В-82). */
  if(!CURATOR.open){ S.screen='picker'; render(); return; }
  /* Час прогону пише dataCheck — у шапку сторінки. */
  const stamp = el('small',{class:'sys-stamp'});
  put(root, el('div',{class:'page admin-page'},[
    el('header',{class:'page-title'},[
      el('div',{},[el('h1',{text:'Система'}), el('p',{text:'Стан автоматичних перевірок'})]),
      stamp
    ]),
    dataCheck(stamp)
  ]));
}

function Models(root){
  /* X93-C1 · ТИМЧАСОВИЙ дім сходинки драбини, ключа Groq і технічних даних — тіло
     старого Settings дослівно, разом із замиканнями (keyInput · test · drawRungs).
     живе доки: порт A6 «AI / Моделі» (ЧЕРГА щабель 4, В-78).
     Х22.4: ключ і модель — кураторські (В-27), тож лише за дверима. */
  if(!CURATOR.open){ S.screen='picker'; render(); return; }""", "Settings → Models + новий Settings")

    rep("""  /* X89-A7: форма A7 мокапу. Час прогону пише dataCheck — у шапку сторінки. */
  const stamp = el('small',{class:'sys-stamp'});
  put(root, el('div',{class:'page admin-page'},[
    el('header',{class:'page-title'},[
      el('div',{},[el('h1',{text:'Система'}), el('p',{text:'Стан автоматичних перевірок'})]),
      stamp
    ]),
    dataCheck(stamp),
    el('h2',{class:'sys-h',text:'Технічне'}),
""", """  put(root, el('div',{class:'page admin-page'},[
    el('header',{class:'page-title'},[
      el('div',{},[el('h1',{text:'AI / Моделі'}),
        el('p',{text:'Тимчасово тут: сходинка драбини, ключ Groq і технічні дані'})])
    ]),
""", "шапка Models, без dataCheck і «Технічне»")

    rep("""    status,
    editEntry(),
""", """    status,
""", "Models без входу в редактор")

    # 3 · dataCheck без вибору файлу
    rep("""  /* Логіка панелі 6а — без змін: runRules() · picked · takeFiles · classifyJson.""",
        """  /* Логіка панелі 6а: runRules() на даних застосунку. Вибору файлу немає (В-82, X93-C1).""",
        "коментар dataCheck")
    rep("""  const srcText  = el('span');
  const fileNote = el('p',{class:'sys-src sys-bad',style:'display:none'});
  const picked = {cat:null, scen:null, catName:'', scenName:''};
""", "", "dataCheck: srcText · fileNote · picked")
    rep("""    srcText.textContent = 'Судиться: каталог — ' + (picked.catName || 'дані застосунку') +
                          ' · сценарії — ' + (picked.scenName || 'дані застосунку') + ' · ';
    const r = runRules(picked.cat, picked.scen);""",
        """    const r = runRules(null, null);""", "dataCheck: рядок «Судиться»")
    m = re.search(r"\n  /\* ⚠ accept НЕ ставимо\..*?\n(  run\(\);   /\* В-76 \*/)", s, re.S)
    if not m or s.count("/* ⚠ accept НЕ ставимо.") != 1:
        sys.exit("✗ dataCheck: блок вибору файлу не знайдено рівно один раз")
    s = s[:m.start()] + "\n" + m.group(1) + s[m.end():]
    print("  ✓ dataCheck: fileIn · takeFiles · srcLine")
    rep("""  return el('section',{class:'sys-checks'},[sum, list, srcLine, fileNote]);""",
        """  return el('section',{class:'sys-checks'},[sum, list]);""", "dataCheck: повернення")
    rep("""function classifyJson(v){""",
        """/* X93-C1: продукт більше не кличе classifyJson · jsonErrorText · readFileText (вибір файлу A7
   геть, В-82). живе доки: виселення смоуків — smoke_ui_v1 :372–386 кличе їх напряму (щабель 11). */
function classifyJson(v){""", "примітка над функціями файлу")

    # 4 · editEntry — мертвий
    m = re.search(r"function editEntry\(\)\{\n.*?\n  return box;\n\}\n\n", s, re.S)
    if not m or s.count("function editEntry(){") != 1:
        sys.exit("✗ editEntry не знайдено рівно один раз")
    s = s[:m.start()] + s[m.end():]
    print("  ✓ editEntry геть")

    # 5 · Editor у домі `ascen`: навігація — панель, «назад» на A7 не веде
    rep("""      el('div',{class:'toprow'},[backBtn('назад',()=>{S.screen='settings';render()})]),
""", "", "Editor: «назад» на settings геть")
    rep("""  if(!rec){ S.screen='edit'; render(); return; }""",
        """  if(!rec){ S.screen='ascen'; render(); return; }""", "ScenCard: без запису → ascen")
    rep("""backBtn('до списку',()=>{S.screen='edit';render()})""",
        """backBtn('до списку',()=>{S.screen='ascen';render()})""", "ScenCard: «до списку» → ascen")

    # 6 · реєстрація тимчасових домів
    rep("""V2.escen    = v2Adapt(ScenCard);
""", """V2.escen    = v2Adapt(ScenCard);
V2.models   = v2Adapt(Models);   /* X93-C1 · тимчасово · живе доки: порт A6 */
V2.ascen    = v2Adapt(Editor);   /* X93-C1 · тимчасово · живе доки: порт A2 */
""", "V2.models · V2.ascen")
    rep("""   Обидва кураторські пункти — заглушки, поки немає екранів (живість з V2, П80). */""",
        """   Обидва кураторські пункти — заглушки, поки немає екранів (живість з V2, П80).
   X93-C1: 'ascen' живий тимчасово — старий Editor до порту A2. */""", "коментар ascen")

open(out_path, 'w', encoding='utf-8').write(s)
print("вихід:", out_path, "· md5", hashlib.md5(s.encode('utf-8')).hexdigest())
