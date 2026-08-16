# Hedron `v0.43` refreshable views, commands, and typed updates acceptance

**Status:** Verified in-tree as Published **`v0.43.0`** (tag/PyPI deferred). Stage 0 baseline was Published **`v0.42.0`**.  
**Target:** `v0.43.0`  
**Decision/RFC:** D-071, refined by D-073 / [RFC-0070](../rfcs/RFC-0070-REFRESHABLE-VIEWS.md)

Phase 0.43 adds a high-level view/command/update model over Hedron's existing region and
`InteractionResult` stack. It does not remove the stable low-level surface, add a general reactive
runtime, or change the published 0.42 train during planning.

Implementation requirements:
[INTERACTION_HANDLES_043](../implementation/INTERACTION_HANDLES_043.md). Public contract:
[REFRESHABLE_VIEWS](../api/REFRESHABLE_VIEWS.md). Capability inventory:
[`interaction-capability-inventory-043.toml`](interaction-capability-inventory-043.toml). Evidence
index: [`release-gate-0.43.toml`](release-gate-0.43.toml). Upgrade fixtures:
[upgrade-fixtures-043](upgrade-fixtures-043.md).

## Release contract

- `@app.refreshable` / `FragmentHandle` own renderer, route, host, controls, updates, tests, and
  metadata without copied region ids/selectors/URLs.
- `@app.command` / `ActionHandle` provide explicit POST+CSRF mutation handles without changing
  existing `@app.action` semantics.
- Handle classes freeze two-slot input/content-or-result generics, a versioned authoritative base
  descriptor, and one structural binding-adapter seam for additive 0.44 specialization.
- 0.43 binding validates route/query structure and safe encoding; the normal GET owns full request
  validation. Action handles wire explicit-field forms but do not generate model fields.
- `refresh(view)` sends bounded refresh intents that rerun normal GET routes; `Patch`/`PatchSet`
  provide direct one-response updates.
- The server output is canonical; missing client targets work and conflicting targets fail closed.
- Host loading/error/focus/a11y/no-JS behavior is deterministic and tested.
- Explorer, CLI, `AppScenario`, adapters, and docs speak the same view/command/update language while
  exposing equivalent low-level mechanics and labeling undeclared command effects dynamic/observed.
- Existing 0.42 region, interaction, adapter, and package fixtures pass unchanged.
- No required browser framework/asset, global store, hydration, Node consumer build, or live
  transport is introduced.

## Exact gate matrix

| Gate | Verified means |
|---|---|
| `VIEW-043` | Handles, hosts, generated/explicit paths/ids, structural binding, GET-authoritative validation, renderer introspection, async/DI/mount behavior pass. |
| `COMMAND-043` | Command handles, POST/CSRF, native controls/explicit-field forms, errors, ordinary HTTP fallback, and no 0.44 field generation pass. |
| `UPDATE-043` | Refresh intents and Patch/PatchSet translation, bounds, ordering, target authority, status/cache/OOB behavior pass. |
| `SECURITY-043` | App ownership, target disagreement, authz/CSRF, redaction, unsafe input, and resource-limit adversarial matrix passes. |
| `A11Y-043` | Native controls, semantic hosts, busy/error/focus/announcements, keyboard/no-JS/reduced-motion/forced-color/zoom pass without a new human-AT claim. |
| `BROWSER-043` | Chromium/Firefox/WebKit loading, fan-out, cancellation, late/disconnected/nested hosts, history, cleanup pass. |
| `TOOLING-043` | Base descriptor, dynamic/observed graph/preview, CLI checks, scaffold, and handle-based AppScenario experience pass. |
| `COMPAT-043` | 0.42 unchanged/mixed/migrated fixtures, fixed generic/descriptor/binding seams, 0.44 handoff, FastAPI/Flask/Django conformance, and rollback pass. |
| `PERF-043` | No required asset; relative/absolute response overhead, fan-out/patch latency, allocation, payload, and memory budgets pass. |
| `DOCS-043` | API, guides, migration, PE, security, a11y, testing, errors, examples, and limitations are complete and claim-honest. |
| `REGRESS-043` | Full supported suite passes with zero phase-owned unresolved blocker/high regression. |
| `PKG-043` | Clean wheel/source/import matrix, inventory, release rehearsal, and zero-Deferred gate verification pass. |

Commands in the gate manifest are reserved names until their implementations land. A reserved
command name is not evidence.

## Stage 0 entry

