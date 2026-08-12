# Security policy

## Supported versions

Security fixes land on the **current published train** (`0.32.x`). Older `0.x` lines should
upgrade; there is **no multi-year LTS**. Best-effort triage for the immediately previous
minor (`0.30.x`) continues through approximately **2027-01-12** — after that, upgrade
is required. There is **no contractual patch SLA**.

| Version | Supported |
|---|---|
| `0.32.x` | Yes (current living tip — pin `>=0.32.0,<0.33`; in-tree `v0.32.0`, git tag deferred) |
| `0.31.x` | Yes (previous published train — pin `>=0.32.0,<0.33`; last published `v0.31.0`) |
| `0.30.x` | Prefer upgrade to `0.31.x` (best-effort security triage through approximately 2027-01-12) |
| `0.29.x` | Prefer upgrade to `0.31.x` |
| `0.28.x` | Prefer upgrade to `0.31.x` |
| `0.27.x` | Prefer upgrade to `0.31.x` |
| `0.26.x` | Prefer upgrade to `0.31.x` |
| `0.25.x` | Prefer upgrade to `0.31.x` |
| `0.24.x` | Prefer upgrade to `0.31.x` |
| `0.23.x` | Prefer upgrade to `0.31.x` |
| `0.22.x` | Prefer upgrade to `0.31.x` |
| `0.20.x` | Prefer upgrading to the current train |
| `0.19.x` | Prefer upgrading to the current train |
| `0.18.x` | Prefer upgrading to the current train |
| `0.17.x` | Prefer upgrading to the current train |
| `0.16.x` | Prefer upgrading to the current train |
| `0.15.x` | Prefer upgrading to the current train |
| `0.14.x` | Prefer upgrading to the current train |
| `0.13.x` | Prefer upgrading to the current train |
| `0.12.x` | Prefer upgrading to the current train |
| `0.11.x` | Prefer upgrading to the current train |
| `0.10.x` | Prefer upgrading to the current train |
| `0.9.x` | Prefer upgrading to the current train |
| `0.8.x` | Final HDN-capable line; critical issues may be noted only |
| `< 0.8` | No |

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
4. Fixes land on the current published train (`0.32`); see Supported versions above.

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
plugins, misconfigured deployments, and host-framework CVEs (report those upstream).

## Supply chain / evidence

Release evidence and dependency inventories are produced by maintainer scripts
(`scripts/build_evidence_bundle.py`, `scripts/generate_sbom.py`,
`scripts/license_inventory.py`). See the [Evidence pack](guides/evidence-pack.md) for how
evaluators obtain SBOM / license inventory for the current train.

## See also

[Security guide](guides/security.md) · [Threat model](guides/threat-model.md) ·
[Support](guides/support.md) · [Code of Conduct](CODE_OF_CONDUCT.md)
