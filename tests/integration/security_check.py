from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
protected=['backend/app/api/routes/admin_console.py','backend/app/api/routes/admin_sport.py','backend/app/api/routes/admin_manage.py','backend/app/api/routes/cms_blocks.py']
failed=[]
for rel in protected:
    p=ROOT/rel
    if not p.exists(): failed.append(rel+' missing'); continue
    text=p.read_text(encoding='utf-8')
    if 'require_roles("admin")' not in text and "require_roles('admin')" not in text:
        failed.append(rel+' lacks explicit admin guard')
if failed: raise SystemExit('\n'.join(failed))
print('Security static checks: OK')
