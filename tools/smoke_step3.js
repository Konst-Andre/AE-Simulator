/* смоук кроку В — читає ВИХІД, не перераховує (1.15, пастка 4) */
const fs=require('fs'); let ok=0,bad=0;
const A=(c,m)=>{c?(ok++,console.log('✓ '+m)):(bad++,console.log('✗ '+m))};
const h=fs.readFileSync(process.argv[2]||'ae_out/index.html','utf8');
const inj=process.argv.includes('--inject');
let src=h; if(inj) src=src.replace("headers['x-ae-code'] = NET.get()","void 0");

A(/else if\(NET\.get\(\)\) headers\['x-ae-code'\]/.test(src),'кодове слово йде заголовком');
A(/localStorage\.getItem\('ae_net_code'\)/.test(src),'кодове слово живе в localStorage');
A(!/endpoint\.startsWith\('\/'\)/.test(src),'евристика startsWith знята');
A(/!S\.cfg\.model\.workerReady/.test(src),'стан читається з оголошення workerReady');
A(/r\.headers\.get\('x-ae-model'\)/.test(src),'модель читається з заголовка відповіді');
A(/Кодове слово мережі не підходить/.test(src),'401 без ключа більше не бреше про Groq');
A(/needCode && !c\.trim\(\)/.test(src),'ворота не пускають без кодового слова');
A(/r\.status===503/.test(src),'503 з воркера показується текстом воркера');

// перевірка в другий бік: у прямому режимі заголовок кодового слова НЕ шлеться
A(/if\(key\) headers\['Authorization'\][\s\S]{0,80}else if\(NET\.get\(\)\)/.test(src),
  'ключ і кодове слово взаємовиключні');

console.log(`\n✓${ok} · ✗${bad}`+(inj?' (inject)':''));
process.exit(bad?1:0);
