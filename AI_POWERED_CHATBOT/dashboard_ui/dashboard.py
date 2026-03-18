# dashboard_ui/dashboard.py
"""Streamlit dashboard entry-point and UI rendering for AI Code Reviewer Pro."""

from __future__ import annotations
import ast
import csv
import io
import json
import textwrap
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from core.parser.python_parser import (
    analyze_code, extract_functions, inject_docstring,
    scan_file, has_docstring_node, load_path,
)
from core.docstring_engine.generator import generate_docstring, build_description
from core.reporter.coverage_reporter import CoverageReporter
from core.validator.validator import CodeValidator

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Code Reviewer Pro",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Matplotlib dark theme ──────────────────────────────────────────────────────
matplotlib.rcParams.update({
    "figure.facecolor": "#060818",
    "axes.facecolor": "#03040d",
    "axes.edgecolor": "#0e1530",
    "axes.labelcolor": "#3a5080",
    "xtick.color": "#2a3a60",
    "ytick.color": "#2a3a60",
    "text.color": "#7a8db0",
    "grid.color": "#0e1530",
    "grid.linestyle": "--",
    "grid.alpha": 0.5,
    "axes.titlecolor": "#7a8db0",
    "figure.titlesize": 11,
    "font.family": "monospace",
})


# ── CSS injection ──────────────────────────────────────────────────────────────

def inject_css(dark: bool = True) -> None:
    """Inject theme CSS into the Streamlit page.

    Args:
        dark (bool): If True inject dark theme, otherwise light theme.
    """
    from dashboard_ui._styles import DARK_CSS, LIGHT_CSS
    st.markdown(DARK_CSS if dark else LIGHT_CSS, unsafe_allow_html=True)


# ── Session state helpers ──────────────────────────────────────────────────────

DEFAULTS = {
    "files": {}, "file_paths": {}, "loaded_path": "",
    "reviewer_scanned": False, "is_demo": False,
    "selected_file": None, "selected_func": None,
    "generated_docs": {}, "last_save": {},
    "code_content": "", "current_file": None,
    "pep_mode": False, "dashboard_mode": False,
    "scan_results": [], "test_summary": {}, "scan_done": False,
    "expanded_card": None,
    "dark_mode": True,
    "top_mode": "🏠 Home",
}


def init_session_state() -> None:
    """Initialise all session state keys with their defaults."""
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Utility ────────────────────────────────────────────────────────────────────

def calc_pct(total: int, part: int) -> float:
    """Calculate a percentage safely.

    Args:
        total (int): Denominator.
        part (int): Numerator.

    Returns:
        float: Percentage rounded to 1 decimal, or 0.0 if total is 0.
    """
    return round((part / total) * 100, 1) if total else 0.0


def docstring_badge(has_doc: bool) -> str:
    """Return an HTML badge string for docstring presence.

    Args:
        has_doc (bool): Whether the entity has a docstring.

    Returns:
        str: HTML span with appropriate badge style.
    """
    if has_doc:
        return "<span class='badge badge-green'>✔ Yes</span>"
    return "<span class='badge badge-red'>✖ No</span>"


def write_file_to_disk(path_str: str, content: str):
    """Write content to disk and verify the write.

    Args:
        path_str (str): Target file path.
        content (str): Content to write.

    Returns:
        tuple: (success, resolved_path_or_error_message).
    """
    try:
        p = Path(path_str)
        p.write_text(content, encoding="utf-8")
        verify = p.read_text(encoding="utf-8")
        if verify == content:
            return True, str(p.resolve())
        return False, "Write verification failed"
    except PermissionError:
        return False, f"Permission denied: {path_str}"
    except FileNotFoundError:
        return False, f"Directory not found: {Path(path_str).parent}"
    except Exception as e:
        return False, str(e)


# ── Nav cards ──────────────────────────────────────────────────────────────────

