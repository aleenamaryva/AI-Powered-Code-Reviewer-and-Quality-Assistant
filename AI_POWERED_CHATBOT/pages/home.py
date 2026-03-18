# pages/home.py
"""Home page — quick dashboard with coverage metrics and function drill-down."""

from __future__ import annotations
import json
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from core.parser.python_parser import analyze_code


def render(calc_pct, docstring_badge) -> None:
    """Render the Home page.

    Args:
        calc_pct: Callable(total, part) -> float for percentage calculation.
        docstring_badge: Callable(bool) -> str HTML badge.
    """
    st.markdown("<div class='banner banner-blue'>🏠 Scanner Home</div>", unsafe_allow_html=True)

    if not st.session_state.scan_done:
        st.markdown(
            "<div class='info-banner info-tip'>"
            "👈 Choose an input mode in the sidebar and click <b>▶ Load &amp; Analyse</b> to get started."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    _val_code = st.session_state.code_content or None
    _val_file = st.session_state.current_file

    if not _val_code:
        st.markdown("<div class='info-banner info-tip'>📂 Upload a Python file to see the full dashboard here.</div>", unsafe_allow_html=True)
        return

    st.markdown(f"<div class='info-banner info-live'>📄 <b>Active File:</b> {_val_file}</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)

    _functions, _classes, _module_doc, _error = analyze_code(_val_code)
    _total_functions = len(_functions) if _functions else 0
    _total_classes = len(_classes) if _classes else 0
    _documented_functions = sum(f["Has Docstring"] for f in (_functions or []))
    _documented_classes = sum(c["Has Docstring"] for c in (_classes or []))
    _undoc_f = _total_functions - _documented_functions
    _func_pct = calc_pct(_total_functions, _documented_functions)
    _class_pct = calc_pct(_total_classes, _documented_classes)
    _overall_pct = calc_pct(_total_functions + _total_classes, _documented_functions + _documented_classes)

    st.markdown("<div class='banner banner-blue' style='margin-top:1.1rem'>📊 Quick Dashboard</div>", unsafe_allow_html=True)
    if _error:
        st.info("Resolve syntax issues to view metrics.")
        return

    _dash_cols = st.columns(5)
    _dash_cols[0].metric("Total Functions", _total_functions)
    _dash_cols[1].metric("Module Docstring", "✅" if _module_doc else "❌")
    _dash_cols[2].metric("Functions Documented", _documented_functions)
    _dash_cols[3].metric("Missing Docs", _undoc_f)
    _dash_cols[4].metric("Coverage %", f"{_func_pct:.0f}%")

    _tab1, _tab2, _tab3, _tab4 = st.tabs(["📊 Chart", "📋 Table", "📦 JSON", "📊 Analysis Dashboard"])

    with _tab1:
        _fig, _ax = plt.subplots(figsize=(7, 4))
        _bars = _ax.bar(["Functions", "Classes", "Overall"], [_func_pct, _class_pct, _overall_pct],
                        color=["#00d4ff", "#b060ff", "#00ffaa"], width=.5, zorder=3)
        _ax.set_ylim(0, 110)
        _ax.set_ylabel("Coverage %")
        _ax.yaxis.grid(True, zorder=0)
        _ax.set_axisbelow(True)
        for _bar, _val in zip(_bars, [_func_pct, _class_pct, _overall_pct]):
            _ax.text(_bar.get_x() + _bar.get_width() / 2, _bar.get_height() + 2,
                     f"{_val:.1f}%", ha="center", va="bottom", fontsize=10, color="#e8eeff", fontweight="bold")
        _fig.tight_layout()
        st.pyplot(_fig)
        plt.close(_fig)

    with _tab2:
        _df = pd.DataFrame((_functions or []) + (_classes or []))
        if not _df.empty:
            _df["Has Docstring"] = _df["Has Docstring"].map(lambda v: "✔ Yes" if v else "✖ No")
            st.dataframe(_df, use_container_width=True, height=500)
        else:
            st.info("No functions or classes found.")

    with _tab3:
        _result_data = {
            "file": _val_file, "timestamp": datetime.now().isoformat(),
            "module_docstring": _module_doc, "function_coverage": _func_pct,
            "class_coverage": _class_pct, "overall_coverage": _overall_pct,
            "functions": _functions or [], "classes": _classes or [],
        }
        st.json(_result_data)
        st.download_button("⬇ Download Coverage Report JSON",
            json.dumps(_result_data, indent=4).encode("utf-8"),
            file_name=f"{_val_file}_coverage_report.json", mime="application/json", key="home_dl_json")

    with _tab4:
        snap_cols = st.columns(3)
        snap_cols[0].metric("Module Docstring", "Present" if _module_doc else "Missing")
        snap_cols[1].metric("Function Coverage", f"{_documented_functions}/{_total_functions}", delta=f"{_func_pct:.0f}%" if _total_functions else None)
        snap_cols[2].metric("Class Coverage", f"{_documented_classes}/{_total_classes}", delta=f"{_class_pct:.0f}%" if _total_classes else None)

        if _module_doc:
            st.success("Module-level documentation detected.")
        else:
            st.warning("No module docstring found.")
        st.progress(_func_pct / 100 if _total_functions else 0)
        st.caption("Function documentation completeness")

        if _functions:
            st.markdown("<div style='font-weight:700;color:#7a8db0;margin:.9rem 0 .5rem'>🔎 Function Drill-down</div>", unsafe_allow_html=True)
            func_filter = st.radio("Function filter", ["All", "Documented", "Missing Docstrings"], horizontal=True, key="home_func_filter")
            _df_funcs = pd.DataFrame(_functions).sort_values(by="Complexity", ascending=False)
            if func_filter == "Documented":
                _df_view = _df_funcs[_df_funcs["Has Docstring"]]
            elif func_filter == "Missing Docstrings":
                _df_view = _df_funcs[~_df_funcs["Has Docstring"]]
            else:
                _df_view = _df_funcs
            if _df_view.empty:
                st.info("No functions match the selected filter.")
            else:
                st.dataframe(_df_view[["Name", "Kind", "Start Line", "End Line", "Complexity", "Has Docstring"]], use_container_width=True)
            _most_complex = _df_funcs.iloc[0]
            st.info(f"Highest complexity: {_most_complex['Name']} ({_most_complex['Complexity']})")

        if _functions:
            st.markdown("<div style='font-weight:700;color:#7a8db0;margin:.9rem 0 .5rem'>📉 Complexity Distribution</div>", unsafe_allow_html=True)
            cfig, cax = plt.subplots(figsize=(7, max(3, len(_functions) * 0.4)))
            colors = ["#ff4d6d" if c > 5 else "#ffb830" if c > 3 else "#00d4ff" for c in [f["Complexity"] for f in _functions]]
            cax.barh([f["Name"] for f in _functions], [f["Complexity"] for f in _functions], color=colors, zorder=3)
            cax.xaxis.grid(True, zorder=0)
            cax.set_xlabel("Complexity Score")
            cfig.tight_layout()
            st.pyplot(cfig)
            plt.close(cfig)

    if _functions:
        st.markdown("<div style='font-weight:700;color:#7a8db0;font-size:1rem;margin:1.1rem 0 .6rem'>🔍 Function Details</div>", unsafe_allow_html=True)
        for fn in _functions:
            with st.expander(fn["Name"]):
                c1, c2, c3 = st.columns(3)
                c1.metric("Complexity", fn["Complexity"])
                c2.metric("Start Line", fn["Start Line"])
                c3.metric("End Line", fn["End Line"])
                st.markdown(f"Has Docstring: {docstring_badge(fn['Has Docstring'])}", unsafe_allow_html=True)

    if _classes:
        st.markdown("<div style='font-weight:700;color:#7a8db0;font-size:1rem;margin:1.1rem 0 .6rem'>🏷 Class Details</div>", unsafe_allow_html=True)
        for cls in _classes:
            with st.expander(cls["Name"]):
                c1, c2, c3 = st.columns(3)
                c1.metric("Complexity", cls["Complexity"])
                c2.metric("Start Line", cls["Start Line"])
                c3.metric("End Line", cls["End Line"])
                st.markdown(f"Has Docstring: {docstring_badge(cls['Has Docstring'])}", unsafe_allow_html=True)
