select
    event_id,
    user_id,
    event_name,
    cast(event_ts as timestamp) as event_ts,
    cast(event_ts as date) as event_date,
    session_id,
    experiment_id,
    variant,
    cast(coalesce(revenue, 0) as numeric) as revenue,
    properties
from {{ source('app_raw', 'raw_events') }}
