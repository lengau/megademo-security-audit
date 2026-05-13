# Proof-of-concept scripts

These scripts reproduce or validate the 32 findings from the MegaDemo security audit.

## Warning

Use these scripts **only for authorized testing** against systems you own or have permission to assess.

## Prerequisites

```bash
python3 -m pip install -r poc/requirements.txt
```

Only `requests` is required.

## Environment

By default each script uses the placeholder cookie below. To override it:

```bash
export MEGADEMO_COOKIE='connect.sid=YOUR_SESSION_COOKIE_HERE'
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
python3 poc/15_forced_team_join.py
python3 poc/16_github_oauth_login_csrf.py
# ...
python3 poc/32_ci_pipeline_no_security_scan.py
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
- `15_forced_team_join.py` - add arbitrary users to a project team without consent
- `16_github_oauth_login_csrf.py` - verify GitHub OAuth redirect omits the CSRF-protecting state value
- `17_draft_vote_idor.py` - optional draft-ID probe plus local references for the draft-project voting issue
- `18_project_email_exposure.py` - scrape a project page for exposed owner/team email addresses
- `19_uploads_no_auth.py` - fetch an uploaded asset without authentication once its URL is known
- `20_deadline_bypass.py` - documents the deadline-enforcement gap and performs harmless supporting checks
- `21_unbounded_resources.py` - documents missing project/team quotas and checks creation views
- `22_vote_milestone_race.py` - documents the concurrent milestone notification race with supporting checks
- `23_concurrent_edit_lost_update.py` - documents the lost-update issue and checks edit entrypoints
- `24_mattermost_markdown_injection.py` - documents webhook markdown injection and checks project form access
- `25_github_ssrf.py` - documents weak GitHub URL validation and checks repository-field entrypoints
- `26_user_search_redos.py` - compares short vs long authenticated user-search requests
- `27_weak_cast_id_validation.py` - documents cast-ID validation weakness and checks relevant form fields
- `28_missing_cache_control.py` - inspect authenticated pages for missing anti-cache headers
- `29_morgan_dev_logging.py` - documents production logging format via local audit references
- `30_static_assets_create_session.py` - confirm static asset responses set unnecessary session cookies
- `31_vote_endpoint_rate_limit.py` - documents missing vote-specific throttling without altering live votes
- `32_ci_pipeline_no_security_scan.py` - documents absent CI security scanning and optionally inspects a local source checkout