def nav_cards(caller: str = "dashboard") -> None:
    """Render the four expandable nav cards (Filters, Search, Export, Help).

    Args:
        caller (str): Namespace prefix to avoid key collisions across pages.
    """
    if "expanded_card" not in st.session_state:
        st.session_state.expanded_card = None

    card_defs = [
        ("Advanced Filters", "Filter by status", "linear-gradient(135deg,#667eea,#764ba2)", "🔍"),
        ("Search", "Find functions", "linear-gradient(135deg,#f093fb,#f5576c)", "🔎"),
        ("Export", "JSON & CSV", "linear-gradient(135deg,#4facfe,#00f2fe)", "📤"),
        ("Help & Tips", "Quick guide", "linear-gradient(135deg,#43e97b,#38f9d7)", "ℹ️"),
    ]

    active_card = st.session_state.expanded_card
    cols = st.columns(4)
    for col, (name, sub, grad, icon) in zip(cols, card_defs):
        with col:
            btn_key = f"{caller}_{name}_btn"
            active = active_card == f"{caller}_{name}"
            act_cls = "nc-active" if active else ""
            st.markdown(
                f"<div class='nc-outer'>"
                f"<div class='nc-visual {act_cls}' style='background:{grad};'>"
                f"<div class='nc-icon'>{icon}</div>"
                f"<div class='nc-name'>{name}</div>"
                f"<div class='nc-sub'>{sub}</div>"
                f"</div><div class='nc-btn-wrap' style='position:absolute;inset:0;z-index:2;'>",
                unsafe_allow_html=True,
            )
            if st.button(name, key=btn_key, use_container_width=True):
                st.session_state.expanded_card = None if active else f"{caller}_{name}"
                st.rerun()
            st.markdown("</div></div>", unsafe_allow_html=True)

    expanded = st.session_state.expanded_card
    if expanded and expanded.startswith(caller + "_"):
        active_name = expanded[len(caller) + 1:]
        st.markdown("<hr style='margin:1rem 0'>", unsafe_allow_html=True)
        _render_card_content(active_name)


