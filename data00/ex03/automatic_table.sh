#!/bin/bash

sleep 4

set -e

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
