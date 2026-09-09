#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tests/integration/run_static_checks.py
docker compose -f docker-compose.prod.yml config >/dev/null
echo 'Full Build 2.1 local readiness: OK'
