# Product Analytics Data Product

A versioned analytics pipeline for synthetic product events. Python generates
and validates a source snapshot, PostgreSQL stores the raw contract, and dbt
builds tested staging, intermediate, and mart models for activation, retention,
feature engagement, and experiment analysis.

The repository models a domain-owned data product: inputs, grains, owners,
quality rules, downstream consumers, and operational verification are explicit.
It is not a production data mesh or a connection to customer systems.

## System behavior

- Generates a reproducible source snapshot when the same seed and UTC reference
  time are supplied.
- Validates required columns and source keys before loading any rows.
- Replaces the three raw source tables in one database transaction so a failed
  load does not expose a partial snapshot.
- Builds nine dbt staging, intermediate, and mart models.
- Applies schema tests, relationship tests, accepted-value checks, and custom
  grain and non-empty-mart tests.
- Publishes documented dbt exposures for the dashboard and daily report.
- Verifies row-count contracts after every warehouse build.
- Produces activation-funnel, cohort-retention, feature-engagement, and A/B test
  outputs from synthetic data.

## Architecture

```text
Deterministic synthetic events
            |
            v
Python contract validation and transactional snapshot load
            |
            v
PostgreSQL raw source tables
            |
            v
dbt staging -> intermediate models -> consumer-facing marts
            |                               |
            |                               +-> Daily metrics report
            +----------------------------------> Product metrics dashboard
```

See [data contract](docs/data-contract.md),
[architecture](docs/architecture.md), and
[operations](docs/operations.md).

## Data models

| Layer | Models | Contract |
| --- | --- | --- |
| Source | `raw_events`, `dim_users`, `ab_test_assignments` | Validated columns and unique source keys |
| Staging | `stg_raw_events`, `stg_dim_users`, `stg_ab_test_assignments` | Typed timestamps, accepted values, user relationships |
| Intermediate | `int_user_activity`, `int_user_funnel_steps` | User activity and ordered activation state |
| Marts | `fct_funnel`, `fct_cohort_retention`, `fct_ab_tests`, `fct_feature_engagement` | Documented consumer grains and dbt tests |

## Run the Python checks

Requirements: Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
python scripts/run_daily_pipeline.py
```

The report and charts are written under `reports/`.

## Run the warehouse path

Start a disposable PostgreSQL 16 instance. The supplied Compose file is one
option:

```bash
docker compose up -d postgres
```

Then generate, load, build, test, and reconcile a fixed source snapshot:

```bash
python simulate/generate_events.py \
  --users 1200 \
  --seed 42 \
  --as-of 2026-07-26T00:00:00Z
python scripts/init_db.py
python scripts/load_to_postgres.py
dbt build \
  --project-dir dbt_project \
  --profiles-dir dbt_project \
  --vars '{"as_of_timestamp": "2026-07-26 00:00:00+00"}' \
  --no-partial-parse \
  --warn-error
python scripts/verify_warehouse.py
```

Connection settings can be overridden through `DATABASE_URL` and the
`DBT_HOST`, `DBT_PORT`, `DBT_USER`, `DBT_PASSWORD`, `DBT_DBNAME`, and
`DBT_SCHEMA` environment variables.

## Automated verification

`Data Product Quality Gates` runs on every push and pull request:

- Python unit and integration tests.
- Bytecode compilation and daily report generation.
- PostgreSQL 16 source initialization and deterministic load.
- `dbt build`, including all models and data tests.
- Post-build warehouse contract reconciliation.

The scheduled workflow runs the Python tests and report generation, then
uploads the report as a seven-day Actions artifact. It never commits generated
files or writes directly to the default branch.

## Technology

- Python 3.12, pandas, NumPy, SciPy, statsmodels, SQLAlchemy, and pytest.
- PostgreSQL 16.
- dbt Core and dbt-postgres.
- Plotly Dash, Matplotlib, and Seaborn.
- GitHub Actions and Docker Compose.

## Evidence boundaries

- All users, events, assignments, plans, countries, and revenue values are
  synthetic.
- PostgreSQL is the implemented and tested warehouse. BigQuery is not
  configured, executed, or claimed.
- The repository demonstrates data-product contracts and ownership metadata,
  not a deployed decentralized data mesh.
- There is no production traffic, customer data, regulated deployment, service
  level objective, business-impact metric, or scale benchmark.
