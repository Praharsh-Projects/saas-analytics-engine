from __future__ import annotations

import json
import os

from sqlalchemy import create_engine, text


COUNT_QUERIES = {
    "raw_events": "select count(*) from raw_events",
    "stg_raw_events": "select count(*) from stg_raw_events",
    "dim_users": "select count(*) from dim_users",
    "stg_dim_users": "select count(*) from stg_dim_users",
    "ab_test_assignments": "select count(*) from ab_test_assignments",
    "fct_ab_tests": "select count(*) from fct_ab_tests",
    "fct_funnel": "select count(*) from fct_funnel",
    "fct_cohort_retention": "select count(*) from fct_cohort_retention",
    "fct_feature_engagement": "select count(*) from fct_feature_engagement",
}


def main() -> None:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://analytics:analytics@localhost:5432/analytics",
    )
    engine = create_engine(database_url)

    with engine.connect() as connection:
        counts = {
            name: int(connection.execute(text(query)).scalar_one())
            for name, query in COUNT_QUERIES.items()
        }

    expected_funnel_rows = counts["dim_users"] * 5
    checks = {
        "staging_event_count_matches_source": (
            counts["stg_raw_events"] == counts["raw_events"]
        ),
        "staging_user_count_matches_source": (
            counts["stg_dim_users"] == counts["dim_users"]
        ),
        "assignment_mart_matches_source": (
            counts["fct_ab_tests"] == counts["ab_test_assignments"]
        ),
        "funnel_has_five_rows_per_user": (
            counts["fct_funnel"] == expected_funnel_rows
        ),
        "cohort_mart_is_not_empty": counts["fct_cohort_retention"] > 0,
        "engagement_mart_is_not_empty": counts["fct_feature_engagement"] > 0,
    }

    result = {"counts": counts, "checks": checks}
    print(json.dumps(result, indent=2, sort_keys=True))

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit(f"Warehouse verification failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
