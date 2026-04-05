select
    experiment_id,
    user_id,
    variant,
    cast(assigned_ts as timestamp) as assigned_ts
from {{ source('app_raw', 'ab_test_assignments') }}
