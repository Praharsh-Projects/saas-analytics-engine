with funnel_count as (
    select count(*) as cnt from {{ ref('fct_funnel') }}
),
cohort_count as (
    select count(*) as cnt from {{ ref('fct_cohort_retention') }}
),
ab_count as (
    select count(*) as cnt from {{ ref('fct_ab_tests') }}
)

select *
from funnel_count
where cnt = 0

union all

select *
from cohort_count
where cnt = 0

union all

select *
from ab_count
where cnt = 0