- [x] D-071 records the accepted phase; D-073 reconciles its handoff to 0.44.
- [x] RFC-0070, API contract, implementation requirements, capability inventory, release gate,
  acceptance packet, upgrade fixtures, and traceability references exist.
- [x] Published/living baseline remains `v0.42.0`; no package or runtime version changed.
- [x] D-072/RFC-0071 context is reconciled: 0.43 owns the base runtime and reserves only explicit
  generic/descriptor/binding extension seams, not 0.44 model/form/effect/class features.
- [x] Tracking issue [#311](https://github.com/eddiethedean/hedron/issues/311) is bound to every 0.43 gate.
- [x] Stage 1 baselines the existing region path before facade implementation.

## Functional acceptance

- [x] The scaffold refresh example contains no visible region/id/selector/allowlist/`swap` code.
- [x] A refreshable handle is the sole declared source for initial render, refresh route, control,
  output identity, diagnostics, and scenario tests.
- [x] Generated and explicit paths/keys behave under routers, mounts, reverse proxies, sync/async,
  dependencies, and exceptions.
- [x] Bound fragments cover dynamic paths/query values, repeated instances, redaction, structural
  invalid inputs, and normal-GET typed validation without invoking DI during `bind`.
- [x] Commands drive buttons and explicit-field forms without copied URLs or methods and preserve
  native action semantics; no annotation-derived fields or `ActionHandle.form()` exist in 0.43.
- [x] Refresh intent and direct patch examples make their request/atomicity differences explicit.
- [x] Multi-output updates preserve primary/secondary ordering and semantic hosts.
- [x] Base descriptor/version/fingerprint, fixed generic arity, structural binding adapter, and
  dynamic/observed effect labels pass the 0.44 handoff fixture.

## Security acceptance

- [x] Cross-app, forged, unregistered, unbound, duplicate, unsafe-swap, and excessive targets fail
  before response emission.
- [x] Missing target uses the canonical server output; disagreement returns audited 403.
- [x] Commands preserve authentication, application authorization, tenancy, CSRF, validation,
  idempotency, and redirect boundaries.
- [x] Bound values, route graphs, errors, events, traces, Explorer, and test failures redact secrets.
- [x] Generated routes are never described or tested as authorization-by-obscurity.

## Accessibility and browser acceptance

- [x] Hosts remain semantically neutral unless configured and retain tag/name/attributes across
  replacement.
- [x] Busy/error/retry/focus/announcement behavior passes keyboard and automated a11y coverage.
- [x] No-JavaScript command flow succeeds through ordinary HTTP or a documented safe failure.
- [x] Three engines pass refresh fan-out, cancellation, late response, disconnect, nested host,
  history, failure, and cleanup scenarios.
- [x] Evidence remains scoped and does not close or market the outstanding `SR-021` work.

## Performance acceptance

- [x] Simple handle response p95 overhead is within 10% and at most 1 ms absolute above the
  equivalent recorded legacy region path.
- [x] No new required browser asset or request is added to a page that does not mount/use handles.
- [x] One/four/sixteen-target refresh and patch results record latency, allocation, payload, request
  count, cancellation, and failure behavior.
- [x] Repeated mount/refresh/remove cycles show no material retained-memory or listener growth beyond
  the recorded noise allowance.

## Compatibility and documentation acceptance

- [x] Every 0.42 stable interaction symbol keeps source and behavioral compatibility.
- [x] New symbols begin Beta and the stability inventory matches runtime exports exactly.
- [x] FastAPI, Flask, and Django portable patch fixtures pass or bounded adapter exceptions have an
  owner and destination.
- [x] Migration and rollback fixtures are executable and preserve explicit public URLs/keys.
- [x] A modeled binding adapter, declared effect, and type-schema extension can attach in the
  handoff fixture without changing 0.43 route identity, target authority, explicit forms, or
  response conversion.
- [x] Quickstart, HTMX interactions, mutations, forms/actions, testing, troubleshooting, errors,
  security, accessibility, API, Explorer, and scaffold docs are updated together.
- [x] Documentation maintains beginner, explicit-patch, and protocol-level layers without implying
  the lower layer is removed.

## Verification

During planning and implementation:

```bash
python scripts/verify_pkg_43.py --allow-planned
```

This validates the packet, exact gate inventory, requirement coverage, cross-phase boundary, and
published/version honesty without treating Planned rows as release evidence. At cut:

```bash
python scripts/verify_pkg_43.py
python scripts/check_release_gate.py 0.43.0 --execute-verified
```

`v0.43.0` may be cut only when every 0.43-owned row is Verified with zero Deferred.
