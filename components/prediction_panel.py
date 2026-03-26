# =============================================================================
# components/prediction_panel.py
# Employee risk assessment panel: profile card, SHAP bar chart, feature map.
# =============================================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import shap
import streamlit as st
import joblib
from pathlib import Path

POSIT_BLUE   = "#3D6B8E"
POSIT_GRAY   = "#404041"
POSIT_ORANGE = "#E6772E"
POSIT_LIGHT  = "#EAF1F7"
POSIT_RED    = "#A32D2D"
POSIT_GREEN  = "#3B6D11"

MODEL_PATH = Path("model/attrition_model.pkl")

FEATURE_LABELS = {
    "OverTime":               "Overtime status",
    "StockOptionLevel":       "Stock option level",
    "YearsAtCompany":         "Years at company",
    "NumCompaniesWorked":     "Number of companies worked",
    "JobSatisfaction":        "Job satisfaction",
    "TrainingTimesLastYear":  "Training sessions last year",
    "JobLevel":               "Job level",
    "WorkLifeBalance":        "Work-life balance",
    "MonthlyIncome":          "Monthly income",
    "YearsSinceLastPromotion":"Years since last promotion",
}

SATISFACTION_MAP = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
WLB_MAP          = {1: "Bad",  2: "Good",  3: "Better", 4: "Best"}


@st.cache_resource
def load_model():
    artifact = joblib.load(MODEL_PATH)
    return artifact


def _persona_to_df(persona: dict, features: list) -> pd.DataFrame:
    row = {f: persona[f] for f in features}
    return pd.DataFrame([row])


def _get_shap_values(pipeline, X_df: pd.DataFrame) -> np.ndarray:
    """Transform with preprocessor, then compute SHAP for the attrition (class=1) output."""
    X_transformed = pipeline.named_steps["preprocessor"].transform(X_df)
    explainer = shap.TreeExplainer(pipeline.named_steps["classifier"])
    sv = explainer.shap_values(X_transformed)
    # sv shape: (n_classes, n_samples, n_features) or (n_samples, n_features)
    if isinstance(sv, list):
        return sv[1][0]   # class 1 = Attrition
    return sv[0]


