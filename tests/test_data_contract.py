from datetime import UTC, datetime

import pandas as pd
import pytest

from scripts.load_to_postgres import validate_frame
from simulate.generate_events import generate_saas_dataset


AS_OF = datetime(2026, 7, 26, tzinfo=UTC)


def test_simulation_is_reproducible_for_seed_and_reference_time(tmp_path) -> None:
    first = generate_saas_dataset(
        n_users=40,
        seed=19,
        output_dir=tmp_path / "first",
        as_of=AS_OF,
    )
    second = generate_saas_dataset(
        n_users=40,
        seed=19,
        output_dir=tmp_path / "second",
        as_of=AS_OF,
    )

    for first_frame, second_frame in zip(first, second, strict=True):
        pd.testing.assert_frame_equal(first_frame, second_frame)


def test_simulation_emits_unique_contract_keys(tmp_path) -> None:
    users, events, assignments = generate_saas_dataset(
        n_users=60,
        seed=23,
        output_dir=tmp_path,
        as_of=AS_OF,
    )

    assert users["user_id"].is_unique
    assert events["event_id"].is_unique
    assert not assignments.duplicated(["experiment_id", "user_id"]).any()

    validate_frame(users, "dim_users")
    validate_frame(events, "raw_events")
    validate_frame(assignments, "ab_test_assignments")


def test_simulation_rejects_non_positive_user_count(tmp_path) -> None:
    with pytest.raises(ValueError, match="n_users must be positive"):
        generate_saas_dataset(
            n_users=0,
            output_dir=tmp_path,
            as_of=AS_OF,
        )


def test_contract_validation_rejects_duplicate_keys() -> None:
    duplicate_users = pd.DataFrame(
        [
            {
                "user_id": "user-1",
                "signup_ts": "2026-07-26T00:00:00Z",
                "plan": "free",
                "channel": "direct",
                "country": "SE",
            },
            {
                "user_id": "user-1",
                "signup_ts": "2026-07-26T00:00:00Z",
                "plan": "pro",
                "channel": "organic",
                "country": "SE",
            },
        ]
    )

    with pytest.raises(ValueError, match="duplicate key"):
        validate_frame(duplicate_users, "dim_users")
