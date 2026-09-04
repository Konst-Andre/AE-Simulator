/* AE-Simulator · валідатор цілісності даних — ОБГОРТКА
   живе доки: catalog.json + scenarios.json лишаються джерелом даних тренажера
   запуск: node tools/ae_validate.js   (читає data/catalog.json і data/scenarios.json)

   ⚠ Правил тут НЕМАЄ і бути не може. Вони живуть в tools/ae_rules.js —
   одним тілом на командний рядок, браузерну перевірку і редактор. Правило,
   вписане сюди, розійдеться з ними мовчки. Файл робить рівно три речі:
   читає з диска, друкує, віддає код виходу. */
const fs=require('fs');
const {validate}=require('./ae_rules.js');

const catalog=JSON.parse(fs.readFileSync(process.argv[2]||'data/catalog.json','utf8'));
const scen=JSON.parse(fs.readFileSync(process.argv[3]||'data/scenarios.json','utf8'));
/* Третій файл — носій характерів. Читається так само з диска й так само без
   розбору: що з ним робити, вирішують правила. Немає файла — віддаємо null,
   і правила скажуть про це ⚠ самі. */
const charsPath=process.argv[4]||'prompts/characters.md';
const chars=fs.existsSync(charsPath)?fs.readFileSync(charsPath,'utf8'):null;

const SIGN={ok:'  ✓ ',warn:'  ⚠ ',err:'  ✗ '};
const r=validate(catalog,scen,chars);
for(const m of r.out) console.log(SIGN[m.lvl]+m.msg);

console.log('\n'+(r.err?'✗':'✓')+' підсумок: ✓'+r.ok+' · ⚠'+r.warn+' · ✗'+r.err);
process.exit(r.err?1:0);
