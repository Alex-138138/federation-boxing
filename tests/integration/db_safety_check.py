from pathlib import Path

for name in ['deploy/update-full-build-2.1.sh','deploy/rollback-full-build-2.1.sh']:
    text=Path(name).read_text()
    forbidden=['down -v','docker volume rm','volume prune']
    for token in forbidden:
        assert token not in text, f'unsafe database operation in {name}: {token}'
update=Path('deploy/update-full-build-2.1.sh').read_text()
assert 'backup-db-full-build-2.1.sh' in update
print('database safety: OK')
