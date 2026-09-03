#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

STAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p .backups
[ -d frontend ] && tar -czf ".backups/frontend-${STAMP}.tgz" frontend || true
[ -d backend ] && tar -czf ".backups/backend-${STAMP}.tgz" backend || true

if [ ! -f .env ]; then
  echo "ERROR: .env not found. Run deploy/first-run.sh first." >&2
  exit 1
fi

git fetch origin main

# Recreate the complete original source tree if this checkout was made from
# the archive-based Full Build 1.0 repository. This does not touch Docker volumes.
python3 bootstrap.py

# Overlay all tracked Full Build 2.0 sources from GitHub.
git checkout origin/main -- frontend backend nginx docker-compose.prod.yml deploy/Caddyfile

# Rebuild application services only. Never use `down -v`: PostgreSQL data stays intact.
docker compose -f docker-compose.prod.yml up -d --build backend frontend caddy

echo
printf 'Full Build 2.0 updated. PostgreSQL volume was preserved.\n'
printf 'Application: https://176-215-254-156.sslip.io\n'
printf 'API docs:    https://176-215-254-156.sslip.io/api/docs\n'
printf 'Backups:     .backups/*-%s.tgz\n' "$STAMP"
