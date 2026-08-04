# What’s new in 0.10.1

Security and correctness patch on the **0.10** train (packages `0.10.1`, 2026-08-04).
Capability narrative for the phase remains [What’s new in 0.10](whats-new-0.10.md).

## Why upgrade

Pin or upgrade to **`0.10.1`** if you use caching, redirects, SSE/streaming, job status,
or poll-based job helpers. The patch tightens fail-closed behavior on several boundaries.

## Highlights (from package changelogs)

- Require `vary_on` for default private `cache_data` scopes.
- Reject credentialed URLs in `redirect_external`.
- Validate SSE / stream / preload header names and values for control characters.
- Job SSE returns HTTP 403/404 on authz/missing jobs; sanitize bad `Last-Event-ID`.
- Poll `job_status_response` enforces the same job authz contract as SSE.

Full lists: [hedron CHANGELOG](https://github.com/eddiethedean/hedron/blob/main/packages/hedron/CHANGELOG.md)
and sibling package changelogs linked from [Release notes](release-notes.md).

## Install

```bash
pip install -U "hedron>=0.10.1"
# or
uv add "hedron>=0.10.1"
```

## See also

- [What’s ready today](whats-ready.md)
- [Upgrade (0.8 → 0.10)](upgrade.md)
- [STATUS](../STATUS.md) · [RELEASE runbook](../RELEASE.md)
