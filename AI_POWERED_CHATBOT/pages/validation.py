# pages/validation.py
"""Validation page — PEP 257 compliance checks, complexity analysis, and coverage charts."""

from __future__ import annotations
import json
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from core.parser.python_parser import analyze_code, fix_with_regex
from core.validator.validator import CodeValidator


def _calc_pct(total, part):
    return round((part / total) * 100, 1) if total else 0.0


def render() -> None:
    """Render the Validation page."""
    st.markdown(
        "<div style='display:flex;align-items:center;gap:1.2rem;margin-bottom:1.5rem'>"
        "<div style='width:52px;height:52px;border-radius:16px;background:linear-gradient(135deg,#011a18,#053a36);display:flex;align-items:center;justify-content:center;font-size:1.6rem'>✅</div>"
        "<div><div style='font-size:1.55rem;font-weight:800'>Validation</div>"
        "<div style='font-size:.75rem;color:#2a3a60;margin-top:.2rem'>Analyze documentation coverage, complexity &amp; structure</div></div>"
        "</div><hr>",
        unsafe_allow_html=True,
    )

    analyzer_code = st.session_state.code_content or None
    active_file_name = st.session_state.current_file

    if not analyzer_code:
        st.markdown("<div class='info-banner info-tip'>📂 Upload a Python file in the sidebar to start the analysis.</div>", unsafe_allow_html=True)
        return

    st.markdown(f"<div class='info-banner info-live'>📄 <b>Active File:</b> {active_file_name}</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)

    functions, classes, module_doc, error = analyze_code(analyzer_code)
    validator = CodeValidator(analyzer_code, filename=active_file_name or "module.py")

    total_functions = len(functions) if functions else 0
    total_classes = len(classes) if classes else 0
    documented_functions = sum(f["Has Docstring"] for f in (functions or []))
    documented_classes = sum(c["Has Docstring"] for c in (classes or []))
    undoc_f = total_functions - documented_functions
    func_pct = _calc_pct(total_functions, documented_functions)
    class_pct = _calc_pct(total_classes, documented_classes)
    overall_pct = _calc_pct(total_functions + total_classes, documented_functions + documented_classes)

    if st.session_state.pep_mode:
        st.markdown("<div class='banner banner-rose'>🧪 PEP Validation</div>", unsafe_allow_html=True)
        if error:
            st.error(f"Syntax Error: {error}")
            st.session_state.code_content = st.text_area("Fix syntax here:", value=analyzer_code, height=300)
        else:
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown("<div style='font-weight:700;color:#7a8db0;margin-bottom:.5rem'>Source Code</div>", unsafe_allow_html=True)
                st.session_state.code_content = st.text_area(
                    "Editor", value=st.session_state.code_content, height=600, label_visibility="collapsed")
            with col_right:
                st.markdown("<div style='font-weight:700;color:#7a8db0;margin-bottom:.5rem'>🚦 Live Fix Status</div>", unsafe_allow_html=True)
                for fn in (functions or []):
                    if not fn["Has Docstring"]:
                        st.error(f"❌ {fn['Name']} (Missing Docstring)")
                        if st.button(f"Fix {fn['Name']}", key=f"fix_{fn['Name']}"):
                            st.session_state.code_content = fix_with_regex(fn["Name"], st.session_state.code_content)
                            st.rerun()
                    else:
                        st.success(f"✅ {fn['Name']} (Documented)")

            pep_cols = st.columns(3)
            pep_cols[0].metric("Documented Functions", documented_functions)
            pep_cols[1].metric("Missing Docstrings", max(undoc_f, 0))
            pep_cols[2].metric("Coverage", f"{func_pct:.1f}%" if total_functions else "N/A")

            summary = validator.summary()
            missing_names = validator.missing_functions()
            if missing_names:
                st.warning("Functions without docstrings: " + ", ".join(missing_names))
            if not module_doc:
                st.warning("Module docstring missing.")
            if not missing_names and module_doc:
                st.success("All documented elements comply with docstring expectations.")

            violations = validator.validate()
            non_style = [v for v in violations if v["rule"] != "SYNTAX_ERROR"]
            if non_style:
                rule_counts = validator.rule_counts()
                file_counts: dict = {}
                for v in non_style:
                    file_counts[v.get("file") or active_file_name] = file_counts.get(v.get("file") or active_file_name, 0) + 1
                chart_cols = st.columns(2)
                with chart_cols[0]:
                    st.caption("Error Distribution by Rule Type")
                    fig, ax = plt.subplots(figsize=(5, 4))
                    ax.pie(list(rule_counts.values()), labels=list(rule_counts.keys()), autopct="%1.1f%%", startangle=140, colors=["#00d4ff", "#b060ff", "#00ffaa"])
                    ax.axis("equal")
                    st.pyplot(fig)
                    plt.close(fig)
                with chart_cols[1]:
                    st.caption("Error Distribution by File")
                    fig2, ax2 = plt.subplots(figsize=(5, 4))
                    ax2.pie(list(file_counts.values()), labels=list(file_counts.keys()), autopct="%1.1f%%", startangle=140, colors=["#ffb830", "#ff4d6d", "#b060ff"])
                    ax2.axis("equal")
                    st.pyplot(fig2)
                    plt.close(fig2)
            else:
                st.info("No PEP-style violations detected.")
    else:
        st.markdown("<div class='info-banner info-tip'>👆 Click <b>🧪 PEP Validation</b> in the sidebar to get started.</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    download_name = active_file_name or "code.py"
    st.download_button("💾 Download Fixed File", st.session_state.code_content, file_name=f"fixed_{download_name}")
