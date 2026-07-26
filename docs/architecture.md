# Architecture

## Boundaries

The repository separates four concerns:

1. `simulate/` owns deterministic synthetic source generation.
2. `scripts/` validates and loads one complete source snapshot.
3. `dbt_project/` owns transformations, tests, metadata, and consumer exposures.
4. `analytics/` and `dashboards/` consume data for reports and local review.

The PostgreSQL load is a snapshot boundary. The loader validates every input
frame before starting a transaction, truncates all three raw source tables, and
loads the replacement snapshot within that transaction. A validation or insert
failure rolls the transaction back.

## Model layers

- Staging models standardize source types and validate identifiers,
  relationships, and enumerated values.
- Intermediate models calculate user activity and activation timestamps.
- Marts expose stable grains for funnel, retention, experiment, and feature
  analysis.
- dbt exposures identify the local dashboard and scheduled report as consumers.

## Determinism

The generator accepts a random seed and an `as_of` timestamp. Both timestamp
selection and UUID generation derive from those inputs, allowing tests and CI
to reproduce the same source snapshot. The daily workflow may use the current
time, but the warehouse quality gate always uses a fixed reference timestamp.
