# Hedron `v0.11` native framework depth acceptance

Phase 0.11 delivers native Flask/Django ergonomics beyond the initial routing slices,
a bounded Django QuerySet `DataSource`, a Django forms bridge, a portable adapter test
harness, HDJ dynamic manifests / foreign namespaces / SecurityPolicy–CSP reconciliation,
optional Celery/RQ `JobBackend` bridges, and capability-labeled Flask/Django live helpers
(D-044 / D-046). Evidence is indexed by [`release-gate-0.11.toml`](release-gate-0.11.toml).

## Spec packet

- [x] ROADMAP §0.11 scope accepted; D-036 superseded by D-046; capability labels recorded.
- [x] Entry gate: 0.9/0.10 evidence remains closed; 0.11 gate TOML owns Verified/Deferred rows.

## Flask ergonomics

- [x] `HedronFlask.init_app` + `HedronBlueprint` (`page` / `component` / `action` /
  `include_component`). *(`ADP-FLK-011`)*

## Django ergonomics

- [x] `HedronDjangoConfig`, system checks, namespaced URL helpers. *(`ADP-DJG-011`)*

## Portable testing harness

- [x] Shared app-fixture scenarios across FastAPI, Flask, and Django; native clients retained.
  *(`TEST-011`)*

## Forms and QuerySet

- [x] Django forms bridge (widgets, CSRF helpers, error rendering). *(`ADP-DJG-004`)*
- [x] Bounded Django QuerySet `DataSource` with query-count / tenant / transaction evidence.
  *(`ADP-DJG-002`)*

## HDJ / CSP / inventory

- [x] Finite fingerprinted dynamic manifests, foreign namespaces, CSP reconciliation,
  CLI/Explorer inventory. *(`HDJ-DEF-011`)*

## Jobs and live hosts

- [x] Celery/RQ `JobBackend` bridges. *(`JOB-011`)*
- [x] Flask/Django live helpers with honest capability labels; polling remains Supported.
  *(`LIVE-011`)*
- [ ] Full multi-engine adapter live browser matrix — **Deferred at 0.11 cut**;
  **Superseded** in **0.24** under `polling_only` / `BROWSER-024`
  *(`LIVE-011-BROWSER`)*

## Exit

- [x] Full regression suite. *(`REGRESS-011`)*
- [x] Packaging rehearsal. *(`PKG-011`)*

**Exit met / published** as coordinated `0.11.0` (`v0.11.0`).
`LIVE-011-BROWSER` was later **Superseded** in **0.24** (`polling_only`); it does not
reopen the 0.11 train.
