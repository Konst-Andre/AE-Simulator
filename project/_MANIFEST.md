# AE-Simulator · `project/_MANIFEST.md`

живе доки: тека `project/` існує

**Що це і чим не є.** Це **інвентар теки**: який файл тут лежить, його md5, доки він живий,
до якого щабля стосується. Це НЕ заміна `AE_Simulator_CHERGA.md` — ЧЕРГА лишається єдиним
носієм **відкритого по продукту** (що робити далі) і живе в `summary/`. Маніфест відповідає
на питання «що тут лежить і чи воно ще те саме», ЧЕРГА — на питання «що робимо».

Заміряно інструментом (`md5sum`) у сесії S80 · 19.09.2026; рядки S82 — 22.09.2026; S83 — 22.09.2026
(S83 виправив два рядки, що відстали після коміту фіксації S82: черга і досьє).
Розбіжність md5 із фактичним файлом = подія, яку розбирають до роботи.

| файл | md5 (8) | розмір | живе доки | щабель ЧЕРГИ |
|---|---|---|---|---|
| `summary/AE_Simulator_CHERGA.md` | `4a723a07` | 9 КБ | у черзі є хоч один непройдений щабель | — |
| `summary/AE_Simulator_session_summary_S83_V45_PROKHID.md` | `d4ee244d` | 12 КБ | наступне самері не стало живим | — |
| `knowledge/AE_Simulator_SPEC_v0_5.md` | `9a345be9` | 87 КБ | назавжди | — |
| `knowledge/AE_Simulator_BIBLIOTEKA_HARAKTERIV_v1.md` | `b210bef7` | 19 КБ | назавжди | — |
| `knowledge/AE_Simulator_MOOD_RULE_v1.md` | `b53d54b0` | 16 КБ | назавжди | — |
| `knowledge/AE_Simulator_PROMPT_JUDGE_SPEC_v1.md` | `0a91ea5c` | 9 КБ | назавжди | — |
| `knowledge/AE_Simulator_DOSIE_COMPOSER_v1.md` | `06d71512` | 11 КБ | щабель 3 не закрито | щабель 3 |
| `stand/a2/mock_a2v2_tpl_v4_5.html` | `145a9ba0` | 61 КБ | A2 v2 не портовано в продукт (D2) | щабель 2 · D2 |
| `stand/a2/d1_a2v2_mock_build_v4_5.py` | `b2e655b4` | 2 КБ | шаблон v4.5 живий | щабель 2 · D2 |
| `stand/a2/s83_olya_walk_v4.py` | `230cb324` | 25 КБ | стенд A2 живий (66 вердиктів: v3 цілком + кроки 24–38) | щабель 2 · D2 |
| `stand/a2/AE_D1v4_FINDINGS_v5.md` | `dc560efa` | 31 КБ | вироки не перенесено в SPEC і код (П116, D2) | щабель 2 · D2 |
| `stand/composer/AE_COMPOSER_harness_v2.html` | `fc20a6b8` | 35 КБ | Е2 «Композер» не закрито | щабель 3 |
| `stand/sources/mockup_X21_v1_html.html` | `d779cfc7` | 88 КБ | є непортовані A-екрани | щаблі 5·6·7 |
| `stand/sources/AE_X27_SIDEBAR_v19.html` | `4609434b` | 160 КБ | є непортовані A-екрани | щаблі 5·6·7 |
| `stand/sources/ANC_island_animations_standalone_v1.html` | `67da39db` | 28 КБ | рух і шрифти не зроблено | щабель 8 |
| `tools/x70_preview_build_v3.py` | `a2690507` | 5 КБ | прев'ю потрібне для видачі оператору | — |

## Не в `project/` за рішенням

| файл | де він | чому |
|---|---|---|
| `AE_MOCK_A2v2_D1_v4_5.html` | відтворюється `stand/a2/d1_a2v2_mock_build_v4_5.py` | похідне; md5 `36a19319` (П34 · П37) |
| `ae_rules_X95_v1.js` | `tools/ae_rules.js` у корені репо | побайтово той самий файл, `e0b99591` |
| `v42`/`v43`/`v44`/`v45_apply_v1.py` | `archive/apply/` | одноразові, шаблон уже запечено |
| шаблон і генератор v4.3 · v4.4 (`807bf9ae`) · `s79_v44_probe_v1` / `s79_v44_grp_probe_v1` | `archive/stand/` | мертві версії (П118); v4.4 змерджено в v4.5 (S83) |
| `s78_olya_walk_v3.py` · `s83_v45_touch_v1.py` · `AE_D1v4_FINDINGS_v4.md` · `s80_freewalk_probe_v1` / `_v2_add` | `archive/stand/` | поглинуті (Н9–Н14 стали кроками 30–36 і замірами) `s83_olya_walk_v4.py` і FINDINGS v5 (S83) |
| `x99_composer_island_apply_v1/v2.py` · `x100_composer_popover_apply_v1.py` | `archive/apply/` | запечено: X100 у корені (S82). Вхід x99 — X97 (`archive/index/`) |
| самері S73–S82 · `x95`–`x98_apply` · `AE_WORK_index_X24_5` | `archive/` | мертві версії |
| робочий білд | корінь репо `index.html` = X100 `72c8cca1` (S82) | В-139: репо — єдиний дім; попередні — git-історія. ланцюг відтворюється: `archive/index/AE_WORK_index_X97_v1.html` (`386394e6`) → x99 v2 → x100 |
| старий v1 `index.html` (build v30, `410efa15`) | `archive/index/index_v30_2026-09-07.html` | заміщений X100 у корені (S82) |
| `AE_CHAT_BG_stagebench_v1.html` | ніде | стенд фону чату, заміщений композером (В-116) |
