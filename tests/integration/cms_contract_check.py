from pathlib import Path
p=Path('backend/app/api/routes/cms.py').read_text()
required=['/public/pages/{page_key}','/cms/pages/{page_key}','/cms/pages/{page_key}/save','/cms/pages/{page_key}/publish/{version_id}','published_version_id','AuditLog']
missing=[x for x in required if x not in p]
if missing: raise SystemExit('CMS contract missing: '+', '.join(missing))
print('CMS contract: OK')
