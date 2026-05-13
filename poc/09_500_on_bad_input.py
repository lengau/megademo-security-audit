#!/usr/bin/env python3
"""Send malformed project identifiers to endpoints that should return 400/404 but currently trigger 500 errors."""
import os
import re
import sys

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)


def extract(text, pattern, flags=re.S):
    match = re.search(pattern, text, flags)
    return match.group(1) if match else None


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})
    csrf_page = session.get(f'{BASE_URL}/projects', timeout=20)
    csrf = extract(csrf_page.text, r'meta name="csrf-token" content="([^"]+)"')

    checks = [
        ('GET', '/projects/notanid/edit', {}),
        ('POST', '/projects/notanid/vote', {'json': {'stars': 5}, 'headers': {'x-csrf-token': csrf}}),
        ('POST', '/projects/notanid/join', {'json': {}, 'headers': {'x-csrf-token': csrf}}),
    ]
    statuses = []
    for method, path, kwargs in checks:
        response = session.request(method, f'{BASE_URL}{path}', timeout=20, **kwargs)
        statuses.append(response.status_code)
        print(f'{method} {path} -> {response.status_code}')
        print(response.text[:250].replace(chr(10), ' '))
        print('')

    if statuses == [500, 500, 500]:
        print('CONFIRMED: malformed project IDs caused 500 errors instead of clean 400/404 responses.')
        return 0

    print('NOT CONFIRMED: at least one malformed-input request no longer produced a 500 response.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
