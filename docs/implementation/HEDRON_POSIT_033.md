# Phase 0.33 implementation plan: `hedron-posit`

This plan turns [RFC-0066](../rfcs/RFC-0066-HEDRON-POSIT.md) into reviewable work. It is not
authorization to implement the Draft RFC. The contract-probe stage must finish and RFC-0066 must be
Accepted before package movement begins.

## Outcome

Ship `hedron-posit` `0.33.0` Beta as the preferred Hedron deployment facade for local Uvicorn,
Posit Workbench, and the declared Posit Connect matrix. Keep `hedron-workbench` `0.33.0` as a
supported compatibility package with no dependency cycle or behavior regression.

The phase is complete only when native Connect is proven live, the optional bridge is proven on its
named topology, and every row in
[`release-gate-0.33.toml`](../acceptance/release-gate-0.33.toml) is Verified.

## Decisions already locked

| Topic | Decision |
|---|---|
| Primary facade | `hedron_posit.HedronPosit` with one nested frozen `PositConfig` |
| Dependency direction | `hedron-posit -> hedron + fastapi-workbench`; `hedron-workbench -> hedron-posit`; no reverse import |
| Compatibility type | `HedronWorkbench` remains a distinct subclass that translates old arguments |
| Compatibility window | Supported through at least 0.35; no 0.33 runtime deprecation warning |
| Product resolution | Explicit setting, protected Connect marker, existing Workbench evidence, then inactive; conflicts fail |
| Native Connect floor | Protocol floor 2024.11.0; cut floor also respects Posit's then-current support window |
| Native cookie behavior | Pass request cookies unchanged; preserve existing owned response-cookie repair |
| Bridge | Off by default; fixed versioned headers; 16 KiB decoded limit; owned-cookie allowlist; fail closed |
| Identity | Connect credentials/session headers are application inputs, never Hedron authentication |
| Publishing/admin | Out of scope |

## Stage 0 — contract probe and RFC acceptance

**Goal:** replace assumptions with sanitized live evidence before creating a compatibility protocol.

Deliverables:

- `tests/fixtures/posit-connect/` sanitized ASGI scope/response fixtures for GUID and vanity mounts;
- a private evidence record for licensed server versions/topologies, with only redacted results
  committed;
- native request/response cookie traces using synthetic non-secret values;
- HTTP, HTMX, redirect, asset, OpenAPI, lifespan, worker restart, and WebSocket observations;
- proof of whether the claimed legacy request-cookie loss exists on a reproducible version/topology;
- exact minimum/current/off-host matrix recorded in the acceptance packet; and
- RFC-0066 revision and acceptance decision.

Stop conditions:

- If current Supported Connect does not provide the documented base header or matching `root_path`,
  native mode is blocked; do not compensate with the cookie bridge.
- If the legacy cookie failure cannot be reproduced, remove bridge implementation from 0.33 and
  retain only the documented extension point.
- If bridge headers do not pass Connect without appearing in ordinary logs/evidence, redesign or
  drop the bridge; do not waive redaction.

Exit: `CONTRACT-033` can move from Planned only after the matrix and wire-contract decision are
recorded and RFC-0066 is Accepted.

## Stage 1 — additive package extraction

**Goal:** establish the package boundary with no deployment behavior change.

Repository changes:

```text
packages/hedron-posit/
  pyproject.toml
  README.md
  CHANGELOG.md
  LICENSE
  src/hedron_posit/
    __init__.py
    app.py
    cli.py
    config.py
    detect.py
    diagnostics.py
    middleware.py
    resolve.py
    urls.py
    py.typed

packages/hedron-workbench/src/hedron_workbench/
  app.py          # compatibility subclass/argument translation only
  cli.py          # delegates, preserves command name/output compatibility
  *.py            # public compatibility re-exports where documented
```

Work items:

1. Add the distribution, workspace member, `hedron[posit]` extra, build metadata, type marker,
   license, changelog, package page, and isolation test.
2. Move Hedron-specific app/URL/middleware code to `hedron_posit`; preserve git history where
   practical. Do not move generic resolver/normalizer/runner behavior out of `fastapi-workbench`.
3. Add `HedronWorkbench(HedronPosit)` with exact translation of all public 0.32 constructor
   keywords and markers.
4. Delegate `hedron-workbench` CLI commands to the new implementation while preserving exit codes,
   text/JSON schema, pre-import discovery, factory behavior, signals, and shutdown.
5. Prove `fastapi-workbench` imports no Hedron package, `hedron-posit` imports no
   `hedron-workbench`, and clean dependency resolution has no cycle.

Test locations:

- `tests/unit/test_posit_isolation.py`
- `tests/adapters/posit/test_compat.py`
- existing `tests/adapters/workbench/`
- existing `tests/integration/test_workbench_*.py`
- `tests/upgrade/test_0_32_to_0_33_posit.py`

Exit: `PACKAGE-033`, inactive `PARITY-033`, and Workbench compatibility tests pass before any
Connect-specific behavior lands.

## Stage 2 — product resolver and native Connect

**Goal:** make Connect a first-class, typed deployment rather than a request-time side effect.

New modules:

```text
src/hedron_posit/products.py
src/hedron_posit/connect.py
src/hedron_posit/cookies.py
```

Work items:

1. Implement frozen `PositConfig`, `ConnectConfig`, `ResolvedPositDeployment`, and `PositStatus`,
   plus string enums with strict parsing and redacted representations.
2. Implement a pure resolver accepting an explicit environment/scope mapping in tests. Record
   evidence kinds, reject conflicting Connect/Workbench signals, and keep explicit product choice
   separate from header trust.
3. Move existing Connect base/header validation and response-cookie repair behind the resolved
   Connect path. Reject duplicate base headers and base/root mismatches.
