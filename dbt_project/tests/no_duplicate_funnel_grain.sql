select
    user_id,
    stage,
    count(*) as records
from {{ ref('fct_funnel') }}
group by 1, 2
having count(*) > 1
