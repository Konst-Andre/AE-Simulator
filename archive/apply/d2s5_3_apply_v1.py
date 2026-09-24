#!/usr/bin/env python3
"""d2s5_3_apply_v1.py · AE-Simulator · S86 · D2 крок 5.3 — JS острова: публікація оживає (Р1 / В-146 знято)
живе доки: запечено в X107 (лежить в archive/apply/ як ланцюг)
Вхід: корінь AE (index.html X106 4254b656…). Пише <вихід>/index.html.
· вхід в острів кличе loadSnap (як старий Editor :3636); стан S.epub → смуга #m-sync (paintSync, у paint()).
· «Опублікувати» → publish() рушія; пише лише на зеленій звірці або після відмови по коду (як старий редактор).
· поле коду → EDITKEY.code (памʼять модуля, не S і не диск); Enter у полі = «Опублікувати».
· «Звірити ще раз» → нова звірка. Після успішного запису esnap порожній: нові правки просять звірку (sha воркер
  не повертає, а перечитати одразу — ризик «застаріло» від відставання API).
· успіх — тостом один раз (S.epub.done/shown): publish сам перемальовує екран, тост старого екземпляра острова
  лишився б у відʼєднаному DOM.
Кожна заміна — assert ×1. Повтор на виході = відмова (П34).
Запуск: python3 d2s5_3_apply_v1.py <корінь AE> <тека виходу>
"""
import sys, hashlib, pathlib
root, out = map(pathlib.Path, sys.argv[1:3]); out.mkdir(parents=True, exist_ok=True)
t = (root/'index.html').read_text(encoding='utf-8')
assert hashlib.md5(t.encode()).hexdigest().startswith('4254b656'), 'вхід не X106'

def sub(s, R):
    for a, b in R:
        n = s.count(a); assert n == 1, (n, a[:70]); s = s.replace(a, b)
    return s

R = [
# ── рушій: мітка успіху для тоста ──
("  S.epub = {state:'ok', text:(j.text||'Збережено.')",
 "  S.epub = {state:'ok', done:true, text:(j.text||'Збережено.')"),
# ── paint: Р1 геть, стан запису — paintSync ──
("""  /* Р1 · публікація з острова — D2 крок 5: mergeDraft поки губить нові записи (ходить лише по id файлу) */
  pub.disabled = true;
""", ""),
("""  pub.title = blockers.length ? 'Спершу виправте проблеми: '+blockers.map(i=>cur(i).title||'Без назви').join(', ') : dirty.length>1 ? 'Опублікує зміни в '+plural(dirty.length,'сценарії','сценаріях','сценаріях') : '';
""",
"""  pub.title = blockers.length ? 'Спершу виправте проблеми: '+blockers.map(i=>cur(i).title||'Без назви').join(', ') : dirty.length>1 ? 'Опублікує зміни в '+plural(dirty.length,'сценарії','сценаріях','сценаріях') : '';
  paintSync(pub, dirty);
"""),
("function paintPub(dirty, blockers){",
"""/* D2 крок 5.3 · смуга запису: стан S.epub рушія (loadSnap/publish) → #m-sync. Дані (#m-pub) і запис — різні предмети.
   Пише лише зелена звірка або відмова по коду — як старий редактор (:3806). Помилка — role=alert, очікування — status. */
function paintSync(pub, dirty){
  const w=$('#m-sync'); if(!w) return;
  const e=S.epub; let tone='bad', text='', lines=[], code=false, again=false, block=false;
  if(!pubReady()){ text='Публікація недоступна: у config.json не оголошено editEndpoint або sourceApi.'; block=true; }
  else if(!e || e.state==='busy'){ tone='busy'; text=(e&&e.text)||'Звіряємо з репозиторієм…'; block=true; }
  else if(e.state==='ok' && !S.esnap){ block=true;
    if(dirty.length){ tone='busy'; text='Нові правки після публікації — спершу звірте з репозиторієм.'; again=true; } }
  else if(e.state==='ok'){ }
  else if(e.state==='code'){ text=e.text; code=true; }
  else { text=e.text; lines=e.lines||[]; again=true; block=true; }
  w.hidden=!text; w.dataset.tone=tone; w.setAttribute('role', tone==='bad' ? 'alert' : 'status');
  $('#m-sync-t').textContent=text; $('#m-sync-l').textContent=lines.join(' · ');
  $('#m-code').hidden=!code; $('#resync').hidden=!again;
  const f=$('#f-code'); if(f.value!==EDITKEY.code) f.value=EDITKEY.code;
  if(block){ pub.disabled=true; if(text) pub.title=text; }
}

function paintPub(dirty, blockers){"""),
# ── події ──
("""  if (e.key==='Enter' && ['f-title','f-who','f-mode'].includes(e.target.id)) e.preventDefault();
""",
"""  if (e.key==='Enter' && ['f-title','f-who','f-mode'].includes(e.target.id)) e.preventDefault();
  if (e.key==='Enter' && e.target.id==='f-code'){ e.preventDefault(); if(!$('#pub').disabled) publish(); }
"""),
("""  if (t.id==='q'){ st.q=t.value; drawList(); return; }
""",
"""  if (t.id==='q'){ st.q=t.value; drawList(); return; }
  if (t.id==='f-code'){ EDITKEY.code=t.value; return; }   /* 5.3 · ключ — лише памʼять модуля */
"""),
("  if(t.id==='pub'){ return; }   /* Р1 · крок 5 */",
 "  if(t.id==='pub'){ publish(); return; }   /* 5.3 · Р1 знято: запис — publish() рушія */\n"
 "  if(t.id==='resync'){ S.epub=null; S.esnap=null; loadSnap(); return; }"),
# ── вхід: звірка до першого малювання; успіх — тостом один раз ──
("""  drawEditor();
  Object.assign(window, {set, drawEditor, openGroups, drawGroups, ask, toast, cur, st});""",
"""  if(pubReady() && S.epub===null) loadSnap();   /* 5.3 · звірка на вході, як старий Editor */
  drawEditor();
  if(S.epub && S.epub.done && !S.epub.shown){ S.epub.shown=true; toast(S.epub.text); }
  Object.assign(window, {set, drawEditor, openGroups, drawGroups, ask, toast, cur, st});"""),
]
t = sub(t, R)
(out/'index.html').write_text(t, encoding='utf-8')
print('index.html', hashlib.md5(t.encode()).hexdigest())
