# core/parser/__init__.py
from .python_parser import analyze_code, extract_functions, inject_docstring

__all__ = ["analyze_code", "extract_functions", "inject_docstring"]
