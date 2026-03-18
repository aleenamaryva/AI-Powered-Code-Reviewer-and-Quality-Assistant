# tests/test_coverage_reporter.py
"""Unit tests for core.reporter.coverage_reporter.CoverageReporter."""

import json
import pytest
from core.reporter.coverage_reporter import CoverageReporter

# ── Fixtures ───────────────────────────────────────────────────────────────────

SAMPLE_RESULTS = [
    {"file": "sample_a.py", "function": "calculate_average", "line": 5,  "docstring": False, "args": 1},
    {"file": "sample_a.py", "function": "find_max",          "line": 10, "docstring": False, "args": 1},
    {"file": "sample_b.py", "function": "read_file",         "line": 7,  "docstring": False, "args": 1},
    {"file": "sample_b.py", "function": "write_json",        "line": 12, "docstring": True,  "args": 2},
    {"file": "sample_b.py", "function": "validate_email",    "line": 21, "docstring": False, "args": 1},
]


@pytest.fixture
def reporter():
    """Provide a CoverageReporter pre-loaded with sample results."""
    return CoverageReporter(SAMPLE_RESULTS)


@pytest.fixture
def all_documented_reporter():
    """Provide a CoverageReporter where every function is documented."""
    results = [dict(r, docstring=True) for r in SAMPLE_RESULTS]
    return CoverageReporter(results)


@pytest.fixture
def empty_reporter():
    """Provide a CoverageReporter with no results."""
    return CoverageReporter([])


# ── Stats ──────────────────────────────────────────────────────────────────────

class TestStats:
    def test_total(self, reporter):
        assert reporter.stats["total"] == 5

    def test_documented(self, reporter):
        assert reporter.stats["documented"] == 1

    def test_missing(self, reporter):
        assert reporter.stats["missing"] == 4

    def test_coverage_pct(self, reporter):
        assert reporter.stats["coverage_pct"] == 20.0

    def test_full_coverage(self, all_documented_reporter):
        assert all_documented_reporter.stats["coverage_pct"] == 100.0

    def test_empty_coverage(self, empty_reporter):
        assert empty_reporter.stats["coverage_pct"] == 0.0
        assert empty_reporter.stats["total"] == 0


# ── JSON export ────────────────────────────────────────────────────────────────

class TestToJson:
    def test_returns_string(self, reporter):
        assert isinstance(reporter.to_json(), str)

    def test_valid_json(self, reporter):
        data = json.loads(reporter.to_json())
        assert "summary" in data
        assert "functions" in data
        assert "generated_at" in data

    def test_summary_matches_stats(self, reporter):
        data = json.loads(reporter.to_json())
        assert data["summary"]["total"] == reporter.stats["total"]
        assert data["summary"]["documented"] == reporter.stats["documented"]

    def test_functions_count(self, reporter):
        data = json.loads(reporter.to_json())
        assert len(data["functions"]) == 5


# ── CSV export ─────────────────────────────────────────────────────────────────

class TestToCsv:
    def test_returns_string(self, reporter):
        assert isinstance(reporter.to_csv(), str)

    def test_has_header(self, reporter):
        csv_str = reporter.to_csv()
        assert "file" in csv_str
        assert "function" in csv_str
        assert "docstring" in csv_str

    def test_row_count(self, reporter):
        csv_lines = reporter.to_csv().strip().splitlines()
        # header + 5 data rows
        assert len(csv_lines) == 6


# ── Test suite grouping ────────────────────────────────────────────────────────

class TestRunTests:
    def test_returns_dict(self, reporter):
        result = reporter.run_tests()
        assert isinstance(result, dict)

    def test_suite_keys_contain_tests(self, reporter):
        result = reporter.run_tests()
        for key in result:
            assert "Tests" in key

    def test_passed_counts(self, reporter):
        result = reporter.run_tests()
        total_passed = sum(v["passed"] for v in result.values())
        assert total_passed == 1  # only write_json is documented


# ── Missing functions ──────────────────────────────────────────────────────────

class TestMissingFunctions:
    def test_returns_list(self, reporter):
        assert isinstance(reporter.missing_functions(), list)

    def test_count(self, reporter):
        assert len(reporter.missing_functions()) == 4

    def test_names(self, reporter):
        names = {r["function"] for r in reporter.missing_functions()}
        assert "calculate_average" in names
        assert "write_json" not in names

    def test_empty_when_all_documented(self, all_documented_reporter):
        assert reporter_empty := all_documented_reporter.missing_functions() == []


# ── Coverage by file ───────────────────────────────────────────────────────────

class TestCoverageByFile:
    def test_returns_dict(self, reporter):
        assert isinstance(reporter.coverage_by_file(), dict)

    def test_files_present(self, reporter):
        by_file = reporter.coverage_by_file()
        assert "sample_a.py" in by_file
        assert "sample_b.py" in by_file

    def test_sample_a_zero_coverage(self, reporter):
        by_file = reporter.coverage_by_file()
        assert by_file["sample_a.py"]["coverage_pct"] == 0.0
        assert by_file["sample_a.py"]["total"] == 2

    def test_sample_b_partial_coverage(self, reporter):
        by_file = reporter.coverage_by_file()
        # 1 of 3 documented
        assert by_file["sample_b.py"]["documented"] == 1
        assert by_file["sample_b.py"]["missing"] == 2
