# megademo.ai Security Audit

![Scope](https://img.shields.io/badge/scope-authenticated%20pen--test%20%2B%20source%20review-0ea5e9?style=for-the-badge)
![Findings](https://img.shields.io/badge/findings-14%20validated-111827?style=for-the-badge)
![High](https://img.shields.io/badge/high-3-dc2626?style=for-the-badge)
![Medium](https://img.shields.io/badge/medium-6-f59e0b?style=for-the-badge)
![Low](https://img.shields.io/badge/low-5-16a34a?style=for-the-badge)
![Status](https://img.shields.io/badge/disclosure-responsible-7c3aed?style=for-the-badge)

> 🚨 **From a normal user account to full project takeover:** this expanded assessment identified **14 validated vulnerabilities and issues** in megademo.ai, including a **high-severity authorization flaw** that allowed any authenticated user to join another team's non-draft project and immediately gain edit control.

A responsible disclosure security review of the megademo.ai hackathon platform.

## Quick Stats

| Metric | Value |
| --- | --- |
| Findings validated | **14 findings** |
| Severity mix | **3 High · 6 Medium · 5 Low** |
| Most impressive finding | **Project takeover via unauthorized self-join** |
| Testing approach | **Authenticated penetration testing + source code review** |
| Positive control verified | **Admin privilege escalation was not possible** |

## Findings at a Glance

| Severity | Finding | Why it matters |
| --- | --- | --- |
| 🔴 **High** | **Project Takeover via Self-Join** | Any authenticated user could join another team's non-draft project and immediately gain full edit rights. |
| 🟡 **Medium** | **Session Fixation** | Login did not rotate the session ID, enabling session hijacking if an attacker could plant a known cookie first. |
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
| 🔵 **Info** | **Admin Escalation Not Possible** | Server-side role checks on `/admin` held up under testing and bypass attempts failed. |

## Executive Summary

This report documents multiple security, privacy, logic, and operational findings identified during authenticated testing performed with permission on megademo.ai. The most serious issue is a **high-severity project takeover vulnerability** that allows any authenticated user to join any non-draft project and immediately gain full edit rights. Additional issues affect **session handling, secret exposure, authenticated privacy leaks, markdown-based tracking, input validation, browse-page performance, outbound API usage, storage hygiene, and dependency health**.

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

megademo.ai would benefit from immediate remediation of the **project self-join takeover issue**, the **plaintext secret exposure on the admin dashboard**, and the **vulnerable dependency set**, as these create the clearest high-impact risk. The **session fixation**, **authenticated user enumeration**, **markdown image beacon**, **missing server-side validation**, and **browse-page pagination** issues should also be prioritized because they affect authentication security, privacy, data quality, and platform reliability. The remaining low-severity issues still merit cleanup to improve correctness and operational hygiene.

Priority recommendations:

1. Fix project membership authorization before allowing users to join or edit projects.
2. Mask dashboard secrets by default and remove plaintext exposure of sensitive values.
3. Regenerate session IDs on every successful authentication event.
4. Restrict sensitive helper endpoints and never send secrets in URLs.
5. Add server-side validation, input guards, pagination, and dependency upgrade remediation as regression-backed fixes.

## Responsible Disclosure Note

These findings are documented to support remediation and improve platform security. Testing was performed against the live application using authenticated access and focused on validating authorization, session handling, privacy exposure, input validation, and operational behavior.
