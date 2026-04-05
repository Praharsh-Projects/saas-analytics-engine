with funnel as (
    select * from {{ ref('int_user_funnel_steps') }}
),

stages as (
    select user_id, 'signup' as stage, signup_ts as converted_at from funnel
    union all
    select user_id, 'onboarding_started' as stage, onboarding_started_ts from funnel
    union all
    select user_id, 'onboarding_completed' as stage, onboarding_completed_ts from funnel
    union all
    select user_id, 'first_project_created' as stage, first_project_created_ts from funnel
    union all
    select user_id, 'teammate_invited' as stage, teammate_invited_ts from funnel
)

select
    user_id,
    stage,
    converted_at,
    case when converted_at is null then true else false end as dropped
from stages
