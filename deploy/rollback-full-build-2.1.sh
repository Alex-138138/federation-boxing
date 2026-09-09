#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
BACKUP=${1:-}
if [ -z "$BACKUP" ] || [ ! -d "$BACKUP" ]; then
  echo "Usage: $0 backup/YYYYMMDD-HHMMSS" >&2
  exit 2
fi
rm -rf frontend backend
cp -a "$BACKUP/frontend" frontend
cp -a "$BACKUP/backend" backend
docker compose -f docker-compose.prod.yml build backend frontend
docker compose -f docker-compose.prod.yml up -d backend frontend caddy
echo "Rollback complete. Database volume was not modified."
