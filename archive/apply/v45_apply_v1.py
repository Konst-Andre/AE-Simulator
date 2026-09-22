#!/usr/bin/env python3
"""v45_apply_v1.py · AE-Simulator · S83 · D1 v4.5 — вироки В-118…В-126 (S80 §3) на шаблон v4.4
живе доки: одноразовий; після пушу — archive/apply/
Запуск: python3 v45_apply_v1.py <mock_a2v2_tpl_v4_4.html> <mock_a2v2_tpl_v4_5.html>
Кожна заміна — рівно одне входження (assert). Детермінований."""
import sys, pathlib, hashlib
src = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'); t = src
def R(old, new, n=1):
    global t
    c = t.count(old); assert c == n, f'{c}× замість {n}: {old[:70]!r}'
    t = t.replace(old, new)

# ── HTML/CSS ──
# В-121 · оверлейні скролбари Chrome: горизонталь прев'ю закрито
R('.pv{position:sticky;top:20px;max-height:calc(100vh - 40px);overflow:auto;min-width:0}',
  '.pv{position:sticky;top:20px;max-height:calc(100vh - 40px);overflow:auto;overflow-x:hidden;min-width:0}')
# В-125 · тост (bottom 24 + ~40 висоти) не накриває останній рядок: низ робочої зони 96px
R('.page{padding:20px 20px 40px 234px;', '.page{padding:20px 20px 96px 234px;')
# В-124 · розрив між деструктивом і парою: 8 (gap) + 16 = 24px
R('.btn.danger.solid{', '#delSc{margin-inline-end:16px}\n.btn.danger.solid{')
# В-118 · рядок групи: радіо «за замовчуванням» першою колонкою
R('.grow{display:grid;grid-template-columns:minmax(0,1fr) 96px 34px;gap:8px;align-items:center}',
  '.grow{display:grid;grid-template-columns:20px minmax(0,1fr) 96px 34px;gap:8px;align-items:center}\n'
  '.grow input[type=radio]{width:18px;height:18px;margin:0;accent-color:var(--anc-blue)}\n'
  '.grow small em{display:block;font-style:normal;color:var(--anc-blue)}')
# В-122 · «i» у шапці діалогу груп
R('<div class="dg-h"><div><b id="dgt">Групи сценаріїв</b><small>',
  '<div class="dg-h"><div><b id="dgt">Групи сценаріїв</b> <button type="button" class="info" popovertarget="i-grp" aria-label="Що можна робити з групами" aria-expanded="false">i</button>'
  '<div class="tip" id="i-grp" popover><b>Групи сценаріїв</b>Групи — полиці, по яких розкладено сценарії; за ними фільтрується список ліворуч. '
  'Тут можна перейменувати групу (нову назву отримають усі її сценарії), додати нову й видалити порожню. '
  'Кружечок ● — група за замовчуванням: сюди лягає новий сценарій, коли в списку обрано «Усі групи». Її не видалити — спершу позначте іншу. '
  'Зміни назв ідуть у чернетку й діють після «Опублікувати».</div><small>')
# В-123 · обидва «Скасувати» в діалогах — звичайна .btn, як на головному екрані
R('<button class="btn ghost" data-dgcancel>Скасувати</button>', '<button class="btn" data-dgcancel>Скасувати</button>')
R('<button class="btn ghost" id="dcNo">Скасувати</button>', '<button class="btn" id="dcNo">Скасувати</button>')

# ── JS ──
# В-118 · явний змінюваний дефолт: держиться за групу, не за «першу за абеткою»
R("const st = { pub:{}, draft:{}, del:{}, created:{}, extraGroups:[], sel:null, grp:'', q:'', view:'form' };",
  "const st = { pub:{}, draft:{}, del:{}, created:{}, extraGroups:[], sel:null, grp:'', q:'', view:'form', defGrp:'' };")
R("for (const x of st.extraGroups) if(!g.includes(x)) g.push(x);\n",
  "for (const x of st.extraGroups) if(!g.includes(x)) g.push(x);\n  /* v4.5 · В-118: група за замовчуванням живе завжди, навіть порожня */\n  if(st.defGrp && !g.includes(st.defGrp)) g.push(st.defGrp);\n")
R("  return g.sort((a,b)=>a.localeCompare(b,'uk')); };\n",
  "  return g.sort((a,b)=>a.localeCompare(b,'uk')); };\n"
  "/* v4.5 · В-118: стартовий дефолт — «Базові»; далі Оля змінює в діалозі груп */\n"
  "st.defGrp = groupsNow().includes('Базові') ? 'Базові' : (groupsNow()[0] || '');\n")
R("grp: st.grp || groupsNow()[0],", "grp: st.grp || st.defGrp,")
R("function openGroups(){ gw = groupsNow().map(g=>({old:g, name:g, gone:false}));",
  "function openGroups(){ gw = groupsNow().map(g=>({old:g, name:g, gone:false, def:g===st.defGrp}));")
