---
description: The authoritative release, installation, and support status for Hedron.
search:
  boost: 2
---

# Current release and support

This page is the public release-status source of truth. Other pages should link here
instead of repeating version numbers.

## At a glance

| Channel | Version | Meaning |
|---|---|---|
| Repository train | `1.0.0` / `1.0.x` | Verified coordinated release candidate; tag and registry publication pending |
| Stable PyPI | `0.66.2` / `0.66.x` | Current public release and production pin |
| Migration baseline | `0.67.0` | Immutable predecessor used by the 1.0 bridge |
| Package maturity | Stable coordinated inventory | Satellite packages retain their independent maturity; no commercial SLA |
| Supported Python | 3.10–3.14 | CPython only |

The 1.0 package split is intentional:

| Package | 1.0 role | Status |
|---|---|---|
| `hedron-posit` | Coordinated Hedron facade for Posit Workbench and Connect | `1.0.0` repository candidate |
| `fastapi-workbench` | Independent generic adapter for plain FastAPI/ASGI apps | `1.0.1` |
| `hedron-workbench` | Former compatibility distribution | Removed in 1.0.0 |

Application documentation uses the latest public PyPI pin:

```text
hedron>=0.66.2,<0.67
```

Contributors working from a checkout should use `uv sync` so local packages resolve
from the workspace.

## PyPI vs checkout (one screen)

| You want… | Do this |
|---|---|
| Build an application | Install the stable release: `hedron>=0.66.2,<0.67` |
| Contribute / hack on Hedron | Clone the repo and `uv sync` (editable workspace) |
| Evaluate the beta preview | Use `v0.67.0` only for beta evaluation; stable applications should remain on `v0.66.2` |
| Know security support window | Current repository train `1.0.x`; public registry train `0.66.x` until publication — [SECURITY.md](../SECURITY.md) |
| Know human AT / screen-reader status | Protocol engineering only; compensated sessions **not Supported** — [What’s ready](whats-ready.md) |

The `0.66.2` release is the latest stable public release available from PyPI. The
`0.67.0` beta is the immutable migration baseline for the verified `1.0.0` repository
candidate, not the next development train. See `docs/release.toml` for registry facts.

## What should I install?

- Building an application: follow [Installation](../getting-started/installation.md).
- Trying the framework: follow [Build your first app](../getting-started/quickstart.md).
- Contributing to Hedron: follow [Contributor day one](contributor-day-one.md).
- Evaluating production use: read [What's ready today](whats-ready.md), then
  [Evaluate Hedron](evaluate.md).

## Release terminology

- **Repository train**: the version represented by the current checkout and workspace
  metadata.
- **Latest PyPI release**: the newest version that a clean application can resolve from
  the public package index.
- **Published**: the release is available from PyPI and has a corresponding release
  record.
- **Supported**: a capability covered by the current maturity matrix when the stated
  version and configuration are pinned.
- **Experimental**: available for evaluation but subject to change; use the documented
  fallback when one exists.

## Update policy

The values on this page are derived from [`docs/release.toml`](../release.toml). When a
release is uploaded, update that file first, then run the documentation checks before
editing any prose. Do not hand-edit historical release pages to make them current.
