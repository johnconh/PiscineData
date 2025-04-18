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

def create_tables_from_csv(conn):
    with conn.cursor() as cursor:
        for filename in os.listdir(CSV_DIR):
            if filename.endswith(".csv"):
                table_name = filename.replace(".csv", "")
                print(f"Creating table {table_name}...")

                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        event_time TIMESTAMP NOT NULL,
                        event_type TEXT,
                        product_id INTEGER,
                        price MONEY,
                        user_id BIGINT,
                        user_session UUID
                    );
                """)
                conn.commit()

                file_path = os.path.join(CSV_DIR, filename)
                with open(file_path, 'r') as f:
                    cursor.copy_expert(f"""
                        COPY {table_name} (event_time, event_type, product_id, price, user_id, user_session)
                        FROM STDIN
                        WITH CSV HEADER
                    """, f)
                conn.commit()
                print(f"Data from {filename} successfully loaded into {table_name}.")

def create_customers_table(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                event_time TIMESTAMP NOT NULL,
                event_type TEXT,
                product_id INTEGER,
                price MONEY,
                user_id BIGINT,
                user_session UUID,
                source_table TEXT
            );
        """)
        conn.commit()

def merge_tables_into_customers(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name LIKE 'data_202%' AND table_type = 'BASE TABLE';
        """)
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            print(f"Merging data from {table_name} into 'customers'...")

            cursor.execute(f"""
                INSERT INTO customers (event_time, event_type, product_id, price, user_id, user_session, source_table)
                SELECT event_time, event_type, product_id, price, user_id, user_session, '{table_name}' 
                FROM {table_name};
            """)
            conn.commit()
            print(f"Data from {table_name} successfully merged.")

def move_and_delete_duplicates_temp_table(conn):
    print("\n🚿 Removing duplicates using TEMP table...")
    with conn.cursor() as cursor:
        # 1. Crear tabla temporal con los duplicados
        cursor.execute("""
            CREATE TEMP TABLE customers_dupes_temp AS
            SELECT *
            FROM (
                SELECT *,
                       LAG(event_time) OVER (
                           PARTITION BY event_type, product_id, user_id
                           ORDER BY event_time
                       ) AS prev_event_time
                FROM customers
            ) sub
            WHERE prev_event_time IS NOT NULL
              AND EXTRACT(EPOCH FROM (event_time - prev_event_time)) <= 1;
        """)
        conn.commit()
        print("✅ Duplicates selected into TEMP table.")

        cursor.execute("""
            DELETE FROM customers
            WHERE ctid IN (SELECT ctid FROM customers_dupes_temp);
        """)
        deleted = cursor.rowcount
        conn.commit()
        print(f"🗑️ Deleted {deleted} duplicate rows from customers.")

def main():
    conn = create_connection()

    try:
        # create_tables_from_csv(conn)
        # create_customers_table(conn)
        # merge_tables_into_customers(conn)
        move_and_delete_duplicates_temp_table(conn)
        print("🚀 All operations completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
