#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
BASE_URL="${BASE_URL:-http://127.0.0.1}"
BASE_URL="$BASE_URL" ./deploy/verify-full-build-2.1.sh
./deploy/status-full-build-2.1.sh
echo "Open: $BASE_URL"