def feature_contribution_chart(shap_vals: np.ndarray, feature_names: list) -> go.Figure:
    labels = [FEATURE_LABELS.get(f, f) for f in feature_names]
    colors = [POSIT_RED if v < 0 else POSIT_BLUE for v in shap_vals]
    # Negative SHAP = pushes toward attrition (reversed for HR intuition)
    bar_vals = [-v for v in shap_vals]
    sorted_idx = np.argsort(np.abs(bar_vals))[::-1]

    fig = go.Figure(go.Bar(
        x=[bar_vals[i] for i in sorted_idx],
        y=[labels[i] for i in sorted_idx],
        orientation="h",
        marker=dict(
            color=[colors[i] for i in sorted_idx],
            line=dict(width=0),
        ),
        hovertemplate="%{y}: %{x:.3f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_width=1.5, line_color=POSIT_GRAY)
    fig.update_layout(
        title=dict(text="Feature Contributions to Attrition Risk", font=dict(size=14, color=POSIT_GRAY)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            title="← Higher Risk   |   Lower Risk →",
            showgrid=True, gridcolor="#E8E8E4",
            zeroline=False,
            tickfont=dict(color=POSIT_GRAY, size=10),
        ),
        yaxis=dict(
            tickfont=dict(color=POSIT_GRAY, size=11),
            autorange="reversed",
        ),
        margin=dict(l=10, r=20, t=50, b=50),
        height=380,
        font=dict(family="Arial, sans-serif"),
        showlegend=False,
    )
    return fig


def feature_description_table(shap_vals: np.ndarray, feature_names: list) -> pd.DataFrame:
    rows = []
    for i, f in enumerate(feature_names):
        sv = shap_vals[i]
        direction = "High Risk" if sv < 0 else "Low Risk"
        rows.append({"Feature": FEATURE_LABELS.get(f, f), "Direction": direction})
    return pd.DataFrame(rows).sort_values("Direction")


def render_prediction_panel(persona: dict, cfg: dict):
    artifact = load_model()
    pipeline = artifact["pipeline"]
    features = artifact["features"]

    X_df = _persona_to_df(persona, features)
    proba = pipeline.predict_proba(X_df)[0]
    pred  = pipeline.predict(X_df)[0]

    p_attrite = proba[1] * 100
    p_stay    = proba[0] * 100
    is_risk   = pred == 1

    shap_vals = _get_shap_values(pipeline, X_df)

    # --- Layout: 3 columns ---
    col_left, col_mid, col_right = st.columns([1.1, 1.8, 1.1])

    with col_left:
        risk_color = POSIT_RED if is_risk else POSIT_BLUE
        risk_label = cfg["section5"]["risk_high_label"] if is_risk else cfg["section5"]["risk_low_label"]
        prediction_text = "Yes" if is_risk else "No"

        st.markdown(
            f"""
            <div style="
                border: 1px solid #D3D1C7;
                border-radius: 10px;
                padding: 1.2rem;
                background: white;
                height: 100%;
            ">
                <div style="font-size:0.8rem; color:#888780; margin-bottom:0.3rem;">
                    {persona['id']}
                </div>
                <div style="font-size:1.05rem; font-weight:600; color:{risk_color}; margin-bottom:0.8rem;">
                    Attrition Prediction: {prediction_text}
                </div>
                <div style="font-size:0.85rem; color:{POSIT_GRAY}; margin-bottom:0.2rem;">
                    {risk_label} Prediction: <strong>{p_attrite:.1f}%</strong>
                </div>
                <div style="font-size:0.85rem; color:{POSIT_GRAY}; margin-bottom:1rem;">
                    Low Risk Prediction: <strong>{p_stay:.1f}%</strong>
                </div>
                <hr style="border-top:1px solid #E8E8E4; margin: 0.8rem 0;">
                <div style="font-size:0.8rem; color:#888780;">Job Role:</div>
                <div style="font-size:0.9rem; color:{POSIT_GRAY}; margin-bottom:0.5rem;">{persona['job_role']}</div>
                <div style="font-size:0.8rem; color:#888780;">Department:</div>
                <div style="font-size:0.9rem; color:{POSIT_GRAY}; margin-bottom:0.5rem;">{persona['department']}</div>
                <div style="font-size:0.8rem; color:#888780;">Education Field:</div>
                <div style="font-size:0.9rem; color:{POSIT_GRAY};">{persona['education_field']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_mid:
        fig = feature_contribution_chart(shap_vals, features)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        df_table = feature_description_table(shap_vals, features)
        st.markdown(
            "<div style='font-size:0.9rem; font-weight:600; color:#3D6B8E; margin-bottom:0.5rem;'>"
            "Feature Description Map</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(
            df_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Feature": st.column_config.TextColumn("Feature"),
                "Direction": st.column_config.TextColumn("Direction"),
            },
            height=360,
        )


def render_manual_entry_form(cfg: dict):
    """Allow users to enter custom feature values and get a live prediction."""
    st.markdown(
        f"<p style='font-size:0.88rem; color:#888780; font-style:italic;'>"
        f"{cfg['section5']['manual_entry_hint']}</p>",
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        overtime       = st.selectbox("Overtime", ["No", "Yes"])
        stock_option   = st.slider("Stock option level", 0, 3, 1)
        years_at_co    = st.slider("Years at company", 0, 40, 5)
        num_companies  = st.slider("Number of companies worked", 0, 10, 2)
        job_sat        = st.select_slider(
            "Job satisfaction",
            options=[1, 2, 3, 4],
            format_func=lambda x: SATISFACTION_MAP[x],
            value=3,
        )
    with col2:
        training_times = st.slider("Training sessions last year", 0, 6, 3)
        job_level      = st.slider("Job level (1 = entry, 5 = director)", 1, 5, 2)
        wlb            = st.select_slider(
            "Work-life balance",
            options=[1, 2, 3, 4],
            format_func=lambda x: WLB_MAP[x],
            value=3,
        )
        monthly_income = st.number_input(
            "Monthly income ($)", min_value=1000, max_value=30000,
            value=5000, step=500,
        )
        yrs_promo      = st.slider("Years since last promotion", 0, 15, 2)

    custom_persona = {
        "id": "CUSTOM",
        "name": "Custom Employee",
        "job_role": "—",
        "department": "—",
        "education_field": "—",
        "arc": "custom",
        "OverTime": overtime,
        "StockOptionLevel": stock_option,
        "YearsAtCompany": years_at_co,
        "NumCompaniesWorked": num_companies,
        "JobSatisfaction": job_sat,
        "TrainingTimesLastYear": training_times,
        "JobLevel": job_level,
        "WorkLifeBalance": wlb,
        "MonthlyIncome": monthly_income,
        "YearsSinceLastPromotion": yrs_promo,
    }
    render_prediction_panel(custom_persona, cfg)
