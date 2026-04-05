from __future__ import annotations

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split


FEATURES = [
    "session_count",
    "feature_events",
    "days_since_active",
    "revenue_total",
]


def build_behavior_table(events_df: pd.DataFrame) -> pd.DataFrame:
    events = events_df.copy()
    events["event_ts"] = pd.to_datetime(events["event_ts"], utc=True, errors="coerce")

    grouped = events.groupby("user_id")

    behavior = pd.DataFrame(
        {
            "session_count": grouped["event_name"].apply(lambda x: (x == "session_started").sum()),
            "feature_events": grouped["event_name"].apply(lambda x: x.str.startswith("feature_").sum()),
            "revenue_total": grouped.apply(
                lambda df: df.loc[df["event_name"] == "subscription_payment", "revenue"].fillna(0).sum(),
                include_groups=False,
            ),
            "last_event_ts": grouped["event_ts"].max(),
            "churned": grouped["event_name"].apply(lambda x: int((x == "churned").any())),
        }
    ).reset_index()

    now_ts = events["event_ts"].max()
    behavior["days_since_active"] = (now_ts - behavior["last_event_ts"]).dt.days.clip(lower=0)
    return behavior


def fit_churn_model(behavior_df: pd.DataFrame) -> dict[str, float | LogisticRegression]:
    data = behavior_df.dropna(subset=FEATURES + ["churned"]).copy()
    if data.empty or data["churned"].nunique() < 2:
        raise ValueError("Insufficient class diversity to train churn model.")

    x = data[FEATURES]
    y = data["churned"]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=200)
    model.fit(x_train, y_train)

    probabilities = model.predict_proba(x_test)[:, 1]
    auc = roc_auc_score(y_test, probabilities)

    return {
        "model": model,
        "auc": float(auc),
    }
