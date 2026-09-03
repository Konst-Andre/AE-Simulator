/* AE-Simulator · ПРАВИЛА цілісності даних — єдине тіло на всіх споживачів
   живе доки: catalog.json + scenarios.json лишаються джерелом даних тренажера

   Тут немає fs, console, process і нічого з Node: файл мусить читатись
   однаково з командного рядка, з браузера і (крок «в») з воркера. Друк,
   шляхи і код виходу живуть в обгортці tools/ae_validate.js.

   ⚠ ЄДИНА КОПІЯ. Правило, вписане повз цей файл, розходиться з рештою
   мовчки: гейт на push, браузерна перевірка і редактор почнуть казати
   різне про той самий файл. Сторож на це стоїть у tools/smoke_step3.js.

   validate(catalogRaw, scenariosRaw) → {out:[{lvl:'ok'|'warn'|'err', msg}], ok, warn, err}

   ⚠ Повідомлення складаються в ОДИН масив у порядку виникнення, а не в три
   за рівнем. Оригінал друкував їх у момент спрацювання, і ✓/⚠/✗ у виводі
   перемішані за ходом коду; три масиви дали б ті самі числа при іншому
   тексті — тобто зелений гейт на зміненому виводі (1.15, пастка 4). */

function validate(catalogRaw, scenariosRaw){
  /* Нормалізація форми файлу — це ПРАВИЛО, не читання: обидві форми
     («{categories:{…}}» і голий обʼєкт, «{scenarios:[…]}» і голий масив)
     приходять однаково і з диска, і з поля вибору файлу в браузері. */
  const CAT = catalogRaw && catalogRaw.categories
    ? Object.fromEntries(Object.entries(catalogRaw.categories).map(([k,v])=>[k,v.items]))
    : catalogRaw;
  const SCEN = (scenariosRaw && scenariosRaw.scenarios) || scenariosRaw;

  const out=[]; let ok=0,warn=0,err=0;
  const E=m=>{out.push({lvl:'err', msg:m}); err++};
  const W=m=>{out.push({lvl:'warn',msg:m}); warn++};
  const O=m=>{out.push({lvl:'ok',  msg:m}); ok++};

  // --- індекс товарів
  const ALL={},dupC=[];
  for(const [cat,arr] of Object.entries(CAT))
    for(const it of arr){ if(ALL[it.c])dupC.push(it.c); ALL[it.c]={...it,cat}; }
  dupC.length?E('дублі кодів товару: '+dupC.join(', ')):O('коди товарів унікальні ('+Object.keys(ALL).length+')');

  // --- поля товару
  const badItem=[];
  for(const [c,it] of Object.entries(ALL)){
    if(typeof it.n!=='string'||!it.n.trim())badItem.push(c+' — немає назви');
    if(typeof it.b!=='number'||!(it.b>=0))badItem.push(c+' — бонус не число');
    if(!['ВТМ','ЗФ','—',undefined,null].includes(it.k)&&typeof it.k!=='string')badItem.push(c+' — мітка k');
  }
  badItem.length?badItem.forEach(E):O('поля товарів цілі (n, b, k)');
  const noPrice=Object.values(ALL).filter(i=>i.p===null).length;
  noPrice&&W('товарів без ціни (p:null): '+noPrice+' — норма, позиція нова');

  // --- сценарії
  const ids=SCEN.map(s=>s.id), dupId=ids.filter((x,i)=>ids.indexOf(x)!==i);
  dupId.length?E('дублі id сценаріїв: '+[...new Set(dupId)].join(', ')):O('id сценаріїв унікальні ('+SCEN.length+')');

  const nums=SCEN.filter(s=>s.no).map(s=>s.no);
  const dupNo=nums.filter((x,i)=>nums.indexOf(x)!==i);
  dupNo.length?W('однакові номери замовлень: '+[...new Set(dupNo)].join(', ')):O('номери замовлень унікальні ('+nums.length+' інтернет-замовлень)');

  const REQ=['id','grp','title','cats','main','order','open','who','mood','mode'];
  let hang=0,badf=0,badcat=0,badmain=0;
  for(const s of SCEN){
    const tag='#'+s.id+' «'+(s.title||'?')+'»';
    for(const f of REQ) if(s[f]===undefined||s[f]===null||s[f]===''){E(tag+' — немає поля '+f);badf++}
    for(const k of (s.cats||[])) if(!CAT[k]){E(tag+' — категорія «'+k+'» не існує');badcat++}
    if(s.main&&!(s.cats||[]).includes(s.main)){E(tag+' — main «'+s.main+'» не у cats');badmain++}
    for(const fld of ['order','bv','bm'])
      for(const c of (s[fld]||[])) if(!ALL[c]){E(tag+' — '+fld+': код «'+c+'» не існує в каталозі');hang++}
    // ідеальна розмова має бути в межах доступного асортименту
    const pool=new Set((s.cats||[]).flatMap(k=>(CAT[k]||[]).map(i=>i.c)));
    for(const fld of ['order','bv','bm'])
      for(const c of (s[fld]||[])) if(ALL[c]&&!pool.has(c))
        W('#'+s.id+' — '+fld+': «'+c+'» поза cats сценарію (модель його не побачить)');
    if(!s.noSale){
      if(!s.bv||!s.bv.length)W(tag+' — немає bv (ідеал під правило ВТМ)');
      if(!s.bm||!s.bm.length)W(tag+' — немає bm (ідеал під правило СТМ)');
    }
  }
  !badf&&O('обовʼязкові поля на місці ('+REQ.join(', ')+')');
  !badcat&&O('усі cats існують у каталозі');
  !badmain&&O('main завжди входить у cats');
  !hang&&O('висячих кодів немає (order · bv · bm)');

  // --- потенціал > 0
  const bonus=cs=>cs.reduce((a,c)=>a+(ALL[c]?ALL[c].b:0),0);
  let zero=[];
  for(const s of SCEN){
    if(s.noSale)continue;
    for(const [r,f] of [['ВТМ','bv'],['СТМ','bm']]){
      if(!s[f]||!s[f].length)continue;
      const p=bonus(s[f])-bonus(s.order||[]);
      if(p<=0)zero.push('#'+s.id+' '+r+': приріст '+p.toFixed(2)+' ₴');
    }
  }
  zero.length?zero.forEach(W):O('ідеал завжди дорожчий за замовлення (приріст > 0)');

  // --- склад зміни: pickShift потребує пулів
  const NET=SCEN.filter(s=>s.no);
  const pools={'пастка/noSale':NET.filter(s=>s.trap||s.noSale),'багатопозиційні':NET.filter(s=>(s.order||[]).length>1),'рецептурні':NET.filter(s=>s.grp==='Рецептурні')};
  for(const [k,v] of Object.entries(pools)) v.length?O('пул «'+k+'»: '+v.length):E('пул «'+k+'» порожній — зміна не збереться');
  NET.length>=5?O('інтернет-замовлень для зміни: '+NET.length+' (треба ≥5)'):E('інтернет-замовлень '+NET.length+', зміна потребує 5');

  return {out, ok, warn, err};
}

/* Два виходи, бо споживачі різні: Node бере require, браузер — тег <script>.
   ⚠ Воркер (крок «в») хоче ESM-import і цим хвостом НЕ закривається. */
if (typeof module !== 'undefined' && module.exports) module.exports = { validate };
if (typeof globalThis !== 'undefined') globalThis.AE_RULES = { validate };
