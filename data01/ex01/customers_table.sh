#!/bin/bash

sleep 4
set -e

# This script creates and loads tables from CSV files in the ../customer directory into a PostgreSQL database.
for filepath in .././customer/*.csv; do
    filename=$(basename "$filepath")
    table_name="${filename%.*}"
    
    echo "Creating and loading table: $table_name"
    
    cat <<EOF > load.sql
DROP TABLE IF EXISTS $table_name;

CREATE TABLE $table_name (
    event_time TIMESTAMP NOT NULL,
    event_type TEXT,
    product_id INTEGER,
    price MONEY,
    user_id BIGINT,
    user_session UUID
);

\copy $table_name FROM '/csv/$filename' DELIMITER ',' CSV HEADER;
EOF
    
    docker exec -i postgres psql -U jdasilva -d piscineds < load.sql
done

rm load.sql
echo "All tables created and loaded successfully."

# This script combines all the tables in the customers table into a single table.
echo "Beginning to combine all the tables in the customers table..."

cat <<EOF > combine.sql
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    event_time TIMESTAMP NOT NULL,
    event_type TEXT,
    product_id INTEGER,
    price MONEY,
    user_id BIGINT,
    user_session UUID,
    source_table TEXT
);

CREATE OR REPLACE FUNCTION insert_into_customers() RETURNS VOID AS \$\$
DECLARE
    table_record RECORD;
    query TEXT;
BEGIN
    FOR table_record IN
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name LIKE 'data_202%_%'
        AND table_schema = 'public'
    LOOP
        query := format('INSERT INTO customers (event_time, event_type, product_id, price, user_id, user_session, source_table)
                         SELECT event_time, event_type, product_id, price, user_id, user_session, %L FROM %I',
                         table_record.table_name, table_record.table_name);
        EXECUTE query;
        RAISE NOTICE 'Inserted data from table: %', table_record.table_name;
    END LOOP;
    RAISE NOTICE 'All tables have been combined into the customers table.';
END;
\$\$ LANGUAGE plpgsql;

SELECT insert_into_customers();
EOF

docker exec -i postgres psql -U jdasilva -d piscineds < combine.sql
rm combine.sql
echo "All tables have been combined into the customers table."
