/* смоук кроку В — читає ВИХІД, не перераховує (1.15, пастка 4) */
const fs=require('fs'); let ok=0,bad=0;
const A=(c,m)=>{c?(ok++,console.log('✓ '+m)):(bad++,console.log('✗ '+m))};
const h=fs.readFileSync(process.argv[2]||'ae_out/index.html','utf8');
const inj=process.argv.includes('--inject');
let src=h; if(inj) src=src.replace("headers['x-ae-code'] = encodeURIComponent(NET.get())","void 0");

A(/headers\['x-ae-code'\] = encodeURIComponent/.test(src),'кодове слово йде заголовком, %-кодованим');
A(/localStorage\.getItem\('ae_net_code'\)/.test(src),'кодове слово живе в localStorage');
A(!/endpoint\.startsWith\('\/'\)/.test(src),'евристика startsWith знята');
A(/!S\.cfg\.model\.workerReady/.test(src),'стан читається з оголошення workerReady');
A(/r\.headers\.get\('x-ae-model'\)/.test(src),'модель читається з заголовка відповіді');
A(/Кодове слово мережі не підходить/.test(src),'401 без ключа більше не бреше про Groq');
A(!/needCode/.test(src),'ворота не вимагають кодового слова');
A(/r\.status===503/.test(src),'503 з воркера показується текстом воркера');

// перевірка в другий бік: у прямому режимі заголовок кодового слова НЕ шлеться
A(/if\(key\) headers\['Authorization'\][\s\S]{0,400}else if\(NET\.get\(\)\)/.test(src),
  'ключ і кодове слово взаємовиключні');
A(/decodeURIComponent/.test(require('fs').readFileSync('worker/ae-proxy.js','utf8')),
  'воркер декодує кодове слово');
A(/if \(env\.AE_CODE\) \{/.test(require('fs').readFileSync('worker/ae-proxy.js','utf8')),
  'без AE_CODE перевірки немає — кодове слово необовʼязкове');

console.log(`\n✓${ok} · ✗${bad}`+(inj?' (inject)':''));
process.exit(bad?1:0);
