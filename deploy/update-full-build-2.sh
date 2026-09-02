#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR=".backup/frontend-$STAMP"
mkdir -p .backup

if [ -d frontend ]; then
  mv frontend "$BACKUP_DIR"
  echo "Backup frontend -> $BACKUP_DIR"
fi

git fetch origin main
mkdir -p frontend
git checkout origin/main -- frontend

if [ ! -f .env ]; then
  echo "ERROR: .env not found. Run deploy/first-run.sh first." >&2
  exit 1
fi

# Rebuild only the frontend. Database volume and backend are not removed.
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d --no-deps frontend

# Ensure reverse proxy remains up.
docker compose -f docker-compose.prod.yml up -d caddy

echo
echo "Full Build 2.0 frontend updated successfully."
echo "Application: https://176-215-254-156.sslip.io"
echo "Backup:      $BACKUP_DIR"
