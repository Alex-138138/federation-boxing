#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
LINES="${LINES:-80}"
echo '=== backend ==='
docker compose -f docker-compose.prod.yml logs --tail="$LINES" backend || true
echo '=== caddy ==='
docker compose -f docker-compose.prod.yml logs --tail="$LINES" caddy || true
echo '=== db ==='
docker compose -f docker-compose.prod.yml logs --tail=30 db || true
