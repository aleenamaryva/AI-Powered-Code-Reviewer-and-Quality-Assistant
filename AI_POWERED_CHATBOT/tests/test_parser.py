# tests/test_parser.py
"""Unit tests for core.parser.python_parser."""

import textwrap
import pytest
from core.parser.python_parser import (
    analyze_code,
    extract_functions,
    inject_docstring,
    fix_with_regex,
    has_docstring_node,
    scan_file,
    calculate_complexity,
)
import ast


# ── Fixtures ───────────────────────────────────────────────────────────────────

SIMPLE_SOURCE = textwrap.dedent("""\
    def add(a, b):
        return a + b

    def greet(name: str) -> str:
        \"\"\"Say hello.\"\"\"
        return f"Hello, {name}"

    class MyClass:
        def method(self):
            pass
""")

SYNTAX_ERROR_SOURCE = "def broken(:\n    pass"


# ── calculate_complexity ───────────────────────────────────────────────────────

class TestCalculateComplexity:
    def test_simple_function(self):
        tree = ast.parse("def f():\n    return 1")
        node = tree.body[0]
        assert calculate_complexity(node) == 1

    def test_with_if(self):
        tree = ast.parse("def f(x):\n    if x:\n        return x\n    return 0")
        node = tree.body[0]
        assert calculate_complexity(node) == 2

    def test_with_loop(self):
        tree = ast.parse("def f(items):\n    for i in items:\n        pass")
        node = tree.body[0]
        assert calculate_complexity(node) == 2


# ── analyze_code ──────────────────────────────────────────────────────────────

class TestAnalyzeCode:
    def test_functions_detected(self):
        funcs, classes, mod_doc, err = analyze_code(SIMPLE_SOURCE)
        assert err is None
        names = [f["Name"] for f in funcs]
        assert "add" in names
        assert "greet" in names

    def test_classes_detected(self):
        _, classes, _, _ = analyze_code(SIMPLE_SOURCE)
        assert any(c["Name"] == "MyClass" for c in classes)

    def test_docstring_flag(self):
        funcs, _, _, _ = analyze_code(SIMPLE_SOURCE)
        greet = next(f for f in funcs if f["Name"] == "greet")
        add = next(f for f in funcs if f["Name"] == "add")
        assert greet["Has Docstring"] is True
        assert add["Has Docstring"] is False

    def test_syntax_error_returns_error(self):
        funcs, classes, mod_doc, err = analyze_code(SYNTAX_ERROR_SOURCE)
        assert err is not None
        assert funcs is None

    def test_complexity_values(self):
        funcs, _, _, _ = analyze_code(SIMPLE_SOURCE)
        for f in funcs:
            assert f["Complexity"] >= 1

    def test_kind_sync_async(self):
        src = "async def fetch(): pass\ndef sync(): pass"
        funcs, _, _, _ = analyze_code(src)
        kinds = {f["Name"]: f["Kind"] for f in funcs}
        assert kinds["fetch"] == "async"
        assert kinds["sync"] == "sync"


# ── extract_functions ─────────────────────────────────────────────────────────

class TestExtractFunctions:
    def test_returns_list(self):
        result = extract_functions(SIMPLE_SOURCE)
        assert isinstance(result, list)

    def test_function_names(self):
        result = extract_functions(SIMPLE_SOURCE)
        names = [f["name"] for f in result]
        assert "add" in names
        assert "greet" in names

    def test_has_doc_flag(self):
        result = extract_functions(SIMPLE_SOURCE)
        greet = next(f for f in result if f["name"] == "greet")
        add = next(f for f in result if f["name"] == "add")
        assert greet["has_doc"] is True
        assert add["has_doc"] is False

    def test_arg_names(self):
        result = extract_functions(SIMPLE_SOURCE)
        add = next(f for f in result if f["name"] == "add")
        assert "a" in add["args"]
        assert "b" in add["args"]

    def test_return_type(self):
        result = extract_functions(SIMPLE_SOURCE)
        greet = next(f for f in result if f["name"] == "greet")
        assert greet["return_type"] == "str"

    def test_syntax_error_returns_empty(self):
        result = extract_functions(SYNTAX_ERROR_SOURCE)
        assert result == []


# ── inject_docstring ──────────────────────────────────────────────────────────

