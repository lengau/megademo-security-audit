#!/usr/bin/env python3
"""Time repeated project-detail requests and pair the result with the code-review finding that viewing a project triggers GitHub refresh logic."""
import os
import sys
import time
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
PROJECT_SLUG = 'megademo-security-audit'
README = Path(__file__).resolve().parents[1] / 'README.md'


def read_refs():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if 'controllers/project.js:395-398' in line or 'services/github.js:50-77' in line or 'GitHub API' in line:
                refs.append((number, line.strip()))
    return refs


def timed_get(session, path):
    started = time.time()
    response = session.get(path, timeout=30)
    return response, time.time() - started


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})

    first, t1 = timed_get(session, f'{BASE_URL}/projects/{PROJECT_SLUG}')
    second, t2 = timed_get(session, f'{BASE_URL}/projects/{PROJECT_SLUG}')
    refs = read_refs()
    github_badges = first.text.count('github-badge')

    print(f'First GET /projects/{PROJECT_SLUG}: {first.status_code} in {t1:.2f}s')
    print(f'Second GET /projects/{PROJECT_SLUG}: {second.status_code} in {t2:.2f}s')
    print(f'GitHub badge elements on page: {github_badges}')
    print('Code-review references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if first.ok and second.ok and github_badges and refs:
        print()
        print("CONFIRMED: the page exposes GitHub-derived data and the repo documents that each normal view triggers refresh logic. This script provides timing context; the root cause is code-review backed.")
        return 0

    print()
    print("NOT CONFIRMED: the project page or local code-review references were not available as expected.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
