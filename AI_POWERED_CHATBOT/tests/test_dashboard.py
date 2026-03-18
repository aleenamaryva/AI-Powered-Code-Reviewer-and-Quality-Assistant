# tests/test_dashboard.py
"""Unit tests for dashboard_ui.dashboard utility functions."""

import pytest
from unittest.mock import MagicMock, patch
import tempfile
import os

# Import only pure utility functions — no Streamlit dependency at import time
from dashboard_ui.dashboard import calc_pct, docstring_badge, write_file_to_disk


# ── calc_pct ──────────────────────────────────────────────────────────────────

class TestCalcPct:
    def test_standard_case(self):
        assert calc_pct(10, 5) == 50.0

    def test_full_coverage(self):
        assert calc_pct(4, 4) == 100.0

    def test_zero_coverage(self):
        assert calc_pct(10, 0) == 0.0

    def test_zero_total_returns_zero(self):
        assert calc_pct(0, 0) == 0.0

    def test_rounding(self):
        result = calc_pct(3, 1)
        assert result == 33.3


# ── docstring_badge ───────────────────────────────────────────────────────────

class TestDocstringBadge:
    def test_true_returns_green_badge(self):
        badge = docstring_badge(True)
        assert "badge-green" in badge
        assert "Yes" in badge

    def test_false_returns_red_badge(self):
        badge = docstring_badge(False)
        assert "badge-red" in badge
        assert "No" in badge

    def test_returns_html_span(self):
        assert docstring_badge(True).startswith("<span")
        assert docstring_badge(False).startswith("<span")


# ── write_file_to_disk ────────────────────────────────────────────────────────

class TestWriteFileToDisk:
    def test_writes_and_returns_true(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            tmp_path = f.name
        try:
            content = "# hello\ndef foo(): pass\n"
            ok, result = write_file_to_disk(tmp_path, content)
            assert ok is True
            assert tmp_path in result or os.path.exists(result)
        finally:
            os.unlink(tmp_path)

    def test_content_is_persisted(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            tmp_path = f.name
        try:
            content = "x = 42\n"
            write_file_to_disk(tmp_path, content)
            with open(tmp_path, "r") as f:
                assert f.read() == content
        finally:
            os.unlink(tmp_path)

    def test_permission_error(self):
        ok, msg = write_file_to_disk("/root/no_permission.py", "test")
        assert ok is False
        assert isinstance(msg, str)

    def test_directory_not_found(self):
        ok, msg = write_file_to_disk("/nonexistent/path/file.py", "test")
        assert ok is False
        assert isinstance(msg, str)

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


# ── calc_pct ───────────────────────────────────────────────────────────────────

class TestCalcPct:
    def _calc_pct(self, total, part):
        from dashboard_ui.dashboard import calc_pct
        return calc_pct(total, part)

    def test_half(self):
        assert self._calc_pct(10, 5) == 50.0

    def test_zero_total(self):
        assert self._calc_pct(0, 0) == 0.0

    def test_full(self):
        assert self._calc_pct(4, 4) == 100.0

    def test_rounding(self):
        result = self._calc_pct(3, 1)
        assert result == 33.3


# ── docstring_badge ────────────────────────────────────────────────────────────

class TestDocstringBadge:
    def _badge(self, val):
        from dashboard_ui.dashboard import docstring_badge
        return docstring_badge(val)

    def test_true_returns_green(self):
        badge = self._badge(True)
        assert "badge-green" in badge
        assert "Yes" in badge

    def test_false_returns_red(self):
        badge = self._badge(False)
        assert "badge-red" in badge
        assert "No" in badge


# ── write_file_to_disk ────────────────────────────────────────────────────────

class TestWriteFileToDisk:
    def test_writes_and_verifies(self, tmp_path):
        from dashboard_ui.dashboard import write_file_to_disk
        target = tmp_path / "test.py"
        ok, msg = write_file_to_disk(str(target), "# hello\n")
        assert ok is True
        assert str(target.resolve()) in msg

    def test_content_is_correct(self, tmp_path):
        from dashboard_ui.dashboard import write_file_to_disk
        target = tmp_path / "out.py"
        content = "def foo(): pass\n"
        write_file_to_disk(str(target), content)
        assert target.read_text() == content

    def test_bad_directory_returns_error(self):
        from dashboard_ui.dashboard import write_file_to_disk
        ok, msg = write_file_to_disk("/nonexistent_dir/foo.py", "x")
        assert ok is False
        assert "not found" in msg.lower() or "denied" in msg.lower()
