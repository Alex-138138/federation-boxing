#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
./deploy/preflight-full-build-2.1.sh
./deploy/backup-db-full-build-2.1.sh
STAMP=$(date +%Y%m%d-%H%M%S)
mkdir -p "backup/$STAMP"
cp -a frontend "backup/$STAMP/frontend" 2>/dev/null || true
cp -a backend "backup/$STAMP/backend" 2>/dev/null || true
git fetch origin full-build-2.1
git checkout origin/full-build-2.1 -- frontend backend deploy tests
docker compose -f docker-compose.prod.yml build backend frontend
docker compose -f docker-compose.prod.yml up -d db backend frontend caddy
sleep 5
BASE_URL="${BASE_URL:-http://127.0.0.1}" ./deploy/verify-full-build-2.1.sh
echo "Full Build 2.1 updated. Application backup: backup/$STAMP"
