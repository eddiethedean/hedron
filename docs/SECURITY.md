# Security policy

## Supported versions

| Version | Supported |
|---|---|
| `0.10.x` | Yes |
| `0.9.x` | Security fixes while 0.10 remains Beta; prefer upgrading |
| `0.8.x` | Final HDN-capable line; critical issues may be noted only |
| `< 0.8` | No |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email the maintainer through the address listed on the
[GitHub profile](https://github.com/eddiethedean) for the repository owner, or use
GitHub's private [security advisory](https://github.com/eddiethedean/hedron/security/advisories/new)
flow when available.

Include:

- Affected package(s) and versions
- A minimal reproduction
- Impact assessment (confidentiality, integrity, availability)
- Whether a fix is already known

You should receive an acknowledgment within a few business days. Coordinated disclosure
is preferred; please allow reasonable time before public discussion.

## Scope

In scope: Hedron first-party packages (`hedron`, `hedron-core`, adapters, Explorer, data,
charts, jinja) and their documented secure defaults (escaping, CSRF, redirects, trust
types, asset URLs).

Out of scope: application-authored HDJ/templates that embed untrusted content, third-party
plugins, misconfigured deployments, and host-framework CVEs (report those upstream).

## See also

[Security guide](guides/security.md) · [Threat model](guides/threat-model.md) ·
[Support](guides/support.md)
