import psycopg2
import time
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"), 
    "host": "postgres",
    "port":  5432
}

CSV_DIR = "csv/"  

def create_connection():
    return psycopg2.connect(**DB_PARAMS)

def move_and_delete_duplicates_temp_table(conn):
    print("\n🧹 Removing duplicates...")
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TEMPORARY TABLE temp_table AS
            WITH table_events AS (
                SELECT
                    event_time,
                    event_type,
                    product_id,
                    price,
                    user_id,
                    user_session,
                    ROW_NUMBER() OVER (
                        PARTITION BY event_type, product_id
                        ORDER BY event_time
                    ) AS row_num,
                    LAG(event_time) OVER (
                        PARTITION BY event_type, product_id
                        ORDER BY event_time
                    ) AS prev_time
                FROM customers
            )
            SELECT
                event_time, event_type, product_id, price, user_id, user_session
            FROM table_events
            WHERE
                row_num = 1
            OR
                (prev_time IS NOT NULL AND (event_time - prev_time > INTERVAL '1 second'));
        """)
        print("✅ Temporary table created with duplicates removed.")
        cursor.execute("TRUNCATE customers")
        print("🗑️ Original customers table truncated.")
        cursor.execute("""
            INSERT INTO customers
            SELECT * FROM temp_table
        """)
        conn.commit()
        print("✅ Cleaned data inserted back into customers table.")

def main():
    conn = create_connection()

    try:
        move_and_delete_duplicates_temp_table(conn)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
