from __future__ import annotations

import pandas as pd


class CohortRetention:
    def __init__(self, events_df: pd.DataFrame, users_df: pd.DataFrame, period: str = "weekly") -> None:
        self.events_df = events_df.copy()
        self.users_df = users_df.copy()
        self.period = period

        if "event_ts" in self.events_df.columns:
            self.events_df["event_ts"] = pd.to_datetime(self.events_df["event_ts"], utc=True, errors="coerce")
        if "signup_ts" in self.users_df.columns:
            self.users_df["signup_ts"] = pd.to_datetime(self.users_df["signup_ts"], utc=True, errors="coerce")

    def _normalize_period(self, series: pd.Series) -> pd.Series:
        normalized = series.dt.tz_localize(None) if getattr(series.dt, "tz", None) is not None else series
        if self.period == "monthly":
            return normalized.dt.to_period("M").dt.to_timestamp()
        return normalized.dt.to_period("W").dt.start_time

    def compute(self) -> pd.DataFrame:
        sessions = self.events_df[self.events_df["event_name"] == "session_started"].copy()
        if sessions.empty or self.users_df.empty:
            return pd.DataFrame(columns=["cohort_period", "period_number", "users", "retained", "retention_rate"])

        users = self.users_df[["user_id", "signup_ts"]].dropna().copy()
        users["cohort_period"] = self._normalize_period(users["signup_ts"])

        sessions = sessions[["user_id", "event_ts"]].dropna().copy()
        sessions["active_period"] = self._normalize_period(sessions["event_ts"])

        joined = sessions.merge(users, on="user_id", how="inner")
        if joined.empty:
            return pd.DataFrame(columns=["cohort_period", "period_number", "users", "retained", "retention_rate"])

        if self.period == "monthly":
            joined["period_number"] = (
                (joined["active_period"].dt.year - joined["cohort_period"].dt.year) * 12
                + joined["active_period"].dt.month
                - joined["cohort_period"].dt.month
            )
        else:
            joined["period_number"] = ((joined["active_period"] - joined["cohort_period"]).dt.days // 7).astype(int)

        joined = joined[joined["period_number"] >= 0]

        retained = (
            joined.groupby(["cohort_period", "period_number"], as_index=False)["user_id"]
            .nunique()
            .rename(columns={"user_id": "retained"})
        )
        cohort_sizes = users.groupby("cohort_period", as_index=False)["user_id"].nunique().rename(columns={"user_id": "users"})

        result = retained.merge(cohort_sizes, on="cohort_period", how="left")
        result["retention_rate"] = result["retained"] / result["users"]
        result = result.sort_values(["cohort_period", "period_number"]).reset_index(drop=True)
        return result

    def heatmap(self) -> pd.DataFrame:
        cohort = self.compute()
        if cohort.empty:
            return pd.DataFrame()

        matrix = cohort.pivot_table(
            index="cohort_period",
            columns="period_number",
            values="retention_rate",
            aggfunc="mean",
            fill_value=0.0,
        )
        matrix.index = matrix.index.astype(str)
        return matrix
