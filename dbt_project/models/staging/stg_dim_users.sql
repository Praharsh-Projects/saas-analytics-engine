select
    user_id,
    cast(signup_ts as timestamp) as signup_ts,
    cast(signup_ts as date) as signup_date,
    plan,
    channel,
    country
from {{ source('app_raw', 'dim_users') }}
