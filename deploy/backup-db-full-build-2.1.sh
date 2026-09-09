#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p backups
STAMP=$(date +%Y%m%d-%H%M%S)
OUT="backups/boxing-$STAMP.sql"
echo "Creating database backup: $OUT"
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U boxing -d boxing > "$OUT"
test -s "$OUT"
echo "Database backup ready: $OUT"
