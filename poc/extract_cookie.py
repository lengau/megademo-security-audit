#!/usr/bin/env python3
"""Extract the megademo.ai session cookie from Firefox.

Firefox stores cookies in a SQLite database (cookies.sqlite) inside the profile
directory. Since Firefox locks the DB while running, we copy it to a temp file
before reading.

Usage:
    python3 extract_cookie.py [--profile PROFILE_NAME]

If --profile is not given, searches all profiles for megademo.ai cookies.
Prints the cookie in a format ready to use with curl or as an env var.
"""

import argparse
import configparser
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path


def find_firefox_dir() -> Path:
    """Find the Firefox profiles directory."""
    candidates = [
        Path.home() / ".mozilla" / "firefox",
        Path.home() / "snap" / "firefox" / "common" / ".mozilla" / "firefox",
    ]
    for d in candidates:
        if d.is_dir():
            return d
    sys.exit("Could not find Firefox profiles directory")


def get_profiles(firefox_dir: Path) -> list[tuple[str, Path]]:
    """Return list of (profile_name, profile_path) tuples."""
    ini_path = firefox_dir / "profiles.ini"
    if not ini_path.exists():
        # Fall back to listing directories
        return [(d.name, d) for d in firefox_dir.iterdir() if d.is_dir()]

    config = configparser.ConfigParser()
    config.read(ini_path)

    profiles = []
    for section in config.sections():
        if not section.startswith("Profile"):
            continue
        name = config.get(section, "Name", fallback=section)
        path = config.get(section, "Path", fallback=None)
        is_relative = config.getboolean(section, "IsRelative", fallback=True)
        if path:
            full_path = firefox_dir / path if is_relative else Path(path)
            profiles.append((name, full_path))

    return profiles


def extract_cookie(cookies_db: Path, host: str = "megademo.ai") -> list[dict]:
    """Extract cookies for a given host from a cookies.sqlite file."""
    if not cookies_db.exists():
        return []

    # Copy DB to avoid lock issues with running Firefox
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    shutil.copy2(cookies_db, tmp_path)

    try:
        conn = sqlite3.connect(f"file:{tmp_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT name, value, host, path, expiry, isSecure, isHttpOnly
            FROM moz_cookies
            WHERE host LIKE ?
            ORDER BY name
            """,
            (f"%{host}%",),
        )
        cookies = [dict(row) for row in cursor.fetchall()]
        conn.close()
    finally:
        tmp_path.unlink(missing_ok=True)

    return cookies


def format_cookie_header(cookies: list[dict]) -> str:
    """Format cookies as a Cookie header value."""
    return "; ".join(f"{c['name']}={c['value']}" for c in cookies)


def main():
    parser = argparse.ArgumentParser(description="Extract megademo.ai cookie from Firefox")
    parser.add_argument("--profile", "-p", help="Firefox profile name to search")
    parser.add_argument("--host", default="megademo.ai", help="Host to search for (default: megademo.ai)")
    parser.add_argument("--export", "-e", action="store_true", help="Print as export statement for shell")
    args = parser.parse_args()

    firefox_dir = find_firefox_dir()
    profiles = get_profiles(firefox_dir)

    if args.profile:
        profiles = [(n, p) for n, p in profiles if args.profile.lower() in n.lower()]
        if not profiles:
            sys.exit(f"No profile matching '{args.profile}' found")

    found_any = False
    for name, path in profiles:
        cookies_db = path / "cookies.sqlite"
        cookies = extract_cookie(cookies_db, args.host)

        if not cookies:
            continue

        found_any = True
        print(f"\n{'='*60}")
        print(f"Profile: {name} ({path})")
        print(f"{'='*60}")

        # Find the session cookie specifically
        session_cookie = next((c for c in cookies if c["name"] == "connect.sid"), None)

        if session_cookie:
            value = session_cookie["value"]
            print(f"\nSession cookie (connect.sid):")
            print(f"  {value}")

            if args.export:
                print(f"\nexport MEGADEMO_COOKIE='connect.sid={value}'")
            else:
                print(f"\nFor curl:")
                print(f"  -b 'connect.sid={value}'")
                print(f"\nFor env var:")
                print(f"  export MEGADEMO_COOKIE='connect.sid={value}'")

        if len(cookies) > 1 or not session_cookie:
            print(f"\nAll cookies for {args.host}:")
            for c in cookies:
                marker = " ← session" if c["name"] == "connect.sid" else ""
                print(f"  {c['name']} = {c['value'][:50]}...{marker}" if len(c["value"]) > 50
                      else f"  {c['name']} = {c['value']}{marker}")

    if not found_any:
        print(f"No cookies found for {args.host} in any Firefox profile.")
        print("Make sure you've logged into megademo.ai in Firefox first.")
        sys.exit(1)


if __name__ == "__main__":
    main()
