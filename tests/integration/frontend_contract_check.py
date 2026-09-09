from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
html=(ROOT/'frontend/index.html').read_text(encoding='utf-8')
app=(ROOT/'frontend/app.js').read_text(encoding='utf-8')
required=['cms-editor.js','cms-renderer.js','admin-console.js','role-dashboard.js','trainer-tools.js','parent-tools.js','athlete-tools.js','session-guard.js','error-boundary.js']
missing=[x for x in required if x not in html]
if "const API='/api'" not in app: missing.append('API base /api')
if missing: raise SystemExit('Missing frontend contracts: '+', '.join(missing))
print('Frontend contract static checks: OK')
