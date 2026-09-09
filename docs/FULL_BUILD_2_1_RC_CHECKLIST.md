# Full Build 2.1 — Release Candidate Checklist

Before promotion to main:

- [ ] pre-install gate passes
- [ ] PostgreSQL backup created
- [ ] all four containers are Up
- [ ] `/api/health` responds successfully
- [ ] admin login and role switch work
- [ ] trainer groups/applications/messages work
- [ ] parent children/join flow works
- [ ] athlete schedule/rating/attendance/achievements work
- [ ] CMS save, preview, publish and version history work
- [ ] public page renders published CMS blocks
- [ ] restart preserves database data
- [ ] rollback script preserves database volume

Promotion is allowed only after this checklist passes on the local installation.
