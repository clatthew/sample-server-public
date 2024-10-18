"""Data for test cases."""

categories_result = [{"id": 1, "name": "Baby"}, {"id": 2, "name": "Movies"}]


products_results = [
    {
        "product_id": 5,
        "title": "Car",
        "description": "Nice",
        "product_cost": 101.00,
        "category": "Movies",
    },
    {
        "product_id": 7,
        "title": "Sausages",
        "description": "Tasty",
        "product_cost": 978.00,
        "category": "Baby",
    },
]

products_expected = [
    {
        "product_id": 5,
        "title": "Car",
        "description": "Nice",
        "product_cost": 101.00,
        "category": "Movies",
    },
    {
        "product_id": 7,
        "title": "Sausages",
        "description": "Tasty",
        "product_cost": 978.00,
        "category": "Baby",
    },
]

users_results = [
    {"user_id": 5, "first_name": "Afton", "last_name": "Hauck"},
    {"user_id": 3, "first_name": "Marcelino", "last_name": "Bergnaum"},
    {"user_id": 7, "first_name": "John", "last_name": "Smith"},
]


sample_data = [["a", "b", "c"], ["d", "e", "f"]]


sample_headers = [{"name": "col1"}, {"name": "col2"}, {"name": "col3"}]


sample_result = [
    {"col1": "a", "col2": "b", "col3": "c"},
    {"col1": "d", "col2": "e", "col3": "f"},
]


single_sale = [
    {
        "sale_id": 1,
        "product_id": 1,
        "product_cost": 101.0,
        "user": "10",
        "sale_value": 202.0,
    }
]

multiple_sales = [
    {
        "sale_id": 1,
        "product_id": 10,
        "product_cost": 125.0,
        "user": "10",
        "sale_value": 125.0,
    },
    {
        "sale_id": 2,
        "product_id": 9,
        "product_cost": 65.0,
        "user": "10",
        "sale_value": 130.0,
    },
    {
        "sale_id": 3,
        "product_id": 8,
        "product_cost": 99.0,
        "user": "10",
        "sale_value": 99.0,
    },
]

user_sales_results = [
    {
        "user_id": 7,
        "sales_id": 408,
        "product_id": 5,
        "transaction_ts": "2022-10-02T23:31:41.853Z",
        "product_title": "Bespoke Frozen Salad",
        "product_cost": 488.000000000000000000000000000000,
        "category": "Clothing",
        "num_items": 2,
    },
    {
        "user_id": 7,
        "sales_id": 373,
        "product_id": 9,
        "transaction_ts": "2022-10-06T11:34:50.096Z",
        "product_title": "Bespoke Wooden Bike",
        "product_cost": 393.000000000000000000000000000000,
        "category": "Garden",
        "num_items": 1,
    },
]
