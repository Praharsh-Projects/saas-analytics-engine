with base as (
    select
        user_id,
        count(case when event_name = 'session_started' then 1 end) as session_count,
        count(case when event_name like 'feature_%' then 1 end) as feature_events,
        max(event_ts) as last_event_ts,
        min(event_ts) as first_event_ts,
        sum(case when event_name = 'subscription_payment' then revenue else 0 end) as revenue_total,
        max(case when event_name = 'churned' then 1 else 0 end) as churned_flag
    from {{ ref('stg_raw_events') }}
    group by 1
)

select
    user_id,
    session_count,
    feature_events,
    first_event_ts,
    last_event_ts,
    revenue_total,
    churned_flag,
    date_part('day', now() - last_event_ts) as days_since_active
from base
