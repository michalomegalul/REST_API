import pytest
import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
API_BASE_URL = "http://0.0.0.0:5000/api"


def test_db_exists():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname='product_db'")
        result = cur.fetchone()
        assert result is not None, "Database does not exist"
    except Exception as e:
        pytest.fail(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def test_tables_exist():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        tables_to_check = ["products", "offers"]
        for table in tables_to_check:
            cur.execute(f"SELECT to_regclass('{table}')")
            result = cur.fetchone()[0]
            assert (
                result is not None
            ), f"Table '{table}' does not exist"  # This is still valid
    except Exception as e:
        pytest.fail(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
