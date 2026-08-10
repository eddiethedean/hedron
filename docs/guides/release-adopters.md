# Release summary (adopters)

Living train for public installs. Maintainer cut process:
[Release process (summary)](release-summary.md) · full runbook on GitHub
([RELEASE.md](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)).

## Current train

| Item | Value |
|---|---|
| Version | **v0.25.1** (Published; workspace candidate `0.25.2`) |
| Pin | `hedron>=0.25.0,<0.26` |
| Package maturity | Beta (flagship + adapters) |
| GitHub Release | [github.com/eddiethedean/hedron/releases](https://github.com/eddiethedean/hedron/releases) |
| Supply-chain | Prefer Release assets for SBOM / evidence bundle when attached; regenerate with repo scripts if missing |

```bash
pip install -U "hedron>=0.25.0,<0.26"
# or
uv add "hedron>=0.25.0,<0.26"
```

## What to read next

| Need | Page |
|---|---|
| Adopter highlights | [What’s new in 0.25](whats-new-0.25.md) |
| Capability maturity | [What’s ready](whats-ready.md) |
| Upgrade from 0.24 | [Upgrade](upgrade.md) |
| Ship checklist | [Ship a Hedron app](ship.md) |
| Per-package CHANGELOG | [Package changelogs](changelog.md) |

No commercial SLA and no scheduled 1.0 — pin upper bounds on `0.x`.
