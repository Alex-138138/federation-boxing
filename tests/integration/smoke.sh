#!/usr/bin/env bash
set -euo pipefail
BASE=${1:-http://127.0.0.1}
echo "Checking frontend: $BASE/"
curl -fsS "$BASE/" >/dev/null
echo "Checking API: $BASE/api/health"
curl -fsS "$BASE/api/health"
echo
echo 'Smoke checks passed.'
