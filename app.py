"""
FraudGuard executive dashboard.
Reads results.csv written by consumer.py.
Run with: python -m streamlit run app.py
"""

import os
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RESULTS_FILE = "results.csv"
REFRESH = 3
WINDOW = 2500

st.set_page_config(
    page_title="FraudGuard Control Room",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f4f8fc;
    --bg-soft: #edf4fb;
    --surface: rgba(255, 255, 255, 0.94);
    --surface-strong: #ffffff;
    --line: #dce6ef;
    --text: #122033;
    --muted: #6b7e91;
    --navy: #15324c;
    --cyan: #1d9bf0;
    --teal: #44b6a1;
    --coral: #df3f46;
    --gold: #e9b949;
    --violet: #7b7cf6;
    --space-1: 8px;
    --space-2: 16px;
    --space-3: 24px;
    --space-4: 32px;
    --card-pad: 18px;
    --shadow: 0 14px 34px rgba(24, 54, 84, 0.07);
}

html, body, [class*="css"] {
    font-family: "Manrope", sans-serif;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(circle at 0% 0%, rgba(29, 155, 240, 0.10), transparent 22%),
        radial-gradient(circle at 100% 16%, rgba(20, 184, 166, 0.08), transparent 20%),
        linear-gradient(180deg, #fbfdff 0%, #f3f8fd 44%, #eef4fa 100%);
}

#MainMenu, footer, header, [data-testid="stToolbar"] {
    display: none !important;
}

.block-container {
    max-width: 1180px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-top: var(--space-2);
    padding-left: var(--space-3);
    padding-right: var(--space-3);
    padding-bottom: var(--space-4);
}

@media (max-width: 900px) {
    .block-container {
        padding-left: 0.85rem;
        padding-right: 0.85rem;
    }
}

[data-testid="stPlotlyChart"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0.75rem 0.8rem 0.5rem;
    box-shadow: var(--shadow);
    overflow: visible;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 8px;
    box-shadow: var(--shadow);
    overflow: hidden;
}

[data-testid="stExpander"] {
    background: var(--surface-strong) !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    box-shadow: var(--shadow);
}

[data-testid="stExpander"] details summary p {
    color: var(--text) !important;
    font-weight: 800 !important;
}

.hero-card {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: var(--space-2);
    align-items: stretch;
    padding: 0;
    text-align: left;
}

.hero-summary {
    grid-column: span 2;
    grid-row: span 2;
    padding: var(--card-pad);
    border-radius: 8px;
    border: 1px solid var(--line);
    background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(243,248,253,0.95));
    box-shadow: var(--shadow);
}

.spotlight-card {
    min-height: 100%;
    padding: var(--card-pad);
    border-radius: 8px;
    border: 1px solid var(--line);
    background:
        radial-gradient(circle at top left, rgba(20, 184, 166, 0.10), transparent 32%),
        linear-gradient(135deg, rgba(255,255,255,0.98), rgba(240,247,255,0.97));
    box-shadow: var(--shadow);
}

.eyebrow {
    color: var(--cyan);
    font-size: 0.74rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0;
}

.hero-title {
    margin: 8px 0 8px;
    color: var(--text);
    font-family: "Space Grotesk", sans-serif;
    font-size: 2rem;
    line-height: 1.05;
    letter-spacing: 0;
    max-width: 19ch;
}

.hero-copy {
    color: var(--muted);
    font-size: 0.92rem;
    line-height: 1.55;
    max-width: 58ch;
}

.mini-grid {
    display: contents;
}

.mini-card {
    padding: var(--card-pad);
    border-radius: 8px;
    border: 1px solid var(--line);
    background: rgba(255, 255, 255, 0.78);
}

.mini-label {
    color: #7a8ca0;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0;
}

.mini-value {
    margin-top: var(--space-1);
    color: var(--text);
    font-size: 1.55rem;
    font-weight: 800;
}

