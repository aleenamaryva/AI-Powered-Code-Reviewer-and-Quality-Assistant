import streamlit as st
import ast
import re
import os
import json
import csv
import io
import textwrap
import zipfile
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Code Reviewer Pro",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# THEME / CSS INJECTION
# ═══════════════════════════════════════════════════════════════════════════════

def inject_dark_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:          #1a1f36;
  --bg2:         #222845;
  --bg3:         #2a3158;
  --bg4:         #323c6a;
  --border:      rgba(140,160,255,0.2);
  --border-hi:   rgba(140,160,255,0.5);
  --indigo:      #7c83fd;
  --indigo-lt:   #a5aaff;
  --sky:         #48cae4;
  --sky-dim:     rgba(72,202,228,0.18);
  --coral:       #ff6b6b;
  --coral-dim:   rgba(255,107,107,0.18);
  --mint:        #51e5a0;
  --mint-dim:    rgba(81,229,160,0.18);
  --amber:       #ffd166;
  --amber-dim:   rgba(255,209,102,0.18);
  --violet:      #c77dff;
  --violet-dim:  rgba(199,125,255,0.18);
  --text:        #eef0ff;
  --text-mid:    #b8bde8;
  --text-dim:    #7880b0;
  --radius:      12px;
  --radius-lg:   18px;
}

@keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
@keyframes pulse  { 0%,100%{opacity:.8} 50%{opacity:1} }

