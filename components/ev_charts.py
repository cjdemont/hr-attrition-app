# =============================================================================
# components/ev_charts.py
# The four Economic Value charts (Sections 1–4), each with Plotly + sliders.
# Colors follow the Posit brand palette:
#   Primary blue:  #3D6B8E
#   Gray:          #404041
#   Orange accent: #E6772E
#   Light blue bg: #EAF1F7
# =============================================================================

import numpy as np
import plotly.graph_objects as go
import streamlit as st

# ---- Shared helpers --------------------------------------------------------

POSIT_BLUE   = "#3D6B8E"
POSIT_GRAY   = "#404041"
POSIT_ORANGE = "#E6772E"
POSIT_TEAL   = "#3B8B8A"
POSIT_LIGHT  = "#EAF1F7"
POSIT_RED    = "#A32D2D"

def _base_layout(title="Value To Organization Over Time") -> dict:
    return dict(
        title=dict(text=title, font=dict(size=15, color=POSIT_GRAY)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            title="Time (months)",
            showgrid=True, gridcolor="#E8E8E4", zeroline=True,
            zerolinecolor="#D3D1C7", zerolinewidth=1,
            tickfont=dict(color=POSIT_GRAY),
        ),
        yaxis=dict(
            title="Economic Value",
            showgrid=True, gridcolor="#E8E8E4", zeroline=True,
            zerolinecolor=POSIT_GRAY, zerolinewidth=1.5,
            tickfont=dict(color=POSIT_GRAY),
            showticklabels=False,
        ),
        margin=dict(l=50, r=30, t=50, b=50),
        height=340,
        font=dict(family="Arial, sans-serif", color=POSIT_GRAY),
        showlegend=False,
    )


def _ev_curve(months, steepness=0.12, offset=10) -> np.ndarray:
    """Sigmoid-based economic value curve: negative early, growing positive."""
    t = np.array(months, dtype=float)
    return 1 / (1 + np.exp(-steepness * (t - offset))) - 0.35


# ---- Section 1: EV over time -----------------------------------------------

def ev_chart_section1(tenure_months: int) -> go.Figure:
    t = np.linspace(0, 60, 300)
    ev = _ev_curve(t)
    ev_at_tenure = float(_ev_curve([tenure_months])[0])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t, y=ev, mode="lines",
        line=dict(color=POSIT_BLUE, width=2.5),
        name="EV curve",
    ))
    # Dot tracking along curve
    fig.add_trace(go.Scatter(
        x=[tenure_months], y=[ev_at_tenure],
        mode="markers",
        marker=dict(size=14, color=POSIT_ORANGE, line=dict(color="white", width=2)),
        name="Current tenure",
    ))
    # Formula annotation
    fig.add_annotation(
        x=48, y=-0.2,
        text="EV(t) = Value(t) − Cost(t)",
        showarrow=False,
        font=dict(size=12, color=POSIT_GRAY),
        bgcolor="white",
        bordercolor=POSIT_GRAY,
        borderwidth=1,
        borderpad=6,
    )
    ev_label = "positive" if ev_at_tenure >= 0 else "negative"
    fig.add_annotation(
        x=tenure_months, y=ev_at_tenure + 0.08,
        text=f"Month {tenure_months}: EV is {ev_label}",
        showarrow=True, arrowhead=2, arrowcolor=POSIT_ORANGE,
        font=dict(size=11, color=POSIT_ORANGE),
        ax=30, ay=-30,
    )
    layout = _base_layout()
    layout["yaxis"]["range"] = [-0.5, 0.8]
    fig.update_layout(**layout)
    return fig


# ---- Section 2: Investment / Return / Break-even ---------------------------

def ev_chart_section2(breakeven_months: int, onboarding_cost: int) -> go.Figure:
    t = np.linspace(0, 60, 300)
    ev = _ev_curve(t, offset=breakeven_months * 0.6)

    # Find actual breakeven x
    be_idx = np.argmin(np.abs(ev))
    be_x = float(t[be_idx])

    fig = go.Figure()
    # Investment zone shading
    fig.add_vrect(
        x0=0, x1=be_x,
        fillcolor="#D3D1C7", opacity=0.35, line_width=0,
        annotation_text="Investment Zone",
        annotation_position="top left",
        annotation_font=dict(color=POSIT_GRAY, size=12),
    )
    # Return zone shading
    fig.add_vrect(
        x0=be_x, x1=60,
        fillcolor=POSIT_LIGHT, opacity=0.55, line_width=0,
        annotation_text="Return Zone",
        annotation_position="top right",
        annotation_font=dict(color=POSIT_BLUE, size=13),
    )
    fig.add_trace(go.Scatter(
        x=t, y=ev, mode="lines",
        line=dict(color=POSIT_BLUE, width=2.5),
    ))
    # Break-even dot
    fig.add_trace(go.Scatter(
        x=[be_x], y=[0],
        mode="markers+text",
        marker=dict(size=12, color=POSIT_GRAY, line=dict(color="white", width=2)),
        text=["Break Even"], textposition="bottom right",
        textfont=dict(size=11, color=POSIT_GRAY),
    ))
    # Onboarding cost annotation
    fig.add_annotation(
        x=be_x / 2, y=-0.28,
        text=f"Onboarding cost: ${onboarding_cost:,}",
        showarrow=False,
        font=dict(size=11, color=POSIT_GRAY),
        bgcolor="white",
        bordercolor="#D3D1C7",
        borderwidth=1, borderpad=4,
    )
    layout = _base_layout()
    layout["yaxis"]["range"] = [-0.5, 0.8]
    fig.update_layout(**layout)
    return fig


