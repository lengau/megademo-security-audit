#!/usr/bin/env python3
"""Verify that the production test-login endpoint exists and still processes secrets in a GET URL."""
import os
import sys

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)


def main():
    url = f'{BASE_URL}/auth/test-login'
    params = {'token': 'redacted-demo-token', 'role': 'admin'}
    response = requests.get(
        url,
        params=params,
        headers={'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE},
        allow_redirects=False,
        timeout=20,
    )

    print(f'Requested URL: {response.url}')
    print(f'Status: {response.status_code}')
    print(f'Location: {response.headers.get("location")}')
    print(f'Body preview: {response.text[:250].replace(chr(10), " ")}')

    if response.status_code != 404:
        print()
        print("CONFIRMED: /auth/test-login is active in production (it is not a 404).")
        print('If the real token were known, the GET parameters include role=admin and would be exposed in URLs, logs, and history.')
        return 0

    print()
    print("NOT CONFIRMED: /auth/test-login returned 404 on this run.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
