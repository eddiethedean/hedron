# Hedron `v0.44` type-driven authoring acceptance

**Status:** Published in-tree as `v0.44.0` (tag/PyPI deferred; D-076)<br>
**Planning baseline:** Published in-tree `v0.43.0` (original Stage 0 baseline was Published `v0.42.0`)<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.43.0`<br>
**Target:** `v0.44.0`<br>
**Decision/RFC:** D-072, refined by D-073 / D-076 / [RFC-0071](../rfcs/RFC-0071-TYPE-DRIVEN-AUTHORING.md)

Phase 0.44 adds Pydantic-backed boundary models, `Annotated` markers, generic specialization,
schema-derived native forms, declared command effects, typed outcomes, optional class handlers,
and a shared normalized schema extension over the **shipped** 0.43 handle API. It neither changes
Published 0.43 during planning nor authorizes implementation before a tracking issue exists.

Implementation requirements:
[TYPE_DRIVEN_AUTHORING_044](../implementation/TYPE_DRIVEN_AUTHORING_044.md). Public contract:
[TYPE_DRIVEN_AUTHORING](../api/TYPE_DRIVEN_AUTHORING.md). Capability inventory:
[`type-authoring-capability-inventory-044.toml`](type-authoring-capability-inventory-044.toml).
Form inventory:
[`type-form-inventory-044.toml`](type-form-inventory-044.toml). TypeSchema lock:
[`type-schema-044.toml`](type-schema-044.toml). Adapter dispositions:
[`adapter-disposition-044.toml`](adapter-disposition-044.toml). Evidence index:
[`release-gate-0.44.toml`](release-gate-0.44.toml). Upgrade fixtures:
[upgrade-fixtures-044](upgrade-fixtures-044.md).

## Release contract

- `ViewParams` and `FormBody` explicitly separate bindable/request models from injected
  dependencies and reuse one compiled Pydantic validation path.
- The fixed 0.43 generic slots are specialized with parameter/input models and content/results in
  stock mypy and pyright without changing arity, classes, or runtime semantics.
- Generated forms support a closed proven field inventory, native semantics, server validation,
  CSRF, safe errors, progressive enhancement, and explicit per-field/full-form escape hatches.
- `Refreshes`/`Updates` declare and validate allowed explicit command outputs; they never execute
  effects, infer dependencies, or widen target authorization.
- Typed discriminated outcomes require complete explicit response/effect mappings; arbitrary
  Pydantic returns are not auto-rendered.
- Optional `RefreshableView` and `CommandHandler` classes compile to the same 0.43 handles, routes,
  responses, security, fallbacks, tests, and tooling as functions.
- Type-aware runtime paths and tooling consume one versioned redacted `TypeSchema` extension bound
  to the authoritative 0.43 descriptor fingerprint; static analysis never imports/evaluates the
  target project.
- Fallback/cache remain explicit route/class configuration, not annotations; unmodeled handlers
  keep 0.43 structural binding, explicit forms, and dynamic/observed effect behavior.
- Existing 0.42 and 0.43 applications run unchanged unless they opt into Hedron markers/classes.
- No inferred authz/tenancy/transactions/retries, hidden reactivity, required checker plugin,
  browser framework, Node build, hydration, store, or live transport is introduced.

## Exact gate matrix

| Gate | Verified means |
|---|---|
| `MODEL-044` | Boundary/source normalization, Pydantic adapters, markers, serialization, ambiguity, limits, and DI separation pass. |
| `TYPING-044` | Fixed-arity 0.43 generic specialization and decorator/class signatures pass mypy and pyright positive/negative fixtures on supported Python. |
| `FORM-044` | Supported field inventory, native form generation, overrides, validation, CSRF, encoding, fallback, and errors pass. |
| `EFFECT-044` | Declared effects, dynamic labeling, typed outcomes/maps, actual-result verification, and failures pass. |
| `CLASS-044` | Function/class equivalence, lifecycle, factories, shared-state rejection, async/cancellation/concurrency/teardown pass. |
| `SCHEMA-044` | Fingerprint-bound redacted TypeSchema extension, provenance, single-consumer path, cache invalidation, bounds, and descriptor/schema mismatch behavior pass. |
| `SECURITY-044` | Dependency shadowing, secret leakage, hostile schemas/forms/effects/outcomes, CSRF/uploads, no-static-exec, and resource limits pass. |
| `A11Y-044` | Native semantics, labels/groups, errors/focus/retention, keyboard/visual modes/no-JS pass without a new product-wide human-AT claim. |
| `BROWSER-044` | Chromium/Firefox/WebKit generated/overridden form, validation, file/choice/union, HTMX/no-JS, cancellation, and cleanup pass. |
| `TOOLING-044` | Explorer, CLI static/dynamic modes, OpenAPI extensions, autodoc, diagnostics, and typed AppScenario consume the shared schema. |
| `COMPAT-044` | Unchanged 0.42/0.43, frozen predecessor handoff, incremental migrations, rollback, documented upstream APIs, and adapter/Jinja conformance pass. |
| `PERF-044` | Cold/warm normalization, validators, forms, effects/outcomes, schema payload/cache, allocation, concurrency, and memory budgets pass. |
| `DOCS-044` | API/guides/examples/migration/errors/security/a11y/testing/adapters/limits/escape-hatch documentation is complete and honest. |
| `REGRESS-044` | Full supported suite passes with zero phase-owned unresolved blocker/high regression. |
| `PKG-044` | Clean package/version/dependency/import matrix, inventory, release rehearsal, and zero-Deferred verification pass. |

Commands in the gate manifest are executable evidence for the in-tree `v0.44.0` cut.

## Stage 0 entry

- [x] D-072 records the accepted phase; D-073 reconciles its boundary with the 0.43 foundation.
- [x] D-076 rebases planning onto Published in-tree `v0.43.0` and locks form/`TypeSchema`/adapter
  inventories against shipped handle/descriptor/adapter seams. No runtime or version bump.
- [x] RFC-0071, API contract, implementation requirements, capability inventory, form inventory,
  TypeSchema lock, adapter dispositions, release gate, acceptance packet, upgrade fixtures,
  roadmap, indexes, status, and traceability references exist.
- [x] Published/living baseline is `v0.43.0`; no package or runtime version changed by this refine.
- [x] Verified in-tree 0.43 is an explicit prerequisite for Stage 1 and the 0.44 cut baseline.
  Stage 1 does not wait on `#311` PyPI/Git assets.
