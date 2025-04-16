#!/bin/bash

sleep 4

set -e

TABLE_NAME="items"
CSV_FILE="item.csv"

echo "Creating and loading table: $TABLE_NAME"

cat <<EOF > load.sql
DROP TABLE IF EXISTS $TABLE_NAME;

CREATE TABLE $TABLE_NAME (
    product_id INTEGER,
    category_id BIGINT,
    category_code TEXT,
    brand TEXT
);

\copy $TABLE_NAME FROM '/item/$CSV_FILE' DELIMITER ',' CSV HEADER;
EOF

docker exec -i postgres psql -U jdasilva -d piscineds < load.sql

rm load.sql

echo "Table $TABLE_NAME created and loaded successfully."
