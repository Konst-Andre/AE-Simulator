#!/usr/bin/env python3
# x25_apply_v2.py — Х25.2 «ЛОГО» + В-45 «канва» поверх Х25.1 (x25_apply_v1).
# живе доки: фінальний пуш (В-31). У рецепті дерева — ОСТАННІМ, ЗАМІСТЬ x25_apply_v1 (v1 на файлі після v2 падає своїм гардом).
#   Регенерація з d47f7650: рецепт S45 → x25_apply_v1 → x25_apply_v2. v1 лишається в Project лише для цього.
# В-45 (вирок оператора, compare канви, варіант В): сторінка = жовтий 5 % #FFFEF6; плашки всередині карток = жовтий 10 % #FFFCEC
#   (нова роль plate — на 5 % плашка на білій картці зникала: #FFFEF6 проти #FFFFFF).
# Х25.2: плитка бренду = синє лого АНЦ на жовтому колі (брендбук с. 6 · фавікон); лого 75 % діаметра = безпечна зона ≥12.5 % (с. 8;
#   замір вектора: коло 331.5 од. на лого 250.6 → 75.6 %, верхня межа, бо враховано контрольні точки кривих).
# Стани входу: після v1 → переносить · після v2 → «вже застосовано», exit 0 · без x25 → падіння «спершу x25_apply_v1».
# Запуск: python3 x25_apply_v2.py <тека AE>
import re, sys, os
TOK = {  # ім'я → HEX. Брендбук: yellow · blue · тінти прозорістю · white. Сайт: text · gray · border · positive.
 'yellow':'#FFE241','yellow-50':'#FFF0A0','yellow-25':'#FFF8D0','blue':'#008ECC','blue-25':'#BFE3F2',
 'canvas':'#FFFEF6','plate':'#FFFCEC','text':'#1C1E24','text-2':'#4F4F4F','gray':'#6E6E77','gray-light':'#9B9CA1',
 'border':'#E7E7E7','positive':'#1E815D'}
# з x25_apply_v1 — дозволені літерали (гард нижче той самий)
LIT_OUT = {'#1c1e2410','#1c1e2425','#1c1e2428','#008ecc1a'}
KEEP = {'#ffffff','#bd2f45','#9d2542','#a51f37','#ab2944','#bd2f4514','#f0dce1','#ffe0e6','#fff0f3','#fff5f6','#fffafa'}
PAGE  = ['.v2', '.v2 .sidebar', '.v2 .messages']                       # канва = сторінка: лишається var(--anc-canvas)
PLATE = ['.v2 .product-art', '.v2 .scenario-intro', '.v2 .review-item',  # плашки всередині білих карток → var(--anc-plate)
         '.v2 .regular-table th', '.v2 textarea:disabled']
ANC_EXTRA = ('.v2 .brand-mark { background:var(--anc-yellow); color:var(--anc-blue); border-radius:50%; }'
             '  /* Х25.2: лого на жовтому колі (фавікон брендбука); icon-chip не чіпаємо */\n'
             '.v2 .brand-mark svg { width:75%; height:75%; fill:currentColor; stroke:none; }'
             '  /* 75 % = безпечна зона ≥12.5 %; .v2 svg дає fill:none + stroke — для лого навпаки */')
