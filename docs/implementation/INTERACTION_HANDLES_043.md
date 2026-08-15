# Phase 0.43 implementation requirements — refreshable views and commands

**Status:** Planned; Stage 0 requirements packet  
**Target:** Hedron `v0.43.0`  
**Baseline:** Published `v0.42.0`  
**Decision/RFC:** D-071, refined by D-073 / [RFC-0070](../rfcs/RFC-0070-REFRESHABLE-VIEWS.md)<br>
**Public contract:** [REFRESHABLE_VIEWS](../api/REFRESHABLE_VIEWS.md)  
**Capability inventory:**
[`interaction-capability-inventory-043.toml`](../acceptance/interaction-capability-inventory-043.toml)

This document defines implementation boundaries and traceable requirements. Public names and
observable behavior are controlled by RFC-0070 and the API contract; private module/class placement
may change if dependency direction and the requirement IDs remain satisfied.

## Architecture

The ergonomic layer must compile into the existing interaction stack:

```text
FragmentHandle / ActionHandle / refresh / PatchSet
                    │
                    ▼
base handle descriptor + structural binding adapter
                    │
                    ▼
route metadata + FragmentRegion + ComponentRef
                    │
                    ▼
InteractionResult + OobUpdate + existing authorization
                    │
                    ▼
existing renderer / HTMX headers / host adapters
```

No parallel router, renderer, security policy, cache policy, or general browser state runtime is
permitted. The base descriptor reserves bounded namespaced extensions for 0.44; extensions may
enrich validation/tooling but cannot override base identity, routing, hosts, outputs, or authority.

## Package boundaries

| Package | 0.43 responsibility |
|---|---|
| `hedron-core` | Portable host metadata, refresh-intent schema, `Patch`/`PatchSet`, versioned base-descriptor/extension records, validation, registry output metadata, conformance fixtures. No FastAPI imports. |
| `hedron` | `FragmentHandle`, `BoundFragment`, `ActionHandle`, structural binding adapter, app decorators, reverse routing, explicit-form action wiring, controls, response conversion, scenario helpers. |
| `hedron-explorer` | Handle/command/output graph, redacted binding inspection, click/command preview, mismatch remediation. |
| `hedron-conformance` | Portable patch/refresh fixtures and adapter capability labels. |
| `hedron-flask` / `hedron-django` | Consume portable patch results and provide documented handle parity or machine-visible bounded exceptions. |
| `hedron-jinja` | Optional typed bridge to registered handles; no string-only implicit route exposure. |

`hedron-core` must not import FastAPI, Starlette, Flask, Django, Explorer, Jinja, or browser packages.

## Normative requirements

### View model (`IH-VIEW-*`)

- **IH-VIEW-001:** `@app.refreshable` registers one GET renderer and returns a callable,
  introspectable `FragmentHandle` without changing `@app.fragment` behavior.
- **IH-VIEW-002:** the handle and its versioned base descriptor are the single source for renderer,
  route, method, logical id, DOM id, default swap, fallback, registry output, controls, tests, and
  low-level region compatibility.
- **IH-VIEW-003:** omitted paths generate deterministic mount-aware internal routes hidden from
  OpenAPI by default; explicit paths remain supported.
- **IH-VIEW-004:** omitted keys derive from a stable logical-id algorithm; explicit `key=` is
  validated and compatibility-protected.
- **IH-VIEW-005:** calling a handle renders a stable `FragmentHost` around the renderer result;
  initial and refresh responses have the same root tag/id/owned attributes.
- **IH-VIEW-006:** the handle exposes the original renderer, `renderer_signature`, `__wrapped__`,
  annotations, docs, and source metadata; handle `__call__()` itself means mount and accepts no
  renderer/dependency arguments.
- **IH-VIEW-007:** sync, async, dependency-bearing, router-prefixed, app-mounted, module-function,
  documented bound-method, and exception paths have parity with existing component routes; handler
  class registration is not part of 0.43.
