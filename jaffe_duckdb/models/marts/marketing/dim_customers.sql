with customers as (
    select * from {{ ref('stg_jaffle_shop__customers') }}
),

orders as (
    select * from {{ ref('fct_orders') }}
),

customer_orders as (
    select 
        customer_id,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        count(order_id) as number_of_orders,
        sum(amount) as lifetime_value
    from orders
    group by 1 
)

select 
    c.customer_id, 
    c.first_name,
    c.last_name,
    co.first_order_date,
    co.last_order_date,
    coalesce(co.number_of_orders, 0) as number_of_orders,
    co.lifetime_value
from customers c 
left join customer_orders co
on c.customer_id = co.customer_id