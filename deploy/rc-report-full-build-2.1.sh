#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo '=== Full Build 2.1 RC report ==='
git rev-parse --short HEAD
docker compose -f docker-compose.prod.yml ps
printf '\nHealth: '
curl -fsS http://127.0.0.1/api/health || true
printf '\nBackups: '
find backup -maxdepth 2 -type f 2>/dev/null | tail -5 || true
printf '\nNo destructive volume operation is performed by this report.\n'
