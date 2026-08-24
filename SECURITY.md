# Security policy

## Supported versions

Security fixes land on the **current published train** (`0.62.x`).
Older `0.x` lines should
upgrade; there is **no multi-year LTS**. Best-effort triage for the immediately previous
minor (`0.61.x`) continues through approximately **2027-08-20** — after that, upgrade
is required. There is **no contractual patch SLA**.

The current published train is **`v0.62.0`** on PyPI. First-run pins use
`>=0.62.0,<0.63`.

| Version | Supported |
|---|---|
| `0.62.x` | Yes (current published train — pin `>=0.62.0,<0.63`; published `v0.62.0`) |
| `0.61.x` | Best-effort security triage through approximately 2027-08-20; upgrade to `0.62.x` |
| `0.56.x` | Best-effort security triage through approximately 2027-08-20; upgrade to `0.60.x` |
| `0.55.x` | Best-effort security triage through approximately 2027-08-20; upgrade to `0.56.x` / `0.57.x` |
| `0.53.x` | Best-effort security triage through approximately 2027-08-20; upgrade to `0.56.x` / `0.57.x` |
| `0.52.x` | Best-effort security triage through approximately 2027-08-20; upgrade to `0.53.x` / `0.56.x` |
| `0.51.x` | Best-effort security triage through approximately 2027-08-20; upgrade to `0.52.x` / `0.53.x` |
| `0.50.x` | Best-effort security triage through approximately 2027-08-19; upgrade to `0.51.x` / `0.52.x` |
| `0.49.x` | Best-effort security triage through approximately 2027-08-17; upgrade to `0.50.x` |
| `0.48.x` | Best-effort security triage through approximately 2027-08-17; upgrade to `0.49.x` |
| `0.47.x` | Best-effort security triage through approximately 2027-08-17; upgrade to `0.48.x` |
| `0.46.x` | Best-effort security triage through approximately 2027-08-16; upgrade to `0.47.x` |
| `0.45.x` | Best-effort security triage through approximately 2027-08-16; upgrade to `0.46.x` |
| `0.44.x` | Best-effort security triage through approximately 2027-08-16; upgrade to `0.45.x` |
| `0.43.x` | Best-effort security triage through approximately 2027-08-16; upgrade to `0.44.x` |
| `0.42.x` | Best-effort security triage through approximately 2027-08-16; upgrade to `0.43.x` |
| `0.41.x` | Best-effort security triage through approximately 2027-08-16; upgrade to `0.42.x` |
| `0.40.x` | Best-effort security triage through approximately 2027-08-16; upgrade to `0.41.x` |
| `0.39.x` | Best-effort security triage through approximately 2027-08-16; upgrade to `0.40.x` |

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
4. Fixes target the current repository train (`0.62.x`); see Supported versions above.

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
