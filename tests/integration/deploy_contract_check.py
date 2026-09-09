from pathlib import Path
p=Path('deploy/update-full-build-2.1.sh').read_text()
for bad in ['down -v','volume rm','docker volume rm']:
    if bad in p: raise SystemExit('Unsafe deploy command: '+bad)
for good in ['backup-db-full-build-2.1.sh','verify-full-build-2.1.sh']:
    if good not in p: raise SystemExit('Deploy contract missing: '+good)
print('Deploy contract: OK')
