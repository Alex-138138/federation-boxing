from pathlib import Path
p=Path('backend/app/api/routes/auth.py')
assert p.exists(), 'auth route missing'
s=p.read_text(encoding='utf-8')
for token in ['/auth/request-code','/auth/verify-code']:
    assert token in s, f'missing auth endpoint {token}'
print('Auth flow contract: OK')
