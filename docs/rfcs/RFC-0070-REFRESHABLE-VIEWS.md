# RFC-0070: Refreshable views, commands, and typed updates

**Status:** Accepted  
**Target phase:** 0.43 (`v0.43.0`)  
**Decision:** D-071  
**Cross-phase refinement:** D-073<br>
**Baseline:** Published `v0.42.0`  
**Extends:** RFC-0008, RFC-0009, RFC-0015, RFC-0019, RFC-0023, RFC-0024,
RFC-0025, RFC-0039, RFC-0040, RFC-0044, and RFC-0053
**Forward extension:** RFC-0071 / D-072, refined by D-073 (phase 0.44 type-driven authoring)
**Tracking:** [#311](https://github.com/eddiethedean/hedron/issues/311)

## Summary

Phase 0.43 adds an ergonomic interaction layer in which authors work with refreshable views,
commands, and typed updates rather than coordinating fragment-region ids, CSS selectors, route
allowlists, HTMX attributes, and `InteractionResult` fields for every ordinary partial update.

The beginner model is:

> Views render UI. Commands do work. Commands refresh views.

```python
@app.refreshable
def status():
    return StatusPanel(...)


@app.command
def restart_service():
    restart()
    return refresh(status).toast("Service restarted")


@app.page("/")
def home():
    return Page(
        status(),
        status.refresh_button("Refresh"),
        restart_service.button("Restart"),
    )
```

`@app.refreshable` returns a typed `FragmentHandle`; `@app.command` returns a typed
`ActionHandle`. Generated internal routes, DOM ids, HTMX targets, swap strategies, CSRF wiring,
and registry metadata derive from those handles. Direct multi-target responses use `Patch` and
`PatchSet`; the existing `FragmentRegion`, `Hedron.region`, `Hedron.fragment`,
`fragment_regions=`, `RefreshButton.for_region`, `swap`, `OobUpdate`, `InteractionPolicy`, and
`InteractionResult` contracts remain available and are not deprecated in 0.43.

This is an additive authoring layer, not a reactive client runtime, global state system, SPA
router, hydration model, or replacement for explicit server authorization.

Phase 0.43 is also the stable runtime foundation for phase 0.44. It owns handle identity, routing,
structural binding, explicit form actions, response effects, target authority, host behavior, and a
versioned handle descriptor. Phase 0.44 may attach typed Pydantic metadata and refine the generic
input slots, but it may not replace those mechanics or change unmodeled 0.43 behavior.

## Problem

The current region API correctly exposes Hedron's HTMX transport and fail-closed target policy,
but a basic refresh still asks an author to understand and coordinate several technical concepts:

1. declare a `FragmentRegion` or call `app.region`;
2. place its id on a DOM host;
3. attach the region to a fragment route allowlist;
4. configure a control with the matching target and route;
5. return either a component with the expected root or an interaction envelope;
6. reason about primary versus out-of-band swaps.

The region object reduces string duplication, but it still makes a CSS selector and request target
part of the day-one application model. “Region” also sounds spatial while the object actually
combines a logical output identity, DOM destination, route policy entry, and diagnostic label.

This causes avoidable first-hour failures, makes ordinary actions read like transport code, and
pushes authors toward copying ids and URLs. The technical surface remains valuable for advanced
HTMX work; it should not be the only supported way to express “refresh this view.”

## Goals

- Make a single refresh readable without knowledge of HTMX targets or CSS selectors.
- Make handles the source of truth for rendering, reverse routing, controls, output identity,
  diagnostics, testing, and Explorer metadata.
- Freeze a two-slot generic handle shape and versioned base descriptor that 0.44 can enrich without
  changing class arity, route identity, or response semantics.
- Generate internal routes and DOM ids when the author does not need public stable values.
- Make mutations addressable through typed command handles with automatic unsafe-method and CSRF
  defaults.
- Support two explicit update modes: invalidate/re-fetch normal view renderers, or return direct
  typed patches.
- Keep server-owned output identity authoritative and reject conflicting client targets.
- Preserve ordinary HTTP, no-JavaScript, accessibility, cache, status, error, and focus behavior.
- Retain the complete low-level interaction API and provide a reviewable migration path.
- Reuse Hedron's existing HTMX and rendering machinery; add no required browser framework.

## Non-goals

- Hidden dependency tracking, signals, hooks, a global store, or full-script reruns.
- Automatically refreshing every view that happens to read mutated data.
- Inferring business authorization, tenancy, idempotency, or transaction boundaries.
- Treating a generated internal route as an authorization boundary.
- Rendering arbitrary callback graphs or executing client-provided Python/JavaScript.
- Replacing FastAPI dependency injection or depending on undocumented FastAPI internals.
- Removing or deprecating the stable region/`swap` facade in 0.43.
- Requiring custom elements, hydration, a virtual DOM, Node.js, SSE, WebSockets, or preload.
- Making every existing action or component decorator return a different runtime type.
- Pydantic boundary models, Hedron `Annotated` markers, schema-derived field controls, declared
  effect sets, discriminated outcome maps, and class-handler registration; these belong to 0.44.
- Full type/constraint validation during 0.43 `bind(...)`; 0.43 performs structural route binding
  and the normal GET route remains authoritative for request validation.

## Terminology

| Term | Meaning |
|---|---|
| **Refreshable view** | Explicitly exposed GET renderer with a stable logical identity and mounted fragment host. |
| **`FragmentHandle`** | Callable, inspectable descriptor returned by `@app.refreshable`. |
| **Bound fragment** | A handle plus validated path/query parameters and an instance identity. |
| **Structural binding** | 0.43 validation of route/query names, required values, safe serialization, URL encoding, ownership, and identity; it is not Pydantic/domain validation. |
| **Handle descriptor** | Versioned registry record for handle kind, identity, route, host, binding shape, output mechanics, fallback, and extension namespaces. |
| **Dynamic effect graph** | A command's outputs are explicit at runtime but unknown before execution unless a later typed extension declares them. |
| **Fragment host** | Stable server-rendered wrapper that owns swap, busy, error, and identity behavior. |
| **Command** | Explicitly exposed unsafe operation, POST by default, with ordinary authz/CSRF requirements. |
| **`ActionHandle`** | Callable, inspectable descriptor returned by `@app.command`. |
| **Refresh intent** | Response instruction that asks mounted handles to issue their normal GET requests. |
| **Patch** | Direct server-provided content update for one registered handle. |
| **Patch set** | One primary patch plus bounded secondary OOB patches and optional framework sinks such as toast. |

“Fragment region” remains the low-level compatibility term. New beginner documentation uses
“view,” “command,” “refresh,” and “update.”

## Public model

### Refreshable views

The default form generates an internal route:

```python
@app.refreshable
def status():
    return StatusPanel(...)
```

An explicit route remains available when the URL is externally meaningful or needed for a full
HTTP fallback:

```python
@app.refreshable("/status", key="service-status")
def status():
    return StatusPanel(...)
```

The decorated name is a `FragmentHandle`. It preserves the original renderer through `renderer`,
`renderer_signature`, `__wrapped__`, annotations, documentation, and source metadata. The handle's
own public call means “mount this already-unbound view” and accepts no application/dependency
arguments. Calling it mounts the view:

```python
Page(status())
```

The handle provides discoverable conveniences:

```python
status.refresh_button("Refresh status")
status.replace(special_content)  # outerHTML patch
status.update(inner_content)     # innerHTML patch
status.bind(account_id=account.id)
```

Parameterized views must be bound before mounting: `status.bind(account_id=...)()`. Dependency
values are supplied only when the registered GET route runs; they are never caller arguments to the
handle.

The exact generated route and DOM id are inspectable but are not public compatibility promises.
Authors who link from outside the application, write CSS against the host, or persist an identity
must provide an explicit path or key.

### Host contract

Initial page rendering and refresh responses use the same host identity and shape. The default host
is a neutral `div` with a generated safe id and logical metadata. Authors may configure an
allowlisted semantic tag and safe ordinary HTML/ARIA attributes. The framework does not infer a
landmark role from a Python function name.

The host owns:

- stable target identity;
- its view URL and default `outerHTML` replacement behavior;
- request synchronization and duplicate-request policy;
- loading and error presentation hooks;
- `aria-busy`, focus restoration, and live-announcement policy;
- optional refresh-event listening;
- registry and Explorer identity.

Mounting one unbound handle more than once in the same rendered page is a diagnostic error because
it would produce duplicate DOM ids. Repeated views use `bind(...)` or an explicit instance key.

### Bound views

Parameterized renderers use a bound handle:

```python
user_card = user_view.bind(user_id=user.id)

Page(
    user_card(),
    user_card.refresh_button("Refresh user"),
)
```

Binding performs structural validation: it accepts only the registered route's bindable path/query
names, checks required/extra values and safe serialization, produces a mount-aware URL, and derives
an instance id from a canonical non-secret fingerprint. It does not invoke FastAPI dependency
injection or duplicate the route's full Pydantic/type validation. Invalid typed/domain values
therefore follow the normal GET route's validation behavior. Phase 0.44 may install an opt-in
Pydantic binding adapter for eager model validation through this same binding seam.

Secret-like values must never appear in DOM ids, debug metadata, traces, or generated event names.
Path and query values still follow ordinary URL privacy rules; secret values do not become safe
merely because they are bound to a handle.

### Commands

`@app.command` is the high-level mutation counterpart:

```python
@app.command
def restart_service():
    authorize_restart()
    restart()
    return refresh(status)
```

Commands default to POST, require the active security profile's CSRF protection for cookie-backed
requests, and are hidden from OpenAPI unless explicitly exposed. They may accept an explicit path,
method, dependencies, response model, and schema visibility. `ActionHandle` supports controls and
forms without string URLs:

```python
restart_service.button("Restart")
Form(Text("Note"), action="/save")
```

In 0.43, form fields remain explicit. The handle supplies only the registered action URL, method,
CSRF/fallback integration, identity, and testing metadata. `ActionHandle.form()` and model-derived
controls are reserved for the opt-in 0.44 `FormBody` contract.

Existing `@app.action` semantics do not change. `@app.command` is additive so 0.43 does not change
the decorated value type or identity behavior of stable routes.

### Refresh intents

The common mutation response reruns a mounted view through its normal GET route:

```python
return refresh(notes, note_count).toast("Saved")
```

A refresh intent does not invoke FastAPI dependency injection from inside the command. Instead,
the response emits a bounded, typed framework event; each mounted host performs its authorized GET
with its normal route dependencies, authentication, cache behavior, cancellation, and tracing.
This uses HTMX's event/request model and requires no general Hedron client state runtime.

Refresh intents are appropriate when the normal renderer should run again. They may create one
additional GET per target, so the target count is bounded, visible in Explorer, and measured.
Request synchronization defaults prevent repeated intents from creating an unbounded queue.

The no-JavaScript path uses the command's explicit redirect/fallback policy and never treats the
refresh event as the only correctness path.

### Direct patches

When an action already has the new content, it can update one or more registered views in the same
response:

```python
return patches(
    notes.replace(notes_panel()),
    note_count.update(count_panel()),
    toast="Saved",
)
```

`Patch` contains a registered app-owned target handle, content, and a closed safe swap strategy.
`PatchSet` contains exactly one primary patch, zero or more ordered secondary patches, typed status,
cache, trigger, history, and framework-sink fields. Secondary patches compile to `OobUpdate`.

The high-level patch API does not accept arbitrary CSS selector strings. Advanced applications may
continue using `InteractionResult`, `retarget`, and `OobUpdate` with existing validation.

Duplicate patch targets, cross-application handles, an unbound parameterized handle, unknown swap
strategies, and OOB updates on 204 fail before response emission. Phase 0.43 verifies the explicit
runtime result against app ownership and target policy; it has no public predeclared command-effect
set. Phase 0.44 may add `Refreshes`/`Updates` declarations that further narrow—never widen—this
runtime authority.

### Loading and failure states

Refreshable hosts have accessible defaults without requiring custom configuration:

- existing content remains available while a refresh is in flight;
- native controls expose a visible busy/disabled state without removing keyboard focus;
- the host advertises `aria-busy` only during the owned request;
- a safe generic failure is announced once and does not destroy the previous useful content;
- retry uses the same handle and route;
- late or cancelled responses cannot overwrite a newer successful response;
- application-provided loading/error components are rendered through ordinary trust boundaries.

The API permits explicit loading, empty, and error content. It does not infer application-specific
error messages, retry safety, or whether a command may be repeated.

### Progressive enhancement

Generated internal fragment routes may return a fragment on direct navigation and therefore are
not automatically useful no-JavaScript destinations. Controls that claim progressive enhancement
must have an explicit full-page fallback or be mounted in a form/navigation flow with one.

Commands follow ordinary POST/Redirect/GET behavior without HTMX. An HTMX refresh or patch is an
enhancement of the same authorized mutation, not the only success path. Scaffold and guide examples
must demonstrate both paths.

### Testing and inspection

Application tests use handles rather than selectors and raw headers for ordinary flows:

```python
scenario.refresh(status)
scenario.expect(status).to_contain("Healthy")

scenario.run(save_note, note="Hello")
scenario.expect(notes).to_contain("Hello")
```

Raw client, header, selector, and `InteractionResult` assertions remain available.

Explorer and CLI show a handle graph with view/command names, generated or explicit paths,
structurally bindable parameters with redaction, canonical view outputs, observed command outputs,
refresh fan-out, swap strategy, CSRF, fallback, cache, loading/error policy, and equivalent
low-level route/region mechanics. Before 0.44 declarations, a command's possible effects are
explicitly labeled **dynamic**, not guessed from code or prior observations.

Development diagnostics use application language first. For example, a mismatch reports that the
“Restart” command attempted to update the `stats` view while the request targeted the `status`
view, then shows a handle-based fix. Production diagnostics remain compact and redact route maps,
bound values, and application structure.

## Phase 0.43 / 0.44 contract boundary

The phases form one stack with a deliberate ownership line:

| Concern | 0.43 owns | 0.44 may add |
|---|---|---|
| Handle typing | Stable two-slot `FragmentHandle[Bind, Content]` and `ActionHandle[Input, Result]` arity; coarse `Mapping[str, object]` input slots | Pydantic model types in the existing input slots plus stricter overloads; no arity change |
| Binding | Structural path/query plan, safe encoding, identity, ownership, mount-aware reversal, normal-route validation | Opt-in Pydantic adapter implementing the same binding protocol for eager model validation |
| Forms | Explicit `Form(action=handle, ...)` and handle-derived URL/method/CSRF/fallback | `FormBody` and `ActionHandle.form()` for a closed schema-derived control inventory |
| Effects | Explicit runtime `RefreshIntent`/`PatchSet`, app ownership, target policy, dynamic/observed tooling graph | `Refreshes`/`Updates` declarations that narrow actual results and make the graph statically known |
| Metadata | Versioned base handle descriptor authoritative for route, identity, host, output, and security | Versioned redacted `TypeSchema` extension referencing the base descriptor fingerprint |
| Handler shape | Decorated functions/callables; no handler-class registration contract | Optional `RefreshableView` / `CommandHandler` classes compiling to the same handles |

The 0.43 base descriptor reserves namespaced extensions and records whether binding/effect/type
metadata is structural, dynamic, observed, or declared. Unknown future extensions cannot alter base
route/output authority. The 0.43 runtime and tooling do not evaluate application annotations in
anticipation of 0.44.

## Layered authoring contract

Hedron deliberately exposes three layers:

1. **Views and commands:** `@app.refreshable`, `@app.command`, handle controls, `refresh(...)`.
2. **Explicit typed updates:** `Patch`, `PatchSet`, `replace`, `update`, `patches`.
3. **Protocol control:** regions, selectors, `InteractionPolicy`, `InteractionResult`, OOB and raw
   validated HTMX fields.

Higher layers compile to lower layers. They do not maintain parallel routing, rendering, security,
or browser semantics.

## Internal translation

The implementation reuses the existing contracts:

- every `FragmentHandle` owns an internal `FragmentRegion`;
- handle controls derive a `ComponentRef` and validated HTMX attributes;
- refreshable routes register through the existing component route machinery;
- direct patches normalize into `InteractionResult` plus `OobUpdate`;
- a canonical primary output supplies `region_id` and an approved `HX-Retarget`;
- missing client targets resolve to the canonical server output;
- conflicting client targets fail through the existing target-disagreement path;
- cache, CSRF, history, status, response-header, OOB, and selector policies remain centralized;
- Flask/Django adapters consume portable patch and metadata types rather than importing FastAPI.
- one versioned base handle descriptor is shared by runtime, Explorer, CLI, scenarios, and adapter
  fixtures; consumers do not reconstruct handle semantics independently;
- a binding-adapter protocol separates 0.43 structural binding from the opt-in 0.44 model adapter;
- descriptor extensions are namespaced, versioned, bounded, and cannot override base route,
  identity, ownership, target, fallback, or host fields.

The registry gains typed base handle/output metadata. Command effects are `dynamic` until observed
at runtime; an observation is diagnostic evidence, not a declaration. Existing string
`fragment_regions` inference remains for legacy routes during the compatibility window.

## Security implications

- A handle is an app-owned capability object, not a user-provided selector. Patch conversion
  rejects handles created by another app or registry.
- Generated route obscurity is never authorization. All normal authentication, authorization,
  tenancy, CSRF, and business validation remains mandatory.
- The server declares the canonical output. A supplied `HX-Target` may agree or be absent; a
  conflicting target is rejected and audited.
- New high-level APIs do not branch sensitive response content on raw client target values.
- Commands default to unsafe-method protections and do not silently downgrade to GET.
- Binding and diagnostics redact secrets and bound values according to existing policies.
- Structural binding never accepts dependency/request/security-context names and does not create a
  synthetic request or invoke dependency/type solvers.
- Refresh fan-out, patch count, content size, event payloads, recursion, and generated metadata are
  bounded before allocation or response emission.
- Cross-origin URLs, unsafe selectors, raw HTML, executable event payloads, and unregistered sinks
  remain rejected by existing trust boundaries.
- Error responses and Explorer detail remain development-gated.

## Accessibility implications

- `Refresh` and command controls use native button, link, and form semantics.
- A host is neutral by default; semantic tags/roles require explicit author intent.
- Loading state preserves focus, exposes visible state, and updates `aria-busy` on the correct host.
- Errors are visible and programmatically announced once; repeated refresh events do not create
  announcement storms.
- `outerHTML` replacement follows existing focus restoration and live-region policies.
- Keyboard-only, screen-reader-oriented automated scenarios, reduced motion, forced colors, zoom,
  and no-JavaScript fallbacks are acceptance requirements.
- Phase 0.43 does not claim completion of the outstanding human AT program (`SR-021`).

## Performance implications

- A simple refreshable view adds no new required JavaScript asset and no new browser framework.
- Direct patch responses use the existing single response/OOB path.
- `refresh(...)` intentionally performs one GET per target; target count is bounded and observable.
- The simple handle path must remain within 10% of the equivalent legacy region route for p95
  framework normalization/render overhead on the recorded CI runner, with an absolute p95 delta no
  greater than 1 ms.
- Generated host markup overhead is measured and documented; no view adds an asset or request until
  mounted or refreshed.
- Registration, binding, route reversal, one/four/sixteen-target patch sets, cancellation, repeated
  refresh, and memory retention receive explicit benchmarks.

## Alternatives considered

### Rename `FragmentRegion` to `Target` or `Outlet`

This improves vocabulary but preserves most ceremony and CSS-selector leakage. Aliases may help
advanced documentation, but a handle-based model solves the coordination problem.

### Bind only the target to the route

`@app.fragment("/status", into="status")` removes one repeated declaration but still leaves route
strings, host ids, controls, and response behavior separate. It is a useful internal translation,
not the complete beginner API.

### Infer targets from returned element ids

Keyed DOM reconciliation avoids request targets but requires a new morphing contract, duplicate-key
rules, and browser runtime. Typed handles retain ordinary HTMX behavior and make outputs explicit.

### Automatically track renderer dependencies

A reactive graph could refresh every view that read mutated data, but it would introduce hidden
state, invalidation, lifetime, and concurrency semantics. Explicit `refresh(view)` keeps causality
readable.

### Invoke view renderers inside commands

Calling renderer functions from a command appears efficient but would either bypass FastAPI
dependency injection or depend on unsupported internal DI APIs. Refresh intents issue normal GETs;
direct patches are available when the action already has content.

### Change existing decorators to return handles

Changing `@app.fragment` or `@app.action` return values could break function identity, decorator
stacking, dependency overrides, introspection, and stable code. New decorators are additive.

### Adopt a custom client state runtime

This would make loading, invalidation, and updates easy to centralize but conflicts with Hedron's
standards-first, server-authoritative, no-hidden-runtime principles. Existing HTMX events and
requests are sufficient.

## Testing strategy

- **Unit:** identity generation, host configuration, structural binding, redaction, handle
  ownership, patch normalization, duplicate targets, closed swaps, refresh event payloads,
  descriptor version/extensions, generic arity, and renderer/handle introspection.
- **Routing:** generated/explicit paths, mounts, routers, methods, OpenAPI visibility, dependency
  injection, async handlers, exceptions, redirects, cookies, cache, CSRF.
- **Interaction:** matching/missing/conflicting targets, refresh fan-out, primary/OOB patches,
  cancellation, late responses, history, 204, validation failures, fallback.
- **Browser:** focus, busy/error states, repeated requests, disconnected hosts, no-JavaScript path,
  three-engine HTMX behavior, reduced motion, forced colors, zoom.
- **Security:** cross-app handles, forged metadata, unsafe bound values, CSRF, authz/tenant fixtures,
  untrusted targets, output limits, error redaction, event injection.
- **Accessibility:** semantic hosts/controls, keyboard flows, announcement counts, focus restoration,
  axe/ACT checks, no human-AT claim beyond collected evidence.
- **Performance:** registration, binding, route reversal, simple refresh, refresh fan-out, patch sets,
  repeated mount/unmount, retained memory, payload and markup overhead.
- **Compatibility:** unchanged legacy region tests, 0.42 application fixtures, mixed high/low-level
  routes, manual migration and rollback.
- **Adapters/conformance:** portable patch fixtures for FastAPI, Flask, and Django; adapter-native
  controls may remain host-specific while semantics match.

## Compatibility and migration

Phase 0.43 is additive. No 0.42 public symbol is removed, renamed, or behaviorally widened. In
particular, the stable interaction facade remains supported. New symbols begin as `beta`; they may
join the stable tier only when every 0.43 gate is Verified and the stability inventory explicitly
lists them.

The migration guide provides side-by-side recipes:

- `app.region` + host id + `@app.fragment` + `RefreshButton.for_region` + `swap` to one
  `@app.refreshable` handle;
- action `fragment_regions=` + OOB updates to command handles and `PatchSet`;
- public fragment URLs to explicit-path refreshables;
- parameterized routes to structurally bound handles, with full request validation left on the GET;
- raw test headers/selectors to scenario handle assertions;
- rollback to the unchanged low-level API.

`hedron check` may report reviewable opportunities and mismatches, but 0.43 does not silently
rewrite application code. Generated ids and paths are not migration-stable; applications that
depend on them must make them explicit.

## Resolved questions (D-071)

| Question | Decision |
|---|---|
| Beginner nouns | **Refreshable view**, **command**, **refresh**, and **update**. “Region” remains low-level. |
| Decorators | Add `@app.refreshable` and `@app.command`; do not change existing decorator return types. |
| Default paths | Generate mount-aware internal routes; explicit paths remain supported and are required for external URL compatibility. |
| Default identity | Deterministic logical-id-derived safe DOM id; explicit `key=` is the compatibility escape hatch. |
| Mutation rerender | `refresh(view)` emits a bounded typed refresh intent; it does not invoke FastAPI DI internally. |
| Direct response | `Patch` / `PatchSet` compile to `InteractionResult` / `OobUpdate`. |
| Target authority | Server canonical output wins; absent client target is allowed, disagreement fails closed. |
| Browser runtime | Reuse HTMX events/lifecycle; no new general client state runtime or custom element requirement. |
| Legacy API | Fully retained and not deprecated in 0.43. |
| Stability | New surface starts Beta; stable promotion requires the phase inventory and all gates Verified. |
| Adapter depth | Portable types and fixtures are required; FastAPI owns full ergonomic decorators, Flask/Django receive documented parity or explicit bounded exceptions before cut. |
| Human AT | Automated/scoped interaction evidence only; phase does not close `SR-021`. |
| 0.44 handoff | Freeze two-slot generic arity, structural binding adapter, explicit-form plumbing, dynamic-effect labeling, and a versioned extensible base descriptor; do not pre-implement annotation/model/class features. |

## Acceptance criteria

- The scaffold's refresh example contains no visible region declaration, DOM target id, CSS
  selector, `fragment_regions=`, `RefreshButton.for_region`, or `swap` call.
- A refreshable view has one source of truth for renderer, route, host, controls, diagnostics, and
  tests.
- Generated and explicit paths, bound instances, async/dependency renderers, and mounted prefixes
  pass integration tests.
- Commands default to POST plus the active CSRF policy and have an ordinary HTTP fallback.
- `refresh(view)` reruns normal view routes through bounded HTMX events; direct patches remain a
  one-response path.
- Missing targets resolve to the server output; conflicting targets return a compact production
  failure and a useful development diagnostic.
- Patch targets must be registered handles owned by the active application; arbitrary high-level
  selector strings and cross-app handles fail.
- Loading, error, focus, announcement, keyboard, no-JavaScript, cancellation, and late-response
  browser scenarios pass.
- Explorer, CLI, and `AppScenario` use handles and expose equivalent low-level mechanics.
- The 0.43 handoff fixture proves 0.44 can attach a model adapter and namespaced type metadata
  without replacing route identity, target authority, explicit forms, or response conversion.
- FastAPI, Flask, and Django portable patch conformance is Verified or any adapter exception is
  explicitly inventoried with owner and destination.
- Existing region/interaction tests and 0.42 upgrade fixtures pass unchanged.
- No new required browser asset, global store, hydration runtime, live transport, or Node consumer
  build is introduced.
- Every row in `release-gate-0.43.toml` is Verified with zero Deferred before `v0.43.0` is cut.