def _render_card_content(name: str) -> None:
    """Render the expanded content panel for a nav card.

    Args:
        name (str): Card name — one of 'Advanced Filters', 'Search', 'Export', 'Help & Tips'.
    """
    results = st.session_state.scan_results
    total_fns = len(results)
    total_with_doc = sum(1 for r in results if r["docstring"])
    total_missing = total_fns - total_with_doc

    if name == "Advanced Filters":
        st.markdown(
            "<div class='filter-banner'><h3>🔍 Advanced Filters</h3>"
            "<p>Filter dynamically by file, function, and documentation status</p></div>",
            unsafe_allow_html=True,
        )
        if not st.session_state.scan_done:
            st.info("👈 Upload and analyse files first.")
            return
        col_f, col_s = st.columns([2, 1])
        with col_f:
            doc_filter = st.selectbox("📊 Documentation status", ["All", "OK", "Fix"], key="inline_doc_filter")
        with col_s:
            file_list = ["All files"] + sorted(set(r["file"] for r in results))
            file_filter = st.selectbox("📁 File", file_list, key="inline_file_filter")
        filtered = results
        if doc_filter == "OK":
            filtered = [r for r in filtered if r["docstring"]]
        elif doc_filter == "Fix":
            filtered = [r for r in filtered if not r["docstring"]]
        if file_filter != "All files":
            filtered = [r for r in filtered if r["file"] == file_filter]
        st.markdown(
            f"<div class='stat-cards-row-sm'>"
            f"<div class='stat-card-sm stat-card-blue-sm'><div class='stat-number-sm'>{len(filtered)}</div><div class='stat-label-sm'>Showing</div></div>"
            f"<div class='stat-card-sm stat-card-purple-sm'><div class='stat-number-sm'>{total_fns}</div><div class='stat-label-sm'>Total</div></div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if filtered:
            rows = "".join(
                f"<tr><td>{r['file']}</td><td><code>{r['function']}</code></td>"
                f"<td><span class='{'badge-yes' if r['docstring'] else 'badge-no'}'>"
                f"{'✅ Yes' if r['docstring'] else '❌ No'}</span></td></tr>"
                for r in filtered
            )
            st.markdown(
                f"<table class='review-table'><thead><tr><th>📁 FILE</th><th>⚙️ FUNCTION</th>"
                f"<th>✅ DOCSTRING</th></tr></thead><tbody>{rows}</tbody></table>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("No functions match the selected filters.")

    elif name == "Search":
        st.markdown(
            "<div style='background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:14px;"
            "padding:1.3rem 1.8rem;margin-bottom:1rem'>"
            "<h3 style='color:#fff;margin:0 0 .2rem'>🔎 Search Functions</h3>"
            "<p style='color:#ffe0e8;font-size:.82rem;margin:0'>Instant search across all parsed functions</p></div>",
            unsafe_allow_html=True,
        )
        if not st.session_state.scan_done:
            st.info("👈 Upload and analyse files first.")
            return
        query = st.text_input("🔍 Enter function name", placeholder="Type to search…", key="inline_search")
        if query:
            matches = [r for r in results if query.lower() in r["function"].lower() or query.lower() in r["file"].lower()]
            st.markdown(f"<div style='font-size:.85rem;color:#6b7280;margin-bottom:.8rem'>Found <strong>{len(matches)}</strong> result(s)</div>", unsafe_allow_html=True)
            for r in matches:
                badge = "<span class='badge-yes'>✅ Documented</span>" if r["docstring"] else "<span class='badge-no'>❌ Missing doc</span>"
                st.markdown(
                    f"<div class='search-result'><div>"
                    f"<div class='search-result-fn'>{r['function']}</div>"
                    f"<div class='search-result-file'>{r['file']} · line {r['line']} · {r['args']} arg(s)</div>"
                    f"</div>{badge}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div style='color:#9ca3af;font-size:.85rem'>Type a function or file name to search.</div>", unsafe_allow_html=True)

    elif name == "Export":
        st.markdown(
            "<div style='background:linear-gradient(135deg,#4facfe,#00f2fe);border-radius:14px;"
            "padding:1.3rem 1.8rem;margin-bottom:1rem'>"
            "<h3 style='color:#fff;margin:0 0 .2rem'>📤 Export Results</h3>"
            "<p style='color:#e0f8ff;font-size:.82rem;margin:0'>Download your analysis as JSON or CSV</p></div>",
            unsafe_allow_html=True,
        )
        if not st.session_state.scan_done:
            st.info("👈 Upload and analyse files first.")
            return
        st.markdown(
            f"<div style='background:rgba(102,126,234,.08);border:1px solid rgba(102,126,234,.2);"
            f"border-radius:10px;padding:.9rem 1.2rem;margin-bottom:1rem;font-size:.85rem'>"
            f"<strong>{total_fns}</strong> functions &nbsp;·&nbsp; "
            f"<strong>{total_with_doc}</strong> documented &nbsp;·&nbsp; "
            f"<strong>{total_missing}</strong> missing</div>",
            unsafe_allow_html=True,
        )
        reporter = CoverageReporter(results)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Download JSON", data=reporter.to_json(),
                               file_name="review_results.json", mime="application/json",
                               use_container_width=True, key="inline_dl_json")
        with c2:
            st.download_button("⬇️ Download CSV", data=reporter.to_csv(),
                               file_name="review_results.csv", mime="text/csv",
                               use_container_width=True, key="inline_dl_csv")

    elif name == "Help & Tips":
        st.markdown(
            "<div style='background:linear-gradient(135deg,#43e97b,#38f9d7);border-radius:14px;"
            "padding:1.3rem 1.8rem;margin-bottom:1rem'>"
            "<h3 style='color:#fff;margin:0 0 .2rem'>❓ Help & Tips</h3>"
            "<p style='color:#e0fff8;font-size:.82rem;margin:0'>Quick guide to using the AI Code Reviewer</p></div>",
            unsafe_allow_html=True,
        )
        tips = [
            ("📂 How to upload", "Click **Upload Python file(s)** in the sidebar, select `.py` files, then click **Analyse**."),
            ("📊 Dashboard", "Shows a bar chart of functions per file and pass/fail rows based on docstring coverage."),
            ("🔍 Advanced Filters", "Filter by **OK** (has docstring) or **Fix** (missing docstring)."),
            ("🔎 Search", "Type any function or file name to instantly find matching results."),
            ("📤 Export", "Download results as **JSON** or **CSV** for CI/CD pipelines or reports."),
            ("✅ Docstring status", "`OK` = function has a docstring. `Fix` = docstring is missing."),
            ("💡 Pro tip", "Export CSV and import into your issue tracker to track documentation debt over time."),
        ]
        for title, body in tips:
            with st.expander(title):
                st.markdown(body)
