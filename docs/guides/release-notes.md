# Releases

This is the canonical adopter-facing release history. Package-level implementation
details remain in the [package changelogs](changelog.md).

!!! note "PyPI history before 0.1.0"

    Releases older than `0.1.0` belong to an unrelated, retired geolocation package.
    The current web framework starts at `0.1.0`; there is no supported migration path or
    API continuity with that legacy project.

## 0.28.1 — 2026-08-10

Correctness and tip-honesty patch for the 0.28 train.

- Raises the `hedron[native]` floor and wires Supported native wheel publish evidence.
- Fixes Auto Experimental remediation, optional chart HTMX dispose, Flask/Django
  mount-aware static prefixes, and live `HEDRON_NATIVE_DISABLE`.
- Hardens tip-hub SSOT wrap scans and CI native/crates publish footguns.

```bash
python -m pip install -U "hedron>=0.28.1,<0.29"
```

## 0.28.0 — 2026-08-10

Hedron 0.28.0 graduates charts and optional native acceleration inventories.

- Publishes a machine-checked production-grade inventory for `hedron-charts` and
  `hedron-native` (D-056 / RFC-0059).
- Matplotlib/static beginner charts are Supported; Plotly/Altair remain Experimental
  and are excluded from production Auto defaults.
- Optional Rust escape acceleration ships with `HEDRON_NATIVE_DISABLE` fallback and a
  Supported wheel matrix.
- Charts `0.1.9` and native `0.1.2` leave Alpha for declared Supported scopes.

No Supported CRUD/admin API removal is listed. Polling remains the production path for
live status; SSE, WebSocket, streaming, and preload remain experimental.

## 0.27.0 — 2026-08-10

Hedron 0.27.0 graduates data, Flask/Django, HDJ, and curated extras inventories.

- Publishes a machine-checked production-grade inventory for `hedron-data`,
  `hedron-flask`, `hedron-django`, `hedron-jinja`, and `hedron-extras`.
- Validates upgrades from Published `v0.26.0` across satellite public contracts.
- Verifies host-only Flask/Django/data/HDJ/extras smokes and portable PAGE/FRAGMENT
  parity.
- Scopes `hedron check` Django / Plotly-Altair notices to detected adapters and chart
  extras (`#54`); injects HTMX before bundled extensions on PAGE responses (`#55`);
  warns on `select_oob` + `OobUpdate` same-target conflicts and defaults `OobUpdate`
  swaps to `innerHTML` (`#57`).
- Mounts `/hedron-static` and injects shared PAGE assets on Flask and Django like
  FastAPI.

No Supported CRUD/admin API removal is listed. Polling remains the production path for
live status; SSE, WebSocket, streaming, and preload remain experimental.

```bash
python -m pip install -U "hedron>=0.28.1,<0.29"
```

Read [Upgrade to 0.27](upgrade.md) before changing a production lockfile. Maintainer
evidence identifiers and packets are linked from [What’s new in 0.27](whats-new-0.27.md).

## 0.26.1 — 2026-08-10

Correctness and adoption-readiness patch for the 0.26 train.

- Fixes Explorer navigation, component-detail, and static-asset links when Hedron is
  mounted under a subpath (for example reverse-proxy `/app`), and requires
  `hedron-explorer>=0.26.1` from the `dev` extra.
- Fixes `hedron new`, `hedron new --flask`, and `hedron new --django` to generate the
  then-current `>=0.26.0,<0.27` dependency range rather than the obsolete 0.25 range.
- Repairs optional-integration install commands and package-index links.
- Replaces the abbreviated OIDC outline and model-demo stub with tested, runnable
  application flows.
- Reorganizes documentation around tasks, adds an actual 5-minute quick start and
  0.25.2→0.26 upgrade guide, and makes release/maturity/support claims consistent.
- Adds CI enforcement for release-train metadata, API export coverage, documentation
  ownership, generated pages, PyPI-safe package links, and scheduled external links.
- Adds checksummed release manifests, versioned evidence metadata, documentation-version
  guidance, and an exact-PyPI quick-start gate before GitHub Release creation.

No Supported API removal is included. Existing 0.26.0 applications can upgrade within
their bounded 0.26 train pin.

## 0.26.0 — 2026-08-10

Hedron 0.26.0 strengthens the Supported CRUD/admin path.

- Publishes a machine-checked inventory of Supported, Experimental, and excluded
  surfaces for `hedron-core`, `hedron`, and `hedron-explorer`.
- Validates upgrades from 0.25.2 across facade identities, diagnostics, manifests, and
  HTMX interactions.
- Verifies secured Explorer behavior and refusal of development Explorer in production.
- Verifies the documented FastAPI multi-worker, Redis, and reverse-proxy deployment
  pattern.

No Supported CRUD/admin API removal is listed. Polling remains the production path for
live status; SSE, WebSocket, streaming, and preload remain experimental.

Historical pin for this train: `hedron>=0.26.0,<0.27`. Current tip is
[Upgrade to 0.27](upgrade.md) / [What’s new in 0.27](whats-new-0.27.md).

## 0.25.2 — 2026-08-10

Security and correctness patch for fragment authorization, CSRF cookies, mount paths,
Redis job/status state, adapter lifecycle handling, and streaming cache headers.

## 0.25.1 — 2026-08-09

Restored a resolvable charts extra, repaired adopter recipes, and hardened the release
workflow so failed PyPI publication cannot create a GitHub Release.

## 0.25.0 — 2026-08-09

Added the production reference-app archetype, critical-path budgets, explicit
experimental-UI quarantine, and release evidence assets.

## Earlier releases

Use the [release archive](whats-new-archive.md) for 0.10–0.24. The project does not
rewrite historical release pages to describe current maturity; use
[What’s ready today](whats-ready.md) for present-day capability claims.
