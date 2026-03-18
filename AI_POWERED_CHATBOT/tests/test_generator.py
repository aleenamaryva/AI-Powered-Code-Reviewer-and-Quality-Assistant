# tests/test_generator.py
"""Unit tests for core.docstring_engine.generator."""

import pytest
from core.docstring_engine.generator import (
    generate_docstring,
    build_description,
    smart_description,
    _words,
    _humanize,
    VERB_MAP,
)


# ── _words / _humanize ─────────────────────────────────────────────────────────

class TestWords:
    def test_snake_case(self):
        assert _words("get_user_name") == ["get", "user", "name"]

    def test_camel_case(self):
        assert _words("getUserName") == ["get", "user", "name"]

    def test_single_word(self):
        assert _words("parse") == ["parse"]

    def test_empty(self):
        assert _words("") == []


class TestHumanize:
    def test_snake(self):
        assert _humanize("find_max") == "find max"

    def test_camel(self):
        assert _humanize("calculateAverage") == "calculate average"


# ── smart_description ──────────────────────────────────────────────────────────

class TestSmartDescription:
    def test_known_verb(self):
        desc = smart_description("get_user", ["self", "user_id"])
        assert "Retrieves" in desc

    def test_ends_with_period(self):
        desc = smart_description("calculate_sum", ["a", "b"])
        assert desc.endswith(".")

    def test_empty_name_fallback(self):
        desc = smart_description("", [])
        assert "Performs the" in desc or desc.endswith(".")

    def test_includes_arg_names(self):
        desc = smart_description("process_data", ["input_data"])
        assert "`input_data`" in desc


# ── build_description ──────────────────────────────────────────────────────────

class TestBuildDescription:
    def _func(self, name, args=None, arg_types=None, return_type="", body_lines=None):
        return {
            "name": name,
            "args": args or [],
            "arg_types": arg_types or {},
            "return_type": return_type,
            "body_lines": body_lines or [],
        }

    def test_basic_verb_mapping(self):
        desc = build_description(self._func("get_config"))
        assert "Retrieves" in desc or "Gets" in desc

    def test_return_type_included(self):
        desc = build_description(self._func("fetch_data", return_type="list"))
        assert "list" in desc

    def test_file_io_annotation(self):
        desc = build_description(self._func("read_data", body_lines=["with open(path) as f:"]))
        assert "file I/O" in desc.lower() or "Performs" in desc

    def test_network_annotation(self):
        desc = build_description(self._func("send_request", body_lines=["import requests"]))
        assert "network" in desc.lower() or "Sends" in desc

    def test_ends_with_period(self):
        desc = build_description(self._func("validate_input"))
        assert desc.endswith(".")

    def test_capitalized(self):
        desc = build_description(self._func("run_task"))
        assert desc[0].isupper()


# ── generate_docstring ─────────────────────────────────────────────────────────

class TestGenerateDocstring:
    def _func(self, name="my_func", args=None, arg_types=None, return_type="str"):
        return {
            "name": name,
            "args": args or ["x", "y"],
            "arg_types": arg_types or {"x": "int", "y": "int"},
            "return_type": return_type,
            "body_lines": [],
        }

    def test_google_style_sections(self):
        doc = generate_docstring(self._func(), "GOOGLE")
        assert "Args:" in doc
        assert "Returns:" in doc

    def test_numpy_style_sections(self):
        doc = generate_docstring(self._func(), "NUMPY")
        assert "Parameters" in doc
        assert "Returns" in doc
        assert "----------" in doc

    def test_rest_style_params(self):
        doc = generate_docstring(self._func(), "reST")
        assert ":param x:" in doc
        assert ":param y:" in doc

    def test_google_has_triple_quotes(self):
        doc = generate_docstring(self._func(), "GOOGLE")
        assert '"""' in doc

    def test_self_cls_excluded(self):
        func = self._func(args=["self", "value"], arg_types={"value": "str"})
        doc = generate_docstring(func, "GOOGLE")
        assert "self" not in doc

    def test_numpy_no_filtered_args_when_only_self(self):
        func = self._func(args=["self"], arg_types={}, return_type="None")
        doc = generate_docstring(func, "NUMPY")
        assert "Parameters" in doc  # section still rendered

    def test_rest_type_annotation(self):
        doc = generate_docstring(self._func(), "reST")
        assert ":type x: int" in doc

import pytest
from core.docstring_engine.generator import (
    generate_docstring,
    build_description,
    smart_description,
    _words,
    _humanize,
)

# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def simple_func():
    return {
        "name": "calculate_average",
        "args": ["numbers"],
        "arg_types": {"numbers": "list"},
        "return_type": "float",
        "body_lines": ["total = sum(numbers)", "return total / len(numbers)"],
        "has_doc": False,
        "docstring": "",
    }