- **IH-VIEW-008:** duplicate unbound mounts cannot emit duplicate ids; the diagnostic identifies
  the handle and recommends `bind`/instance identity.
- **IH-VIEW-009:** generated route/id algorithms are versioned internal contracts and are visible in
  Explorer; only explicit path/key values are adopter compatibility promises.

### Binding (`IH-BIND-*`)

- **IH-BIND-001:** `bind(...)` structurally validates registered path/query names, required/extra
  values, safe serialization, and encoding and produces one reusable `BoundFragment` for mount,
  control, patch, test, and inspection operations.
- **IH-BIND-002:** canonical bindings generate deterministic instance ids and URLs independent of
  mapping insertion order.
- **IH-BIND-003:** secrets and sensitive values never appear in ids, events, traces, diagnostics,
  snapshots, or registry metadata; URL privacy follows the existing safe URL contract.
- **IH-BIND-004:** missing/extra parameters, unsafe values, unsupported encodings, and duplicate
  instance identities fail before response emission.
- **IH-BIND-005:** mount prefixes, reverse proxies, route converters, query repetition, Unicode,
  and percent encoding have explicit fixtures.
- **IH-BIND-006:** structural binding does not perform full Pydantic/domain validation, synthesize a
  request, invoke dependency solvers, or accept dependency/request/security-context names; the
  normal GET is authoritative and a single adapter protocol permits the opt-in 0.44 model adapter.

### Commands (`IH-CMD-*`)

- **IH-CMD-001:** `@app.command` returns an `ActionHandle` without changing `@app.action` return
  identity or semantics.
- **IH-CMD-002:** commands default to POST, current CSRF strategy, hidden schema visibility, and the
  existing action response converter.
- **IH-CMD-003:** generated and explicit paths, methods, dependencies, authz failures, validation,
  redirects, cookies, mounts, and exceptions retain native FastAPI behavior.
- **IH-CMD-004:** native buttons and explicit-field forms accept an action handle without a copied
  URL or method; the handle supplies route/method/CSRF/fallback wiring, not generated fields.
- **IH-CMD-005:** no-JavaScript requests have an explicit redirect/full-page/error outcome; an HTMX
  refresh event is never the only correctness path.
- **IH-CMD-006:** action handles do not grant authorization or idempotency and never downgrade an
  unsafe command to GET.
- **IH-CMD-007:** 0.43 does not expose `ActionHandle.form()`, infer fields from annotations, or
  register handler classes; those opt-in contracts are reserved for 0.44.

### Refresh intents (`IH-REFRESH-*`)

- **IH-REFRESH-001:** `refresh(*targets)` accepts only registered handles/bound fragments owned by
  the active app and returns a typed result.
- **IH-REFRESH-002:** refresh does not directly invoke FastAPI DI; mounted hosts perform normal GETs
  in response to a bounded typed event.
- **IH-REFRESH-003:** duplicate targets coalesce deterministically; default maximum targets is 16
  and the serialized payload is bounded by the existing interaction-event payload limit.
- **IH-REFRESH-004:** absent/disconnected hosts are safe no-ops; repeated events obey host sync
  policy and cannot build an unbounded queue.
- **IH-REFRESH-005:** auth, cache, tenant, dependency, cancellation, tracing, and error semantics are
  those of each view's GET route.
- **IH-REFRESH-006:** refresh fan-out and completion/failure are visible in Explorer and tests;
  refresh is not falsely presented as an atomic transaction.
- **IH-REFRESH-007:** refresh-event names and payloads use generated non-secret logical ids and are
  not author-controlled executable strings.

### Direct updates (`IH-PATCH-*`)

- **IH-PATCH-001:** portable frozen `Patch` and `PatchSet` values represent one registered direct
  update and one-primary-plus-secondary update sets.
- **IH-PATCH-002:** `replace` maps to `outerHTML`; `update` maps to `innerHTML`; the closed Supported
  swap set may expand only through an RFC/API amendment.
- **IH-PATCH-003:** patch conversion uses existing `InteractionResult`, `InteractionPolicy`,
  `OobUpdate`, selector authorization, cache/status/header validation, and rendering.
