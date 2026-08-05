# Security policy

## Supported versions

| Version | Supported |
|---|---|
| `0.11.x` | Yes |
| `0.10.x` | Security fixes while 0.11 remains Beta; prefer upgrading |
| `0.9.x` | Prefer upgrading to the current train |
| `0.8.x` | Final HDN-capable line; critical issues may be noted only |
| `< 0.8` | No |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

**Preferred:** open a private GitHub
[security advisory](https://github.com/eddiethedean/hedron/security/advisories/new)
— this is the dedicated disclosure channel for Hedron.

**Alternate:** email **odosmatthews@gmail.com** (package author / maintainer contact
published in package metadata) with the same details. Do not open a public issue for
vulnerabilities.

Include:

- Affected package(s) and versions
- A minimal reproduction
- Impact assessment (confidentiality, integrity, availability)
- Whether a fix is already known

You should receive an acknowledgment within a few business days (best-effort; there is
**no contractual security SLA**). Coordinated disclosure is preferred; please allow
reasonable time before public discussion.

## Scope

In scope: Hedron first-party packages (`hedron`, `hedron-core`, adapters, Explorer, data,
charts, jinja) and their documented secure defaults (escaping, CSRF, redirects, trust
types, asset URLs).

Out of scope: application-authored HDJ/templates that embed untrusted content, third-party
plugins, misconfigured deployments, and host-framework CVEs (report those upstream).

## Supply chain / evidence

Release evidence and dependency inventories are produced by maintainer scripts
(`scripts/build_evidence_bundle.py`, `scripts/generate_sbom.py`,
`scripts/license_inventory.py`). Published release notes and GitHub Releases attach or
link evidence when a train is cut—see [RELEASE](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md).

## See also

[Security guide](guides/security.md) · [Threat model](guides/threat-model.md) ·
[Support](guides/support.md) · [Code of Conduct](CODE_OF_CONDUCT.md)
