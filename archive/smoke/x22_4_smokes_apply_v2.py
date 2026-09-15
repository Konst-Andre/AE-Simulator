# x22_4_smokes_apply_v2.py — v1 + Х22.4б (device S43): smoke_ui — око дверей (сховано · показує на місці · × скидає ·
#   відмикання скидає) і одне кільце фокуса. Стоїть у ланцюгу ЗАМІСТЬ v1.
# x22_4_smokes_apply_v1.py — Х22.4: смоуки продукту мігрують тим самим кроком, що й двері (П12)
#   smoke_ui_v1: мок POST за зразком ae-edit.js (код до тіла: 403 / 400) · Settings лише за дверима ·
#                нові твердження дверей (картка, розкриття на місці, чужий код) · панель перевірки без замка
#                (мертве: «чужий код не відкриває вивід» — замка в панелі немає, двері вже пройдено)
#   smoke_edit_ui_v1: openEditor — через двері (мок уже вміє 403); стук дверей не рахується записом;
#                код із дверей уже в полі публікації; сторож порожнього коду судиться на стертому полі
# живе доки: пуш Х22 (тоді смоуки в репо)   запуск: python3 x22_4_smokes_apply_v1.py <тека AE>   Ідемпотентний.
import sys, os
d = os.path.abspath(sys.argv[1])
def patch(fn, pairs):
    p = os.path.join(d, 'tools', fn); s = open(p, encoding='utf-8').read()
    for name, old, new in pairs:
        if new in s: continue
        assert s.count(old) == 1, (fn, name, s.count(old)); s = s.replace(old, new, 1)
    open(p, 'w', encoding='utf-8').write(s)
