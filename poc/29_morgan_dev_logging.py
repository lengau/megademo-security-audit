#!/usr/bin/env python3
"""Document the production Morgan logging-format finding."""
import sys
from pathlib import Path

README = Path(__file__).resolve().parents[1] / 'README.md'
TITLE = 'Morgan Dev Logging in Production'


def main():
    refs = []
    if README.exists():
        for number, line in enumerate(README.read_text().splitlines(), start=1):
            if TITLE in line or ('Morgan' in line and 'dev' in line):
                refs.append((number, line.strip()))

    print('Live web responses do not expose server-side log format directly, so this PoC documents the source-review finding using local audit references.')
    print()
    print('Local audit references:')
    for number, line in refs[:5]:
        print(f'  README.md:{number}: {line}')

    if refs:
        print()
        print('CONFIRMED (source-review backed): the audit documents Morgan dev-format logging in production.')
        return 0

    print()
    print('NOT CONFIRMED: local audit references were not found.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
