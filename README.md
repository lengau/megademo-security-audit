# megademo.ai Security Audit

![Scope](https://img.shields.io/badge/scope-authenticated%20pen--test%20%2B%20source%20review-0ea5e9?style=for-the-badge)
![Findings](https://img.shields.io/badge/findings-32%20validated-111827?style=for-the-badge)
![High](https://img.shields.io/badge/high-5-dc2626?style=for-the-badge)
![Medium](https://img.shields.io/badge/medium-17-f59e0b?style=for-the-badge)
![Low](https://img.shields.io/badge/low-10-16a34a?style=for-the-badge)
![Status](https://img.shields.io/badge/disclosure-responsible-7c3aed?style=for-the-badge)

> 🚨 **From a normal user account to full project takeover:** this expanded assessment identified **32 validated vulnerabilities and issues** in megademo.ai, including a **high-severity authorization flaw** that allowed any authenticated user to join another team's non-draft project and immediately gain edit control, plus newly consolidated **high-severity deadline-bypass and SSRF findings**.

A responsible disclosure security review of the megademo.ai hackathon platform.

## Proof-of-Concept Scripts

A complete set of runnable Python PoC scripts for all 32 findings now lives in [`poc/`](poc/). They use only `requests` plus the standard library, accept the audit session cookie through `MEGADEMO_COOKIE`, and are intended only for authorized testing.

## Quick Stats

| Metric | Value |
| --- | --- |
| Findings validated | **32 findings** |
| Severity mix | **5 High · 17 Medium · 10 Low** |
| Most impressive finding | **Project takeover via unauthorized self-join** |
| Testing approach | **Authenticated penetration testing + source code review** |
| Positive control verified | **Admin privilege escalation was not possible** |

## Findings at a Glance

| Severity | Finding | Why it matters |
| --- | --- | --- |
| 🔴 **High** | **Project Takeover via Self-Join** | Any authenticated user could join another team's non-draft project and immediately gain full edit rights. |
| 🟡 **Medium** | **Session Fixation** | Login did not rotate the session ID, enabling session hijacking if an attacker could plant a known cookie first. |
| 🟡 **Medium** | **OAuth Login CSRF via Missing GitHub State** | GitHub OAuth starts without a `state` parameter, enabling account-confusion / login-CSRF attacks. |
| 🟡 **Medium** | **Test Login Token in URL** | A production test-login endpoint accepted secrets in a GET URL, increasing exposure through logs, history, and intermediaries. |
| 🟢 **Low** | **Self-Voting Allowed** | Project owners and team members could rate their own submissions, undermining judging integrity. |
| 🟡 **Medium** | **Authenticated User Enumeration (Privacy Leak)** | Authenticated user search exposed employee names and emails, including test accounts, enabling scraping and phishing. |
| 🔴 **High** | **Admin Dashboard Exposes Secrets in Plaintext** | Sensitive admin secrets were displayed directly in the dashboard, making leakage via screenshots or shared sessions easy. |
| 🟡 **Medium** | **External Image Beacons via Markdown** | Remote image embeds allowed attackers to track viewers and force external requests from project pages. |
| 🟡 **Medium** | **Missing Server-Side Validation for Required Fields** | Client-side-only validation allowed incomplete project records to be written directly to the database. |
| 🟢 **Low** | **Malformed Input Causes 500 Errors** | Invalid IDs and enum values triggered avoidable server errors instead of clean client-facing validation failures. |
| 🟢 **Low** | **Leave Succeeds for Non-Members** | Non-members received misleading success responses when attempting to leave projects they never joined. |
| 🟡 **Medium** | **No Pagination on Browse Page** | The browse page returned the full project corpus in one response, hurting performance and mobile usability. |
| 🟢 **Low** | **GitHub API Refresh Triggered on Every Project View** | Normal browsing triggered unnecessary outbound GitHub refreshes, increasing rate-limit pressure. |
| 🟢 **Low** | **Orphaned Logo Files on Replace/Delete** | Replaced and deleted project logos were left behind in storage, causing an avoidable storage leak. |
| 🔴 **High** | **Vulnerable npm Dependencies** | Several direct and transitive packages were behind known security advisories and should be upgraded. |
| 🟡 **Medium** | **Forced Team Membership Without Consent** | Project owners could add any registered user to their team without invitation or acceptance, enabling reputation manipulation. |
| 🟡 **Medium** | **IDOR Voting on Draft Projects** | Logged-in users can cast votes on draft projects if they learn the project ID. |
| 🟡 **Medium** | **Project Pages Expose Owner and Team Emails** | Any authenticated participant can harvest owner and teammate email addresses from project detail pages. |
| 🟡 **Medium** | **Uploaded Assets Accessible Without Authentication** | Files under `/uploads` remain directly reachable without login if the URL is known. |
| 🔴 **High** | **Submission Deadline Bypass** | Submission deadlines are stored but not enforced, allowing late submissions and post-cutoff edits. |
| 🟡 **Medium** | **Unbounded Project Creation and Team Growth** | No quotas limit project sprawl or oversized teams, making abuse and operational noise easy. |
| 🟡 **Medium** | **Voting Milestone Webhook Race** | Concurrent votes can trigger duplicate milestone notifications and spam downstream channels. |
| 🟡 **Medium** | **Concurrent Edit Lost-Update** | Parallel edits overwrite each other silently because project writes lack optimistic locking. |
| 🟡 **Medium** | **Mattermost Markdown Injection** | Project titles can inject markdown into webhook messages and manipulate how notifications render. |
| 🔴 **High** | **SSRF via Weak GitHub Repository URL Validation** | Loose GitHub URL validation leaves room for attacker-controlled outbound fetch targets. |
| 🟢 **Low** | **ReDoS Potential in User Search** | Very long authenticated search queries can force expensive regex work against the user collection. |
| 🟢 **Low** | **Weak Asciinema Cast ID Validation** | The cast ID parser accepts untrusted strings more broadly than intended. |
| 🟡 **Medium** | **Missing Cache-Control on Authenticated Pages** | Sensitive dynamic pages do not instruct browsers or proxies not to cache user-specific responses. |
| 🟢 **Low** | **Morgan Dev Logging in Production** | Production logging uses the verbose development format instead of a safer structured format. |
| 🟢 **Low** | **Static Asset Requests Create Sessions** | CSS, JS, and image requests can mint unnecessary session cookies and session-store entries. |
| 🟡 **Medium** | **Vote Endpoint Lacks Dedicated Rate Limiting** | Authenticated users can script large numbers of vote requests because only the global limiter applies. |
| 🟢 **Low** | **CI Pipeline Lacks Security Scanning** | CI does not run dependency, SAST, or secret-scanning checks before changes are merged. |
| 🔵 **Info** | **Admin Escalation Not Possible** | Server-side role checks on `/admin` held up under testing and bypass attempts failed. |

## Executive Summary

This report documents security, privacy, business-logic, injection, and operational findings identified during authenticated testing and source review performed with permission on megademo.ai. The most serious issue remains a **high-severity project takeover vulnerability** that allows any authenticated user to join any non-draft project and immediately gain full edit rights. Newly consolidated findings also include a **high-severity submission deadline bypass** and **high-severity SSRF potential in GitHub repository URL handling**, plus additional issues affecting **draft voting, email privacy, unauthenticated asset access, webhook integrity, cache behavior, rate limiting, concurrency safety, and CI/CD hygiene**.

The assessment also confirmed an important positive control: **admin privilege escalation was not possible** during testing. Administrative routes correctly enforce authorization using the database-backed role check.

## Methodology

Testing was performed using an authenticated user session with permission to assess the application. The review focused on:

- Project membership and authorization flows
- Authentication and session handling
- Administrative access controls and secret handling
- Input validation, error handling, and voting behavior
- Privacy exposure, content rendering, and operational/performance issues
- Dependency review for known vulnerable packages

The testing approach was manual and behavior-driven, using normal application requests and direct HTTP requests to verify authorization, session management, privacy exposure, and validation behavior, supported by source review to confirm impact and likely root causes.

## Findings Summary

| Severity | Title | Description | Reproduction Steps | Recommendation |
| --- | --- | --- | --- | --- |
| HIGH | Project Takeover via Self-Join | Any authenticated user can POST `/projects/:id/join` on any non-draft project and gains full edit rights without ownership or invitation checks. | Log in as a normal user, send `POST /projects/:id/join` for another team's non-draft project, then edit that project's details. | Restrict joins to explicit invitations, ownership-approved membership changes, or validated team workflows; enforce authorization server-side before membership changes. |
| MEDIUM | Session Fixation | Login does not regenerate the session ID after authentication, allowing an attacker who can pre-set a victim's cookie to hijack the authenticated session. | Obtain or set a victim browser session ID, have the victim authenticate, and observe that the session ID remains unchanged and becomes authenticated. | Regenerate the session identifier immediately after successful login and invalidate any prior unauthenticated session. |
| MEDIUM | OAuth Login CSRF via Missing GitHub State | `/auth/github` starts OAuth without a `state` parameter and `/auth/github/callback` performs no state verification, enabling account-confusion attacks. | Request `/auth/github` and observe that the GitHub redirect lacks `state`. Complete GitHub auth as the attacker, send the resulting callback URL to a victim, and observe the victim browser establish a session for the attacker's account. | Enable OAuth state handling on the GitHub strategy and reject callbacks that do not match the stored state. |
| MEDIUM | Test Login Token in URL (GET parameter) | `/auth/test-login?token=...&role=admin` is active in production, exposing the token in URLs, logs, browser history, and proxies. | Visit `/auth/test-login?token=...&role=admin` and note that the token is processed via GET and appears in request logs and history. | Disable the endpoint in production; if retained for non-production use, require POST and additional environment gating. |
| LOW | Self-Voting Allowed | Users can vote 5 stars on their own projects because ownership/team membership is not checked before accepting votes. | Log in as a project owner or team member and submit a vote for that same project. | Reject votes from project owners and team members server-side. |
| MEDIUM | Authenticated User Enumeration (Privacy Leak) | `GET /api/users/search?q=al` returns employee names and emails, including test accounts, without authenticated rate-limit protection. | Query `/api/users/search?q=al` while authenticated and observe employee names, emails, and test/local accounts in the response. | Restrict endpoint access, add rate limiting, and filter test/local accounts from search results. |
| HIGH | Admin Dashboard Exposes Secrets in Plaintext | The admin dashboard renders the Mattermost webhook URL and test-login token directly in the page. | Sign in as an admin, open the dashboard, and observe the webhook URL and test-login token displayed in plaintext. | Mask secrets by default and reveal them only on explicit demand with an intentional interaction. |
| MEDIUM | External Image Beacons via Markdown | Markdown sanitization allows remote image URLs and `<img>` tags, enabling tracking beacons in project content. | Add markdown containing an external image, load the project detail page from another browser, and observe the external image request firing. | Disallow image tags entirely or proxy/allowlist remote image hosts. |
| MEDIUM | Missing Server-Side Validation for Required Fields | The server accepts project creation requests missing required fields that are enforced only by the client UI. | Submit a draft creation request containing only a title and category, and observe that description, team, and AI tools are not required server-side. | Enforce schema validation in the controller before writing to the database. |
| LOW | Malformed Input Causes 500 Errors | Invalid ObjectIds and bogus `completionStage` values produce 500 errors instead of 400/404 responses. | Request endpoints such as `GET /projects/notanid/edit` or `POST /projects/notanid/vote` and observe a 500 response. | Validate ObjectIds and enum values before database access and return 400/404 for invalid inputs. |
| LOW | Leave Succeeds for Non-Members | `POST /projects/:id/leave` returns `{"success":true}` even when the requester is not on the team. | Call the leave endpoint for a project the authenticated user never joined and observe a success response. | Check membership before processing the leave and return an error for non-members. |
| MEDIUM | No Pagination on Browse Page | The browse page loads roughly 376 projects in a single ~327 KB response, increasing load time and memory usage. | Open the browse page and observe that all projects are rendered in a single response without pagination or incremental loading. | Implement pagination or infinite scroll to limit per-request payload size. |
| LOW | GitHub API Refresh Triggered on Every Project View | Viewing a project triggers outbound GitHub API refresh logic during normal browsing. | Load a project detail page repeatedly and observe repository refresh calls being initiated from the view path. | Move refreshes to a background job and add per-project throttling. |
| LOW | Orphaned Logo Files on Replace/Delete | Replacing project logos or deleting projects leaves prior logo files behind in storage. | Replace a logo or delete a project, then inspect storage and observe that the old logo file remains. | Delete superseded logo files during replace, remove, and project-delete flows. |
| HIGH | Vulnerable npm Dependencies | The project includes vulnerable versions of `axios`, `fast-xml-builder`, and moderate-risk `express-rate-limit` / `ip-address` dependency paths. | Review `package.json` / lockfile entries or run dependency audit tooling and observe reported advisories for the listed packages. | Upgrade direct and transitive dependencies to patched versions and re-run audit checks. |
| MEDIUM | Forced Team Membership Without Consent | Project owners can add any registered user to their team via `POST /projects/:id/team` with no invitation or acceptance flow. | Search for a user's email via `/api/users/search`, then POST their email to `/projects/:id/team` and observe them added without consent. | Implement an invitation/acceptance flow requiring explicit consent before listing someone as a team member. |
| MEDIUM | IDOR Voting on Draft Projects | The vote endpoint accepts votes for draft projects when a logged-in user knows the project ID because visibility checks are missing. | Obtain a draft project ID, POST `/projects/:id/vote` with a valid session and CSRF token, and observe a normal vote response instead of 403/404. | Require projects to be viewable and vote-eligible before accepting votes; reject draft voting for non-team members or entirely. |
| MEDIUM | Project Pages Expose Owner and Team Emails | Project detail views populate and render owner/team email addresses to any authenticated participant. | Log in as a normal user, open another team's submitted or finalist project page, and observe owner/team email addresses in the rendered page. | Expose emails only to authorized team-management contexts and omit them from general project browsing. |
| MEDIUM | Uploaded Assets Accessible Without Authentication | The `/uploads` static route is registered before the production auth gate, so uploaded files are publicly reachable if their URLs leak. | Find an `/uploads/...` asset URL while authenticated, then request it again from a logged-out browser and observe a 200 response. | Move upload serving behind authentication if assets are private, or separate truly public assets from sensitive uploaded content. |
| HIGH | Submission Deadline Bypass | `submissionDeadline` is configurable but not enforced during project submission or later edits, allowing post-deadline changes. | Set the deadline to a past time, submit a draft after cutoff, and edit a submitted/finalist project after the deadline; both actions still succeed. | Enforce the deadline server-side in create, submit, and update flows, with explicit admin override paths if needed. |
| MEDIUM | Unbounded Project Creation and Team Growth | The application does not cap projects per user or members per project, enabling resource abuse and platform noise. | Repeatedly create projects or add/join team members and observe no quota or size limit being enforced. | Add hard quotas, write throttles, and abuse monitoring for project creation and team growth. |
| MEDIUM | Voting Milestone Webhook Race | Milestone notifications use stale pre-update vote counts, so concurrent threshold-crossing votes can emit duplicate webhook messages. | Bring a project near a milestone, send concurrent votes from multiple accounts, and observe duplicate Mattermost milestone posts. | Make milestone emission idempotent with an atomic check-and-set or deduplicated job queue. |
| MEDIUM | Concurrent Edit Lost-Update | Project updates load, mutate, and save full documents without optimistic locking, so stale writes can overwrite newer changes. | Open the same project edit view in two sessions, submit different changes from each, and observe one user's changes disappear silently. | Enable optimistic concurrency or switch to atomic field-level updates with conflict detection. |
| MEDIUM | Mattermost Markdown Injection | Mattermost webhook messages interpolate project titles and descriptions into markdown without escaping. | Create or rename a project using markdown control characters, submit or update it, and observe manipulated formatting in the Mattermost message. | Escape markdown metacharacters before building webhook text or use a structured message format. |
| HIGH | SSRF via Weak GitHub Repository URL Validation | GitHub repository URLs are parsed with a loose regex that does not strictly validate hostname and owner/repo structure before outbound fetch logic runs. | Supply a crafted repository URL containing confusing `github.com` placement or malformed path components, trigger the GitHub refresh path, and observe the value is accepted instead of rejected. | Parse URLs with a real URL parser, require the exact GitHub hostname, and strictly validate `[owner]/[repo]` components before any outbound request. |
| LOW | ReDoS Potential in User Search | Authenticated user search builds a regex from user input and runs it against user fields, so very long queries can create avoidable performance pressure. | Send very long `q` values to `/api/users/search` while authenticated and measure the endpoint processing those regex searches. | Cap query length aggressively, use prefix/index-backed search, and rate limit authenticated search traffic. |
| LOW | Weak Asciinema Cast ID Validation | The cast ID parser returns trimmed arbitrary input when the expected URL format is not matched, weakening input validation. | Submit malformed or non-numeric cast identifiers and observe they are accepted into the stored project data path. | Accept only a strict allowlisted cast ID format and reject anything else. |
| MEDIUM | Missing Cache-Control on Authenticated Pages | Sensitive authenticated pages do not set explicit `Cache-Control`, `Pragma`, or `Expires` headers. | Visit pages such as `/projects` or `/projects/mine` while logged in and inspect the response headers for missing no-store directives. | Add cache-busting headers to authenticated dynamic responses. |
| LOW | Morgan Dev Logging in Production | Production uses Morgan's `dev` format, which is verbose and less suitable for secure log aggregation. | Review the production logging configuration or live logs and observe colorized `dev`-format request lines. | Switch to an environment-aware structured or combined production log format. |
| LOW | Static Asset Requests Create Sessions | Session middleware runs before static asset handlers, so anonymous asset requests can still receive a `connect.sid` cookie. | Request a static asset such as `/css/main.css` without a session and observe a `Set-Cookie` header for the session. | Serve static assets before session middleware or skip session creation for static paths. |
| MEDIUM | Vote Endpoint Lacks Dedicated Rate Limiting | `/projects/:id/vote` relies only on the global limiter, allowing a logged-in user to send many vote-related requests in a short window. | Script repeated vote requests across multiple project IDs and observe no vote-specific throttling or block condition beyond the global limit. | Add a dedicated low-threshold vote limiter and alert on bursty voting behavior. |
| LOW | CI Pipeline Lacks Security Scanning | The CI workflow runs install, lint, and tests but does not run dependency audit, SAST, or secret-scanning steps. | Review the CI workflow definition and observe the absence of security scanning jobs. | Add dependency auditing, SAST, and secret scanning to CI before merges. |
| INFO | Admin Escalation Not Possible (good) | Admin middleware checks the database-stored role on each request; `/admin` routes return 403 for non-admins, and tested bypasses failed. | Attempt admin access as a non-admin via parameter pollution, cookie tampering, and OIDC role selection; observe 403 responses or ignored input. | Maintain the current authorization model and continue validating admin checks against the persisted server-side role. |

## Findings

### HIGH - Project Takeover via Self-Join

**Affected behavior:** Any authenticated user can join any non-draft project.

**Description**

The endpoint `POST /projects/:id/join` accepts membership requests from any authenticated user for any project that is not in draft state. On success, the user is added as a project member and immediately receives full edit permissions over the project, including the ability to modify descriptions, media, and team membership.

No ownership, invitation, or approval check is performed before granting access.

**Impact**

This creates a direct project takeover and sabotage risk. Any participant can alter or damage another team's submission, misrepresent ownership, or disrupt judging.

**Reproduction Steps**

1. Authenticate as a normal user.
2. Identify the ID of a non-draft project owned by another team.
3. Send a `POST` request to `/projects/:id/join` for that project.
4. Open the project editing interface or submit update requests.
5. Observe that the user now has full edit rights over the other team's project.

**Recommendation**

Require explicit authorization for joining a project. Suitable mitigations include invitation tokens, owner-approved join requests, or a server-side workflow that limits who may become a member. Edit permissions should be granted only after a validated membership transition.

---

### MEDIUM - Session Fixation

**Affected behavior:** Successful login does not regenerate the session ID.

**Description**

After authentication, the application continues using the same pre-authentication session identifier rather than issuing a fresh session. If an attacker can cause a victim browser to use a known session cookie before login—for example through a related subdomain, browser injection, or XSS elsewhere—the attacker may be able to reuse that same session after the victim authenticates.

**Impact**

This enables session fixation and possible account hijacking if an attacker can plant or predict the victim's session identifier before login.

**Reproduction Steps**

1. Establish or set a known unauthenticated session cookie in the victim browser.
2. Have the victim authenticate normally.
3. Observe that the session ID is not regenerated after login.
4. Reuse the fixed session cookie and confirm it now represents the victim's authenticated session.

**Recommendation**

Regenerate the session ID immediately after successful authentication and ensure any old session state is invalidated. Review the login flow for all authentication methods, including OIDC and test helpers.

---

### MEDIUM - OAuth Login CSRF via Missing GitHub State

**Location:** `controllers/auth.js:78-94`, `app.js:349-350`

**Description**

The GitHub OAuth flow is started with `passport.authenticate('github', { scope: [...] })` but does not enable Passport's `state` protection. Live testing confirmed that `GET /auth/github` redirects to GitHub without any `state=` parameter in the authorization URL, and the callback handler accepts the returned code without checking a stored state value.

This creates a classic login-CSRF / account-confusion condition: an attacker can authenticate to GitHub with their own account, capture the resulting MegaDemo callback URL, and trick a victim browser into visiting it. Because there is no state binding between the OAuth initiation request and the callback, the victim can end up signed into the attacker's MegaDemo account.

**Impact**

Victims can unknowingly perform actions under an attacker-controlled account, leading to project edits, votes, or team-management actions being attributed to the wrong identity. It also weakens the application's cross-site request forgery defenses around the authentication boundary.

**Reproduction Steps**

1. Request `GET /auth/github` and inspect the `Location` header.
2. Observe that the GitHub authorization URL does **not** contain a `state` parameter.
3. Complete the GitHub OAuth flow as the attacker and capture the resulting `/auth/github/callback?code=...` URL.
4. Cause a victim browser to request that callback URL.
5. Observe that the victim is logged into the attacker's MegaDemo account because no per-session state value is validated.

**Recommendation**

Enable state handling for the GitHub OAuth strategy (for example `passport.authenticate('github', { scope: [...], state: true })` or an equivalent custom state store), persist the state server-side, and reject any callback whose `state` does not exactly match the stored value. Add a regression test that asserts the outbound GitHub redirect contains `state=`.

---

### MEDIUM - Test Login Token in URL (GET parameter)

**Affected behavior:** `/auth/test-login?token=...&role=admin` is available in production and accepts secrets in the query string.

**Description**

The application exposes a test login endpoint in production that accepts a token and role through URL query parameters. Because the endpoint uses GET, the sensitive token may be written to server logs, browser history, monitoring systems, analytics tools, and intermediary proxies.

If the token is disclosed, an attacker can create an administrative session using a simple GET request.

**Impact**

Exposure of the token enables unauthorized account creation or elevation to admin through a low-friction request. Even if the token is intended to be secret, URL transport materially increases leakage risk.

**Reproduction Steps**

1. Make a request to `/auth/test-login?token=...&role=admin`.
2. Observe that the request succeeds via GET.
3. Confirm that the token is present in the requested URL, making it visible to logs, history, and intermediaries.
4. If the token is known, observe that a valid admin session can be created.

**Recommendation**

Disable the endpoint in production entirely. If a non-production helper is still required, restrict it by environment, remove role selection, require POST, and treat the token as a secret that must never appear in URLs.

---

### LOW - Self-Voting Allowed

**Affected behavior:** Users can rate their own projects.

**Description**

The voting flow accepts ratings from a project's owner or team members without checking whether the voter is affiliated with the project.

**Impact**

This undermines scoring integrity and can unfairly influence rankings, though the impact is limited compared to direct authorization vulnerabilities.

**Reproduction Steps**

1. Log in as the owner or a team member of a project.
2. Submit a 5-star vote for that same project.
3. Observe that the vote is accepted.

**Recommendation**

Reject votes from project owners and team members on the server side. Consider recording and alerting on attempts to self-vote.

---

### MEDIUM - Authenticated User Enumeration (Privacy Leak)

**Location:** `controllers/project.js:746-753`, `app.js:241-247`

**Description**

The authenticated endpoint `GET /api/users/search?q=al` returns employee names and email addresses, including test accounts such as `test-participant@megademo-test.local`. The route does not emit rate-limit headers for authenticated requests, making bulk scraping easier for any logged-in user.

**Impact**

This is a privacy leak that enables user enumeration, targeted phishing, and internal-directory scraping with very little friction.

**Reproduction Steps**

1. Authenticate as a normal user.
2. Request `GET /api/users/search?q=al`.
3. Observe that the response contains employee names, email addresses, and test/local accounts.
4. Repeat requests and note the absence of authenticated rate-limit signals or controls.

**Recommendation**

Restrict access to the endpoint, apply rate limiting to authenticated requests, and filter test/local accounts from the returned results.

---

### HIGH - Admin Dashboard Exposes Secrets in Plaintext

**Location:** `controllers/admin.js:104-123`, `views/admin/dashboard.pug:57-65,116-130`

**Description**

The admin dashboard renders sensitive values directly into the page, including the Mattermost webhook URL and the test-login token. Anyone viewing the page can immediately read or copy those secrets without an explicit reveal step.

**Impact**

Plaintext secret exposure creates leakage risk through screenshots, screen sharing, shoulder surfing, cached browser content, and overly broad admin access.

**Reproduction Steps**

1. Authenticate as an administrative user.
2. Open the admin dashboard.
3. Observe that the Mattermost webhook URL and test-login token are displayed in plaintext.
4. Confirm they are visible without any deliberate reveal interaction.

**Recommendation**

Mask secrets by default and require explicit user interaction to reveal them only when needed. Limit display to the minimum necessary audience and action.

---

### MEDIUM - External Image Beacons via Markdown

**Location:** `models/Project.js:5-8,115-116`, `views/projects/detail.pug:68-70`

**Description**

Markdown sanitization currently permits remote image URLs and external `<img>` tags in project content. An attacker can embed a tracking beacon so that every viewer of the project page causes a request to an attacker-controlled host.

**Impact**

This leaks viewer IP addresses and user-agent data to third parties and can also degrade page performance when external image hosts are slow or malicious.

**Reproduction Steps**

1. Create or edit project content to include a remote image or `<img>` tag.
2. Save the content and open the project detail page from another browser or account.
3. Observe an outbound request to the attacker-controlled image host when the page renders.
4. Confirm the remote host receives viewer metadata such as IP address and user-agent.

**Recommendation**

Disallow image tags in markdown entirely or proxy and allowlist approved image hosts before rendering remote content.

---

### MEDIUM - Missing Server-Side Validation for Required Fields

**Location:** `controllers/project.js:278-317`; client-only enforcement in `views/projects/new.pug`

**Description**

The project creation flow relies on client-side enforcement for required fields such as description, team, and AI tools. Direct requests to the controller can bypass the browser checks and create draft records with only a title and category.

**Impact**

This allows incomplete or invalid project records into the database, increasing data-quality issues and creating inconsistent application behavior.

**Reproduction Steps**

1. Open the new-project form and note that the browser UI requires multiple fields.
2. Send a direct project creation request containing only a title and category.
3. Observe that the draft is created successfully despite missing required fields.
4. Confirm the incomplete record is persisted in the database.

**Recommendation**

Enforce schema validation in the controller before database writes so required fields are validated server-side regardless of client behavior.

---

### LOW - Malformed Input Causes 500 Errors

**Location:** `controllers/project.js:413-415,437,613,714,773,799`

**Description**

Several endpoints pass unvalidated ObjectIds and enum-like parameters directly into downstream logic. Inputs such as invalid project IDs or bogus `completionStage` values trigger unhandled server-side failures that surface as `500 Internal Server Error`.

**Impact**

The issue creates poor user experience, noisy logs, and an easy way for bots or curious users to generate avoidable error traffic.

**Reproduction Steps**

1. Request `GET /projects/notanid/edit`.
2. Submit `POST /projects/notanid/vote`.
3. Send requests with invalid `completionStage` values where applicable.
4. Observe `500` responses instead of clean `400` or `404` validation failures.

**Recommendation**

Validate ObjectIds and allowed enum values before database calls and return `400` or `404` responses for malformed input.

---

### LOW - Leave Succeeds for Non-Members

**Location:** `controllers/project.js:797-809`

**Description**

The leave endpoint returns `{"success":true}` even when the authenticated user is not actually a member of the project team. The response does not reflect whether any membership change occurred.

**Impact**

This produces misleading UI state and inconsistent behavior that can confuse users and make automation harder to reason about.

**Reproduction Steps**

1. Authenticate as a user who is not on the target project's team.
2. Submit `POST /projects/:id/leave` for that project.
3. Observe a success response.
4. Confirm that no membership existed to remove.

**Recommendation**

Check membership before processing the leave request and return an error when the user is not actually a project member.

---

### MEDIUM - No Pagination on Browse Page

**Location:** `controllers/project.js:195-234`, `views/projects/list.pug:5-26`

**Description**

The browse page loads the entire project set in a single response. During testing this meant roughly 376 projects, about 327 KB transferred, and approximately 2.6 seconds of load time for one page request.

**Impact**

Loading the full corpus at once slows page loads, worsens the mobile experience, and increases server memory and rendering costs.

**Reproduction Steps**

1. Open the browse page.
2. Observe that all available projects are returned in a single response.
3. Measure the payload size and page load time.
4. Confirm that no pagination or incremental loading is applied.

**Recommendation**

Implement pagination or infinite scroll so each request handles a smaller, bounded subset of projects.

---

### LOW - GitHub API Refresh Triggered on Every Project View

**Location:** `controllers/project.js:395-398`, `services/github.js:50-77`

**Description**

Viewing a project detail page triggers outbound GitHub API calls to refresh repository data. This happens as part of normal browsing rather than a background synchronization workflow.

**Impact**

Routine page views create unnecessary API traffic and increase pressure on rate limits without corresponding user benefit.

**Reproduction Steps**

1. Open a project detail page with a linked repository.
2. Refresh the page multiple times.
3. Observe that repository refresh logic runs on each view.
4. Confirm the behavior generates outbound GitHub API activity from normal browsing.

**Recommendation**

Move repository refreshes to a background cron job or queue and add per-project throttling to avoid repeated refreshes during normal page views.

---

### LOW - Orphaned Logo Files on Replace/Delete

**Location:** `controllers/project.js:510-512,582-593,673-675`

**Description**

When a project logo is replaced or a project is deleted, the previously stored logo file is not unlinked from storage. The application only updates references, leaving obsolete files behind.

**Impact**

This creates a storage leak that grows over time and wastes disk or object-storage capacity.

**Reproduction Steps**

1. Upload a project logo.
2. Replace it with a new logo or delete the project entirely.
3. Inspect storage after the operation.
4. Observe that the old logo file remains present.

**Recommendation**

Delete superseded logo files during logo replacement, explicit logo removal, and project deletion flows.

---

### HIGH - Vulnerable npm Dependencies

**Location:** `package.json:19`, lockfile transitive dependencies

**Description**

Dependency review identified a high-severity advisory affecting `axios`, a high-severity advisory affecting transitive `fast-xml-builder`, and moderate-risk issues in the `express-rate-limit` / `ip-address` dependency path. These packages should be upgraded to patched versions.

**Impact**

Known vulnerable dependencies expand the application's attack surface and can expose the project to publicly documented exploit paths.

**Reproduction Steps**

1. Inspect `package.json` and the lockfile.
2. Run dependency audit tooling against the installed package set.
3. Observe advisories for `axios`, `fast-xml-builder`, and the `express-rate-limit` / `ip-address` chain.
4. Confirm the affected versions are below patched releases.

**Recommendation**

Upgrade direct and transitive dependencies to patched versions and re-run audit checks to confirm remediation.

---

### MEDIUM - Forced Team Membership Without Consent

**Location:** `controllers/project.js:713-730`

**Description**

Project owners can add any registered user to their project team by POSTing their email to `/projects/:id/team`. There is no invitation flow, acceptance step, or notification to the target user. Combined with the user enumeration endpoint (finding #5), an attacker can discover anyone's email and immediately force them onto a project.

**Impact**

Reputation and attribution manipulation. A malicious project owner could list respected engineers as "team members" to imply endorsement or involvement in their project. The victim has no way to know they've been added unless they check the project page directly.

**Reproduction Steps**

1. Authenticate as any user who owns a project.
2. Use `GET /api/users/search?q=<name>` to find the target's email.
3. `POST /projects/:id/team` with `{"addEmail": "victim@canonical.com"}` and CSRF token.
4. Observe the target is now listed as a team member without any consent.

**Recommendation**

Implement an invitation/acceptance flow: the target user should receive a notification and must explicitly accept before being listed as a team member.

---

### MEDIUM - IDOR Voting on Draft Projects

**Location:** `controllers/project.js:613-639`

**Description**

`POST /projects/:id/vote` accepts a project ID and records a vote without checking whether the caller is allowed to view or vote on that project. Other flows already treat draft projects as non-public, but the vote path does not apply the same visibility rule.

A logged-in user who learns a draft project's Mongo ObjectId can therefore cast or overwrite a vote on a project that should remain hidden from them.

**Impact**

This weakens draft confidentiality and judging integrity. It also creates an existence oracle for hidden drafts because a valid draft ID produces normal vote behavior rather than a clean authorization failure.

**Reproduction Steps**

1. Authenticate as a normal user who is not on the target draft project.
2. Obtain the draft project's ObjectId from a leak, log, browser history entry, or other source.
3. Send `POST /projects/:id/vote` with a valid CSRF token and rating.
4. Observe that the request is processed instead of rejected as unauthorized.

**Recommendation**

Centralize visibility and vote-eligibility checks so the vote handler rejects draft projects for non-team members, or rejects draft voting entirely.

---

### MEDIUM - Project Pages Expose Owner and Team Emails

**Location:** `controllers/project.js:359-409`

**Description**

The project detail route populates `owner` and `team` records with `email` alongside profile names and pictures, then renders those objects into the project page. Because any authenticated participant can browse submitted and finalist projects, any logged-in user can harvest owner and teammate email addresses from other teams.

**Impact**

This is a privacy and social-engineering issue. It exposes personal contact details beyond what is necessary for normal project browsing and makes targeted phishing/spam easier.

**Reproduction Steps**

1. Authenticate as any normal participant.
2. Open another team's submitted or finalist project page.
3. Inspect the rendered page or source.
4. Observe owner/team email addresses present for users who are not on that project.

**Recommendation**

Remove email addresses from general project-detail rendering. If they are needed for team management, return them only to authorized editors/admins via a separate privileged path.

---

### MEDIUM - Uploaded Assets Accessible Without Authentication

**Location:** `app.js:320-350`

**Description**

The static `/uploads` route is registered before the production authentication gate. As a result, uploaded logos and related assets remain directly fetchable without authentication whenever the URL is known.

This is distinct from the orphaned-file issue: even non-orphaned, currently referenced uploads can be fetched anonymously if their paths leak.

**Impact**

Draft/private project media can become accessible outside the authenticated application boundary. This weakens access control and increases the blast radius of any leaked asset URL.

**Reproduction Steps**

1. While authenticated, obtain an uploaded asset URL such as `/uploads/<filename>` from a project page.
2. Open a logged-out browser or send an unauthenticated request for that URL.
3. Observe that the asset still returns `200 OK`.

**Recommendation**

If uploads are intended to be private, move `/uploads` behind authentication or a signed-URL mechanism. If they are intentionally public, document that choice explicitly and keep sensitive assets out of that path.

---

### HIGH - Submission Deadline Bypass

**Location:** `controllers/project.js:263-358,436-577`; `controllers/admin.js:344-387`

**Description**

The application stores a configurable `submissionDeadline`, but the project submission and update flows do not enforce it. Participants can submit drafts after the deadline and continue making material edits to submitted/finalist projects after the judging cutoff should have passed.

**Impact**

This undermines hackathon fairness and trust. Teams can improve projects after the official deadline, and judges may evaluate submissions that changed after the cutoff.

**Reproduction Steps**

1. Configure `submissionDeadline` to a timestamp in the past.
2. Submit a draft project after the cutoff time.
3. Edit a submitted or finalist project after the deadline.
4. Observe that the server accepts the changes.

**Recommendation**

Enforce deadlines server-side on create, submit, and update paths. Lock or narrowly restrict post-deadline fields, with explicit admin override workflows for exceptions.

---

### MEDIUM - Unbounded Project Creation and Team Growth

**Location:** `controllers/project.js:263-358,713-737,771-787`; `models/Project.js:61`

**Description**

There is no quota on how many projects a user may create and no hard cap on how large a project team may become. A single participant or coordinated group can create excessive project records, grow oversized teams, and generate operational clutter with little friction.

**Impact**

This increases storage and moderation burden, degrades UX, and expands abuse potential during a time-sensitive event.

**Reproduction Steps**

1. Authenticate as a normal user.
2. Repeatedly create new projects.
3. Repeatedly join a project from multiple accounts or add users as the owner.
4. Observe that no quota or size limit is enforced.

**Recommendation**

Add project-per-user and members-per-project limits, plus write throttles and abuse monitoring around project creation and team management.

---

### MEDIUM - Voting Milestone Webhook Race

**Location:** `controllers/project.js:616-639`; `services/mattermost.js:71-79`

**Description**

Vote milestone notifications compare the previous vote count from a stale pre-update read against the new post-vote count. When multiple votes arrive concurrently near the same milestone threshold, more than one request can conclude that it crossed the threshold and each can emit the Mattermost notification.

**Impact**

This causes duplicate milestone messages, noisy downstream channels, and unreliable operational signaling.

**Reproduction Steps**

1. Bring a project near a milestone threshold such as 5 votes.
2. Submit multiple concurrent votes from different accounts.
3. Observe duplicate milestone notifications for the same threshold crossing.

**Recommendation**

Make milestone emission idempotent by storing which milestones have already fired, or emit notifications through a deduplicated background queue.

---

### MEDIUM - Concurrent Edit Lost-Update

**Location:** `controllers/project.js:436-577,652-707,713-737`

**Description**

Project update flows load documents, mutate them in memory, and save them back without optimistic locking or version checks. If two sessions edit the same project concurrently, a later stale save can silently overwrite earlier changes.

**Impact**

Users can lose data without warning, and malicious or accidental racing updates can overwrite important project content.

**Reproduction Steps**

1. Open the same project edit view in two sessions.
2. Submit a change from session A.
3. Submit a different change from session B using the stale form.
4. Observe that one change can overwrite or erase the other without a conflict warning.

**Recommendation**

Enable optimistic concurrency control (for example with a version key) or switch critical updates to atomic field-level operations that detect conflicts.

---

### MEDIUM - Mattermost Markdown Injection

**Location:** `services/mattermost.js:37-78`

**Description**

Mattermost notification templates interpolate project titles and descriptions directly into markdown-formatted webhook messages without escaping markdown metacharacters. A project owner can therefore inject formatting, links, or structural markdown into downstream notifications.

**Impact**

This enables message spoofing or presentation manipulation in an operational channel that judges and organizers may trust.

**Reproduction Steps**

1. Create or rename a project using markdown control characters such as `**[Click Here](https://attacker.example)**`.
2. Trigger a Mattermost notification by submitting the project or crossing a milestone.
3. Observe that the rendered Mattermost message contains attacker-controlled markdown effects.

**Recommendation**

Escape markdown metacharacters before composing webhook text, or use structured message fields that do not interpret raw markdown from user content.

---

### HIGH - SSRF via Weak GitHub Repository URL Validation

**Location:** `services/github.js:9-44`; `controllers/project.js:16-22`

**Description**

The repository URL handling accepts user-supplied GitHub URLs and derives an outbound fetch target using a loose regex that looks for `github.com/` but does not strictly parse and validate the hostname and owner/repo components. Crafted values with confusing hostnames or malformed path segments can slip through validation and reach the outbound repository-refresh logic.

**Impact**

This creates SSRF potential and weakens trust boundaries around server-side outbound requests. At minimum it permits attacker-controlled fetch targets within a loosely validated GitHub namespace, and parsing edge cases may broaden that impact further.

**Reproduction Steps**

1. Provide a crafted repository URL that embeds `github.com` in an attacker-controlled context or uses malformed owner/repo path components.
2. Trigger the repository refresh path by viewing or updating the project.
3. Observe that the URL is accepted instead of rejected for strict GitHub validation failure.

**Recommendation**

Parse the URL with a real URL parser, require the exact expected GitHub hostname, and strictly validate `[owner]/[repo]` with an allowlisted character set before any outbound request is made.

---

### LOW - ReDoS Potential in User Search

**Location:** `controllers/project.js:746-754`

**Description**

Authenticated user search builds a case-insensitive regex from user input and applies it to email/name fields. The input is escaped, which helps against regex injection, but very long queries can still create avoidable performance pressure on the database and application.

**Impact**

This is a low-severity availability risk. A single authenticated user can force repeated expensive search operations with large query strings.

**Reproduction Steps**

1. Authenticate as a normal user.
2. Send repeated `GET /api/users/search?q=<very long string>` requests.
3. Observe the endpoint accept and process the requests rather than quickly rejecting oversized input.

**Recommendation**

Add a strict maximum query length, use indexed/prefix-safe search where possible, and apply a dedicated authenticated search limiter.

---

### LOW - Weak Asciinema Cast ID Validation

**Location:** `controllers/project.js:29-33,326-327,515-520,688`

**Description**

The Asciinema cast parser returns the entire trimmed input when it does not match the expected URL pattern. This means arbitrary untrusted strings can flow through a path that appears to expect a tightly constrained cast ID.

**Impact**

The immediate impact is limited, but weak validation increases the chance of downstream errors, inconsistent data, or unsafe future assumptions about the field.

**Reproduction Steps**

1. Submit malformed or unexpected cast-ID input rather than a normal Asciinema URL or ID.
2. Observe that the value is accepted into the project data path instead of being rejected.

**Recommendation**

Require a strict allowlisted cast-ID format and return a validation error for anything else.

---

### MEDIUM - Missing Cache-Control on Authenticated Pages

**Location:** `app.js` authenticated dynamic routes

**Description**

Authenticated pages such as `/projects` and `/projects/mine` do not set explicit anti-caching headers such as `Cache-Control: no-store`, `Pragma: no-cache`, or `Expires: 0`. The site relies on infrastructure defaults rather than clear cache instructions for sensitive user-specific content.

**Impact**

Browsers, shared devices, and intermediaries may retain authenticated responses longer than intended, increasing privacy and session-after-logout exposure risk.

**Reproduction Steps**

1. Authenticate and request an authenticated page such as `/projects`.
2. Inspect the response headers.
3. Observe that explicit anti-caching directives are absent.

**Recommendation**

Set no-store / private cache-control headers on authenticated dynamic routes and exempt only intentionally cacheable static assets.

---

### LOW - Morgan Dev Logging in Production

**Location:** `app.js:195-197`

**Description**

The production server uses Morgan's `dev` logging format outside of tests. That format is convenient for local development but is verbose, colorized, and less suitable for production log aggregation, alerting, and sensitive-data handling.

**Impact**

This is primarily an information-disclosure and operations-hardening issue: logs are noisier and less structured than they should be in production.

**Reproduction Steps**

1. Review the production logging configuration or active logs.
2. Observe `dev`-style request lines rather than a production-safe structured format.

**Recommendation**

Use an environment-aware production format such as `combined` or structured JSON logging.

---

### LOW - Static Asset Requests Create Sessions

**Location:** `app.js:320-321`

**Description**

Session middleware runs before static middleware, so requests for CSS, JavaScript, images, and uploaded files can create a session cookie even when no application session is needed.

**Impact**

This wastes session-store capacity, adds unnecessary cookies to otherwise cacheable asset responses, and slightly increases attack surface and operational load.

**Reproduction Steps**

1. Request a static asset such as `/css/main.css` without an existing session.
2. Inspect the response headers.
3. Observe `Set-Cookie: connect.sid=...` in the asset response.

**Recommendation**

Serve static assets before session middleware or explicitly skip session creation on static paths.

---

### MEDIUM - Vote Endpoint Lacks Dedicated Rate Limiting

**Location:** `app.js:383`

**Description**

`POST /projects/:id/vote` relies on the broad global limiter rather than a tighter vote-specific limit. Although duplicate votes on the same project are prevented, a single authenticated user can still send many vote-related requests across the project corpus in a short period.

**Impact**

This increases abuse potential for vote manipulation, noisy automation, and avoidable write load on the voting path.

**Reproduction Steps**

1. Authenticate as a normal user.
2. Script repeated vote requests across many project IDs.
3. Observe that only the coarse global limiter applies.

**Recommendation**

Add a dedicated vote limiter with a much lower threshold and monitor bursty vote activity.

---

### LOW - CI Pipeline Lacks Security Scanning

**Location:** `.github/workflows/ci.yml`

**Description**

The CI workflow runs install, lint, and test steps but does not perform dependency auditing, static analysis, or secret scanning. Security regressions can therefore pass through normal CI without explicit detection.

**Impact**

This weakens SDLC defenses and increases the chance that vulnerable dependencies, insecure code patterns, or accidentally committed secrets reach production.

**Reproduction Steps**

1. Review the CI workflow definition.
2. Observe the absence of dependency audit, SAST, or secret-scanning jobs.

**Recommendation**

Add dependency security checks, SAST, and secret scanning to the CI pipeline and gate merges on high-confidence failures.

---

### INFO - Admin Escalation Not Possible (good)

**Tested behavior:** Non-admin users cannot reach `/admin` functionality through common bypass attempts.

**Description**

The administrative authorization middleware correctly checks the role stored in the database on each request. Testing showed that parameter pollution and cookie tampering do not bypass this control, and the OIDC login flow does not permit client-side role selection.

**Impact**

This is a positive result. It indicates that administrative access control is enforced server-side rather than trusted from user-controlled inputs.

**Verification Steps**

1. Attempt access to `/admin` routes as a non-admin user.
2. Try parameter pollution variations and cookie tampering.
3. Attempt to influence role assignment during OIDC login.
4. Observe consistent `403 Forbidden` responses or ignored malicious input.

**Recommendation**

Preserve the current server-side role enforcement approach and continue validating it in regression testing.

## Conclusion and Recommendations

megademo.ai now has **32 validated vulnerabilities and issues** spanning authorization, session handling, privacy, business logic, injection, infrastructure, and SDLC hygiene. Immediate remediation should focus on the **project self-join takeover issue**, the **submission deadline bypass**, the **weak GitHub repository URL validation with SSRF potential**, the **plaintext secret exposure on the admin dashboard**, and the **vulnerable dependency set**, as these create the clearest high-impact risk. The medium-severity issues around **draft voting, email exposure, unauthenticated uploads, webhook integrity, markdown injection, cache behavior, vote throttling, and concurrency safety** should follow close behind. The remaining low-severity findings still merit cleanup to reduce abuse surface and improve reliability.

Priority recommendations:

1. Fix project membership authorization and apply the same visibility checks to draft voting and uploaded assets.
2. Enforce submission deadlines server-side and add quotas plus conflict controls for project mutation workflows.
3. Strictly validate GitHub repository URLs before any outbound fetch and escape user-controlled markdown in webhook messages.
4. Mask dashboard secrets, regenerate sessions after login, and require OAuth `state` for GitHub authentication.
5. Add explicit cache-control headers, dedicated rate limits for sensitive authenticated actions, and no-session handling for static assets.
6. Expand CI with dependency, SAST, and secret scanning while moving production logging to a structured format.

## Responsible Disclosure Note

These findings are documented to support remediation and improve platform security. Testing was performed against the live application using authenticated access and focused on validating authorization, session handling, privacy exposure, input validation, and operational behavior.
