import pytest
import psycopg2
import os
import requests
from dotenv import load_dotenv

load_dotenv()

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
            # Check if the table exists
            cur.execute("SELECT to_regclass(%s)", (table_to_check,))
            table_exists = cur.fetchone()[0]
            assert table_exists is not None, f"Table '{table_to_check}' does not exist"

            # get all comums
            cur.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
                (table_to_check,),
            )
            columns = cur.fetchall()
            column_names = [col[0] for col in columns]

            for field in expected_fields:
                assert (
                    field in column_names
                ), f"Field '{field}' does not exist in '{table_to_check}'"

            additional_fields = set(column_names) - set(expected_fields)
            assert not additional_fields, f"Additional fields {additional_fields} found in table '{table_to_check}'"


@pytest.mark.parametrize(
    ("test_input", "expected_output"),
    [
        ("name", "name"),
    ],
)
def test_create_product_get_product(test_input, expected_output):
    create = requests.post(
        API_BASE_URL + "/products", json={"name": test_input, "description": test_input}
    )
    assert (
        create.status_code == 201
    ), f"Product not created. Status code: {create.status_code}"
    product_id = create.json()["id"]
    update = requests.put(
        API_BASE_URL + f"/products/{product_id}",
        json={"name": "uwu", "description": "uwu"},
    )
    assert (
        update.status_code == 200
    ), f"Product not updated. Status code: {update.status_code}"
    update_back = requests.put(
        API_BASE_URL + f"/products/{product_id}",
        json={"name": test_input, "description": test_input},
    )
    assert (
        update_back.status_code == 200
    ), f"Product not updated. Status code: {update_back.status_code}"
    delete = requests.delete(API_BASE_URL + f"/products/{product_id}")
    assert (
        delete.status_code == 200
    ), f"Product not deleted. Status code: {delete.status_code}"
    get = requests.get(API_BASE_URL + "/products")
    assert expected_output not in [
        product["name"] for product in get.json()
    ], f"Product not deleted. Status code: {delete.status_code}"  # github copilot idk


# def delete_table_data(table_name):
#     with psycopg2.connect(DATABASE_URL) as conn:
#         with conn.cursor() as cur:
#             cur.execute(f"DELETE FROM {table_name}")
#             conn.commit()

# delete_table_data("products")
