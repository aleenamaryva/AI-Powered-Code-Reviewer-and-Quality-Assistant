# core/validator/validator.py
"""PEP-compliance validator — checks docstring presence and style conformance."""

from __future__ import annotations
import ast
import re
from typing import List, Dict, Any, Optional, Tuple


class CodeValidator:
    """Validates Python source code for docstring completeness and PEP 257 compliance.

    Detects:
      - Missing module-level docstrings
      - Missing function/method docstrings
      - Missing class docstrings
      - Basic style conformance (one-liner vs multi-line)

    Args:
        source (str): Python source code to validate.
        filename (str): Filename used in violation reports.
    """

    def __init__(self, source: str, filename: str = "module.py"):
        """Initialize the validator with source code.

        Args:
            source (str): Python source code.
            filename (str): Module filename for reporting. Defaults to 'module.py'.
        """
        self.source = source
        self.filename = filename
        self._tree: Optional[ast.Module] = None
        self._parse_error: Optional[str] = None
        self._violations: Optional[List[Dict]] = None

        try:
            self._tree = ast.parse(source)
        except SyntaxError as e:
            self._parse_error = str(e)

    # ── Public API ─────────────────────────────────────────────────────────────

    @property
    def has_parse_error(self) -> bool:
        """Return True if the source has a syntax error.

        Returns:
            bool: Whether a SyntaxError was raised during parsing.
        """
        return self._parse_error is not None

    @property
    def parse_error(self) -> Optional[str]:
        """Return the parse error message, or None.

        Returns:
            str | None: SyntaxError description.
        """
        return self._parse_error

    def validate(self) -> List[Dict[str, Any]]:
        """Run all validation checks and return a list of violations.

        Returns:
            list[dict]: Each dict has keys: rule, file, line, name, severity.
        """
        if self._violations is not None:
            return self._violations

        if self._tree is None:
            return [{"rule": "SYNTAX_ERROR", "file": self.filename,
                     "line": 0, "name": "", "severity": "error",
                     "message": self._parse_error}]

        violations: List[Dict] = []

        # Module docstring
        if not ast.get_docstring(self._tree):
            violations.append(self._v("MISSING_MODULE_DOCSTRING", self.filename, 1, "", "warning"))

        for node in ast.walk(self._tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    violations.append(self._v(
                        "MISSING_FUNCTION_DOCSTRING", self.filename,
                        node.lineno, node.name, "warning"
                    ))
                else:
                    doc = ast.get_docstring(node)
                    style_issues = self._check_docstring_style(doc, node.name)
                    violations.extend(style_issues)

            elif isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    violations.append(self._v(
                        "MISSING_CLASS_DOCSTRING", self.filename,
                        node.lineno, node.name, "warning"
                    ))

        self._violations = violations
        return violations

    def is_valid(self) -> bool:
        """Return True if no violations were found.

        Returns:
            bool: True when the source passes all checks.
        """
        return len(self.validate()) == 0

    def missing_functions(self) -> List[str]:
        """Return names of functions missing docstrings.

        Returns:
            list[str]: Function names without docstrings.
        """
        return [
            v["name"] for v in self.validate()
            if v["rule"] == "MISSING_FUNCTION_DOCSTRING"
        ]

    def has_module_docstring(self) -> bool:
        """Check whether a module-level docstring is present.

        Returns:
            bool: True if the module has a docstring.
        """
        if self._tree is None:
            return False
        return bool(ast.get_docstring(self._tree))

    def summary(self) -> Dict[str, Any]:
        """Return a summary dict of validation results.

        Returns:
            dict: total_violations, missing_functions, missing_classes,
                  has_module_doc, is_valid.
        """
        violations = self.validate()
        return {
            "total_violations": len(violations),
            "missing_functions": len([v for v in violations if v["rule"] == "MISSING_FUNCTION_DOCSTRING"]),
            "missing_classes": len([v for v in violations if v["rule"] == "MISSING_CLASS_DOCSTRING"]),
            "has_module_doc": self.has_module_docstring(),
            "is_valid": self.is_valid(),
        }

    def rule_counts(self) -> Dict[str, int]:
        """Return violation counts grouped by rule type.

        Returns:
            dict: Rule name → count.
        """
        counts: Dict[str, int] = {}
        for v in self.validate():
            counts[v["rule"]] = counts.get(v["rule"], 0) + 1
        return counts

    # ── Private helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _v(rule: str, file: str, line: int, name: str, severity: str) -> Dict:
        """Construct a violation dict.

        Args:
            rule (str): Violation rule code.
            file (str): Filename.
            line (int): Line number.
            name (str): Entity name (function or class).
            severity (str): 'error' or 'warning'.

        Returns:
            dict: Violation record.
        """
        return {"rule": rule, "file": file, "line": line,
                "name": name, "severity": severity}

    @staticmethod
    def _check_docstring_style(doc: str, name: str) -> List[Dict]:
        """Perform basic PEP 257 style checks on an existing docstring.

        Args:
            doc (str): Docstring text (without triple quotes).
            name (str): Function or class name.

        Returns:
            list[dict]: Zero or more style violations.
        """
        issues = []
        lines = doc.strip().splitlines()
        if lines and not lines[0].strip():
            issues.append({"rule": "DOCSTRING_STARTS_WITH_BLANK_LINE",
                           "file": "", "line": 0, "name": name, "severity": "info"})
        if lines and not lines[0][0].isupper():
            issues.append({"rule": "DOCSTRING_NOT_CAPITALIZED",
                           "file": "", "line": 0, "name": name, "severity": "info"})
        if lines and not lines[-1].strip().endswith("."):
            issues.append({"rule": "DOCSTRING_MISSING_PERIOD",
                           "file": "", "line": 0, "name": name, "severity": "info"})
        return issues
