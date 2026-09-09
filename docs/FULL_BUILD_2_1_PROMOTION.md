# Promotion of Full Build 2.1

Promotion is allowed only after the static readiness check and local runtime verification pass.

1. Keep PostgreSQL volume intact.
2. Create DB backup.
3. Run `deploy/check-full-build-2.1.sh`.
4. Install branch build with `deploy/update-full-build-2.1.sh`.
5. Run `BASE_URL=http://192.168.95.103 deploy/post-update-full-build-2.1.sh`.
6. Execute the role/CMS test matrix.
7. Only after successful acceptance, promote the branch to `main`.

Never use `docker compose down -v` during this process.