@pytest.fixture
def no_arg_func():
    return {
        "name": "get_version",
        "args": [],
        "arg_types": {},
        "return_type": "str",
        "body_lines": ["return '1.0.0'"],
        "has_doc": False,
        "docstring": "",
    }


@pytest.fixture
def self_func():
    return {
        "name": "save_data",
        "args": ["self", "data", "path"],
        "arg_types": {"data": "dict", "path": "str"},
        "return_type": "None",
        "body_lines": ["with open(path, 'w') as f:", "json.dump(data, f)"],
        "has_doc": False,
        "docstring": "",
    }


# ── _words ─────────────────────────────────────────────────────────────────────

class TestWords:
    def test_snake_case(self):
        assert _words("get_user_name") == ["get", "user", "name"]

    def test_camel_case(self):
        assert _words("getUserName") == ["get", "user", "name"]

    def test_single_word(self):
        assert _words("parse") == ["parse"]

    def test_empty(self):
        assert _words("") == []


# ── _humanize ─────────────────────────────────────────────────────────────────

class TestHumanize:
    def test_snake(self):
        assert _humanize("calculate_average") == "calculate average"

    def test_camel(self):
        assert _humanize("getUserName") == "get user name"


# ── smart_description ─────────────────────────────────────────────────────────

class TestSmartDescription:
    def test_known_verb(self):
        desc = smart_description("get_user", ["user_id"])
        assert desc.startswith("Retrieves")

    def test_ends_with_period(self):
        desc = smart_description("parse_json", ["text"])
        assert desc.endswith(".")

    def test_includes_args(self):
        desc = smart_description("validate_email", ["email"])
        assert "`email`" in desc

    def test_unknown_verb(self):
        desc = smart_description("xyz_operation", ["data"])
        assert "xyz" in desc.lower() or "Performs" in desc


# ── build_description ─────────────────────────────────────────────────────────

class TestBuildDescription:
    def test_returns_string(self, simple_func):
        assert isinstance(build_description(simple_func), str)

    def test_starts_with_capital(self, simple_func):
        desc = build_description(simple_func)
        assert desc[0].isupper()

    def test_ends_with_period(self, simple_func):
        assert build_description(simple_func).endswith(".")

    def test_file_io_detected(self, self_func):
        desc = build_description(self_func)
        assert "I/O" in desc or "file" in desc.lower()

    def test_no_args_func(self, no_arg_func):
        desc = build_description(no_arg_func)
        assert isinstance(desc, str) and len(desc) > 0


# ── generate_docstring — GOOGLE ───────────────────────────────────────────────

class TestGenerateDocstringGoogle:
    def test_contains_args_section(self, simple_func):
        doc = generate_docstring(simple_func, "GOOGLE")
        assert "Args:" in doc

    def test_contains_returns_section(self, simple_func):
        doc = generate_docstring(simple_func, "GOOGLE")
        assert "Returns:" in doc

    def test_arg_listed(self, simple_func):
        doc = generate_docstring(simple_func, "GOOGLE")
        assert "numbers" in doc

    def test_wrapped_in_quotes(self, simple_func):
        doc = generate_docstring(simple_func, "GOOGLE")
        assert doc.startswith('"""')
        assert doc.endswith('"""')

    def test_self_excluded(self, self_func):
        doc = generate_docstring(self_func, "GOOGLE")
        assert "self" not in doc


# ── generate_docstring — NUMPY ────────────────────────────────────────────────

class TestGenerateDocstringNumpy:
    def test_parameters_section(self, simple_func):
        doc = generate_docstring(simple_func, "NUMPY")
        assert "Parameters" in doc

    def test_returns_section(self, simple_func):
        doc = generate_docstring(simple_func, "NUMPY")
        assert "Returns" in doc

    def test_dashes_present(self, simple_func):
        doc = generate_docstring(simple_func, "NUMPY")
        assert "----------" in doc or "-------" in doc


# ── generate_docstring — reST ─────────────────────────────────────────────────

class TestGenerateDocstringReST:
    def test_param_directive(self, simple_func):
        doc = generate_docstring(simple_func, "reST")
        assert ":param" in doc

    def test_type_directive(self, simple_func):
        doc = generate_docstring(simple_func, "reST")
        assert ":type" in doc

    def test_rtype_directive(self, simple_func):
        doc = generate_docstring(simple_func, "reST")
        assert ":rtype:" in doc

    def test_no_args_no_param(self, no_arg_func):
        doc = generate_docstring(no_arg_func, "reST")
        assert ":param" not in doc
