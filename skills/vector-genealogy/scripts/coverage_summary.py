#!/usr/bin/env python3
"""Сводка покрытия дела: сколько источников заведено, что уже оценено, где стоят блокировки.

Только читает существующие реестры; ничего не меняет и не обращается к сети.
«Заведено» — строки реестра артефактов; «оценено» — артефакт, которому назначен статус,
отличный от `lead-only`; «ожидает независимости» — не заполнена группа исходного документа.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # `python -I` omits the script folder

from research_common import SourceError, configure_utf8_stdio, outside_skill, output_json

UNASSESSED_STATUSES = {"", "lead-only"}
SEARCH_STATUSES = ("found", "not-found", "blocked", "partial")
SEARCH_LOG = "search-log.csv"
ARTIFACT_REGISTER = "artifact-register.csv"


def read_rows(path, id_field):
    if not path.is_file():
        raise SourceError("Сначала создайте дело через init_case.py.")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if id_field not in fields:
            raise SourceError(f"Некорректный реестр {path.name}.")
        rows = [row for row in reader if any((value or "").strip() for value in row.values())]
    return rows


def summarize(case):
    case = Path(case).expanduser().resolve()
    artifacts = read_rows(case / ARTIFACT_REGISTER, "artifact_id")
    searches = read_rows(case / SEARCH_LOG, "search_id")
    by_status = Counter((row.get("status") or "").strip() or "не оценено" for row in artifacts)
    assessed = sum(1 for row in artifacts if (row.get("status") or "").strip() not in UNASSESSED_STATUSES)
    without_group = sum(1 for row in artifacts if not (row.get("independence_group") or "").strip())
    by_result = Counter((row.get("result_status") or "").strip() or "не указан" for row in searches)
    unknown_statuses = sorted(set(by_result) - set(SEARCH_STATUSES) - {"не указан"})
    by_source = Counter((row.get("source_or_domain") or "").strip() or "не указан" for row in searches)
    blocked = [{"search_id": row.get("search_id", ""), "source": (row.get("source_or_domain") or "").strip(),
                "blocker": (row.get("blocker") or "").strip()}
               for row in searches if (row.get("result_status") or "").strip() == "blocked"]
    return {
        "artifacts": {"total": len(artifacts), "assessed": assessed,
                      "awaiting_assessment": len(artifacts) - assessed,
                      "without_independence_group": without_group, "by_status": dict(sorted(by_status.items()))},
        "searches": {"total": len(searches), "by_result_status": dict(sorted(by_result.items())),
                     "unknown_result_statuses": unknown_statuses, "by_source": dict(sorted(by_source.items()))},
        "blocked_searches": blocked,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(allow_abbrev=False, description="Сводка покрытия дела по реестрам.")
    parser.add_argument("--case-dir", required=True)
    parser.add_argument("--out", help="JSON вне папки навыка; по умолчанию stdout")
    args = parser.parse_args(argv)
    try:
        if args.out:
            outside_skill(args.out)
        output_json(summarize(args.case_dir), args.out)
        return 0
    except (SourceError, OSError, ValueError, TypeError, KeyError) as exc:
        message = str(exc) if isinstance(exc, SourceError) else "Некорректный файл или ошибка локального чтения."
        print("Ошибка: " + message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    configure_utf8_stdio()
    raise SystemExit(main())
