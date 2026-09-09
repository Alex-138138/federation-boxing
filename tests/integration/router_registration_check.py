from pathlib import Path

text=Path('backend/app/main.py').read_text()
for module in ['admin_console','admin_content','admin_sport','cms_blocks']:
    assert module in text, f'{module} router not registered'
assert 'include_router' in text
print('router registration: OK')
