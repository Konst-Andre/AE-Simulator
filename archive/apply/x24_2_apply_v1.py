# x24_2_apply_v1.py · Х24.2 «Summary() непідключений» (S48; план S45, дельта S48)
# живе доки: фінальний пуш (В-31); у рецепті дерева — після x25_2a_apply_v1.py
# P1: символ i-check у спрайт (байт-у-байт з mockup_X21_v1.html).
# P2: function Summary() у блоці v2 після `V2.game = Talk;` — V2.result НЕ ставиться (П12; підключення — Х24.3).
# Арифметика й тексти станів — старого Result дослівно; розбір — раз на зміну в S.shift.debrief.
# Стани: «було» → застосувати · «стало» → exit 0 без змін · інакше — падіння до запису.
import os, sys
CHECK = '<symbol id="i-check" viewBox="0 0 24 24"><path d="m5 12 4 4L19 6"/></symbol>'
SPR_ANCHOR = '</symbol></svg>'          # кінець v2-sprite (рівно раз)
JS_ANCHOR = 'V2.game = Talk;\n'
SUMMARY = r'''
/* ── Х24.2 · E3 «Підсумок зміни» — Summary(), НЕ підключено (П12; V2.result ставить Х24.3) ──
   DOM — renderSummary макета (П28). Арифметика — старого Result дослівно: got/pot/pct/slips/retries,
   «не міняти» — поза відсотком. Розбір — РАЗ на зміну в S.shift.debrief (старий Result кликав
   debrief на кожен рендер — повторний платний запит); пізня відповідь чужої зміни відкидається.
   Повторні спроби — форма макета (inline-стиль, кольори — токени). Промах: b — назва · small — причина · em — тип замовлення (номер знято, Х25.2а). Дія .slip — Х24.4. */
function Summary(){
  const sh = S.shift, rows = sh.rows, scored = rows.filter(r=>!r.sc.noSale);
  const got = scored.reduce((a,r)=>a+r.delta,0);
  const pot = scored.reduce((a,r)=>a+r.pot,0)||1;
  const pct = Math.max(0,Math.min(100,Math.round(got/pot*100)));
  const slips = rows.filter(r=>r.delta<0||(r.sc.noSale&&r.delta>0));
  const retries = rows.reduce((a,r)=>a+((r.tries||1)-1),0);
  const kind = sc => sc.noSale ? 'Не міняти' : sc.trap ? 'Пастка' : sc.grp;
  const why = r => r.sc.noSale && r.delta>0 ? 'продаж там, де «не міняти»' : 'стало гірше: −' + uah(-r.delta) + ' ₴';
  const toE1 = () => { S.shift = null; S.screen = 'picker'; render(); };
  if(!MOCK && !sh.debrief){
    sh.debrief = {st:'wait'};
    engineLive.debrief(rows).then(d => { if(S.shift !== sh) return;
      sh.debrief = {st:'ok', d}; sh.curatorNote = d.curator; if(S.screen === 'result') render(); })
    .catch(e => { if(S.shift !== sh) return;
      sh.debrief = {st:'err', msg:e.message}; if(S.screen === 'result') render(); });
  }
  const metric = (cls, label, value, bar) => el('article', {class:'metric' + (cls ? ' ' + cls : '')},
    [el('small', {text:label}), el('strong', {text:value}),
     bar == null ? null : el('div', {class:'metric-bar'}, [el('i', {style:'width:' + bar + '%'})])]);
  const item = (ic, head, text) => el('div', {class:'review-item'}, [icon(ic), el('div', {}, [el('strong', {text:head}), el('span', {text})])]);
  const db = sh.debrief;
  const review = MOCK ? [el('p', {class:'coach-overall', text:'Заглушка: у робочому режимі тут зʼявиться розбір від наставника.'})]
    : !db || db.st === 'wait' ? [el('p', {class:'coach-overall', text:'Наставник читає вашу зміну…'})]
    : db.st === 'err' ? [el('p', {class:'coach-overall', text:'Розбір не вдався: ' + db.msg + ' Результат зміни збережено — його видно вище.'})]
    : [el('div', {class:'review-grid'}, [el('p', {class:'coach-overall', text:db.d.overall}),
        el('div', {class:'review-list'}, [...(db.d.mistakes||[]).map(t=>item('i-info', 'Повторюється', t)),
                                          ...(db.d.strengths||[]).map(t=>item('i-check', 'Виходить стабільно', t))])]),
       el('div', {class:'review-list', style:'margin-top:15px'}, (db.d.rules||[]).map(t=>item('i-check', 'Наступного разу', t)))];
  return el('div', {class:'page summary-wrap'}, [
    el('header', {class:'page-title'}, [
      el('div', {}, [el('h1', {text:'Підсумок зміни'}),
        el('p', {text:'Завершено розмов: ' + rows.length + '. Ось що повторюється у вашій практиці.'})]),
      el('button', {type:'button', class:'secondary', onclick:toE1}, ['До тренувань'])]),
    el('div', {id:'summary'}, [
      el('div', {class:'summary-grid'}, [
        metric('accent', 'Виконано від орієнтиру', pct + '%', pct),
        metric('positive', 'Додано за зміну', (got>0 ? '+' : '') + uah(got) + ' ₴'),
        metric('', 'Орієнтир зміни', uah(pot) + ' ₴'),
        metric('', 'Завершено розмов', String(rows.length))]),
      el('section', {class:'summary-section'}, [
        el('h2', {}, [icon('i-info'), ' На що звернути увагу']),
        el('p', {text:'Промахи — це розмови, де результат став гіршим або де пропозиція була недоречною.'}),
        slips.length ? el('div', {class:'slips'}, slips.map((r,i) => el('button', {type:'button', class:'slip', 'data-slip':String(r.sc.id)}, [
            el('span', {text:String(i+1)}), el('div', {}, [el('b', {text:r.sc.title}), el('small', {text:why(r)}), el('em', {text:kind(r.sc)})])])))
          : el('p', {text:'Промахів у цій зміні немає'})]),
      el('section', {class:'summary-section'}, [el('h2', {}, [icon('i-target'), ' Розбір наставника']), ...review]),
      el('div', {class:'final-actions'}, [
        retries ? el('span', {style:'margin-right:auto;align-self:center;color:var(--anc-gray);font-size:13px'}, ['Повторні спроби: ', el('b', {style:'color:var(--anc-text)', text:String(retries)})]) : null,
        el('button', {type:'button', class:'secondary', onclick:toE1}, ['До тренувань'])])])]);
}
/* ── /Х24.2 ── */
'''
def main(root):
    f=os.path.join(root,'index.html'); h=open(f,encoding='utf-8').read()
    has_sum=h.count('function Summary()'); has_chk=h.count('id="i-check"')
    if has_sum==1 and has_chk==1:
        assert h.count(SUMMARY)==1 and h.count(CHECK)==1, 'Summary / i-check є, але не ті (руками правили?)'
        assert 'V2.result =' not in h or 'V2.result = Summary' in h
        print('x24_2: вже застосовано, без змін · символ 0 · Summary 0'); return
    assert has_sum==0 and has_chk==0, 'змішаний стан: Summary %d · i-check %d' % (has_sum,has_chk)
    assert h.count(SPR_ANCHOR)==1 and h.count(JS_ANCHOR)==1, 'якір не рівно раз'
    assert 'V2.result =' not in h, 'V2.result уже підключено — база не та'
    h=h.replace(SPR_ANCHOR, '</symbol>'+CHECK+'</svg>',1).replace(JS_ANCHOR, JS_ANCHOR+SUMMARY,1)
    assert h.count(CHECK)==1 and h.count('function Summary()')==1 and 'V2.result =' not in h, 'гард після вставки'
    open(f,'w',encoding='utf-8').write(h)
    print('x24_2: застосовано · символ i-check +1 · Summary +1 (не підключено)')
if __name__=='__main__': main(sys.argv[1] if len(sys.argv)>1 else '.')
