import pandas as pd

from analytics.cohort_analysis import CohortRetention
from analytics.funnel_analysis import FunnelAnalyzer


def _events_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"user_id": "u1", "event_name": "signup", "event_ts": "2026-01-01T00:00:00Z"},
            {"user_id": "u1", "event_name": "onboarding_started", "event_ts": "2026-01-01T01:00:00Z"},
            {"user_id": "u1", "event_name": "onboarding_completed", "event_ts": "2026-01-01T02:00:00Z"},
            {"user_id": "u1", "event_name": "session_started", "event_ts": "2026-01-08T00:00:00Z"},
            {"user_id": "u2", "event_name": "signup", "event_ts": "2026-01-03T00:00:00Z"},
            {"user_id": "u2", "event_name": "onboarding_started", "event_ts": "2026-01-03T01:00:00Z"},
            {"user_id": "u2", "event_name": "session_started", "event_ts": "2026-01-15T00:00:00Z"},
        ]
    )


def _users_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"user_id": "u1", "signup_ts": "2026-01-01T00:00:00Z"},
            {"user_id": "u2", "signup_ts": "2026-01-03T00:00:00Z"},
        ]
    )


def test_funnel_compute_shape() -> None:
    funnel = FunnelAnalyzer(_events_df()).compute()
    assert len(funnel) == 5
    assert set(["step", "users", "conversion_from_previous", "dropoff_from_previous"]).issubset(set(funnel.columns))


def test_cohort_heatmap_not_empty() -> None:
    matrix = CohortRetention(_events_df(), _users_df(), period="weekly").heatmap()
    assert not matrix.empty
