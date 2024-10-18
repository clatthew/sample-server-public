"""Defines the entrypoint and functionality for the API routes.

The API server is started by running this file directly
from Python.

Run:
    make start-server
from the root directory.

Then navigate to localhost:8000/docs to see the OpenAPI documentation,
or navigate to localhost:8000/api/<route> to see an API request result.
"""

from src.data.sql import query_strings
from fastapi import FastAPI, HTTPException
from pg8000.native import Error
from src.api.helpers import (
    process_query,
    logger,
    DBConnectionException,
    ItemNotFoundException,
    check_user,
)


PORT = 8000

app = FastAPI()


@app.get("/api/categories")
def get_categories() -> list[dict]:
    """Gets list of all product categories.

    If no categories, returns empty list.

    Returns:
       Result of query.

        Example:
        [
            {
                "category_id": 1,
                "category_name": "Baby"
            },
            {
                "category_id": 2,
                "category_name": "Movies"
            }
        ]
    """
    query = query_strings["categories"]
    try:
        result = process_query(query)
        if len(result) == 0:
            raise ItemNotFoundException("categories")
        return result
    except (DBConnectionException, Error) as d:
        raise HTTPException(status_code=500, detail=str(d))
    except ItemNotFoundException as i:
        logger.info(f"No categories: {i}")
        raise HTTPException(status_code=404, detail=str(i))
    except HTTPException as e:
        logger.info(f"Connection exception in /categories endpoint: {e.detail}")
        raise HTTPException(status_code=500, detail=str(e.detail))
    except Exception as e:
        logger.info(f"Unexpected exception in /categories endpoint: {e}")
        raise e


@app.get("/api/products")
def get_products() -> list[dict]:
    """Gets list of all products with named category.

    If no products, returns empty list.

    Returns:
        Result of query.

        Example:
        [
            {
                "product_id": 5,
                "title": "Car",
                "description": "Nice",
                "product_cost": 101.00,
                "category": "Movies"
            }
        ]
    """
    query = query_strings["products"]
    try:
        result = process_query(query)
        if len(result) == 0:
            raise ItemNotFoundException("products")
        return result
    except DBConnectionException as d:
        raise HTTPException(status_code=500, detail=str(d))
    except ItemNotFoundException as i:
        logger.info(f"No products: {i}")
        raise HTTPException(status_code=404, detail=str(i))
    except Exception as e:
        logger.info(f"Unexpected exception in /products endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/average_spend")
def get_user_average_spend(user_id: int) -> dict:
    """Gets average purchase value for a given user.

    Aggregates all sales to a given user and averages cost. If
    no sales for user, return zero. If user does not exist, return
    error message

    Args:
        user_id: the id of the user.

    Returns:
        Result of query.
        Examples:
        {"user_id": 10, "average_spend": 101.00}
        {"user_id": 975, "query_error": "User does not exist"}
    """
    present = check_user(user_id)
    if len(present) == 1:
        try:
            query = query_strings["sales_average"]
            sales = process_query(query, user_id=user_id)
            if len(sales) == 0:
                raise ItemNotFoundException("user", user_id)
            spends = [s["sale_value"] for s in sales if s["sale_value"]]
            total = 0
            count = 0
            for spend in spends:
                total += spend
                count += 1
            return {"user_id": user_id, "average_spend": round(total / count, 2)}
        except DBConnectionException as d:
            raise HTTPException(status_code=500, detail=str(d))
        except ItemNotFoundException as i:
            logger.info(f"No sales for user: {i}")
            raise HTTPException(status_code=404, detail=str(i))
        except Exception as e:
            logger.info(f"Unexpected exception in /users/average_spend endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products/{product_id}")
