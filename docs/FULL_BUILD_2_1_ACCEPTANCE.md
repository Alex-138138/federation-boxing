# Full Build 2.1 acceptance

Release is accepted only after all checks below pass on the target machine.

- frontend returns HTTP 200
- `/api/health` returns HTTP 200
- admin can open user, directory, audit and CMS controls
- trainer sees only own groups and can process applications
- parent sees linked children and can submit a join application
- athlete sees own schedule, rating, achievements and attendance
- CMS can save, preview, publish and restore versions
- published CMS content is visible without admin privileges
- PostgreSQL backup exists before update
- update does not run `docker compose down -v` and does not remove DB volumes
- rollback script affects application files/containers only, not database data
