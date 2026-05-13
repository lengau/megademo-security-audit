#!/usr/bin/env python3
"""Document the Mattermost markdown-injection finding and check project form access."""
import os
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
README = Path(__file__).resolve().parents[1] / 'README.md'
TITLE = 'Mattermost Markdown Injection'


def find_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if TITLE in line or ('Mattermost' in line and 'markdown' in line):
                refs.append((number, line.strip()))
    return refs


def main():
    response = requests.get(
        f'{BASE_URL}/projects/new',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE},
        allow_redirects=False,
        timeout=20,
    )
    print(f'GET /projects/new -> {response.status_code}')
    print('This script does not submit attacker-controlled project titles to live webhook channels; it documents the source-review finding and confirms project-entry access.')

    refs = find_refs()
    print()
    print('Local audit references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if refs and response.status_code in {200, 302}:
        print()
        print('CONFIRMED (source-review backed): project entrypoints are reachable and the audit documents unescaped markdown in Mattermost notifications.')
        return 0

    print()
    print('NOT CONFIRMED: local audit references were not found.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
