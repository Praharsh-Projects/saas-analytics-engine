from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics.ab_test_evaluator import ABTestEvaluator
from analytics.cohort_analysis import CohortRetention
from analytics.funnel_analysis import FunnelAnalyzer


def _load_raw_data(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw_dir = root / "data" / "raw"
    users = pd.read_csv(raw_dir / "dim_users.csv")
    events = pd.read_csv(raw_dir / "raw_events.csv")
    assignments = pd.read_csv(raw_dir / "ab_test_assignments.csv")
    return users, events, assignments


def _save_funnel_chart(funnel_df: pd.DataFrame, path: Path) -> None:
    plt.figure(figsize=(8, 4))
    sns.barplot(data=funnel_df, x="step", y="users", color="#2d6cdf")
    plt.xticks(rotation=20)
    plt.title("Activation Funnel")
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()


def _save_cohort_heatmap(cohort_matrix: pd.DataFrame, path: Path) -> None:
    plt.figure(figsize=(9, 5))
    sns.heatmap(cohort_matrix, annot=False, cmap="Blues", vmin=0, vmax=1)
    plt.title("Cohort Retention Heatmap")
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()


def build_daily_metrics_report() -> Path:
    root = ROOT
    report_dir = root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    users, events, assignments = _load_raw_data(root)

    funnel = FunnelAnalyzer(events).compute()
    dropoff = FunnelAnalyzer(events).biggest_dropoff()

    cohort_matrix = CohortRetention(events, users, period="weekly").heatmap()

    conversion_events = events[events["event_name"].isin(["onboarding_completed", "first_project_created"])].copy()
    converted_users = set(conversion_events["user_id"].astype(str).unique())

    ab_df = assignments.copy()
    ab_df["converted"] = ab_df["user_id"].astype(str).isin(converted_users).astype(int)

    control = ab_df.loc[ab_df["variant"] == "control", "converted"].to_numpy()
    treatment = ab_df.loc[ab_df["variant"] == "treatment", "converted"].to_numpy()
    ab_result = ABTestEvaluator(control, treatment).evaluate()

    funnel_png = report_dir / "funnel.png"
    cohort_png = report_dir / "cohort_heatmap.png"
    _save_funnel_chart(funnel, funnel_png)
    if not cohort_matrix.empty:
        _save_cohort_heatmap(cohort_matrix, cohort_png)

    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Daily SaaS Metrics Report",
        "",
        f"Generated: {now}",
        "",
        "## Topline",
        f"- Users in dataset: **{users['user_id'].nunique():,}**",
        f"- Events in dataset: **{len(events):,}**",
        f"- Experiments tracked: **{ab_df['experiment_id'].nunique()}**",
        "",
        "## Activation Funnel",
        f"- Biggest drop-off step: **{dropoff['step']}** ({dropoff['dropoff']:.1%} drop-off)" if dropoff else "- Not enough data for drop-off analysis",
        "",
        funnel.to_markdown(index=False),
        "",
        "## A/B Test Evaluation",
        f"- Control conversion: **{ab_result['control_rate']:.2%}**",
        f"- Treatment conversion: **{ab_result['treatment_rate']:.2%}**",
        f"- Uplift: **{ab_result['uplift']:.2%}**",
        f"- p-value: **{ab_result['p_value']:.4f}**",
        f"- 95% CI: **[{ab_result['confidence_interval'][0]:.2%}, {ab_result['confidence_interval'][1]:.2%}]**",
        f"- MDE (80% power): **{ab_result['mde']:.2%}**",
        f"- Recommendation: **{ab_result['recommendation']}**",
        "",
        "## Cohort Retention",
        "- Weekly cohort retention matrix generated.",
        "",
        "## Artifacts",
        "- `reports/funnel.png`",
        "- `reports/cohort_heatmap.png`",
    ]

    report_path = report_dir / "daily_metrics.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


if __name__ == "__main__":
    result = build_daily_metrics_report()
    print(f"Report written to {result}")