R('''    return `<div class="grow"><input class="in" data-gi="${i}"''',
  '''    return `<div class="grow"><input type="radio" name="gdef" data-gdef="${i}" ${r.def?'checked':''} aria-label="Група за замовчуванням: ${esc(r.name||'без назви')}" title="Сюди лягають нові сценарії">
      <input class="in" data-gi="${i}"''')
R('''      <small>${plural(n,'сценарій','сценарії','сценаріїв')}</small>
      <button class="x" data-gdel="${i}" ${n?'disabled':''} title="${n?'Спершу перенесіть сценарії в іншу групу':'Видалити порожню групу'}" aria-label="Видалити групу">🗑</button>''',
  '''      <small>${plural(n,'сценарій','сценарії','сценаріїв')}${r.def?'<em>за замовчуванням</em>':''}</small>
      <button class="x" data-gdel="${i}" ${n||r.def?'disabled':''} title="${r.def?'Групу за замовчуванням не видалити — спершу позначте іншу':n?'Спершу перенесіть сценарії в іншу групу':'Видалити порожню групу'}" aria-label="Видалити групу">🗑</button>''')
R('''+ `<p class="hint msg" style="color:var(--anc-gray)">Порожня група живе, доки в ній з'явиться хоч один сценарій. Нову назву отримають усі сценарії групи.</p>`;''',
  '''+ `<p class="hint msg" style="color:var(--anc-gray)">● — група за замовчуванням: сюди лягає новий сценарій при «Усі групи». Порожня група живе, доки в ній з'явиться хоч один сценарій. Нову назву отримають усі сценарії групи.</p>`;''')
R("    pruneGroups(); $('#dg').close(); drawEditor();\n    toast(ren.length ? 'Групи змінено — у чернетці, публікуйте або скасуйте' : 'Групи оновлено');",
  "    const d = gw.find(r=>r.def && !r.gone), was = st.defGrp; if(d) st.defGrp = d.name.trim();\n"
  "    pruneGroups(); $('#dg').close(); drawEditor();\n"
  "    const moved = d && d.old!==was ? ' · нові сценарії лягають у «'+st.defGrp+'»' : '';\n"
  "    toast((ren.length ? 'Групи змінено — у чернетці, публікуйте або скасуйте' : 'Групи оновлено') + moved);")
R("  if(t.id==='gf'){ st.grp=t.value; drawList(); return; }",
  "  if(t.id==='gf'){ st.grp=t.value; drawList(); return; }\n"
  "  if(t.dataset.gdef!==undefined){ gw.forEach((r,i)=>r.def = i===+t.dataset.gdef); drawGroups(); $(`[data-gdef=\"${t.dataset.gdef}\"]`)?.focus(); return; }")
# В-119 · орієнтир не бреше: немає набору → «—»; приріст ≤0 → «0 ₴»
R("  const pot = Math.max(1, Math.round(bonus(s[RULE]) - bonus(s.order)));",
  "  /* v4.5 · В-119: Math.max(1,…) знято. Порожній ідеальний набір → «—»; приріст ≤0 → чесні «0 ₴» */\n"
  "  const potN = Math.round(bonus(s[RULE]) - bonus(s.order));\n"
  "  const potTxt = s.noSale || !s[RULE].length ? '—' : potN > 0 ? 'до +'+potN.toLocaleString('uk-UA')+' ₴' : '0 ₴';")
R("${s.noSale ? '—' : 'до +'+pot.toLocaleString('uk-UA')+' ₴'}", "${potTxt}")
# В-120 · набір не за правилом сценарію підписаний явно
R("hset(ALT, LAB[ALT], 'теж добре')", "hset(ALT, LAB[ALT], 'теж добре · у орієнтир не входить')")
# В-126 · крапка — найважчий стан: err > warn > draft
R("    const mark = e ? 'err' : ch ? 'draft' : w ? 'warn' : '';\n    const tip = st.del[id]?'Буде видалено після публікації':e?'Є проблема':ch?'Є неопубліковані зміни':w?'Є попередження':'';",
  "    /* v4.5 · В-126: найважчий стан, не найновіший (Н11). Видалений — лише «чернетка»: його попередження вже неважливі */\n"
  "    const mark = st.del[id] ? 'draft' : e ? 'err' : w ? 'warn' : ch ? 'draft' : '';\n"
  "    const tip = st.del[id]?'Буде видалено після публікації':e?'Є проблема':w?(ch?'Є попередження і неопубліковані зміни':'Є попередження'):ch?'Є неопубліковані зміни':'';")
# номер версії в коментарі-шапці, якщо є
dst = pathlib.Path(sys.argv[2]); dst.write_text(t, encoding='utf-8')
print('вихід:', dst, '· md5', hashlib.md5(t.encode()).hexdigest())
