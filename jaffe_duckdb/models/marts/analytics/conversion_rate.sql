select
    month(order_date) as month,
    round(
        count(customer_id)*100.0/(select count(customer_id) from {{ref('stg_jaffle_shop__customers')}}) 
    ,2) as conversion_rate 
from {{ ref('fct_orders')}}
group by 1
order by 1
