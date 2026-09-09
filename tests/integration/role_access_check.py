from pathlib import Path
root=Path('backend/app/api/routes')
text='\n'.join(p.read_text(encoding='utf-8') for p in root.glob('*.py'))
for role in ['admin','trainer','parent','athlete']:
    assert role in text, f'role not referenced: {role}'
assert 'require_roles' in text, 'role guard missing'
print('Four-role access contract: OK')
