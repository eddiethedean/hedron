# Hedron `v0.33` unified Posit adapter acceptance

Phase 0.33 ships **`hedron-posit` `0.33.0` Beta** as the preferred local / Posit Workbench / Posit
Connect facade and keeps **`hedron-workbench` `0.33.0` Beta** as a supported compatibility package.
Baseline: Published `v0.32.0`. Evidence is indexed by
[`release-gate-0.33.toml`](release-gate-0.33.toml). **Zero Deferred:** every 0.33-owned gate must be
Verified at cut.

Owning decision: [D-061](../DECISIONS.md). Design: [RFC-0066](../rfcs/RFC-0066-HEDRON-POSIT.md)
(Draft until the contract probe completes). Implementation:
[HEDRON_POSIT_033](../implementation/HEDRON_POSIT_033.md). Tracking:
[#167](https://github.com/eddiethedean/hedron/issues/167).

## Release contract

- `hedron-posit==0.33.*` depends on `hedron>=0.33,<0.34` and
  `fastapi-workbench>=1,<2`; it never imports `hedron-workbench`.
- `hedron-workbench==0.33.*` depends on `hedron-posit>=0.33,<0.34` and retains its public 0.32
  imports, CLI, configuration, and Beta maturity.
- `hedron[posit]` installs the new facade; `hedron[workbench]` remains installable.
- Native Connect is the default. Bridge v1 is off by default and Supported only for the exact live
  Connect/proxy matrix recorded at cut.
- Protocol floor for native Connect is 2024.11.0. The cut's Supported floor must also be inside
  Posit's then-current support window and is written here before `CONNECT-033` becomes Verified.
- Python 3.11–3.14 remain the supported interpreter matrix.

## Entry criteria

- [x] Phase 0.33 ownership recorded in ROADMAP / D-061
- [x] Draft RFC-0066 and implementation plan present
- [x] Tracking issue #167 bound to phase and gate IDs
- [ ] Sanitized licensed Connect contract probe completed
- [ ] Exact native and bridge version/topology matrix recorded
- [ ] Legacy cookie failure reproduced or bridge removed from 0.33 scope
- [ ] RFC-0066 Accepted
- [ ] Planned release-gate rows and checker ownership reviewed

## Exact cut matrix

Fill this table with concrete versions before RFC acceptance. `TBD` is never permitted at cut.

| Lane | Version/topology | Required evidence |
|---|---|---|
| Native minimum | TBD; >= 2024.11.0 and inside Posit support window | Licensed GUID + vanity, private + public, HTTP/WS/session/CSRF |
| Native current | TBD current stable at cut | Same plus scale/restart and upgrade behavior |
| Native off-host | TBD licensed Kubernetes execution, if declared Supported | Same functional contract and worker lifecycle |
| Workbench | Existing `REALWB-029`/`REALWB-030` floor + current cut image | Launcher, session/project proxy, HTTP/WS/session/CSRF |
| Bridge reference | TBD reproduced legacy Connect + named proxy/version | Native failure, repaired flow, bypass/rotation/log/rollback |
| Local | Linux/macOS/Windows supported Python lanes | Ordinary Uvicorn parity and no-op product resolution |

If off-host evidence is unavailable, off-host Connect is explicitly Experimental. If the bridge
reference row cannot be made concrete, bridge code does not ship as Supported.

## Locked evidence gates

Gate ownership (reviewed at packet refine): Posit-specific rows are owned by the future
`hedron-posit` distribution; `PARITY-033` is owned by the retained `hedron-workbench`
compatibility package; shared train rows `REGRESS-033` / `PKG-033` are owned by `hedron`.

| Gate | Owner | Verified means |
|---|---|---|
| `CONTRACT-033` | `hedron-posit` | Accepted RFC, exact cut matrix, public API, product evidence, protocol floor, compatibility window, dependency graph, bridge decision, and exclusions agree |
| `PACKAGE-033` | `hedron-posit` | New distribution/extra/type marker/metadata, one-way dependency graph, wheel/sdist/editable/offline installs, optional isolation, licenses, SBOM, and provenance pass |
| `PARITY-033` | `hedron-workbench` | Inactive `Hedron` parity and 0.32 `HedronWorkbench` import/type/constructor/CLI/config/status/URL/cookie behavior pass through upgrade and rollback |
| `WORKBENCH-033` | `hedron-posit` | Existing Workbench pre-import discovery, runner, HTTP/WebSocket normalization, URLs, redirects, assets, OpenAPI, session/CSRF cookies, workers, shutdown, and real-image suites pass with one normalizer |
| `CONNECT-033` | `hedron-posit` | Exact licensed native matrix passes protected product/base/root evidence, GUID/vanity URLs, HTTP/HTMX/WS, assets, redirects, OpenAPI, login/logout/session, CSRF, cookie paths, scale/restart, diagnostics, and rollback |
| `BRIDGE-033` | `hedron-posit` | Either (a) reproduced native-cookie failure is repaired on the named reference topology with full adversarial suites, or (b) Stage 0 proves native cookies round-trip and Supported bridge is absent (extension-point docs only) |
| `PERF-033` | `hedron-posit` | p95 ceilings pass: inactive <=5 ms, Workbench <=5 ms, native Connect <=5 ms, bridge <=10 ms when in scope; native does no bridge parsing and every mode has one normalizer |
| `REVIEW-033` | `hedron-posit` | Independent review covers package inversion, product/header trust, origin/mount, request/response cookies, bridge secret/proxy/bypass/replay/logging (when in scope), sessions/CSRF, diagnostics, workers, supply chain, and rollback with no unresolved critical/high finding |
| `DOCS-033` | `hedron-posit` | Copyable local, Workbench, native Connect, and bridge (when in scope) recipes, compatibility migration, health/readiness, secret rotation, failure diagnostics, kill switch, rollback, and Supported/Experimental boundaries pass review |
| `REGRESS-033` | `hedron` | Full tests, minimum/current dependencies, Python 3.11–3.14, upgrade/mixed-train/rollback/uninstall, docs strict build, and redaction/inventory checks pass |
| `PKG-033` | `hedron` | Clean consumer and offline wheelhouse rehearsal, release metadata, changelogs, inventories, tags/artifact plan, vulnerability disposition, and all 0.33 gate commands pass with zero Deferred |

## Required adversarial cases

- Conflicting explicit/Connect/Workbench evidence; spoofed or duplicate base header; base/root
  mismatch; hostile origin; traversal/encoding; token-like data in diagnostics.
- Client-supplied or duplicated bridge headers; wrong/weak/missing/rotated secret; direct path around
  proxy; proxy logging enabled; header retained downstream.
- Malformed base64url; decoded input over 16 KiB; >128 pairs; overlong/invalid cookie names or
  values; >32 custom names; late registry mutation.
- Unregistered Connect/platform cookies; identical and conflicting native/bridge owned values;
  session fixation attempt; logout and CSRF replay.
- HTTP/WebSocket, one/many workers, restart during session, late response, disconnect, and bridge
  disable/rollback.

No evidence artifact may contain real secrets, raw cookies, credentials or user-session headers,
content/session identifiers, CSRF material, or token-shaped path/query values.

## Cut verification

During packet refine (living tip still on `0.32.x`):

```bash
python scripts/verify_pkg_33.py --allow-planned
# equivalent:
python scripts/check_release_gate.py 0.32.0 \
  --evidence-manifest docs/acceptance/release-gate-0.33.toml \
  --allow-planned
```

At cut (after train bump to `0.33.0` and every row Verified):

```bash
python scripts/verify_pkg_33.py
python scripts/check_release_gate.py 0.33.0 --execute-verified
```

## Exit

- [ ] Exact cut matrix has no `TBD`
- [ ] RFC-0066 Accepted and implementation matches it
- [ ] Every 0.33-owned release-gate row Verified with zero Deferred
- [ ] `hedron-posit` and retained `hedron-workbench` maturity claims match the inventory
- [ ] Close #167 only after artifacts and evidence are published