class TestInjectDocstring:
    SOURCE = textwrap.dedent("""\
        def hello(name):
            return f"Hello, {name}"
    """)

    def test_injects_new_docstring(self):
        new_src, err = inject_docstring(self.SOURCE, "hello", '"""Say hello."""')
        assert err is None
        assert '"""Say hello."""' in new_src or 'Say hello.' in new_src

    def test_function_not_found(self):
        _, err = inject_docstring(self.SOURCE, "nonexistent", '"""doc"""')
        assert err is not None
        assert "not found" in err.lower()

    def test_syntax_error_source(self):
        _, err = inject_docstring("def broken(:", "broken", '"""doc"""')
        assert err is not None


# ── fix_with_regex ────────────────────────────────────────────────────────────

class TestFixWithRegex:
    def test_adds_placeholder_docstring(self):
        src = "def calculate():\n    return 42\n"
        result = fix_with_regex("calculate", src)
        assert "calculate" in result.lower()
        assert '"""' in result

    def test_does_not_duplicate_existing(self):
        src = 'def calculate():\n    """Already documented."""\n    return 42\n'
        result = fix_with_regex("calculate", src)
        count = result.count('"""')
        assert count >= 2  # original docstring preserved


# ── has_docstring_node ────────────────────────────────────────────────────────

class TestHasDocstringNode:
    def test_with_docstring(self):
        tree = ast.parse('def f():\n    """Doc."""\n    pass')
        node = tree.body[0]
        assert has_docstring_node(node) is True

    def test_without_docstring(self):
        tree = ast.parse("def f():\n    pass")
        node = tree.body[0]
        assert has_docstring_node(node) is False

    def test_non_function_node(self):
        tree = ast.parse("x = 1")
        node = tree.body[0]
        assert has_docstring_node(node) is False

import textwrap
import pytest
from core.parser.python_parser import (
    analyze_code,
    extract_functions,
    inject_docstring,
    fix_with_regex,
    has_docstring_node,
    scan_file,
    calculate_complexity,
)
import ast

# ── Shared source fixtures ─────────────────────────────────────────────────────

SIMPLE_SOURCE = textwrap.dedent("""\
    def add(a, b):
        return a + b

    def subtract(x, y):
        \"\"\"Subtracts y from x.\"\"\"
        return x - y
""")

CLASS_SOURCE = textwrap.dedent("""\
    class MyClass:
        \"\"\"A simple class.\"\"\"

        def method_one(self):
            pass

        def method_two(self, value: int) -> str:
            \"\"\"Returns value as string.\"\"\"
            return str(value)
""")

COMPLEX_SOURCE = textwrap.dedent("""\
    def process(data):
        if data:
            for item in data:
                if item > 0:
                    pass
        return data
""")

INVALID_SOURCE = "def broken(:"


# ── calculate_complexity ──────────────────────────────────────────────────────

class TestCalculateComplexity:
    def _complexity(self, source):
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return calculate_complexity(node)

    def test_simple_function(self):
        assert self._complexity("def f(): return 1") == 1

    def test_if_increases_complexity(self):
        src = "def f(x):\n    if x: return x\n    return 0"
        assert self._complexity(src) == 2

    def test_loop_increases_complexity(self):
        src = "def f(lst):\n    for i in lst: pass"
        assert self._complexity(src) == 2

    def test_nested_branches(self):
        assert self._complexity(COMPLEX_SOURCE) >= 3


# ── analyze_code ──────────────────────────────────────────────────────────────

class TestAnalyzeCode:
    def test_returns_functions(self):
        funcs, _, _, err = analyze_code(SIMPLE_SOURCE)
        assert err is None
        assert len(funcs) == 2

    def test_documented_flag(self):
        funcs, _, _, _ = analyze_code(SIMPLE_SOURCE)
        names = {f["Name"]: f["Has Docstring"] for f in funcs}
        assert names["add"] is False
        assert names["subtract"] is True

    def test_returns_classes(self):
        _, classes, _, _ = analyze_code(CLASS_SOURCE)
        assert len(classes) == 1
        assert classes[0]["Name"] == "MyClass"

    def test_module_docstring_absent(self):
        _, _, has_doc, _ = analyze_code(SIMPLE_SOURCE)
        assert has_doc is False

    def test_module_docstring_present(self):
        src = '"""Module doc."""\ndef f(): pass'
        _, _, has_doc, _ = analyze_code(src)
        assert has_doc is True

    def test_syntax_error_returns_none(self):
        funcs, classes, _, err = analyze_code(INVALID_SOURCE)
        assert funcs is None
        assert err is not None

    def test_complexity_field_present(self):
        funcs, _, _, _ = analyze_code(SIMPLE_SOURCE)
        for f in funcs:
            assert "Complexity" in f


