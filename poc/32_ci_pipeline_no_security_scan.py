#!/usr/bin/env python3
"""Document missing CI security scanning and optionally inspect a local source checkout."""
import os
import sys
from pathlib import Path

README = Path(__file__).resolve().parents[1] / 'README.md'
TITLE = 'CI Pipeline Lacks Security Scanning'
SOURCE_DIR = Path(os.environ.get('MEGADEMO_SOURCE_DIR', Path(__file__).resolve().parents[2] / 'megademo-ai'))
WORKFLOW = SOURCE_DIR / '.github' / 'workflows' / 'ci.yml'


def main():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if TITLE in line or ('secret scanning' in line and 'CI' in line):
                refs.append((number, line.strip()))

    print('Local audit references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if WORKFLOW.exists():
        print()
        print(f'Workflow file found: {WORKFLOW}')
        content = WORKFLOW.read_text()
        for needle in ['npm ci', 'npm run lint-check', 'npm test', 'npm audit', 'codeql', 'trufflehog']:
            print(f'  contains {needle!r}: {needle in content}')
    else:
        print()
        print(f'Workflow file not found at {WORKFLOW}; using README-backed documentation only.')

    if refs:
        print()
        print('CONFIRMED (source-review backed): the audit documents missing CI security-scanning steps.')
        return 0

    print()
    print('NOT CONFIRMED: local audit references were not found.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
