from __future__ import annotations

import argparse
import json
import random
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


PLANS = ["free", "pro", "team", "enterprise"]
CHANNELS = ["organic", "paid_search", "linkedin_ads", "referral", "direct"]
COUNTRIES = ["US", "SE", "DE", "GB", "IN", "CA"]
EXPERIMENT_ID = "onboarding_copy_test"


@dataclass
class SimulationConfig:
    n_users: int = 8000
    seed: int = 42
    start_days_ago: int = 120


def _weighted_choice(values: list[str], weights: list[float]) -> str:
    return random.choices(values, weights=weights, k=1)[0]


def _event_row(
    *,
    user_id: str,
    event_name: str,
    event_ts: datetime,
    session_id: str,
    experiment_id: str | None,
    variant: str | None,
    revenue: float | None,
    properties: dict,
) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "event_name": event_name,
        "event_ts": event_ts.isoformat(),
        "session_id": session_id,
        "experiment_id": experiment_id,
        "variant": variant,
        "revenue": revenue,
        "properties": json.dumps(properties),
    }


def generate_saas_dataset(n_users: int = 8000, seed: int = 42, output_dir: str | Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    random.seed(seed)
    np.random.seed(seed)

    cfg = SimulationConfig(n_users=n_users, seed=seed)
    base_date = datetime.now(UTC) - timedelta(days=cfg.start_days_ago)

    users: list[dict] = []
    events: list[dict] = []
    assignments: list[dict] = []

    for _ in range(cfg.n_users):
        user_id = str(uuid.uuid4())
        signup_ts = base_date + timedelta(days=random.randint(0, cfg.start_days_ago), hours=random.randint(0, 23))

        plan = _weighted_choice(PLANS, [0.55, 0.26, 0.14, 0.05])
        channel = _weighted_choice(CHANNELS, [0.24, 0.22, 0.12, 0.20, 0.22])
        country = _weighted_choice(COUNTRIES, [0.31, 0.09, 0.11, 0.14, 0.25, 0.10])
        variant = _weighted_choice(["control", "treatment"], [0.5, 0.5])

        users.append(
            {
                "user_id": user_id,
                "signup_ts": signup_ts.isoformat(),
                "plan": plan,
                "channel": channel,
                "country": country,
            }
        )

        assignments.append(
            {
                "experiment_id": EXPERIMENT_ID,
                "user_id": user_id,
                "variant": variant,
                "assigned_ts": signup_ts.isoformat(),
            }
        )

        session_id = str(uuid.uuid4())
        events.append(
            _event_row(
                user_id=user_id,
                event_name="signup",
                event_ts=signup_ts,
                session_id=session_id,
                experiment_id=EXPERIMENT_ID,
                variant=variant,
                revenue=0.0,
                properties={"plan": plan, "channel": channel},
            )
        )

        p_onboarding_start = 0.82
        p_onboarding_complete = 0.58 if variant == "control" else 0.66
        p_first_project = 0.44 if variant == "control" else 0.53
        p_invite = 0.26 if variant == "control" else 0.31

        current_ts = signup_ts + timedelta(minutes=random.randint(5, 120))

        if random.random() < p_onboarding_start:
            session_id = str(uuid.uuid4())
            events.append(
                _event_row(
                    user_id=user_id,
                    event_name="onboarding_started",
                    event_ts=current_ts,
                    session_id=session_id,
                    experiment_id=EXPERIMENT_ID,
                    variant=variant,
                    revenue=0.0,
                    properties={"step": 1},
                )
            )

            if random.random() < p_onboarding_complete:
                current_ts += timedelta(minutes=random.randint(10, 180))
                events.append(
                    _event_row(
                        user_id=user_id,
                        event_name="onboarding_completed",
                        event_ts=current_ts,
                        session_id=session_id,
                        experiment_id=EXPERIMENT_ID,
                        variant=variant,
                        revenue=0.0,
                        properties={"step": 2},
                    )
                )

                if random.random() < p_first_project:
                    current_ts += timedelta(minutes=random.randint(5, 240))
                    events.append(
                        _event_row(
                            user_id=user_id,
                            event_name="first_project_created",
                            event_ts=current_ts,
                            session_id=session_id,
                            experiment_id=EXPERIMENT_ID,
                            variant=variant,
                            revenue=0.0,
                            properties={"project_template": _weighted_choice(["blank", "marketing", "sales"], [0.5, 0.3, 0.2])},
                        )
                    )

                    if random.random() < p_invite:
                        current_ts += timedelta(minutes=random.randint(5, 120))
                        events.append(
                            _event_row(
                                user_id=user_id,
                                event_name="teammate_invited",
                                event_ts=current_ts,
                                session_id=session_id,
                                experiment_id=EXPERIMENT_ID,
                                variant=variant,
                                revenue=0.0,
                                properties={"invite_count": random.randint(1, 3)},
                            )
                        )

        session_count = int(np.random.poisson(lam=6 if plan in {"team", "enterprise"} else 4)) + 1
        retained_days = random.randint(2, 90)
        last_active = signup_ts

        for _session in range(session_count):
            session_day = signup_ts + timedelta(days=random.randint(0, retained_days))
            session_id = str(uuid.uuid4())
            last_active = max(last_active, session_day)

            events.append(
                _event_row(
                    user_id=user_id,
                    event_name="session_started",
                    event_ts=session_day,
                    session_id=session_id,
                    experiment_id=EXPERIMENT_ID,
                    variant=variant,
                    revenue=0.0,
                    properties={"device": _weighted_choice(["web", "mobile"], [0.74, 0.26])},
                )
            )

            feature_events = random.randint(1, 4)
            for _ in range(feature_events):
                feature = _weighted_choice(
                    ["feature_analytics_viewed", "feature_collab_used", "feature_export_used"],
                    [0.45, 0.35, 0.20],
                )
                event_ts = session_day + timedelta(minutes=random.randint(1, 90))
                events.append(
                    _event_row(
                        user_id=user_id,
                        event_name=feature,
                        event_ts=event_ts,
                        session_id=session_id,
                        experiment_id=EXPERIMENT_ID,
                        variant=variant,
                        revenue=0.0,
                        properties={"feature": feature.replace("feature_", "")},
                    )
                )

            if plan != "free" and random.random() < 0.18:
                payment_amount = float(np.random.lognormal(mean=3.1, sigma=0.6))
                payment_ts = session_day + timedelta(minutes=random.randint(1, 100))
                events.append(
                    _event_row(
                        user_id=user_id,
                        event_name="subscription_payment",
                        event_ts=payment_ts,
                        session_id=session_id,
                        experiment_id=EXPERIMENT_ID,
                        variant=variant,
                        revenue=round(payment_amount, 2),
                        properties={"plan": plan},
                    )
                )

        if (datetime.now(UTC) - last_active).days > random.randint(14, 45):
            churn_ts = last_active + timedelta(days=random.randint(7, 35))
            events.append(
                _event_row(
                    user_id=user_id,
                    event_name="churned",
                    event_ts=churn_ts,
                    session_id=str(uuid.uuid4()),
                    experiment_id=EXPERIMENT_ID,
                    variant=variant,
                    revenue=0.0,
                    properties={"reason": _weighted_choice(["no_value", "price", "competitor", "unknown"], [0.35, 0.26, 0.18, 0.21])},
                )
            )

    users_df = pd.DataFrame(users)
    events_df = pd.DataFrame(events).sort_values("event_ts").reset_index(drop=True)
    assignments_df = pd.DataFrame(assignments)

    destination = Path(output_dir) if output_dir else Path(__file__).resolve().parents[1] / "data" / "raw"
    destination.mkdir(parents=True, exist_ok=True)

    users_df.to_csv(destination / "dim_users.csv", index=False)
    events_df.to_csv(destination / "raw_events.csv", index=False)
    assignments_df.to_csv(destination / "ab_test_assignments.csv", index=False)

    print(
        f"Generated dataset -> users: {len(users_df)}, events: {len(events_df)}, assignments: {len(assignments_df)}"
    )
    return users_df, events_df, assignments_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic SaaS product event dataset")
    parser.add_argument("--users", type=int, default=8000, help="Number of synthetic users")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for CSV files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_saas_dataset(n_users=args.users, seed=args.seed, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
