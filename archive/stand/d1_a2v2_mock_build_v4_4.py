#!/usr/bin/env python3
"""d1_a2v2_mock_build_v4_3.py · AE-Simulator · S78 · D1 v4.3 — мокап A2 v2 на реальних даних (усі 43 сценарії повні)
живе доки: вирок D1 v4.3 не перенесено в продукт ходом D2 (після — в архів)
Вхід: корінь репо AE (data/scenarios.json, data/catalog.json, config.json, prompts/characters.md) і шаблон mock_a2v2_tpl_v4_4.html поруч.
Б4 (S77): список характерів — з носія prompts/characters.md (записи «## назва», порядок носія), не зі сценаріїв.
Запуск: python3 d1_a2v2_mock_build_v4_3.py <AE> <вихід.html>
Детермінований: той самий вхід → той самий md5 (П34).
"""
import sys, json, pathlib, hashlib
root = pathlib.Path(sys.argv[1]); dst = pathlib.Path(sys.argv[2])
tpl = (pathlib.Path(__file__).parent / 'mock_a2v2_tpl_v4_4.html').read_text(encoding='utf-8')
S = json.loads((root/'data/scenarios.json').read_text(encoding='utf-8'))
S = S if isinstance(S, list) else S['scenarios']
C = json.loads((root/'data/catalog.json').read_text(encoding='utf-8'))['categories']
CH = [l[3:].strip() for l in (root/'prompts/characters.md').read_text(encoding='utf-8').splitlines() if l.startswith('## ')]
assert CH and len(CH)==len(set(CH)), 'носій характерів порожній або з дублями'
cfg = json.loads((root/'config.json').read_text(encoding='utf-8'))
data = {
  'scenarios': S,
  'cats': {k: {'label': v['label'], 'items': [{'c': i['c'], 'n': i['n'], 'p': i['p'], 'b': i['b'], 'k': i['k']} for i in v['items']]} for k, v in C.items()},
  'chars': CH,
  'rule': cfg.get('rule', 'vtm'),
}
out = tpl.replace('/*DATA*/null', json.dumps(data, ensure_ascii=False, sort_keys=True))
assert out != tpl, 'якір /*DATA*/null не знайдено'
dst.write_text(out, encoding='utf-8')
print('вихід:', dst, '· md5', hashlib.md5(out.encode()).hexdigest(), '·', len(out)//1024, 'КБ')