- **IH-PATCH-004:** the primary target supplies canonical `region_id`/retarget; missing client target
  succeeds and a conflicting target fails through the existing audited 403 path.
- **IH-PATCH-005:** secondary updates are ordered, bounded to 16, and cannot duplicate the primary
  or another secondary target.
- **IH-PATCH-006:** arbitrary selector strings, cross-app handles, unregistered/foreign handles,
  unresolved bound handles, unsafe swaps, and OOB-on-204 fail before response emission.
- **IH-PATCH-007:** toast and other reserved framework sinks retain current authorization and
  semantic-host behavior.
- **IH-PATCH-008:** mixed direct patches and refresh intents have one documented ordering rule or
  fail as an unsupported combination; implementation may not choose incidentally.

### Host, accessibility, and failure (`IH-HOST-*`)

- **IH-HOST-001:** the default host is semantically neutral; an allowlisted tag and safe ordinary
  HTML/ARIA attributes are explicit.
- **IH-HOST-002:** previous content remains usable during loading; busy state is visible,
  programmatic, request-scoped, and removed on success/failure/cancellation.
- **IH-HOST-003:** default errors preserve useful content, announce once, expose retry where safe,
  and never reveal exception text or route inventories in production.
- **IH-HOST-004:** outer replacement preserves the existing focus restoration contract; inner
  update does not steal focus.
- **IH-HOST-005:** native keyboard activation, reduced motion, forced colors, 200%/400% zoom,
  no-JavaScript, and automated screen-reader-oriented scenarios pass.
- **IH-HOST-006:** nested hosts, disconnected hosts, late responses, history restore, OOB conflict,
  and swap cleanup have deterministic ownership and teardown.
- **IH-HOST-007:** 0.43 evidence is automated/scoped and does not claim completion of `SR-021`.

### Security and privacy (`IH-SEC-*`)

- **IH-SEC-001:** every handle carries an unforgeable app/registry ownership identity checked during
  control, refresh, and patch normalization.
- **IH-SEC-002:** generated routes are explicit exposure, never authentication/authorization.
- **IH-SEC-003:** the high-level path never chooses sensitive content from raw `HX-Target`; the
  server output is canonical and disagreement is rejected.
- **IH-SEC-004:** commands use normal authz/tenant checks and unsafe-method CSRF behavior.
- **IH-SEC-005:** ids, bindings, events, traces, diagnostics, Explorer, and scenario failures follow
  secret/sensitive-value redaction.
- **IH-SEC-006:** target count, patch count, binding count/size, event bytes, content bytes,
  recursion, and metadata are bounded before allocation/emission.
- **IH-SEC-007:** unsafe URLs, selectors, raw HTML, event JavaScript, prototype-pollution keys,
  external redirects, and header bypasses remain rejected by the existing typed boundaries.

### Phase 0.44 extension seam (`IH-EXT-*`)

- **IH-EXT-001:** `FragmentHandle[Bind, Content]` and `ActionHandle[Input, Result]` have exactly two
  public generic slots in that order; 0.43 uses coarse mapping inputs and 0.44 may specialize those
  slots without changing runtime classes or arity.
- **IH-EXT-002:** `BoundFragment[Content]` and `Patch[Content]` expose their content slot from 0.43;
  0.44 may improve inference but cannot introduce an incompatible generic shape.
- **IH-EXT-003:** one immutable, versioned base handle descriptor is consumed by runtime, Explorer,
  CLI, scenarios, adapters, and conformance; each descriptor has a stable fingerprint and bounded
  namespaced-extension map.
- **IH-EXT-004:** extension data may narrow validation or add tooling metadata but cannot replace or
  override base route/method, app ownership, logical/DOM identity, host, target/output policy,
  fallback, limits, or response conversion.
- **IH-EXT-005:** command effect knowledge is `dynamic` before execution or `observed` in a trace;
  observations are never treated as declarations. Phase 0.43 defines no public effect-declaration
  syntax.
