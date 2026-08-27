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
| Stable | `0.66.2` / `0.66.x` | Current stable release and production pin |
| Beta | `0.67.0` | Preview release for the next phase; subject to change |
| Package maturity | Beta | Beta surfaces remain usable with pins; no SLA |
| Supported Python | 3.11–3.14 | CPython only |

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
| Know security support window | Current stable train `0.66.x` — [SECURITY.md](../SECURITY.md) |
| Know human AT / screen-reader status | Protocol engineering only; compensated sessions **not Supported** — [What’s ready](whats-ready.md) |

The `0.66.2` release is the latest stable public release and is available from PyPI. The
`0.67.0` beta is the next preview train. See
`docs/release.toml` for the public registry facts.

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
