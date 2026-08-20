# Phase 0.52 upgrade and rollback fixtures

**Status:** Planned; Stage 0 refine against Published in-tree `v0.51.2` (D-090)<br>
**Planning baseline:** Published in-tree `v0.51.2`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.51.2`<br>
**Target:** Hedron `v0.52.0`<br>
**Decision/RFC:** D-089 / D-090 / [RFC-0079](../rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md)<br>
**Tracking:** [#522](https://github.com/eddiethedean/hedron/issues/522)

Baseline conformance and Posit capture remains read-only during Stage 0.
PKG-052 upgrade source is **0.51**, not 0.50. Do not start Stage 1 during
this refine. Living tip stays `v0.51.2`.

## 0.51.2 install fixtures

1. `hedron-conformance` exposes `CONTRACT_VERSION = "hedron-portable-1"`,
   `Capability`, and `load_bundled_fixtures()`.
2. Default corpus is top-level `fixtures/*.json` only.
3. `hedron-runtime-node` / `hedron-runtime-java` remain tooling-grade
   repository/tooling artifacts until `RUNTIME-052` / `PKG-052`.
4. `HedronPosit` helpers: `href` / `href_for`, `redirect` / `redirect_for`,
   `browser_url` / `browser_url_for`, `external_url` / `durable_url`.
5. `cookie_path_for_mount` and `workbenchify` own cookie Path repair;
   `ConnectCookieMode.NATIVE` Supported; bridge stays `drop_supported`.
6. CLI: `hedron-posit check` / `run` / `doctor` (no `--matrix` yet).

## Honesty fixtures (Stage 1 migration)

1. Extending `hedron-portable-1` requires negotiation; do not silently
   replace `CONTRACT_VERSION`.
2. Node/Java must not be marketed as FastAPI, browser, or complete Hedron.
3. Supported Connect authenticated-header cookie bridge stays dropped.
4. Rollback to 0.51.2 restores repository-only evaluator paths and
   app-owned cookie/redirect adaptation where Stage 1 closed those gaps.

## Frozen 0.51.2 Posit helper names

`href`, `href_for`, `redirect`, `redirect_for`, `browser_url`,
`browser_url_for`, `external_url`, `durable_url`, `durable_url_for`,
`cookie_path_for_mount`, `workbenchify`, `ConnectCookieMode`.

## Hosts

Flask/Django stay `projection_adapter`. No WSGI Posit runtime rewrite in
Stage 0. Explorer package-health may ingest conformance reports later
under `CI-052` without requiring GitHub.