- **IH-EXT-006:** the 0.43 runtime and static tooling do not evaluate application annotations,
  derive model schemas, generate form fields, auto-render model returns, or register handler
  classes in anticipation of 0.44.
- **IH-EXT-007:** a versioned 0.43-to-0.44 handoff fixture proves a model binding adapter,
  `TypeSchema` extension, generated form, and declared effect can attach without changing the base
  descriptor fingerprint fields, route identity, explicit-form path, target authority, or response
  conversion.

### Developer experience (`IH-DX-*`)

- **IH-DX-001:** the scaffold's basic refresh uses only a refreshable handle and handle-derived
  control; no region/id/selector/allowlist/`swap` appears.
- **IH-DX-002:** the minimal mutation example uses a command plus `refresh(view)` and shows an
  ordinary HTTP fallback.
- **IH-DX-003:** autocomplete exposes mount, bind, refresh-control, replace, update, and inspection
  methods without requiring private attributes.
- **IH-DX-004:** development errors name views/commands and give handle-based remediation;
  production errors remain compact.
- **IH-DX-005:** Explorer renders a view-command-output graph and the equivalent route, target,
  swap, CSRF, cache, fallback, and fan-out mechanics; command effects are labeled dynamic or
  observed and are never inferred as declarations.
- **IH-DX-006:** CLI/check reports duplicate mounts, copied stale paths/targets, foreign handles,
  missing fallback claims, unbounded fan-out, and legacy migration opportunities.
- **IH-DX-007:** documentation maintains three deliberate layers: handles, typed patches, and the
  existing protocol-level API.

### Testing, adapters, compatibility, and performance (`IH-QUAL-*`)

- **IH-QUAL-001:** `AppScenario` can refresh/run/expect handles and inspect refreshes/patches without
  raw selectors; existing raw assertions remain.
- **IH-QUAL-002:** conformance fixtures cover portable refresh/patch success and adversarial cases
  on FastAPI, Flask, and Django, with machine-visible exceptions where exact ergonomics differ.
- **IH-QUAL-003:** every existing region/interaction test and 0.42 upgrade fixture passes unchanged.
- **IH-QUAL-004:** new symbols start Beta; stable promotion occurs only through the 0.43 inventory
  after all gates are Verified.
- **IH-QUAL-005:** no required browser asset, custom-element dependency, Node consumer build, live
  transport, hydration, or global store is added.
- **IH-QUAL-006:** simple handle response p95 framework overhead stays within 10% of the equivalent
  region route and the absolute p95 delta is at most 1 ms on the recorded runner.
- **IH-QUAL-007:** registration/binding/reversal and one/four/sixteen-target refresh/patch paths have
  recorded latency, allocation, payload, cancellation, and retained-memory evidence.
- **IH-QUAL-008:** docs include migration, rollback, progressive enhancement, troubleshooting,
  security, accessibility, testing, advanced escape hatches, and limitations.
- **IH-QUAL-009:** clean wheels/imports and the Supported Python/browser/adapter matrix pass without
  optional packages.

## Work slices

### Stage 0 — contract and inventory

- Accept D-071/RFC-0070.
- Land API, implementation, capability inventory, release gate, acceptance, upgrade, and
  traceability documents.
- Create and bind one tracking issue before runtime work begins.
- Keep workspace versions and published claims at 0.42.

### Stage 1 — portable model

- Add host/output metadata, refresh-intent schema, `Patch`, `PatchSet`, validation, diagnostics, and
  conformance fixtures in `hedron-core`.
- Lock generated identity/event algorithms, resource limits, base descriptor version/fingerprint,
  extension namespace rules, and the structural binding-adapter protocol.
- Benchmark existing region baselines before adding facade code.

### Stage 2 — FastAPI handles and routing

- Add `FragmentHandle`, `BoundFragment`, `ActionHandle`, decorators, generated routes, reverse
  routing, host wrapping, ownership, and introspection.
- Freeze the two-slot handle generic arity and prove sync/async/DI/mount/router/dynamic-route
  behavior without accepting dependency arguments through mount/bind.