4. Preserve the existing local/browser/durable URL distinction. Workbench session URLs remain
   ephemeral; Connect GUID and vanity URLs are durable only after trusted validation.
5. Add bounded cookie-loop diagnostics without storing identifiers or values.
6. Extend `run`, `check`, and `doctor` with stable text/JSON status. `doctor --live` probes a
   synthetic app; it never requests or prints real authentication material.
7. Run the licensed native matrix and attach only redacted pass/fail/version/topology evidence.

Required test groups:

- resolver precedence, deprecated marker, conflicts, explicit simulation, and inactive parity;
- GUID/vanity/root-path/base-header positive and adversarial cases;
- HTTP/HTMX/history/OOB, redirects, assets, docs/OpenAPI, CSRF, session login/logout;
- WebSocket origin/path, one and multiple workers, restart/scale, and disconnect cleanup;
- public/private content without interpreting Connect identity headers; and
- local and `hedron-workbench` rollback.

Exit: `CONNECT-033`, native portions of `REVIEW-033`, and the native `PERF-033` budget pass.

## Stage 3 — authenticated bridge v1

**Goal:** repair only a reproduced legacy request-cookie gap on one documented topology.

Implementation shape:

- `BridgeCookieRegistry`: app-owned, mutable only before lifespan startup, frozen afterward;
- `AuthenticatedCookieBridgeMiddleware`: outermost Posit middleware, Connect-only, no-op unless
  explicitly enabled;
- secret holder with redacted `repr`, current/previous slots, and bounded rotation overlap;
- singular v1 auth/cookie header parser with base64url validation and strict limits; and
- canonical cookie merge that admits only registered names and rejects conflicts.

Adversarial corpus:

- direct-to-Connect bypass and client-supplied bridge headers;
- missing, weak, wrong, duplicated, rotated, or leaked-looking secrets;
- malformed/overlong base64, decoded 16 KiB boundary, too many pairs, invalid tokens/controls;
- duplicate owned names, identical native/bridge values, conflicting values, and unowned platform
  cookies;
- late cookie registration, plugin load ordering, two middleware instances, and multiple workers;
- Connect proxy-header/access/application log capture and exception/status redaction; and
- rollback from bridge to native without invalidating valid Hedron sessions unnecessarily.

Operations packet:

- one version-controlled reference proxy template with placeholders, never a committed secret;
- topology diagram, direct-access firewall rule, TLS and WebSocket configuration;
- secret generation, dual-slot rotation, emergency disable, and rollback steps;
- startup/readiness probes that reveal no secret or cookie data; and
- explicit Supported Connect/proxy versions and exclusions.

Exit: `BRIDGE-033` and bridge portions of `REVIEW-033`/`PERF-033` pass. No simulated test can replace
the live repaired-session run.

## Stage 4 — release closure

Work items:

1. Complete `docs/guides/posit.md`, migration material, package reference, native and bridge runbooks,
   troubleshooting, and release notes.
2. Run clean wheel/sdist/editable/offline installs for `hedron-posit`, `hedron[posit]`, direct
   `hedron-workbench`, and `hedron[workbench]`; test minimum/current dependencies and Python
   3.11–3.14.
3. Verify 0.32 -> 0.33 upgrade, same-process import compatibility where supported, rollback,
   uninstall, mixed-train rejection, and no optional import leakage.
4. Complete independent security review, SBOM, provenance, license inventory, vulnerability
   disposition, full tests, docs strict build, and release rehearsal.
5. Update readiness/maturity inventories only after every gate is Verified.

Exit: `DOCS-033`, `REVIEW-033`, `REGRESS-033`, and `PKG-033` Verified; zero Deferred.

## Performance budgets

These are CI regression ceilings, not latency SLAs:

- inactive product resolution/no-op: p95 <= 5 ms over 1,000 in-process calls;
- existing Workbench normalization: retain the 5 ms p95 `PERF-029`/`PERF-030` ceiling;
- native Connect validation/response repair: p95 <= 5 ms over 1,000 in-process calls; and
- bridge authentication, 16 KiB-bounded decode, filter, and merge: p95 <= 10 ms over 1,000 calls.

Native mode must not parse bridge headers or build a per-request cookie registry. Repeated scope
normalization must remain byte-idempotent and normalizer count must equal one.

## Risk ledger

| Risk | Prevention / exit evidence |
|---|---|
| Dependency cycle during rename | Import graph checker and clean resolver in `PACKAGE-033` |
| Existing Workbench users break | Compatibility subclass plus full 0.32 corpus and upgrade fixture |
| Connect version assumptions drift | Exact cut matrix, protocol floor, current release lane, live smoke |
| Bridge becomes an auth bypass | Explicit mode, protected runtime, singular authenticated headers, direct-path denial |
| Cookie leakage in logs/evidence | Raw-header removal, redaction corpus, proxy logging warning, independent review |
| Cookie collision/session fixation | Owned-name freeze, native/bridge conflict rejection, no platform-cookie restoration |
| Double path/cookie rewriting | One normalizer invariant and idempotence corpus |
| New facade conflates platform identity | Identity headers remain pass-through and are excluded from auth APIs |
| Feature cannot roll back | Native default, bridge kill switch, compatibility package, upgrade/rollback rehearsal |

## Definition of done

- The same source-level `HedronPosit` app passes local, Workbench, and Supported native Connect.
- The reference bridge repairs a reproduced legacy failure without admitting unowned cookies or
  weakening native mode.
- Existing `HedronWorkbench` imports/CLI/configuration remain supported and behaviorally compatible.
- No product path applies more than one normalizer or trusts an ambiguous product/header signal.
- All package, security, performance, operations, documentation, and release gates are Verified
  with zero Deferred.
