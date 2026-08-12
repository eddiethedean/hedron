# RFC-0062: Production-grade Posit Workbench deployment adapter

**Status:** Accepted
**Phase:** 0.29 (`v0.29.0`; baseline Published `v0.28.2`)
**Stability:** `beta` (package + public API)
**Evidence:** [RELEASE_0_29.md](../acceptance/RELEASE_0_29.md) ·
[release-gate-0.29.toml](../acceptance/release-gate-0.29.toml) ·
[production-grade-inventory-029.toml](../acceptance/production-grade-inventory-029.toml)
**Tracking:** [#134](https://github.com/eddiethedean/hedron/issues/134)
**Related:** D-015, D-051 (MOUNT-020), D-053, D-056, D-057;
[RFC-0028](RFC-0028-DEPLOYMENT.md); [RFC-0056](RFC-0056-PRODUCTION-QUALITY.md);
[ROADMAP §0.29](../ROADMAP.md); [MOUNT.md](../api/MOUNT.md)

## Summary

Ship optional `hedron-workbench` (import `hedron_workbench`) so an existing FastAPI
Hedron app runs unchanged behind Posit Workbench / RStudio Server by changing only
the launch command. An explicit ASGI wrapper remains available. The adapter
composes Hedron's trusted mount, redirect, CSRF, cookie, asset, OpenAPI, and
Explorer contracts. Installing or importing the package, or setting `RS_SERVER_URL`,
never monkey-patches FastAPI/Hedron or grants trust.

Behavior baseline is observed [fastapi-workbench 0.3.4](https://github.com/eddiethedean/jwt-user-management/tree/main/fastapi_workbench)
(MIT). Hedron reimplements adopted behavior with attribution and does **not**
vendor or depend on that package.

## Motivation and background

Posit Workbench and RStudio Server expose session apps under dynamic prefixes
(`/s/<id>/p/<port>/`, `/proxy/<port>/…`). FastAPI needs ASGI `root_path` and
Hedron needs `HEDRON_ROOT_PATH` **before** `Hedron()` construction because
session and CSRF cookie `Path` are frozen then. Adopters should not hand-assemble
`rserver-url`, cookie scoping, and HTMX prefixing. A separate optional package
keeps Posit detection out of `hedron-core` and the flagship.

## Proposed design

### Package boundary

| Surface | Contract |
|---|---|
| Distribution | `hedron-workbench` `0.29.0` Beta; extra `hedron[workbench]` |
| Hosts | `Hedron()` and plain FastAPI + Hedron routers over ASGI HTTP/WebSocket |
| Automatic | `hedron-workbench run module:app` and `module:create_app --factory` |
| Native facade | `HedronWorkbench`, inactive outside Workbench and never double-wrapped |
| Explicit | Idempotent `workbenchify(app, *, config=...)` |
| Dependency | May import public `hedron` / Starlette / Uvicorn. Core, flagship, Flask, Django never import it |
| Connect | Experimental trusted-peer + `rstudio-connect-app-base-url` only |

### Public API

- `WorkbenchMode`: `auto` / `on` / `off`
- `HedronWorkbench`: `Hedron` subclass with pre-construction mount resolution
- Immutable `WorkbenchConfig` and `ResolvedDeployment`
- `resolve_deployment(...)` — side-effect-free
- `WorkbenchPathMiddleware`, `workbenchify`
- `hedron-workbench run` / `check` / `--dry-run` with `--format text|json`
- Thin URL helpers over `normalize_mount_path`, `prefix_local_path`, `redirect_local`, `SafeUrl`

### Configuration precedence (per setting)

1. Explicit Python/CLI value
2. `HEDRON_WORKBENCH_*`
3. Compatibility alias (`WORKBENCH_FORCE`, `WORKBENCH_DEBUG`, `BASE_PATH`, `PUBLIC_BASE_URL`, `HOST`, `PORT`) — warn
4. Trusted `rserver-url` when `RS_SERVER_URL` is non-empty
5. Request-scope signals

Namespaced values win. Conflicting explicit mount/origin fail closed.
`RS_SERVER_URL` requests discovery only — not a browser base, trust grant, or identity.

### Launcher ordering (mandatory)

1. Bind loopback socket (including port `0`) — no check-then-bind race
2. Exec configured absolute `rserver-url` binary **without a shell**
3. Export `HEDRON_ROOT_PATH` and namespaced public-base state
4. Import app object or call factory
5. Wrap once
6. Serve the pre-bound socket

Defaults: loopback, one worker, no reload, exact loopback proxy allowlist.
The pre-bound runner rejects reload and multi-worker topologies; operators use
an external supervisor when they need multiple processes.

### Normalization pipeline

Only HTTP and WebSocket scopes. Order: recognize encoded absolute target;
percent-decode once; accept only `http`/`https`; extract path/query without
trusting authority; canonicalize Workbench root; strip at most one exact
segment-boundary mount prefix. `/proxy/<decimal-port>/<rest>` only in
root/mount position. Double application is byte-identical. Scope is copied,
never mutated in place.

When an explicit resolved mount exists and ASGI `root_path` is absent, the
middleware establishes that exact root only when the request path matches the
mount boundary. Oversized, traversal, unsafe absolute, and conflicting-query
targets receive explicit 4xx responses.

### Supported product matrix

- Posit Workbench / RStudio Server session and project proxy shapes documented by
  `rserver-url -l <port>` (path or full URL)
- Official image `posit/workbench` (linux/amd64), pinned in REALWB-029
- Python 3.11–3.14, Uvicorn Supported
- Ordinary local Uvicorn and generic ASGI `root_path` remain unchanged (`mode=off` no-op)

### Diagnostics

Stable `HED-WB-*` codes. Session/project IDs and token-like path/query redacted
before text, JSON, logs, and evidence.

## Alternatives considered

1. **Vendor fastapi-workbench.** Rejected — untracked copy, parallel safety model, FluxLit/Alembic surface.
2. **Put detection in hedron.** Rejected — D-015; Posit-specific code stays in the satellite.
3. **Import-time auto-wrap when `RS_SERVER_URL` is set.** Rejected — implicit activation is a non-goal.
4. **Fix cookie Path at request time.** Rejected — Starlette SessionMiddleware path is construction-time.

## Security implications

Absolute-target decode, untrusted forwarded headers, open redirects, traversal,
cookie Path, subprocess argv (no shell), loopback bind, import timing, and
license/token redaction are in scope for SECURITY-029. Workbench authentication
is not Hedron identity. Connect headers are ignored unless the peer is trusted
under the existing Hedron proxy model.

## Accessibility implications

No new UI. PAGE/FRAGMENT/Explorer-off behavior reuses existing a11y contracts.
Human AT is not claimed for this package.

## Performance implications

Middleware copies scope only when normalization applies. Locked startup and
per-request overhead budgets are PERF-029. Native acceleration is unrelated.

## Testing strategy

- Pure resolver unit tests (no Workbench, no listener)
- ASGI path fixtures including 0.3.4 adopted behaviors
- Hedron URL/CSRF/cookie/asset integration
- Fake `rserver-url` runner tests
- Adversarial security corpus
- Docker REALWB-029 using `WORKBENCH_API_KEY` as `PWB_LICENSE`
- Upgrade/rollback from 0.28.2; non-Workbench parity

## Compatibility and migration

New optional package. Existing 0.28 apps need no source change. Launch command
becomes `hedron-workbench run module:app` on Workbench. Uninstall restores
ordinary Uvicorn. Compatibility aliases warn. No Flask/Django claim.

## Open questions

None remaining for acceptance. REALWB image tag is pinned in the inventory
(`posit/workbench:2026.07.0` or latest 2026.07 patch available at cut).

## Acceptance criteria

Every 0.29-owned gate row Verified with zero Deferred.
`python scripts/verify_pkg_29.py` passes without `--allow-planned` at cut.
Production-grade label applies only to the declared Supported inventory.
Close [#134](https://github.com/eddiethedean/hedron/issues/134) only then.
