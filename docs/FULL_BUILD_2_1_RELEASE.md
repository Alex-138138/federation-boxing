# Full Build 2.1 release procedure

1. Keep the existing PostgreSQL Docker volume.
2. Run `deploy/preflight-full-build-2.1.sh`.
3. Run `deploy/update-full-build-2.1.sh`.
4. Run `tests/integration/smoke.sh http://192.168.95.103` on the local federation host.
5. Test admin, trainer, parent and athlete accounts.
6. Test CMS save, preview, publish and restore.
7. If application code must be reverted, use `deploy/rollback-full-build-2.1.sh <backup-dir>`.

Never use `docker compose down -v` during an application update because that removes named volumes, including PostgreSQL data.
