/* AE-Simulator · смоук крок 1 — прогін застосунку в jsdom без браузера */
const fs=require('fs'), path=require('path');
const {JSDOM}=require('jsdom');
const BASE='/mnt/user-data/outputs/AE';
const INJECT = process.argv.includes('--inject');
let ok=0,bad=0;
const T=(n,c)=>{ c?(ok++,console.log('  ✓ '+n)):(bad++,console.log('  ✗ '+n)); };

const files={'config.json':'config.json','data/catalog.json':'data/catalog.json',
  'data/scenarios.json':'data/scenarios.json','prompts/client.md':'prompts/client.md',
  'prompts/client.parts.md':'prompts/client.parts.md','prompts/debrief.md':'prompts/debrief.md'};
let html=fs.readFileSync(path.join(BASE,'index.html'),'utf8');
if(INJECT) html=html.replace('const bonusOf = cs => cs.reduce((s,c)=>s+(S.ALL[c]?S.ALL[c].b:0),0);',
                             'const bonusOf = cs => 0;');   // ламаємо підрахунок

const dom=new JSDOM(html,{runScripts:'dangerously',url:'https://x.test/?mock=1',
  beforeParse(w){
    w.fetch=(u)=>{ const raw=fs.readFileSync(path.join(BASE,files[u]||u),'utf8');
      return Promise.resolve({json:()=>Promise.resolve(JSON.parse(raw)),
                              text:()=>Promise.resolve(raw)}); };
    w.scrollTo=()=>{};
    w.HTMLElement.prototype.scrollIntoView=()=>{};
  }});
const w=dom.window;

(async()=>{
  await new Promise(r=>setTimeout(r,300));
  const d=w.document, S=w.S;
  console.log('\n— завантаження —');
  T('config прочитано', !!S.cfg && S.cfg.shiftSize===5);
  T('181 товар в індексі', Object.keys(S.ALL).length===181);
  T('43 сценарії', S.SCEN.length===43);
  T('23 категорії мають label', Object.keys(S.LABEL).length===23 && S.LABEL.throat==='Горло');
  T('стартовий екран — Gate', S.screen==='gate' && /представтесь/.test(d.body.textContent));

  console.log('\n— вхід —');
  const inp=d.querySelectorAll('.field input');
  inp[0].value='Оля Тест'; inp[0].dispatchEvent(new w.Event('input'));
  inp[1].value='67'; inp[1].dispatchEvent(new w.Event('input'));
  [...d.querySelectorAll('button')].find(b=>b.textContent==='Далі').click();
  T('перейшли до списку', S.screen==='picker');
  T('імʼя збережено', JSON.parse(w.localStorage.getItem('ae_me')).name==='Оля Тест');
  T('карток = 43', d.querySelectorAll('.card').length===43);
  T('вкладки груп є', d.querySelectorAll('.tabs button').length===7);

  console.log('\n— арифметика —');
  const sc=S.SCEN.find(s=>s.id===1);
  const base=sc.order.reduce((a,c)=>a+S.ALL[c].b,0);
  const ideal=sc.bv.reduce((a,c)=>a+S.ALL[c].b,0);
  T('приріст сценарію #1 > 0', Math.round(ideal-base)>0);
  let allPos=true;
  for(const s of S.SCEN){ if(s.noSale||!s.bv||!s.bv.length)continue;
    const b=s.order.reduce((a,c)=>a+S.ALL[c].b,0), i=s.bv.reduce((a,c)=>a+S.ALL[c].b,0);
    if(i-b<=0)allPos=false; }
  T('усі 43 сценарії мають додатний орієнтир', allPos);

  console.log('\n— розмова —');
  // беремо сценарій із НЕнульовим бонусом замовлення: у 9 із 43 клієнт
  // замовив оригінал (бонус 0) — на такому підрахунок не перевіриш
  const iCard=S.SCEN.findIndex(x=>x.order.reduce((a,c)=>a+S.ALL[c].b,0)>0);
  d.querySelectorAll('.card')[iCard].click();
  T('екран гри', S.screen==='game');
  T('чек стартує з замовлення', S.cart.length===S.sc.order.length);
  // ключове: суму читаємо ЗІ СТРІЧКИ, тобто з коду застосунку, а не рахуємо самі
  const tapeTxt=d.querySelector('.tape').textContent;
  const expBase=S.sc.order.reduce((a,c)=>a+S.ALL[c].b,0);
  const shown=(tapeTxt.match(/Було в замовленні([\d\s,]+)/)||[])[1];
  T('стрічка показує правильну суму замовлення ('+expBase.toFixed(2).replace('.',',')+')',
    !!shown && shown.trim()===expBase.toFixed(2).replace('.',','));
  T('сума замовлення не нульова', !!shown && parseFloat(shown.replace(',','.'))>0);
  const ta=d.querySelector('.say textarea');
  const say=async t=>{ ta.value=t; ta.dispatchEvent(new w.Event('input'));
    [...d.querySelectorAll('.btn')].find(b=>b.textContent==='Сказати').click();
    await new Promise(r=>setTimeout(r,340)); };
  await say('Добрий день, зараз віддам.');
  T('репліка потрапила в лог', /Добрий день, зараз віддам/.test(d.querySelector('.log').textContent));
  T('клієнт відповів', S.history.length===2 && S.history[1].role==='assistant');

  console.log('\n— панель перевірки рахує чек —');
  const before=d.querySelector('.tape').textContent;
  const box=d.querySelector('.mock input[type=checkbox]:not(:checked)');
  box.checked=true; box.dispatchEvent(new w.Event('change'));
  const after=d.querySelector('.tape').textContent;
  T('чек перерахувався після додавання позиції', before!==after);
  T('стрічка показує приріст', /Приріст розмови/.test(after));

  console.log('\n— завершення —');
  for(let i=0;i<3;i++) await say('репліка '+i);
  T('розмова завершилась після 4 реплік', S.ended===true);
  T('розбір зʼявився', S.feedback.length>20);
  T('кнопка виходу відкрилась', !d.querySelector('.hide')||!/hide/.test(
      [...d.querySelectorAll('.btn')].find(b=>/до списку|Наступне/i.test(b.textContent))?.className||'hide'));

  console.log('\n— зміна на 5 замовлень —');
  S.screen='picker'; w.render();
  [...d.querySelectorAll('.btn')].find(b=>/Почати зміну/.test(b.textContent)).click();
  T('черга зміни зібрана з 5', S.shift.queue.length===5);
  T('усі 5 різні', new Set(S.shift.queue.map(s=>s.id)).size===5);
  T('усі 5 — інтернет-замовлення', S.shift.queue.every(s=>!!s.no));
  const q=S.shift.queue;
  T('у зміні є пастка або noSale', q.some(s=>s.trap||s.noSale));
  T('у зміні є багатопозиційне', q.some(s=>s.order.length>1));

  console.log('\n'+(bad?'✗':'✓')+' підсумок: ✓'+ok+' · ✗'+bad+(INJECT?'  [inject-режим: очікуємо ✗]':''));
  process.exit(bad?1:0);
})();
