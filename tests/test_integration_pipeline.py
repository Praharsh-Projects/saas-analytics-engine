from pathlib import Path

import pandas as pd

from analytics.ab_test_evaluator import ABTestEvaluator
from analytics.cohort_analysis import CohortRetention
from analytics.funnel_analysis import FunnelAnalyzer
from simulate.generate_events import generate_saas_dataset


def test_pipeline_outputs_expected_rows(tmp_path: Path) -> None:
    users, events, assignments = generate_saas_dataset(n_users=400, seed=7, output_dir=tmp_path)

    assert len(users) == 400
    assert len(assignments) == 400
    assert len(events) > 2000

    funnel = FunnelAnalyzer(events).compute()
    assert int(funnel.loc[funnel["step"] == "signup", "users"].iloc[0]) == 400

    cohort_matrix = CohortRetention(events, users, period="weekly").heatmap()
    assert isinstance(cohort_matrix, pd.DataFrame)

    converted_users = set(
        events.loc[events["event_name"].isin(["onboarding_completed", "first_project_created"]), "user_id"]
    )
    ab = assignments.copy()
    ab["converted"] = ab["user_id"].isin(converted_users).astype(int)

    result = ABTestEvaluator(
        control=ab.loc[ab["variant"] == "control", "converted"].to_numpy(),
        treatment=ab.loc[ab["variant"] == "treatment", "converted"].to_numpy(),
    ).evaluate()

    assert "p_value" in result
    assert "mde" in result
