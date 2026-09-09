from pathlib import Path
import py_compile

files=list(Path('backend').rglob('*.py'))
assert files, 'backend python files missing'
for path in files:
    py_compile.compile(str(path), doraise=True)
print(f'python syntax: OK ({len(files)} files)')
