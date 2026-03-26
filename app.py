# =============================================================================
# app.py — HR Attrition Data Experience
# Main Streamlit entry point. All text is loaded from config/text_content.yaml.
# Deploy to Posit Connect Cloud: rsconnect deploy streamlit --name myconnect .
# =============================================================================

import yaml
import streamlit as st
from pathlib import Path

from components.section_header import (
    section_header, pull_quote, interaction_hint, divider
)
from components.ev_charts import (
    ev_chart_section1,
    ev_chart_section2,
    ev_chart_section3,
    ev_chart_section4,
)
from components.prediction_panel import (
    render_prediction_panel,
    render_manual_entry_form,
)
from data.personas import PERSONAS, PERSONA_MAP, PERSONA_OPTIONS

# ---- Page config -----------------------------------------------------------
st.set_page_config(
    page_title="HR Attrition | Posit Connect",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---- Load text content -----------------------------------------------------
@st.cache_data
def load_cfg():
    with open(Path("config/text_content.yaml"), "r") as f:
        return yaml.safe_load(f)

cfg = load_cfg()

# ---- Global style tweaks ---------------------------------------------------
st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 1100px; }
    h1 { color: #3D6B8E !important; }
    h2 { color: #3D6B8E !important; }
    .stSlider > div > div > div { background: #3D6B8E !important; }
    .stSelectbox label, .stSlider label { color: #404041 !important; }
    div[data-testid="stDataFrame"] { border: 1px solid #D3D1C7; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HEADER BANNER
# =============================================================================
st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, #3D6B8E 0%, #2A4F6B 100%);
        padding: 2.5rem 2rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    ">
        <h1 style="color: white !important; margin: 0; font-size: 2rem;">
            {cfg['header']['title']}
        </h1>
        <p style="color: #B5D4F4; margin: 0.4rem 0 1rem; font-size: 1.1rem;">
            {cfg['header']['subtitle']}
        </p>
        <div style="
            background: rgba(230, 119, 46, 0.15);
            border-left: 4px solid #E6772E;
            padding: 0.8rem 1rem;
            border-radius: 0 8px 8px 0;
            color: #EAF1F7;
            font-size: 0.9rem;
            line-height: 1.6;
        ">
            {cfg['header']['demo_banner']}
        </div>
        <p style="color: #7BA7C4; margin: 0.8rem 0 0; font-size: 0.8rem;">
            {cfg['header']['built_with']}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# INTRODUCTION
# =============================================================================
section_header(
    cfg["intro"]["title"],
    body=cfg["intro"]["body"],
)
pull_quote(cfg["intro"]["pull_quote"])
st.markdown(cfg["intro"]["body_2"])
divider()


# =============================================================================
# SECTION 1 — EV Over Time
# =============================================================================
section_header(
    cfg["section1"]["title"],
    subtitle=cfg["section1"]["subtitle"],
    body=cfg["section1"]["body"],
    body_2=cfg["section1"]["formula_note"],
)
interaction_hint(cfg["section1"]["interaction_hint"])

tenure = st.slider(
    "Employee tenure (months)", min_value=1, max_value=60, value=12, step=1,
    key="s1_tenure",
)
st.plotly_chart(
    ev_chart_section1(tenure),
    use_container_width=True,
    config={"displayModeBar": False},
)
divider()


# =============================================================================
# SECTION 2 — Investment / Return Zones
# =============================================================================
section_header(
    cfg["section2"]["title"],
    subtitle=cfg["section2"]["subtitle"],
    body=cfg["section2"]["body"],
    body_2=cfg["section2"]["body_2"],
)
interaction_hint(cfg["section2"]["interaction_hint"])

col_s2a, col_s2b = st.columns(2)
with col_s2a:
    breakeven = st.slider(
        "Break-even point (months)", min_value=3, max_value=30, value=12, step=1,
        key="s2_breakeven",
    )
with col_s2b:
    onboarding = st.select_slider(
        "Onboarding cost estimate",
        options=[5000, 10000, 15000, 20000, 30000, 40000, 50000],
        value=15000,
        format_func=lambda x: f"${x:,}",
        key="s2_onboarding",
    )
st.plotly_chart(
    ev_chart_section2(breakeven, onboarding),
    use_container_width=True,
    config={"displayModeBar": False},
)
divider()


# =============================================================================
# SECTION 3 — The Quit Event
# =============================================================================
section_header(
    cfg["section3"]["title"],
    subtitle=cfg["section3"]["subtitle"],
    body=cfg["section3"]["body"],
    body_2=cfg["section3"]["body_2"],
)
interaction_hint(cfg["section3"]["interaction_hint"])

col_s3a, col_s3b = st.columns([3, 1])
with col_s3a:
    quit_month = st.slider(
        "Month the employee resigns", min_value=1, max_value=55, value=18, step=1,
        key="s3_quit",
    )
with col_s3b:
    show_replacement = st.toggle("Show replacement hire", value=True, key="s3_repl")

st.plotly_chart(
    ev_chart_section3(quit_month, show_replacement),
    use_container_width=True,
    config={"displayModeBar": False},
)
divider()


# =============================================================================
# SECTION 4 — Lost Productivity + Time
# =============================================================================
section_header(
    cfg["section4"]["title"],
    subtitle=cfg["section4"]["subtitle"],
    body=cfg["section4"]["body"],
    body_2=cfg["section4"]["body_2"],
)
interaction_hint(cfg["section4"]["interaction_hint"])

col_s4a, col_s4b, col_s4c = st.columns(3)
with col_s4a:
    quit_month_4 = st.slider(
        "Month employee leaves", min_value=1, max_value=55, value=18, step=1,
        key="s4_quit",
    )
with col_s4b:
    replacement_weeks = st.slider(
        "Weeks to replace", min_value=4, max_value=52, value=16, step=2,
        key="s4_weeks",
    )
    prod_loss = st.slider(
        "Productivity loss (%)", min_value=10, max_value=100, value=40, step=5,
        key="s4_prod",
    )
with col_s4c:
    annual_salary = st.number_input(
        "Annual salary of role ($)", min_value=20000, max_value=300000,
        value=75000, step=5000, key="s4_salary",
    )

fig_s4, total_cost = ev_chart_section4(
    quit_month_4, replacement_weeks, prod_loss, annual_salary
)
st.plotly_chart(fig_s4, use_container_width=True, config={"displayModeBar": False})

st.markdown(
    f"""
    <div style="
        background: #EAF1F7;
        border: 1px solid #B5D4F4;
        border-left: 5px solid #3D6B8E;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-top: 0.5rem;
    ">
        <span style="font-size: 1.05rem; color: #3D6B8E; font-weight: 600;">
            Estimated cost of this attrition event:&nbsp;
        </span>
        <span style="font-size: 1.3rem; color: #A32D2D; font-weight: 700;">
            ${total_cost:,.0f}
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
divider()


# =============================================================================
# BRIDGE SECTION
# =============================================================================
section_header(
    cfg["bridge"]["title"],
    subtitle=cfg["bridge"]["subtitle"],
    body=cfg["bridge"]["body"],
    body_2=cfg["bridge"]["body_2"],
)
st.markdown(cfg["bridge"]["body_3"])
divider()


# =============================================================================
# SECTION 5 — Employee Risk Assessment
# =============================================================================
section_header(
    cfg["section5"]["title"],
    subtitle=cfg["section5"]["subtitle"],
    body=cfg["section5"]["body"],
)

# Persona selector
selected_label = st.selectbox(
    "Select an employee profile",
    options=list(PERSONA_OPTIONS.keys()),
    key="persona_selector",
)
selected_id = PERSONA_OPTIONS[selected_label]
persona = PERSONA_MAP[selected_id]

# Arc badge
arc_colors = {"high": "#A32D2D", "borderline": "#E6772E", "low": "#3B6D11"}
arc_labels = {"high": "High Risk Profile", "borderline": "Borderline Profile", "low": "Low Risk Profile"}
arc_color = arc_colors.get(persona["arc"], "#404041")
arc_label = arc_labels.get(persona["arc"], "")

st.markdown(
    f"""<span style="
        background:{arc_color}; color:white; padding:0.25rem 0.75rem;
        border-radius:20px; font-size:0.8rem; font-weight:500;
    ">{arc_label}</span>""",
    unsafe_allow_html=True,
)
st.markdown("")

render_prediction_panel(persona, cfg)

# Manual entry toggle
st.markdown("<br>", unsafe_allow_html=True)
manual_mode = st.toggle(
    cfg["section5"]["manual_entry_label"],
    value=False, key="manual_toggle",
)
if manual_mode:
    render_manual_entry_form(cfg)

divider()


# =============================================================================
# SECTION 6 — Methodology
# =============================================================================
section_header(
    cfg["section6"]["title"],
    subtitle=cfg["section6"]["subtitle"],
    body=cfg["section6"]["body"],
    body_2=cfg["section6"]["body_2"],
)
st.markdown(cfg["section6"]["body_3"])

st.info(
    f"**Model performance note:** {cfg['section6']['accuracy_note']}",
    icon="ℹ️",
)
st.markdown(
    f"[{cfg['section6']['repo_note']}]({cfg['footer']['repo_url']})"
    if cfg["footer"]["repo_url"] != "https://github.com/your-org/hr-attrition-app"
    else f"_{cfg['section6']['repo_note']}_"
)
divider()


# =============================================================================
# FOOTER
# =============================================================================
st.markdown(
    f"""
    <div style="
        text-align: center;
        color: #888780;
        font-size: 0.8rem;
        padding: 1rem 0 2rem;
    ">
        {cfg['footer']['built_with']} &nbsp;·&nbsp; {cfg['footer']['deployed_on']}
        <br>
        {cfg['footer']['dataset_credit']}
    </div>
    """,
    unsafe_allow_html=True,
)
