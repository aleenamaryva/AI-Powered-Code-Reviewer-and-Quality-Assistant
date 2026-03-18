# core/review_engine/ai_review.py
"""AI-powered code review engine — orchestrates docstring generation and file write-back."""

from __future__ import annotations
import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.parser.python_parser import extract_functions, inject_docstring, load_path
from core.docstring_engine.generator import generate_docstring


class AIReviewer:
    """Orchestrates automated docstring generation across one or more Python files.

    Loads file(s), extracts function metadata, generates docstrings for
    undocumented functions, and optionally writes the results back to disk.

    Args:
        style (str): Docstring format — 'GOOGLE', 'NUMPY', or 'reST'.
        auto_save (bool): If True, write changes to disk after generation.
    """

    def __init__(self, style: str = "GOOGLE", auto_save: bool = False):
        """Initialize the AIReviewer.

        Args:
            style (str): Docstring format. Defaults to 'GOOGLE'.
            auto_save (bool): Whether to persist generated docstrings automatically.
        """
        self.style = style
        self.auto_save = auto_save
        self._files: Dict[str, str] = {}
        self._file_paths: Dict[str, str] = {}
        self._generated: Dict[str, str] = {}
        self._save_results: Dict[str, Tuple[bool, str]] = {}

    # ── Loading ────────────────────────────────────────────────────────────────

    def load_path(self, path_str: str) -> Optional[str]:
        """Load .py files from a file or directory path.

        Args:
            path_str (str): Path to a .py file or a folder.

        Returns:
            str | None: Error message, or None on success.
        """
        files, paths, err = load_path(path_str)
        if err:
            return err
        self._files = files
        self._file_paths = paths
        return None

    def load_sources(self, sources: Dict[str, str]) -> None:
        """Load source files from an in-memory dict.

        Args:
            sources (dict): Mapping of filename → source code string.
        """
        self._files = dict(sources)
        self._file_paths = {}

    # ── Review ─────────────────────────────────────────────────────────────────

    def review_all(self, only_missing: bool = True) -> Dict[str, List[Dict]]:
        """Generate docstrings for all loaded files.

        Args:
            only_missing (bool): If True, skip functions that already have docstrings.

        Returns:
            dict: Mapping of filename → list of function review dicts.
        """
        report: Dict[str, List[Dict]] = {}
        for fname, source in self._files.items():
            funcs = extract_functions(source)
            reviewed = []
            for func in funcs:
                if only_missing and func["has_doc"]:
                    reviewed.append({"name": func["name"], "action": "skipped", "docstring": func["docstring"]})
                    continue
                cache_key = f"{fname}__{func['name']}"
                if cache_key not in self._generated:
                    self._generated[cache_key] = generate_docstring(func, self.style)
                doc = self._generated[cache_key]
                reviewed.append({"name": func["name"], "action": "generated", "docstring": doc})
                if self.auto_save:
                    self._apply(fname, func["name"], doc)
            report[fname] = reviewed
        return report

    def review_function(self, filename: str, func_name: str) -> Optional[str]:
        """Generate (or retrieve cached) docstring for a specific function.

        Args:
            filename (str): Filename key as loaded.
            func_name (str): Function name.

        Returns:
            str | None: Generated docstring, or None if function not found.
        """
        source = self._files.get(filename)
        if not source:
            return None
        funcs = extract_functions(source)
        func = next((f for f in funcs if f["name"] == func_name), None)
        if not func:
            return None
        cache_key = f"{filename}__{func_name}"
        if cache_key not in self._generated:
            self._generated[cache_key] = generate_docstring(func, self.style)
        return self._generated[cache_key]

    # ── Apply / save ───────────────────────────────────────────────────────────

    def apply_in_memory(self, filename: str, func_name: str, docstring: str) -> Optional[str]:
        """Inject a docstring into the in-memory source for a file.

        Args:
            filename (str): Filename key.
            func_name (str): Target function name.
            docstring (str): Docstring text to inject.

        Returns:
            str | None: Error message, or None on success.
        """
        source = self._files.get(filename)
        if source is None:
            return f"File '{filename}' not loaded."
        new_src, err = inject_docstring(source, func_name, docstring)
        if err:
            return err
        self._files[filename] = new_src
        return None

    def save_to_disk(self, filename: str) -> Tuple[bool, str]:
        """Write the current in-memory source for a file back to disk.

        Args:
            filename (str): Filename key.

        Returns:
            tuple: (success, message_or_path).
        """
        disk_path = self._file_paths.get(filename, "").strip()
        if not disk_path:
            return False, "No disk path for this file (demo mode)."
        source = self._files.get(filename, "")
        try:
            p = Path(disk_path)
            p.write_text(source, encoding="utf-8")
            verify = p.read_text(encoding="utf-8")
            if verify != source:
                return False, "Write verification failed."
            result = (True, str(p.resolve()))
        except PermissionError:
            result = (False, f"Permission denied: {disk_path}")
        except FileNotFoundError:
            result = (False, f"Directory not found: {Path(disk_path).parent}")
        except Exception as e:
            result = (False, str(e))
        self._save_results[filename] = result
        return result

    def save_all_to_disk(self) -> Dict[str, Tuple[bool, str]]:
        """Write all files with known disk paths back to disk.

        Returns:
            dict: Filename → (success, message).
        """
        results = {}
        for fname in self._file_paths:
            results[fname] = self.save_to_disk(fname)
        return results

    # ── Accessors ──────────────────────────────────────────────────────────────

    @property
    def files(self) -> Dict[str, str]:
        """Return the currently loaded file sources."""
        return self._files

    @property
    def file_paths(self) -> Dict[str, str]:
        """Return the disk-path mapping for loaded files."""
        return self._file_paths

    @property
    def generated_docs(self) -> Dict[str, str]:
        """Return the cache of generated docstrings."""
        return self._generated

    def _apply(self, filename: str, func_name: str, docstring: str) -> None:
        """Internal helper to apply docstring in memory.

        Args:
            filename (str): Filename key.
            func_name (str): Target function.
            docstring (str): Docstring to inject.
        """
        self.apply_in_memory(filename, func_name, docstring)
