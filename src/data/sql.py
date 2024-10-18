"""Contains SQL queries for routes."""

sales_average_sql = """select
    s.id,
    s.product_id,
    s.num_items,
    p.product_cost,
    u.id as user,
    s.num_items * p.product_cost as sale_value
from sales s
inner join products p on s.product_id = p.id
inner join users u on s.buyer_id = u.id
where u.id = :user_id;"""

products_sql = """select
p.id,
p.title,
p.description,
p.product_cost,
c.category_name as category
from products p
inner join categories c on p.category_id = c.id;"""

product_id_sql = """select
p.id,
p.title,
p.description,
p.product_cost,
c.category_name as category
from products p
inner join categories c on p.category_id = c.id
where p.id = :product_id;"""

users_sql = """select id, first_name, last_name from users
order by id;"""

user_sales_sql = """select
s.buyer_id as user_id,
s.id as sales_id,
s.product_id as product_id,
s.num_items as num_items,
s.transaction_ts,
p.title as product_title,
p.product_cost as product_cost,
c.category_name as category,
s.num_items * p.product_cost as sale_value
from sales s
inner join products p on s.product_id = p.id
inner join categories c on p.category_id = c.id
where s.buyer_id = :user_id and transaction_ts > :date_from
and transaction_ts < :date_to
order by transaction_ts;
"""

latest_sales_sql = """select
s.buyer_id as user_id,
s.id as sales_id,
s.product_id as product_id,
s.num_items as num_items,
s.transaction_ts,
p.title as product_title,
p.product_cost as product_cost,
c.category_name as category,
s.num_items * p.product_cost as sale_value
from sales s
inner join products p on s.product_id = p.id
inner join categories c on p.category_id = c.id
where s.buyer_id = :user_id
order by transaction_ts desc limit 5;
"""

query_strings = {
    "categories": "SELECT * from categories;",
    "products": products_sql,
    "product": product_id_sql,
    "sales_average": sales_average_sql,
    "users": users_sql,
    "user_sales": user_sales_sql,
    "latest_sales": latest_sales_sql,
}
