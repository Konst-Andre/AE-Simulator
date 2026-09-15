#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x70_preview_build_v1.py — AE-Simulator · АВТОНОМНЕ ПРЕВ'Ю

живе доки: продукт вантажить дані сусідніми файлами

Вхід : AE_WORK_index_X27P5_v1.html + тека AE (config.json, data/, prompts/)
Вихід: AE_WORK_PREVIEW_X27P5_v1.html — один файл, відкривається з file://
       без мережі й без сусідніх файлів.

ЯК. boot() робить вісім fetch() до локальних шляхів. З file:// вони падають,
і продукт чесно каже «дані не завантажились». Прев'ю не чіпає boot():
перед ним ставиться шар, який перехоплює РІВНО ці вісім шляхів і віддає
вшитий вміст. Усе решта — мережа, проксі моделі — йде як було.

Дані лежать base64, не як сирий текст: інакше будь-яка лапка чи </script>
у каталозі рвала б документ. Декодування через TextDecoder — кирилиця цілі́.

⚠ Прев'ю — НЕ білд для передачі. Продукт лишається AE_WORK_index_*.
  В-31 чинний: нікуди не пушимо.
"""
import base64, hashlib, json, pathlib, sys

SRC  = pathlib.Path('AE_WORK_index_X27P5_v1.html')
DST  = pathlib.Path('AE_WORK_PREVIEW_X27P5_v1.html')
ROOT = pathlib.Path('/home/claude/AE')

FILES = ['config.json', 'data/catalog.json', 'data/scenarios.json',
         'prompts/client.md', 'prompts/client.parts.md', 'prompts/characters.md',
         'prompts/debrief.md', 'prompts/judge.md']

MARK = 'AE-PREVIEW-SHIM'


def main() -> int:
    if not SRC.exists():
        print(f'✗ немає входу: {SRC}'); return 1
    t = SRC.read_text(encoding='utf-8')
    if MARK in t:
        print('  шар прев\'ю — вже було'); DST.write_text(t, encoding='utf-8'); return 0

    blob = {}
    for f in FILES:
        p = ROOT / f
        if not p.exists():
            print(f'  ✗ немає даних: {p}'); return 2
        blob[f] = base64.b64encode(p.read_bytes()).decode('ascii')
        print(f'  вшито {f} · {p.stat().st_size} б')

    shim = """<script id="AE-PREVIEW-SHIM">
/* ── АВТОНОМНЕ ПРЕВ'Ю ────────────────────────────────────────────────────
   Шар над fetch: вісім локальних шляхів boot() віддаються з вшитих даних,
   решта запитів іде в справжній fetch без змін. Ставиться ДО коду продукту,
   тому boot() навіть не знає, що читає не з диска.
   Це прев'ю для перегляду верстки, не білд для передачі (В-31). */
(function(){
  var DATA = __BLOB__;
  var dec = new TextDecoder('utf-8');
  function bytes(b64){
    var bin = atob(b64), a = new Uint8Array(bin.length);
    for(var i=0;i<bin.length;i++) a[i] = bin.charCodeAt(i);
    return a;
  }
  var real = window.fetch ? window.fetch.bind(window) : null;
  window.fetch = function(url, opt){
    var key = String(url).replace(/^\\.\\//,'').split('?')[0];
    if(Object.prototype.hasOwnProperty.call(DATA, key)){
      var txt = dec.decode(bytes(DATA[key]));
      return Promise.resolve({
        ok:true, status:200, url:String(url),
        text:function(){ return Promise.resolve(txt); },
        json:function(){ return Promise.resolve(JSON.parse(txt)); }
      });
    }
    if(!real) return Promise.reject(new Error('fetch недоступний: ' + key));
    return real(url, opt);
  };
})();
</script>
"""
    shim = shim.replace('__BLOB__', json.dumps(blob, ensure_ascii=True))

    anchor = '<script>'
    i = t.find(anchor)
    if i < 0:
        print('  ✗ не знайдено, куди ставити шар'); return 3
    t = t[:i] + shim + t[i:]

    out = t.encode('utf-8')
    DST.write_bytes(out)
    print(f'вихід: {DST} · md5 {hashlib.md5(out).hexdigest()} · {len(out)//1024} КБ')
    return 0


if __name__ == '__main__':
    sys.exit(main())
