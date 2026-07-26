select
    experiment_id,
    user_id,
    count(*) as records
from {{ ref('fct_ab_tests') }}
group by 1, 2
having count(*) > 1
