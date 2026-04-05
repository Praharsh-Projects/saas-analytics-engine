from __future__ import annotations

import os

from sqlalchemy import create_engine, text


DDL = """
CREATE TABLE IF NOT EXISTS raw_events (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_name TEXT NOT NULL,
    event_ts TIMESTAMP NOT NULL,
    session_id TEXT,
    experiment_id TEXT,
    variant TEXT,
    revenue NUMERIC,
    properties JSONB
);

CREATE TABLE IF NOT EXISTS dim_users (
    user_id TEXT PRIMARY KEY,
    signup_ts TIMESTAMP NOT NULL,
    plan TEXT NOT NULL,
    channel TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ab_test_assignments (
    experiment_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    variant TEXT NOT NULL,
    assigned_ts TIMESTAMP NOT NULL,
    PRIMARY KEY (experiment_id, user_id)
);
"""


def main() -> None:
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://analytics:analytics@localhost:5432/analytics")
    engine = create_engine(db_url)

    with engine.begin() as connection:
        connection.execute(text(DDL))

    print("Database schema initialized")


if __name__ == "__main__":
    main()