.mini-note {
    margin-top: 6px;
    color: var(--muted);
    font-size: 0.78rem;
    line-height: 1.45;
}

.spotlight-label {
    color: var(--cyan);
    font-size: 0.74rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0;
}

.spotlight-value {
    margin-top: 10px;
    color: var(--text);
    font-family: "Space Grotesk", sans-serif;
    font-size: 3rem;
    line-height: 1;
    letter-spacing: 0;
}

.spotlight-copy {
    margin-top: 12px;
    color: var(--muted);
    font-size: 0.95rem;
    line-height: 1.7;
}

.spotlight-stack {
    display: grid;
    gap: var(--space-2);
    margin-top: var(--space-2);
}

.spotlight-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 12px;
    align-items: center;
    padding: 10px 12px;
    border-radius: 8px;
    background: rgba(29, 155, 240, 0.05);
    border: 1px solid rgba(216, 228, 240, 0.9);
}

.spotlight-row-label {
    color: var(--muted);
    font-size: 0.83rem;
}

.spotlight-row-value {
    color: var(--text);
    font-weight: 800;
}

.metric-card {
    padding: var(--card-pad);
    min-height: 144px;
    border-radius: 8px;
    border: 1px solid var(--line);
    background: var(--surface);
    box-shadow: var(--shadow);
    text-align: center;
}

.metric-label {
    color: #7a8ca0;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0;
}

.metric-value {
    margin-top: var(--space-1);
    color: var(--text);
    font-size: 2.35rem;
    font-weight: 800;
    line-height: 1;
}

.metric-card.metric-coral {
    border-color: rgba(223, 63, 70, 0.28);
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(255, 246, 246, 0.95));
}

.metric-card.metric-teal {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(245, 252, 250, 0.95));
}

.metric-card.metric-coral .metric-value {
    color: var(--coral);
}

.metric-card.metric-teal .metric-value {
    color: #399d8a;
}

.metric-card.metric-gold .metric-value {
    color: #b78119;
}

.metric-card.metric-cyan .metric-value {
    color: var(--cyan);
}

.metric-note {
    margin-top: var(--space-1);
    color: var(--muted);
    font-size: 0.8rem;
    line-height: 1.5;
    max-width: 28ch;
    margin-left: auto;
    margin-right: auto;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: var(--space-2);
    margin: var(--space-2) 0 var(--space-3);
}

.section-head {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: var(--space-2);
    margin: var(--space-3) 2px var(--space-1);
}

.section-title {
    color: var(--text);
    font-family: "Space Grotesk", sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0;
}

.section-copy {
    color: var(--muted);
    font-size: 0.78rem;
    line-height: 1.45;
    max-width: 50ch;
}

.notice {
    padding: var(--card-pad);
    border-radius: 8px;
    border: 1px solid var(--line);
    background: linear-gradient(135deg, #ffffff, #f5faff);
    box-shadow: var(--shadow);
    color: var(--muted);
}

.notice strong {
    color: var(--text);
}

.queue-shell {
    padding: var(--card-pad);
    border-radius: 8px;
    border: 1px solid var(--line);
    background: var(--surface-strong);
    box-shadow: var(--shadow);
}

.queue-row {
    padding: 14px 16px;
    border-radius: 8px;
    border: 1px solid rgba(239, 106, 106, 0.18);
    background: linear-gradient(90deg, rgba(239, 106, 106, 0.10), rgba(255,255,255,0.88));
    margin-bottom: 10px;
}

.queue-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 7px 10px;
    border-radius: 999px;
    background: rgba(239, 106, 106, 0.12);
    color: var(--coral);
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0;
}

.queue-primary {
    color: var(--text);
    font-weight: 800;
    font-size: 0.95rem;
}

.queue-secondary {
    color: var(--muted);
    font-size: 0.8rem;
}

.queue-number {
    color: var(--text);
    font-weight: 800;
    text-align: right;
}

