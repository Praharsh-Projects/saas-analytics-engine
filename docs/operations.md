# Operations

## Verification sequence

1. Generate a source snapshot with an explicit seed and UTC reference time.
2. Initialize the raw PostgreSQL tables.
3. Validate and transactionally replace the source snapshot.
4. Run `dbt build` to create models and execute tests.
5. Run `scripts/verify_warehouse.py` to reconcile source and mart counts.

The GitHub Actions quality workflow executes this sequence against a disposable
PostgreSQL 16 service.

## Recovery

- Source validation happens before the database transaction.
- A load failure rolls back the snapshot replacement.
- Re-run the load with the same input files to recreate the same raw state.
- Re-run `dbt build` to replace views and tables from the validated sources.
- Treat a failed dbt test or warehouse reconciliation as a blocked publication,
  not as a warning.

## Monitoring scope

The current repository exposes build/test status through GitHub Actions and
prints structured row-count reconciliation as JSON. It does not implement
production orchestration, alert routing, SLOs, lineage services, or on-call
operations.

## Security and privacy

All tracked data is generated and synthetic. Connection credentials are
environment variables. No cloud keys, production credentials, customer
identifiers, or bank data belong in this repository.
