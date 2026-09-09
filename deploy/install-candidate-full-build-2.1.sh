#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
./deploy/pre-install-full-build-2.1.sh
git fetch origin full-build-2.1
git checkout origin/full-build-2.1 -- backend frontend deploy tests docs
docker compose -f docker-compose.prod.yml build backend frontend
docker compose -f docker-compose.prod.yml up -d db backend frontend caddy
./deploy/post-update-full-build-2.1.sh
echo 'Full Build 2.1 release candidate installed.'
