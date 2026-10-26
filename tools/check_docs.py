#!/usr/bin/env python3
"""Check local Markdown file links and Bash fences; never execute the fences."""
from pathlib import Path
import re
import subprocess
import sys
import ast
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
errors = []
blocks = 0
python_blocks = 0
links = 0
for path in sorted(ROOT.rglob('*.md')):
    if '.git' in path.parts:
        continue
    text = path.read_text()
    if not text.startswith('# '):
        errors.append(f'{path.relative_to(ROOT)}: missing top-level title')
    if len(re.findall(r'^```', text, re.M)) % 2:
        errors.append(f'{path.relative_to(ROOT)}: unbalanced code fences')
    for match in re.finditer(r'```(?:bash|sh)\s*\n(.*?)```', text, re.S):
        blocks += 1
        check = subprocess.run(['bash', '-n'], input=match.group(1), text=True,
                               capture_output=True)
        if check.returncode:
            line = text[:match.start()].count('\n') + 1
            errors.append(f'{path.relative_to(ROOT)}:{line}: {check.stderr.strip()}')
    for match in re.finditer(r'```python\s*\n(.*?)```', text, re.S):
        python_blocks += 1
        try:
            ast.parse(match.group(1))
        except SyntaxError as error:
            line = text[:match.start()].count('\n') + 1
            errors.append(f'{path.relative_to(ROOT)}:{line}: {error}')
    for match in re.finditer(r'\]\(([^)]+)\)', text):
        target = match.group(1)
        if re.match(r'^[a-zA-Z]+:', target) or target.startswith('#'):
            continue
        links += 1
        target = unquote(target.split('#', 1)[0])
        if not (path.parent / target).exists():
            errors.append(f'{path.relative_to(ROOT)}: missing {target}')
print(f'Checked {blocks} Bash fences, {python_blocks} Python fences and {links} relative file links')
print('Heading fragments and external URL content are not checked by this script.')
for error in errors:
    print(error, file=sys.stderr)
sys.exit(bool(errors))
