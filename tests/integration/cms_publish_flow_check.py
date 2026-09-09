from pathlib import Path
s=Path('backend/app/api/routes/cms.py').read_text(encoding='utf-8')
for token in ['/cms/pages/{page_key}/save','/cms/pages/{page_key}/publish/{version_id}','published_version_id','PageVersion']:
    assert token in s, f'CMS publish contract missing: {token}'
print('CMS save/publish/version contract: OK')
