#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
BASE_URL="${BASE_URL:-http://127.0.0.1}"
echo '[1/4] containers'
docker compose -f docker-compose.prod.yml ps
echo '[2/4] frontend'
curl -fsS "$BASE_URL/" >/dev/null
echo '[3/4] backend health'
curl -fsS "$BASE_URL/api/health" >/dev/null
echo '[4/4] static contracts'
python3 tests/integration/api_contract_check.py
python3 tests/integration/frontend_contract_check.py
echo 'Full Build 2.1 verification: OK'
