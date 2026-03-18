# core/reporter/coverage_reporter.py
"""Coverage reporter — aggregates scan results and produces structured reports."""

from __future__ import annotations
import csv
import io
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class CoverageReporter:
    """Builds docstring-coverage reports from scan results.

    Supports JSON and CSV export, and generates test suite summaries
    compatible with the dashboard UI.

    Args:
        results (list[dict]): Raw scan results from python_parser.scan_file().
    """

    def __init__(self, results: List[Dict[str, Any]]):
        """Initialize the reporter with a list of scan results.

        Args:
            results (list[dict]): Scan result dicts (file, function, line,
                                  docstring, args).
        """
        self.results = results
        self._computed: Optional[Dict] = None

    # ── Computed stats ─────────────────────────────────────────────────────────

    @property
    def stats(self) -> Dict[str, Any]:
        """Return cached summary statistics.

        Returns:
            dict: Keys: total, documented, missing, coverage_pct.
        """
        if self._computed is None:
            self._computed = self._compute_stats()
        return self._computed

    def _compute_stats(self) -> Dict[str, Any]:
        """Compute summary statistics from raw results.

        Returns:
            dict: Aggregated stats dictionary.
        """
        total = len(self.results)
        documented = sum(1 for r in self.results if r.get("docstring"))
        missing = total - documented
        coverage_pct = round((documented / total * 100), 1) if total else 0.0
        return {
            "total": total,
            "documented": documented,
            "missing": missing,
            "coverage_pct": coverage_pct,
        }

    # ── Report generation ──────────────────────────────────────────────────────

    def to_json(self, indent: int = 2) -> str:
        """Serialize the full report to a JSON string.

        Args:
            indent (int): JSON indentation level.

        Returns:
            str: JSON-encoded report.
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.stats,
            "functions": self.results,
        }
        return json.dumps(report, indent=indent)

    def to_csv(self) -> str:
        """Serialize function results to a CSV string.

        Returns:
            str: CSV-encoded function list.
        """
        output = io.StringIO()
        fieldnames = ["file", "function", "line", "docstring", "args"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(self.results)
        return output.getvalue()

    def run_tests(self) -> Dict[str, Dict]:
        """Group scan results into per-file test suites with pass/fail counts.

        Returns:
            dict: Mapping of suite name → {total, passed, items}.
        """
        groups: Dict[str, list] = {}
        for r in self.results:
            fname = r["file"]
            key = fname.replace(".py", "").replace("_", " ").title() + " Tests"
            groups.setdefault(key, []).append(r)

        test_summary = {}
        for suite, items in groups.items():
            total = len(items)
            passed = sum(1 for i in items if i["docstring"])
            test_summary[suite] = {"total": total, "passed": passed, "items": items}
        return test_summary

    def missing_functions(self) -> List[Dict[str, Any]]:
        """Return only the functions that are missing a docstring.

        Returns:
            list[dict]: Filtered results where docstring is False.
        """
        return [r for r in self.results if not r.get("docstring")]

    def coverage_by_file(self) -> Dict[str, Dict[str, Any]]:
        """Compute per-file coverage statistics.

        Returns:
            dict: File name → {total, documented, missing, coverage_pct}.
        """
        by_file: Dict[str, list] = {}
        for r in self.results:
            by_file.setdefault(r["file"], []).append(r)

        report = {}
        for fname, items in by_file.items():
            total = len(items)
            documented = sum(1 for i in items if i.get("docstring"))
            missing = total - documented
            pct = round((documented / total * 100), 1) if total else 0.0
            report[fname] = {
                "total": total,
                "documented": documented,
                "missing": missing,
                "coverage_pct": pct,
            }
        return report

    def save_json(self, path: str) -> None:
        """Write the JSON report to disk.

        Args:
            path (str): Destination file path.
        """
        from pathlib import Path
        Path(path).write_text(self.to_json(), encoding="utf-8")

    def save_csv(self, path: str) -> None:
        """Write the CSV report to disk.

        Args:
            path (str): Destination file path.
        """
        from pathlib import Path
        Path(path).write_text(self.to_csv(), encoding="utf-8")