- [x] The predecessor boundary is reconciled: 0.44 consumes fixed generic slots, the structural
  binding adapter, explicit form plumbing, dynamic effects, and the `hedron.type` extension seam.
- [x] A tracking issue is created and bound to every 0.44 gate before Stage 1 begins:
  [#318](https://github.com/eddiethedean/hedron/issues/318).
- [x] Stage 1 records equivalent 0.43 bind/form/result performance and compatibility baselines.

## Functional acceptance

- [x] One Pydantic model/adapter validates bind, request reconstruction, form submission, Explorer
  preview, and scenario submission identically.
- [x] The adapter implements the 0.43 binding protocol and documented FastAPI/Pydantic request
  registration; it does not add raw-request parsing or invoke dependency-solver internals.
- [x] `bind` and form data cannot populate dependencies, request context, security principals, or
  server-owned metadata.
- [x] Model aliases/defaults/strictness/extras/validators/discriminators/generics/forward refs have
  explicit fixtures and deterministic fingerprints.
- [x] Generated forms either use a Supported field shape with complete semantics or require an
  explicit override; no guessed fallback control appears.
- [x] Effect declarations validate explicit returned effects without executing them; undeclared
  or foreign outputs fail before emission.
- [x] Typed outcomes cover every discriminator variant exactly once and map explicitly to
  content/status/effects/fallback behavior.
- [x] Function/class handler equivalents agree and shared mutable request state is rejected.
- [x] The 0.43 base descriptor remains authoritative for route/identity/host/fallback/target/
  response behavior, and fingerprint mismatch rejects stale type metadata.

## Typing and schema acceptance

- [x] Model/content/result types fill the fixed 0.43 fragment/action/bound/patch slots and decorator
  overloads pass stock mypy/pyright positive and negative fixtures without changing arity.
- [x] Useful basic typing does not require a checker plugin; any optional plugin has parity and
  graceful-absence evidence.
- [x] `TypeSchema` is immutable, versioned, provenance-bearing, redacted, bounded, references the
  0.43 descriptor fingerprint, and contains no callbacks/request/model instances/dependency values.
- [x] Every type-aware consumer checks the same extension and base-descriptor versions/fingerprint;
  mismatch fails clearly while base runtime consumers continue using the 0.43 descriptor.
- [x] Pydantic JSON Schema and FastAPI OpenAPI remain authoritative for their domains; Hedron
  extensions do not fork or silently reinterpret them.
- [x] Static analysis performs no import, annotation evaluation, plugin loading, or target code
  execution and labels unknown facts honestly.

## Security acceptance

- [x] Pydantic validation is never documented or treated as authn/authz/tenancy/business/transaction
  or retry policy.
- [x] Sensitive values/defaults/examples/custom serialization cannot leak through ids/events,
  markup, errors, schemas, logs, traces, Explorer, OpenAPI extensions, snapshots, or scenarios.
- [x] Generated forms preserve unsafe-method CSRF, content type, body/file/field limits, escaping,
  safe URLs/redirects, CSP, and upload policy.
- [x] Forged/cross-app effects and hostile aliases/extras/unions/recursion/collections/error storms/
  schema cache pressure fail inside recorded bounds.
- [x] 0.43 route/dependency/output authorization remains final authority after type normalization.

## Accessibility and browser acceptance

- [x] Generated controls have visible/programmatic labels, descriptions, grouped legends,
  required/invalid state, errors, native keyboard behavior, and safe value retention.
- [x] Missing labels and incompatible hints fail with accessible remediation instead of guessing.
- [x] Enhanced and ordinary HTTP validation paths provide usable error summary/focus/announcements
  and do not rely on color or client validation alone.
- [x] Supported file/choice/collection/nested/discriminated shapes and explicit overrides pass
  keyboard, no-JS, reduced-motion, forced-colors, zoom, and three-engine tests.
- [x] Evidence remains scoped and does not close or market `SR-021`.

## Performance acceptance

- [x] Cached modeled bind/form/result validation p95 overhead is within 10% and at most 1 ms
  absolute above equivalent recorded 0.43 paths.
- [x] Handler registration, cold/warm schema build, adapter compilation, form build/render,
  effect/outcome validation, and schema projection record latency and allocation.
- [x] Tiny/typical/maximum models record schema bytes, field/control/error counts, concurrency,
  cache behavior, and retained memory.
- [x] Applications not using 0.44 markers/classes have no material request-path regression and no
  new browser asset/request.

## Compatibility and documentation acceptance

- [x] Published 0.42 and Verified 0.43 fixtures pass unchanged; ordinary annotations and
  third-party metadata are not reinterpreted without opt-in.
- [x] The 0.43 handoff goldens prove generic arity, base descriptor authority, unmodeled structural
  binding, explicit forms, dynamic/observed effects, target policy, and response conversion remain
  unchanged after 0.44 attaches.
- [x] New symbols start Beta and runtime exports, type stubs/`py.typed`, docs, and stability
  inventory agree exactly.
- [x] FastAPI flagship and Flask/Django/Jinja/conformance projections pass or publish bounded
  machine-visible exceptions with owners/destinations.
- [x] Incremental model/form/effect/outcome/class migrations and rollback are executable and
  preserve explicit URLs/keys/data.
- [x] Docs teach simple function boundaries first, then forms/effects/outcomes, optional classes,
  and explicit/manual/protocol escape hatches.
- [x] Error catalog, limitations, version support, static-vs-dynamic tooling, security, a11y,
  testing, and performance guidance are updated together.

## Verification

During planning:

```bash
python scripts/verify_pkg_44.py --allow-planned
```

The command exists. At the in-tree cut:

```bash
python scripts/verify_pkg_44.py
python scripts/check_release_gate.py 0.44.0 --execute-verified
```

`v0.44.0` may be cut only when Verified 0.43 is the baseline and every 0.44-owned row is Verified
with zero Deferred.
