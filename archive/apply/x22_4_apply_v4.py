# x22_4_apply_v4.py — наступник v3 у рецепті дерева (S44 §5): лише config.json і памʼятка Олі.
# живе доки: фінальний пуш (В-31)
# Чому не v3: v3 вирізає символ i-arrow («більше ніхто не кличе», шапка v3:6) і перевставляє низ панелі —
#   E2 v2 (Х23) кличе i-arrow і змінив низ панелі. index.html тут — робоча версія AE_WORK, що вже несе
#   Х22.4б і Х23: цей скрипт її НЕ пише, лише перевіряє, що вона та.
# запуск: python3 x22_4_apply_v4.py AE      · повтор — без змін
import os, re, sys, json
d = sys.argv[1] if len(sys.argv) > 1 else 'AE'
h = open(os.path.join(d, 'index.html'), encoding='utf-8').read()
assert '/* ── Х23.2 · E2 Розмова · JS' in h and h.count('const DOOR = ') == 1 and h.count('<symbol id="i-arrow"') == 1, \
    'index.html — не робоча версія з Х22.4б і Х23 (для старої бази — x22_4_apply_v3.py)'
assert 'curatorCode' not in h.replace('curatorCode знято', ''), 'curatorCode лишився в коді'
cp = os.path.join(d, 'config.json'); c = open(cp, encoding='utf-8').read()
c = re.sub(r'\n  "curatorCode": "[^"]*",', '', c); json.loads(c); open(cp, 'w', encoding='utf-8').write(c)
assert 'curatorCode' not in c
op = os.path.join(d, 'ДЛЯ_ОЛІ', 'ПОЧНИ_ЗВІДСИ.md'); o = open(op, encoding='utf-8').read()
o = o.replace('скільки замовлень у зміні, код куратора, правило', 'скільки замовлень у зміні, правило'); open(op, 'w', encoding='utf-8').write(o)
assert 'код куратора' not in o
print('Х22.4 (v4: config + памʼятка) застосовано:', d)
