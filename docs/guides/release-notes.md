# Releases

This is the canonical adopter-facing release history. Package-level implementation
details remain in the [package changelogs](changelog.md).

## 0.36.0 — 2026-08-13

Coordinated Beta train cut for Web Component ABI / lifecycle foundation
(D-064 / RFC-0060).

- Ships Alpha `hedron-elements` `0.36.0` with shared bridge and reference
  `hedron-example` (SSR/HTMX lifecycle; not form-associated).
- Versioned element registry, `ElementStateOwnership`, and `HED-ELEMENT-*` /
  `HED-ELEMENT-STATE-*` diagnostics.
- Fleet inventory-036 registers `hedron-elements` as incubator until 0.41.
- Pin `hedron>=0.36.0,<0.37`.

```bash
python -m pip install -U "hedron>=0.36.0,<0.37"
python -m pip install "hedron[elements]>=0.36.0,<0.37"
```

## 0.35.0 — 2026-08-13

Coordinated Beta train cut for whole-fleet production-grade closure
(D-063 / RFC-0068).

- Publishes fleet inventory `production-grade-inventory-035.toml` with dispositions
  for every publishable package/runtime.
- Tooling packages (notebook, sample-kit, sim, runtimes) reconciled to Beta tooling-grade.
- PRESENT-034 default presentation gallery remains deferred/experimental.
- Historical cut pin `hedron>=0.35.0,<0.36`. Install the current tip with the pin under
  **0.36.0** above.

## 0.34.0 — 2026-08-13

Coordinated Beta train cut for production-grade Gradio / Hugging Face client
interop (D-062 / RFC-0067).

- Ships `hedron-gradio` `0.2.0` Beta: allowlisted remote predict/stream, bounded
  files, scoped jobs, HF Space vendor helpers.
- Coordinated `hedron` / core packages `0.34.0`; `fastapi-workbench` stays `1.x`;
  MCP stays satellite `>=0.2.0,<0.3`.
- Default presentation gallery (`PRESENT-034`) deferred to whole-fleet `0.35` audit.
- Historical cut pin `hedron>=0.34.0,<0.35`. Install the current tip with the pin under
  **0.36.0** above.

## 0.33.0 — 2026-08-13

Coordinated Beta train cut for unified Posit Workbench / Connect adapter
(D-061 / RFC-0066).

- Ships `hedron-posit` `0.33.0` Beta: `HedronPosit` + `PositConfig` / native Connect.
- `hedron-workbench` `0.33.0` remains a Supported compatibility package (≥0.35).
- Supported cookie bridge dropped after Stage 0 (`BRIDGE_DECISION=drop_supported`).
- Coordinated `hedron` / core packages `0.33.0`; `fastapi-workbench` stays `1.x`;
  MCP stays satellite `>=0.2.0,<0.3`.
- Historical cut pin `hedron>=0.33.0,<0.34`. Install the current tip with the pin under
  **0.34.0** above.

## 0.32.0 — 2026-08-12

Coordinated Beta train cut for production-grade deny-by-default MCP projection
(D-060 / RFC-0065).

- Ships `hedron-mcp` `0.2.0` Beta: authenticated Streamable HTTP projection;
  Supported inventory only; mutations remain Experimental.
- Coordinated `hedron` / core packages `0.32.0`; MCP stays satellite `>=0.2.0,<0.3`.
- Security hardening: session-bound MCP principals, formula-injection evasion strip,
  optional-session scope gates, MCP cancel/session lifecycle bounds.
- Historical cut pin `hedron>=0.32.0,<0.33`. Install the current tip with the pin under
  **0.34.0** above.

## 0.31.0 — 2026-08-12

Coordinated Beta train cut for tooling-grade developer/portable conformance and the
Streamlit AST migrator (D-059 / RFC-0064 / RFC-0061).

- Tooling-grade `hedron-conformance`, `hedron-sample-kit`, `hedron-sim`, `hedron-notebook`.
- Published Node/Java evaluators (`hedron-runtime-node` / `hedron-runtime-java` `0.31.0`).
- `hedron migrate streamlit` non-executing AST assistant.
- Historical cut pin `hedron>=0.31.0,<0.32`. Install the current tip with the pin under
  **0.34.0** above.

```bash
python -m pip install -U "hedron>=0.36.0,<0.37"
hedron migrate streamlit streamlit_app.py --analyze-only --format text
```

## 0.30.0 — 2026-08-12

Coordinated Beta train cut for standalone Workbench package extraction (D-058 /
RFC-0063).

- Ships monorepo-owned `fastapi-workbench` `1.0.0` for plain FastAPI Posit Workbench /
  RStudio Server deployment without installing Hedron.
- `hedron-workbench` `0.30.0` depends on `fastapi-workbench>=1.0.0,<2.0` and delegates
  generic resolver / middleware / runner behavior.
- Historical cut pin `hedron>=0.30.0,<0.31`. Install the current tip with the pin under
  **0.34.0** above.

Historical cut used `hedron` / `hedron-workbench` on the 0.30 train and
`fastapi-workbench>=1.0.0,<2.0`. Prefer the current tip pin under **0.35.0** above.

## 0.29.0 — 2026-08-11

Coordinated Beta train cut for production-grade `hedron-workbench`.

- Ships optional `hedron[workbench]` / `hedron-workbench`: Posit Workbench /
  RStudio Server launcher that exports `HEDRON_ROOT_PATH` before import.
- Hedron-neutral polish: `Hedron(root_path=...)`, re-exported
  `resolve_mount_path_from_environ`, color-mode cookie Path.
- No auto-activation on install/import/`RS_SERVER_URL`. Flask/Django unchanged.
- Historical cut pin `hedron>=0.29.0,<0.30`. Install the current tip with the pin under
  **0.34.0** above.

## 0.28.2 — 2026-08-11

Coordinated Beta patch on the 0.28 train.

- Raises coordinated package versions / pins to `0.28.2` (historical cut pin
  `>=0.28.2,<0.29`).
- Aligns `hedron new` scaffolds and the published-quickstart release checker on
  `docs/release.toml` `pin_floor` (fixes the v0.28.1 release verify footgun).
- HTMX/OOB hardening: validated OOB swaps, select_oob conflict fail-closed,
  landmark-safe `HtmxLink` default `innerHTML`, FastAPI fragment-target auth parity,
  Flask/Django `allow_htmx_eval` + PAGE asset inject, portable Django CSRF header.
- Chart hosts listen for OOB/load lifecycle events; Plotly/Vega generation guards;
  MapLibre `coord_order`; tip `hedron-charts` `0.1.11` (floor `>=0.1.10`).
- GitHub Release create waits on quickstart verify and omits plain `linux_*` wheels.
- No Supported CRUD/admin API removal.

Install the current tip with the pin under **0.35.0** above (historical cut pin was
`>=0.28.2,<0.29`).

## 0.28.1 — 2026-08-10

Correctness and tip-honesty patch for the 0.28 train.

- Raises the `hedron[native]` floor and wires Supported native wheel publish evidence.
- Fixes Auto Experimental remediation, optional chart HTMX dispose, Flask/Django
  mount-aware static prefixes, and live `HEDRON_NATIVE_DISABLE`.
- Hardens tip-hub SSOT wrap scans and CI native/crates publish footguns.

Install the current tip with the pin under **0.35.0** above (historical cut pin was
`>=0.28.1,<0.29`).

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

Install the current tip with the pin under **0.35.0** above.

Read [Upgrade to 0.33](upgrade.md) before changing a production lockfile. Maintainer
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
[Upgrade to 0.28](upgrade.md) / [What’s new in 0.27](whats-new-0.27.md).

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