SYM = '<symbol id="i-anc" viewBox="0 0 250.6 229.9"><path fill-rule="evenodd" d="M55.5 134.9L28.1 134.9L23.1 149.7C22.7 151.1 21.4 152.0 20.0 152.0L3.8 152.0C1.6 152.0 0.0 149.8 0.7 147.7L21.8 81.8C22.2 80.4 23.5 79.5 24.9 79.5L58.8 79.5C60.2 79.5 61.5 80.4 61.9 81.8L83.3 147.7C84.0 149.8 82.4 152.0 80.2 152.0L63.3 152.0C61.8 152.0 60.6 151.0 60.1 149.7L55.5 134.9M32.7 119.4L50.5 119.5L41.8 91.0L32.7 119.4Z"/><path fill-rule="evenodd" d="M177.2 148.3L177.2 83.0C177.2 81.2 178.7 79.7 180.5 79.7L197.5 79.7C199.3 79.7 200.8 81.2 200.8 83.0L200.8 133.1L217.8 133.1L217.8 83.0C217.8 81.2 219.2 79.7 221.1 79.7L238.1 79.7C239.9 79.7 241.4 81.2 241.4 83.0L241.4 133.1L247.3 133.1C249.1 133.1 250.6 134.6 250.6 136.4L250.6 161.9C250.6 163.7 249.1 165.2 247.3 165.2L239.9 165.2C238.2 165.2 236.8 163.9 236.6 162.3L235.0 151.6L180.5 151.6C178.7 151.6 177.2 150.2 177.2 148.3Z"/><path fill-rule="evenodd" d="M162.1 82.8L162.1 148.3C162.1 150.2 160.6 151.6 158.8 151.6L140.9 151.6C139.1 151.6 137.6 150.2 137.6 148.3L137.6 125.1L117.5 125.1L117.5 148.3C117.5 150.2 116.0 151.6 114.2 151.6L96.3 151.6C94.5 151.6 93.0 150.2 93.0 148.3L93.0 82.8C93.0 81.0 94.5 79.5 96.3 79.5L114.2 79.5C116.0 79.5 117.5 81.0 117.5 82.8L117.5 106.0L137.6 106.0L137.6 82.8C137.6 81.0 139.1 79.5 140.9 79.5L158.8 79.5C160.6 79.5 162.1 81.0 162.1 82.8Z"/><path fill-rule="nonzero" d="M110.0 27.6C116.2 39.1 129.0 42.9 129.0 42.9C136.9 45.4 165.4 43.1 172.4 44.5C179.4 45.9 185.4 46.3 187.6 44.4C189.8 42.5 187.3 39.5 184.1 38.1C174.4 33.8 152.3 30.1 152.3 30.1C152.3 30.1 184.8 15.3 219.6 61.5C221.9 64.5 230.1 63.8 226.4 56.6C222.3 48.6 193.9 0.0 126.2 0.0C80.2 0.0 43.9 30.2 28.0 61.6C27.4 62.9 29.1 64.0 30.0 62.9C42.4 48.3 73.0 18.5 110.0 27.6Z"/><path fill-rule="nonzero" d="M143.5 202.3C137.4 190.8 124.5 187.0 124.5 187.0C116.6 184.5 88.1 186.8 81.1 185.4C74.1 183.9 68.1 183.6 65.9 185.5C63.7 187.4 66.2 190.3 69.4 191.7C79.1 196.0 101.2 199.7 101.2 199.7C101.2 199.7 68.7 214.5 33.9 168.4C31.6 165.3 23.4 166.1 27.1 173.3C31.2 181.3 59.6 229.9 127.3 229.9C173.3 229.9 209.7 199.6 225.5 168.3C226.1 167.0 224.4 165.8 223.5 166.9C211.1 181.5 180.5 211.4 143.5 202.3Z"/></symbol>'
JS = [  # П15: [назва, було, стало]
 ('плитка бренду · sidebar()', "el('div',{class:'brand-mark'},[icon('i-bag')])", "el('div',{class:'brand-mark'},[icon('i-anc')])"),
]
V1_BLOCK = '<style id="v2-css-anc">\n/* ── АНЦ токени · x25_apply_v1 (генерується, руками не правити) ── */\n.v2 { --anc-yellow:#FFE241; --anc-yellow-50:#FFF0A0; --anc-yellow-25:#FFF8D0; --anc-blue:#008ECC; --anc-blue-25:#BFE3F2; --anc-canvas:#FEFFE7; --anc-text:#1C1E24; --anc-text-2:#4F4F4F; --anc-gray:#6E6E77; --anc-gray-light:#9B9CA1; --anc-border:#E7E7E7; --anc-positive:#1E815D; }\n.v2 .brand-mark { background:var(--anc-yellow); color:var(--anc-blue); }  /* плитка бренду ≠ icon-chip; іконку замінить лого (Х25.2) */\n</style>'
A0, A1 = '<style id="v2-css-anc">', '</style>'
SPRITE = '<svg id="v2-sprite"'
def anc_block():
    return (A0 + '\n/* ── АНЦ токени · x25_apply_v2 (генерується, руками не правити) ── */\n.v2 { ' +
            ' '.join('--anc-%s:%s;' % kv for kv in TOK.items()) + ' }\n' + ANC_EXTRA + '\n' + A1)
def blocks(h):
    out=[]
    for bid in ('v2-css','v2-css-own'):
        a=h.index('<style id="%s">'%bid)+len('<style id="%s">'%bid); out.append((a,h.index('</style>',a)))
    return out
