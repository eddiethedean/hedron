# Security policy

## Supported versions

Security fixes land on the **current repository train** (`1.0.x`). Until the candidate is tagged
and uploaded, public installs use the `0.67.x` fallback. Older lines should upgrade;
there is **no multi-year LTS**. Best-effort triage for the immediately
previous minor (`0.67.x`) continues through approximately **2027-02-27** — after that, upgrade
is required. There is **no contractual patch SLA**.

The current repository train is **`1.0.x`**, pinned in-tree as `>=1.0.0,<1.1`; the public PyPI
fallback is `>=0.67.0,<0.68` until upload.

| Version | Supported |
|---|---|
| `1.0.x` | Yes (current repository train — public PyPI pin remains `>=0.67.0,<0.68`; upload deferred) |
| `0.67.x` | Best-effort security triage through approximately 2027-02-27; upgrade to `1.0.x` |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

### Disclosure channel (required)

Open a private GitHub
[security advisory](https://github.com/eddiethedean/hedron/security/advisories/new).
This is the **dedicated** disclosure channel for Hedron — use it even if you also email
the maintainer. Advisories give a private thread, artifact tracking, and coordinated
publication.

### Process (best-effort)

1. File the private advisory with the details below.
2. Expect acknowledgment within a few business days (**no contractual security SLA**).
3. Coordinated disclosure is preferred; allow reasonable time before public discussion.
4. Fixes target the current repository train (`1.0.x`); see Supported versions above.

### Alternate contact

If GitHub advisories are unavailable to you, email **odosmatthews@gmail.com** (package
author / maintainer contact in package metadata) with the same details and note that you
could not open an advisory. Prefer the advisory form whenever possible — a personal inbox
is not a dedicated security mailbox and is best-effort only.

Include:

- Affected package(s) and versions
- A minimal reproduction
- Impact assessment (confidentiality, integrity, availability)
- Whether a fix is already known

**Severity classes (best-effort):**

| Class | Examples | Target acknowledgment |
|---|---|---|
| Critical | RCE, auth bypass in first-party packages | Same or next business day |
| High | CSRF/session break in defaults, XSS via renderer bug | Few business days |
| Medium / Low | Hardening gaps, docs misclaims | Best-effort backlog |

Credit is offered in release notes / advisories when reporters want it. Advisory cadence
follows GitHub Security Advisories when a fix ships — there is no fixed monthly bulletin.

## Scope

In scope: Hedron first-party packages (`hedron`, `hedron-core`, adapters, Explorer, data,
charts, jinja) and their documented secure defaults (escaping, CSRF, redirects, trust
types, asset URLs).

Out of scope: application-authored HDJ/templates that embed untrusted content, third-party
plugins, Posit/Connect host misconfiguration, and vulnerabilities that only appear when
operators disable documented secure defaults.

## Prefer secure defaults

- Keep CSRF, TrustedHost, and redirect allowlists enabled.
- Do not disable escaping or pass untrusted HTML into trusted-HTML APIs.
- Prefer polling for job status unless you accept the experimental SSE/WebSocket posture
  (`HEDRON_SECURITY_RISK_ACCEPTANCE=experimental-live` under production).
- Under production, omit `[tool.hedron] plugins` to load none, or set an explicit allowlist.
- Treat session secrets and worker shared state as production requirements — see
  [Secrets and workers](https://github.com/eddiethedean/hedron/blob/main/docs/guides/secrets-and-workers.md).

## Accepted residuals (honest gaps)

These remain **accepted** residuals on the current train — document them; do not market them away:

- Plugin / Explorer abuse corpus beyond default guards
- Explorer live traces (`EXPLORER-10-001`, Deferred on `0.10.x`)
- Idiomorph / morphing (`MORPH-048`, Deferred)
- Human AT sessions (protocol Verified; compensated sessions Planned — [#86](https://github.com/eddiethedean/hedron/issues/86))
- Application-owned authz / multi-tenant isolation (out of framework scope)
- `TrustedHtml.reviewed` / trusted HDJ as explicit trust sinks
- Soft CI performance budgets are not product SLOs

See [Public 1.0 readiness](https://github.com/eddiethedean/hedron/blob/main/docs/guides/one-point-zero-readiness.md).

## Language

This policy describes maintainer intent. It is **not** a warranty, SLA, or insurance product.
