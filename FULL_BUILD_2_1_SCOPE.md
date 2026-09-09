# Full Build 2.1 — unified delivery

This branch is the integration line for the complete role and CMS upgrade.

## Administrator
- users and multi-role management
- halls, trainers, groups and schedules
- applications and moderation
- all group messages and audit
- athletes, attendance, achievements and rating
- public content and role-dashboard content

## Visual CMS
- page/block editor for public_home, admin_home, trainer_home, parent_home, athlete_home
- block types: text, image, hero/banner, card, button/link, gallery, grid, divider, news, greeting, person/profile
- add, duplicate, delete, reorder, hide/show
- editable title, text, media URL, link, background, text alignment, size, radius and layout metadata
- draft/version history, preview, publish and restore-by-version
- protected authorization and relationship logic remains server-side

## Trainer
- own groups and athletes only
- applications approve/reject
- QR/join code
- schedules, attendance, achievements and rating
- messages to one or all owned groups

## Parent
- linked children
- hall, group, trainer contacts, schedule
- attendance, achievements, rating/history
- trainer messages and notifications
- enrollment via QR/join code

## Athlete
- personal sport profile
- hall/group/trainer/schedule
- attendance, achievements, rating/history
- messages and notifications

## Delivery rule
Do not delete PostgreSQL volumes during upgrade. Full Build 2.1 must overlay the existing deployment and preserve user data.
