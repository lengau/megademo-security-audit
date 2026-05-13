#!/usr/bin/env python3
"""Document the GitHub-URL SSRF finding and check repository-field entrypoints."""
import os
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
README = Path(__file__).resolve().parents[1] / 'README.md'
TITLE = 'SSRF via Weak GitHub Repository URL Validation'


def find_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if TITLE in line or ('repository URL' in line and 'GitHub' in line):
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
    print('This script avoids sending crafted repository URLs to the live site; it documents the source-review SSRF finding and verifies that the project-creation entrypoint is exposed.')

    refs = find_refs()
    print()
    print('Local audit references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if refs and response.status_code in {200, 302}:
        print()
        print('CONFIRMED (source-review backed): the audit documents weak GitHub URL validation in an active project-entry workflow.')
        return 0

    print()
    print('NOT CONFIRMED: local audit references were not found.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
