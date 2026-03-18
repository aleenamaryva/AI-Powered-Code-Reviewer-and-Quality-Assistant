# pages/docstring_reviewer.py
"""Docstring Reviewer page — browse, generate, and save docstrings."""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from core.parser.python_parser import extract_functions, inject_docstring
from core.docstring_engine.generator import generate_docstring, build_description


def _write_file(path_str: str, content: str):
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


def render(doc_style: str = "GOOGLE") -> None:
    """Render the Docstring Reviewer page.

    Args:
        doc_style (str): Selected docstring style — 'GOOGLE', 'NUMPY', or 'reST'.
    """
    if not st.session_state.reviewer_scanned:
        st.markdown(
            "<div style='text-align:center;padding:5rem 2rem'>"
            "<div style='font-size:4rem'>🔮</div>"
            "<h2>AI Docstring Reviewer</h2>"
            "<p>Paste a .py path or folder in the sidebar and click <b>Load & Analyse</b>.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.stop()

    all_funcs = {f: extract_functions(s) for f, s in st.session_state.files.items()}
    total = sum(len(v) for v in all_funcs.values())
    missing = sum(1 for v in all_funcs.values() for fn in v if not fn["has_doc"])

    if st.session_state.is_demo:
        st.markdown("<div class='info-banner info-demo'>⚠️ <b>Demo mode</b> — saving won't update disk.</div>", unsafe_allow_html=True)
    else:
        lp = st.session_state.loaded_path
        st.markdown(f"<div class='info-banner info-live'>💾 <b>Live mode</b> — saves write to <code>{lp}</code></div>", unsafe_allow_html=True)

    # ── Stats row ──────────────────────────────────────────────────────────────
    coverage_pct = int((total - missing) / total * 100) if total else 0
    c1, c2, c3, c4 = st.columns(4)
    for col, num, label, icon, sub in [
        (c1, len(st.session_state.files), "Files Loaded",  "📁", "in scope"),
        (c2, total,                        "Functions",     "⚙️", "detected"),
        (c3, missing,                      "Missing Docs",  "⚠️", "need attention"),
        (c4, f"{coverage_pct}%",           "Coverage",      "✅", "documented"),
    ]:
        col.markdown(
            f"<div class='stat-card'><div class='stat-icon'>{icon}</div>"
            f"<div class='stat-num'>{num}</div>"
            f"<div class='stat-label'>{label}</div>"
            f"<div class='stat-sub'>{sub}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin:.9rem 0'></div>", unsafe_allow_html=True)
    left, right = st.columns([5, 7], gap="large")

    # ── Left: file + function tree ─────────────────────────────────────────────
    with left:
        st.markdown("<div class='banner banner-violet'>📁 Project Files</div>", unsafe_allow_html=True)
        for fname in st.session_state.files:
            funcs = all_funcs.get(fname, [])
            n_miss = sum(1 for fn in funcs if not fn["has_doc"])
            active = st.session_state.selected_file == fname
            ca, cb = st.columns([3, 1])
            with ca:
                if st.button(f"{'▶' if active else '📄'}  {fname}", key=f"f_{fname}", use_container_width=True):
                    st.session_state.selected_file = fname
                    st.session_state.selected_func = None
                    st.rerun()
            with cb:
                if n_miss:
                    st.markdown(f"<div class='badge badge-red'>⚠ {n_miss}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='badge badge-green'>✓ OK</div>", unsafe_allow_html=True)
            if active and funcs:
                with st.expander(f"  {len(funcs)} functions", expanded=True):
                    for fn in funcs:
                        icon = "🟢" if fn["has_doc"] else "🔴"
                        is_sel = st.session_state.selected_func == fn["name"]
                        if st.button(f"{'▶ ' if is_sel else '  '}{icon}  {fn['name']}()", key=f"fn_{fname}_{fn['name']}"):
                            st.session_state.selected_func = fn["name"]
                            st.rerun()

    # ── Right: review panel ────────────────────────────────────────────────────
    with right:
        st.markdown("<div class='banner banner-blue'>⚙️ Function Review</div>", unsafe_allow_html=True)
        sel_file = st.session_state.selected_file
        funcs_in = all_funcs.get(sel_file, []) if sel_file else []

        if not funcs_in:
            st.info("No functions found in the selected file.")
        else:
            func_names = [f["name"] for f in funcs_in]
            if st.session_state.selected_func not in func_names:
                st.session_state.selected_func = func_names[0]

            chosen = st.selectbox("Select function", func_names,
                                  index=func_names.index(st.session_state.selected_func),
                                  format_func=lambda n: f"● {n}", key="func_sel")
            if chosen != st.session_state.selected_func:
                st.session_state.selected_func = chosen
                st.rerun()

            func_data = next(f for f in funcs_in if f["name"] == chosen)
            cache_key = f"{sel_file}__{chosen}"
            if cache_key not in st.session_state.generated_docs:
                st.session_state.generated_docs[cache_key] = generate_docstring(func_data, doc_style)

            dc, gc = st.columns(2)
            with dc:
                if func_data["has_doc"]:
                    st.markdown("<div class='code-box-header'><span class='dot' style='background:#ff4d6d'></span><span class='dot' style='background:#ffb830'></span><span class='dot' style='background:#00ffaa'></span>&nbsp;&nbsp;📝 Current Docstring</div>", unsafe_allow_html=True)
                    st.markdown(f'<div class="code-box attached">"""\n{func_data["docstring"]}\n"""</div>', unsafe_allow_html=True)
                else:
                    st.markdown("<div class='code-box-header'><span class='dot' style='background:#ff4d6d'></span><span class='dot' style='background:#ffb830'></span><span class='dot' style='background:#00ffaa'></span>&nbsp;&nbsp;⚡ Inferred Description</div>", unsafe_allow_html=True)
                    auto = build_description(func_data)
                    st.markdown(f'<div class="code-box inferred attached"><span style="font-size:.67rem;font-style:italic">no docstring yet</span>\n\n"""\n{auto}\n"""</div>', unsafe_allow_html=True)

            with gc:
                st.markdown(f"<div class='code-box-header'><span class='dot' style='background:#ff4d6d'></span><span class='dot' style='background:#ffb830'></span><span class='dot' style='background:#00ffaa'></span>&nbsp;&nbsp;✨ Generated ({doc_style})</div>", unsafe_allow_html=True)
                edited = st.text_area("gen_edit", value=st.session_state.generated_docs[cache_key], height=215, key=f"edit_{cache_key}", label_visibility="collapsed")
                if edited != st.session_state.generated_docs[cache_key]:
                    st.session_state.generated_docs[cache_key] = edited

            st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin:.7rem 0'></div>", unsafe_allow_html=True)
            disk_path = st.session_state.file_paths.get(sel_file, "").strip()
            b1, b2, b3 = st.columns(3)

            with b1:
                if st.button("🔄 Regenerate", key="regen", use_container_width=True):
                    st.session_state.generated_docs.pop(cache_key, None)
                    st.rerun()
            with b2:
                if st.button("✅ Apply in Memory", key="apply", use_container_width=True):
                    new_src, err = inject_docstring(st.session_state.files[sel_file], chosen, st.session_state.generated_docs[cache_key])
                    if err:
                        st.error(err)
                    else:
                        st.session_state.files[sel_file] = new_src
                        st.toast("Applied in memory ✓", icon="✅")
                        st.rerun()
            with b3:
                if st.button("💾 Save to File", key="save_disk", use_container_width=True, disabled=not disk_path):
                    new_src, err = inject_docstring(st.session_state.files[sel_file], chosen, st.session_state.generated_docs[cache_key])
                    if err:
                        st.session_state.last_save[cache_key] = (False, err)
                    else:
                        ok, msg = _write_file(disk_path, new_src)
                        st.session_state.last_save[cache_key] = (ok, msg)
                        if ok:
                            st.session_state.files[sel_file] = new_src
                    st.rerun()

            save_res = st.session_state.last_save.get(cache_key)
            if save_res:
                ok, msg = save_res
                if ok:
                    st.markdown(f"<div class='save-ok'>💾 Saved → <code>{msg}</code></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='save-err'>❌ {msg}</div>", unsafe_allow_html=True)
            elif not disk_path:
                st.markdown("<div class='info-banner info-demo'>⚠️ Demo mode — paste your real file path to enable saving.</div>", unsafe_allow_html=True)

    # ── Source viewer ──────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**📂 Source Viewer** — reflects saved changes", unsafe_allow_html=True)
    src_tabs = st.tabs(list(st.session_state.files.keys()))
    for i, (fname, src) in enumerate(st.session_state.files.items()):
        with src_tabs[i]:
            p = st.session_state.file_paths.get(fname, "")
            if p:
                st.markdown(f"<div class='info-banner info-tip'>📁 <code>{p}</code></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='info-banner info-demo'>🧪 Demo file — no disk path</div>", unsafe_allow_html=True)
            st.code(src, language="python", line_numbers=True)

    # ── Bottom bar ─────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    ba1, ba2 = st.columns([3, 2])
    with ba1:
        saveable = {k: v for k, v in st.session_state.file_paths.items() if v.strip()}
        if st.button(f"💾 Save ALL {len(saveable)} file(s) to disk", use_container_width=True, disabled=not saveable):
            ok_n, errs = 0, []
            for fname, fpath in saveable.items():
                ok, msg = _write_file(fpath, st.session_state.files[fname])
                if ok:
                    ok_n += 1
                else:
                    errs.append(f"{fname}: {msg}")
            if ok_n:
                st.success(f"✅ Saved {ok_n} file(s).")
            for m in errs:
                st.error(f"❌ {m}")
    with ba2:
        st.download_button(
            "⬇ Export Docstrings JSON",
            data=json.dumps({"generated_at": datetime.now().isoformat(), "style": doc_style, "docstrings": st.session_state.generated_docs}, indent=2),
            file_name="review_logs.json", mime="application/json", use_container_width=True,
        )
