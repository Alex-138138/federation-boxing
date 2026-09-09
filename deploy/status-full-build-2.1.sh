#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f docker-compose.prod.yml ps
printf '\nFrontend: '
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1/
printf 'API health: '
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1/api/health