.queue-prob {
    color: var(--coral);
    font-weight: 800;
    text-align: right;
}

.queue-time {
    color: var(--muted);
    font-size: 0.8rem;
    text-align: right;
}

.empty-state {
    padding: var(--card-pad);
    border-radius: 8px;
    border: 1px dashed var(--line);
    background: #f8fbff;
    color: var(--muted);
}

.footer-note {
    color: var(--muted);
    font-size: 0.82rem;
    margin-top: 4px;
}

@media (max-width: 1100px) {
    .hero-card {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .hero-summary {
        grid-column: span 2;
        grid-row: auto;
    }

    .metric-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

}

@media (max-width: 680px) {
    .hero-card,
    .metric-grid {
        grid-template-columns: 1fr;
    }

    .hero-summary {
        grid-column: auto;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Manrope, sans-serif", size=12, color="#6b7e91"),
    margin=dict(l=24, r=18, t=34, b=24),
    hoverlabel=dict(bgcolor="#122033", bordercolor="#122033", font=dict(color="#ffffff")),
)

CHART_CONFIG = {"displayModeBar": False, "scrollZoom": False, "responsive": True}

COLORS = {
    "normal": "#44b6a1",
    "normal_soft": "rgba(68, 182, 161, 0.30)",
    "fraud": "#df3f46",
    "fraud_soft": "rgba(223, 63, 70, 0.18)",
    "cyan": "#1d9bf0",
    "gold": "#e9b949",
    "violet": "#7b7cf6",
    "text": "#122033",
    "muted": "#6b7e91",
    "grid": "rgba(96, 116, 139, 0.09)",
}


def load_data() -> pd.DataFrame:
    if not os.path.exists(RESULTS_FILE):
        return pd.DataFrame()

    df = pd.read_csv(RESULTS_FILE)
    for column in ["fraud_probability", "amount", "prediction", "true_label"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def fmt_int(value: int) -> str:
    return f"{int(value):,}"


def fmt_money(value: float) -> str:
    return f"${value:,.2f}"


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def section_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="section-head">
            <div>
                <div class="section-title">{title}</div>
                <div class="section-copy">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_axes(fig: go.Figure, x_title: str, y_title: str, height: int) -> None:
    fig.update_layout(
        **PLOT_LAYOUT,
        height=height,
        xaxis=dict(
            title=dict(text=x_title, font=dict(color=COLORS["muted"], size=12)),
            gridcolor=COLORS["grid"],
            tickfont=dict(color=COLORS["muted"], size=11),
            zeroline=False,
            showline=False,
            color=COLORS["muted"],
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(color=COLORS["muted"], size=12)),
            gridcolor=COLORS["grid"],
            tickfont=dict(color=COLORS["muted"], size=11),
            zeroline=False,
            showline=False,
            color=COLORS["muted"],
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=COLORS["muted"]),
        ),
    )


df = load_data()

if df.empty:
    st.markdown(
        """
        <div class="notice">
            <strong>Waiting for live transaction data.</strong><br>
            Start <code>consumer.py</code> and <code>producer.py</code>, then the dashboard will populate automatically.
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(REFRESH)
    st.rerun()

total = len(df)
fraud_n = int(df["prediction"].fillna(0).sum())
normal_n = max(total - fraud_n, 0)
fraud_pct = fraud_n / total * 100 if total else 0.0
avg_fraud_amount = df.loc[df["prediction"] == 1, "amount"].mean()
avg_fraud_amount = 0.0 if pd.isna(avg_fraud_amount) else float(avg_fraud_amount)
peak_probability = float(df["fraud_probability"].fillna(0).max()) if total else 0.0

tail = df.tail(WINDOW).copy()
tail["idx"] = range(len(tail))
tail_fraud = int(tail["prediction"].fillna(0).sum()) if not tail.empty else 0
tail_rate = tail_fraud / len(tail) * 100 if len(tail) else 0.0
tail_mean_probability = float(tail["fraud_probability"].fillna(0).mean()) if not tail.empty else 0.0
high_conf_count = int((tail["fraud_probability"].fillna(0) >= 0.85).sum()) if not tail.empty else 0
largest_transaction = float(df["amount"].fillna(0).max()) if "amount" in df else 0.0
average_amount = float(df["amount"].fillna(0).mean()) if "amount" in df else 0.0

rolling_window = max(20, min(120, len(tail) // 18)) if len(tail) else 20
tail["rolling_rate"] = tail["prediction"].fillna(0).rolling(rolling_window, min_periods=1).mean() * 100

precision = recall = f1_score = accuracy = None
confusion = None
if "true_label" in df.columns and df["true_label"].notna().any():
    valid = df[df["true_label"].notna()].copy()
    valid["true_label"] = pd.to_numeric(valid["true_label"], errors="coerce")
    valid = valid[valid["true_label"].isin([0, 1])]
    if not valid.empty:
        tp = int(((valid["prediction"] == 1) & (valid["true_label"] == 1)).sum())
        fp = int(((valid["prediction"] == 1) & (valid["true_label"] == 0)).sum())
        fn = int(((valid["prediction"] == 0) & (valid["true_label"] == 1)).sum())
        tn = int(((valid["prediction"] == 0) & (valid["true_label"] == 0)).sum())
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0.0
        confusion = [[tn, fp], [fn, tp]]

page_col = st.container()

with page_col:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-summary">
                <div class="eyebrow">Realtime fraud command system</div>
                <div class="hero-title">FraudGuard Control Room</div>
                <div class="hero-copy">
                    Live Kafka scoring, risk triage, and model health in one focused operations view.
                </div>
            </div>
            <div class="mini-grid">
                <div class="mini-card">
                    <div class="mini-label">Transactions processed</div>
                    <div class="mini-value">{fmt_int(total)}</div>
                    <div class="mini-note">Total observed rows.</div>
                </div>
                <div class="mini-card">
                    <div class="mini-label">Fraud share</div>
                    <div class="mini-value">{fmt_pct(fraud_pct)}</div>
                    <div class="mini-note">Current stream incidence.</div>
                </div>
                <div class="mini-card">
                    <div class="mini-label">High-confidence alerts</div>
                    <div class="mini-value">{fmt_int(high_conf_count)}</div>
                    <div class="mini-note">Above escalation threshold.</div>
                </div>
                <div class="mini-card">
                    <div class="mini-label">Window alerts</div>
                    <div class="mini-value">{fmt_int(tail_fraud)}</div>
                    <div class="mini-note">Latest {len(tail):,} records.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cards = [
        ("metric-coral", "Fraud detected", fmt_int(fraud_n), "Escalated events routed to review."),
        ("metric-cyan", "Window fraud rate", fmt_pct(tail_rate), "Active observation window."),
        ("metric-gold", "Average fraud amount", fmt_money(avg_fraud_amount), "Mean value of flagged activity."),
        ("metric-teal", "Legitimate flow", fmt_int(normal_n), "Non-flagged transaction volume."),
    ]
    metric_cards_html = "".join(
        f'<div class="metric-card {klass}"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>'
        for klass, label, value, note in metric_cards
    )
    st.markdown(
        f'<div class="metric-grid">{metric_cards_html}</div>',
        unsafe_allow_html=True,
    )

    stream_left, stream_right = st.columns([1.35, 0.85], gap="small")
    with stream_left:
        section_header(
            "Probability stream",
            "Latest transaction confidence with flagged outliers separated.",
        )
        scatter_fig = go.Figure()
        normal_mask = tail["prediction"] == 0
        fraud_mask = tail["prediction"] == 1
        scatter_fig.add_trace(
            go.Scattergl(
                x=tail.loc[normal_mask, "idx"],
                y=tail.loc[normal_mask, "fraud_probability"],
                mode="markers",
                name="Legitimate",
                marker=dict(size=4.5, color=COLORS["normal_soft"]),
                hovertemplate="Txn %{x}<br>Probability %{y:.2%}<extra>Legitimate</extra>",
            )
        )
        scatter_fig.add_trace(
            go.Scattergl(
                x=tail.loc[fraud_mask, "idx"],
                y=tail.loc[fraud_mask, "fraud_probability"],
                mode="markers",
                name="Fraud",
                marker=dict(size=8.5, color=COLORS["fraud"], line=dict(width=1.2, color="#ffd7da")),
                hovertemplate="Txn %{x}<br>Probability %{y:.2%}<extra>Fraud</extra>",
            )
        )
        scatter_fig.add_hline(
            y=0.80,
            line_width=1.4,
            line_dash="dot",
            line_color="rgba(233, 185, 73, 0.95)",
            annotation_text="Escalation threshold",
            annotation_position="top left",
            annotation_font_color="#a97611",
        )
        style_axes(scatter_fig, "Recent transaction order", "Fraud probability", 330)
        st.plotly_chart(scatter_fig, use_container_width=True, key="probability_stream", config=CHART_CONFIG)

    with stream_right:
        section_header(
            "Rolling fraud rate",
            "Short-horizon acceleration inside the live window.",
        )
        rolling_fig = go.Figure()
        rolling_fig.add_trace(
            go.Scatter(
                x=tail["idx"],
                y=tail["rolling_rate"],
                mode="lines",
                name="Rolling fraud rate",
                line=dict(color=COLORS["cyan"], width=3.4),
                fill="tozeroy",
                fillcolor="rgba(29, 155, 240, 0.13)",
                hovertemplate="Txn %{x}<br>Rolling rate %{y:.2f}%<extra></extra>",
            )
        )
        style_axes(rolling_fig, "Recent transaction order", "Fraud rate %", 330)
        st.plotly_chart(rolling_fig, use_container_width=True, key="rolling_fraud_rate", config=CHART_CONFIG)

    row_one_left, row_one_right = st.columns(2, gap="small")
    with row_one_left:
        section_header(
            "System balance",
            "The current split between legitimate and fraudulent classifications.",
        )
        donut_fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Legitimate", "Fraud"],
                    values=[normal_n, fraud_n],
                    hole=0.72,
                    sort=False,
                    marker=dict(
                        colors=["rgba(68, 182, 161, 0.72)", COLORS["fraud"]],
                        line=dict(color="#ffffff", width=3),
                    ),
                    textinfo="none",
                    hovertemplate="%{label}<br>%{value:,} transactions<br>%{percent}<extra></extra>",
                )
            ]
        )
        donut_fig.update_layout(
            **PLOT_LAYOUT,
            height=320,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0.5, xanchor="center"),
            annotations=[
                dict(
                    text=f"<span style='font-size:13px;color:#6b7e91'>Fraud share</span><br><span style='font-size:34px;color:#122033'><b>{fraud_pct:.2f}%</b></span>",
                    x=0.5,
                    y=0.52,
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(donut_fig, use_container_width=True, key="system_balance", config=CHART_CONFIG)

    with row_one_right:
        section_header(
            "Confidence by class",
            "A violin view of model confidence across legitimate and fraudulent predictions.",
        )
        violin_fig = go.Figure()
        class_series = [
            ("Legitimate", tail.loc[tail["prediction"] == 0, "fraud_probability"], "rgba(68, 182, 161, 0.50)", COLORS["normal"]),
            ("Fraud", tail.loc[tail["prediction"] == 1, "fraud_probability"], "rgba(223, 63, 70, 0.58)", COLORS["fraud"]),
        ]
        for name, values, fill_color, line_color in class_series:
            if len(values) > 0:
                violin_fig.add_trace(
                    go.Violin(
                        y=values,
                        x=[name] * len(values),
                        name=name,
                        box_visible=True,
                        meanline_visible=True,
                        points=False,
                        fillcolor=fill_color,
                        line=dict(color=line_color, width=2.4),
                        opacity=0.9,
                        hovertemplate=f"{name}<br>Probability %{{y:.2%}}<extra></extra>",
                    )
                )
        style_axes(violin_fig, "", "Fraud probability", 320)
        violin_fig.update_xaxes(showgrid=False)
        st.plotly_chart(violin_fig, use_container_width=True, key="confidence_violin", config=CHART_CONFIG)

    row_two_left, row_two_right = st.columns(2, gap="small")
    with row_two_left:
        section_header(
            "Model shape",
            "Performance metrics shown as a radar profile instead of another flat bar chart.",
        )
        if precision is None:
            st.markdown(
                """
                <div class="notice">
                    <strong>Ground truth not available yet.</strong><br>
                    Precision, recall, F1, and accuracy will appear here once labeled rows arrive in the results file.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            categories = ["Precision", "Recall", "F1", "Accuracy"]
            values = [precision, recall, f1_score, accuracy]
            radar_fig = go.Figure()
            radar_fig.add_trace(
                go.Scatterpolar(
                    r=values + [values[0]],
                    theta=categories + [categories[0]],
                    fill="toself",
                    fillcolor="rgba(29, 155, 240, 0.14)",
                    line=dict(color=COLORS["cyan"], width=3.2),
                    name="Model profile",
                    hovertemplate="%{theta}: %{r:.3f}<extra></extra>",
                )
            )
            radar_fig.update_layout(
                **PLOT_LAYOUT,
                height=320,
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(
                        range=[0, 1],
                        gridcolor=COLORS["grid"],
                        tickcolor=COLORS["grid"],
                        color=COLORS["muted"],
                        tickfont=dict(size=11, color=COLORS["muted"]),
                    ),
                    angularaxis=dict(color=COLORS["muted"], tickfont=dict(size=11, color=COLORS["muted"])),
                ),
                showlegend=False,
            )
            st.plotly_chart(radar_fig, use_container_width=True, key="model_radar", config=CHART_CONFIG)

    with row_two_right:
        section_header(
            "Amount spread by class",
            "Transaction amounts compared between legitimate flow and flagged fraud using box distributions.",
        )
        box_fig = go.Figure()
        legit_amounts = df.loc[df["prediction"] == 0, "amount"].dropna()
        fraud_amounts = df.loc[df["prediction"] == 1, "amount"].dropna()
        if len(legit_amounts) > 0:
            box_fig.add_trace(
                go.Box(
                    y=legit_amounts,
                    name="Legitimate",
                    marker_color="rgba(68, 182, 161, 0.46)",
                    line=dict(color=COLORS["normal"], width=2.4),
                    boxmean=True,
                    hovertemplate="Legitimate<br>Amount %{y:$,.2f}<extra></extra>",
                )
            )
        if len(fraud_amounts) > 0:
            box_fig.add_trace(
                go.Box(
                    y=fraud_amounts,
                    name="Fraud",
                    marker_color=COLORS["fraud_soft"],
                    line=dict(color=COLORS["fraud"], width=2.4),
                    boxmean=True,
                    hovertemplate="Fraud<br>Amount %{y:$,.2f}<extra></extra>",
                )
            )
        style_axes(box_fig, "", "Transaction amount", 320)
        box_fig.update_xaxes(showgrid=False)
        st.plotly_chart(box_fig, use_container_width=True, key="amount_boxplot", config=CHART_CONFIG)

    row_three_left, row_three_right = st.columns(2, gap="small")
    with row_three_left:
        section_header(
            "Confusion surface",
            "True versus predicted outcomes when labels are present.",
        )
        if confusion is None:
            st.markdown(
                """
                <div class="empty-state">
                    Confusion matrix is waiting for labeled rows. Once true labels are present, this panel switches to a live matrix.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            heatmap_fig = go.Figure(
                data=go.Heatmap(
                    z=confusion,
                    x=["Predicted Legit", "Predicted Fraud"],
                    y=["Actual Legit", "Actual Fraud"],
                    colorscale=[[0.0, "#f3f8fc"], [0.45, "#9fcfe7"], [1.0, COLORS["cyan"]]],
                    text=confusion,
                    texttemplate="%{text}",
                    hovertemplate="%{y}<br>%{x}<br>Count %{z}<extra></extra>",
                )
            )
            heatmap_fig.update_layout(
                **PLOT_LAYOUT,
                height=300,
                xaxis=dict(showgrid=False, color=COLORS["muted"]),
                yaxis=dict(showgrid=False, autorange="reversed", color=COLORS["muted"]),
            )
            st.plotly_chart(heatmap_fig, use_container_width=True, key="confusion_heatmap", config=CHART_CONFIG)

    with row_three_right:
        section_header(
            "Cumulative risk",
            "Fraud detections accumulated across the full observed history.",
        )
        cumulative_fig = go.Figure()
        cumulative_fig.add_trace(
            go.Scatter(
                x=list(range(total)),
                y=df["prediction"].fillna(0).cumsum(),
                mode="lines",
                fill="tozeroy",
                line=dict(color=COLORS["fraud"], width=3.4),
                fillcolor=COLORS["fraud_soft"],
                hovertemplate="Txn %{x}<br>Cumulative fraud %{y}<extra></extra>",
            )
        )
        style_axes(cumulative_fig, "Transaction order", "Cumulative fraud count", 300)
        st.plotly_chart(cumulative_fig, use_container_width=True, key="cumulative_trajectory", config=CHART_CONFIG)

    section_header(
        "Analyst queue",
        "The newest escalations, ordered from most recent to oldest, ready for intervention.",
    )
    alerts = df[df["prediction"] == 1].tail(10).sort_index(ascending=False)
    if alerts.empty:
        st.markdown(
            """
            <div class="notice">
                <strong>No suspicious transactions are waiting right now.</strong><br>
                The system is still monitoring the stream and will surface new alerts here automatically.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        queue_df = alerts.copy()
        queue_df["status"] = "FLAGGED"
        queue_df["transaction"] = queue_df.get("transaction_id", "N/A").map(lambda x: f"Transaction #{x}")
        queue_df["amount_display"] = queue_df.get("amount", 0).fillna(0).map(lambda x: f"${float(x):,.2f}")
        queue_df["probability_display"] = queue_df.get("fraud_probability", 0).fillna(0).map(lambda x: f"{float(x) * 100:.1f}%")
        queue_df["timestamp_display"] = queue_df.get("timestamp", "Unknown").fillna("Unknown")

        queue_view = queue_df[["status", "transaction", "amount_display", "probability_display", "timestamp_display"]].rename(
            columns={
                "status": "Status",
                "transaction": "Transaction",
                "amount_display": "Amount",
                "probability_display": "Probability",
                "timestamp_display": "Timestamp",
            }
        )
        st.dataframe(
            queue_view,
            use_container_width=True,
            hide_index=True,
            row_height=40,
            column_config={
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Transaction": st.column_config.TextColumn("Transaction", width="medium"),
                "Amount": st.column_config.TextColumn("Amount", width="small"),
                "Probability": st.column_config.TextColumn("Probability", width="small"),
                "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
            },
        )

    with st.expander("Open full transaction ledger"):
        st.dataframe(
            df.tail(200).sort_index(ascending=False),
            use_container_width=True,
            hide_index=True,
            row_height=34,
        )

    st.markdown(
        """
        <div class="footer-note">
            FraudGuard refreshes automatically so the interface stays synchronized with the live stream.
        </div>
        """,
        unsafe_allow_html=True,
    )

time.sleep(REFRESH)
st.rerun()
