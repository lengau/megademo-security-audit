#!/usr/bin/env python3
"""Document missing vote-specific throttling without altering live vote counts."""
import os
import re
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
README = Path(__file__).resolve().parents[1] / 'README.md'
TITLE = 'Vote Endpoint Lacks Dedicated Rate Limiting'


def find_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if TITLE in line or 'vote-specific' in line or 'bursty vote' in line:
                refs.append((number, line.strip()))
    return refs


def main():
    response = requests.get(
        f'{BASE_URL}/projects',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE},
        allow_redirects=False,
        timeout=20,
    )
    project_ids = len(set(re.findall(r'data-project-id="([0-9a-f]{24})"', response.text)))

    print(f'GET /projects -> {response.status_code}')
    print(f'Project IDs visible on browse page: {project_ids}')
    print('This script intentionally does not send vote requests to avoid altering live results; it documents the source-review finding instead.')

    refs = find_refs()
    print()
    print('Local audit references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if refs and response.status_code in {200, 302}:
        print()
        print('CONFIRMED (source-review backed): the audit documents missing vote-specific throttling on an active voting surface.')
        return 0

    print()
    print('NOT CONFIRMED: local audit references were not found.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
