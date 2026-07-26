# Data Contract

## Sources

### `dim_users`

Grain: one row per `user_id`.

Required fields: `user_id`, `signup_ts`, `plan`, `channel`, `country`.

### `raw_events`

Grain: one row per `event_id`.

Required fields: `event_id`, `user_id`, `event_name`, `event_ts`,
`session_id`, `experiment_id`, `variant`, `revenue`, `properties`.

Every event user must exist in `dim_users`. Accepted event names are maintained
in `models/staging/staging_schema.yml`.

### `ab_test_assignments`

Grain: one row per `experiment_id` and `user_id`.

Required fields: `experiment_id`, `user_id`, `variant`, `assigned_ts`.

Every assigned user must exist in `dim_users`; variants are limited to
`control` and `treatment`.

## Consumer marts

- `fct_funnel`: one row per user and activation stage.
- `fct_cohort_retention`: one row per cohort week and activity period.
- `fct_ab_tests`: one row per experiment and user assignment.
- `fct_feature_engagement`: one row per user, week, and feature event.

Schema tests and singular dbt tests enforce these identifiers, relationships,
accepted values, grains, and non-empty outputs.