### Stage 3 — controls and responses

- Add `Refresh`, handle methods, explicit-form/action controls, refresh-event materialization,
  direct patch conversion, fallback, status, cache, history, and cancellation behavior. Do not add
  schema-derived fields or `ActionHandle.form()`.

### Stage 4 — tooling and adapters

- Add the versioned base descriptor, dynamic/observed effect labels, Explorer graph/preview, CLI
  diagnostics, AppScenario helpers, HDJ bridge, adapter conversions, portable conformance, and the
  0.44 handoff fixture.

### Stage 5 — UX, security, accessibility, and performance closure

- Complete browser failure/focus/busy/no-JS matrices, adversarial tests, redaction, limits,
  benchmarks, memory/cleanup, and docs/scaffold migration.

### Stage 6 — release closure

- Run every 0.43 gate with retained artifacts.
- Update stability inventory only for proven symbols.
- Produce upgrade/rollback evidence and clean-wheel rehearsal.
- Cut `v0.43.0` only with zero Deferred 0.43-owned rows.

## Traceability matrix

| Requirements | Gate |
|---|---|
| `IH-VIEW-*`, `IH-BIND-*` | `VIEW-043` |
| `IH-CMD-*` | `COMMAND-043` |
| `IH-REFRESH-*`, `IH-PATCH-*` | `UPDATE-043` |
| `IH-HOST-*` | `A11Y-043`, `BROWSER-043` |
| `IH-SEC-*` | `SECURITY-043` |
| `IH-EXT-*` | `COMPAT-043`, `TOOLING-043` |
| `IH-DX-*` | `TOOLING-043`, `DOCS-043` |
| `IH-QUAL-001`–`IH-QUAL-004`, `IH-QUAL-008`–`IH-QUAL-009` | `COMPAT-043`, `REGRESS-043`, `PKG-043` |
| `IH-QUAL-005`–`IH-QUAL-007` | `PERF-043` |

The capability inventory maps every individual requirement id to a gate and evidence class. A gate
cannot become Verified if any mapped requirement is missing, Deferred, or represented only by an
unchecked prose claim.

## Required artifacts at cut

- API/autodoc and stability inventory for every new public symbol.
- Generic-arity type fixtures, base descriptor schema/fingerprint fixtures, structural binding
  adapter fixtures, and the 0.44 handoff compatibility corpus.
- Generated identity/path algorithm fixtures.
- Portable refresh/patch JSON fixtures and negative corpus.
- Three-host adapter conformance report.
- Three-engine browser, a11y, no-JS, focus, cancellation, and error artifacts.
- Security/adversarial/redaction report.
- Performance/allocation/payload/memory baseline and results.
- Explorer/CLI/scenario snapshots.
- Updated scaffold, Quickstart, interaction guide, mutation guide, testing guide, troubleshooting,
  error codes, migration, and release notes.
- Upgrade and rollback fixtures from 0.42.
- Clean wheel/source install and package verification output.

## Implementation prohibitions

- Do not change existing decorator return types.
- Do not duplicate target authorization or response-header policy outside the existing core path.
- Do not call FastAPI dependency solvers through undocumented internals.
- Do not perform full type/domain validation in the 0.43 structural binding adapter or allow bind
  values to populate dependencies/request/security context.
- Do not make generated ids/paths contain raw bound values.
- Do not allow high-level patch selector strings.
- Do not make refresh fan-out unbounded or claim it is atomic.
- Do not add a hidden browser store, hydration pass, or required custom element.
- Do not evaluate annotations, derive Pydantic boundary schemas, generate model fields, declare
  effects, auto-render model outcomes, expose `ActionHandle.form()`, or register handler classes in
  0.43; those contracts belong to 0.44.
- Do not update train versions or published claims during Stage 0/planning.

## Exit condition

The phase is complete only when the scaffold and reference application demonstrate the view/command
model, all low-level compatibility fixtures still pass, every `release-gate-0.43.toml` row is
Verified with retained evidence, and no 0.43-owned row is Deferred.
