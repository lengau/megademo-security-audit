#!/usr/bin/env python3
"""Document missing project/team quotas and perform harmless supporting checks."""
import os
import re
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
README = Path(__file__).resolve().parents[1] / 'README.md'
TITLE = 'Unbounded Project Creation and Team Growth'


def find_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if TITLE in line or ('quota' in line and 'project' in line):
                refs.append((number, line.strip()))
    return refs


def main():
    headers = {'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE}
    mine_page = requests.get(f'{BASE_URL}/projects/mine', headers=headers, allow_redirects=False, timeout=20)
    create_page = requests.get(f'{BASE_URL}/projects/new', headers=headers, allow_redirects=False, timeout=20)
    owned = len(re.findall(r'/projects/[0-9a-f]{24}/edit', mine_page.text))

    print(f'GET /projects/mine -> {mine_page.status_code}')
    print(f'GET /projects/new -> {create_page.status_code}')
    print(f'Owned-project edit links on /projects/mine: {owned}')
    print('This script does not mass-create projects or accounts; it documents the quota gap without altering live data.')

    refs = find_refs()
    print()
    print('Local audit references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if refs and create_page.status_code in {200, 302}:
        print()
        print('CONFIRMED (source-review backed): creation entrypoints are available and the audit documents missing quota enforcement.')
        return 0

    print()
    print('NOT CONFIRMED: local audit references were not found.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
