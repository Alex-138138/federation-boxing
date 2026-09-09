#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null
command -v git >/dev/null
test -f docker-compose.prod.yml
test -f .env
grep -q '^POSTGRES_PASSWORD=' .env
echo 'Preflight OK: Docker, Git, compose and environment are present.'
