#!/usr/bin/env python3
"""x97_a2frame_apply_v1.py · AE-Simulator · S73 · щабель 2 · крок C1 (каркас A2)
живе доки: A2 «Сценарії» не переписано наново

`ascen` перестає бути тимчасовим домом редактора (В-83) і стає екраном A2 у композиції
мокапу X21 (П101): список · форма · попередній перегляд. РУШІЙ НЕ ЧІПАЄТЬСЯ:
ліва колонка — Editor (фільтри, звірка, публікація), центр — ScenCard (edraft, правила,
межа mood), праворуч — картка E1 з recOf. «Правити» в A2 міняє форму НА МІСЦІ (SPEC §7.1).
Входи (П103, греп S73): `S.screen='escen'` — лише «Правити» (:2967). Поза A2 (старий
ключ `edit`) кнопка веде, як і раніше, в `escen`. `V2.escen` лишається: живе доки C2.

Вхід: AE_WORK_index_X96_v1.html (md5 3088cb4ba50fa9eb3cc2aa0f02aa11ff)
Запуск: python3 x97_a2frame_apply_v1.py <вхід.html> <вихід.html>
Ідемпотентність: маркер — ВУЗОЛ `function A2Scen(root)` (П94).
"""
import sys, hashlib
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
MARK = "function A2Scen(root){"
FN = r"""/* X97-C1 · A2 «Сценарії» = композиція мокапу X21 навколо чинного рушія (П101). */
function A2Scen(root){
  if(!CURATOR.open){ S.screen='settings'; render(); return; }
  const ids = S.SCEN.map(x=>String(x.id));
  /* Обраний запис зник (дані перезавантажились) — беремо перший, а не петлю через ScenCard. */
  if(S.escen===null || !ids.includes(String(S.escen))) S.escen = ids.length ? ids[0] : null;
  const listCol = el('div',{class:'a2-col a2-list'});
  const formCol = el('div',{class:'a2-col a2-form'});
  const prevCol = el('aside',{class:'a2-col a2-prev'});
  Editor(listCol);                 if(S.screen!=='ascen') return;
  if(S.escen!==null){ ScenCard(formCol); if(S.screen!=='ascen') return; }
  const id = S.escen===null ? null : String(S.escen);
  const rec = id===null ? null : recOf(id);
  if(rec){
    const dr = draftFields(id);
    prevCol.append(
      el('h2',{class:'a2-h',text:'Попередній перегляд'}),
      el('p',{class:'a2-cap',text:'Так картка виглядатиме в E1'}),
      el('article',{class:'a2-card'},[
        el('span',{class:'a2-no',text: rec.no ? '#'+rec.no : 'Оформлення на місці'}),
        el('h3',{text:rec.title||'без назви'}),
        el('span',{class:'a2-tag',text:rec.grp||'—'}),
        el('p',{text:(rec.who||'—')+' · '+(rec.order||[]).length+' поз.'}),
        rec.noSale ? el('p',{text:'Правильна дія — нічого не пропонувати.'}) : null]),
      /* Поля status у даних немає: «чернетка» = є незбережені правки цього запису. */
      el('span',{class:'a2-badge'+(dr.length?' draft':''),text: dr.length?'чернетка':'опубліковано'}));
  }
  root.append(el('div',{class:'a2'},[listCol, formCol, prevCol]));
}
V2.settings = v2Adapt(Settings);"""
CSS = """.v2 .system-message small.sys-hint { color:#34465c; }   /* X94-C3 · підказка дії темніша за лічильник */
/* X97-C1 · A2 три колонки мокапу; ≤1440 — перегляд під формою (замір S73) */
.v2 .a2 { display:grid; grid-template-columns:300px minmax(0,1fr) 260px; gap:20px; align-items:start; }
.v2 .a2-col { min-width:0; }
.v2 .a2-prev { position:sticky; top:16px; background:#fff; border:1px solid #e3e8ee; border-radius:14px; padding:16px; }
.v2 .a2-h { font-size:16px; margin:0 0 2px; } .v2 .a2-cap { font-size:12.5px; color:#6b7a8c; margin:0 0 12px; }
.v2 .a2-card { border:1px solid #e3e8ee; border-left:3px solid var(--vtm); border-radius:10px; padding:14px; display:grid; gap:6px; }
.v2 .a2-card h3 { margin:0; font-size:17px; } .v2 .a2-card p { margin:0; font-size:13px; color:#51606f; }
.v2 .a2-no { font-size:12.5px; color:#51606f; font-weight:600; }
.v2 .a2-tag, .v2 .a2-badge { justify-self:start; font-size:12px; font-weight:600; padding:3px 8px; border-radius:6px; background:#e7f4ee; color:#1d6b4f; }
.v2 .a2-badge { display:inline-block; margin-top:12px; } .v2 .a2-badge.draft { background:#fff3dc; color:#8a5a00; }
.v2 .a2-list .emood, .v2 .a2-list details.acc { display:none; }
.v2 .a2-list .ecard[aria-current="true"] { box-shadow:inset 3px 0 0 var(--vtm); }
.v2 .a2-form .toprow { display:none; }
@media (max-width:1440px){ .v2 .a2 { grid-template-columns:280px minmax(0,1fr); } .v2 .a2-prev { grid-column:2; position:static; } }"""
R = [
 ("V2.settings = v2Adapt(Settings);", FN),
 ("V2.ascen    = v2Adapt(Editor);   /* X93-C1 · тимчасово · живе доки: порт A2 */",
  "V2.ascen    = v2Adapt(A2Scen);   /* X97-C1 · A2 · В-83 знято для ascen */"),
 ("      const card = el('div',{class:'card ecard'},[",
  "      const card = el('div',{class:'card ecard','aria-current':(S.screen==='ascen'&&String(S.escen)===id)?'true':null},["),
 ("text:'Правити', onclick:()=>{ S.escen=id; S.screen='escen'; render(); }}),",
  "text:'Правити', onclick:()=>{ S.escen=id; S.screen=(S.screen==='ascen'?'ascen':'escen'); render(); }}),"),
 (".v2 .system-message small.sys-hint { color:#34465c; }   /* X94-C3 · підказка дії темніша за лічильник */", CSS),
]
if MARK in s:
    print('  = уже застосовано (маркер-вузол A2Scen)')
else:
    for a, b in R:
        n = s.count(a)
        if n != 1: sys.exit(f'  ✗ якір знайдено {n} раз(и): {a[:60]}…')
        s = s.replace(a, b)
    print(f'  ✓ застосовано {len(R)} правок')
open(dst, 'w', encoding='utf-8').write(s)
print('вихід:', dst, '· md5', hashlib.md5(s.encode()).hexdigest())