UI = [
 ('код дверей', "const dom=new JSDOM(html,{runScripts:'dangerously',url:'https://x.test/?mock=1',",
  "/* Х22.4: код дверей — кирилицею свідомо: латиниця проїхала б і без відсоткового кодування. */\nconst DOOR_CODE='код дверей';\nconst dom=new JSDOM(html,{runScripts:'dangerously',url:'https://x.test/?mock=1',"),
 ('мок POST', "    w.fetch=(u)=>{ const raw=fs.readFileSync(path.join(BASE,files[u]||u),'utf8');",
  "    w.fetch=(u,o)=>{\n      /* Х22.4: двері питають воркер. Мок — як ae-edit.js: код до тіла; не той → 403, той → 400 «немає даних». */\n      if(o && o.method==='POST'){ let g=(o.headers||{})['x-ae-edit-code']||'';\n        /* як браузер: символ поза ISO-8859-1 у заголовку — TypeError до мережі (некодована кирилиця) */\n        if(/[^\\x00-\\xff]/.test(g)) return Promise.reject(new TypeError('non ISO-8859-1 code point'));\n        try{ g=decodeURIComponent(g); }catch(_){}\n        return Promise.resolve({ok:false, status:g===DOOR_CODE?400:403, json:()=>Promise.resolve({})}); }\n      const raw=fs.readFileSync(path.join(BASE,files[u]||u),'utf8');"),
 ('марка за дверима', "  S.screen='settings'; w.render();\n  T('марка збірки видима",
  "  w.eval('CURATOR.grant()'); S.screen='settings'; w.render(); /* Х22.4: Settings лише за дверима; самі двері — у «Налаштуваннях» нижче */\n  T('марка збірки видима"),
 ('двері знову зачинені', "  T('марка взята з config, не зашита в код', !src.includes('Збірка '+S.cfg.build));\n",
  "  T('марка взята з config, не зашита в код', !src.includes('Збірка '+S.cfg.build));\n  w.eval('CURATOR.open=false'); S.screen='picker'; w.render();\n  T('без дверей Settings не відкривається', (S.screen='settings', w.render(), S.screen==='picker'));\n"),
 ('двері', "  click('Кураторський режим').click();\n  T('екран налаштувань', S.screen==='settings');",
  "  /* Х22.4: двері — картка з замком; код питає воркер (мок вище) */\n  const doorHead=()=>d.querySelector('.v2 .door [data-v2-door=head]');\n  const dIn=()=>d.querySelector('.v2 .door-input'), dGo=()=>d.querySelector('.v2 .door [data-v2-door=go]');\n  T('двері — «Кураторський режим · відкривається кодом»', !!doorHead() && /Кураторський режим/.test(doorHead().textContent) && /відкривається кодом/.test(doorHead().textContent));\n  doorHead().click();\n  T('двері розкрились на місці: поле й «Відімкнути», екран той самий', !!dIn() && !!dGo() && S.screen==='picker');\n  dIn().value='не той код'; dIn().dispatchEvent(new w.Event('input')); dGo().click(); await new Promise(r=>setTimeout(r,60));\n  T('чужий код: «Код не підходить.», двері зачинені', S.screen==='picker' && !w.eval('CURATOR.open') && /Код не підходить/.test((d.querySelector('.v2 .door')||{}).textContent||''));\n  dIn().value=DOOR_CODE; dIn().dispatchEvent(new w.Event('input')); dGo().click(); await new Promise(r=>setTimeout(r,60));\n  T('екран налаштувань', S.screen==='settings');"),
 ('поля коду куратора немає', "  T('поле коду куратора є', !!codeField);",
  "  T('поля коду куратора немає — одні двері (Х22.4)', !codeField);"),
 ('панель без замка', "  if(codeField && panel){\n    codeField.value='не той код'; codeField.dispatchEvent(new w.Event('input'));\n    click('Перевірити дані').click();\n    T('чужий код не відкриває вивід', !/підсумок: ✓/.test(panel.textContent));\n    codeField.value=S.cfg.curatorCode; codeField.dispatchEvent(new w.Event('input'));\n    click('Перевірити дані').click();\n    T('правильний код друкує підсумок',",
  "  if(!codeField && panel){\n    /* Х22.4: мертве — «чужий код не відкриває вивід»: замка в панелі немає, двері вже пройдено. */\n    T('до кнопки виводу немає', !/підсумок: ✓/.test(panel.textContent));\n    click('Перевірити дані').click();\n    T('кнопка друкує підсумок',"),
]
# Х22.4б: око вшито в «двері» того самого списку, а не окремою парою — інакше повтор бачить «двері» зміненими
# і падає (ідемпотентність доведено повтором, П18).
A1, N1 = "  dIn().value='не той код'; dIn().dispatchEvent(new w.Event('input')); dGo().click();", "  /* Х22.4б (device S43, В-30): око — показати/сховати код; скидається разом із дверима */\n  const dEye=()=>d.querySelector('.v2 .door [data-v2-door=eye]');\n  T('поле сховане: password, око «Показати код», не натиснуте', dIn().type==='password' && !!dEye() && dEye().getAttribute('aria-pressed')==='false' && dEye().getAttribute('aria-label')==='Показати код' && !!dEye().querySelector('use,svg'));\n  dIn().value='абв'; dIn().dispatchEvent(new w.Event('input')); dEye().click();\n  T('око показує введене на місці: text, значення ціле, фокус у полі, «Сховати код»', dIn().type==='text' && dIn().value==='абв' && d.activeElement===dIn() && dEye().getAttribute('aria-pressed')==='true' && dEye().getAttribute('aria-label')==='Сховати код' && S.screen==='picker');\n  d.querySelector('.v2 .door-x').click(); doorHead().click();\n  T('× скидає око: знову password і порожньо', dIn().type==='password' && dIn().value==='' && dEye().getAttribute('aria-pressed')==='false');\n  dEye().click();\n  dIn().value='не той код'; dIn().dispatchEvent(new w.Event('input')); dGo().click();"
A2, N2 = "  T('екран налаштувань', S.screen==='settings');", "  T('екран налаштувань', S.screen==='settings');\n  T('після відмикання око скинуто (код не лишається відкритим)', w.eval('DOOR.show')===false);\n  T('поле дверей — одне кільце фокуса: outline знято, рідне око Edge сховане', html.includes('.v2 .door .door-input:focus-visible { outline:none; }') && html.includes('.v2 .door .door-input::-ms-reveal { display:none; }'));"
k = [x[0] for x in UI].index('двері'); nm, old, new = UI[k]
assert new.count(A1) == 1 and new.count(A2) == 1, 'якорі ока в «двері»'
UI[k] = (nm, old, new.replace(A1, N1, 1).replace(A2, N2, 1))
patch('smoke_ui_v1.js', UI)
patch('smoke_edit_ui_v1.js', [
 ('двері замість кнопки', "  click('Кураторський режим').click();\n",
  "  /* Х22.4: двері — картка з замком; код питає воркер (мок нижче вміє 403 і 200 за EDIT_CODE) */\n  d.querySelector('.v2 .door [data-v2-door=head]').click();\n"),
 ('код дверей замість коду куратора', "  const codeField=[...d.querySelectorAll('input')]\n    .find(i=>i.getAttribute('placeholder')==='код куратора');\n  door.badCode = (()=>{ codeField.value='не той код';\n    codeField.dispatchEvent(new w.Event('input'));\n    click('Перевірити дані').click();\n    return !visible(); })();\n  codeField.value=w.S.cfg.curatorCode; codeField.dispatchEvent(new w.Event('input'));\n  click('Перевірити дані').click();\n  door.shownAfter = visible();",
  "  const dIn=()=>d.querySelector('.v2 .door-input'), dGo=()=>d.querySelector('.v2 .door [data-v2-door=go]');\n  const tryDoor=async v=>{ dIn().value=v; dIn().dispatchEvent(new w.Event('input')); dGo().click();\n    await new Promise(r=>setTimeout(r,60)); };\n  await tryDoor('не той код'); door.badCode = !visible() && !w.eval('CURATOR.open');\n  await tryDoor(EDIT_CODE); door.shownAfter = visible();\n  door.keyFromDoor = w.eval('EDITKEY.code')===EDIT_CODE;\n  /* Стук дверей — не публікація: лічильник записів починається після них. */\n  w.__gh.posts.length = 0;"),
 ('твердження дверей', "  T('після коду куратора вхід зʼявляється без перемальовування екрана', A.door.shownAfter);",
  "  T('після коду дверей вхід у редактор є', A.door.shownAfter);\n  T('код із дверей уже лежить у ключі запису (публікація не питає вдруге)', A.door.keyFromDoor);"),
 ('сторож на стертому полі', "  const readsWas = P.w.__gh.reads.length;\n  P.pub().click(); await tick();",
  "  P.key(''); /* Х22.4: двері вписали код самі — сторожа порожнього коду судимо на стертому полі */\n  const readsWas = P.w.__gh.reads.length;\n  P.pub().click(); await tick();"),
 ('один ключ', "     Код редактора — не код куратора. Перший відмикає екран і лежить у\n     публічному config.json; другий відмикає запис і не лежить ніде. */\n  T('поле коду редактора стоїть у смузі й назване іншим ключем',",
  "     Х22.4: код один — ним відмикаються двері, і він же відмикає запис; ніде не лежить. */\n  T('поле коду редактора стоїть у смузі й назване кодом дверей',"),
 ('текст підпису', "[...P.d.querySelectorAll('.pubbar')].some(x=>/НЕ код куратора/.test(x.textContent)));",
  "[...P.d.querySelectorAll('.pubbar')].some(x=>/яким відімкнено двері/.test(x.textContent)));"),
])
print('смоуки Х22.4+4б застосовано: smoke_ui_v1.js, smoke_edit_ui_v1.js')
