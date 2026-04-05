with assignments as (
    select * from {{ ref('stg_ab_test_assignments') }}
),

conversion as (
    select
        user_id,
        max(case when event_name in ('onboarding_completed', 'first_project_created') then 1 else 0 end) as converted,
        sum(case when event_name = 'subscription_payment' then revenue else 0 end) as revenue
    from {{ ref('stg_raw_events') }}
    group by 1
)

select
    a.experiment_id,
    a.user_id,
    a.variant,
    coalesce(c.converted, 0) as converted,
    coalesce(c.revenue, 0) as revenue,
    a.assigned_ts
from assignments a
left join conversion c using (user_id)