def get_product(product_id: int) -> dict:
    """Gets details of specific product

    Returns details of specific product. If no such product,
    returns error response.

    Args:
        product_id: the identifier for the product.
    Returns:
        Result of query.

        Example:
        {
            "product_id": 5,
            "title": "Car",
            "description": "Nice",
            "product_cost": 101.00,
            "category": "Movies"
        }
    """
    query = query_strings["product"]
    try:
        res = process_query(query, product_id=product_id)
        if len(res) == 0:
            raise ItemNotFoundException("product", product_id)
        if len(res) == 1:
            return res[0]
        else:
            return {
                "product_id": product_id,
                "error": "Ambiguous result - check database",
            }
    except DBConnectionException as d:
        raise HTTPException(status_code=500, detail=str(d))
    except ItemNotFoundException as i:
        logger.info(f"No product: {i}")
        raise HTTPException(status_code=404, detail=str(i))
    except Exception as e:
        logger.info(f"Unexpected exception in /products/id endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users")
def get_users() -> list[dict]:
    """Gets list of all users

    Returns list of users excluding important contact details,
    for example email and phone number. If no users, returns
    empty list.

    Returns:
        (Response) Result of query.

        Example:
        [
            {
                "user_id": 1,
                "first_name": "John",
                "last_name": "Smith"
            },
            {
                "user_id": 2,
                "first_name": "Jane",
                "last_name": "Jones"
            }
        ]
    """
    query = query_strings["users"]
    try:
        resp = process_query(query)
        if len(resp) == 0:
            raise ItemNotFoundException("users")
        return resp
    except DBConnectionException as d:
        raise HTTPException(status_code=500, detail=str(d))
    except ItemNotFoundException as i:
        logger.info(f"No user: {i}")
        raise HTTPException(status_code=404, detail=str(i))
    except Exception as e:
        logger.info(f"Unexpected exception in /users endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/sales")
def get_user_sales(user_id: int, date_from: str, date_to: str):
    """Gets sales for specific user between two dates

    Returns error response if user does not exist. Returns
    empty list if no sales in date range. (Data is available between
    1/9/2022 - 23/1/2023).

    Args:
        user_id (int): valid user identifier
        date_from (str): date in format yyyy-mm-dd
        date_to (str): date in format yyyy-mm-dd

    Returns:
        (Response) Result of query

        Example:
        [
            {'user_id': 5, 'sales_id': 14, 'product_id': 14,
            'Category': 'Movies', 'product_title': 'Awesome',
            'transaction_ts': '2023-01-23 12:17:01.181', 'product_cost': 19:52, 'num_items':2},
            {'user_id': 5, 'sales_id': 272, 'product_id': 3,
            'Category': 'Books', 'product_title': 'Wow',
            'transaction_ts': '2023-01-02 01:17:01.181', 'product_cost': 7.47,, 'num_items':1}
        ]
    """
    present = check_user(user_id)
    if len(present) == 1:
        query = query_strings["user_sales"]
        date_limit = f"{date_to} 23:59:59.99"
        try:
            return process_query(
                query, user_id=user_id, date_from=date_from, date_to=date_limit
            )
        except DBConnectionException as d:
            logger.info("Connection exception while querying sales")
            raise HTTPException(status_code=500, detail=str(d))
        except Exception as e:
            logger.info(f"Unexpected exception in /users/id/sales endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/sales/latest")
def get_user_sales_latest(user_id: int):
    """Gets latest sales for user up to maximum of five

    Returns error response if user does not exist. Returns
    empty list if no sales.

    Args:
        user_id (int): valid user identifier

    Returns:
        (Response) Result of query

        Example:
        [
            {'user_id': 5, 'sales_id': 14, 'product_id': 14,
            'category': 'Movies', 'product_title': 'Awesome',
            'transaction_ts': '2023-01-23 12:17:01.181', 'product_cost': 19:52, 'num_items':2},
            {'user_id': 5, 'sales_id': 272, 'product_id': 3,
            'category': 'Books', 'product_title': 'Wow',
            'transaction_ts': '2023-01-02 01:17:01.181', 'product_cost': 7.47, 'num_items':2}
        ]
    """
    present = check_user(user_id)
    if len(present) == 1:
        query = query_strings["latest_sales"]
        try:
            return process_query(query, user_id=user_id)
        except DBConnectionException as d:
            logger.info("Connection exception while querying latest sales")
            raise HTTPException(status_code=500, detail=str(d))
        except Exception as e:
            logger.info(f"Unexpected exception in /sales/latest endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))