html,body,[class*="css"] {
  font-family:'Inter',sans-serif !important;
  background:#1a1f36 !important;
  color:var(--text) !important;
}
.stApp { background:#1a1f36 !important; }
.main .block-container {
  padding:2rem 2.5rem !important;
  max-width:1400px !important;
  animation:fadeUp .4s ease;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#141828 0%,#1a1f36 100%) !important;
  border-right:1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color:var(--text) !important; }

.app-title { display:flex;align-items:center;gap:.85rem;padding:.5rem .4rem 1.2rem;border-bottom:1px solid var(--border);margin-bottom:1.3rem; }
.app-title-dot { width:40px;height:40px;border-radius:12px;flex-shrink:0;background:linear-gradient(135deg,#7c83fd,#48cae4);display:flex;align-items:center;justify-content:center;font-size:1.2rem;box-shadow:0 4px 20px rgba(124,131,253,.5); }
.app-title-text { font-weight:800;font-size:1.05rem;color:#eef0ff;letter-spacing:-.02em; }
.app-title-sub  { font-size:.6rem;color:var(--text-dim);letter-spacing:.14em;text-transform:uppercase;font-weight:600;margin-top:2px;font-family:'JetBrains Mono',monospace; }

.section-label { font-size:.6rem;text-transform:uppercase;letter-spacing:.18em;color:var(--text-mid);margin:.4rem 0 .7rem;font-weight:700;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;gap:.5rem; }
.section-label::after { content:'';flex:1;height:1px;background:linear-gradient(90deg,var(--border),transparent); }

/* ── Selectbox/Radio ── */
[data-testid="stSelectbox"] > div > div {
  background:var(--bg2) !important;border:1px solid var(--border) !important;
  border-radius:var(--radius) !important;color:var(--text) !important;font-size:.85rem !important;
}
[data-testid="stRadio"] > div { gap:.35rem !important;flex-direction:column !important; }
[data-testid="stRadio"] label {
  background:var(--bg2) !important;border:1px solid var(--border) !important;
  border-radius:var(--radius) !important;padding:.55rem 1rem !important;
  font-size:.83rem !important;font-weight:600 !important;color:var(--text-mid) !important;
  transition:all .2s !important;cursor:pointer !important;
}
[data-testid="stRadio"] label:hover { border-color:var(--indigo-lt) !important;color:var(--text) !important;background:var(--bg3) !important; }
[data-testid="stRadio"] label:has(input:checked) {
  border-color:var(--indigo) !important;background:rgba(124,131,253,.15) !important;color:var(--indigo-lt) !important;
  box-shadow:0 0 0 3px rgba(124,131,253,.12) !important;
}

/* ── Buttons ── */
.stButton > button {
  background:linear-gradient(135deg,#7c83fd,#9b59f5) !important;
  color:#fff !important;border:none !important;border-radius:var(--radius) !important;
  font-weight:700 !important;font-size:.85rem !important;padding:.5rem 1.4rem !important;
  font-family:'Inter',sans-serif !important;letter-spacing:.01em !important;
  transition:all .2s !important;box-shadow:0 4px 18px rgba(124,131,253,.35) !important;
}
.stButton > button:hover { transform:translateY(-2px) !important;box-shadow:0 8px 26px rgba(124,131,253,.5) !important;filter:brightness(1.08) !important; }
.stButton > button:active { transform:translateY(0) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input {
  background:var(--bg2) !important;border:1.5px solid var(--border) !important;
  border-radius:var(--radius) !important;color:var(--text) !important;
  font-family:'JetBrains Mono',monospace !important;font-size:.82rem !important;
}
.stTextInput > div > div > input:focus { border-color:var(--indigo) !important;box-shadow:0 0 0 3px rgba(124,131,253,.2) !important; }
.stTextInput > div > div > input::placeholder { color:var(--text-dim) !important; }
.stTextArea textarea {
  background:var(--bg2) !important;border:1.5px solid var(--border) !important;
  border-radius:var(--radius) !important;color:var(--mint) !important;
  font-family:'JetBrains Mono',monospace !important;font-size:.8rem !important;
}
.stTextArea textarea:focus { border-color:var(--indigo) !important;box-shadow:0 0 0 3px rgba(124,131,253,.2) !important; }

/* ── Labels & general text ── */
label, .stSelectbox label, .stTextInput label, .stTextArea label,
.stRadio label, .stCheckbox label, .stFileUploader label {
  color:var(--text-mid) !important;font-weight:600 !important;font-size:.84rem !important;
}
p, span, div { color:var(--text) !important; }

/* ── Metrics ── */
[data-testid="stMetric"] {
  background:var(--bg2) !important;border:1px solid var(--border) !important;
  border-radius:var(--radius-lg) !important;padding:1.1rem 1.3rem !important;
}
[data-testid="stMetricLabel"] { font-size:.65rem !important;color:var(--text-mid) !important;font-weight:700 !important;letter-spacing:.1em !important;text-transform:uppercase !important;font-family:'JetBrains Mono',monospace !important; }
[data-testid="stMetricValue"] { font-size:1.9rem !important;font-weight:900 !important;color:var(--indigo-lt) !important;-webkit-text-fill-color:var(--indigo-lt) !important; }

/* ── Tabs ── */
[data-testid="stTabs"] button { font-family:'Inter',sans-serif !important;font-weight:700 !important;font-size:.84rem !important;color:var(--text-mid) !important;border-radius:0 !important;padding:.65rem 1.3rem !important;transition:all .2s !important;background:transparent !important;border:none !important; }
[data-testid="stTabs"] button:hover { color:var(--indigo-lt) !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color:var(--indigo-lt) !important;border-bottom:2.5px solid var(--indigo) !important; }

/* ── Expanders ── */
[data-testid="stExpander"] { background:var(--bg2) !important;border:1px solid var(--border) !important;border-radius:var(--radius) !important;margin-bottom:.5rem !important; }
[data-testid="stExpander"] summary { font-weight:700 !important;font-size:.86rem !important;color:var(--text) !important; }
[data-testid="stExpander"] p { color:var(--text-mid) !important; }

/* ── Progress ── */
.stProgress > div { background:var(--bg3) !important;border-radius:6px !important;height:7px !important; }
.stProgress > div > div { background:linear-gradient(90deg,var(--indigo),var(--sky)) !important;border-radius:6px !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] { background:var(--bg2) !important;border:1.5px dashed var(--border-hi) !important;border-radius:var(--radius) !important; }
[data-testid="stFileUploader"] * { color:var(--text) !important; }

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
  background:linear-gradient(135deg,#2a3158,#323c6a) !important;border:1.5px solid var(--border-hi) !important;
  color:var(--sky) !important;border-radius:var(--radius) !important;font-weight:700 !important;font-size:.85rem !important;
}
[data-testid="stDownloadButton"] button:hover { background:linear-gradient(135deg,#7c83fd,#9b59f5) !important;color:#fff !important;border-color:transparent !important;transform:translateY(-2px) !important; }

/* ── DataFrame ── */
[data-testid="stDataFrame"] { border:1px solid var(--border) !important;border-radius:var(--radius) !important; }

/* ── Stat cards ── */
.stat-card {
  background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-lg);
  padding:1.4rem;text-align:center;position:relative;overflow:hidden;
  transition:all .25s;animation:fadeUp .4s ease;
}
.stat-card:hover { transform:translateY(-3px);box-shadow:0 14px 36px rgba(0,0,0,.35);border-color:var(--border-hi); }
.stat-num { font-size:2.4rem;font-weight:900;line-height:1;color:var(--indigo-lt); }
.stat-label { font-size:.63rem;color:var(--text-mid);text-transform:uppercase;letter-spacing:.15em;margin-top:.5rem;font-weight:700;font-family:'JetBrains Mono',monospace; }
.stat-sub { font-size:.72rem;color:var(--text-mid);margin-top:.2rem; }
.stat-icon { font-size:1.5rem;margin-bottom:.4rem; }

/* ── Banners ── */
.banner { border-radius:var(--radius-lg);padding:1.1rem 1.6rem;font-weight:700;font-size:.96rem;margin-bottom:1.2rem;display:flex;align-items:center;gap:.8rem;position:relative;overflow:hidden; }
.banner-violet { background:linear-gradient(135deg,rgba(199,125,255,.2),rgba(124,131,253,.15));border:1px solid rgba(199,125,255,.4);color:#ddb8ff; }
.banner-blue   { background:linear-gradient(135deg,rgba(72,202,228,.18),rgba(124,131,253,.12));border:1px solid rgba(72,202,228,.4);color:#90e5f8; }
.banner-teal   { background:linear-gradient(135deg,rgba(81,229,160,.18),rgba(72,202,228,.12));border:1px solid rgba(81,229,160,.4);color:#90f0c4; }
.banner-rose   { background:linear-gradient(135deg,rgba(255,107,107,.18),rgba(255,209,102,.12));border:1px solid rgba(255,107,107,.4);color:#ffaaaa; }
.banner-green  { background:linear-gradient(135deg,rgba(81,229,160,.18),rgba(72,202,228,.12));border:1px solid rgba(81,229,160,.4);color:#90f0c4; }

/* ── Badges ── */
.badge { border-radius:20px;padding:3px 12px;font-size:.67rem;font-weight:700;font-family:'JetBrains Mono',monospace;white-space:nowrap;letter-spacing:.04em;display:inline-block; }
.badge-red    { background:rgba(255,107,107,.2);color:#ff9090;border:1px solid rgba(255,107,107,.4); }
.badge-green  { background:rgba(81,229,160,.2);color:#80f5c0;border:1px solid rgba(81,229,160,.4); }
.badge-amber  { background:rgba(255,209,102,.2);color:#ffe080;border:1px solid rgba(255,209,102,.4); }
.badge-blue   { background:rgba(72,202,228,.2);color:#80dff0;border:1px solid rgba(72,202,228,.4); }
.badge-yes    { background:rgba(81,229,160,.2);color:#80f5c0;border:1px solid rgba(81,229,160,.4);border-radius:20px;padding:3px 12px;font-size:.73rem;font-weight:700; }
.badge-no     { background:rgba(255,107,107,.2);color:#ff9090;border:1px solid rgba(255,107,107,.4);border-radius:20px;padding:3px 12px;font-size:.73rem;font-weight:700; }

/* ── Code box ── */
.code-box {
  background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);
  padding:1.2rem 1.4rem;font-family:'JetBrains Mono',monospace;font-size:.78rem;
  line-height:1.85;white-space:pre-wrap;min-height:175px;color:var(--mint);tab-size:4;
}
.code-box.inferred { color:var(--sky);border-color:rgba(72,202,228,.3); }
.code-box-header { background:var(--bg3);border:1px solid var(--border);border-bottom:none;border-radius:var(--radius) var(--radius) 0 0;padding:.5rem 1.2rem;font-family:'JetBrains Mono',monospace;font-size:.67rem;color:var(--text-mid);display:flex;align-items:center;gap:.5rem; }
.code-box-header .dot { width:10px;height:10px;border-radius:50%;display:inline-block; }
.code-box.attached { border-radius:0 0 var(--radius) var(--radius);min-height:160px; }

/* ── Info banners ── */
.info-banner { border-radius:var(--radius);padding:.8rem 1.2rem;font-size:.82rem;display:flex;align-items:flex-start;gap:.55rem;line-height:1.65;margin:.5rem 0;font-family:'JetBrains Mono',monospace; }
.info-live  { background:rgba(81,229,160,.15);border:1px solid rgba(81,229,160,.4);color:#80f5c0; }
.info-demo  { background:rgba(255,209,102,.15);border:1px solid rgba(255,209,102,.4);color:#ffe080; }
.info-tip   { background:rgba(72,202,228,.15);border:1px solid rgba(72,202,228,.4);color:#90e5f8; }

/* ── Func card ── */
.func-card { background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-lg);padding:1.2rem 1.4rem;margin-bottom:1rem;font-family:'JetBrains Mono',monospace;position:relative;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,.2);animation:fadeUp .3s ease;transition:border-color .2s; }
.func-card:hover { border-color:var(--indigo-lt); }
.func-name   { color:var(--sky);font-size:.97rem;font-weight:500; }
.func-lineno { font-size:.63rem;color:var(--text-mid);background:var(--bg3);border:1px solid var(--border);border-radius:6px;padding:2px 8px; }

/* ── Save/err ── */
.save-ok { background:rgba(81,229,160,.15);border:1px solid rgba(81,229,160,.4);border-radius:var(--radius);padding:.85rem 1.2rem;color:#80f5c0;font-family:'JetBrains Mono',monospace;font-size:.78rem;margin-top:.7rem;word-break:break-all;line-height:1.7;animation:fadeUp .3s ease; }
.save-err { background:rgba(255,107,107,.15);border:1px solid rgba(255,107,107,.4);border-radius:var(--radius);padding:.85rem 1.2rem;color:#ff9090;font-family:'JetBrains Mono',monospace;font-size:.78rem;margin-top:.7rem;animation:fadeUp .3s ease; }

/* ── Path card ── */
.path-card { background:var(--bg2);border:1px solid rgba(72,202,228,.25);border-radius:var(--radius);padding:1.1rem 1.2rem;margin-bottom:.9rem;position:relative;overflow:hidden; }
.demo-card { background:var(--bg);border:1px dashed var(--border);border-radius:var(--radius);padding:.9rem 1.1rem;margin-top:.6rem; }

/* ── Hero ── */
.hero-glyph { width:82px;height:82px;margin:0 auto 1.5rem;background:var(--bg2);border:2px solid rgba(124,131,253,.5);border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:2.2rem;box-shadow:0 0 40px rgba(124,131,253,.3);animation:pulse 4s ease-in-out infinite; }

/* ── Tables ── */
.review-table { width:100%;border-collapse:collapse;border-radius:var(--radius-lg);overflow:hidden;background:var(--bg2); }
.review-table thead tr { background:linear-gradient(135deg,#4a51c4,#6b2fa0); }
.review-table th { padding:.95rem 1.3rem;text-align:left;font-size:.78rem;font-weight:700;letter-spacing:.06em;color:#fff;font-family:'JetBrains Mono',monospace; }
.review-table td { padding:.85rem 1.3rem;font-size:.83rem;border-bottom:1px solid var(--border);color:var(--text-mid);background:var(--bg2);font-family:'JetBrains Mono',monospace; }
.review-table tr:hover td { background:var(--bg3);color:var(--text); }

/* ── Search results ── */
.search-result { background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:.95rem 1.3rem;margin-bottom:.5rem;display:flex;justify-content:space-between;align-items:center;transition:all .2s; }
.search-result:hover { border-color:var(--indigo-lt);background:var(--bg3); }
.search-result-file { font-size:.76rem;color:var(--text-mid);font-family:'JetBrains Mono',monospace; }
.search-result-fn   { font-weight:700;font-size:.87rem;color:var(--text); }

/* ── Stat cards row ── */
.stat-cards-row-sm { display:flex;gap:.8rem;margin-bottom:1rem; }
.stat-card-sm { flex:1;border-radius:var(--radius);padding:1.1rem;text-align:center;color:#fff; }
.stat-card-blue-sm   { background:linear-gradient(135deg,#4a51c4,#6b2fa0);border:1px solid rgba(124,131,253,.35); }
.stat-card-purple-sm { background:linear-gradient(135deg,#6b2fa0,#9b59b6);border:1px solid rgba(199,125,255,.35); }
.stat-number-sm { font-size:2rem;font-weight:900;line-height:1; }
.stat-label-sm  { font-size:.71rem;opacity:.9;margin-top:.3rem;font-family:'JetBrains Mono',monospace;letter-spacing:.1em;text-transform:uppercase; }

/* ── Test rows ── */
.test-row { display:flex;align-items:center;justify-content:space-between;background:rgba(81,229,160,.15);border:1px solid rgba(81,229,160,.35);border-radius:var(--radius);padding:.85rem 1.3rem;margin-bottom:.5rem;font-weight:700;font-size:.87rem;color:#80f5c0; }
.test-row-fail { background:rgba(255,107,107,.15);border-color:rgba(255,107,107,.35);color:#ff9090; }

/* ── Filter/feature banners ── */
.feature-banner { background:linear-gradient(135deg,#4a51c4,#6b2fa0);border-radius:var(--radius-lg);padding:1.3rem 1.8rem;margin-bottom:1.2rem; }
.feature-banner h3 { color:#fff;font-size:1.2rem;font-weight:800;margin:0 0 .3rem; }
.feature-banner p  { color:rgba(255,255,255,.82);font-size:.86rem;margin:0; }
.filter-banner { background:linear-gradient(135deg,#4a51c4,#6b2fa0);border-radius:var(--radius-lg);padding:1.2rem 1.8rem;margin-bottom:1.2rem; }
.filter-banner h3 { color:#fff;font-size:1.1rem;font-weight:800;margin:0 0 .2rem; }
.filter-banner p  { color:rgba(255,255,255,.82);font-size:.83rem;margin:0; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:5px;height:5px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--indigo);border-radius:4px; }
hr { border-color:var(--border) !important; }
.stCaption,small { color:var(--text-mid) !important;font-family:'JetBrains Mono',monospace !important; }

/* ── Nav cards ── */
.nc-outer { position:relative;margin-bottom:0; }
.nc-visual { border-radius:16px;padding:1.6rem 1rem 1.4rem;text-align:center;pointer-events:none;position:relative;z-index:1;transition:transform .2s,box-shadow .2s; }
.nc-icon { font-size:2.8rem;line-height:1;margin-bottom:.5rem; }
.nc-name { font-weight:800;font-size:.96rem;color:#fff;margin-bottom:.25rem; }
.nc-sub  { font-size:.76rem;color:rgba(255,255,255,.85); }
.nc-outer:hover .nc-visual { transform:translateY(-4px);box-shadow:0 14px 36px rgba(0,0,0,.4); }
.nc-visual.nc-active { outline:3px solid rgba(255,255,255,.8);outline-offset:-3px; }
.nc-btn-wrap > div > button {
  position:absolute !important;inset:0 !important;width:100% !important;
  height:100% !important;opacity:0 !important;cursor:pointer !important;
  z-index:2 !important;border:none !important;background:transparent !important;
  border-radius:16px !important;
}
</style>
""", unsafe_allow_html=True)

def inject_light_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

html,body,[class*="css"] { font-family:'Inter',sans-serif !important;background:#f0f2f8 !important;color:#1e2147 !important; }
.stApp { background:#f0f2f8 !important; }
.main,.main .block-container { background:#f0f2f8 !important;padding:2rem 2.5rem;max-width:1300px; }

[data-testid="stSidebar"] { background:#ffffff !important;border-right:1px solid #d4d8f0 !important; }
[data-testid="stSidebar"] * { color:#1e2147 !important;background-color:transparent !important; }

[data-testid="stFileUploader"] { background:#fff !important;border:2px dashed #b8bee8 !important;border-radius:12px !important; }
[data-testid="stFileUploader"] * { color:#1e2147 !important;background-color:transparent !important; }

[data-testid="stTextInput"] input,[data-testid="stSelectbox"] > div > div,div[data-baseweb="select"] > div {
  background:#fff !important;border:1.5px solid #c8ceec !important;border-radius:10px !important;font-size:.85rem !important;color:#1e2147 !important;
}
[data-testid="stMetric"] { background:#fff !important;border:1px solid #d4d8f0 !important;border-radius:14px !important;padding:1.1rem 1.3rem !important; }
[data-testid="stMetricLabel"] { font-size:.65rem !important;color:#5c6296 !important;font-weight:700 !important;letter-spacing:.1em !important;text-transform:uppercase !important; }
[data-testid="stMetricValue"] { font-size:1.9rem !important;font-weight:900 !important;color:#4a51c4 !important; }
.stAlert { background:#fff !important;border-radius:12px !important;color:#1e2147 !important; }
[data-testid="stExpander"] { background:#fff !important;border:1px solid #d4d8f0 !important;border-radius:12px !important; }
[data-testid="stExpander"] * { color:#1e2147 !important;background-color:transparent !important; }
[data-testid="stExpander"] summary { color:#1e2147 !important;font-weight:700 !important; }

.stButton > button { background:linear-gradient(135deg,#4a51c4,#7c3aed) !important;color:#fff !important;border:none !important;border-radius:10px !important;font-weight:700 !important;font-size:.85rem !important;padding:.5rem 1.4rem !important;box-shadow:0 4px 16px rgba(74,81,196,.3) !important;transition:all .2s !important; }
.stButton > button:hover { transform:translateY(-2px) !important;box-shadow:0 8px 22px rgba(74,81,196,.4) !important; }
.stDownloadButton > button { background:linear-gradient(135deg,#4a51c4,#7c3aed) !important;color:#fff !important;border:none !important;border-radius:10px !important;font-weight:700 !important; }
.stDownloadButton > button:hover { transform:translateY(-2px) !important;box-shadow:0 8px 22px rgba(74,81,196,.4) !important; }
.stMarkdown p,.stMarkdown div,.stMarkdown span { color:#1e2147 !important; }

p,span,label { color:#1e2147 !important; }

::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:#f0f2f8; }
::-webkit-scrollbar-thumb { background:#a0a8e0;border-radius:4px; }

.review-table { width:100%;border-collapse:collapse;border-radius:14px;overflow:hidden;background:#fff;box-shadow:0 2px 12px rgba(74,81,196,.08); }
.review-table thead tr { background:linear-gradient(135deg,#4a51c4,#6b2fa0);color:#fff; }
.review-table th { padding:.9rem 1.2rem;text-align:left;font-size:.8rem;font-weight:700;letter-spacing:.05em; }
.review-table td { padding:.8rem 1.2rem;font-size:.85rem;border-bottom:1px solid #eef0f8;color:#1e2147;background:#fff; }
.review-table tr:hover td { background:#f5f3ff;color:#1e2147; }
.badge-yes { background:#dcfce7;color:#15803d;border-radius:20px;padding:.2rem .75rem;font-size:.74rem;font-weight:700;border:1px solid #86efac; }
.badge-no  { background:#fee2e2;color:#b91c1c;border-radius:20px;padding:.2rem .75rem;font-size:.74rem;font-weight:700;border:1px solid #fca5a5; }

.search-result { background:#fff;border:1px solid #d4d8f0;border-radius:12px;padding:.9rem 1.2rem;margin-bottom:.5rem;display:flex;justify-content:space-between;align-items:center;transition:all .2s; }
.search-result:hover { border-color:#7c83fd;box-shadow:0 4px 16px rgba(74,81,196,.12); }
.search-result-file { font-size:.76rem;color:#5c6296;font-family:'JetBrains Mono',monospace; }
.search-result-fn   { font-weight:700;font-size:.87rem;color:#1e2147; }

.stat-cards-row-sm { display:flex;gap:1rem;margin-bottom:1.2rem; }
.stat-card-sm { flex:1;border-radius:12px;padding:1.2rem;text-align:center;color:#fff; }
.stat-card-blue-sm   { background:linear-gradient(135deg,#4a51c4,#6b2fa0); }
.stat-card-purple-sm { background:linear-gradient(135deg,#6b2fa0,#9b59b6); }
.stat-number-sm { font-size:2rem;font-weight:900;line-height:1; }
.stat-label-sm  { font-size:.78rem;opacity:.9;margin-top:.3rem; }

.test-row { display:flex;align-items:center;justify-content:space-between;background:#dcfce7;border:1px solid #86efac;border-radius:10px;padding:.8rem 1.2rem;margin-bottom:.5rem;font-weight:700;font-size:.88rem;color:#15803d; }
.test-row-fail { background:#fee2e2;border-color:#fca5a5;color:#b91c1c; }
.feature-banner { background:linear-gradient(135deg,#4a51c4,#6b2fa0);border-radius:14px;padding:1.3rem 1.8rem;margin-bottom:1.2rem; }
.feature-banner h3 { color:#fff;font-size:1.2rem;font-weight:800;margin:0 0 .3rem; }
.feature-banner p  { color:rgba(255,255,255,.85);font-size:.85rem;margin:0; }
.filter-banner { background:linear-gradient(135deg,#4a51c4,#6b2fa0);border-radius:14px;padding:1.2rem 1.8rem;margin-bottom:1.2rem; }
.filter-banner h3 { color:#fff;font-size:1.1rem;font-weight:800;margin:0 0 .2rem; }
.filter-banner p  { color:rgba(255,255,255,.85);font-size:.82rem;margin:0; }

/* ── Nav cards ── */
.nc-outer { position:relative;margin-bottom:0; }
.nc-visual { border-radius:16px;padding:1.6rem 1rem 1.4rem;text-align:center;pointer-events:none;position:relative;z-index:1;transition:transform .2s,box-shadow .2s; }
.nc-icon { font-size:2.8rem;line-height:1;margin-bottom:.5rem; }
.nc-name { font-weight:800;font-size:.96rem;color:#fff;margin-bottom:.25rem; }
.nc-sub  { font-size:.76rem;color:rgba(255,255,255,.88); }
.nc-outer:hover .nc-visual { transform:translateY(-4px);box-shadow:0 14px 36px rgba(0,0,0,.2); }
.nc-visual.nc-active { outline:3px solid rgba(255,255,255,.9);outline-offset:-3px; }
.nc-btn-wrap > div > button {
  position:absolute !important;inset:0 !important;width:100% !important;
  height:100% !important;opacity:0 !important;cursor:pointer !important;
  z-index:2 !important;border:none !important;background:transparent !important;
  border-radius:16px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Matplotlib global dark theme ─────────────────────────────────────────────
matplotlib.rcParams.update({
    "figure.facecolor":  "#060818",
    "axes.facecolor":    "#03040d",
    "axes.edgecolor":    "#0e1530",
    "axes.labelcolor":   "#3a5080",
    "xtick.color":       "#2a3a60",
    "ytick.color":       "#2a3a60",
    "text.color":        "#7a8db0",
    "grid.color":        "#0e1530",
    "grid.linestyle":    "--",
    "grid.alpha":        0.5,
    "axes.titlecolor":   "#7a8db0",
    "figure.titlesize":  11,
    "font.family":       "monospace",
})

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
for k, v in {
    # App1 reviewer state
    "files": {}, "file_paths": {}, "loaded_path": "",
    "reviewer_scanned": False, "is_demo": False,
    "selected_file": None, "selected_func": None,
    "generated_docs": {}, "last_save": {},
    "code_content": "", "current_file": None,
    "pep_mode": False, "dashboard_mode": False,
    # App2 scanner state
    "scan_results": [], "test_summary": {}, "scan_done": False,
    "expanded_card": None,
    # Shared
    "dark_mode": True,
    "top_mode": "🏠 Home",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Apply theme
if st.session_state.dark_mode:
    inject_dark_css()
else:
    inject_light_css()

# ═══════════════════════════════════════════════════════════════════════════════
# SHARED UTILITIES — App1
# ═══════════════════════════════════════════════════════════════════════════════
def calc_pct(total, part):
    return round((part / total) * 100, 1) if total else 0.0

def docstring_badge(has_docstring_val: bool) -> str:
    if has_docstring_val:
        return "<span class='badge badge-green'>✔ Yes</span>"
    return "<span class='badge badge-red'>✖ No</span>"

def calculate_complexity(node):
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.While,
                               ast.Try, ast.With, ast.BoolOp)):
            complexity += 1
    return complexity

FUNCTION_NODE_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)

def analyze_code(code):
    try:
        tree = ast.parse(code)
    except Exception as e:
        return None, None, False, str(e)
    functions, classes = [], []
    module_docstring = ast.get_docstring(tree) is not None
    for node in ast.walk(tree):
        if isinstance(node, FUNCTION_NODE_TYPES):
            functions.append({
                "Name": node.name, "Type": "Function",
                "Kind": "async" if isinstance(node, ast.AsyncFunctionDef) else "sync",
                "Start Line": node.lineno, "End Line": node.end_lineno,
                "Complexity": calculate_complexity(node),
                "Has Docstring": ast.get_docstring(node) is not None,
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "Name": node.name, "Type": "Class",
                "Start Line": node.lineno, "End Line": node.end_lineno,
                "Complexity": calculate_complexity(node),
                "Has Docstring": ast.get_docstring(node) is not None,
            })
    return functions, classes, module_docstring, None

def fix_with_regex(func_name, current_code):
    lines = current_code.splitlines()
    fixed_lines = []
    pattern = re.compile(rf"^\s*def\s+{func_name}\s*\(.*?\)\s*:")
    for i, line in enumerate(lines):
        fixed_lines.append(line)
        if pattern.match(line):
            if i + 1 < len(lines) and '"""' in lines[i + 1]:
                continue
            indent = " " * (len(line) - len(line.lstrip()) + 4)
            fixed_lines.append(f'{indent}"""{func_name.replace("_", " ").capitalize()} function."""')
    return "\n".join(fixed_lines)

VERB_MAP = {
    "get":"Retrieves","fetch":"Fetches","load":"Loads","read":"Reads",
    "set":"Sets","put":"Stores","save":"Saves","write":"Writes","store":"Stores",
    "update":"Updates","edit":"Edits","modify":"Modifies","patch":"Patches",
    "delete":"Deletes","remove":"Removes","clear":"Clears","reset":"Resets",
    "create":"Creates","make":"Creates","build":"Builds","generate":"Generates",
    "add":"Adds","insert":"Inserts","append":"Appends","push":"Appends",
    "check":"Checks","validate":"Validates","verify":"Verifies","is":"Checks if",
    "has":"Checks whether","can":"Determines whether",
    "find":"Finds","search":"Searches for","lookup":"Looks up","query":"Queries",
    "filter":"Filters","sort":"Sorts","parse":"Parses","decode":"Decodes","encode":"Encodes",
    "format":"Formats","render":"Renders","display":"Displays","show":"Shows",
    "send":"Sends","post":"Posts","upload":"Uploads","download":"Downloads",
    "export":"Exports","convert":"Converts","transform":"Transforms",
    "compute":"Computes","calculate":"Calculates","process":"Processes",
    "run":"Runs","execute":"Executes","start":"Starts","stop":"Stops",
    "open":"Opens","close":"Closes","connect":"Connects to",
    "log":"Logs","print":"Prints","init":"Initializes","setup":"Sets up",
    "configure":"Configures","handle":"Handles","test":"Tests",
    "merge":"Merges","split":"Splits","join":"Joins","combine":"Combines",
    "count":"Counts","sum":"Computes the sum of","average":"Calculates the average of",
    "min":"Returns the minimum of","max":"Returns the maximum of",
    "list":"Lists","collect":"Collects","encrypt":"Encrypts","decrypt":"Decrypts",
    "hash":"Hashes","draw":"Draws","plot":"Plots","resize":"Resizes","crop":"Crops",
    "notify":"Notifies","compare":"Compares","evaluate":"Evaluates",
}

def _words(name):
    name = re.sub(r'([A-Z])', r'_\1', name).lower()
    return [w for w in re.split(r'[_\s]+', name) if w]

def _humanize(name):
    return " ".join(_words(name))

def smart_description(func_name, args):
    words    = _words(func_name)
    filtered = [a for a in args if a not in ("self","cls")]
    if not words:
        return f"Performs the {func_name} operation."
    verb_word, rest = words[0], words[1:]
    verb = VERB_MAP.get(verb_word)
    obj  = " ".join(rest) if rest else None
    if verb:
        desc = f"{verb} the {obj}" if obj else (f"{verb} {filtered[0]}" if filtered else f"{verb}s")
    else:
        desc = f"Performs {_humanize(func_name)}"
    desc = desc[0].upper() + desc[1:]
    if not desc.endswith("."): desc += "."
    if filtered:
        desc += "\n\nTakes " + ", ".join(f"`{a}`" for a in filtered) + " as input."
    return desc

def extract_functions(source):
    funcs = []
    src_lines = source.splitlines()
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, FUNCTION_NODE_TYPES):
                doc  = ast.get_docstring(node) or ""
                args = [a.arg for a in node.args.args]
                arg_types = {}
                for a in node.args.args:
                    if a.annotation:
                        try: arg_types[a.arg] = ast.unparse(a.annotation)
                        except: pass
                return_type = ""
                if node.returns:
                    try: return_type = ast.unparse(node.returns)
                    except: pass
                start = node.body[0].lineno - 1
                end   = getattr(node, "end_lineno", start + 10)
                body_lines = [l.strip() for l in src_lines[start:end] if l.strip()
                              and not l.strip().startswith('"""')
                              and not l.strip().startswith("'''")]
                funcs.append({
                    "name": node.name, "args": args, "lineno": node.lineno,
                    "docstring": doc, "has_doc": bool(doc.strip()),
                    "arg_types": arg_types, "return_type": return_type,
                    "body_lines": body_lines,
                })
    except SyntaxError:
        pass
    return funcs

def build_description(func):
    name        = func["name"]
    args        = func["args"]
    arg_types   = func.get("arg_types", {})
    return_type = func.get("return_type", "")
    body        = " ".join(func.get("body_lines", []))
    filtered    = [a for a in args if a not in ("self","cls")]
    words     = _words(name)
    verb_word = words[0] if words else ""
    rest      = words[1:]
    verb      = VERB_MAP.get(verb_word)
    obj       = " ".join(rest) if rest else None
    if verb:
        desc = f"{verb} the {obj}" if obj else (f"{verb} {filtered[0]}" if filtered else f"{verb}s")
    else:
        desc = f"Performs {_humanize(name)}"
    if filtered and arg_types:
        type_counts: dict = {}
        for a in filtered:
            t = arg_types.get(a, "")
            if t: type_counts[t] = type_counts.get(t, 0) + 1
        def _article(t): return "an" if t[0].lower() in "aeiou" else "a"
        if type_counts:
            parts = []
            for t, count in type_counts.items():
                num_word = {1:"a",2:"two",3:"three",4:"four"}.get(count, str(count))
                parts.append(f"{_article(t)} {t}" if count == 1 else f"{num_word} {t}s")
            type_phrase = " and ".join(parts)
            if verb:
                desc = f"{verb} {type_phrase}" if not obj else f"{verb} the {obj} of {type_phrase}"
            else:
                desc = f"Performs {_humanize(name)} on {type_phrase}"
    if return_type and return_type not in ("None","none",""):
        desc += f" and returns a {return_type}"
    body_lower = body.lower()
    if "raise" in body_lower or "raises" in body_lower:
        desc += ". May raise exceptions on invalid input"
    if "open(" in body_lower or "read(" in body_lower or "write(" in body_lower:
        desc += ". Performs file I/O"
    if "request" in body_lower or "http" in body_lower or "urllib" in body_lower:
        desc += ". Makes network requests"
    desc = desc[0].upper() + desc[1:]
    if not desc.endswith("."): desc += "."
    return desc

def generate_docstring(func, style):
    name        = func["name"]
    args        = func["args"]
    arg_types   = func.get("arg_types", {})
    return_type = func.get("return_type", "")
    filtered    = [a for a in args if a not in ("self","cls")]
    summary     = build_description(func)
    def _ret_type(): return return_type if return_type else _humanize(name)
    if style == "GOOGLE":
        lines = ['"""', summary, ""]
        if filtered:
            lines += ["Args:"]
            for a in filtered:
                t = arg_types.get(a, "")
                lines.append(f"    {a}{' (' + t + ')' if t else ''}: The {_humanize(a)} value.")
        lines += ["", "Returns:", f"    {_ret_type()}: Result of {_humanize(name)}.", '"""']
    elif style == "NUMPY":
        lines = ['"""', summary, "", "Parameters", "----------"]
        for a in filtered:
            t = arg_types.get(a, "any")
            lines += [f"{a} : {t}", f"    The {_humanize(a)} value."]
        lines += ["","Returns","-------", return_type if return_type else "any",
                  f"    Result of {_humanize(name)}.", '"""']
    else:
        lines = ['"""', summary, ""]
        for a in filtered:
            t = arg_types.get(a, "")
            lines.append(f":param {a}: The {_humanize(a)} value.")
            if t: lines.append(f":type {a}: {t}")
        if return_type: lines.append(f":rtype: {return_type}")
        lines += [f":returns: Result of {_humanize(name)}.", '"""']
    return "\n".join(lines)

def inject_docstring(source, func_name, new_doc_raw):
    try: tree = ast.parse(source)
    except SyntaxError: return source, "SyntaxError: could not parse file"
    lines = source.splitlines(keepends=True)
    for node in ast.walk(tree):
        if isinstance(node, FUNCTION_NODE_TYPES) and node.name == func_name:
            body_line = lines[node.body[0].lineno - 1]
            indent = ""
            for ch in body_line:
                if ch in (" ", "\t"): indent += ch
                else: break
            clean = new_doc_raw.strip()
            for q in ('"""', "'''"):
                if clean.startswith(q) and clean.endswith(q) and len(clean) > 6:
                    clean = clean[3:-3].strip(); break
            doc_lines = clean.splitlines()
            block = f'{indent}"""{doc_lines[0]}\n'
            for dl in doc_lines[1:]: block += f"{indent}{dl}\n"
            block += f'{indent}"""\n'
            first_stmt = node.body[0]
            if (isinstance(first_stmt, ast.Expr) and
                    isinstance(first_stmt.value, (ast.Constant, ast.Str))):
                lines[first_stmt.lineno - 1:first_stmt.end_lineno] = [block]
            else:
                lines.insert(node.lineno, block)
            return "".join(lines), None
    return source, f"Function '{func_name}' not found"

def write_file_to_disk(path_str, content):
    try:
        p = Path(path_str)
        p.write_text(content, encoding="utf-8")
        verify = p.read_text(encoding="utf-8")
        if verify == content: return True, str(p.resolve())
        return False, "Write verification failed"
    except PermissionError: return False, f"Permission denied: {path_str}"
    except FileNotFoundError: return False, f"Directory not found: {Path(path_str).parent}"
    except Exception as e: return False, str(e)

def load_path(path_str):
    p = Path(path_str.strip())
    if not p.exists(): return {}, {}, f"Path not found: {p}"
    if p.is_file():
        if p.suffix != ".py": return {}, {}, f"Not a .py file: {p.name}"
        content = p.read_text(encoding="utf-8", errors="ignore")
        return {p.name: content}, {p.name: str(p.resolve())}, None
    if p.is_dir():
        files, paths = {}, {}
        for py in sorted(p.rglob("*.py")):
            try:
                rel = str(py.relative_to(p))
                files[rel] = py.read_text(encoding="utf-8", errors="ignore")
                paths[rel] = str(py.resolve())
            except: pass
        if not files: return {}, {}, "No .py files found in that folder."
        return files, paths, None
    return {}, {}, f"Unknown path type: {p}"

# ═══════════════════════════════════════════════════════════════════════════════
# SHARED UTILITIES — App2 Scanner
# ═══════════════════════════════════════════════════════════════════════════════
def has_docstring_node(node) -> bool:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    if (node.body and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
        return True
    return False

def scan_file(filepath: str) -> List[Dict[str, Any]]:
    results = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                results.append({
                    "file":      os.path.basename(filepath),
                    "function":  node.name,
                    "line":      node.lineno,
                    "docstring": has_docstring_node(node),
                    "args":      len(node.args.args),
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

def run_tests(results: List[Dict]) -> Dict[str, Dict]:
    groups: Dict[str, list] = {}
    for r in results:
        fname = r["file"]
        key = fname.replace(".py", "").replace("_", " ").title() + " Tests"
        groups.setdefault(key, []).append(r)
    test_summary = {}
    for suite, items in groups.items():
        total = len(items)
        passed = sum(1 for i in items if i["docstring"])
        test_summary[suite] = {"total": total, "passed": passed, "items": items}
    return test_summary

def coverage_report_json_scanner():
    results        = st.session_state.scan_results
    total_fns      = len(results)
    total_with_doc = sum(1 for r in results if r["docstring"])
    total_missing  = total_fns - total_with_doc
    coverage_pct   = (total_with_doc / total_fns * 100) if total_fns > 0 else 0.0
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_functions": total_fns,
            "documented": total_with_doc,
            "missing": total_missing,
            "coverage_pct": round(coverage_pct, 1),
        },
        "functions": results,
    }
    return json.dumps(report, indent=2)

# ═══════════════════════════════════════════════════════════════════════════════
# App2: NAV CARDS (Dashboard inline expandable cards)
# ═══════════════════════════════════════════════════════════════════════════════
def nav_cards(caller="dashboard"):
    if "expanded_card" not in st.session_state:
        st.session_state.expanded_card = None

    card_defs = [
        ("Advanced Filters", "Filter by status",  "linear-gradient(135deg,#667eea,#764ba2)", "🔍"),
        ("Search",           "Find functions",    "linear-gradient(135deg,#f093fb,#f5576c)", "🔎"),
        ("Export",           "JSON & CSV",        "linear-gradient(135deg,#4facfe,#00f2fe)", "📤"),
        ("Help & Tips",      "Quick guide",       "linear-gradient(135deg,#43e97b,#38f9d7)", "ℹ️"),
    ]

    active_card = st.session_state.expanded_card

    # One-time CSS injection
    st.markdown("""<style>
    .nc-outer { position:relative; margin-bottom:0; }
    .nc-visual {
        border-radius:16px; padding:1.6rem 1rem 1.4rem;
        text-align:center; pointer-events:none;
        position:relative; z-index:1;
        transition:transform .2s, box-shadow .2s;
    }
    .nc-icon { font-size:2.8rem; line-height:1; margin-bottom:.5rem; }
    .nc-name { font-weight:800; font-size:.95rem; color:#fff; margin-bottom:.25rem; letter-spacing:-.01em; }
    .nc-sub  { font-size:.75rem; color:rgba(255,255,255,.82); }
    .nc-outer:hover .nc-visual { transform:translateY(-4px); box-shadow:0 12px 32px rgba(0,0,0,.35); }
    .nc-visual.nc-active { outline:3px solid rgba(255,255,255,.7); outline-offset:-3px; }
    .nc-btn-wrap > div > button {
        position:absolute !important; inset:0 !important; width:100% !important;
        height:100% !important; opacity:0 !important; cursor:pointer !important;
        z-index:2 !important; border:none !important; background:transparent !important;
        border-radius:16px !important;
    }
    </style>""", unsafe_allow_html=True)

    cols = st.columns(4)
    for col, (name, sub, grad, icon) in zip(cols, card_defs):
        with col:
            btn_key = f"{caller}_{name}_btn"
            active  = active_card == f"{caller}_{name}"
            act_cls = "nc-active" if active else ""

            st.markdown(
                "<div class='nc-outer'>"
                "<div class='nc-visual " + act_cls + "' style='background:" + grad + ";'>"
                "<div class='nc-tip-wrap'>"
                "<div class='nc-icon'>" + icon + "</div>"
                "<div class='nc-name'>" + name + "</div>"
                "<div class='nc-sub'>" + sub + "</div>"
                "</div></div>"
                "<div class='nc-btn-wrap' style='position:absolute;inset:0;z-index:2;'>",
                unsafe_allow_html=True,
            )
            if st.button(name, key=btn_key, use_container_width=True, help="Click on " + name):
                st.session_state.expanded_card = None if active else f"{caller}_{name}"
                st.rerun()
            st.markdown("</div></div>", unsafe_allow_html=True)

    expanded = st.session_state.expanded_card
    if expanded and expanded.startswith(caller + "_"):
        active_name = expanded[len(caller)+1:]
        st.markdown("<hr style='margin:1rem 0'>", unsafe_allow_html=True)
        _render_card_content(active_name)

def _render_card_content(name: str):
    results        = st.session_state.scan_results
    total_fns      = len(results)
    total_with_doc = sum(1 for r in results if r["docstring"])
    total_missing  = total_fns - total_with_doc

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
        if doc_filter == "OK":   filtered = [r for r in filtered if r["docstring"]]
        elif doc_filter == "Fix": filtered = [r for r in filtered if not r["docstring"]]
        if file_filter != "All files": filtered = [r for r in filtered if r["file"] == file_filter]
        st.markdown(f"""
        <div class='stat-cards-row-sm'>
            <div class='stat-card-sm stat-card-blue-sm'><div class='stat-number-sm'>{len(filtered)}</div><div class='stat-label-sm'>Showing</div></div>
            <div class='stat-card-sm stat-card-purple-sm'><div class='stat-number-sm'>{total_fns}</div><div class='stat-label-sm'>Total</div></div>
        </div>""", unsafe_allow_html=True)
        if filtered:
            rows_html = "".join(
                f"<tr><td>{r['file']}</td><td><code>{r['function']}</code></td>"
                f"<td><span class='{'badge-yes' if r['docstring'] else 'badge-no'}'>"
                f"{'✅ Yes' if r['docstring'] else '❌ No'}</span></td></tr>"
                for r in filtered
            )
            st.markdown(f"<table class='review-table'><thead><tr><th>📁 FILE</th><th>⚙️ FUNCTION</th><th>✅ DOCSTRING</th></tr></thead><tbody>{rows_html}</tbody></table>", unsafe_allow_html=True)
        else:
            st.warning("No functions match the selected filters.")

    elif name == "Search":
        st.markdown("<div style='background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);border-radius:14px;padding:1.3rem 1.8rem;margin-bottom:1rem'><h3 style='color:#fff;margin:0 0 0.2rem'>🔎 Search Functions</h3><p style='color:#ffe0e8;font-size:0.82rem;margin:0'>Instant search across all parsed functions</p></div>", unsafe_allow_html=True)
        if not st.session_state.scan_done:
            st.info("👈 Upload and analyse files first.")
            return
        query = st.text_input("🔍 Enter function name", placeholder="Type to search...", key="inline_search")
        if query:
            matches = [r for r in results if query.lower() in r["function"].lower() or query.lower() in r["file"].lower()]
            st.markdown(f"<div style='font-size:0.85rem;color:#6b7280;margin-bottom:0.8rem'>Found <strong>{len(matches)}</strong> result(s)</div>", unsafe_allow_html=True)
            for r in matches:
                doc_badge = "<span class='badge-yes'>✅ Documented</span>" if r["docstring"] else "<span class='badge-no'>❌ Missing doc</span>"
                st.markdown(f"<div class='search-result'><div><div class='search-result-fn'>{r['function']}</div><div class='search-result-file'>{r['file']} · line {r['line']} · {r['args']} arg(s)</div></div>{doc_badge}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#9ca3af;font-size:0.85rem'>Type a function or file name to search.</div>", unsafe_allow_html=True)

    elif name == "Export":
        st.markdown("<div style='background:linear-gradient(135deg,#4facfe,#00f2fe);border-radius:14px;padding:1.3rem 1.8rem;margin-bottom:1rem'><h3 style='color:#fff;margin:0 0 0.2rem'>📤 Export Results</h3><p style='color:#e0f8ff;font-size:0.82rem;margin:0'>Download your analysis as JSON or CSV</p></div>", unsafe_allow_html=True)
        if not st.session_state.scan_done:
            st.info("👈 Upload and analyse files first.")
            return
        st.markdown(f"<div style='background:rgba(102,126,234,.08);border:1px solid rgba(102,126,234,.2);border-radius:10px;padding:0.9rem 1.2rem;margin-bottom:1rem;font-size:0.85rem'><strong>{total_fns}</strong> functions &nbsp;·&nbsp; <strong>{total_with_doc}</strong> documented &nbsp;·&nbsp; <strong>{total_missing}</strong> missing</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇️ Download JSON", data=json.dumps(results, indent=2), file_name="review_results.json", mime="application/json", use_container_width=True, key="inline_dl_json")
        with col2:
            out = io.StringIO()
            w = csv.DictWriter(out, fieldnames=["file","function","line","docstring","args"])
            w.writeheader(); w.writerows(results)
            st.download_button("⬇️ Download CSV", data=out.getvalue(), file_name="review_results.csv", mime="text/csv", use_container_width=True, key="inline_dl_csv")

    elif name == "Help & Tips":
        st.markdown("<div style='background:linear-gradient(135deg,#43e97b,#38f9d7);border-radius:14px;padding:1.3rem 1.8rem;margin-bottom:1rem'><h3 style='color:#fff;margin:0 0 0.2rem'>❓ Help & Tips</h3><p style='color:#e0fff8;font-size:0.82rem;margin:0'>Quick guide to using the AI Code Reviewer</p></div>", unsafe_allow_html=True)
        tips = [
            ("📂 How to upload", "Click **Upload Python file(s)** in the sidebar, select one or more `.py` files, then click **Analyse**."),
            ("📊 Dashboard", "Shows a bar chart of functions per file and pass/fail rows based on docstring coverage."),
            ("🔍 Advanced Filters", "Filter by documentation status: **OK** (has docstring) or **Fix** (missing docstring)."),
            ("🔎 Search", "Type any function or file name to instantly find matching results."),
            ("📤 Export", "Download your results as **JSON** or **CSV** for CI/CD pipelines or reports."),
            ("✅ Docstring status", "`OK` = function has a docstring. `Fix` = docstring is missing."),
            ("💡 Pro tip", "Export CSV and import into your issue tracker to track documentation debt over time."),
        ]
        for title, body in tips:
            with st.expander(title):
                st.markdown(body)


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Title badge
    st.markdown("""
    <div class='app-title'>
        <div class='app-title-dot'>🔮</div>
        <div>
            <div class='app-title-text'>Code Reviewer Pro</div>
            <div class='app-title-sub'>AI · Python · Unified</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Dark / Light toggle
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        theme_label = "🌙 Dark" if not st.session_state.dark_mode else "☀️ Light"
        st.markdown(f"<div style='font-size:.75rem;font-weight:600;padding-top:.45rem;color:{'#7a8db0' if st.session_state.dark_mode else '#4c4f8a'}'>{theme_label} mode</div>", unsafe_allow_html=True)
    with col_t2:
        if st.button("🔆" if st.session_state.dark_mode else "🌙", help="Toggle theme", key="theme_btn"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin:.6rem 0'></div>", unsafe_allow_html=True)

    # ── TOP-LEVEL NAV: Validation now above Docstring Reviewer ────────────────
    app_mode = st.selectbox("View", [
        "🏠 Home",
        "✅ Validation",
        "🔮 Docstring Reviewer",
        "📊 Dashboard",
    ], label_visibility="collapsed", key="top_mode_radio")
    st.session_state.top_mode = app_mode

    st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin:.7rem 0'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # UNIFIED FILE INPUT — shared across all pages
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("<div class='section-label'>📂 File Input</div>", unsafe_allow_html=True)

    unified_input_mode = st.radio(
        "Input mode", ["📄 Upload file(s)", "🗂️ Folder path"],
        label_visibility="collapsed", key="unified_input_mode"
    )

    unified_uploaded_files = None
    unified_folder_path    = ""

    if unified_input_mode == "📄 Upload file(s)":
        st.markdown("<div style='font-size:.73rem;color:#2a3a60;margin-bottom:.4rem;"
                    "font-family:\"DM Mono\",monospace'>Upload one or more .py files</div>",
                    unsafe_allow_html=True)
        unified_uploaded_files = st.file_uploader(
            "Upload .py files", type=["py"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="unified_py_upload"
        )
        if unified_uploaded_files:
            st.markdown(f"<div class='info-banner info-live'>✅ {len(unified_uploaded_files)} file(s) ready</div>",
                        unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:.73rem;color:#2a3a60;margin-bottom:.4rem;"
                    "font-family:\"DM Mono\",monospace'>Paste a .py file or folder path</div>",
                    unsafe_allow_html=True)
        unified_folder_path = st.text_input(
            "Folder or file path",
            value=st.session_state.loaded_path,
            placeholder="e.g. C:/myproject/src  or  C:/myproject/sample.py",
            label_visibility="collapsed",
            key="unified_folder_input"
        )
        if unified_folder_path.strip():
            _up = Path(unified_folder_path.strip())
            if _up.exists():
                _kind = "📄 File" if _up.is_file() else "📁 Folder"
                st.markdown(f"<div class='info-banner info-live'>✅ {_kind}: <code>{_up.name}</code></div>",
                            unsafe_allow_html=True)
            else:
                st.markdown("<div class='info-banner info-demo'>❌ Path not found</div>",
                            unsafe_allow_html=True)

    # ── Load / Analyse button ─────────────────────────────────────────────────
    _col_load, _col_reload = st.columns(2)
    with _col_load:
        unified_load = st.button("▶ Load & Analyse", use_container_width=True, key="unified_load")
    with _col_reload:
        unified_reload = st.button("🔄 Reload", use_container_width=True,
                                   key="unified_reload",
                                   disabled=not st.session_state.loaded_path and not unified_uploaded_files)

    if unified_load:
        # ── branch A: uploaded files ─────────────────────────────────────────
        if unified_input_mode == "📄 Upload file(s)" and unified_uploaded_files:
            with st.spinner("Loading..."):
                # Populate scan_results (Dashboard / Home)
                all_results = []
                _files_dict = {}
                for uf in unified_uploaded_files:
                    raw = uf.read()
                    source = raw.decode("utf-8", errors="ignore")
                    _files_dict[uf.name] = source
                    try:
                        tree = ast.parse(source, filename=uf.name)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                all_results.append({
                                    "file":      uf.name,
                                    "function":  node.name,
                                    "line":      node.lineno,
                                    "docstring": has_docstring_node(node),
                                    "args":      len(node.args.args),
                                })
                    except SyntaxError as e:
                        all_results.append({
                            "file": uf.name,
                            "function": f"[SyntaxError line {e.lineno}]",
                            "line": e.lineno or 0,
                            "docstring": False,
                            "args": 0,
                        })
                st.session_state.scan_results = all_results
                st.session_state.test_summary = run_tests(all_results)
                st.session_state.scan_done    = True

                # Populate code_content (Validation) — use first file
                first_name = list(_files_dict.keys())[0]
                st.session_state.code_content = _files_dict[first_name]
                st.session_state.current_file = first_name
                st.session_state.pep_mode     = False
                st.session_state.dashboard_mode = False

                # Populate reviewer files (Docstring Reviewer)
                st.session_state.files        = _files_dict
                st.session_state.file_paths   = {}
                st.session_state.loaded_path  = ""
                st.session_state.reviewer_scanned = True
                st.session_state.is_demo      = False
                st.session_state.selected_file = first_name
                st.session_state.generated_docs = {}
                st.session_state.last_save    = {}

            st.success(f"✅ Loaded {len(unified_uploaded_files)} file(s) — {len(all_results)} functions found")
            st.rerun()

        # ── branch B: folder / file path ─────────────────────────────────────
        elif unified_input_mode == "🗂️ Folder path" and unified_folder_path.strip():
            with st.spinner("Loading..."):
                _p = Path(unified_folder_path.strip())

                # Populate reviewer files (Docstring Reviewer)
                files, paths, err = load_path(unified_folder_path)
                if err:
                    st.error(err)
                else:
                    st.session_state.files        = files
                    st.session_state.file_paths   = paths
                    st.session_state.loaded_path  = unified_folder_path.strip()
                    st.session_state.reviewer_scanned = True
                    st.session_state.is_demo      = False
                    st.session_state.selected_file = list(files.keys())[0]
                    st.session_state.generated_docs = {}
                    st.session_state.last_save    = {}

                    # Populate scan_results (Dashboard / Home)
                    all_results = []
                    py_names    = []
                    if _p.is_dir():
                        py_files_list = sorted(_p.rglob("*.py"))
                        py_names = [str(f) for f in py_files_list]
                        for py_file in py_files_list:
                            all_results.extend(scan_file(str(py_file)))
                    elif _p.is_file():
                        all_results.extend(scan_file(str(_p)))
                    st.session_state.scan_results = all_results
                    st.session_state.test_summary = run_tests(all_results)
                    st.session_state.scan_done    = True

                    # Populate code_content (Validation) — use first file
                    first_name = list(files.keys())[0]
                    first_src  = files[first_name]
                    st.session_state.code_content   = first_src
                    st.session_state.current_file   = first_name
                    st.session_state.pep_mode       = False
                    st.session_state.dashboard_mode = False

                    total_found = len(all_results)
                    st.success(f"✅ Loaded {len(files)} file(s) — {total_found} functions found")
                    st.rerun()
        else:
            st.warning("Please provide file(s) or a path before loading.")

    if unified_reload and (st.session_state.loaded_path or unified_uploaded_files):
        if st.session_state.loaded_path:
            files, paths, err = load_path(st.session_state.loaded_path)
            if err:
                st.error(err)
            else:
                st.session_state.files      = files
                st.session_state.file_paths = paths
                st.session_state.generated_docs = {}
                st.session_state.last_save  = {}
                # re-scan
                all_results = []
                _p2 = Path(st.session_state.loaded_path)
                if _p2.is_dir():
                    for py_file in sorted(_p2.rglob("*.py")):
                        all_results.extend(scan_file(str(py_file)))
                elif _p2.is_file():
                    all_results.extend(scan_file(str(_p2)))
                st.session_state.scan_results = all_results
                st.session_state.test_summary = run_tests(all_results)
                st.session_state.scan_done    = True
                st.success("Reloaded ✓")
                st.rerun()

    if st.session_state.reviewer_scanned and not st.session_state.is_demo and st.session_state.loaded_path:
        lp = st.session_state.loaded_path
        st.markdown(f"<div class='info-banner info-live' style='margin-top:.5rem;word-break:break-all'>"
                    f"💾 <b>Live</b> · <code style='font-size:.7rem'>{lp}</code></div>",
                    unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin:1rem 0'></div>",
                unsafe_allow_html=True)

    # ── Page-specific controls ────────────────────────────────────────────────
    if app_mode == "🔮 Docstring Reviewer":
        st.markdown("<div class='section-label'>⚙ Reviewer Settings</div>", unsafe_allow_html=True)
        doc_style = st.selectbox("Docstring style", ["GOOGLE","NUMPY","reST"], label_visibility="collapsed")

        st.markdown("""
        <div class='demo-card'>
            <div style='font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;
                 color:#2a3a60;margin-bottom:.5rem;font-family:"DM Mono",monospace'>⚠ Demo — no disk write-back</div>
        </div>""", unsafe_allow_html=True)

        if st.button("🧪 Load Demo Files", use_container_width=True):
            st.session_state.files = {
                "sample_a.py": textwrap.dedent("""\
                    def calculate_average(numbers):
                        total = sum(numbers)
                        return total / len(numbers)

                    def find_max(items):
                        return max(items)

                    def format_string(text, width=80):
                        return text.center(width)
                """),
                "sample_b.py": textwrap.dedent("""\
                    def read_file(path):
                        with open(path) as f:
                            return f.read()

                    def write_json(data, path):
                        \"\"\"Write data to a JSON file.\"\"\"
                        import json
                        with open(path, "w") as f:
                            json.dump(data, f)

                    def validate_email(email):
                        import re
                        return bool(re.match(r"[^@]+@[^@]+\\.[^@]+", email))
                """),
            }
            st.session_state.file_paths   = {}
            st.session_state.loaded_path  = ""
            st.session_state.reviewer_scanned = True
            st.session_state.is_demo      = True
            st.session_state.selected_file = "sample_a.py"
            st.session_state.generated_docs = {}
            st.session_state.last_save    = {}
            st.rerun()

        if st.session_state.reviewer_scanned and st.session_state.is_demo:
            st.markdown("<div class='info-banner info-demo' style='margin-top:.5rem'>"
                        "🧪 Demo — paste a real path above to enable write-back.</div>",
                        unsafe_allow_html=True)

    elif app_mode == "✅ Validation":
        st.markdown("<div class='section-label'>⚙ Validation Controls</div>", unsafe_allow_html=True)
        if st.button("🧪 PEP Validation", use_container_width=True, key="toggle_pep"):
            st.session_state.pep_mode = not st.session_state.pep_mode
            st.rerun()

    st.markdown(f"<div style='font-size:.66rem;color:#2a3a60;margin-top:.8rem;"
                f"font-family:\"DM Mono\",monospace'>Last scan: {datetime.now().strftime('%d %b %Y, %H:%M')}</div>",
                unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DOCSTRING REVIEWER
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.top_mode == "🔮 Docstring Reviewer":

    if not st.session_state.reviewer_scanned:
        st.markdown("""
        <div style='text-align:center;padding:5rem 2rem 3rem;animation:fadeUp .6s ease'>
            <div class='hero-glyph'>🔮</div>
            <h1 style='font-family:"Syne",sans-serif;font-size:2.8rem;font-weight:800;
                background:linear-gradient(135deg,#e8eeff,#00d4ff,#b060ff,#00ffaa);
                background-size:300%;animation:aurora 6s ease infinite;
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                margin-bottom:.8rem;letter-spacing:-.05em;line-height:1.05'>
                AI Docstring Reviewer
            </h1>
            <p style='color:#2a3a60;max-width:500px;margin:.8rem auto 0;
                 font-size:.9rem;line-height:1.75;font-family:"DM Mono",monospace'>
                Paste a <span style='color:#00d4ff'>.py file path</span> or
                <span style='color:#b060ff'>folder path</span> in the sidebar and click
                <span style='color:#00ffaa'>Load</span> to begin analysis.
            </p>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div class='info-banner info-tip' style='max-width:640px;margin:0 auto'>"
                    "👈 Use the <b>📂 File Input</b> panel in the sidebar to upload files or paste a folder path, "
                    "then click <b>▶ Load &amp; Analyse</b> — or use <b>🧪 Load Demo Files</b> below."
                    "</div>", unsafe_allow_html=True)
        st.stop()

    # metadata
    all_funcs = {f: extract_functions(s) for f, s in st.session_state.files.items()}
    total   = sum(len(v) for v in all_funcs.values())
    missing = sum(1 for v in all_funcs.values() for f in v if not f["has_doc"])

    if st.session_state.is_demo:
        st.markdown("<div class='info-banner info-demo'>"
                    "⚠️ <b>Demo mode</b> — Saving won't update disk. "
                    "Paste your real file path in the sidebar.</div>", unsafe_allow_html=True)
    else:
        lp = st.session_state.loaded_path
        st.markdown(f"<div class='info-banner info-live'>"
                    f"💾 <b>Live mode</b> — Saving writes directly to "
                    f"<code>{lp}</code> — VS Code updates instantly.</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin:.7rem 0'></div>", unsafe_allow_html=True)

    # stats
    c1, c2, c3, c4 = st.columns(4)
    coverage_pct = int((total - missing) / total * 100) if total else 0

    stat_configs = [
        (c1, len(st.session_state.files), "Files Loaded",  "#00d4ff", "linear-gradient(135deg,#00d4ff,#b060ff)", "rgba(0,212,255,.06)", "rgba(0,212,255,.2)", "in scope",      "📁"),
        (c2, total,                        "Functions",     "#00ffaa", "linear-gradient(135deg,#00ffaa,#00d4ff)", "rgba(0,255,170,.06)", "rgba(0,255,170,.2)", "detected",       "⚙️"),
        (c3, missing,                      "Missing Docs",  "#ff4d6d", "linear-gradient(135deg,#ff4d6d,#ffb830)", "rgba(255,77,109,.06)", "rgba(255,77,109,.2)", "need attention", "⚠️"),
        (c4, f"{coverage_pct}%",           "Coverage",      "#00ffaa", "linear-gradient(135deg,#00ffaa,#b060ff)", "rgba(0,255,170,.06)", "rgba(0,255,170,.2)", "documented",     "✅"),
    ]
    for col, num, label, color, grad, glow_dim, glow_bright, sub, icon in stat_configs:
        col.markdown(f"""
        <div class='stat-card' style='--accent-color:{color};--accent-grad:{grad};--accent-glow:{glow_dim}'>
            <div class='stat-icon'>{icon}</div>
            <div class='stat-num'>{num}</div>
            <div class='stat-label'>{label}</div>
            <div class='stat-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:.9rem 0'></div>", unsafe_allow_html=True)

    left, right = st.columns([5, 7], gap="large")

    with left:
        st.markdown(f"""
        <div class='banner banner-violet'>
            <span style='font-size:1.1rem'>📁</span> Project Files
            <span style='margin-left:auto;font-size:.7rem;font-weight:500;opacity:.75;font-family:"DM Mono",monospace'>
                style: {doc_style}
            </span>
        </div>""", unsafe_allow_html=True)

        for fname in st.session_state.files:
            funcs  = all_funcs.get(fname, [])
            n_miss = sum(1 for f in funcs if not f["has_doc"])
            active = st.session_state.selected_file == fname
            ca, cb = st.columns([3, 1])
            with ca:
                if st.button(f"{'▶' if active else '📄'}  {fname}",
                             key=f"f_{fname}", use_container_width=True):
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
                        icon   = "🟢" if fn["has_doc"] else "🔴"
                        is_sel = st.session_state.selected_func == fn["name"]
                        if st.button(
                            f"{'▶ ' if is_sel else '  '}{icon}  {fn['name']}()",
                            key=f"fn_{fname}_{fn['name']}"):
                            st.session_state.selected_func = fn["name"]
                            st.rerun()

    with right:
        st.markdown("""
        <div class='banner banner-blue'>
            <span style='font-size:1.1rem'>⚙️</span> Function Review
        </div>""", unsafe_allow_html=True)

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
                    st.markdown("<div class='code-box-header'>"
                                "<span class='dot' style='background:#ff4d6d'></span>"
                                "<span class='dot' style='background:#ffb830'></span>"
                                "<span class='dot' style='background:#00ffaa'></span>"
                                "&nbsp;&nbsp;📝 Current Docstring</div>", unsafe_allow_html=True)
                    st.markdown(f'<div class="code-box attached">"""\n{func_data["docstring"]}\n"""</div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown("<div class='code-box-header'>"
                                "<span class='dot' style='background:#ff4d6d'></span>"
                                "<span class='dot' style='background:#ffb830'></span>"
                                "<span class='dot' style='background:#00ffaa'></span>"
                                "&nbsp;&nbsp;⚡ Inferred Description</div>", unsafe_allow_html=True)
                    auto = build_description(func_data)
                    st.markdown(
                        f'<div class="code-box inferred attached">'
                        f'<span style="color:#1a2a45;font-size:.67rem;font-style:italic">no docstring yet — inferred from signature</span>\n\n'
                        f'"""\n{auto}\n"""</div>', unsafe_allow_html=True)

            with gc:
                st.markdown(f"<div class='code-box-header'>"
                            "<span class='dot' style='background:#ff4d6d'></span>"
                            "<span class='dot' style='background:#ffb830'></span>"
                            "<span class='dot' style='background:#00ffaa'></span>"
                            f"&nbsp;&nbsp;✨ Generated ({doc_style}) — edit then save</div>",
                            unsafe_allow_html=True)
                edited = st.text_area("gen_edit",
                                      value=st.session_state.generated_docs[cache_key],
                                      height=215, key=f"edit_{cache_key}",
                                      label_visibility="collapsed")
                if edited != st.session_state.generated_docs[cache_key]:
                    st.session_state.generated_docs[cache_key] = edited

            st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin:.7rem 0'></div>",
                        unsafe_allow_html=True)

            disk_path = st.session_state.file_paths.get(sel_file, "").strip()
            b1, b2, b3 = st.columns(3)

            with b1:
                if st.button("🔄 Regenerate", key="regen", use_container_width=True):
                    st.session_state.generated_docs.pop(cache_key, None)
                    st.rerun()
            with b2:
                if st.button("✅ Apply in Memory", key="apply", use_container_width=True):
                    new_src, err = inject_docstring(st.session_state.files[sel_file],
                                                    chosen, st.session_state.generated_docs[cache_key])
                    if err:
                        st.error(err)
                    else:
                        st.session_state.files[sel_file] = new_src
                        st.toast("Applied in memory ✓", icon="✅")
                        st.rerun()
            with b3:
                if st.button("💾 Save to File", key="save_disk",
                             use_container_width=True, disabled=not disk_path):
                    new_src, err = inject_docstring(st.session_state.files[sel_file],
                                                    chosen, st.session_state.generated_docs[cache_key])
                    if err:
                        st.session_state.last_save[cache_key] = (False, err)
                    else:
                        ok, msg = write_file_to_disk(disk_path, new_src)
                        st.session_state.last_save[cache_key] = (ok, msg)
                        if ok:
                            st.session_state.files[sel_file] = new_src
                    st.rerun()

            save_res = st.session_state.last_save.get(cache_key)
            if save_res:
                ok, msg = save_res
                if ok:
                    st.markdown(f"<div class='save-ok'>💾 Saved → <code>{msg}</code><br>"
                                f"<span style='color:#00ffaa;font-size:.7rem'>✓ VS Code will auto-reload</span>"
                                f"</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='save-err'>❌ {msg}</div>", unsafe_allow_html=True)
            elif not disk_path:
                st.markdown("<div class='info-banner info-demo'>"
                            "⚠️ Demo mode — paste your real file path to enable saving."
                            "</div>", unsafe_allow_html=True)

    # bottom bar
    st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin:2rem 0'></div>",
                unsafe_allow_html=True)
    ba1, ba2 = st.columns([3, 2])
    with ba1:
        saveable = {k: v for k, v in st.session_state.file_paths.items() if v.strip()}
        if st.button(f"💾 Save ALL {len(saveable)} file(s) to disk",
                     use_container_width=True, disabled=not saveable):
            ok_n, errs = 0, []
            for fname, fpath in saveable.items():
                ok, msg = write_file_to_disk(fpath, st.session_state.files[fname])
                if ok: ok_n += 1
                else:  errs.append(f"{fname}: {msg}")
            if ok_n:
                st.success(f"✅ Saved {ok_n} file(s) — switch to VS Code to see updates.")
            for m in errs:
                st.error(f"❌ {m}")
    with ba2:
        st.download_button("⬇ Export Docstrings JSON",
            data=json.dumps({"generated_at": datetime.now().isoformat(),
                             "style": doc_style,
                             "docstrings": st.session_state.generated_docs}, indent=2),
            file_name="review_logs.json", mime="application/json", use_container_width=True)

    st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin:1.5rem 0'></div>",
                unsafe_allow_html=True)
    st.markdown("<div style='font-family:\"Syne\",sans-serif;font-weight:700;font-size:.95rem;"
                "color:#2a3a60;margin-bottom:.7rem;display:flex;align-items:center;gap:.5rem'>"
                "📂 Source Viewer "
                "<span style='font-weight:400;color:#1a2540;font-size:.73rem;font-family:\"DM Mono\",monospace'>"
                "— reflects saved changes</span></div>", unsafe_allow_html=True)
    src_tabs = st.tabs(list(st.session_state.files.keys()))
    for i, (fname, src) in enumerate(st.session_state.files.items()):
        with src_tabs[i]:
            p = st.session_state.file_paths.get(fname, "")
            if p:
                st.markdown(f"<div class='info-banner info-tip' style='margin-bottom:.6rem'>"
                            f"📁 <code>{p}</code></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='info-banner info-demo' style='margin-bottom:.6rem'>"
                            "🧪 Demo file — no disk path</div>", unsafe_allow_html=True)
            st.code(src, language="python", line_numbers=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: VALIDATION (formerly Code Analyzer)
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.top_mode == "✅ Validation":
    st.markdown("""
    <div style='display:flex;align-items:center;gap:1.2rem;margin-bottom:1.5rem;animation:fadeUp .4s ease'>
        <div style='width:52px;height:52px;border-radius:16px;flex-shrink:0;
             background:linear-gradient(135deg,#011a18,#053a36,#0a6060);
             display:flex;align-items:center;justify-content:center;
             font-size:1.6rem;
             box-shadow:0 0 30px rgba(0,255,170,.15),inset 0 1px 0 rgba(255,255,255,.06);
             border:1px solid rgba(0,255,170,.2)'>✅</div>
        <div>
            <div style='font-family:"Syne",sans-serif;font-size:1.55rem;
                 font-weight:800;letter-spacing:-.04em;
                 background:linear-gradient(135deg,#e8eeff,#00ffaa);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
                Validation
            </div>
            <div style='font-size:.75rem;color:#2a3a60;margin-top:.2rem;
                 font-family:"DM Mono",monospace;letter-spacing:.02em'>
                Analyze documentation coverage, complexity &amp; structure
            </div>
        </div>
    </div>
    <div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin-bottom:1.5rem'></div>
    """, unsafe_allow_html=True)

    analyzer_code    = st.session_state.code_content or None
    active_file_name = st.session_state.current_file

    if analyzer_code:
        st.markdown(f"<div class='info-banner info-live'>📄 <b>Active File:</b> {active_file_name}</div>",
                    unsafe_allow_html=True)
        st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)

        functions, classes, module_doc, error = analyze_code(analyzer_code)

        total_functions      = len(functions) if functions else 0
        total_classes        = len(classes)   if classes   else 0
        documented_functions = sum(f["Has Docstring"] for f in (functions or []))
        documented_classes   = sum(c["Has Docstring"] for c in (classes   or []))
        undoc_f   = total_functions - documented_functions
        func_pct  = calc_pct(total_functions, documented_functions)
        class_pct = calc_pct(total_classes,   documented_classes)
        overall_total = total_functions + total_classes
        overall_doc   = documented_functions + documented_classes
        overall_pct   = calc_pct(overall_total, overall_doc)
        current_filename = active_file_name or "uploaded_module.py"

        if st.session_state.pep_mode:
            st.markdown("<div class='banner banner-rose'>🧪 PEP Validation</div>",
                        unsafe_allow_html=True)
            if error:
                st.error(f"Syntax Error: {error}")
                st.session_state.code_content = st.text_area("Fix syntax here:", value=analyzer_code, height=300)
            else:
                col_left, col_right = st.columns([1, 1])
                with col_left:
                    st.markdown("<div style='font-weight:700;color:#7a8db0;margin-bottom:.5rem;font-family:\"Syne\",sans-serif'>Source Code</div>",
                                unsafe_allow_html=True)
                    st.session_state.code_content = st.text_area(
                        "Editor", value=st.session_state.code_content,
                        height=600, label_visibility="collapsed")
                with col_right:
                    st.markdown("<div style='font-weight:700;color:#7a8db0;margin-bottom:.5rem;font-family:\"Syne\",sans-serif'>🚦 Live Fix Status</div>",
                                unsafe_allow_html=True)
                    for fn in (functions or []):
                        if not fn["Has Docstring"]:
                            st.error(f"❌ {fn['Name']} (Missing Docstring)")
                            if st.button(f"Fix {fn['Name']}", key=f"fix_{fn['Name']}"):
                                st.session_state.code_content = fix_with_regex(fn['Name'], st.session_state.code_content)
                                st.rerun()
                        else:
                            st.success(f"✅ {fn['Name']} (Documented)")

                pep_cols = st.columns(3)
                pep_cols[0].metric("Documented Functions", documented_functions)
                pep_cols[1].metric("Missing Docstrings", max(undoc_f, 0))
                pep_cols[2].metric("Coverage", f"{func_pct:.1f}%" if total_functions else "N/A")

                if total_functions == 0:
                    st.info("No functions available for validation.")

                violations = []
                if not module_doc:
                    violations.append({"rule": "MISSING_MODULE_DOCSTRING", "file": current_filename})
                for fn in (functions or []):
                    if not fn["Has Docstring"]:
                        violations.append({"rule": "MISSING_FUNCTION_DOCSTRING", "file": current_filename})

                missing_names = [fn["Name"] for fn in (functions or []) if not fn["Has Docstring"]]
                if missing_names:
                    st.warning("Functions without docstrings: " + ", ".join(missing_names))
                if not module_doc:
                    st.warning("Module docstring missing.")
                if not missing_names and module_doc:
                    st.success("All documented elements comply with docstring expectations.")

                if violations:
                    rule_counts = {}
                    file_counts = {}
                    for v in violations:
                        rule_counts[v["rule"]] = rule_counts.get(v["rule"], 0) + 1
                        file_counts[v["file"]] = file_counts.get(v["file"], 0) + 1
                    chart_cols = st.columns(2)
                    with chart_cols[0]:
                        st.caption("Error Distribution by Rule Type")
                        fig_rule, ax_rule = plt.subplots(figsize=(5, 4))
                        ax_rule.pie(list(rule_counts.values()), labels=list(rule_counts.keys()),
                                    autopct="%1.1f%%", startangle=140,
                                    colors=["#00d4ff","#b060ff","#00ffaa"])
                        ax_rule.axis("equal")
                        st.pyplot(fig_rule)
                        plt.close(fig_rule)
                    with chart_cols[1]:
                        st.caption("Error Distribution by File")
                        fig_file, ax_file = plt.subplots(figsize=(5, 4))
                        ax_file.pie(list(file_counts.values()), labels=list(file_counts.keys()),
                                    autopct="%1.1f%%", startangle=140,
                                    colors=["#ffb830","#ff4d6d","#b060ff"])
                        ax_file.axis("equal")
                        st.pyplot(fig_file)
                        plt.close(fig_file)
                else:
                    st.info("No PEP-style violations detected.")

        else:
            st.markdown("<div class='info-banner info-tip'>"
                        "👆 Click <b>🧪 PEP Validation</b> in the sidebar to get started."
                        "</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin:1.2rem 0'></div>", unsafe_allow_html=True)
        download_name = active_file_name or "code.py"
        st.download_button("💾 Download Fixed File",
            st.session_state.code_content,
            file_name=f"fixed_{download_name}")

    else:
        st.markdown("<div class='info-banner info-tip'>"
                    "📂 Upload a Python file or enter a folder path in the sidebar to start the analysis."
                    "</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME / DASHBOARD / FILTERS / SEARCH / EXPORT / HELP
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.top_mode in (
    "🏠 Home", "📊 Dashboard",
    "🔍 Advanced Filters", "🔎 Search", "📤 Export", "❓ Help & Tips"
):
    results        = st.session_state.scan_results
    test_summary   = st.session_state.test_summary
    total_fns      = len(results)
    total_with_doc = sum(1 for r in results if r["docstring"])
    total_missing  = total_fns - total_with_doc
    coverage_pct_s = (total_with_doc / total_fns * 100) if total_fns > 0 else 0.0

    view = st.session_state.top_mode

    # ── Home ──────────────────────────────────────────────────────────────────
    if view == "🏠 Home":
        st.markdown("<div class='banner banner-blue'><span style='font-size:1.1rem'>🏠</span> Scanner Home</div>",
                    unsafe_allow_html=True)

        if not st.session_state.scan_done:
            st.markdown("<div class='info-banner info-tip'>"
                        "👈 Choose an input mode in the sidebar and click <b>🔍 Analyse</b> to get started.</div>",
                        unsafe_allow_html=True)
        else:
            # ── Validation Dashboard (moved from Validation page) ──────────────
            _val_code = st.session_state.code_content or None
            _val_file = st.session_state.current_file

            if not _val_code:
                st.markdown("<div class='info-banner info-tip'>"
                            "📂 Upload a Python file in the ✅ Validation sidebar to see the full dashboard here."
                            "</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='info-banner info-live'>📄 <b>Active File:</b> {_val_file}</div>",
                            unsafe_allow_html=True)
                st.markdown("<div style='margin:.6rem 0'></div>", unsafe_allow_html=True)

                _functions, _classes, _module_doc, _error = analyze_code(_val_code)

                _total_functions      = len(_functions) if _functions else 0
                _total_classes        = len(_classes)   if _classes   else 0
                _documented_functions = sum(f["Has Docstring"] for f in (_functions or []))
                _documented_classes   = sum(c["Has Docstring"] for c in (_classes   or []))
                _undoc_f   = _total_functions - _documented_functions
                _func_pct  = calc_pct(_total_functions, _documented_functions)
                _class_pct = calc_pct(_total_classes,   _documented_classes)
                _overall_total = _total_functions + _total_classes
                _overall_doc   = _documented_functions + _documented_classes
                _overall_pct   = calc_pct(_overall_total, _overall_doc)

                st.markdown("<div class='banner banner-blue' style='margin-top:1.1rem'>📊 Quick Dashboard</div>",
                            unsafe_allow_html=True)
                if _error:
                    st.info("Resolve syntax issues to view metrics.")
                else:
                    _dash_cols = st.columns(5)
                    _dash_cols[0].metric("Total Functions", _total_functions)
                    _dash_cols[1].metric("Files w/ Docstring", 1 if _module_doc else 0)
                    _dash_cols[2].metric("Functions Documented", _documented_functions)
                    _dash_cols[3].metric("Functions Missing Docs", _undoc_f)
                    _dash_cols[4].metric("Coverage %", f"{_func_pct:.0f}%")

                if _error:
                    st.error(f"Syntax Error: {_error}")
                else:
                    _tab1, _tab2, _tab3, _tab4 = st.tabs([
                        "📊 Chart", "📋 Table", "📦 JSON", "📊 Analysis Dashboard"])

                    with _tab1:
                        st.markdown("<div style='font-weight:700;color:#7a8db0;margin-bottom:.9rem;font-family:\"Syne\",sans-serif'>📊 Coverage Visualization</div>",
                                    unsafe_allow_html=True)
                        _fig, _ax = plt.subplots(figsize=(7, 4))
                        _bars = _ax.bar(["Functions","Classes","Overall"],
                                        [_func_pct, _class_pct, _overall_pct],
                                        color=["#00d4ff","#b060ff","#00ffaa"],
                                        width=.5, zorder=3)
                        _ax.set_ylim(0, 110)
                        _ax.set_ylabel("Coverage %")
                        _ax.yaxis.grid(True, zorder=0)
                        _ax.set_axisbelow(True)
                        for _bar, _val in zip(_bars, [_func_pct, _class_pct, _overall_pct]):
                            _ax.text(_bar.get_x() + _bar.get_width()/2, _bar.get_height() + 2,
                                     f"{_val:.1f}%", ha="center", va="bottom", fontsize=10,
                                     color="#e8eeff", fontweight="bold")
                        _fig.tight_layout()
                        st.pyplot(_fig)
                        plt.close(_fig)

                    with _tab2:
                        st.markdown("<div style='font-weight:700;color:#7a8db0;margin-bottom:.6rem;font-family:\"Syne\",sans-serif'>📋 Detailed Analysis Table</div>",
                                    unsafe_allow_html=True)
                        _df = pd.DataFrame((_functions or []) + (_classes or []))
                        if not _df.empty:
                            _df["Has Docstring"] = _df["Has Docstring"].map(lambda v: "✔ Yes" if v else "✖ No")
                            st.dataframe(_df, use_container_width=True, height=500)
                        else:
                            st.info("No functions or classes found.")

                    with _tab3:
                        _result_data = {
                            "file": _val_file,
                            "timestamp": datetime.now().isoformat(),
                            "module_docstring": _module_doc,
                            "function_coverage": _func_pct,
                            "class_coverage": _class_pct,
                            "overall_coverage": _overall_pct,
                            "functions": _functions or [],
                            "classes": _classes or [],
                        }
                        st.json(_result_data)
                        st.download_button("⬇ Download Coverage Report JSON",
                            json.dumps(_result_data, indent=4).encode("utf-8"),
                            file_name=f"{_val_file}_coverage_report.json",
                            mime="application/json",
                            key="home_dl_json")

                    with _tab4:
                        st.markdown("<div style='font-weight:700;color:#7a8db0;margin-bottom:.6rem;font-family:\"Syne\",sans-serif'>📊 Coverage Snapshot</div>",
                                    unsafe_allow_html=True)
                        _snap_cols = st.columns(3)
                        _snap_cols[0].metric("Module Docstring", "Present" if _module_doc else "Missing")
                        _snap_cols[1].metric("Function Coverage", f"{_documented_functions}/{_total_functions}",
                                             delta=f"{_func_pct:.0f}%" if _total_functions else None)
                        _snap_cols[2].metric("Class Coverage", f"{_documented_classes}/{_total_classes}",
                                             delta=f"{_class_pct:.0f}%" if _total_classes else None)
                        if _module_doc:
                            st.success("Module-level documentation detected.")
                        else:
                            st.warning("No module docstring found.")
                        st.progress(_func_pct / 100 if _total_functions else 0)
                        st.caption("Function documentation completeness")

                        st.markdown("<div style='font-weight:700;color:#7a8db0;margin:.9rem 0 .5rem;font-family:\"Syne\",sans-serif'>🔎 Function Drill-down</div>",
                                    unsafe_allow_html=True)
                        if _functions:
                            _func_filter = st.radio("Function filter", ["All","Documented","Missing Docstrings"],
                                                    horizontal=True, key="home_func_filter")
                            _df_funcs = pd.DataFrame(_functions).sort_values(by="Complexity", ascending=False)
                            if _func_filter == "Documented":
                                _df_view = _df_funcs[_df_funcs["Has Docstring"]]
                            elif _func_filter == "Missing Docstrings":
                                _df_view = _df_funcs[~_df_funcs["Has Docstring"]]
                            else:
                                _df_view = _df_funcs
                            if _df_view.empty:
                                st.info("No functions match the selected filter.")
                            else:
                                st.dataframe(_df_view[["Name","Kind","Start Line","End Line","Complexity","Has Docstring"]],
                                             use_container_width=True)
                            _most_complex = _df_funcs.iloc[0]
                            st.info(f"Highest complexity: {_most_complex['Name']} ({_most_complex['Complexity']})")
                        else:
                            st.info("No functions detected.")

                        st.markdown("<div style='font-weight:700;color:#7a8db0;margin:.9rem 0 .5rem;font-family:\"Syne\",sans-serif'>🏷 Class Coverage</div>",
                                    unsafe_allow_html=True)
                        if _classes:
                            _class_filter = st.radio("Class filter", ["All","Documented","Missing Docstrings"],
                                                     horizontal=True, key="home_class_filter")
                            st.write(f"Documented classes: **{_documented_classes}/{_total_classes} ({_class_pct:.0f}%)**")
                            _df_classes = pd.DataFrame(_classes)
                            if _class_filter == "Documented":
                                _df_class_view = _df_classes[_df_classes["Has Docstring"]]
                            elif _class_filter == "Missing Docstrings":
                                _df_class_view = _df_classes[~_df_classes["Has Docstring"]]
                            else:
                                _df_class_view = _df_classes
                            if _df_class_view.empty:
                                st.info("No classes match the selected filter.")
                            else:
                                st.dataframe(_df_class_view[["Name","Start Line","End Line","Complexity","Has Docstring"]],
                                             use_container_width=True)
                        else:
                            st.info("No classes defined.")

                        if _functions:
                            st.markdown("<div style='font-weight:700;color:#7a8db0;margin:.9rem 0 .5rem;font-family:\"Syne\",sans-serif'>📉 Complexity Distribution</div>",
                                        unsafe_allow_html=True)
                            _cfig, _cax = plt.subplots(figsize=(7, max(3, len(_functions) * 0.4)))
                            _colors = ["#ff4d6d" if c > 5 else "#ffb830" if c > 3 else "#00d4ff"
                                       for c in [f["Complexity"] for f in _functions]]
                            _cax.barh([f["Name"] for f in _functions],
                                      [f["Complexity"] for f in _functions],
                                      color=_colors, zorder=3)
                            _cax.xaxis.grid(True, zorder=0)
                            _cax.set_axisbelow(True)
                            _cax.set_xlabel("Complexity Score")
                            _cfig.tight_layout()
                            st.pyplot(_cfig)
                            plt.close(_cfig)

                if _functions:
                    st.markdown("<div style='font-weight:700;color:#7a8db0;font-size:1rem;margin:1.1rem 0 .6rem;font-family:\"Syne\",sans-serif'>🔍 Function Details</div>",
                                unsafe_allow_html=True)
                    for _fn in _functions:
                        with st.expander(_fn["Name"]):
                            _c1, _c2, _c3 = st.columns(3)
                            _c1.metric("Complexity", _fn["Complexity"])
                            _c2.metric("Start Line", _fn["Start Line"])
                            _c3.metric("End Line", _fn["End Line"])
                            st.markdown(f"Has Docstring: {docstring_badge(_fn['Has Docstring'])}",
                                        unsafe_allow_html=True)

                if _classes:
                    st.markdown("<div style='font-weight:700;color:#7a8db0;font-size:1rem;margin:1.1rem 0 .6rem;font-family:\"Syne\",sans-serif'>🏷 Class Details</div>",
                                unsafe_allow_html=True)
                    for _cls in _classes:
                        with st.expander(_cls["Name"]):
                            _c1, _c2, _c3 = st.columns(3)
                            _c1.metric("Complexity", _cls["Complexity"])
                            _c2.metric("Start Line", _cls["Start Line"])
                            _c3.metric("End Line", _cls["End Line"])
                            st.markdown(f"Has Docstring: {docstring_badge(_cls['Has Docstring'])}",
                                        unsafe_allow_html=True)

    # ── Dashboard (formerly Scanner & Dashboard) ──────────────────────────────
    elif view == "📊 Dashboard":
        st.markdown("<div class='banner banner-teal'><span style='font-size:1.1rem'>📊</span> Dashboard</div>",
                    unsafe_allow_html=True)

        if not st.session_state.scan_done:
            st.markdown("<div class='info-banner info-tip'>👈 Upload files and click Analyse first.</div>",
                        unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-weight:700;color:#7a8db0;margin-bottom:.6rem;font-family:\"Syne\",sans-serif'>📊 Test Results</div>",
                        unsafe_allow_html=True)
            if test_summary:
                try:
                    import plotly.graph_objects as go
                    suite_names = list(test_summary.keys())
                    suite_vals  = [v["total"] for v in test_summary.values()]
                    fig = go.Figure(go.Bar(
                        x=suite_names, y=suite_vals,
                        marker_color="#667eea",
                        text=suite_vals, textposition="outside",
                    ))
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(size=11, color="#7a8db0"),
                        margin=dict(l=20, r=20, t=20, b=80),
                        height=300,
                        xaxis=dict(tickangle=-35, gridcolor="#0e1530", linecolor="#0e1530"),
                        yaxis=dict(gridcolor="#0e1530", linecolor="#0e1530", zeroline=False),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except ImportError:
                    fig, ax = plt.subplots(figsize=(8, 3))
                    suite_names = list(test_summary.keys())
                    suite_vals  = [v["total"] for v in test_summary.values()]
                    ax.bar(suite_names, suite_vals, color="#667eea")
                    ax.set_ylabel("Functions")
                    plt.xticks(rotation=35, ha="right")
                    fig.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)

            for suite, info in test_summary.items():
                passed = info["passed"]
                total  = info["total"]
                all_ok = passed == total
                row_cls = "test-row" if all_ok else "test-row test-row-fail"
                icon = "✅" if all_ok else "❌"
                st.markdown(f"""
                <div class='{row_cls}'>
                    <span>{icon} &nbsp; {suite}</span>
                    <span style='font-size:.82rem;font-weight:600'>{passed}/{total} passed</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div class='feature-banner' style='margin-top:1.5rem'><h3>✨ Enhanced UI Features</h3><p>Explore powerful analysis tools below</p></div>",
                        unsafe_allow_html=True)
            nav_cards(caller="dashboard")

    # ── Advanced Filters ──────────────────────────────────────────────────────
    elif view == "🔍 Advanced Filters":
        st.markdown("<div class='banner banner-violet'><span style='font-size:1.1rem'>🔍</span> Advanced Filters</div>",
                    unsafe_allow_html=True)

        st.markdown("<div class='feature-banner'><h3>✨ Enhanced UI Features</h3><p>Explore powerful analysis tools</p></div>",
                    unsafe_allow_html=True)
        nav_cards(caller="filters_page")

        if not st.session_state.scan_done:
            st.markdown("<div class='info-banner info-tip'>👈 Run a scan first to use filters.</div>",
                        unsafe_allow_html=True)
        else:
            col_f, col_s = st.columns([2, 1])
            with col_f:
                doc_filter = st.selectbox("📊 Documentation status", ["All", "OK", "Fix"],
                                           help="Filter by docstring presence")
            with col_s:
                file_list = ["All files"] + sorted(set(r["file"] for r in results))
                file_filter = st.selectbox("📁 File", file_list)

            filtered = results
            if doc_filter == "OK":   filtered = [r for r in filtered if r["docstring"]]
            elif doc_filter == "Fix": filtered = [r for r in filtered if not r["docstring"]]
            if file_filter != "All files": filtered = [r for r in filtered if r["file"] == file_filter]

            st.markdown(f"""
            <div class='stat-cards-row-sm'>
                <div class='stat-card-sm stat-card-blue-sm'>
                    <div class='stat-number-sm'>{len(filtered)}</div>
                    <div class='stat-label-sm'>Showing</div>
                </div>
                <div class='stat-card-sm stat-card-purple-sm'>
                    <div class='stat-number-sm'>{total_fns}</div>
                    <div class='stat-label-sm'>Total</div>
                </div>
            </div>""", unsafe_allow_html=True)

            if filtered:
                rows_html = "".join(
                    f"<tr><td>{r['file']}</td><td><code>{r['function']}</code></td>"
                    f"<td><span class='{'badge-yes' if r['docstring'] else 'badge-no'}'>"
                    f"{'✅ Yes' if r['docstring'] else '❌ No'}</span></td></tr>"
                    for r in filtered
                )
                st.markdown(f"""
                <table class='review-table'>
                    <thead><tr><th>📁 FILE</th><th>⚙️ FUNCTION</th><th>✅ DOCSTRING</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>""", unsafe_allow_html=True)
            else:
                st.warning("No functions match the selected filters.")

            st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin:2rem 0'></div>",
                        unsafe_allow_html=True)
            st.download_button("📥 Download Coverage Report JSON",
                data=coverage_report_json_scanner(),
                file_name="coverage_report.json",
                mime="application/json")

    # ── Search ────────────────────────────────────────────────────────────────
    elif view == "🔎 Search":
        st.markdown("<div class='banner banner-blue'><span style='font-size:1.1rem'>🔎</span> Search Functions</div>",
                    unsafe_allow_html=True)

        st.markdown("<div class='feature-banner'><h3>✨ Enhanced UI Features</h3><p>Explore powerful analysis tools</p></div>",
                    unsafe_allow_html=True)
        nav_cards(caller="search_page")

        query = st.text_input("🔍 Enter function name", placeholder="Type to search...", label_visibility="visible")

        if not st.session_state.scan_done:
            st.markdown("<div class='info-banner info-tip'>👈 Upload files and run Analyse first.</div>",
                        unsafe_allow_html=True)
        elif query:
            matches = [r for r in results if
                       query.lower() in r["function"].lower() or
                       query.lower() in r["file"].lower()]
            st.markdown(f"<div style='font-size:.85rem;color:#7a8db0;margin-bottom:1rem'>"
                        f"Found <strong>{len(matches)}</strong> result(s) for <em>\"{query}\"</em></div>",
                        unsafe_allow_html=True)
            for r in matches:
                doc_badge = "<span class='badge-yes'>✅ Documented</span>" if r["docstring"] \
                            else "<span class='badge-no'>❌ Missing doc</span>"
                st.markdown(f"""
                <div class='search-result'>
                    <div>
                        <div class='search-result-fn'>{r['function']}</div>
                        <div class='search-result-file'>{r['file']} · line {r['line']} · {r['args']} arg(s)</div>
                    </div>
                    {doc_badge}
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#2a3a60;font-size:.88rem;font-family:\"DM Mono\",monospace'>Type a function or file name above to search.</div>",
                        unsafe_allow_html=True)

        if st.session_state.scan_done:
            st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#0e1530,transparent);margin:2rem 0'></div>",
                        unsafe_allow_html=True)
            st.download_button("📥 Download Coverage Report JSON",
                data=coverage_report_json_scanner(),
                file_name="coverage_report.json",
                mime="application/json")

    # ── Export ────────────────────────────────────────────────────────────────
    elif view == "📤 Export":
        st.markdown("<div class='banner banner-teal'><span style='font-size:1.1rem'>📤</span> Export Results</div>",
                    unsafe_allow_html=True)

        if not st.session_state.scan_done:
            st.markdown("<div class='info-banner info-tip'>👈 Run a scan first to export.</div>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='info-banner info-live'>
                <strong>{total_fns}</strong> functions scanned &nbsp;·&nbsp;
                <strong>{total_with_doc}</strong> documented &nbsp;·&nbsp;
                <strong>{total_missing}</strong> missing docstrings
            </div>""", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                json_str = json.dumps(results, indent=2)
                st.download_button("⬇️ Download JSON", data=json_str,
                    file_name="review_results.json", mime="application/json",
                    use_container_width=True)
            with col2:
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=["file","function","line","docstring","args"])
                writer.writeheader()
                writer.writerows(results)
                st.download_button("⬇️ Download CSV", data=output.getvalue(),
                    file_name="review_results.csv", mime="text/csv",
                    use_container_width=True)

            st.markdown("<div style='font-weight:700;color:#7a8db0;margin:1rem 0 .6rem;font-family:\"Syne\",sans-serif'>Preview (first 20 rows)</div>",
                        unsafe_allow_html=True)
            preview = results[:20]
            rows_html = "".join(
                f"<tr><td>{r['file']}</td><td><code>{r['function']}</code></td>"
                f"<td>{r['line']}</td>"
                f"<td><span class='{'badge-yes' if r['docstring'] else 'badge-no'}'>"
                f"{'✅ Yes' if r['docstring'] else '❌ No'}</span></td>"
                f"<td>{r['args']}</td></tr>"
                for r in preview
            )
            st.markdown(f"""
            <table class='review-table'>
                <thead><tr><th>📁 FILE</th><th>⚙️ FUNCTION</th>
                <th>LINE</th><th>✅ DOCSTRING</th><th>ARGS</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>""", unsafe_allow_html=True)

    # ── Help & Tips ───────────────────────────────────────────────────────────
    elif view == "❓ Help & Tips":
        st.markdown("""
        <div style='background:linear-gradient(90deg,#43e97b 0%,#38f9d7 100%);
                    border-radius:14px;padding:2rem 2.2rem;margin-bottom:1.5rem'>
            <div style='display:flex;align-items:center;gap:0.8rem;margin-bottom:0.5rem'>
                <div style='background:rgba(255,255,255,0.3);border-radius:8px;padding:0.3rem 0.6rem;font-size:1.2rem'>ℹ️</div>
                <span style='font-size:1.6rem;font-weight:800;color:#fff'>Interactive Help &amp; Tips</span>
            </div>
            <div style='color:rgba(255,255,255,0.9);font-size:0.9rem;padding-left:0.3rem'>Contextual help and quick reference guide</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style='background:#f0faf4;border:1.5px solid #b6ecd1;border-left:5px solid #22c55e;
                        border-radius:12px;padding:1.6rem 1.8rem;margin-bottom:1rem;min-height:215px'>
                <div style='display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem'>
                    <span style='font-size:1.3rem'>📊</span>
                    <span style='font-size:1.1rem;font-weight:700;color:#16a34a'>Coverage Metrics</span>
                </div>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Coverage % = (Documented / Total) × 100</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Green badge (🟢): ≥90% coverage</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Yellow badge (🟡): 70-89% coverage</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Red badge (🔴): &lt;70% coverage</p>
            </div>""", unsafe_allow_html=True)

            st.markdown("""
            <div style='background:#eff6ff;border:1.5px solid #bfdbfe;border-left:5px solid #3b82f6;
                        border-radius:12px;padding:1.6rem 1.8rem;margin-bottom:1rem;min-height:215px'>
                <div style='display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem'>
                    <span style='font-size:1.3rem'>✏️</span>
                    <span style='font-size:1.1rem;font-weight:700;color:#2563eb'>Test Results</span>
                </div>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Real-time test execution monitoring</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Pass/fail ratio visualization</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Per-file test breakdown</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Integration with pytest reports</p>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style='background:#fffbeb;border:1.5px solid #fde68a;border-left:5px solid #f59e0b;
                        border-radius:12px;padding:1.6rem 1.8rem;margin-bottom:1rem;min-height:215px'>
                <div style='display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem'>
                    <span style='font-size:1.3rem'>✅</span>
                    <span style='font-size:1.1rem;font-weight:700;color:#d97706'>Function Status</span>
                </div>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• ✅ Green: Complete docstring present</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• ❌ Red: Missing or incomplete docstring</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Auto-detection of docstring styles</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Style-specific validation</p>
            </div>""", unsafe_allow_html=True)

            st.markdown("""
            <div style='background:#faf5ff;border:1.5px solid #e9d5ff;border-left:5px solid #8b5cf6;
                        border-radius:12px;padding:1.6rem 1.8rem;margin-bottom:1rem;min-height:215px'>
                <div style='display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem'>
                    <span style='font-size:1.3rem'>📝</span>
                    <span style='font-size:1.1rem;font-weight:700;color:#7c3aed'>Docstring Styles</span>
                </div>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• <strong>Google</strong>: Args:, Returns:, Raises:</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• <strong>NumPy</strong>: Parameters/Returns with dashes</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• <strong>reST</strong>: :param, :type, :return directives</p>
                <p style='margin:.45rem 0;font-size:.84rem;color:#374151'>• Auto-style detection &amp; validation</p>
            </div>""", unsafe_allow_html=True)

        with st.expander("📖 Advanced Usage Guide"):
            st.markdown("""
**Scanning a project**
Upload one or more `.py` files using the sidebar uploader in the 📊 Dashboard mode, then click **Analyse** to extract all functions and check docstring coverage.

**Using the Docstring Reviewer**
Switch to 🔮 Docstring Reviewer mode, paste a `.py` file or folder path, click **Load**, then browse and generate/edit docstrings per function.

**Using Validation**
Switch to ✅ Validation, upload a file or browse a folder, then use **Dashboard** or **PEP Validation** buttons to analyse.

**Reading results**
- The **Dashboard** groups functions by file and shows pass/fail counts per group.
- Use **Advanced Filters** to drill down by documentation status or specific file.
- Use **Search** to instantly locate any function by name.

**Exporting**
Download results as **JSON** (full metadata) or **CSV** (spreadsheet-ready) from the Export page or the inline Export card.

**Pro tip**
Export the CSV and import it into your issue tracker (Jira, GitHub Issues, Linear) to turn documentation gaps into trackable tickets.
            """)