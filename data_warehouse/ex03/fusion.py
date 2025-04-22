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

def create_connection():
    return psycopg2.connect(**DB_PARAMS)

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
        fusion_table(conn)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()