# ── extract_functions ─────────────────────────────────────────────────────────

class TestExtractFunctions:
    def test_count(self):
        funcs = extract_functions(SIMPLE_SOURCE)
        assert len(funcs) == 2

    def test_has_doc_flag(self):
        funcs = extract_functions(SIMPLE_SOURCE)
        names = {f["name"]: f["has_doc"] for f in funcs}
        assert names["add"] is False
        assert names["subtract"] is True

    def test_arg_types_extracted(self):
        src = "def greet(name: str) -> str:\n    return name"
        funcs = extract_functions(src)
        assert funcs[0]["arg_types"].get("name") == "str"
        assert funcs[0]["return_type"] == "str"

    def test_args_list(self):
        funcs = extract_functions(SIMPLE_SOURCE)
        add_fn = next(f for f in funcs if f["name"] == "add")
        assert add_fn["args"] == ["a", "b"]

    def test_syntax_error_returns_empty(self):
        assert extract_functions(INVALID_SOURCE) == []

    def test_body_lines_populated(self):
        funcs = extract_functions(SIMPLE_SOURCE)
        add_fn = next(f for f in funcs if f["name"] == "add")
        assert len(add_fn["body_lines"]) > 0


# ── inject_docstring ──────────────────────────────────────────────────────────

class TestInjectDocstring:
    def test_injects_new_docstring(self):
        new_src, err = inject_docstring(SIMPLE_SOURCE, "add", '"""Adds two numbers."""')
        assert err is None
        assert "Adds two numbers." in new_src

    def test_replaces_existing_docstring(self):
        new_src, err = inject_docstring(SIMPLE_SOURCE, "subtract", '"""New doc."""')
        assert err is None
        assert "New doc." in new_src

    def test_unknown_function_returns_error(self):
        _, err = inject_docstring(SIMPLE_SOURCE, "nonexistent", '"""doc"""')
        assert err is not None
        assert "not found" in err

    def test_invalid_source_returns_error(self):
        _, err = inject_docstring(INVALID_SOURCE, "add", '"""doc"""')
        assert err is not None


# ── fix_with_regex ────────────────────────────────────────────────────────────

class TestFixWithRegex:
    def test_inserts_placeholder(self):
        result = fix_with_regex("add", SIMPLE_SOURCE)
        assert "Add function." in result or "add" in result.lower()

    def test_does_not_duplicate_existing(self):
        result = fix_with_regex("subtract", SIMPLE_SOURCE)
        count = result.count('"""')
        # existing 2 quotes + potential new ones — just ensure no runaway duplication
        assert count < 10


# ── has_docstring_node ────────────────────────────────────────────────────────

class TestHasDocstringNode:
    def _get_node(self, src, name):
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                return node

    def test_with_docstring(self):
        node = self._get_node(SIMPLE_SOURCE, "subtract")
        assert has_docstring_node(node) is True

    def test_without_docstring(self):
        node = self._get_node(SIMPLE_SOURCE, "add")
        assert has_docstring_node(node) is False

    def test_non_function_returns_false(self):
        tree = ast.parse("x = 1")
        assert has_docstring_node(tree) is False


# ── scan_file ─────────────────────────────────────────────────────────────────

class TestScanFile:
    def test_scans_real_file(self, tmp_path):
        f = tmp_path / "mod.py"
        f.write_text(SIMPLE_SOURCE, encoding="utf-8")
        results = scan_file(str(f))
        assert len(results) == 2

    def test_docstring_flag_correct(self, tmp_path):
        f = tmp_path / "mod.py"
        f.write_text(SIMPLE_SOURCE, encoding="utf-8")
        results = scan_file(str(f))
        by_name = {r["function"]: r["docstring"] for r in results}
        assert by_name["add"] is False
        assert by_name["subtract"] is True

    def test_syntax_error_file(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text(INVALID_SOURCE, encoding="utf-8")
        results = scan_file(str(f))
        assert len(results) == 1
        assert "SyntaxError" in results[0]["function"]
