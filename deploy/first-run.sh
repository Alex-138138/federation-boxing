#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if ! command -v docker >/dev/null 2>&1; then
  apt-get update
  apt-get install -y ca-certificates curl gnupg
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  . /etc/os-release
  DOCKER_CODENAME="${UBUNTU_CODENAME:-${VERSION_CODENAME:-noble}}"
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${DOCKER_CODENAME} stable" > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# Restore the complete archived source tree, then put the tracked Full Build 2.0
# files back on top so the archive can never downgrade the current app.
python3 bootstrap.py
git checkout HEAD -- frontend backend nginx docker-compose.prod.yml deploy/Caddyfile

if [ ! -f .env ]; then
  POSTGRES_PASSWORD="$(openssl rand -hex 24)"
  JWT_SECRET="$(openssl rand -hex 48)"
  cat > .env <<EOF
APP_DOMAIN=176-215-254-156.sslip.io
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
JWT_SECRET=${JWT_SECRET}
VAPID_PUBLIC_KEY=
VAPID_PRIVATE_KEY=
VAPID_SUBJECT=mailto:admin@example.org
EOF
  chmod 600 .env
fi

docker compose -f docker-compose.prod.yml up -d --build

echo
printf 'Application: https://176-215-254-156.sslip.io\n'
printf 'API docs:    https://176-215-254-156.sslip.io/api/docs\n'
