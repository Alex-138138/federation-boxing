from pathlib import Path
required=[
'backend/app/main.py','backend/app/api/routes/cms.py','frontend/app.js','frontend/cms-editor.js','frontend/admin-console.js',
'deploy/update-full-build-2.1.sh','deploy/backup-db-full-build-2.1.sh','deploy/verify-full-build-2.1.sh','deploy/rollback-full-build-2.1.sh'
]
missing=[p for p in required if not Path(p).exists()]
if missing: raise SystemExit('Release gate missing files: '+', '.join(missing))
print('Full Build 2.1 release gate: required files present')
