#!/usr/bin/env python3
"""Confirm the admin dashboard exists in production and note the code-review finding that it renders secrets in plaintext."""
import os
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
README = Path(__file__).resolve().parents[1] / 'README.md'


def find_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if 'views/admin/dashboard.pug:57-65,116-130' in line or 'Mattermost webhook URL' in line or 'test-login token' in line:
                refs.append((number, line.strip()))
    return refs


def main():
    response = requests.get(
        f'{BASE_URL}/admin',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE},
        allow_redirects=False,
        timeout=20,
    )

    print(f'GET /admin -> {response.status_code}')
    print(f'Location: {response.headers.get("location")}')
    print(f'Body preview: {response.text[:220].replace(chr(10), " ")}')

    refs = find_refs()
    print()
    print("Local audit references:")
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    exists = response.status_code in {200, 302, 403}
    if exists and refs:
        print()
        print("CONFIRMED: the /admin endpoint exists in production, and the plaintext-secret exposure remains a source-review finding documented in this repo.")
        return 0

    print()
    print("NOT CONFIRMED: the admin endpoint looked absent or the local code-review references were not found.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
