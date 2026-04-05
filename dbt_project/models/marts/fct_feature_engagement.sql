select
    user_id,
    date_trunc('week', event_ts)::date as week_start,
    event_name as feature_event,
    count(*) as usage_count
from {{ ref('stg_raw_events') }}
where event_name like 'feature_%'
group by 1,2,3
