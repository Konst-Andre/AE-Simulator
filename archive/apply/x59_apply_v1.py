#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
x59_apply_v1.py  ·  AE_X27_SIDEBAR_v14.html -> v15
живе доки: Х27-К2 «ПУНКТИ» не закрито вироком оператора.

Х27-К2: три нові осі пунктів навігації (HTML/CSS, JS-логіки продукту не чіпає).
  hover    нинішній | нейтральний 8 %          (вирок S53: НЕ жовтий)
  actform  смуга-зліва | смуга-знизу | заливка | заливка+смуга | капсула
  touch    47 | 48                             (0.3-З, поріг M3)

ДІМ (12.11): живе значення — var state; канал малювання — <style id="lv-nav">
в document.head (пункти живуть у світлому DOM харнеса, НЕ в тіні зліпка,
тому lv-page для них не підходить).

П64: стартова позиція = паспорт оператора 13.09.2026, тобто нинішня поведінка
v14: hover=нинішній · actform=заливка+смуга · touch=47. Нових пресетів не ставлю.
Шаблони зліпка (snapCSS :424-1145 · snapSprite · snapPicker · snapCatalog) НЕ чіпає.
"""
import hashlib, io, os, sys

SRC = 'AE_X27_SIDEBAR_v14.html'
DST = 'AE_X27_SIDEBAR_v15.html'

# ── 1. HTML: три групи важелів, перед групою «сторінка» ─────────────────────
A_HTML = '  <div class="grp" data-k="page"><label>сторінка</label><div class="row" data-ax="page">'
N_HTML = '''  <div class="grp" data-k="hover"><label>пункт · hover</label><div class="row" data-ax="hover">
    <button type="button" data-v="now">нинішній</button>
    <button type="button" data-v="neutral">нейтральний 8 %</button></div></div>
  <div class="grp" data-k="actform"><label>пункт · форма активного</label><div class="row" data-ax="actform">
    <button type="button" data-v="left">смуга зліва</button>
    <button type="button" data-v="bottom">смуга знизу</button>
    <button type="button" data-v="fill">заливка</button>
    <button type="button" data-v="fillbar">заливка+смуга</button>
    <button type="button" data-v="capsule">капсула</button></div></div>
  <div class="grp" data-k="touch"><label>пункт · висота дотику</label><div class="row" data-ax="touch">
    <button type="button" data-v="47">47</button>
    <button type="button" data-v="48">48 (M3)</button></div></div>
''' + A_HTML

# ── 2. state: три ключі, дефолти = паспорт (нинішня поведінка v14) ──────────
A_ST = "              corners:'right' };"
N_ST = ("              corners:'right',\n"
        "              /* Х27-К2 · дефолти = паспорт П64, тобто те, що v14 малює сьогодні:\n"
        "                 active має заливку --anc-yellow-25 І смугу зліва 3px var(--green). */\n"
        "              hover:'now', actform:'fillbar', touch:'47' };")

# ── 3. apply(): нові осі в paintRow і виклик paintNav ───────────────────────
A_AX = ("  ['shell','rule','mode','elev','frame','fit','set','stub','page','sub','rail','railpos','corners']")
N_AX = ("  ['shell','rule','mode','elev','frame','fit','set','stub','page','sub','rail','railpos','corners',\n"
        "   'hover','actform','touch']")

A_CALL = "  paintPage();\n  measure();"
N_CALL = "  paintPage();\n  paintNav();\n  measure();"

# ── 3б. leverWhy: вісь форми мертва за версткою при наборі «6 куратор» ─────
A_WHY = ("  if(k==='fit')     return state.railpos==='group' ? "
         "'при центрі групи панель завжди на висоту вікна' : null;")
N_WHY = A_WHY + ("\n  /* §8.7-а · мертвий за ВЕРСТКОЮ: у SETS['6'] усі шість рядків — заглушки,\n"
                 "     build() не ставить .active нікому, і форма активного не має на чому\n"
                 "     проступити. Важіль мусить назвати винуватця, а не сіріти мовчки. */\n"
                 "  if(k==='actform') return state.set==='6' ? "
                 "'при наборі 6 куратор жоден пункт не активний — усі заглушки (SETS, Д-В2)' : null;")

# ── 4. paintNav(): канал пунктів ────────────────────────────────────────────
A_FN = "function paintPage(){"
N_FN = r'''/* ══ Х27-К2 · КАНАЛ ПУНКТІВ ═══════════════════════════════════════════════
   Окремий вузол style у head, НЕ lv-page: .side-link живе у світлому DOM
   харнеса, а lv-page сидить у shadowRoot зліпка і до пунктів не дістає.
   ⚠ П44 (пробито по мережі): рівна смуга через border-left на елементі з
   радіусом дає криві артефакти по кутах. Тому всі п'ять форм малюються
   ::after-ом з абсолютним позиціонуванням, а вшитий border-left гаситься.
   ⚠ Кожна форма мусить читатись і в РЕЙЦІ 72 (.lbl схований), не лише
   в розгорнутій панелі — інакше вирок виноситься по одному стану з двох. */
var LN = null;
function paintNav(){
  if(!LN){ LN = document.createElement('style'); LN.id = 'lv-nav';
           document.head.appendChild(LN); }
  var css = '';

  /* вісь 3 · висота дотику */
  css += '.v2 .side-link{min-height:' + state.touch + 'px}';

  /* вісь 1 · hover. «нинішній» нічого не додає — показує успадкований стан.
     «нейтральний 8 %» — чорний текстовий токен на 8 % альфи (#1C1E2414),
     навмисно НЕ жовтий: вирок S53. Активний пункт із hover не змішуємо. */
  if(state.hover === 'neutral')
    css += '.v2 .side-link:not(.active):hover{background:#1C1E2414}';

  /* вісь 2 · форма активного. Спершу знімаємо вшите (:87-88), щоб кожна
     форма малювалась із чистого аркуша і П63 могло зміряти різницю. */
  css += '.v2 .side-link{position:relative}'
       + '.v2 .side-link.active{border-left-color:transparent;background:none;'
       + 'border-radius:0 8px 8px 0;margin:0;color:var(--anc-text);font-weight:700}'
       + '.v2 .side-link.active::after{content:none}';

  var BAR_L = '.v2 .side-link.active::after{content:"";position:absolute;left:0;top:0;bottom:0;'
            + 'width:3px;background:var(--green);border-radius:0 3px 3px 0}';
  var FILL  = '.v2 .side-link.active{background:var(--anc-yellow-25)}';

  if(state.actform === 'left')    css += BAR_L;
  if(state.actform === 'bottom')  css += '.v2 .side-link.active::after{content:"";position:absolute;'
                                       + 'left:18px;right:18px;bottom:0;height:3px;'
                                       + 'background:var(--green);border-radius:3px 3px 0 0}';
  if(state.actform === 'fill')    css += FILL;
  if(state.actform === 'fillbar') css += FILL + BAR_L;
  if(state.actform === 'capsule') css += '.v2 .side-link.active{background:var(--anc-yellow-25);'
                                       + 'border-radius:24px;margin:0 8px;padding:0 14px}'
                                       + '.v2[data-mode="rail"] .side-link.active{margin:0 12px;padding:0}';

  LN.textContent = css;
}
function paintPage(){'''

MARK = "id = 'lv-nav'"


def patch(src):
    out = src
    for a, n in ((A_HTML, N_HTML), (A_ST, N_ST), (A_AX, N_AX), (A_CALL, N_CALL),
                 (A_WHY, N_WHY), (A_FN, N_FN)):
        if out.count(a) != 1:
            sys.stderr.write('ЯКІР НЕ ОДИН (%d входжень): %r\n' % (out.count(a), a[:60]))
            sys.exit(2)
        out = out.replace(a, n, 1)
    return out


def main():
    if not os.path.exists(SRC):
        sys.stderr.write('немає %s\n' % SRC); sys.exit(2)
    src = io.open(SRC, encoding='utf-8').read()
    base = io.open(DST, encoding='utf-8').read() if os.path.exists(DST) else None
    if base is not None and MARK in base:
        print('ІДЕМПОТЕНТНО: %s уже містить lv-nav, конвеєр не запускався' % DST)
        print('md5 %s' % hashlib.md5(base.encode('utf-8')).hexdigest())
        return 0
    out = patch(src)
    io.open(DST, 'w', encoding='utf-8').write(out)
    print('зібрано %s  (%d Б)' % (DST, len(out.encode('utf-8'))))
    print('md5 %s' % hashlib.md5(out.encode('utf-8')).hexdigest())
    return 0


if __name__ == '__main__':
    sys.exit(main())
