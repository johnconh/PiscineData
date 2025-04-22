#!/bin/bash

sleep 4

set -e

TABLE_NAME="data_2022_oct"
CSV_FILE="data_2022_oct.csv"

echo "Creating and loading table: $TABLE_NAME"

cat <<EOF > load.sql
DROP TABLE IF EXISTS $TABLE_NAME;

CREATE TABLE $TABLE_NAME (
    event_time TIMESTAMP NOT NULL,
    event_type TEXT,
    product_id INTEGER,
    price MONEY,
    user_id BIGINT,
    user_session UUID
);

\copy $TABLE_NAME FROM '/csv/$CSV_FILE' DELIMITER ',' CSV HEADER;
EOF

docker exec -i postgres psql -U jdasilva -d piscineds < load.sql

rm load.sql

echo " Table $TABLE_NAME created and loaded successfully."
