import psycopg2
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

CSV_DIR = "../customer"  

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

def main():
    conn = create_connection()

    try:
        create_tables_from_csv(conn)
        create_customers_table(conn)
        merge_tables_into_customers(conn)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
