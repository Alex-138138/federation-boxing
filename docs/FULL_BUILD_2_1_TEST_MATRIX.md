# Full Build 2.1 — test matrix

Before promotion to main verify:

- Admin: login, users/roles, halls/groups, applications, messages, audit, CMS.
- Trainer: own groups only, athletes, applications, attendance, rating, achievements, messages.
- Parent: linked children only, schedule, attendance, achievements, rating, coach messages, join code.
- Athlete: own profile, schedule, attendance, achievements, rating history, messages.
- CMS: create blocks, reorder, hide/show, preview, save version, publish, restore older version.
- Security: non-admin cannot call admin routes; trainer cannot manage another trainer's group.
- Persistence: restart containers and verify data remains.
- HTTP local deployment: frontend and `/api/health` respond through Caddy.
