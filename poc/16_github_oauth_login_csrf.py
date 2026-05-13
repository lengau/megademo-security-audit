#!/usr/bin/env python3
"""Validate that the live GitHub OAuth entrypoint omits the CSRF-protecting state parameter."""
import os
import sys
from urllib.parse import parse_qs, urlparse

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')


def main():
    response = requests.get(
        f'{BASE_URL}/auth/github',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0'},
        allow_redirects=False,
        timeout=20,
    )

    location = response.headers.get('location', '')
    parsed = urlparse(location)
    query = parse_qs(parsed.query)
    state = query.get('state')

    print(f'Status: {response.status_code}')
    print(f'Redirect host: {parsed.netloc}')
    print(f'Redirect URL: {location}')
    print(f"state present: {'yes' if state else 'no'}")

    if response.status_code in (301, 302) and parsed.netloc == 'github.com' and not state:
        print()
        print('CONFIRMED: /auth/github redirects to GitHub without a state parameter.')
        print('This leaves the OAuth login flow without the normal CSRF/login-binding check.')
        return 0

    print()
    print('NOT CONFIRMED: this run observed an unexpected redirect or a state parameter was present.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
