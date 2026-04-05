select
    event_id,
    count(*) as records
from {{ ref('stg_raw_events') }}
group by 1
having count(*) > 1
