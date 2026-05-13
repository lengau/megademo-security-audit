#!/usr/bin/env python3
"""Fetch MegaDemo's dependency manifests from GitHub and query OSV to show the vulnerable package versions noted in the audit."""
import json
import os
import sys

import requests

PACKAGE_JSON_URL = 'https://raw.githubusercontent.com/canonical/megademo.ai/main/package.json'
PACKAGE_LOCK_URL = 'https://raw.githubusercontent.com/canonical/megademo.ai/main/package-lock.json'
TARGETS = [
    ('axios', 'direct dependency from package.json'),
    ('fast-xml-builder', 'transitive dependency from package-lock.json'),
    ('ip-address', 'transitive dependency pulled by the express-rate-limit path'),
]


def osv_lookup(name, version):
    response = requests.post(
        'https://api.osv.dev/v1/query',
        json={'package': {'name': name, 'ecosystem': 'npm'}, 'version': version},
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get('vulns', [])


def main():
    package_json = requests.get(PACKAGE_JSON_URL, timeout=30)
    package_json.raise_for_status()
    package_lock = requests.get(PACKAGE_LOCK_URL, timeout=30)
    package_lock.raise_for_status()

    pkg = package_json.json()
    lock = package_lock.json()
    packages = lock.get('packages', {})

    versions = {
        'axios': packages.get('node_modules/axios', {}).get('version') or pkg.get('dependencies', {}).get('axios'),
        'fast-xml-builder': packages.get('node_modules/fast-xml-builder', {}).get('version'),
        'express-rate-limit': packages.get('node_modules/express-rate-limit', {}).get('version') or pkg.get('dependencies', {}).get('express-rate-limit'),
        'ip-address': packages.get('node_modules/ip-address', {}).get('version'),
    }

    print('Resolved package versions:')
    for name, version in versions.items():
        print(f'  - {name}: {version}')

    advisories_found = 0
    print()
    print("OSV advisory lookups:")
    for name, reason in TARGETS:
        version = versions.get(name)
        vulns = osv_lookup(name, version) if version else []
        if vulns:
            advisories_found += 1
        print()
        print(f"{name} ({reason}) @ {version}")
        if vulns:
            for vuln in vulns[:5]:
                print(f"  - {vuln.get('id')}: {vuln.get('summary')}")
        else:
            print('  - No direct OSV entry returned for this exact version during this run.')

    print()
    print(f"express-rate-limit @ {versions['express-rate-limit']} is present, and the same lockfile also includes ip-address @ {versions['ip-address']}.")

    if advisories_found >= 2 and versions['express-rate-limit'] and versions['ip-address']:
        print()
        print("CONFIRMED: the public dependency manifests include the vulnerable packages and dependency path described in the audit.")
        return 0

    print()
    print("NOT CONFIRMED: the manifests no longer expose the vulnerable package set described in the audit.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
