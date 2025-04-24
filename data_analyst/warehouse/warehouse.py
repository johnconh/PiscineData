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

CSV_DIR = "/app/customer" 
ITEM_DIR = "/app/item"

def create_connection():
    return psycopg2.connect(**DB_PARAMS)

def create_table_from_item(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS item;
            CREATE TABLE item (
                product_id INTEGER,
                category_id BIGINT,
                category_code TEXT,
                brand TEXT
            );
        """)
        conn.commit()

        file_path = os.path.join(ITEM_DIR, "item.csv")
        with open(file_path, 'r') as f:
            cursor.copy_expert("""
                COPY item (product_id, category_id, category_code, brand)
                FROM STDIN
                WITH CSV HEADER
            """, f)
        conn.commit()
        print("✅ Data from item.csv successfully loaded into item.")

def create_tables_from_customer(conn):
    with conn.cursor() as cursor:
        for filename in os.listdir(CSV_DIR):
            if filename.endswith(".csv"):
                table_name = filename.replace(".csv", "")
                print(f"🛠️ Creating table {table_name}...")

                cursor.execute(f"""
                    DROP TABLE IF EXISTS {table_name};
                    CREATE TABLE {table_name} (
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
                print(f"✅ Data from {filename} successfully loaded into {table_name}.")

def create_customers_table(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS customers;
            CREATE TABLE customers (
                event_time TIMESTAMP NOT NULL,
                event_type TEXT,
                product_id INTEGER,
                price MONEY,
                user_id BIGINT,
                user_session UUID
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
            print(f"🔄 Merging data from {table_name} into 'customers'...")

            cursor.execute(f"""
                INSERT INTO customers (event_time, event_type, product_id, price, user_id, user_session)
                SELECT event_time, event_type, product_id, price, user_id, user_session 
                FROM {table_name};
            """)
            conn.commit()
            print(f"✅ Data from {table_name} successfully merged.")

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

def fusion_table(conn):
    print("\n🔄 Fusion of tables...")
    with conn.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE customers
            ADD COLUMN IF NOT EXISTS category_id BIGINT,
            ADD COLUMN IF NOT EXISTS category_code TEXT,
            ADD COLUMN IF NOT EXISTS brand TEXT;
        """)
        conn.commit()
        print("✅ Columns added to customers table.")
        cursor.execute("""
            UPDATE customers c
            SET 
                category_id = COALESCE(i.category_id, c.category_id),
                category_code = COALESCE(i.category_code, c.category_code),
                brand = COALESCE(i.brand, c.brand)
            FROM item i
            WHERE c.product_id = i.product_id
              AND (i.category_id IS NOT NULL 
                   OR i.category_code IS NOT NULL 
                   OR i.brand IS NOT NULL);
        """)
        conn.commit()
        print("✅ Customers table updated with item data.")

def main():
    conn = create_connection()

    try:
        create_table_from_item(conn)
        print("✅ Item table created successfully.")
        create_tables_from_customer(conn)
        print("✅ All customer tables created successfully.")
        print("🛠️ Creating customers table...")
        create_customers_table(conn)
        merge_tables_into_customers(conn)
        print("✅ All data merged into customers table successfully.")
        move_and_delete_duplicates_temp_table(conn)
        print("✅ Duplicates removed successfully.")
        fusion_table(conn)
        print("✅ Fusion completed successfully.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