# ---- Section 3: The Quit Event ---------------------------------------------

def ev_chart_section3(quit_month: int, show_replacement: bool) -> go.Figure:
    t = np.linspace(0, 60, 300)
    ev = _ev_curve(t)
    quit_ev = float(_ev_curve([quit_month])[0])

    fig = go.Figure()
    # Original employee curve up to quit
    t_before = t[t <= quit_month]
    ev_before = _ev_curve(t_before)
    fig.add_trace(go.Scatter(
        x=t_before, y=ev_before, mode="lines",
        line=dict(color=POSIT_BLUE, width=2.5),
        name="Original employee",
    ))
    # Dashed continuation (what would have been)
    fig.add_trace(go.Scatter(
        x=t[t > quit_month], y=_ev_curve(t[t > quit_month]),
        mode="lines",
        line=dict(color=POSIT_BLUE, width=1.5, dash="dot"),
        opacity=0.35,
        name="Unrealised value",
    ))
    # Quit drop line
    fig.add_trace(go.Scatter(
        x=[quit_month, quit_month], y=[quit_ev, -0.45],
        mode="lines",
        line=dict(color=POSIT_RED, width=2, dash="dash"),
        name="Resignation",
    ))
    # I Quit annotation
    fig.add_annotation(
        x=quit_month, y=quit_ev + 0.08,
        text="✕  I Quit!",
        showarrow=True, arrowhead=2, arrowcolor=POSIT_RED,
        font=dict(size=12, color=POSIT_RED),
        ax=-50, ay=-30,
    )
    # Replacement curve starting from quit_month
    if show_replacement:
        t_rep = np.linspace(quit_month, 60, 200)
        ev_rep = _ev_curve(t_rep - quit_month, steepness=0.12, offset=10)
        fig.add_trace(go.Scatter(
            x=t_rep, y=ev_rep, mode="lines",
            line=dict(color=POSIT_ORANGE, width=2, dash="longdash"),
            name="Replacement hire",
        ))
        fig.update_layout(showlegend=True)

    layout = _base_layout()
    layout["yaxis"]["range"] = [-0.55, 0.8]
    fig.update_layout(**layout)
    return fig


# ---- Section 4: Lost Productivity + Time -----------------------------------

def ev_chart_section4(
    quit_month: int,
    replacement_weeks: int,
    productivity_loss_pct: int,
    annual_salary: int,
) -> tuple[go.Figure, float]:
    """Returns the Plotly figure and the estimated dollar cost."""
    t = np.linspace(0, 60, 300)
    ev = _ev_curve(t)
    quit_ev = float(_ev_curve([quit_month])[0])

    # Cost calculation
    weekly_salary = annual_salary / 52
    lost_time_cost = weekly_salary * replacement_weeks
    lost_prod_cost = annual_salary * (productivity_loss_pct / 100) * (replacement_weeks / 52)
    total_cost = lost_time_cost + lost_prod_cost

    # Shaded loss rectangle
    rect_x0 = quit_month
    rect_x1 = min(quit_month + replacement_weeks / 4.33, 60)  # weeks → months
    rect_y0 = -0.45
    rect_y1 = quit_ev

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t[t <= quit_month],
        y=_ev_curve(t[t <= quit_month]),
        mode="lines",
        line=dict(color=POSIT_BLUE, width=2.5),
        name="Employee value",
    ))
    # Loss shading rectangle
    fig.add_shape(
        type="rect",
        x0=rect_x0, x1=rect_x1, y0=rect_y0, y1=rect_y1,
        fillcolor="#3D6B8E", opacity=0.18,
        line=dict(color=POSIT_BLUE, width=1),
    )
    # Lost Productivity arrow (vertical)
    fig.add_annotation(
        x=(rect_x0 + rect_x1) / 2 + 1.5, y=(rect_y0 + rect_y1) / 2,
        text="Lost Productivity",
        showarrow=False, textangle=-90,
        font=dict(size=10, color=POSIT_BLUE),
    )
    # Lost Time arrow (horizontal)
    fig.add_annotation(
        x=(rect_x0 + rect_x1) / 2, y=rect_y0 - 0.06,
        text="← Lost Time →",
        showarrow=False,
        font=dict(size=10, color=POSIT_BLUE),
    )
    # Quit marker
    fig.add_trace(go.Scatter(
        x=[quit_month], y=[quit_ev],
        mode="markers",
        marker=dict(size=12, color=POSIT_RED, line=dict(color="white", width=2)),
    ))
    layout = _base_layout()
    layout["yaxis"]["range"] = [-0.65, 0.8]
    fig.update_layout(**layout)
    return fig, total_cost
