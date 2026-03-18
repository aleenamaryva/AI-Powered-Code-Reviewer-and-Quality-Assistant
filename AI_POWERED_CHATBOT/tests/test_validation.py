# tests/test_validation.py
"""Unit tests for core.validator.validator.CodeValidator."""

import textwrap
import pytest
from core.validator.validator import CodeValidator


# ── Fixtures ───────────────────────────────────────────────────────────────────

WELL_DOCUMENTED = textwrap.dedent('''\
    """Module docstring."""

    def add(a, b):
        """Add two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            int: Sum.
        """
        return a + b

    class Calculator:
        """A simple calculator."""

        def multiply(self, x, y):
            """Multiply two numbers."""
            return x * y
''')

UNDOCUMENTED = textwrap.dedent("""\
    def add(a, b):
        return a + b

    def subtract(a, b):
        return a - b

    class Box:
        def area(self):
            return 0
""")

SYNTAX_ERROR = "def broken(:\n    pass"


# ── Instantiation ──────────────────────────────────────────────────────────────

class TestInit:
    def test_no_parse_error_on_valid_source(self):
        v = CodeValidator(WELL_DOCUMENTED)
        assert not v.has_parse_error

    def test_parse_error_on_invalid_source(self):
        v = CodeValidator(SYNTAX_ERROR)
        assert v.has_parse_error
        assert v.parse_error is not None


# ── validate ──────────────────────────────────────────────────────────────────

class TestValidate:
    def test_no_violations_on_well_documented(self):
        v = CodeValidator(WELL_DOCUMENTED)
        violations = v.validate()
        rule_names = [viol["rule"] for viol in violations]
        assert "MISSING_FUNCTION_DOCSTRING" not in rule_names
        assert "MISSING_MODULE_DOCSTRING" not in rule_names

    def test_detects_missing_function_docstrings(self):
        v = CodeValidator(UNDOCUMENTED)
        rules = [viol["rule"] for viol in v.validate()]
        assert "MISSING_FUNCTION_DOCSTRING" in rules

    def test_detects_missing_module_docstring(self):
        v = CodeValidator(UNDOCUMENTED)
        rules = [viol["rule"] for viol in v.validate()]
        assert "MISSING_MODULE_DOCSTRING" in rules

    def test_detects_missing_class_docstring(self):
        v = CodeValidator(UNDOCUMENTED)
        rules = [viol["rule"] for viol in v.validate()]
        assert "MISSING_CLASS_DOCSTRING" in rules

    def test_syntax_error_returns_syntax_violation(self):
        v = CodeValidator(SYNTAX_ERROR)
        violations = v.validate()
        assert violations[0]["rule"] == "SYNTAX_ERROR"

    def test_violation_structure(self):
        v = CodeValidator(UNDOCUMENTED)
        for viol in v.validate():
            assert "rule" in viol
            assert "file" in viol
            assert "severity" in viol


# ── is_valid ──────────────────────────────────────────────────────────────────

class TestIsValid:
    def test_valid_when_fully_documented(self):
        v = CodeValidator(WELL_DOCUMENTED)
        assert v.is_valid()

    def test_invalid_when_undocumented(self):
        v = CodeValidator(UNDOCUMENTED)
        assert not v.is_valid()


# ── missing_functions ──────────────────────────────────────────────────────────

class TestMissingFunctions:
    def test_returns_names(self):
        v = CodeValidator(UNDOCUMENTED)
        missing = v.missing_functions()
        assert "add" in missing
        assert "subtract" in missing

    def test_empty_when_all_documented(self):
        v = CodeValidator(WELL_DOCUMENTED)
        assert v.missing_functions() == []


# ── has_module_docstring ──────────────────────────────────────────────────────

class TestHasModuleDocstring:
    def test_present(self):
        v = CodeValidator(WELL_DOCUMENTED)
        assert v.has_module_docstring()

    def test_absent(self):
        v = CodeValidator(UNDOCUMENTED)
        assert not v.has_module_docstring()


# ── summary ───────────────────────────────────────────────────────────────────

class TestSummary:
    def test_keys_present(self):
        v = CodeValidator(UNDOCUMENTED)
        s = v.summary()
        for key in ("total_violations", "missing_functions", "missing_classes", "has_module_doc", "is_valid"):
            assert key in s

    def test_missing_count_undocumented(self):
        v = CodeValidator(UNDOCUMENTED)
        s = v.summary()
        assert s["missing_functions"] == 3
        assert s["missing_classes"] == 1
        assert s["has_module_doc"] is False

    def test_fully_documented(self):
        v = CodeValidator(WELL_DOCUMENTED)
        s = v.summary()
        assert s["missing_functions"] == 0
        assert s["is_valid"] is True


# ── rule_counts ───────────────────────────────────────────────────────────────

class TestRuleCounts:
    def test_counts_by_rule(self):
        v = CodeValidator(UNDOCUMENTED)
        counts = v.rule_counts()
        assert counts.get("MISSING_FUNCTION_DOCSTRING", 0) == 3
        assert counts.get("MISSING_CLASS_DOCSTRING", 0) == 1

import textwrap
import pytest
from core.validator.validator import CodeValidator

# ── Source fixtures ────────────────────────────────────────────────────────────

