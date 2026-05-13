#!/usr/bin/env python3
"""Show that MegaDemo keeps using the same session identifier across authenticated requests instead of rotating it."""
import os
import re
import sys
from urllib.parse import unquote

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)


def sid_from_cookie(cookie_value):
    decoded = unquote(cookie_value or '')
    match = re.search(r'connect\.sid=s:([^.]+)', decoded)
    return match.group(1) if match else None


def show(label, response):
    print(label)
    print(f'  status: {response.status_code}')
    print(f"  location: {response.headers.get('location')}")
    print(f"  set-cookie: {response.headers.get('set-cookie')}")


def main():
    unauth = requests.get(
        f'{BASE_URL}/auth/github',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0'},
        allow_redirects=False,
        timeout=20,
    )
    preauth_cookie = unauth.headers.get('set-cookie', '')
    preauth_sid = sid_from_cookie(preauth_cookie)

    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})
    current_sid = sid_from_cookie(COOKIE)
    auth_entry = session.get(f'{BASE_URL}/auth/github', allow_redirects=False, timeout=20)
    first = session.get(f'{BASE_URL}/projects', allow_redirects=False, timeout=20)
    second = session.get(f'{BASE_URL}/projects/mine', allow_redirects=False, timeout=20)

    show('Unauthenticated visit to /auth/github:', unauth)
    print(f'  issued pre-auth SID: {preauth_sid}')
    print('')
    show('Authenticated revisit to /auth/github with MEGADEMO_COOKIE:', auth_entry)
    print(f'  supplied authenticated SID: {current_sid}')
    print('')
    show('First authenticated request (/projects):', first)
    show('Second authenticated request (/projects/mine):', second)

    same_sid = bool(current_sid) and first.headers.get('set-cookie') is None and second.headers.get('set-cookie') is None
    if same_sid:
        print()
        print("CONFIRMED: the authenticated session ID stays the same across requests and is not rotated by the login entrypoint.")
        print('This is consistent with the session-fixation finding, although full OAuth completion is not automated here.')
        return 0

    print()
    print("NOT CONFIRMED: this run observed a session rotation or could not parse the session identifier.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
