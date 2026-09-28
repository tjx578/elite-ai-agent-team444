# Security Policy

This policy covers `tjx578/wolf15-sentient` (WOLF15 Sentient).

## Supported Versions

WOLF15 Sentient is in active development. Security maintenance is best-effort
and does not constitute a production-support commitment.

| Version or branch | Security maintenance |
| --- | --- |
| Current `main` | Primary target for triage and security fixes |
| Earlier commits | Reports accepted; fixes normally target current `main`, with no backport commitment |
| Feature branches and experimental checkouts | No independent security-maintenance commitment |
| Stable releases | No stable release support line is currently designated |

Report the exact affected commit SHA. A passing CI run, a development package
version, or an architecture document does not establish production readiness
or a supported release line.

## Reporting a Vulnerability

**Do not publish vulnerability details in public issues, pull requests,
discussions, logs, or shared chat links.**

### Private reporting channel

Use GitHub private vulnerability reporting for this repository when available:

1. Open the repository's **Security** or **Security and quality** tab.
2. Open **Advisories** and select **Report a vulnerability**.
3. Submit the report through the private form.

If the button is unavailable, open a public issue titled
**Request for a private security reporting channel** and mention `@tjx578`.
Include only the request for a private contact method: no affected component,
exploit details, credentials, personal data, logs, or proof of concept. Wait
for a private channel before sharing technical details.

No private email address or alternate messaging account is designated by this
policy. Do not assume an address found in commit metadata is a security contact.

### Information to include privately

- The affected commit SHA, relevant file paths, Python version, dependency
  versions, and configuration needed to reproduce the issue.
- A description of the suspected security impact, expected versus observed
  behavior, and a minimal reproduction using synthetic data in an isolated
  environment you own or are authorized to test.
- Sanitized logs, test output, screenshots, or a proposed fix, when available.
  Distinguish observed results from assumptions and unexecuted tests.

Do not send real credentials, access tokens, private keys, personal emails,
private documents, or unrelated confidential material. If a credential may
have been exposed, notify its owner through a private channel; do not test
whether it works.

### Scope

Reports may concern code, dependency integration, CI workflows, packaging, or
security-relevant documentation maintained in this repository. Relevant issues
include unauthorized actions, bypasses of authority or approval boundaries,
secret exposure, unsafe input handling, and forged or misattributed evidence.

Planned capabilities are not evidence of an existing vulnerability. Identify
the implementation and the affected security boundary, or clearly label the
report as a design concern.

External projects, donor repositories, model providers, messaging accounts,
and WOLF15 Trading are separate systems. Report vulnerabilities in those
systems to their maintainers. A vulnerability in WOLF15 Sentient's own
integration with them remains in scope when that integration exists.

### What to expect

Reports are handled on a best-effort basis. This policy does not promise a
fixed acknowledgment deadline, update interval, remediation deadline, or
financial reward.

After an initial response, maintainers and the reporter should agree on an
update cadence in the private thread. Additional updates should identify
confirmed impact, outstanding questions, mitigation options, or fix status.

If accepted, the report proceeds to private investigation, remediation, and
regression verification. Acceptance for investigation is not confirmation
that the issue is fixed.

If more information is needed, maintainers should request the missing details.
If declined, closed as a duplicate, or referred upstream, the response should
explain the reason when it is safe to do so.

Public disclosure should be coordinated with the reporter after assessing
impact and mitigation readiness. Public advisories must not contain secrets
or unnecessary personal data.

### Testing and disclosure boundaries

Use local, isolated test environments and synthetic data. Do not access other
people's data, disrupt services, run unsolicited scans against deployments,
or test third-party accounts and infrastructure without explicit permission.
Stop testing if unexpected sensitive data or external effects appear.

This policy does not authorize production changes, repository merges,
deployments, credential changes, capability activation, or REE activation.
It does not select or change the repository's license.