FULLY_DOCUMENTED = textwrap.dedent('''\
    """Module docstring."""


    def add(a, b):
        """Add two numbers.

        Args:
            a: First operand.
            b: Second operand.

        Returns:
            Sum of a and b.
        """
        return a + b


    class Greeter:
        """A greeter class."""

        def greet(self, name: str) -> str:
            """Return a greeting string.

            Args:
                name (str): Person to greet.

            Returns:
                str: Greeting sentence.
            """
            return f"Hello, {name}!"
''')

MISSING_DOCS = textwrap.dedent('''\
    def add(a, b):
        return a + b

    def subtract(x, y):
        return x - y

    class Foo:
        def method(self):
            pass
''')

SYNTAX_ERROR_SRC = "def broken(:"

MODULE_DOC_ONLY = textwrap.dedent('''\
    """This module does things."""


    def undocumented():
        pass
''')


# ── Parsing behaviour ─────────────────────────────────────────────────────────

class TestParsing:
    def test_valid_source_no_parse_error(self):
        v = CodeValidator(FULLY_DOCUMENTED)
        assert v.has_parse_error is False

    def test_syntax_error_detected(self):
        v = CodeValidator(SYNTAX_ERROR_SRC)
        assert v.has_parse_error is True
        assert v.parse_error is not None

    def test_validate_on_syntax_error_returns_violation(self):
        v = CodeValidator(SYNTAX_ERROR_SRC)
        violations = v.validate()
        assert any(viol["rule"] == "SYNTAX_ERROR" for viol in violations)


# ── Module docstring ──────────────────────────────────────────────────────────

class TestModuleDocstring:
    def test_present(self):
        v = CodeValidator(FULLY_DOCUMENTED)
        assert v.has_module_docstring() is True

    def test_absent(self):
        v = CodeValidator(MISSING_DOCS)
        assert v.has_module_docstring() is False

    def test_missing_generates_violation(self):
        v = CodeValidator(MISSING_DOCS)
        rules = [viol["rule"] for viol in v.validate()]
        assert "MISSING_MODULE_DOCSTRING" in rules


# ── Function docstrings ───────────────────────────────────────────────────────

class TestFunctionDocstrings:
    def test_fully_documented_no_missing(self):
        v = CodeValidator(FULLY_DOCUMENTED)
        assert v.missing_functions() == []

    def test_missing_two_functions(self):
        v = CodeValidator(MISSING_DOCS)
        missing = v.missing_functions()
        assert "add" in missing
        assert "subtract" in missing

    def test_missing_method(self):
        v = CodeValidator(MISSING_DOCS)
        missing = v.missing_functions()
        assert "method" in missing

    def test_violation_rule_name(self):
        v = CodeValidator(MISSING_DOCS)
        rules = [viol["rule"] for viol in v.validate()]
        assert "MISSING_FUNCTION_DOCSTRING" in rules


# ── Class docstrings ──────────────────────────────────────────────────────────

class TestClassDocstrings:
    def test_missing_class_doc_violation(self):
        v = CodeValidator(MISSING_DOCS)
        rules = [viol["rule"] for viol in v.validate()]
        assert "MISSING_CLASS_DOCSTRING" in rules

    def test_documented_class_no_violation(self):
        v = CodeValidator(FULLY_DOCUMENTED)
        class_viols = [viol for viol in v.validate() if viol["rule"] == "MISSING_CLASS_DOCSTRING"]
        assert class_viols == []


# ── is_valid ──────────────────────────────────────────────────────────────────

class TestIsValid:
    def test_fully_documented_is_valid(self):
        v = CodeValidator(FULLY_DOCUMENTED)
        assert v.is_valid() is True

    def test_missing_docs_not_valid(self):
        v = CodeValidator(MISSING_DOCS)
        assert v.is_valid() is False


# ── summary ───────────────────────────────────────────────────────────────────

class TestSummary:
    def test_summary_keys(self):
        v = CodeValidator(MISSING_DOCS)
        s = v.summary()
        assert "total_violations" in s
        assert "missing_functions" in s
        assert "missing_classes" in s
        assert "has_module_doc" in s
        assert "is_valid" in s

    def test_summary_counts(self):
        v = CodeValidator(MISSING_DOCS)
        s = v.summary()
        assert s["missing_functions"] >= 2
        assert s["has_module_doc"] is False
        assert s["is_valid"] is False

    def test_fully_documented_summary(self):
        v = CodeValidator(FULLY_DOCUMENTED)
        s = v.summary()
        assert s["is_valid"] is True
        assert s["missing_functions"] == 0


# ── rule_counts ───────────────────────────────────────────────────────────────

class TestRuleCounts:
    def test_returns_dict(self):
        v = CodeValidator(MISSING_DOCS)
        rc = v.rule_counts()
        assert isinstance(rc, dict)

    def test_missing_function_counted(self):
        v = CodeValidator(MISSING_DOCS)
        rc = v.rule_counts()
        assert rc.get("MISSING_FUNCTION_DOCSTRING", 0) >= 2

    def test_empty_for_valid_code(self):
        v = CodeValidator(FULLY_DOCUMENTED)
        assert v.rule_counts() == {}


# ── module-doc-only edge case ─────────────────────────────────────────────────

class TestModuleDocOnly:
    def test_module_doc_detected(self):
        v = CodeValidator(MODULE_DOC_ONLY)
        assert v.has_module_docstring() is True

    def test_undocumented_function_detected(self):
        v = CodeValidator(MODULE_DOC_ONLY)
        assert "undocumented" in v.missing_functions()
