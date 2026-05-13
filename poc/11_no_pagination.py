#!/usr/bin/env python3
"""Measure the browse page and show that it returns the full project list in one response without pagination."""
import os
import sys
import time

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)


def main():
    started = time.time()
    response = requests.get(
        f'{BASE_URL}/projects',
        headers={'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE},
        timeout=30,
    )
    elapsed = time.time() - started
    size_kb = len(response.content) / 1024
    project_cards = response.text.count('class="project-card"')
    has_pagination = ('?page=' in response.text) or ('class="pagination"' in response.text.lower())

    print(f'GET /projects -> {response.status_code}')
    print(f'Response size: {size_kb:.1f} KB')
    print(f'Response time: {elapsed:.2f} s')
    print(f'Project cards in one page: {project_cards}')
    print(f'Pagination markers present: {has_pagination}')

    if response.ok and project_cards >= 300 and not has_pagination:
        print()
        print("CONFIRMED: the browse page is returning the entire corpus in a single non-paginated response.")
        return 0

    print()
    print("NOT CONFIRMED: pagination appears to be present or the single-page project count was unexpectedly low.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
