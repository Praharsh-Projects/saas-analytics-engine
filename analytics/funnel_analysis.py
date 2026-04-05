from __future__ import annotations

import pandas as pd


DEFAULT_FUNNEL_STEPS = [
    "signup",
    "onboarding_started",
    "onboarding_completed",
    "first_project_created",
    "teammate_invited",
]


class FunnelAnalyzer:
    def __init__(self, events_df: pd.DataFrame, funnel_steps: list[str] | None = None) -> None:
        self.events_df = events_df.copy()
        self.funnel_steps = funnel_steps or DEFAULT_FUNNEL_STEPS

    def compute(self) -> pd.DataFrame:
        if self.events_df.empty:
            return pd.DataFrame(columns=["step", "users", "conversion_from_previous", "dropoff_from_previous"])

        user_events = self.events_df[["user_id", "event_name"]].drop_duplicates()

        rows: list[dict[str, float | int | str]] = []
        previous_users = None

        for step in self.funnel_steps:
            users_count = int(user_events.loc[user_events["event_name"] == step, "user_id"].nunique())

            if previous_users is None or previous_users == 0:
                conversion = 1.0
                dropoff = 0.0
            else:
                conversion = users_count / previous_users
                dropoff = 1.0 - conversion

            rows.append(
                {
                    "step": step,
                    "users": users_count,
                    "conversion_from_previous": conversion,
                    "dropoff_from_previous": dropoff,
                }
            )
            previous_users = users_count

        return pd.DataFrame(rows)

    def biggest_dropoff(self) -> dict[str, float | str] | None:
        funnel = self.compute()
        if funnel.empty or len(funnel) < 2:
            return None

        subset = funnel.iloc[1:].copy()
        max_row = subset.sort_values("dropoff_from_previous", ascending=False).iloc[0]
        return {
            "step": str(max_row["step"]),
            "dropoff": float(max_row["dropoff_from_previous"]),
            "conversion": float(max_row["conversion_from_previous"]),
        }
