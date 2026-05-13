#!/usr/bin/env python3
"""Show that logo upload/edit functionality exists while noting that orphaned-file cleanup is a code-review-only finding."""
import os
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
README = Path(__file__).resolve().parents[1] / 'README.md'


def read_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if 'controllers/project.js:510-512,582-593,673-675' in line or 'Orphaned Logo Files on Replace/Delete' in line:
                refs.append((number, line.strip()))
    return refs


def main():
    response = requests.get(
        f'{BASE_URL}/projects/6a049d15c7b362fc53d740c3/edit',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE},
        timeout=20,
    )
    refs = read_refs()
    logo_input = 'name="logo"' in response.text

    print(f'GET /projects/6a049d15c7b362fc53d740c3/edit -> {response.status_code}')
    print(f'Logo upload field present: {logo_input}')
    print('Code-review references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if response.ok and logo_input and refs:
        print()
        print("CONFIRMED: the upload/edit path exists, but the orphaned-file issue itself remains a code-review-only finding because storage cannot be inspected externally from this script.")
        return 0

    print()
    print("NOT CONFIRMED: the edit form or local code-review references were not available as expected.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
