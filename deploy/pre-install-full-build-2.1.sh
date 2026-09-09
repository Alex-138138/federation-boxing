#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo '[1/4] static contracts'
python3 tests/integration/run_static_checks.py
echo '[2/4] environment'
test -f .env
test -f docker-compose.prod.yml
echo '[3/4] database backup'
./deploy/backup-db-full-build-2.1.sh
echo '[4/4] pre-install gate'
python3 tests/integration/release_gate.py
echo 'Pre-install Full Build 2.1: OK'
