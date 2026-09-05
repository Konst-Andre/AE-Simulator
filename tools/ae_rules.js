/* AE-Simulator · ПРАВИЛА цілісності даних — єдине тіло на всіх споживачів
   живе доки: catalog.json + scenarios.json лишаються джерелом даних тренажера

   Тут немає fs, console, process і нічого з Node: файл мусить читатись
   однаково з командного рядка, з браузера і (крок «в») з воркера. Друк,
   шляхи і код виходу живуть в обгортці tools/ae_validate.js.

   ⚠ ЄДИНА КОПІЯ. Правило, вписане повз цей файл, розходиться з рештою
   мовчки: гейт на push, браузерна перевірка і редактор почнуть казати
   різне про той самий файл. Сторож на це стоїть у tools/smoke_step3.js.

   validate(catalogRaw, scenariosRaw, charactersRaw, configRaw)
     → {out:[{lvl:'ok'|'warn'|'err', msg}], ok, warn, err}
   Два останні — НОСІЇ закритих переліків (характери · щаблі). Копій цих
   переліків тут немає і бути не може (12.11-а): носій приходить аргументом,
   не прийшов — перевірка каже про це ⚠ вголос.

   ⚠ Повідомлення складаються в ОДИН масив у порядку виникнення, а не в три
   за рівнем. Оригінал друкував їх у момент спрацювання, і ✓/⚠/✗ у виводі
   перемішані за ходом коду; три масиви дали б ті самі числа при іншому
   тексті — тобто зелений гейт на зміненому виводі (1.15, пастка 4). */

