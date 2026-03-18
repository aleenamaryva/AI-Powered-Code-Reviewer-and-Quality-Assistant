# main_app.py
"""AI Code Reviewer Pro — Streamlit application entry-point.

Run with:
    streamlit run main_app.py
"""

from __future__ import annotations
import ast
import csv
import io
import json
import textwrap
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from core.parser.python_parser import (
    analyze_code, extract_functions, inject_docstring,
    scan_file, has_docstring_node, load_path, fix_with_regex,
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
    "figure.facecolor": "#060818", "axes.facecolor": "#03040d",
    "axes.edgecolor": "#0e1530", "axes.labelcolor": "#3a5080",
    "xtick.color": "#2a3a60", "ytick.color": "#2a3a60",
    "text.color": "#7a8db0", "grid.color": "#0e1530",
    "grid.linestyle": "--", "grid.alpha": 0.5,
    "axes.titlecolor": "#7a8db0", "figure.titlesize": 11,
    "font.family": "monospace",
})

# ── CSS ────────────────────────────────────────────────────────────────────────

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --bg:#1a1f36;--bg2:#222845;--bg3:#2a3158;--bg4:#323c6a;
  --border:rgba(140,160,255,0.2);--border-hi:rgba(140,160,255,0.5);
  --indigo:#7c83fd;--indigo-lt:#a5aaff;--sky:#48cae4;--sky-dim:rgba(72,202,228,0.18);
  --coral:#ff6b6b;--mint:#51e5a0;--amber:#ffd166;--violet:#c77dff;
  --text:#eef0ff;--text-mid:#b8bde8;--text-dim:#7880b0;
  --radius:12px;--radius-lg:18px;
}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{opacity:.8}50%{opacity:1}}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:#1a1f36!important;color:var(--text)!important}
.stApp{background:#1a1f36!important}
.main .block-container{padding:2rem 2.5rem!important;max-width:1400px!important;animation:fadeUp .4s ease}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#141828 0%,#1a1f36 100%)!important;border-right:1px solid var(--border)!important}
[data-testid="stSidebar"] *{color:var(--text)!important}
.stButton>button{background:linear-gradient(135deg,#7c83fd,#9b59f5)!important;color:#fff!important;border:none!important;border-radius:var(--radius)!important;font-weight:700!important;font-size:.85rem!important;padding:.5rem 1.4rem!important;transition:all .2s!important;box-shadow:0 4px 18px rgba(124,131,253,.35)!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 26px rgba(124,131,253,.5)!important}
[data-testid="stMetric"]{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:var(--radius-lg)!important;padding:1.1rem 1.3rem!important}
[data-testid="stMetricValue"]{font-size:1.9rem!important;font-weight:900!important;color:var(--indigo-lt)!important}
.stTextArea textarea{background:var(--bg2)!important;border:1.5px solid var(--border)!important;border-radius:var(--radius)!important;color:var(--mint)!important;font-family:'JetBrains Mono',monospace!important;font-size:.8rem!important}
[data-testid="stExpander"]{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important}
.stProgress>div{background:var(--bg3)!important;border-radius:6px!important;height:7px!important}
.stProgress>div>div{background:linear-gradient(90deg,var(--indigo),var(--sky))!important;border-radius:6px!important}
.banner{border-radius:var(--radius-lg);padding:1.1rem 1.6rem;font-weight:700;font-size:.96rem;margin-bottom:1.2rem;display:flex;align-items:center;gap:.8rem}
.banner-violet{background:linear-gradient(135deg,rgba(199,125,255,.2),rgba(124,131,253,.15));border:1px solid rgba(199,125,255,.4);color:#ddb8ff}
.banner-blue{background:linear-gradient(135deg,rgba(72,202,228,.18),rgba(124,131,253,.12));border:1px solid rgba(72,202,228,.4);color:#90e5f8}
.banner-teal{background:linear-gradient(135deg,rgba(81,229,160,.18),rgba(72,202,228,.12));border:1px solid rgba(81,229,160,.4);color:#90f0c4}
.banner-rose{background:linear-gradient(135deg,rgba(255,107,107,.18),rgba(255,209,102,.12));border:1px solid rgba(255,107,107,.4);color:#ffaaaa}
.badge{border-radius:20px;padding:3px 12px;font-size:.67rem;font-weight:700;font-family:'JetBrains Mono',monospace;white-space:nowrap;display:inline-block}
.badge-red{background:rgba(255,107,107,.2);color:#ff9090;border:1px solid rgba(255,107,107,.4)}
.badge-green{background:rgba(81,229,160,.2);color:#80f5c0;border:1px solid rgba(81,229,160,.4)}
.badge-yes{background:rgba(81,229,160,.2);color:#80f5c0;border:1px solid rgba(81,229,160,.4);border-radius:20px;padding:3px 12px;font-size:.73rem;font-weight:700}
.badge-no{background:rgba(255,107,107,.2);color:#ff9090;border:1px solid rgba(255,107,107,.4);border-radius:20px;padding:3px 12px;font-size:.73rem;font-weight:700}
.code-box{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:1.2rem 1.4rem;font-family:'JetBrains Mono',monospace;font-size:.78rem;line-height:1.85;white-space:pre-wrap;min-height:175px;color:var(--mint);tab-size:4}
.code-box.inferred{color:var(--sky);border-color:rgba(72,202,228,.3)}
.code-box-header{background:var(--bg3);border:1px solid var(--border);border-bottom:none;border-radius:var(--radius) var(--radius) 0 0;padding:.5rem 1.2rem;font-family:'JetBrains Mono',monospace;font-size:.67rem;color:var(--text-mid);display:flex;align-items:center;gap:.5rem}
.code-box-header .dot{width:10px;height:10px;border-radius:50%;display:inline-block}
.code-box.attached{border-radius:0 0 var(--radius) var(--radius);min-height:160px}
.info-banner{border-radius:var(--radius);padding:.8rem 1.2rem;font-size:.82rem;display:flex;align-items:flex-start;gap:.55rem;line-height:1.65;margin:.5rem 0;font-family:'JetBrains Mono',monospace}
.info-live{background:rgba(81,229,160,.15);border:1px solid rgba(81,229,160,.4);color:#80f5c0}
.info-demo{background:rgba(255,209,102,.15);border:1px solid rgba(255,209,102,.4);color:#ffe080}
.info-tip{background:rgba(72,202,228,.15);border:1px solid rgba(72,202,228,.4);color:#90e5f8}
.stat-card{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-lg);padding:1.4rem;text-align:center;transition:all .25s;animation:fadeUp .4s ease}
.stat-card:hover{transform:translateY(-3px);box-shadow:0 14px 36px rgba(0,0,0,.35);border-color:var(--border-hi)}
.stat-num{font-size:2.4rem;font-weight:900;line-height:1;color:var(--indigo-lt)}
.stat-label{font-size:.63rem;color:var(--text-mid);text-transform:uppercase;letter-spacing:.15em;margin-top:.5rem;font-weight:700;font-family:'JetBrains Mono',monospace}
.stat-sub{font-size:.72rem;color:var(--text-mid);margin-top:.2rem}
.stat-icon{font-size:1.5rem;margin-bottom:.4rem}
.save-ok{background:rgba(81,229,160,.15);border:1px solid rgba(81,229,160,.4);border-radius:var(--radius);padding:.85rem 1.2rem;color:#80f5c0;font-family:'JetBrains Mono',monospace;font-size:.78rem;margin-top:.7rem;word-break:break-all;line-height:1.7}
.save-err{background:rgba(255,107,107,.15);border:1px solid rgba(255,107,107,.4);border-radius:var(--radius);padding:.85rem 1.2rem;color:#ff9090;font-family:'JetBrains Mono',monospace;font-size:.78rem;margin-top:.7rem}
.review-table{width:100%;border-collapse:collapse;border-radius:var(--radius-lg);overflow:hidden;background:var(--bg2)}
.review-table thead tr{background:linear-gradient(135deg,#4a51c4,#6b2fa0)}
.review-table th{padding:.95rem 1.3rem;text-align:left;font-size:.78rem;font-weight:700;letter-spacing:.06em;color:#fff;font-family:'JetBrains Mono',monospace}
.review-table td{padding:.85rem 1.3rem;font-size:.83rem;border-bottom:1px solid var(--border);color:var(--text-mid);background:var(--bg2);font-family:'JetBrains Mono',monospace}
.review-table tr:hover td{background:var(--bg3);color:var(--text)}
.search-result{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:.95rem 1.3rem;margin-bottom:.5rem;display:flex;justify-content:space-between;align-items:center;transition:all .2s}
.search-result:hover{border-color:var(--indigo-lt);background:var(--bg3)}
.search-result-file{font-size:.76rem;color:var(--text-mid);font-family:'JetBrains Mono',monospace}
.search-result-fn{font-weight:700;font-size:.87rem;color:var(--text)}
.stat-cards-row-sm{display:flex;gap:.8rem;margin-bottom:1rem}
.stat-card-sm{flex:1;border-radius:var(--radius);padding:1.1rem;text-align:center;color:#fff}
.stat-card-blue-sm{background:linear-gradient(135deg,#4a51c4,#6b2fa0);border:1px solid rgba(124,131,253,.35)}
.stat-card-purple-sm{background:linear-gradient(135deg,#6b2fa0,#9b59b6);border:1px solid rgba(199,125,255,.35)}
.stat-number-sm{font-size:2rem;font-weight:900;line-height:1}
.stat-label-sm{font-size:.71rem;opacity:.9;margin-top:.3rem;font-family:'JetBrains Mono',monospace;letter-spacing:.1em;text-transform:uppercase}
.test-row{display:flex;align-items:center;justify-content:space-between;background:rgba(81,229,160,.15);border:1px solid rgba(81,229,160,.35);border-radius:var(--radius);padding:.85rem 1.3rem;margin-bottom:.5rem;font-weight:700;font-size:.87rem;color:#80f5c0}
.test-row-fail{background:rgba(255,107,107,.15);border-color:rgba(255,107,107,.35);color:#ff9090}
.feature-banner{background:linear-gradient(135deg,#4a51c4,#6b2fa0);border-radius:var(--radius-lg);padding:1.3rem 1.8rem;margin-bottom:1.2rem}
.feature-banner h3{color:#fff;font-size:1.2rem;font-weight:800;margin:0 0 .3rem}
.feature-banner p{color:rgba(255,255,255,.82);font-size:.86rem;margin:0}
.filter-banner{background:linear-gradient(135deg,#4a51c4,#6b2fa0);border-radius:var(--radius-lg);padding:1.2rem 1.8rem;margin-bottom:1.2rem}
.filter-banner h3{color:#fff;font-size:1.1rem;font-weight:800;margin:0 0 .2rem}
.filter-banner p{color:rgba(255,255,255,.82);font-size:.83rem;margin:0}
.nc-outer{position:relative;margin-bottom:0}
.nc-visual{border-radius:16px;padding:1.6rem 1rem 1.4rem;text-align:center;pointer-events:none;position:relative;z-index:1;transition:transform .2s,box-shadow .2s}
.nc-icon{font-size:2.8rem;line-height:1;margin-bottom:.5rem}
.nc-name{font-weight:800;font-size:.96rem;color:#fff;margin-bottom:.25rem}
.nc-sub{font-size:.76rem;color:rgba(255,255,255,.85)}
.nc-outer:hover .nc-visual{transform:translateY(-4px);box-shadow:0 14px 36px rgba(0,0,0,.4)}
.nc-visual.nc-active{outline:3px solid rgba(255,255,255,.8);outline-offset:-3px}
.nc-btn-wrap>div>button{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;opacity:0!important;cursor:pointer!important;z-index:2!important;border:none!important;background:transparent!important;border-radius:16px!important}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--indigo);border-radius:4px}
p,span,div{color:var(--text)!important}
</style>
"""

# ── Session state ──────────────────────────────────────────────────────────────

for _k, _v in {
    "files": {}, "file_paths": {}, "loaded_path": "",
    "reviewer_scanned": False, "is_demo": False,
    "selected_file": None, "selected_func": None,
    "generated_docs": {}, "last_save": {},
    "code_content": "", "current_file": None,
    "pep_mode": False, "dashboard_mode": False,
    "scan_results": [], "test_summary": {}, "scan_done": False,
    "expanded_card": None, "dark_mode": True, "top_mode": "🏠 Home",
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

st.markdown(DARK_CSS, unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────

def calc_pct(total, part):
    return round((part / total) * 100, 1) if total else 0.0

def docstring_badge(has_doc):
    return "<span class='badge badge-green'>✔ Yes</span>" if has_doc else "<span class='badge badge-red'>✖ No</span>"

def write_file_to_disk(path_str, content):
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

def nav_cards(caller="dashboard"):
    card_defs = [
        ("Advanced Filters", "Filter by status",  "linear-gradient(135deg,#667eea,#764ba2)", "🔍"),
        ("Search",           "Find functions",    "linear-gradient(135deg,#f093fb,#f5576c)", "🔎"),
        ("Export",           "JSON & CSV",        "linear-gradient(135deg,#4facfe,#00f2fe)", "📤"),
        ("Help & Tips",      "Quick guide",       "linear-gradient(135deg,#43e97b,#38f9d7)", "ℹ️"),
    ]
    active_card = st.session_state.expanded_card
    cols = st.columns(4)
    for col, (name, sub, grad, icon) in zip(cols, card_defs):
        with col:
            btn_key = f"{caller}_{name}_btn"
            active = active_card == f"{caller}_{name}"
            act_cls = "nc-active" if active else ""
            st.markdown(
                f"<div class='nc-outer'><div class='nc-visual {act_cls}' style='background:{grad};'>"
                f"<div class='nc-icon'>{icon}</div><div class='nc-name'>{name}</div>"
                f"<div class='nc-sub'>{sub}</div></div>"
                f"<div class='nc-btn-wrap' style='position:absolute;inset:0;z-index:2;'>",
                unsafe_allow_html=True,
            )
            if st.button(name, key=btn_key, use_container_width=True):
                st.session_state.expanded_card = None if active else f"{caller}_{name}"
                st.rerun()
            st.markdown("</div></div>", unsafe_allow_html=True)

    expanded = st.session_state.expanded_card
    if expanded and expanded.startswith(caller + "_"):
        st.markdown("<hr style='margin:1rem 0'>", unsafe_allow_html=True)
        _render_nav_card(expanded[len(caller) + 1:])

def _render_nav_card(name):
    results = st.session_state.scan_results
    total_fns = len(results)
    total_with_doc = sum(1 for r in results if r["docstring"])
    total_missing = total_fns - total_with_doc
    reporter = CoverageReporter(results)

    if name == "Advanced Filters":
        st.markdown("<div class='filter-banner'><h3>🔍 Advanced Filters</h3><p>Filter dynamically by file, function, and documentation status</p></div>", unsafe_allow_html=True)
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
        if doc_filter == "OK":    filtered = [r for r in filtered if r["docstring"]]
        elif doc_filter == "Fix": filtered = [r for r in filtered if not r["docstring"]]
        if file_filter != "All files": filtered = [r for r in filtered if r["file"] == file_filter]
        st.markdown(f"<div class='stat-cards-row-sm'><div class='stat-card-sm stat-card-blue-sm'><div class='stat-number-sm'>{len(filtered)}</div><div class='stat-label-sm'>Showing</div></div><div class='stat-card-sm stat-card-purple-sm'><div class='stat-number-sm'>{total_fns}</div><div class='stat-label-sm'>Total</div></div></div>", unsafe_allow_html=True)
        if filtered:
            rows = "".join(f"<tr><td>{r['file']}</td><td><code>{r['function']}</code></td><td><span class='{'badge-yes' if r['docstring'] else 'badge-no'}'>{'✅ Yes' if r['docstring'] else '❌ No'}</span></td></tr>" for r in filtered)
            st.markdown(f"<table class='review-table'><thead><tr><th>📁 FILE</th><th>⚙️ FUNCTION</th><th>✅ DOCSTRING</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
        else:
            st.warning("No functions match the selected filters.")

    elif name == "Search":
        st.markdown("<div style='background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:14px;padding:1.3rem 1.8rem;margin-bottom:1rem'><h3 style='color:#fff;margin:0'>🔎 Search Functions</h3></div>", unsafe_allow_html=True)
        if not st.session_state.scan_done:
            st.info("👈 Upload and analyse files first.")
            return
        query = st.text_input("🔍 Enter function name", placeholder="Type to search…", key="inline_search")
        if query:
            matches = [r for r in results if query.lower() in r["function"].lower() or query.lower() in r["file"].lower()]
            for r in matches:
                badge = "<span class='badge-yes'>✅ Documented</span>" if r["docstring"] else "<span class='badge-no'>❌ Missing doc</span>"
                st.markdown(f"<div class='search-result'><div><div class='search-result-fn'>{r['function']}</div><div class='search-result-file'>{r['file']} · line {r['line']} · {r['args']} arg(s)</div></div>{badge}</div>", unsafe_allow_html=True)

    elif name == "Export":
        st.markdown("<div style='background:linear-gradient(135deg,#4facfe,#00f2fe);border-radius:14px;padding:1.3rem 1.8rem;margin-bottom:1rem'><h3 style='color:#fff;margin:0'>📤 Export Results</h3></div>", unsafe_allow_html=True)
        if not st.session_state.scan_done:
            st.info("👈 Upload and analyse files first.")
            return
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Download JSON", data=reporter.to_json(), file_name="review_results.json", mime="application/json", use_container_width=True, key="inline_dl_json")
        with c2:
            st.download_button("⬇️ Download CSV", data=reporter.to_csv(), file_name="review_results.csv", mime="text/csv", use_container_width=True, key="inline_dl_csv")

    elif name == "Help & Tips":
        st.markdown("<div style='background:linear-gradient(135deg,#43e97b,#38f9d7);border-radius:14px;padding:1.3rem 1.8rem;margin-bottom:1rem'><h3 style='color:#fff;margin:0'>❓ Help & Tips</h3></div>", unsafe_allow_html=True)
        tips = [
            ("📂 How to upload", "Click **Upload Python file(s)** in the sidebar, select `.py` files, then click **Analyse**."),
            ("📊 Dashboard", "Shows a bar chart of functions per file and pass/fail rows based on docstring coverage."),
            ("🔍 Advanced Filters", "Filter by **OK** (has docstring) or **Fix** (missing docstring)."),
            ("🔎 Search", "Type any function or file name to instantly find matching results."),
            ("📤 Export", "Download results as **JSON** or **CSV** for CI/CD pipelines or reports."),
            ("💡 Pro tip", "Export CSV and import into your issue tracker to track documentation debt."),
        ]
        for title, body in tips:
            with st.expander(title):
                st.markdown(body)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<div style='font-weight:800;font-size:1.05rem;margin-bottom:1rem'>🔮 Code Reviewer Pro</div>", unsafe_allow_html=True)

    app_mode = st.selectbox("View", ["🏠 Home", "✅ Validation", "🔮 Docstring Reviewer", "📊 Dashboard"], label_visibility="collapsed", key="top_mode_radio")
    st.session_state.top_mode = app_mode
    st.markdown("<hr style='margin:.5rem 0'>", unsafe_allow_html=True)

    # ── Docstring style (for Reviewer page) ───────────────────────────────────
    doc_style = "GOOGLE"
    if app_mode == "🔮 Docstring Reviewer":
        doc_style = st.selectbox("Docstring style", ["GOOGLE", "NUMPY", "reST"], label_visibility="collapsed")

    # ── File input ────────────────────────────────────────────────────────────
    st.markdown("<div style='font-size:.7rem;text-transform:uppercase;letter-spacing:.12em;color:#7880b0;margin:.5rem 0'>📂 File Input</div>", unsafe_allow_html=True)
    input_mode = st.radio("Input mode", ["📄 Upload file(s)", "🗂️ Folder path"], label_visibility="collapsed", key="unified_input_mode")

    uploaded_files = None
    folder_path = ""
    if input_mode == "📄 Upload file(s)":
        uploaded_files = st.file_uploader("Upload .py files", type=["py"], accept_multiple_files=True, label_visibility="collapsed", key="unified_py_upload")
        if uploaded_files:
            st.markdown(f"<div class='info-banner info-live'>✅ {len(uploaded_files)} file(s) ready</div>", unsafe_allow_html=True)
    else:
        folder_path = st.text_input("Folder or file path", value=st.session_state.loaded_path, placeholder="e.g. C:/myproject/src", label_visibility="collapsed", key="unified_folder_input")
        if folder_path.strip():
            _p = Path(folder_path.strip())
            if _p.exists():
                st.markdown(f"<div class='info-banner info-live'>✅ {'📄' if _p.is_file() else '📁'} <code>{_p.name}</code></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='info-banner info-demo'>❌ Path not found</div>", unsafe_allow_html=True)

    col_load, col_reload = st.columns(2)
    with col_load:
        unified_load = st.button("▶ Load & Analyse", use_container_width=True, key="unified_load")
    with col_reload:
        unified_reload = st.button("🔄 Reload", use_container_width=True, key="unified_reload", disabled=not st.session_state.loaded_path and not uploaded_files)

    if unified_load:
        if input_mode == "📄 Upload file(s)" and uploaded_files:
            with st.spinner("Loading…"):
                all_results, _files_dict = [], {}
                for uf in uploaded_files:
                    source = uf.read().decode("utf-8", errors="ignore")
                    _files_dict[uf.name] = source
                    try:
                        tree = ast.parse(source, filename=uf.name)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                all_results.append({"file": uf.name, "function": node.name, "line": node.lineno, "docstring": has_docstring_node(node), "args": len(node.args.args)})
                    except SyntaxError as e:
                        all_results.append({"file": uf.name, "function": f"[SyntaxError line {e.lineno}]", "line": e.lineno or 0, "docstring": False, "args": 0})
                reporter = CoverageReporter(all_results)
                st.session_state.scan_results = all_results
                st.session_state.test_summary = reporter.run_tests()
                st.session_state.scan_done = True
                first_name = list(_files_dict.keys())[0]
                st.session_state.code_content = _files_dict[first_name]
                st.session_state.current_file = first_name
                st.session_state.files = _files_dict
                st.session_state.file_paths = {}
                st.session_state.loaded_path = ""
                st.session_state.reviewer_scanned = True
                st.session_state.is_demo = False
                st.session_state.selected_file = first_name
                st.session_state.generated_docs = {}
                st.session_state.last_save = {}
            st.success(f"✅ Loaded {len(uploaded_files)} file(s) — {len(all_results)} functions found")
            st.rerun()

        elif input_mode == "🗂️ Folder path" and folder_path.strip():
            with st.spinner("Loading…"):
                files, paths, err = load_path(folder_path)
                if err:
                    st.error(err)
                else:
                    all_results = []
                    _p2 = Path(folder_path.strip())
                    for py_file in (sorted(_p2.rglob("*.py")) if _p2.is_dir() else [_p2]):
                        all_results.extend(scan_file(str(py_file)))
                    reporter = CoverageReporter(all_results)
                    st.session_state.scan_results = all_results
                    st.session_state.test_summary = reporter.run_tests()
                    st.session_state.scan_done = True
                    st.session_state.files = files
                    st.session_state.file_paths = paths
                    st.session_state.loaded_path = folder_path.strip()
                    st.session_state.reviewer_scanned = True
                    st.session_state.is_demo = False
                    st.session_state.selected_file = list(files.keys())[0]
                    st.session_state.generated_docs = {}
                    st.session_state.last_save = {}
                    first_name = list(files.keys())[0]
                    st.session_state.code_content = files[first_name]
                    st.session_state.current_file = first_name
                    st.success(f"✅ Loaded {len(files)} file(s) — {len(all_results)} functions found")
                    st.rerun()
        else:
            st.warning("Please provide file(s) or a path before loading.")

    if app_mode == "🔮 Docstring Reviewer":
        st.markdown("<hr style='margin:.5rem 0'>", unsafe_allow_html=True)
        if st.button("🧪 Load Demo Files", use_container_width=True):
            st.session_state.files = {
                "sample_a.py": textwrap.dedent("""\
                    def calculate_average(numbers):
                        total = sum(numbers)
                        return total / len(numbers)

                    def find_max(items):
                        return max(items)
                """),
                "sample_b.py": textwrap.dedent("""\
                    def read_file(path):
                        with open(path) as f:
                            return f.read()

                    def write_json(data, path):
                        \"\"\"Write data to a JSON file.\"\"\"
                        import json
                        with open(path, 'w') as f:
                            json.dump(data, f)
                """),
            }
            st.session_state.file_paths = {}
            st.session_state.loaded_path = ""
            st.session_state.reviewer_scanned = True
            st.session_state.is_demo = True
            st.session_state.selected_file = "sample_a.py"
            st.session_state.generated_docs = {}
            st.session_state.last_save = {}
            st.rerun()

    if app_mode == "✅ Validation":
        if st.button("🧪 PEP Validation", use_container_width=True, key="toggle_pep"):
            st.session_state.pep_mode = not st.session_state.pep_mode
            st.rerun()

    st.markdown(f"<div style='font-size:.66rem;color:#2a3a60;margin-top:.8rem;font-family:monospace'>Last scan: {datetime.now().strftime('%d %b %Y, %H:%M')}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE ROUTING — import page modules
# ══════════════════════════════════════════════════════════════════════════════

mode = st.session_state.top_mode

if mode == "🔮 Docstring Reviewer":
    from pages.docstring_reviewer import render
    render(doc_style)

elif mode == "✅ Validation":
    from pages.validation import render
    render()

elif mode == "📊 Dashboard":
    from pages.dashboard_page import render
    render(nav_cards)

else:  # 🏠 Home
    from pages.home import render
    render(calc_pct, docstring_badge)
