#!/usr/bin/env sh
# Uso: ./scripts/backup_db.sh [nombre_archivo.sql.gz]
# Variables: POSTGRES_* o defaults del compose dev.

set -e

OUT="${1:-backup_$(date +%Y%m%d_%H%M%S).sql.gz}"
HOST="${POSTGRES_HOST:-localhost}"
PORT="${POSTGRES_PORT:-5555}"
USER="${POSTGRES_USER:-postgres}"
DB="${POSTGRES_DB:-db-parcial-1}"

export PGPASSWORD="${POSTGRES_PASSWORD:-postgres}"

pg_dump -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" | gzip -c > "$OUT"
echo "Backup: $OUT"
