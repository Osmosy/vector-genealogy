# NOTICE — откуда взято

Репозиторий содержит навык, собранный на базе открытого проекта. Ниже — одна строка на набор:
что взято, под какой лицензией и что изменено.

| Набор | Лицензия | Что взято | Что изменено |
|---|---|---|---|
| [ex-ussr-kinship-research](https://github.com/DenisSergeevitch/ex-ussr-kinship-research) `@1.37.0` | MIT (© 2026 Denis Shiryaev) | 1 скилл: процедура, 24 справочника, 10 скриптов, 11 шаблонов, 11 эвалов, 85 тестов | навык переименован в `vector-genealogy`, `SKILL.md` переписан как короткий маршрут, добавлены `references/sources-ru.md` и `references/territories.md`, «Точка продолжения» в шаблоне `research-state.template.md`, скрипт `coverage_summary.py`; полный текст апстрима сохранён как `references/upstream-procedure.md` |

Текст лицензии апстрима — `THIRD_PARTY_LICENSES/DenisSergeevitch-ex-ussr-kinship-research.txt`.

## Что именно наше

- `skills/vector-genealogy/SKILL.md` — маршрут работы, границы, стартовый промпт, грабли
  (написано заново; апстримный SKILL.md не переносится);
- `skills/vector-genealogy/references/sources-ru.md` — проверка доступности 16 источников
  (коды ответа, антибот, сертификаты) на 01.11.2026;
- `skills/vector-genealogy/references/territories.md` — территории, юрисдикции, разделители-войны;
- `skills/vector-genealogy/assets/research-state.template.md` — раздел «Точка продолжения»
  (источник, шифр, годы, кадр, прочитано / просмотрено / пропуски); остальной шаблон апстримный;
- `skills/vector-genealogy/scripts/coverage_summary.py` и его тест — сводка
  «заведено / оценено / блокировки» по реестрам дела;
- `README.md`, `NOTICE.md`, `LICENSE`.

Остальные справочники, скрипты, эвалы и тесты — файлы апстрима без изменений. Обновление
апстрима переносится заменой этих каталогов; наши файлы при этом сохраняются.
