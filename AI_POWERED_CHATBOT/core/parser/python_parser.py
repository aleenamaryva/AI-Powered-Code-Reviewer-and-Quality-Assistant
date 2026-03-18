# core/parser/python_parser.py
"""AST-based Python source parser for function and class metadata extraction."""

from __future__ import annotations
import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional

FUNCTION_NODE_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)


# ── Complexity ─────────────────────────────────────────────────────────────────

def calculate_complexity(node: ast.AST) -> int:
    """Compute cyclomatic-style complexity for a function or class node.

    Counts branching constructs: if, for, while, try, with, bool operations.

    Args:
        node (ast.AST): The AST node to analyse.

    Returns:
        int: Complexity score (minimum 1).
    """
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.While,
                               ast.Try, ast.With, ast.BoolOp)):
            complexity += 1
    return complexity


# ── Core analysis ──────────────────────────────────────────────────────────────

def analyze_code(
    code: str,
) -> Tuple[Optional[List[Dict]], Optional[List[Dict]], bool, Optional[str]]:
    """Parse Python source and return function/class metadata plus module docstring flag.

    Args:
        code (str): Raw Python source code string.

    Returns:
        tuple: (functions, classes, has_module_docstring, error_message)
               functions and classes are lists of metadata dicts, or None on error.
               error_message is None on success.
    """
    try:
        tree = ast.parse(code)
    except Exception as e:
        return None, None, False, str(e)

    functions, classes = [], []
    module_docstring = ast.get_docstring(tree) is not None

    for node in ast.walk(tree):
        if isinstance(node, FUNCTION_NODE_TYPES):
            functions.append({
                "Name": node.name,
                "Type": "Function",
                "Kind": "async" if isinstance(node, ast.AsyncFunctionDef) else "sync",
                "Start Line": node.lineno,
                "End Line": node.end_lineno,
                "Complexity": calculate_complexity(node),
                "Has Docstring": ast.get_docstring(node) is not None,
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "Name": node.name,
                "Type": "Class",
                "Start Line": node.lineno,
                "End Line": node.end_lineno,
                "Complexity": calculate_complexity(node),
                "Has Docstring": ast.get_docstring(node) is not None,
            })

    return functions, classes, module_docstring, None


def extract_functions(source: str) -> List[Dict[str, Any]]:
    """Extract detailed metadata for every function defined in source.

    Includes argument names, type annotations, return type, docstring,
    and a cleaned list of body statement lines.

    Args:
        source (str): Python source code.

    Returns:
        list[dict]: List of function metadata dicts.
    """
    funcs = []
    src_lines = source.splitlines()
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, FUNCTION_NODE_TYPES):
                doc = ast.get_docstring(node) or ""
                args = [a.arg for a in node.args.args]
                arg_types: Dict[str, str] = {}
                for a in node.args.args:
                    if a.annotation:
                        try:
                            arg_types[a.arg] = ast.unparse(a.annotation)
                        except Exception:
                            pass
                return_type = ""
                if node.returns:
                    try:
                        return_type = ast.unparse(node.returns)
                    except Exception:
                        pass
                start = node.body[0].lineno - 1
                end = getattr(node, "end_lineno", start + 10)
                body_lines = [
                    l.strip() for l in src_lines[start:end]
                    if l.strip()
                    and not l.strip().startswith('"""')
                    and not l.strip().startswith("'''")
                ]
                funcs.append({
                    "name": node.name,
                    "args": args,
                    "lineno": node.lineno,
                    "docstring": doc,
                    "has_doc": bool(doc.strip()),
                    "arg_types": arg_types,
                    "return_type": return_type,
                    "body_lines": body_lines,
                })
    except SyntaxError:
        pass
    return funcs


# ── Docstring injection ────────────────────────────────────────────────────────

