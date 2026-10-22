#!/usr/bin/env sh
# Uso: ./scripts/restore_db.sh archivo.sql.gz
# Destruye y recrea el esquema público del DB indicado.

set -e

FILE="$1"
if [ -z "$FILE" ]; then
  echo "Uso: $0 backup.sql.gz"
  exit 1
fi

HOST="${POSTGRES_HOST:-localhost}"
PORT="${POSTGRES_PORT:-5555}"
USER="${POSTGRES_USER:-postgres}"
DB="${POSTGRES_DB:-db-parcial-1}"
export PGPASSWORD="${POSTGRES_PASSWORD:-postgres}"

gunzip -c "$FILE" | psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB"
echo "Restore completado en $DB"
