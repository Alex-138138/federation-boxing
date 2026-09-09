from pathlib import Path

root=Path('frontend')
index=(root/'index.html').read_text()
app=(root/'app.js').read_text()
required=['cms-editor.js','cms-renderer.js','admin-console.js','role-dashboard.js','trainer-tools.js','parent-tools.js','athlete-tools.js']
for name in required:
    assert (root/name).exists(), f'missing {name}'
    assert f'src="/{name}"' in index, f'{name} not loaded by index'
assert "const API='/api'" in app
assert 'renderAdmin' in app and 'renderTrainer' in app and 'renderParent' in app and 'renderAthlete' in app
print('frontend JS contracts: OK')
