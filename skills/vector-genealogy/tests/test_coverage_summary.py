"""Тесты coverage_summary.py на временном деле, созданном init_case.py.

Запуск: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import coverage_summary


class CoverageCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.case = Path(self.tmp.name) / "case"
        subprocess.run(
            [sys.executable, str(SCRIPTS / "init_case.py"), "--case-dir", str(self.case),
             "--research-question", "q"],
            check=True, capture_output=True,
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_rows(self, name: str, rows: list[dict]) -> None:
        path = self.case / name
        with path.open(encoding="utf-8", newline="") as handle:
            fields = csv.DictReader(handle).fieldnames or []
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fields})

    def test_empty_case_reports_zeroes(self):
        summary = coverage_summary.summarize(self.case)
        self.assertEqual(summary["artifacts"]["total"], 0)
        self.assertEqual(summary["searches"]["total"], 0)
        self.assertEqual(summary["blocked_searches"], [])

    def test_separates_assessed_from_lead_only_and_lists_blockers(self):
        self.write_rows("artifact-register.csv", [
            {"artifact_id": "A-0001", "status": "lead-only", "independence_group": ""},
            {"artifact_id": "A-0002", "status": "examined", "independence_group": "G1"},
        ])
        self.write_rows("search-log.csv", [
            {"search_id": "S-0001", "source_or_domain": "familysearch.org", "result_status": "found"},
            {"search_id": "S-0002", "source_or_domain": "pamyat-naroda.ru", "result_status": "blocked",
             "blocker": "CAPTCHA"},
        ])
        summary = coverage_summary.summarize(self.case)
        self.assertEqual(summary["artifacts"]["total"], 2)
        self.assertEqual(summary["artifacts"]["assessed"], 1)
        self.assertEqual(summary["artifacts"]["awaiting_assessment"], 1)
        self.assertEqual(summary["artifacts"]["without_independence_group"], 1)
        self.assertEqual(summary["artifacts"]["by_status"], {"examined": 1, "lead-only": 1})
        self.assertEqual(summary["searches"]["by_result_status"], {"blocked": 1, "found": 1})
        self.assertEqual(summary["searches"]["by_source"], {"familysearch.org": 1, "pamyat-naroda.ru": 1})
        self.assertEqual(len(summary["blocked_searches"]), 1)
        self.assertEqual(summary["blocked_searches"][0]["blocker"], "CAPTCHA")

    def test_unknown_result_status_is_reported_not_hidden(self):
        self.write_rows("search-log.csv", [{"search_id": "S-0001", "result_status": "partial-read"}])
        summary = coverage_summary.summarize(self.case)
        self.assertEqual(summary["searches"]["unknown_result_statuses"], ["partial-read"])

    def test_cli_rejects_case_without_registers(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "coverage_summary.py"), "--case-dir", str(Path(self.tmp.name) / "missing")],
            capture_output=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("Ошибка:", proc.stderr)

    def test_cli_runs_in_isolated_mode(self):
        proc = subprocess.run(
            [sys.executable, "-I", str(SCRIPTS / "coverage_summary.py"), "--case-dir", str(self.case)],
            capture_output=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["artifacts"]["total"], 0)


if __name__ == "__main__":
    unittest.main()
