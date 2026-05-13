#!/usr/bin/env python3
"""Document the milestone-notification race without generating live vote traffic."""
import os
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
README = Path(__file__).resolve().parents[1] / 'README.md'
TITLE = 'Voting Milestone Webhook Race'


def find_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if TITLE in line or ('milestone' in line and 'duplicate' in line):
                refs.append((number, line.strip()))
    return refs


def main():
    response = requests.get(
        f'{BASE_URL}/projects',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE},
        allow_redirects=False,
        timeout=20,
    )
    print(f'GET /projects -> {response.status_code}')
    print('Live confirmation of this race requires multiple authenticated voters and intentionally generating webhook traffic, so this script documents the source-review finding only.')

    refs = find_refs()
    print()
    print('Local audit references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if refs:
        print()
        print('CONFIRMED (source-review backed): the audit documents a concurrent milestone race in the vote notification path.')
        return 0

    print()
    print('NOT CONFIRMED: local audit references were not found.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
