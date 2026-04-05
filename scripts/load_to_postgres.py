from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


def load_csv_to_table(engine, csv_path: Path, table_name: str) -> int:
    data = pd.read_csv(csv_path)
    data.to_sql(table_name, engine, if_exists="append", index=False, method="multi", chunksize=5000)
    return len(data)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw_dir = root / "data" / "raw"

    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://analytics:analytics@localhost:5432/analytics")
    engine = create_engine(db_url)

    users_rows = load_csv_to_table(engine, raw_dir / "dim_users.csv", "dim_users")
    events_rows = load_csv_to_table(engine, raw_dir / "raw_events.csv", "raw_events")
    assignments_rows = load_csv_to_table(engine, raw_dir / "ab_test_assignments.csv", "ab_test_assignments")

    print(
        f"Loaded rows -> dim_users: {users_rows}, raw_events: {events_rows}, "
        f"ab_test_assignments: {assignments_rows}"
    )


if __name__ == "__main__":
    main()
