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
| Repository checkout | `0.60.2` / `0.60.x` | Prepared and verified in-tree release candidate |
| PyPI | `0.60.0` / `0.60.x` | Latest installable release from the public package index |
| Package maturity | Beta | Usable with pins; no SLA or scheduled 1.0 release |
| Supported Python | 3.11–3.14 | CPython only |

Application documentation uses the published PyPI pin:

```text
hedron>=0.60.0,<0.61
```

Contributors working from a checkout should use `uv sync` so local packages resolve
from the workspace.

## PyPI vs checkout (one screen)

| You want… | Do this |
|---|---|
| Build an application | Install from PyPI: `hedron>=0.60.0,<0.61` |
| Contribute / hack on Hedron | Clone the repo and `uv sync` (editable workspace) |
| Know security support window | Current train `0.60.x` — [SECURITY.md](../SECURITY.md) |
| Know human AT / screen-reader status | Protocol engineering only; compensated sessions **not Supported** — [What’s ready](whats-ready.md) |

The `0.60.0` release is represented by the latest verified public release and is available
from PyPI; `registry_status = "uploaded"` in [`docs/release.toml`](../release.toml). The
repository's coordinated package metadata is prepared for the `0.60.2` patch candidate;
the public install pin remains unchanged until that candidate is uploaded and verified.

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
