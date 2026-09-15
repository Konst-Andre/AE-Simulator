#!/usr/bin/env python3
"""x98_a2blocks_apply_v1.py · AE-Simulator · S74 · щабель 2 · крок C1b (блоки й компактний список A2)
живе доки: X98 не заступлено наступним кроком A2 (C2)

Лише для S.screen==='ascen'. Старі ключі `edit`/`escen` (живуть до C2, смоук edit_ui_v1 :490)
отримують той самий плаский порядок полів і ті самі картки з «Правити».
· Форма (ScenCard): фабрики полів створюються в ТОМУ САМОМУ порядку (реєстр codeFields не
  зсувається), міняється тільки компонування: рядок «Назва·Група» + блоки «Клієнт / Товари /
  Рекомендації» (SPEC §A2). «Товари» — чинні catField/codeField, не чипи мокапу (В-88).
  Шапка форми в A2 — #no, як у рядку списку і в прев'ю; id лишається в «Не правиться тут».
· Список (Editor): рядок-кнопка `#no · назва · група ✗/⚠ · бейдж` (мокап X21, паритет бейджа
  з прев'ю, SPEC §A2). Звірка, публікація, фільтри ✗/⚠ — на місці.
· CSS: секція X97-C1; зняття max-width:420 лише всередині .a2-form.

Вхід: AE_WORK_index_X97_v1.html (md5 386394e6b2c7b57254712781f7438f46)
Запуск: python3 x98_a2blocks_apply_v1.py <вхід.html> <вихід.html>
Ідемпотентність: маркер — вузол `const blk = (title, kids)` (П94).
"""
import sys, hashlib
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
MARK = "const blk = (title, kids)"

OLD_START = "  put(root,\n    el('div',{class:'top'},[\n      el('div',{class:'toprow'},[backBtn('до списку',()=>{S.screen='ascen';render()})]),"
OLD_END = "    })()\n  );\n  refresh();\n}"

NEW_FORM = r"""  /* X98-C1b · вузли створюються в чинному порядку (codeFields: order·bv·bm), компонування — окремо. */
  const head = el('div',{class:'top'},[
    el('div',{class:'toprow'},[backBtn('до списку',()=>{S.screen='ascen';render()})]),
    el('h1',{class:'toptitle',text:(S.screen==='ascen'
      ? (rec.no ? '#'+rec.no : 'На місці')
      : '#'+id)+' · '+(rec.title||'без назви')})
  ]);
  const note = el('p',{class:'enote',text:
    'Правки живуть у цій сесії. Публікація — у списку редактора, однією '+
    'кнопкою на всі змінені сценарії: файл пишеться цілком.'});
  const fTitle = textField('title','Назва',false);
  const fGrp   = selField('grp','Група',grps,
    el('p',{class:'ehint',text:'Перелік — з наявних груп. Нову групу цією формою не завести.'}));
  const fChar  = selField('character','Характер',chars,
    el('p',{class:'ehint',text:'Перелік — з носія характерів. Значення поза ним зупиняє старт застосунку.'}));
  const fWho   = textField('who','Хто це (who)',false);
  const fMode  = textField('mode','Режим видачі (mode)',false);
  const fOpen  = textField('open','Перша репліка (open)',true);
  const fGoal  = textField('goal','Мета розмови (goal)',true,
    el('p',{class:'ehint',text:'Поза REQ: правила про це поле нічого не кажуть.'}));
  const fMood  = (()=>{ const f=textField('mood','Настрій дня (mood)',true,moodHint);
    f.querySelector('.flab').append(countEl); return f; })();
  const fCats  = catField();
  const fMain  = field('main','Головна категорія (main)', mainSel,
    el('p',{class:'ehint',text:'Тільки з обраних вище. Значення поза cats '+
      'зупиняє не застосунок, а перевірку: правила дають ✗.'}));
  const fOrder = codeField('order','Замовлення (order)');
  const fBv    = codeField('bv','Ідеал ВТМ (bv)');
  const fBm    = codeField('bm','Ідеал СТМ (bm)');
  const roBox  = (()=>{
      /* Перелік і число — з одного місця. Число, написане рукою, замерзне
         брехнею на кроці, який забере звідси cats і main (S25 §4.3). */
      const roRows = [
        ['id', rec.id],
        ['no (номер замовлення)', rec.no]
      ];
      return el('details',{class:'acc',style:'margin-top:18px'},[
        el('summary',{text:'Не правиться тут ('+plural(roRows.length,'поле','поля','полів')+')'}),
        el('div',{class:'accbody'},[
          el('p',{class:'enote',style:'margin-bottom:8px',text:
            'Два номери. id не правиться ніколи: на нього посилаються самі дані, '+
            'і його зміна це не правка запису, а підміна адреси. no — число, і '+
            'текстове поле дало б тут рядок замість числа; це наступний крок.'}),
          el('div',{class:'ero'}, roRows.map(([l,v])=>ro(l,v)))
        ])
      ]);
    })();

  if(S.screen==='ascen'){
    /* A2 · три блоки SPEC §A2. Мітки trap/noSale — C3, порожнього місця під них немає. */
    const full = n => { n.classList.add('full'); return n; };
    const blk = (title, kids) => el('section',{class:'a2-blk'},[
      el('h2',{text:title}), el('div',{class:'a2-grid'},kids)]);
    put(root, head, note, dirtyBox,
      el('div',{class:'a2-grid a2-idrow'},[fTitle, fGrp]),
      blk('Клієнт',      [fWho, fChar, full(fMood), full(fMode), full(fOpen)]),
      blk('Товари',      [fCats, fMain, full(limitLine), full(fOrder)]),
      blk('Рекомендації',[fBv, fBm, full(fGoal)]),
      verdBox, roBox);
  } else {
    put(root, head, note, dirtyBox,
      fTitle, fGrp, fChar, fWho, fMode, fOpen, fGoal, fMood,
      fCats, fMain, limitLine, fOrder, fBv, fBm, verdBox, roBox);
  }
  refresh();
}"""

