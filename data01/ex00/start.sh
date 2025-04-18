#!/bin/bash
set -e

LOGFILE="/app/log.txt"

: > "$LOGFILE"

SCRIPTS=(
  "ex01/customers_table.py"
  "ex02/remove_duplicates.py"
)

echo "=== $(date '+%Y-%m-%d %H:%M:%S') — Iniciando ejecución de scripts ===" | tee -a "$LOGFILE"

for script in "${SCRIPTS[@]}"; do
    if [ -f "/app/$script" ]; then
        echo ">>> $(date '+%Y-%m-%d %H:%M:%S') — Ejecutando $script" | tee -a "$LOGFILE"
        python "/app/$script" >> "$LOGFILE" 2>&1
        echo "<<< $(date '+%Y-%m-%d %H:%M:%S') — $script finalizado (exit=$?)" | tee -a "$LOGFILE"
    else
        echo "!!! WARNING: /app/$script no encontrado" | tee -a "$LOGFILE"
    fi
done

echo "=== $(date '+%Y-%m-%d %H:%M:%S') — Todos los scripts completados ===" | tee -a "$LOGFILE"
