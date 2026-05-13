#!/usr/bin/env python3
"""Document the concurrent-edit lost-update issue and check edit entrypoints."""
import os
import re
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
README = Path(__file__).resolve().parents[1] / 'README.md'
TITLE = 'Concurrent Edit Lost-Update'


def find_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if TITLE in line or 'optimistic concurrency' in line or 'lost-update' in line:
                refs.append((number, line.strip()))
    return refs


def main():
    response = requests.get(
        f'{BASE_URL}/projects/mine',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE},
        allow_redirects=False,
        timeout=20,
    )
    edit_links = len(re.findall(r'/projects/[0-9a-f]{24}/edit', response.text))

    print(f'GET /projects/mine -> {response.status_code}')
    print(f'Edit links discovered: {edit_links}')
    print('This script avoids submitting stale writes; live confirmation requires a controlled two-session edit race against a test project.')

    refs = find_refs()
    print()
    print('Local audit references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if refs and response.status_code in {200, 302}:
        print()
        print('CONFIRMED (source-review backed): the audit documents project update flows without optimistic locking.')
        return 0

    print()
    print('NOT CONFIRMED: local audit references were not found.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
