import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from unittest.mock import patch
from src.data.sql import query_strings
from data import (
    categories_result,
    multiple_sales,
    products_expected,
    single_sale,
    products_results,
    users_results,
    user_sales_results,
)
from src.api.helpers import DBConnectionException


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


def dummy_process(query, **kwargs):
    if query == query_strings["categories"]:
        return categories_result
    elif query == query_strings["products"]:
        return products_results
    elif query == query_strings["product"]:
        ((key, param),) = kwargs.items()
        result = [p for p in products_results if p["product_id"] == int(param)]
        assert len(result) == 1
        return result
    elif query == query_strings["users"]:
        return users_results


class TestGetCategories:
    def test_categories_success_response(self, client):
        with patch("src.api.app.process_query", side_effect=dummy_process):
            result = client.get("/api/categories")
            assert result.json() == categories_result

    @patch("src.api.helpers.get_db_connection")
    def test_categories_500_response(self, mock_conn, client):
        mock_conn.side_effect = DBConnectionException("Awful error")
        result = client.get("/api/categories")
        assert result.status_code == 500
        assert result.json() == {
            "detail": "There was an error connecting to the database: Awful error"
        }


class TestGetProducts:
    def test_get_products_returns_products(self, client):
        with patch("src.api.app.process_query", side_effect=dummy_process):
            result = client.get("/api/products")
            assert result.json() == products_expected


class test_get_products_returns_productsGetProductsById:
    def test_products_id(self, client):
        with patch("src.api.app.process_query", side_effect=dummy_process):
            result = client.get("/api/products/7")
            assert result.json() == products_expected[1]


class TestGetUsers:
    def test_users(self, client):
        with patch("src.api.app.process_query", side_effect=dummy_process):
            result = client.get("/api/users")
            res_list = result.json()
            assert len(res_list) == 3
            assert res_list[0]["first_name"] == "Afton"
            assert res_list[1]["last_name"] == "Bergnaum"
            assert "email" not in res_list[1]


class TestGetUsersAverageSpend:
    def test_get_user_average_calculates_average_one_purchase(self, client):
        patch_return = single_sale
        with patch(
            "src.api.app.process_query", return_value=patch_return
        ) as mock_process:
            expected = {"user_id": 10, "average_spend": 202.00}
            expected_query = query_strings["sales_average"]
            result = client.get("/api/users/10/average_spend")
            mock_process.assert_called_once_with(expected_query, user_id=10)
            assert result.json() == expected

    def test_get_user_average_correctly_calculates_average_many_purchases(self, client):
        patch_return = multiple_sales
        with patch("src.api.app.process_query", return_value=patch_return):
            expected = {"user_id": 10, "average_spend": 118.0}
            result = client.get("/api/users/10/average_spend")
            assert result.json() == expected


class TestGetUserSales:
    @patch("src.api.app.check_user", return_value=[3])
    def test_user_sales(self, mock_check, client):
        with patch("src.api.app.process_query", return_value=user_sales_results):
            result = client.get(
                "/api/users/3/sales?date_from=2022-10-01&date_to=2022-11-01"
            )
            result_list = result.json()
            expected = {
                "user_id": 7,
                "sales_id": 373,
                "product_id": 9,
                "transaction_ts": "2022-10-06T11:34:50.096Z",
                "product_title": "Bespoke Wooden Bike",
                "product_cost": 393.000000000000000000000000000000,
                "category": "Garden",
                "num_items": 1,
            }
            assert len(result_list) == 2
            assert result_list[1] == expected
            assert result_list[0]["sales_id"] == 408


class TestIntegration:
    def test_user_sales_integration(self, client):
        result = client.get(
            "/api/users/3/sales?date_from=2022-10-01&date_to=2022-10-11"
        )
        result_list = result.json()
        assert len(result_list) == 5
        sale_ids = {s["sales_id"] for s in result_list}
        assert sale_ids == set([307, 519, 407, 421, 46])

    def test_user_sales_empty_response_when_sales_dates_out_of_range(self, client):
        result = client.get(
            "/api/users/3/sales?date_from=2023-10-01&date_to=2023-10-11"
        )
        result_list = result.json()
        assert len(result_list) == 0

    def test_error_response_nonexistent_user(self, client):
        res = client.get("/api/users/777/sales?date_from=2022-10-01&date_to=2022-10-11")
        assert res.status_code == 404
        assert res.json() == {
            "detail": "No instance of user was found in the database with id 777."
        }

    def test_latest_sales_for_user(self, client):
        result = client.get("/api/users/7/sales/latest")
        result_list = result.json()
        assert len(result_list) == 5
        assert result_list[0]["transaction_ts"] == "2023-01-23T10:08:26.341000"
        assert result_list[4]["product_title"] == "Refined Steel Sausages"
        err = client.get("/api/users/777/sales/latest")
        assert err.status_code == 404
        assert err.json() == {
            "detail": "No instance of user was found in the database with id 777."
        }

    def test_product_error_response_missing_product(self, client):
        result = client.get("/api/products/88")
        assert result.status_code == 404
        assert result.json() == {
            "detail": "No instance of product was found in the database with id 88."
        }
