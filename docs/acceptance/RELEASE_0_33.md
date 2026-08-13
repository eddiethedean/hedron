# Hedron `v0.33` unified Posit adapter acceptance

**Status:** **Published** as `v0.33.0` (2026-08-13).

Phase 0.33 ships **`hedron-posit` `0.33.0` Beta** as the preferred local / Posit Workbench / Posit
Connect facade and keeps **`hedron-workbench` `0.33.0` Beta** as a supported compatibility package.
Baseline: Published `v0.32.0`. Evidence is indexed by
[`release-gate-0.33.toml`](release-gate-0.33.toml). **Zero Deferred:** every 0.33-owned gate must be
Verified at cut.

Owning decision: [D-061](../DECISIONS.md). Design: [RFC-0066](../rfcs/RFC-0066-HEDRON-POSIT.md)
(**Accepted** 2026-08-13 after Stage 0 probe). Implementation:
[HEDRON_POSIT_033](../implementation/HEDRON_POSIT_033.md). Tracking:
[#167](https://github.com/eddiethedean/hedron/issues/167).

## Release contract

- `hedron-posit==0.33.*` depends on `hedron>=0.34,<0.35` and
  `fastapi-workbench>=1,<2`; it never imports `hedron-workbench`.
- `hedron-workbench==0.33.*` depends on `hedron-posit>=0.34,<0.35` and retains its public 0.32
  imports, CLI, configuration, and Beta maturity.
- `hedron[posit]` installs the new facade; `hedron[workbench]` remains installable.
- Native Connect is the default and the only Supported Connect cookie lane in 0.33.
- `authenticated_header_v1` is **not Supported** in 0.33 (Stage 0
  `BRIDGE_DECISION=drop_supported`); retain docs-only extension-point language, no Supported
  bridge implementation.
- Protocol floor for native Connect is 2024.11.0. Supported live floor is
  Connect **2025.06.0** (licensed on-host GUID evidence, amd64 image). Current
  verified lane remains Connect **2026.07.0**.
- Python 3.11–3.14 remain the supported interpreter matrix.

## Entry criteria

- [x] Phase 0.33 ownership recorded in ROADMAP / D-061
- [x] Draft RFC-0066 and implementation plan present
- [x] Tracking issue #167 bound to phase and gate IDs
- [x] Sanitized licensed Connect contract probe completed
- [x] Exact native and bridge version/topology matrix recorded
- [x] Legacy cookie failure reproduced or bridge removed from 0.33 scope
- [x] RFC-0066 Accepted
- [x] Planned release-gate rows and checker ownership reviewed

## Exact cut matrix

Stage 0 evidence: [`realconnect-033/RESULT.log`](realconnect-033/RESULT.log),
[`CONNECT_PROBE_033.md`](CONNECT_PROBE_033.md),
[`tests/fixtures/posit-connect/`](../../tests/fixtures/posit-connect/).

| Lane | Version/topology | Required evidence |
|---|---|---|
| Native minimum | Connect **2025.06.0** on-host (pinned `posit/connect@sha256:d1921d6dd4344f2e0c3066a29338fc13f7f9ea8b6b31330a7cc6d7df4b4fcfa0`, linux/amd64); protocol eligibility floor remains 2024.11.0 | Licensed GUID mount: product/base/`root_path`, HTTP/HTMX/WS/session/CSRF, native request cookies — [`realconnect-033-202506/RESULT.log`](realconnect-033-202506/RESULT.log) |
| Native current | Connect **2026.07.0** (pinned `posit/connect@sha256:ae5753745ddc576cca06ad7466a370e18bc54580b154f4b5bcbef9390f1c54a9`) | Same plus assets/OpenAPI/redirect/diagnostics; scale/restart expansion at `CONNECT-033` |
| Native off-host | **Experimental** — licensed Kubernetes off-host not exercised in Stage 0 | N/A for Supported claims |
| Workbench minimum | Workbench **2025.05.1** (pinned `posit/workbench@sha256:2b017722bef663940d345178d14d196d8716b37d9cf8a52d3da7caba477e7d23`, linux/amd64) | `hedron-workbench`, `hedron-posit`, and `fastapi-workbench` launcher/HTTP/WS/session/CSRF — [`realwb-030-202505/RESULT.log`](realwb-030-202505/RESULT.log) |
| Workbench current | Workbench **2026.07.0** (pinned `posit/workbench@sha256:d10ee76a840e8af054d54506ed4b54bc27ee7344ee09d8c99541cd23f39b8c32`) | Same plus current-lane `REALWB-030` evidence — [`realwb-030/RESULT.log`](realwb-030/RESULT.log) |
| Bridge reference | **Out of Supported scope** (`BRIDGE_DECISION=drop_supported`) — native cookies round-trip on 2026.07.0 | Extension-point docs only; no Supported bridge wire |
| Local | Linux/macOS/Windows Python 3.11–3.14 | Ordinary Uvicorn parity and no-op product resolution |

Off-host Connect is explicitly Experimental. Supported bridge code does not ship in 0.33.

## Locked evidence gates

Gate ownership: Posit-specific rows are owned by `hedron-posit`; `PARITY-033` is owned by the
retained `hedron-workbench` compatibility package; shared train rows `REGRESS-033` / `PKG-033` are
owned by `hedron`.

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

At `v0.33.0` cut (every row Verified):

```bash
python scripts/verify_pkg_33.py
python scripts/check_release_gate.py 0.33.0 --execute-verified
```

During packet refine (historical; living tip was still on `0.32.x`):

```bash
python scripts/verify_pkg_33.py --allow-planned
python scripts/check_release_gate.py 0.32.0 \
  --evidence-manifest docs/acceptance/release-gate-0.33.toml \
  --allow-planned
```

## Exit

- [x] Exact cut matrix has no `TBD`
- [x] RFC-0066 Accepted and implementation matches it
- [x] Every 0.33-owned release-gate row Verified with zero Deferred
- [x] `hedron-posit` and retained `hedron-workbench` maturity claims match the inventory
- [ ] Close #167 after release assets are published on GitHub/PyPI
