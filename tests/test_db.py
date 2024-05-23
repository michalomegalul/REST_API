import pytest
import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL_LOCAL")
API_BASE_URL = os.environ.get("API_BASE_URL")


@pytest.mark.parametrize(
    ("table_to_check", "expected_fields"),
    [
        ("products", ["id", "name", "description"]),
        ("offers", ["id", "price", "items_in_stock", "product_id", "timestamp"]),
    ],
)
def test_tables_exist(table_to_check, expected_fields: list):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            # Check if table exists (parameterized)
            cur.execute(
                "SELECT to_regclass(%s)", (table_to_check,)
            )  # Parameterized query
            table_exists = cur.fetchone()[0]
            assert table_exists is not None, f"Table '{table_to_check}' does not exist"

            # Check if fields exist (parameterized)
            for field in expected_fields:
                cur.execute(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
                    (table_to_check, field),  # Parameters passed as a tuple
                )
                field_exists = cur.fetchone()
                assert (
                    field_exists
                ), f"Field '{field}' does not exist in table '{table_to_check}'"


# def clean_up():
#     conn = psycopg2.connect(DATABASE_URL)
#     cur = conn.cursor()
#     cur.execute("DELETE FROM products")
#     cur.execute("DELETE FROM offers")
#     conn.commit()
#     conn.close()
# @pytest.mark.parametrize()
# def test_create_product():
#     response = requests.post(
#         f"{API_BASE_URL}/products",
#         json={"name": "Test Product", "description": "This is a test product"},
#     )

#     assert response.status_code == 201
#     assert "id" in response.json()