def rules(h, sel):
    """правила з рівно цим селектором у v2-css + v2-css-own, що несуть токен канви/плашки → [(початок тіла, кінець тіла)]
       (селектор може мати кілька правил — напр. .v2 має три; судимо лише те, що фарбує канвою)"""
    found=[]
    for a,b in blocks(h):
        for r in re.finditer(r'([^{}]+)\{([^{}]*)\}', h[a:b]):
            s=re.sub(r'\s+',' ',re.sub(r'/\*.*?\*/','',r.group(1),flags=re.S)).strip()
            if s==sel and re.search(r'var\(--anc-(canvas|plate)\)', r.group(2)): found.append((a+r.start(2), a+r.end(2)))
    return found
def main(root):
    f=os.path.join(root,'index.html'); h=open(f,encoding='utf-8').read()
    for m in ('<style id="v2-css">','<style id="v2-css-own">',SPRITE): assert h.count(m)==1, 'маркер не рівно раз: '+m
    assert h.count(A0)==1, 'блоку v2-css-anc немає — спершу x25_apply_v1'
    a=h.index(A0); b=h.index(A1,a)+len(A1); blk=h[a:b]
    if blk==V1_BLOCK: state='v1'
    elif blk==anc_block(): state='v2'
    else: raise AssertionError('блок v2-css-anc — ні v1, ні v2 (руками правили?)')
    n_edit=0
    # 1 · блок токенів — цілком
    if state=='v1': h=h[:a]+anc_block()+h[b:]
    # 2 · канва: сторінка лишається, плашки → plate (кожен селектор — рівно одне правило, рівно один var)
    for sel in PAGE:
        r=rules(h,sel); assert len(r)==1, 'сторінка: правил не рівно раз: '+sel
        body=h[r[0][0]:r[0][1]]; assert body.count('var(--anc-canvas)')==1 and 'anc-plate' not in body, 'сторінка не на canvas: '+sel
    for sel in PLATE:
        r=rules(h,sel); assert len(r)==1, 'плашка: правил не рівно раз: '+sel
        s,e=r[0]; body=h[s:e]; nc=body.count('var(--anc-canvas)'); npl=body.count('var(--anc-plate)')
        if state=='v1':
            assert nc==1 and npl==0, 'плашка не в стані «було»: '+sel
            h=h[:s]+body.replace('var(--anc-canvas)','var(--anc-plate)')+h[e:]; n_edit+=1
        else: assert nc==0 and npl==1, 'плашка не в стані «стало»: '+sel
    assert h.count('var(--anc-canvas)')==len(PAGE), 'canvas поза списком сторінки: %d' % h.count('var(--anc-canvas)')
    assert h.count('var(--anc-plate)')==len(PLATE), 'plate поза списком плашок'
    # 3 · символ лого у спрайті
    if state=='v1':
        assert 'id="i-anc"' not in h, 'i-anc уже є — база змішана'
        s=h.index(SPRITE); e=h.index('</svg>',s); h=h[:e]+SYM+h[e:]
    else: assert h.count(SYM)==1 and h.count('id="i-anc"')==1, 'символ i-anc не той'
    # 4 · JS
    for name,old,new in JS:
        if state=='v1': assert h.count(old)==1, 'JS «було» не рівно раз: '+name; h=h.replace(old,new)
        else: assert h.count(new)==1 and old not in h, 'JS не в стані «стало»: '+name
    assert h.count("icon('i-anc')")==1 and h.count("icon('i-bag')")>=1, 'i-anc у плитці / i-bag у icon-chip'
    # гард: у трьох блоках лише дозволені літерали
    allowed=LIT_OUT|KEEP|{'#fff'}|{t.lower() for t in TOK.values()}
    for bid in ('v2-css','v2-css-own','v2-css-anc'):
        s=h.index('<style id="%s">'%bid); e=h.index('</style>',s)
        cl=re.sub(r'/\*.*?\*/','',h[s:e],flags=re.S)
        bad={x.lower() for x in re.findall(r'#[0-9a-fA-F]{3,8}\b',cl)}-allowed
        assert not bad, bid+': літерал поза таблицею: '+str(sorted(bad))
    if state=='v1': open(f,'w',encoding='utf-8').write(h)
    print('x25 v2: %s · плашок %d · символ лого %s · JS %d · токенів %d' % (
        'застосовано (з v1)' if state=='v1' else 'вже застосовано, без змін', n_edit,
        '+1' if state=='v1' else '0', len(JS) if state=='v1' else 0, len(TOK)))
if __name__=='__main__': main(sys.argv[1] if len(sys.argv)>1 else '.')
