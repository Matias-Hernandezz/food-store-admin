import re
from pathlib import Path
root = Path('src')
pattern = re.compile(r'import .* from ["\'](.+?)["\']')
errors = []
for p in root.rglob('*.ts*'):
    text = p.read_text(encoding='utf-8')
    for m in pattern.finditer(text):
        imp = m.group(1)
        if imp.startswith('.'):
            target = (p.parent / imp)
            if target.is_file():
                continue
            found = False
            for suffix in ['.ts', '.tsx', '.js', '.jsx']:
                if (target.with_suffix(suffix)).is_file():
                    found = True
                    break
            if found:
                continue
            for idx in ['index.ts', 'index.tsx', 'index.js', 'index.jsx']:
                if (target / idx).is_file():
                    found = True
                    break
            if not found:
                errors.append((str(p.relative_to(root)), imp, str(target)))
print('FOUND', len(errors), 'BROKEN IMPORTS')
for e in errors:
    print(*e)
