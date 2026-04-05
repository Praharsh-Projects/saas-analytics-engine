with funnel_events as (
    select
        user_id,
        min(case when event_name = 'signup' then event_ts end) as signup_ts,
        min(case when event_name = 'onboarding_started' then event_ts end) as onboarding_started_ts,
        min(case when event_name = 'onboarding_completed' then event_ts end) as onboarding_completed_ts,
        min(case when event_name = 'first_project_created' then event_ts end) as first_project_created_ts,
        min(case when event_name = 'teammate_invited' then event_ts end) as teammate_invited_ts
    from {{ ref('stg_raw_events') }}
    group by 1
)

select *
from funnel_events
