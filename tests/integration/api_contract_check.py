"""Static contract checks for critical Full Build 2.1 routes."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
checks={
 'backend/app/api/routes/cms.py':['/public/pages/{page_key}','/cms/pages/{page_key}/save','/cms/pages/{page_key}/publish/{version_id}'],
 'backend/app/api/routes/profile.py':['/profile/children','/profile/me-athlete'],
 'backend/app/api/routes/trainer.py':['/trainer/groups'],
 'backend/app/api/routes/admin_console.py':['/admin/console/'],
}
failed=[]
for rel,needles in checks.items():
    text=(ROOT/rel).read_text(encoding='utf-8')
    for needle in needles:
        if needle not in text: failed.append(f'{rel}: missing {needle}')
if failed:
    raise SystemExit('\n'.join(failed))
print('API contract static checks: OK')
