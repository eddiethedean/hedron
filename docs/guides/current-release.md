---
description: The authoritative Hedron release, installation, compatibility, and support status.
search:
  boost: 2
---

# Current release and support

This is the public release-status source of truth. Other pages link here instead of
maintaining their own release story.

<!-- hedron-release-status -->

## At a glance

| Package | Version | Maturity | Application requirement | Role |
|---|---:|---|---|---|
| `hedron` | `1.0.3` | Stable | `hedron>=1.0.0` | FastAPI-native component and route authoring |
| `hedron-data` | `1.0.3` | Stable | `hedron-data>=1.0.0` | DataTable, DataEditor, and bounded data contracts |
| `hedron-charts` | `1.0.3` | Stable | `hedron-charts>=1.0.0` | First-party charts and static/Matplotlib output |
| `hedron-maps` | `1.0.3` | Stable | `hedron-maps>=1.0.0` | Bounded first-party maps and offline presentation |
| `edron` | `1.0.3` | Stable | `edron>=1.0.0` | Alternate class-oriented facade over Hedron |

The coordinated release supports CPython **3.10–3.14**. Package maturity, capability
readiness, and individual API stability are separate: a stable package may contain a
clearly labeled experimental capability.

The exact 1.0 package and API boundary is maintained in the repository’s
[`release/support-matrix.toml`](https://github.com/eddiethedean/hedron/blob/main/release/support-matrix.toml). Beta
host/tooling satellites are opt-in compatibility surfaces, not part of the stable platform contract.

## What should I install?

| Goal | Continue with |
|---|---|
| New FastAPI/component application | [Hedron quick start](../getting-started/quickstart.md) |
| Dashboard, CRUD app, or data workflow | [Hedron guides](index.md) |
| Existing Flask or Django application | [Installation and host adapters](../getting-started/installation.md) |
| Repository contribution | `uv sync`, then [Contributor day one](contributor-day-one.md) |

When using the public registry or repository checkout, require the `>=1.0.0` baseline shown above.
Upgrade deliberately after reading the release notes and running the application's own integration
tests.

## Support lifecycle

| Train | Security support | Compatibility expectation |
|---|---|---|
| `1.0.x` | Current published train | Stable APIs follow the 1.x compatibility policy |
| `0.67.x` | Best-effort security triage through approximately 2027-02-27 | Upgrade to 1.0; migration aliases are not the new golden path |
| Earlier `0.x` | Unsupported | Use historical documentation only to plan an upgrade |

There is no commercial SLA. Community support is provided through GitHub; security reports
follow [SECURITY.md](../SECURITY.md), not public issues.

## Stability and deprecation

- **Stable:** compatibility-protected for the documented 1.x contract.
- **Beta:** usable with pins, but its contract may change in a future minor release.
- **Experimental:** opt-in evaluation surface with a documented production fallback.
- **Deprecated:** retained temporarily for migration and absent from new quick starts.

Removal of a stable API requires a deprecation notice, migration guidance, and a future
major release. See [Stability](../api/STABILITY.md) and [Upgrade](upgrade.md).

## Coordinated and independent packages

`hedron-core`, `hedron`, Edron, `hedron-data`, `hedron-charts`, and `hedron-maps` use the
coordinated 1.0 Stable contract in the repository. Host adapters and vendor/tooling satellites
retain independent versions and Beta maturity.
Do not infer satellite compatibility from a similar
version number; use the [compatibility matrix](../COMPATIBILITY.md).

The Workbench split is intentional:

| Package | Role |
|---|---|
| `hedron-posit` | Coordinated Hedron facade for Posit Workbench and Connect |
| `fastapi-workbench` | Independent generic adapter for plain FastAPI/ASGI applications |
| `hedron-workbench` | Removed compatibility distribution |

## Release maintenance

The values rendered in release callouts and install matrices come from
[`docs/release.toml`](../release.toml). A release change begins there and must pass the
documentation source-of-truth, API coverage, link, and strict build checks. Historical release
pages remain historical; they are not edited to masquerade as the current release.
