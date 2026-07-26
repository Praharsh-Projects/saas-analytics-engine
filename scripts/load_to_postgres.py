from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import Connection, create_engine, text


TABLE_CONTRACTS = {
    "dim_users": {
        "required": {"user_id", "signup_ts", "plan", "channel", "country"},
        "key": ["user_id"],
    },
    "raw_events": {
        "required": {
            "event_id",
            "user_id",
            "event_name",
            "event_ts",
            "session_id",
            "experiment_id",
            "variant",
            "revenue",
            "properties",
        },
        "key": ["event_id"],
    },
    "ab_test_assignments": {
        "required": {"experiment_id", "user_id", "variant", "assigned_ts"},
        "key": ["experiment_id", "user_id"],
    },
}


def validate_frame(data: pd.DataFrame, table_name: str) -> None:
    contract = TABLE_CONTRACTS[table_name]
    missing = contract["required"] - set(data.columns)
    if missing:
        raise ValueError(f"{table_name} is missing columns: {sorted(missing)}")

    key = contract["key"]
    if data.duplicated(subset=key).any():
        raise ValueError(f"{table_name} contains duplicate key values for {key}")


def load_snapshot(connection: Connection, raw_dir: Path) -> dict[str, int]:
    frames: dict[str, pd.DataFrame] = {}
    for table_name in TABLE_CONTRACTS:
        data = pd.read_csv(raw_dir / f"{table_name}.csv")
        validate_frame(data, table_name)
        frames[table_name] = data

    connection.execute(
        text("TRUNCATE raw_events, dim_users, ab_test_assignments")
    )
    for table_name, data in frames.items():
        data.to_sql(
            table_name,
            connection,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000,
        )

    return {table_name: len(data) for table_name, data in frames.items()}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw_dir = root / "data" / "raw"

    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://analytics:analytics@localhost:5432/analytics")
    engine = create_engine(db_url)

    with engine.begin() as connection:
        loaded = load_snapshot(connection, raw_dir)

    print(
        f"Loaded snapshot -> dim_users: {loaded['dim_users']}, "
        f"raw_events: {loaded['raw_events']}, "
        f"ab_test_assignments: {loaded['ab_test_assignments']}"
    )


if __name__ == "__main__":
    main()
