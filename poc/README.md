# Proof-of-concept scripts

These scripts reproduce or validate the 14 findings from the MegaDemo security audit.

## Warning

Use these scripts **only for authorized testing** against systems you own or have permission to assess.

## Prerequisites

```bash
python3 -m pip install -r poc/requirements.txt
```

Only `requests` is required.

## Environment

By default each script uses the test session cookie captured during the audit. To override it:

```bash
export MEGADEMO_COOKIE='connect.sid=...'
```

Optional:

```bash
export MEGADEMO_BASE_URL='https://megademo.ai'
```

## Running

Each script is standalone:

```bash
python3 poc/01_project_takeover.py
python3 poc/02_session_fixation.py
# ...
python3 poc/14_vulnerable_deps.py
```

## Included scripts

- `01_project_takeover.py` - unauthorized self-join / takeover
- `02_session_fixation.py` - session ID does not rotate
- `03_test_login_in_url.py` - production GET test-login endpoint
- `04_self_voting.py` - owner/team self-voting allowed
- `05_user_enumeration.py` - authenticated directory scraping
- `06_admin_secrets_exposure.py` - admin endpoint exists; plaintext-secret issue is code-review backed
- `07_image_beacon.py` - external markdown image rendering
- `08_missing_validation.py` - draft creation with missing required fields
- `09_500_on_bad_input.py` - malformed IDs trigger 500s
- `10_leave_non_member.py` - leave endpoint succeeds for non-members
- `11_no_pagination.py` - browse page returns all projects at once
- `12_github_api_on_view.py` - timing-based project-view check backed by source review
- `13_orphaned_logos.py` - upload/edit UI check backed by source review
- `14_vulnerable_deps.py` - dependency manifest + advisory check
