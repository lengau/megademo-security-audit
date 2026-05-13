#!/usr/bin/env python3
"""Inspect authenticated pages for missing anti-cache headers."""
import os
import sys

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)


def check(path):
    response = requests.get(
        f'{BASE_URL}{path}',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE},
        allow_redirects=False,
        timeout=20,
    )
    print(f'{path} -> {response.status_code}')
    print(f'  Cache-Control: {response.headers.get("cache-control")}')
    print(f'  Pragma: {response.headers.get("pragma")}')
    print(f'  Expires: {response.headers.get("expires")}')
    return response


def main():
    projects = check('/projects')
    mine = check('/projects/mine')
    missing = all('no-store' not in (resp.headers.get('cache-control') or '') for resp in (projects, mine))

    if projects.status_code == 200 and mine.status_code == 200 and missing:
        print()
        print('CONFIRMED: authenticated pages did not send explicit no-store cache directives.')
        return 0

    print()
    print('NOT CONFIRMED: expected authenticated pages or missing anti-cache headers were not observed.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
