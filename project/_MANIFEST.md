# AE-Simulator · `project/_MANIFEST.md`

живе доки: тека `project/` існує

**Що це і чим не є.** Це **інвентар теки**: який файл тут лежить, його md5, доки він живий,
до якого щабля стосується. Це НЕ заміна `AE_Simulator_CHERGA.md` — ЧЕРГА лишається єдиним
носієм **відкритого по продукту** (що робити далі) і живе в `summary/`. Маніфест відповідає
на питання «що тут лежить і чи воно ще те саме», ЧЕРГА — на питання «що робимо».

Заміряно інструментом (`md5sum`) у сесії S80 · 19.09.2026.
Розбіжність md5 із фактичним файлом = подія, яку розбирають до роботи.

| файл | md5 (8) | розмір | живе доки | щабель ЧЕРГИ |
|---|---|---|---|---|
| `summary/AE_Simulator_CHERGA.md` | `2e1d0502` | 8 КБ | у черзі є хоч один непройдений щабель | — |
| `summary/AE_Simulator_session_summary_S79_DIM_U_REPO.md` | `125d365c` | 16 КБ | D2 (порт A2 v2 у X97) не завершено | щабель 2 |
| `summary/AE_Simulator_session_summary_S80_PROKHID_V44.md` | `3e880faa` | 23 КБ | v4.5 (В-118…В-126) не видана | щабель 2 |
| `knowledge/AE_Simulator_SPEC_v0_5.md` | `9a345be9` | 87 КБ | назавжди | — |
| `knowledge/AE_Simulator_BIBLIOTEKA_HARAKTERIV_v1.md` | `b210bef7` | 19 КБ | назавжди | — |
| `knowledge/AE_Simulator_MOOD_RULE_v1.md` | `b53d54b0` | 16 КБ | назавжди | — |
| `knowledge/AE_Simulator_PROMPT_JUDGE_SPEC_v1.md` | `0a91ea5c` | 9 КБ | назавжди | — |
| `knowledge/AE_Simulator_DOSIE_COMPOSER_v1.md` | `82d48dae` | 11 КБ | щабель 3 не закрито | щабель 3 |
| `stand/a2/mock_a2v2_tpl_v4_4.html` | `98d4ae93` | 57 КБ | A2 v2 не портовано в X97 | щабель 2 · D2 |
| `stand/a2/d1_a2v2_mock_build_v4_4.py` | `5abac9b9` | 2 КБ | шаблон v4.4 живий | щабель 2 · D2 |
| `stand/a2/s78_olya_walk_v3.py` | `a2e45e42` | 15 КБ | стенд A2 живий (45 кроків регресу) | щабель 2 · D2 |
| `stand/a2/s79_v44_probe_v1.py` | `bfc2e419` | 2 КБ | v4.4 не змерджено в наступну версію | щабель 2 · D2 |
| `stand/a2/s79_v44_grp_probe_v1.py` | `e8bee1bd` | 1 КБ | v4.4 не змерджено в наступну версію | щабель 2 · D2 |
| `stand/a2/s80_freewalk_probe_v1.py` | `8f52f389` | 7 КБ | знахідки Н9–Н14 не винесені у вироки й не стали кроками | щабель 2 |
| `stand/a2/s80_freewalk_probe_v2_add.py` | `e9569a4f` | 3 КБ | те саме (домір Н9 · Н12) | щабель 2 |
| `stand/a2/AE_D1v4_FINDINGS_v4.md` | `59885487` | 26 КБ | вироки не перенесено в SPEC і код (П116) | щабель 2 · D2 |
| `stand/composer/AE_COMPOSER_harness_v2.html` | `fc20a6b8` | 35 КБ | Е2 «Композер» не закрито | щабель 3 |
| `stand/sources/mockup_X21_v1_html.html` | `d779cfc7` | 88 КБ | є непортовані A-екрани | щаблі 5·6·7 |
| `stand/sources/AE_X27_SIDEBAR_v19.html` | `4609434b` | 160 КБ | є непортовані A-екрани | щаблі 5·6·7 |
| `stand/sources/ANC_island_animations_standalone_v1.html` | `67da39db` | 28 КБ | рух і шрифти не зроблено | щабель 8 |
| `tools/x70_preview_build_v3.py` | `a2690507` | 5 КБ | прев'ю потрібне для видачі оператору | — |

## Не в `project/` за рішенням

| файл | де він | чому |
|---|---|---|
| `AE_MOCK_A2v2_D1_v4_4.html` | відтворюється `stand/a2/d1_a2v2_mock_build_v4_4.py` | похідне; md5 `807bf9ae` (П34 · П37) |
| `ae_rules_X95_v1.js` | `tools/ae_rules.js` у корені репо | побайтово той самий файл, `e0b99591` |
| `v42`/`v43`/`v44_apply_v1.py` | `archive/apply/` | одноразові, шаблон уже запечено |
| шаблон і генератор v4.3 | `archive/stand/` | мертва версія (П118) |
| самері S73–S78 · `x95`–`x98_apply` · `AE_WORK_index_X24_5` | `archive/` | мертві версії |
| `AE_WORK_index_X97_v1.html` | тільки claude.ai Project | В-115 дозволив `index_work/`, але `Lens_claude_github_push.py:26` `FORBIDDEN_PATH` блокує шлях — чекає на правку ядра в governance-сесії |
| `AE_CHAT_BG_stagebench_v1.html` | ніде | стенд фону чату, заміщений композером (В-116) |
