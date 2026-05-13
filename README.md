# megademo.ai Security Audit

A responsible disclosure security review of the megademo.ai hackathon platform.

## Executive Summary

This report documents several security findings identified during authenticated testing performed with permission on megademo.ai. The most serious issue is a **high-severity project takeover vulnerability** that allows any authenticated user to join any non-draft project and immediately gain full edit rights. Additional issues include **session fixation**, a **production test-login endpoint that accepts credentials in a GET URL**, and **self-voting on a user's own project**.

The assessment also confirmed an important positive control: **admin privilege escalation was not possible** during testing. Administrative routes correctly enforce authorization using the database-backed role check.

## Methodology

Testing was performed using an authenticated user session with permission to assess the application. The review focused on:

- Project membership and authorization flows
- Authentication and session handling
- Administrative access controls
- Input handling for project voting and project creation features

The testing approach was manual and behavior-driven, using normal application requests and direct HTTP requests to verify authorization and session management behaviors.

## Findings Summary

| Severity | Title | Description | Reproduction Steps | Recommendation |
| --- | --- | --- | --- | --- |
| HIGH | Project Takeover via Self-Join | Any authenticated user can POST `/projects/:id/join` on any non-draft project and gains full edit rights without ownership or invitation checks. | Log in as a normal user, send `POST /projects/:id/join` for another team's non-draft project, then edit that project's details. | Restrict joins to explicit invitations, ownership-approved membership changes, or validated team workflows; enforce authorization server-side before membership changes. |
| MEDIUM | Session Fixation | Login does not regenerate the session ID after authentication, allowing an attacker who can pre-set a victim's cookie to hijack the authenticated session. | Obtain or set a victim browser session ID, have the victim authenticate, and observe that the session ID remains unchanged and becomes authenticated. | Regenerate the session identifier immediately after successful login and invalidate any prior unauthenticated session. |
| MEDIUM | Test Login Token in URL (GET parameter) | `/auth/test-login?token=...&role=admin` is active in production, exposing the token in URLs, logs, browser history, and proxies. | Visit `/auth/test-login?token=...&role=admin` and note that the token is processed via GET and appears in request logs and history. | Disable the endpoint in production; if retained for non-production use, require POST and additional environment gating. |
| LOW | Self-Voting Allowed | Users can vote 5 stars on their own projects because ownership/team membership is not checked before accepting votes. | Log in as a project owner or team member and submit a vote for that same project. | Reject votes from project owners and team members server-side. |
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

megademo.ai would benefit from immediate remediation of the **project self-join takeover issue**, as it directly affects the integrity of participant submissions. The **session fixation** issue and **production test-login endpoint** should also be prioritized because they affect authentication security and could enable broader compromise under realistic conditions. The **self-voting** issue is lower severity but should still be addressed to protect fair competition.

Priority recommendations:

1. Fix project membership authorization before allowing users to join or edit projects.
2. Regenerate session IDs on every successful authentication event.
3. Remove or hard-disable the test-login endpoint in production.
4. Block self-voting by project owners and team members.
5. Add regression tests covering authorization, session lifecycle, and voting restrictions.

## Responsible Disclosure Note

These findings are documented to support remediation and improve platform security. Testing was performed against the live application using authenticated access and focused on validating authorization and session handling behavior.