#!/usr/bin/env python3
"""Create a clearly marked draft project with only title and category to show missing server-side validation."""
import json
import os
import re
import sys
import time

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

    new_page = session.get(f'{BASE_URL}/projects/new', timeout=20)
    csrf = extract(new_page.text, r'name="_csrf" value="([^"]+)"')
    title = f'PoC-validation-test-DELETE-ME-{int(time.time())}'
    payload = {
        '_csrf': csrf,
        'title': title,
        'category': 'Coding Assistant',
        'submitAction': 'draft',
    }
    created = session.post(f'{BASE_URL}/projects', data=payload, timeout=20)
    print(f'POST /projects -> {created.status_code}')
    print(created.text[:300])

    mine = session.get(f'{BASE_URL}/projects/mine', timeout=20)
    present = title in mine.text
    print(f'Project title visible on /projects/mine: {present}')

    ok = created.status_code in {200, 302}
    redirect = None
    if 'application/json' in created.headers.get('content-type', ''):
        try:
            redirect = created.json().get('redirect')
        except ValueError:
            redirect = None
    else:
        redirect = created.headers.get('location')
    print(f'Redirect target: {redirect}')

    if ok and redirect and present:
        print()
        print("CONFIRMED: the server accepted a draft project that omitted description, team, and AI tool fields.")
        return 0

    print()
    print("NOT CONFIRMED: project creation was rejected or the draft was not visible afterwards.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