def inject_docstring(
    source: str, func_name: str, new_doc_raw: str
) -> Tuple[str, Optional[str]]:
    """Inject or replace a docstring for a named function inside source code.

    Args:
        source (str): Full source code of the file.
        func_name (str): Target function name.
        new_doc_raw (str): New docstring text (with or without enclosing quotes).

    Returns:
        tuple: (updated_source, error_message).
               error_message is None on success.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source, "SyntaxError: could not parse file"

    lines = source.splitlines(keepends=True)
    for node in ast.walk(tree):
        if isinstance(node, FUNCTION_NODE_TYPES) and node.name == func_name:
            body_line = lines[node.body[0].lineno - 1]
            indent = ""
            for ch in body_line:
                if ch in (" ", "\t"):
                    indent += ch
                else:
                    break
            clean = new_doc_raw.strip()
            for q in ('"""', "'''"):
                if clean.startswith(q) and clean.endswith(q) and len(clean) > 6:
                    clean = clean[3:-3].strip()
                    break
            doc_lines = clean.splitlines()
            block = f'{indent}"""{doc_lines[0]}\n'
            for dl in doc_lines[1:]:
                block += f"{indent}{dl}\n"
            block += f'{indent}"""\n'
            first_stmt = node.body[0]
            if (isinstance(first_stmt, ast.Expr)
                    and isinstance(first_stmt.value, (ast.Constant, ast.Str))):
                lines[first_stmt.lineno - 1:first_stmt.end_lineno] = [block]
            else:
                lines.insert(node.lineno, block)
            return "".join(lines), None

    return source, f"Function '{func_name}' not found"


def fix_with_regex(func_name: str, current_code: str) -> str:
    """Insert a placeholder docstring for a function using regex (fallback).

    Used when the AST approach is not viable (e.g. syntax errors).

    Args:
        func_name (str): Target function name.
        current_code (str): Source code string.

    Returns:
        str: Source code with placeholder docstring inserted.
    """
    lines = current_code.splitlines()
    fixed_lines = []
    pattern = re.compile(rf"^\s*def\s+{func_name}\s*\(.*?\)\s*:")
    for i, line in enumerate(lines):
        fixed_lines.append(line)
        if pattern.match(line):
            if i + 1 < len(lines) and '"""' in lines[i + 1]:
                continue
            indent = " " * (len(line) - len(line.lstrip()) + 4)
            fixed_lines.append(
                f'{indent}"""{func_name.replace("_", " ").capitalize()} function."""'
            )
    return "\n".join(fixed_lines)


# ── File scanning ──────────────────────────────────────────────────────────────

def has_docstring_node(node: ast.AST) -> bool:
    """Check if a function or async-function node has a docstring.

    Args:
        node (ast.AST): AST node to inspect.

    Returns:
        bool: True if the first statement is a string literal.
    """
    if not isinstance(node, FUNCTION_NODE_TYPES):
        return False
    if (node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
        return True
    return False


def scan_file(filepath: str) -> List[Dict[str, Any]]:
    """Scan a single Python file and return function coverage metadata.

    Args:
        filepath (str): Absolute or relative path to the .py file.

    Returns:
        list[dict]: One dict per function with keys: file, function, line,
                    docstring (bool), args (count).
    """
    import os
    results = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, FUNCTION_NODE_TYPES):
                results.append({
                    "file": os.path.basename(filepath),
                    "function": node.name,
                    "line": node.lineno,
                    "docstring": has_docstring_node(node),
                    "args": len(node.args.args),
                })
    except SyntaxError as e:
        results.append({
            "file": os.path.basename(filepath),
            "function": f"[SyntaxError line {e.lineno}]",
            "line": e.lineno or 0,
            "docstring": False,
            "args": 0,
        })
    except Exception:
        pass
    return results


def load_path(path_str: str) -> Tuple[Dict[str, str], Dict[str, str], Optional[str]]:
    """Load Python source files from a file or directory path.

    Args:
        path_str (str): Path to a .py file or a directory containing .py files.

    Returns:
        tuple: (files_dict, paths_dict, error_message)
               files_dict maps relative name → source code.
               paths_dict maps relative name → absolute path.
               error_message is None on success.
    """
    p = Path(path_str.strip())
    if not p.exists():
        return {}, {}, f"Path not found: {p}"
    if p.is_file():
        if p.suffix != ".py":
            return {}, {}, f"Not a .py file: {p.name}"
        content = p.read_text(encoding="utf-8", errors="ignore")
        return {p.name: content}, {p.name: str(p.resolve())}, None
    if p.is_dir():
        files, paths = {}, {}
        for py in sorted(p.rglob("*.py")):
            try:
                rel = str(py.relative_to(p))
                files[rel] = py.read_text(encoding="utf-8", errors="ignore")
                paths[rel] = str(py.resolve())
            except Exception:
                pass
        if not files:
            return {}, {}, "No .py files found in that folder."
        return files, paths, None
    return {}, {}, f"Unknown path type: {p}"
