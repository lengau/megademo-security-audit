#!/usr/bin/env python3
"""Show that leaving a project you never joined still returns a success JSON response."""
import os
import re
import sys

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
CANDIDATE_SLUGS = ['testmatrixgenerate', 'anbox-test-pilot', 'lab-operator-skills']


def extract(text, pattern, flags=re.S):
    match = re.search(pattern, text, flags)
    return match.group(1) if match else None


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})

    for slug in CANDIDATE_SLUGS:
        page = session.get(f'{BASE_URL}/projects/{slug}', timeout=20)
        project_id = extract(page.text, r'data-project-id="([0-9a-f]{24})"')
        has_join = '/join' in page.text
        has_leave = '/leave' in page.text
        csrf = extract(page.text, r'name="_csrf" value="([^"]+)"') or extract(page.text, r'meta name="csrf-token" content="([^"]+)"')
        if project_id and has_join and not has_leave and csrf:
            response = session.post(
                f'{BASE_URL}/projects/{project_id}/leave',
                json={},
                headers={'x-csrf-token': csrf},
                timeout=20,
            )
            print(f'Using project slug: {slug}')
            print(f'Project id: {project_id}')
            print(f'Join visible: {has_join}; leave visible: {has_leave}')
            print(f'POST /projects/{project_id}/leave -> {response.status_code}')
            print(response.text[:250])
            if response.ok and 'success' in response.text:
                print()
                print("CONFIRMED: a non-member leave request still returned success=true.")
                return 0
            print()
            print("NOT CONFIRMED: the non-member leave request was rejected.")
            return 1

    print('NOT CONFIRMED: no project with Join visible and Leave hidden was found for a clean non-member test.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
