#!/usr/bin/env python3
"""Check Markdown titles, fenced-code syntax, and local links without executing examples."""
from html import unescape
from pathlib import Path
import ast
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
errors = []
blocks = 0
python_blocks = 0
links = 0
fragments = 0


def heading_slugs(text):
    """Approximate GitHub heading IDs, including duplicate-heading suffixes."""
    used = {}
    slugs = set()
    in_fence = False
    fence_char = None
    for line in text.splitlines():
        fence = re.match(r'^\s*(```+|~~~+)', line)
        if fence:
            token = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_char = token[0]
            elif token[0] == fence_char:
                in_fence = False
            continue
        if in_fence:
            continue
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*\s*$', line)
        if not match:
            continue
        title = unescape(match.group(1))
        title = re.sub(r'!?\[([^\]]+)\]\([^)]+\)', r'\1', title)
        title = re.sub(r'`([^`]*)`', r'\1', title)
        title = re.sub(r'<[^>]+>', '', title)
        title = re.sub(r'[*_~]', '', title).lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', title)
        slug = re.sub(r'\s+', '-', slug).strip('-')
        count = used.get(slug, 0)
        used[slug] = count + 1
        slugs.add(slug if count == 0 else f'{slug}-{count}')
    return slugs


for path in sorted(ROOT.rglob('*.md')):
    if '.git' in path.parts:
        continue
    text = path.read_text()
    relative = path.relative_to(ROOT)
    body = text
    if body.startswith('---\n'):
        front_matter = re.match(r'\A---\n.*?\n---\n', body, re.S)
        if front_matter:
            body = body[front_matter.end():].lstrip('\n')
        else:
            errors.append(f'{relative}: unclosed front matter')
    if not body.startswith('# '):
        errors.append(f'{relative}: missing top-level title')
    if len(re.findall(r'^```', text, re.M)) % 2:
        errors.append(f'{relative}: unbalanced code fences')

    for match in re.finditer(r'```(?:bash|sh)\s*\n(.*?)```', text, re.S):
        blocks += 1
        check = subprocess.run(['bash', '-n'], input=match.group(1), text=True,
                               capture_output=True)
        if check.returncode:
            line = text[:match.start()].count('\n') + 1
            errors.append(f'{relative}:{line}: {check.stderr.strip()}')

    for match in re.finditer(r'```python\s*\n(.*?)```', text, re.S):
        python_blocks += 1
        try:
            ast.parse(match.group(1))
        except SyntaxError as error:
            line = text[:match.start()].count('\n') + 1
            errors.append(f'{relative}:{line}: {error}')

    local_slugs = heading_slugs(text)
    for match in re.finditer(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', text):
        target = match.group(1).split()[0]
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('//'):
            continue
        links += 1
        path_part, separator, fragment = target.partition('#')
        path_part = unquote(path_part)
        destination = path if not path_part else (path.parent / path_part)
        if not destination.exists():
            errors.append(f'{relative}: missing link target {path_part}')
            continue
        if separator and fragment:
            fragments += 1
            if not destination.is_file():
                errors.append(f'{relative}: fragment target is not a file: {target}')
                continue
            target_slugs = local_slugs if destination == path else heading_slugs(destination.read_text())
            if unquote(fragment).lower() not in target_slugs:
                errors.append(f'{relative}: missing heading fragment {target}')

print(f'Checked {blocks} Bash fences, {python_blocks} Python fences, {links} local links and {fragments} heading fragments')
print('Bash fences are syntax-checked, not executed; external URL availability/content is not checked.')
for error in errors:
    print(error, file=sys.stderr)
sys.exit(bool(errors))