OLD_ROW = "      shown++;\n"
NEW_ROW = r"""      shown++;
      /* X98-C1b · A2: компактний рядок мокапу X21 замість картки. Вибір — натиском по рядку:
         під рядком нічого не лежить, двох намірів у зоні немає (на відміну від картки з details). */
      if(S.screen==='ascen'){
        const mk = st.err ? ' · ✗ '+st.err+(st.warn?' · ⚠ '+st.warn:'') : (st.warn ? ' · ⚠ '+st.warn : '');
        listBox.append(el('button',{type:'button',class:'ecard a2-row',
          'aria-current': String(S.escen)===id ? 'true' : null,
          onclick:()=>{ S.escen=id; render(); }},[
          el('span',{class:'a2-rno',text: s.no ? '#'+s.no : 'на місці'}),
          el('span',{class:'a2-rtx'},[
            el('b',{text:s.title||'без назви'}),
            el('small',{},[ el('span',{text:s.grp||'—'}),
              mk ? el('span',{style:'color:'+(st.err?TONE.err:TONE.warn),text:mk}) : null ])
          ]),
          el('span',{class:'a2-badge'+(dr.length?' draft':''),text: dr.length?'чернетка':'опубліковано'})
        ]));
        continue;
      }
"""

OLD_CSS = ".v2 .a2-form .toprow { display:none; }"
NEW_CSS = OLD_CSS + """
/* X98-C1b · A2 компактний список (мокап X21 .scenario-item) */
.v2 .a2-list > p.sub { display:none; }
.v2 .a2-list .elist { display:grid; border:1px solid #e3e8ee; border-radius:12px; overflow:hidden; background:#fff; }
.v2 .a2-row { display:grid; grid-template-columns:auto minmax(0,1fr) auto; align-items:center; gap:11px; width:100%; min-height:56px; margin:0; padding:10px 14px; border:0; border-bottom:1px solid #edf1f5; border-radius:0; background:#fff; color:inherit; font:inherit; text-align:left; cursor:pointer; }
.v2 .a2-row:last-child { border-bottom:0; }
.v2 .a2-row:hover, .v2 .a2-row[aria-current="true"] { background:#f1fcf8; }
.v2 .a2-rno { font-size:12px; font-weight:700; color:#657690; white-space:nowrap; }
.v2 .a2-rtx { min-width:0; }
.v2 .a2-rtx b { display:-webkit-box; -webkit-box-orient:vertical; -webkit-line-clamp:2; overflow:hidden; font-size:13px; line-height:1.3; }   /* 2 рядки: у 300 px із бейджем одна лінія лишала 8–10 літер (замір 1920) */
.v2 .a2-rtx small { display:block; margin-top:3px; font-size:11px; color:#74859b; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.v2 .a2-row .a2-badge { margin:0; padding:4px 7px; font-size:10px; }
/* X98-C1b · A2 форма блоками SPEC §A2 */
.v2 .a2-form { display:grid; gap:12px; }
.v2 .a2-blk { padding:18px; border:1px solid #e3e8ee; border-radius:12px; background:#fff; }
.v2 .a2-blk h2 { margin:0 0 14px; font-size:17px; }
.v2 .a2-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:4px 13px; align-items:start; }
.v2 .a2-grid > .full { grid-column:1 / -1; }
.v2 .a2-form .field input, .v2 .a2-form .field textarea, .v2 .a2-form .field select, .v2 .a2-form .flab, .v2 .a2-form .ehint, .v2 .a2-form .pick, .v2 .a2-form .pickgain, .v2 .a2-form .enote, .v2 .a2-form .everd, .v2 .a2-form .ero, .v2 .a2-form .acc { max-width:none; }"""

if MARK in s:
    print('  = уже застосовано (маркер-вузол blk)')
else:
    a = s.count(OLD_START)
    if a != 1: sys.exit(f'  ✗ якір форми знайдено {a} раз(и)')
    i = s.index(OLD_START); j = s.find(OLD_END, i)
    if j < 0: sys.exit('  ✗ кінець форми не знайдено')
    s = s[:i] + NEW_FORM + s[j+len(OLD_END):]
    for x, y in [(OLD_ROW, NEW_ROW), (OLD_CSS, NEW_CSS)]:
        n = s.count(x)
        if n != 1: sys.exit(f'  ✗ якір знайдено {n} раз(и): {x[:50]}…')
        s = s.replace(x, y)
    print('  ✓ застосовано 3 правки')
open(dst, 'w', encoding='utf-8').write(s)
print('вихід:', dst, '· md5', hashlib.md5(s.encode()).hexdigest())
