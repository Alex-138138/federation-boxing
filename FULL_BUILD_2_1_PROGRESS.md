# Full Build 2.1

Integrated development branch for the Federation Boxing application.

## Included in this package

- Administrator console API for users, statuses, roles, halls, groups, applications and all group messages.
- Administrator sport overview for athletes, group/hall assignment, attendance, achievements and rating history.
- CMS page versioning and publication from the existing backend.
- CMS block catalog: text, image, hero/banner, card, gallery, button, columns and divider.
- Managed page keys for public Federation sections and all role dashboards.
- Browser-side visual CMS editor module with add, remove, duplicate, reorder, hide/show and style fields.
- CMS workspace responsive styles.
- API version advanced to 2.1.0.

## Safety boundary

CMS content can change presentation and editorial content. Authentication, role authorization, family relations, trainer/group ownership, age rules and other protected business rules remain backend-controlled.

## Deployment

Do not delete PostgreSQL volumes. The production update must preserve the existing `.env` and database volume.
