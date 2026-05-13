#!/usr/bin/env python3
"""Confirm that static asset responses mint unnecessary session cookies."""
import os
import sys

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')


def main():
    response = requests.get(
        f'{BASE_URL}/css/main.css',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0'},
        allow_redirects=False,
        timeout=20,
    )
    set_cookie = response.headers.get('set-cookie')

    print(f'GET /css/main.css -> {response.status_code}')
    print(f'Set-Cookie: {set_cookie}')
    print(f'Cache-Control: {response.headers.get("cache-control")}')

    if response.status_code == 200 and set_cookie and 'connect.sid=' in set_cookie:
        print()
        print('CONFIRMED: the static asset response created a session cookie.')
        return 0

    print()
    print('NOT CONFIRMED: the static asset response did not expose the expected session cookie behavior.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
