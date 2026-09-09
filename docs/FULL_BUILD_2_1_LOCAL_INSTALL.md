# Full Build 2.1 — local installation

Target: isolated LAN installation over HTTP.

1. Keep `.env` and PostgreSQL volume intact.
2. Run `./deploy/preflight-full-build-2.1.sh`.
3. Run `./deploy/update-full-build-2.1.sh`.
4. Run `./deploy/status-full-build-2.1.sh`.
5. Open the configured LAN HTTP address in the browser.

The updater creates a PostgreSQL dump and application backup before replacement. It never runs `docker compose down -v`.

If verification fails, collect diagnostics with `./deploy/logs-full-build-2.1.sh`. Application files can be rolled back with `deploy/rollback-full-build-2.1.sh`; database restoration is deliberately separate and manual.
