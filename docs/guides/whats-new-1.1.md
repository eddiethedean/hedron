---
description: What shipped in Hedron 1.1.1, including the Phase 1.1 enhancement completion release.
search:
  boost: 1.8
---

# What’s new in Hedron 1.1

!!! note "Historical release note"

    This page describes the 1.1 release. For current installation, support, and release details,
    see [Current release and support](current-release.md).

Hedron `v1.1.1` completes Phase 1.1 and is published on PyPI. The release extends the
server-rendered FastAPI and HTMX authoring model with stronger data, navigation, security,
presentation, and application integration contracts.

## New capability areas

- **Identity and resources:** presentation hooks for identity-aware and resource-oriented views.
- **Collections:** bounded pagination and normalized collection state for predictable data flows.
- **Navigation:** request-aware navigation contracts for links, redirects, and prefetch decisions.
- **Secure forms:** write-only secret-field lifecycles and complementary validation behavior.
- **Application builds:** application-aware build and packaging contracts for release workflows.
- **Presentation:** native shell refinements and computed-style contracts verified in real browsers.

These capabilities remain server-owned and composable with HTMX. Browser-local enhancement stays
optional, while the HTML-first path remains the default.

## Package train

The coordinated Stable platform includes `hedron`, `hedron-core`, `edron`, `hedron-data`,
`hedron-charts`, and `hedron-maps` at `1.1.1`. Host adapters and tooling satellites retain their
documented independent versions and Beta maturity.

## Install

Install the published release from PyPI:

```bash
python -m pip install "hedron>=1.1.3,<1.2" "uvicorn[standard]"
```

For current release status, see [Current release and support](current-release.md).

The historical 1.1.3 evidence bundle is available at
[evidence-bundle-1.1.md](evidence-bundle-1.1.md).
