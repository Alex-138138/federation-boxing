#!/usr/bin/env sh
set -eu
python3 bootstrap.py
printf '\nСборка восстановлена. Запуск:\n  docker compose up --build\n'
