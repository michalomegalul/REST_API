import pytest
import psycopg2
import os
import requests

DATABASE_URL = os.environ.get("DATABASE_URL")
API_BASE_URL = os.environ.get("API_BASE_URL")


@pytest.mark.parametrize("table_to_check", ["products", "offers"])
def test_tables_exist(table_to_check):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute(f"SELECT to_regclass('{table_to_check}')")
        result = cur.fetchone()[0]
        assert result is not None, f"Table '{table_to_check}' does not exist"
    except Exception as e:
        pytest.fail(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


# def clean_up():
#     conn = psycopg2.connect(DATABASE_URL)
#     cur = conn.cursor()
#     cur.execute("DELETE FROM products")
#     cur.execute("DELETE FROM offers")
#     conn.commit()
#     conn.close()
@pytest.mark.parametrize()
def test_create_product():
    response = requests.post(
        f"{API_BASE_URL}/products",
        json={"name": "Test Product", "description": "This is a test product"},
    )

    assert response.status_code == 201
    assert "id" in response.json()
