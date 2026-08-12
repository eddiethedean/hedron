# RFC-0063: Standalone FastAPI Workbench extraction

**Status:** Accepted
**Phase:** 0.30 (`v0.30.0`; `fastapi-workbench` `1.0.0`)
**Stability:** `beta` (both packages)
**Evidence:** [RELEASE_0_30.md](../acceptance/RELEASE_0_30.md) ·
[release-gate-0.30.toml](../acceptance/release-gate-0.30.toml) ·
[production-grade-inventory-030.toml](../acceptance/production-grade-inventory-030.toml)
**Tracking:** [#135](https://github.com/eddiethedean/hedron/issues/135)
**Related:** D-058; [RFC-0062](RFC-0062-POSIT-WORKBENCH-ADAPTER.md); [ROADMAP §0.30](../ROADMAP.md)

## Summary

Extract generic Posit Workbench / RStudio Server deployment behavior from
`hedron-workbench` into a framework-neutral `fastapi-workbench` distribution
(import `fastapi_workbench`) developed in this monorepo. Plain FastAPI
applications receive the hands-off `fastapi-workbench run module:app` experience
without installing Hedron. `hedron-workbench` 0.30 declares
`fastapi-workbench>=1.0.0,<2.0`, delegates generic resolver/middleware/runner
behavior, and retains only Hedron-specific integration.

## Motivation and background

Phase 0.29 shipped production-grade `hedron-workbench` by reimplementing observed
[fastapi-workbench 0.3.4](https://github.com/eddiethedean/jwt-user-management/tree/main/fastapi_workbench)
(MIT) without a runtime dependency. D-058 replaces that boundary for 0.30+ with
an explicit bounded dependency on a monorepo-owned generic package so plain
FastAPI and Hedron share one Workbench implementation.

## Proposed design

### Package boundary

| Surface | `fastapi-workbench` 1.0.0 | `hedron-workbench` 0.30.0 |
|---|---|---|
| Distribution | Independent semver; PyPI `fastapi-workbench` | Coordinated Hedron train `0.30.0` |
| Hosts | Plain FastAPI ASGI HTTP/WebSocket | `Hedron()` and plain FastAPI + Hedron routers |
| Automatic | `fastapi-workbench run` / factory | `hedron-workbench run` (delegates generic launcher) |
| Explicit | Idempotent `workbenchify` | Same + Hedron cookie repair for owned cookies |
| Native facade | — | `HedronWorkbench` |
| Dependency | Starlette + Uvicorn only | `fastapi-workbench>=1.0.0,<2.0`, public `hedron` |
| Diagnostics | `FWB-*` | `HED-WB-*` for Hedron-only failures; generic errors translated |

### Environment namespaces

Primary generic namespace: `FASTAPI_WORKBENCH_*`. Compatibility aliases from 0.3.4
(`WORKBENCH_FORCE`, `BASE_PATH`, `PUBLIC_BASE_URL`, `HOST`, `PORT`, etc.) warn via
`FWB-0008`. Hedron launcher additionally exports `HEDRON_ROOT_PATH` and reads
`HEDRON_WORKBENCH_*` (mapped to generic keys before resolution).

Generic root-path export: `FASTAPI_WORKBENCH_ROOT_PATH`. Hedron adds
`HEDRON_ROOT_PATH` for construction-time cookie Path.

### Public API (`fastapi_workbench`)

- `WorkbenchConfig`, `ResolvedDeployment`, `WorkbenchMode`, `WorkbenchTopology`
- `resolve_deployment`, `parse_rserver_url_output`
- `WorkbenchPathMiddleware`, `workbenchify`
- `export_workbench_state`, `prepare_app`, `run_target`
- `fastapi-workbench run` / `check` / `dry-run` / `doctor`

### Hedron-only surface (`hedron_workbench`)

- `HedronWorkbench`, Hedron URL/redirect/asset adapters
- `export_hedron_state` (generic export + `HEDRON_ROOT_PATH`)
- `hedron-workbench` CLI branding

### Production-grade scope

`fastapi-workbench` 1.0.0 is production-grade for plain-FastAPI Workbench
deployment on the declared Supported inventory. `hedron-workbench` 0.30.0
remains production-grade for Hedron specialization only. Neither release
declares Hedron `1.0`.

## Alternatives considered

1. **Continue reimplementing without dependency.** Rejected — duplicate resolver/runner
   corpora diverge; D-058 accepted monorepo ownership.
2. **Vendor upstream 0.3.4.** Rejected — untracked copy; same as RFC-0062.
3. **Depend on external PyPI 0.3.4.** Rejected — first monorepo release is `1.0.0`
   with explicit migration.

## Security implications

Same trust boundaries as RFC-0062: no import-time activation, bounded
`rserver-url` subprocess, loopback bind defaults, redacted diagnostics,
fail-closed mount/origin validation. Generic package never imports Hedron.
Independent SECURITY-030 review covers both packages.

## Accessibility implications

No new UI. Plain FastAPI and Hedron apps reuse existing page semantics.

## Performance implications

Shared normalization and launcher budgets (`PERF-030`). No native acceleration.

## Testing strategy

- Framework-neutral corpora under `tests/workbench/` (path parity, resolver)
- Package isolation: `fastapi_workbench` imports no Hedron code
- Hedron adapter tests prove delegation + `HEDRON_ROOT_PATH` handoff
- REALWB-030: plain FastAPI reference app + Hedron reference app
- Upgrade fixtures: 0.3.4→1.0.0, 0.29→0.30

## Compatibility and migration

- Public 0.3.4 CLI/env surfaces migrate to `1.0.0` with documented aliases
- `hedron-workbench` 0.29→0.30: add `fastapi-workbench` dependency; public API stable
- Uninstall either package restores ordinary Uvicorn behavior

## Open questions

None remaining for acceptance.

## Acceptance criteria

Every 0.30-owned gate row Verified with zero Deferred.
`python scripts/verify_pkg_30.py` passes without `--allow-planned` at cut.
Close [#135](https://github.com/eddiethedean/hedron/issues/135) only then.
