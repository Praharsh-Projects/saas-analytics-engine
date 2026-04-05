with signups as (
    select
        user_id,
        date_trunc('week', signup_ts)::date as cohort_week
    from {{ ref('stg_dim_users') }}
),

activity as (
    select
        user_id,
        date_trunc('week', event_ts)::date as active_week
    from {{ ref('stg_raw_events') }}
    where event_name = 'session_started'
),

cohort_activity as (
    select
        s.cohort_week,
        date_part('week', age(a.active_week, s.cohort_week))::int as period_number,
        s.user_id
    from signups s
    join activity a on s.user_id = a.user_id
    where a.active_week >= s.cohort_week
)

select
    cohort_week,
    period_number,
    count(distinct user_id) as retained_users
from cohort_activity
group by 1, 2
