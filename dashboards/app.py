from __future__ import annotations

import sys
from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics.ab_test_evaluator import ABTestEvaluator
from analytics.cohort_analysis import CohortRetention
from analytics.funnel_analysis import FunnelAnalyzer

RAW_DIR = ROOT / "data" / "raw"
REPORT_PATH = ROOT / "reports" / "daily_metrics.md"


def _load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not (RAW_DIR / "raw_events.csv").exists():
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    events = pd.read_csv(RAW_DIR / "raw_events.csv")
    users = pd.read_csv(RAW_DIR / "dim_users.csv")
    assignments = pd.read_csv(RAW_DIR / "ab_test_assignments.csv")
    return events, users, assignments


def _funnel_page(events: pd.DataFrame) -> html.Div:
    if events.empty:
        return html.Div("No event data found. Run simulate/generate_events.py first.")

    funnel = FunnelAnalyzer(events).compute()
    chart = px.bar(funnel, x="step", y="users", title="Activation Funnel Users by Step")

    return html.Div(
        [
            dcc.Graph(figure=chart),
            html.H4("Step-by-Step Conversion"),
            html.Pre(funnel.to_string(index=False)),
        ]
    )


def _cohort_page(events: pd.DataFrame, users: pd.DataFrame) -> html.Div:
    if events.empty or users.empty:
        return html.Div("No cohort data available.")

    matrix = CohortRetention(events, users, period="weekly").heatmap()
    if matrix.empty:
        return html.Div("Cohort matrix is empty.")

    chart = px.imshow(
        matrix,
        text_auto=".0%",
        color_continuous_scale="Blues",
        aspect="auto",
        title="Weekly Cohort Retention Heatmap",
    )

    return html.Div([dcc.Graph(figure=chart)])


def _ab_test_page(events: pd.DataFrame, assignments: pd.DataFrame) -> html.Div:
    if events.empty or assignments.empty:
        return html.Div("No A/B assignment data available.")

    converted = set(events.loc[events["event_name"].isin(["onboarding_completed", "first_project_created"]), "user_id"])
    ab_df = assignments.copy()
    ab_df["converted"] = ab_df["user_id"].isin(converted).astype(int)

    control = ab_df.loc[ab_df["variant"] == "control", "converted"].to_numpy()
    treatment = ab_df.loc[ab_df["variant"] == "treatment", "converted"].to_numpy()
    result = ABTestEvaluator(control, treatment).evaluate()

    comparison = pd.DataFrame(
        {
            "variant": ["control", "treatment"],
            "conversion_rate": [result["control_rate"], result["treatment_rate"]],
        }
    )
    chart = px.bar(comparison, x="variant", y="conversion_rate", title="A/B Conversion Comparison")

    return html.Div(
        [
            dcc.Graph(figure=chart),
            html.Ul(
                [
                    html.Li(f"Uplift: {result['uplift']:.2%}"),
                    html.Li(f"p-value: {result['p_value']:.4f}"),
                    html.Li(
                        f"95% CI: [{result['confidence_interval'][0]:.2%}, {result['confidence_interval'][1]:.2%}]"
                    ),
                    html.Li(f"MDE (80% power): {result['mde']:.2%}"),
                    html.Li(f"Recommendation: {result['recommendation']}"),
                ]
            ),
        ]
    )


def _daily_metrics_page() -> html.Div:
    if not REPORT_PATH.exists():
        return html.Div("No daily report found. Run analytics/generate_daily_report.py.")
    return html.Div(dcc.Markdown(REPORT_PATH.read_text(encoding="utf-8")))


app: Dash = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "SaaS Analytics Engine"

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.H1("SaaS Product Analytics Engine"),
        html.Div(
            [
                dcc.Link("Funnel", href="/funnel", style={"marginRight": "1rem"}),
                dcc.Link("Cohorts", href="/cohorts", style={"marginRight": "1rem"}),
                dcc.Link("A/B Test", href="/ab-test", style={"marginRight": "1rem"}),
                dcc.Link("Daily Metrics", href="/daily-metrics"),
            ],
            style={"marginBottom": "1.5rem"},
        ),
        html.Div(id="page-content"),
    ],
    style={"padding": "1rem 2rem", "fontFamily": "Arial, sans-serif"},
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname: str):
    events, users, assignments = _load_data()

    if pathname in ("/", "/funnel"):
        return _funnel_page(events)
    if pathname == "/cohorts":
        return _cohort_page(events, users)
    if pathname == "/ab-test":
        return _ab_test_page(events, assignments)
    if pathname == "/daily-metrics":
        return _daily_metrics_page()

    return html.Div("Page not found")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
