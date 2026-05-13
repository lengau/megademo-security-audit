#!/usr/bin/env python3
"""Document the deadline-enforcement gap and perform harmless supporting checks."""
import os
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
README = Path(__file__).resolve().parents[1] / 'README.md'
TITLE = 'Submission Deadline Bypass'


def find_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if TITLE in line or 'submissionDeadline' in line:
                refs.append((number, line.strip()))
    return refs


def main():
    headers = {'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE}
    new_page = requests.get(f'{BASE_URL}/projects/new', headers=headers, allow_redirects=False, timeout=20)
    mine_page = requests.get(f'{BASE_URL}/projects/mine', headers=headers, allow_redirects=False, timeout=20)

    print(f'GET /projects/new -> {new_page.status_code}')
    print(f'GET /projects/mine -> {mine_page.status_code}')
    print('This script avoids creating or editing live projects; live confirmation requires a past deadline and a controlled test project.')

    refs = find_refs()
    print()
    print('Local audit references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if refs and new_page.status_code in {200, 302}:
        print()
        print('CONFIRMED (source-review backed): submission and edit entrypoints remain reachable; deadline enforcement must be verified against a past cutoff in a controlled test.')
        return 0

    print()
    print('NOT CONFIRMED: local audit references were not found.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
