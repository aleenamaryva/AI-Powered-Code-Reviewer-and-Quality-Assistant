# pages/dashboard_page.py
"""Dashboard page — test suite overview and per-file bar chart."""

from __future__ import annotations
import json

import matplotlib.pyplot as plt
import streamlit as st


def render(nav_cards_fn) -> None:
    """Render the Dashboard page.

    Args:
        nav_cards_fn: Callable that renders the four expandable nav cards.
    """
    st.markdown("<div class='banner banner-teal'>📊 Dashboard</div>", unsafe_allow_html=True)

    if not st.session_state.scan_done:
        st.markdown("<div class='info-banner info-tip'>👈 Upload files and click Load & Analyse first.</div>", unsafe_allow_html=True)
        return

    test_summary = st.session_state.test_summary
    st.markdown("<div style='font-weight:700;color:#7a8db0;margin-bottom:.6rem'>📊 Test Results</div>", unsafe_allow_html=True)

    if test_summary:
        try:
            import plotly.graph_objects as go
            suite_names = list(test_summary.keys())
            suite_vals = [v["total"] for v in test_summary.values()]
            fig = go.Figure(go.Bar(x=suite_names, y=suite_vals, marker_color="#667eea", text=suite_vals, textposition="outside"))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=11, color="#7a8db0"), margin=dict(l=20, r=20, t=20, b=80),
                height=300, xaxis=dict(tickangle=-35, gridcolor="#0e1530"), yaxis=dict(gridcolor="#0e1530"),
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            fig, ax = plt.subplots(figsize=(8, 3))
            suite_names = list(test_summary.keys())
            suite_vals = [v["total"] for v in test_summary.values()]
            ax.bar(suite_names, suite_vals, color="#667eea")
            ax.set_ylabel("Functions")
            plt.xticks(rotation=35, ha="right")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    for suite, info in test_summary.items():
        passed = info["passed"]
        total = info["total"]
        all_ok = passed == total
        row_cls = "test-row" if all_ok else "test-row test-row-fail"
        icon = "✅" if all_ok else "❌"
        st.markdown(
            f"<div class='{row_cls}'>"
            f"<span>{icon} &nbsp; {suite}</span>"
            f"<span style='font-size:.82rem;font-weight:600'>{passed}/{total} passed</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='feature-banner' style='margin-top:1.5rem'><h3>✨ Enhanced UI Features</h3><p>Explore powerful analysis tools below</p></div>", unsafe_allow_html=True)
    nav_cards_fn(caller="dashboard")