function validate(catalogRaw, scenariosRaw, charactersRaw, configRaw){
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

  const REQ=['id','grp','title','cats','main','order','open','who','character','mood','mode'];
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

  // --- характер: значення мусить мати запис у носії
  /* Списку девʼяти тут НЕМАЄ навмисно. Єдиний його дім — prompts/characters.md;
     копія в коді розійшлася б із носієм рівно тоді, коли Оля додасть характер.
     Носій приходить аргументом. Не прийшов — кажемо це вголос: мовчазний
     пропуск виглядав би як пройдена перевірка (12.12-г). */
  /* Перелік назв піднятий сюди: його читає і розділ mood нижче. Другого
     розбору носія не робимо — два парсери того самого файлу розійшлись би. */
  let charNames=null;
  if(typeof charactersRaw === 'string' && charactersRaw.trim()){
    const recs = [...('\n'+charactersRaw.replace(/<!--[\s\S]*?-->/g,'')).matchAll(/\n## (.+?)\n([\s\S]*?)(?=\n## |$)/g)];
    const hasClient = m=>/### для клієнта\s*\S/.test(m[2]);
    const hasRisk   = m=>/### ризик\s*\S/.test(m[2]);
    const known = new Set(recs.filter(hasClient).map(m=>m[1].trim()));
    charNames = [...known];
    known.size ? O('характерів у носії: '+known.size) : E('носій характерів прочитано, але жодного запису з блоком «для клієнта»');
    const orphan=SCEN.filter(s=>s.character && !known.has(s.character));
    orphan.length
      ? orphan.forEach(s=>E('#'+s.id+' — характеру «'+s.character+'» немає в носії'))
      : O('усі character мають запис у носії');
    const idle=[...known].filter(k=>!SCEN.some(s=>s.character===k));
    idle.length && W('характери без жодного сценарію: '+idle.join(', '));
    /* Другий блок запису. «### для клієнта» їде в промпт клієнта,
       «### ризик» — у промпт судді. Запис без другого блоку проходить
       усі перевірки вище і дає судді порожній приціл: дефект того самого
       класу, що характер без опису, тільки з іншого боку носія. */
    const noRisk = recs.filter(m=>hasClient(m) && !hasRisk(m)).map(m=>m[1].trim());
    noRisk.length
      ? noRisk.forEach(n=>E('запис «'+n+'» не має блоку «### ризик» — промпт судді лишиться без прицілу'))
      : O('усі записи носія мають обидва блоки');
  } else {
    W('носій характерів не переданий — значення character не звірені');
  }

  /* --- рядок mood: обставини цього дня, а не характер і не щабель
     Правило повним текстом — AE_Simulator_MOOD_RULE_v1.md §1; людський дім
     для Олі — ДЛЯ_ОЛІ/ПОЧНИ_ЗВІДСИ.md (крок Док-Олі, ще не написаний).

     ⚠ МЕЖА ЦІЄЇ ПЕРЕВІРКИ, названа вголос (12.12-и). Правило сформульоване
     словами («рядок не називає характер»), а перевірка тут ЛЕКСИЧНА: вона
     шукає слова. Рядок, що описує характер інакшими словами — «постійний
     клієнт, звик до свого списку, змін не любить» — проходить зеленим,
     не вживши жодного забороненого кореня. На заміряному прогоні старих
     43 рядків детектор почервонив 19 із них; решту ловить людина по
     таблиці розкладки (MOOD_RULE_v1 §4), не ця функція.
     Зелений тут означає «жодної ознаки не знайдено», а не «правило
     виконане». */
  const MOOD_LIMIT=90;
  /* Корінь назви = слово без двох останніх літер: рід і відмінок у
     прикметнику сидять саме там, а носій тримає одну форму на всі.
     ⚠ Прикладів із назвами характерів і щаблів у цих коментарях НЕМАЄ
     навмисно: смоук грепає тіло файлу на них, і приклад у коментарі
     почервонив би перевірку 12.11-а справедливо — літери в файлі є.
     Нижня межа пʼять літер — нижче корінь починає
     траплятись усередині чужих слів («рах» сидить у «страх»), тому слова
     назв, коротші за пʼять літер, у перевірку не входять узагалі.
     Це друга названа дірка, а не недогляд. */
  const rootsOf = phrase => (String(phrase).toLowerCase().match(/[а-яїієґёa-zʼ']+/g)||[])
    .filter(w=>w.length>=5).map(w=>w.slice(0, Math.max(5, w.length-2)));
  const mWords = t => new Set((String(t).toLowerCase().match(/[а-яїієґёa-zʼ']{5,}/g)||[]));
  const moodOf = s => typeof s.mood==='string' ? s.mood : '';
  let moodBad=0;
  const ME=m=>{E(m);moodBad++};

  for(const s of SCEN){
    const m=moodOf(s), tag='#'+s.id+' mood';
    if(!m) continue;                       // порожнє поле вже спіймав REQ
    if(m.length>MOOD_LIMIT) ME(tag+' — довжина '+m.length+' > '+MOOD_LIMIT);
    if(/[«»"„“]/.test(m))   ME(tag+' — пряма мова в лапках (дім — open)');
    if(/\d/.test(m))        ME(tag+' — цифра в рядку');
    if(/₴|орієнтир|приріст/i.test(m)) ME(tag+' — межа знань: цього слова клієнт не знає');
    for(const fld of ['open','who','mode']){
      const wb=mWords(s[fld]||'');
      const inter=[...mWords(m)].filter(w=>wb.has(w)).sort();
      if(inter.length) ME(tag+' — повторює '+fld+': '+inter.join(', '));
    }
  }

  if(charNames && charNames.length){
    for(const s of SCEN){
      const m=moodOf(s).toLowerCase(); if(!m) continue;
      for(const n of charNames){
        const nl=n.toLowerCase();
        if(m.includes(nl)){ ME('#'+s.id+' mood — назва характеру «'+n+'» (дім — prompts/characters.md)'); continue; }
        const hit=rootsOf(n).find(r=>m.includes(r));
        if(hit) ME('#'+s.id+' mood — корінь назви характеру «'+hit+'» («'+n+'»)');
      }
    }
    O('mood звірений з переліком характерів ('+charNames.length+')');
  } else {
    W('носія характерів немає — mood не звірений з назвами характерів');
  }

  /* Перелік щаблів має рівно один машинний дім — config.json, схема відповіді
     клієнта. Тут його копії немає з тієї самої причини, що й копії характерів. */
  const cs=configRaw&&configRaw.schemas&&configRaw.schemas.turn&&configRaw.schemas.turn.schema;
  const STEPS = cs&&cs.properties&&cs.properties.step&&cs.properties.step.enum;
  if(STEPS && STEPS.length){
    for(const s of SCEN){
      const m=moodOf(s).toLowerCase(); if(!m) continue;
      for(const st of STEPS){
        const hit=[st.toLowerCase(), ...rootsOf(st)].find(r=>m.includes(r));
        if(hit){ ME('#'+s.id+' mood — назва щабля «'+st+'»: стартовий щабель виводиться з рядка, а не називається в ньому'); break; }
      }
    }
    O('mood звірений з переліком щаблів ('+STEPS.length+')');
  } else {
    W('config не переданий — mood не звірений з назвами щаблів');
  }

  const moodSeen={};
  for(const s of SCEN){
    const k=moodOf(s).toLowerCase().trim(); if(!k) continue;
    if(moodSeen[k]!==undefined) ME('#'+s.id+' mood — дослівний дубль #'+moodSeen[k]);
    else moodSeen[k]=s.id;
  }
  for(let a=0;a<SCEN.length;a++) for(let b=a+1;b<SCEN.length;b++){
    const wb=mWords(moodOf(SCEN[b]));
    const inter=[...mWords(moodOf(SCEN[a]))].filter(w=>wb.has(w)).sort();
    if(inter.length>=2) ME('#'+SCEN[a].id+' ~ #'+SCEN[b].id+' mood — спільних слів '+inter.length+': '+inter.join(', '));
  }
  !moodBad && O('рядки mood за правилом (≤'+MOOD_LIMIT+' символів · без лапок, цифр і межі знань · без назв характеру і щабля · без повтору open/who/mode · без дублів)');

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
