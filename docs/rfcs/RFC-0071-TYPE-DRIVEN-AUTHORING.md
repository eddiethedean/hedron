# RFC-0071: Type-driven authoring and schema-derived interactions

**Status:** Accepted<br>
**Target phase:** 0.44 (`v0.44.0`)<br>
**Decision:** D-072<br>
**Cross-phase refinement:** D-073<br>
**Planning baseline:** Published `v0.42.0`<br>
**Required predecessor:** Phase 0.43 (`v0.43.0`; D-071 / RFC-0070)<br>
**Extends:** RFC-0003, RFC-0004, RFC-0008, RFC-0015, RFC-0016, RFC-0019, RFC-0023,
RFC-0024, RFC-0039, RFC-0040, RFC-0044, and RFC-0070

## Summary

Phase 0.44 makes Python type annotations and Pydantic models a first-class description of the
boundaries around refreshable views and commands. The framework uses those declarations for
validation, typed handles, forms, outcome checking, Explorer metadata, testing, and diagnostics in
the same spirit that FastAPI uses annotations for HTTP inputs and outputs.

The beginner model remains “views render UI; commands do work; commands refresh views.” Types make
the inputs and declared effects explicit without introducing hidden reactivity:

```python
class UserCardParams(BaseModel):
    user_id: UUID
    tab: Literal["overview", "activity"] = "overview"


@app.refreshable
def user_card(
    params: Annotated[UserCardParams, ViewParams()],
    actor: Annotated[User, Depends(current_user)],
) -> UserCard:
    return UserCard(...)


class AddNoteInput(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=80), Control(label="Title")]
    body: Annotated[str, Field(max_length=4000), Control(kind="textarea", label="Note")]


@app.command
def add_note(
    data: Annotated[AddNoteInput, FormBody()],
    actor: Annotated[User, Depends(current_user)],
) -> Annotated[CommandResult, Refreshes(notes, note_count)]:
    save_note(actor, data)
    return refresh(notes, note_count)
```

0.43 already freezes `FragmentHandle[Bind, Content]`, `BoundFragment[Content]`,
`ActionHandle[Input, Result]`, and `Patch[Content]`. Phase 0.44 specializes those existing input
slots with Pydantic models; it does not change generic arity or runtime classes. Runtime validation
and generated metadata come from one typed extension attached to the authoritative 0.43 base
handle descriptor. Optional `RefreshableView` and `CommandHandler` classes support applications
that benefit from explicit load/render/execute lifecycle methods; function decorators remain the
primary and shortest API.

Annotations declare boundaries and intent. They do not infer authentication, authorization,
tenancy, transactions, idempotency, retry safety, cache correctness, accessible semantics, or
which views happen to depend on mutated data.

## Problem

RFC-0070 removes most route/selector plumbing from ordinary partial updates, but a handle alone
does not answer several recurring questions:

1. Which arguments are user-bindable view parameters and which are injected dependencies?
2. How are path, query, and form values validated consistently before application code runs?
3. Can an editor retain the parameter, content, command-input, and result types after decoration?
4. Can a safe native form, its validation errors, and its testing helpers derive from one model?
5. Can Explorer know a command's possible outputs before observing one request?
6. Can larger views and commands separate I/O, rendering, and outcome mapping without building an
   application-specific class framework?

Without a single normalized annotation contract, each subsystem is likely to inspect signatures
differently. That creates drift between routing, binding, form rendering, OpenAPI, Explorer,
testing, redaction, and static typing. It also tempts the framework to guess dependencies or UI
semantics from field names, which would make apparently convenient behavior unsafe and surprising.

## Goals

- Let one Pydantic model define a view or command input boundary and validation contract.
- Distinguish bindable/request data from dependency-injected values explicitly with `Annotated`
  metadata.
- Preserve useful generic types through refreshable and command decorators.
- Consume the fixed 0.43 generic slots, structural binding-adapter protocol, and base descriptor
  without replacing or reinterpreting unmodeled handlers.
- Generate conservative native forms from supported model fields while keeping explicit form
  composition and field overrides available.
- Declare and verify command effects without automatically discovering data dependencies.
- Support typed discriminated outcomes with explicit rendering/status/effect mappings.
- Offer optional class-based view and command lifecycles without requiring inheritance.
- Give Explorer, CLI, OpenAPI extensions, and `AppScenario` one redacted normalized schema.
- Preserve RFC-0070's target authority, progressive enhancement, security, and compatibility
  contracts.
- Use documented Pydantic v2 and FastAPI extension points; avoid private dependency-solver or
  schema-generation internals.

## Non-goals

- Inferring which views read a model or automatically refreshing them after a write.
- Deriving authentication, authorization, tenancy, transaction, idempotency, or retry policy from
  Python types or field names.
- Treating type validation as business validation or access control.
- Generating a polished domain-specific UI for every Pydantic/Python type.
- Replacing FastAPI dependency injection, Pydantic, Hedron components, or explicit HTML forms.
- Requiring class-based views/commands or converting existing function handlers into classes.
- Executing application imports or evaluating annotations in static/offline CLI analysis.
- Serializing secrets into schemas, DOM metadata, errors, traces, snapshots, or instance ids.
- Changing existing route, action, form, model, region, interaction, or 0.43 handle semantics.
- Changing 0.43 handle generic arity, base descriptor fingerprints/authority, structural binding
  behavior for unmodeled handlers, explicit-form behavior, or runtime response conversion.
- Adding a client store, reactive graph, hydration, VDOM, Node build, or live transport.

## Terminology

| Term | Meaning |
|---|---|
| **Boundary model** | Pydantic `BaseModel` used as one validated view-parameter, form-input, or typed-outcome boundary. |
| **Marker** | Immutable Hedron metadata carried in `typing.Annotated`; it describes source, presentation, sensitivity, identity, or declared effects. |
| **Normalized schema** | Framework-owned, versioned, redacted 0.44 extension derived from a signature, Pydantic schema, and Hedron markers and attached to a 0.43 descriptor fingerprint. |
| **Bindable value** | Value explicitly marked as view parameters and accepted by `FragmentHandle.bind`. |
| **Injected value** | Value supplied by FastAPI dependency injection or another adapter; never accepted from `bind` or generated controls. |
| **Control hint** | Conservative field presentation metadata; never validation or authorization. |
| **Effect declaration** | Closed list of handles a command may refresh or update, used for validation and tooling rather than automatic execution. |
| **Typed outcome** | Pydantic discriminated result returned by application code and mapped explicitly to a command response. |
| **Class-based view/command** | Optional structured handler with explicit lifecycle methods, registered into the same routes and handles as function handlers. |

## Required 0.43 predecessor contract

Phase 0.44 begins only after the following 0.43 handoff is Verified:

- fixed two-slot handle generics and one-slot bound/patch content generics;
- one authoritative versioned base handle descriptor and fingerprint;
- one structural binding-adapter protocol with normal-GET validation authority;
- explicit-field `Form(action=handle, ...)` wiring;
- runtime `RefreshIntent`/`PatchSet` target authority and dynamic/observed effect labels; and
- bounded namespaced descriptor extensions that cannot override base mechanics.

If implementation discovers that a 0.44 feature requires changing one of those base semantics,
work stops for an RFC/decision amendment; 0.44 must not silently replace its predecessor.

## Public model

### Boundary models and parameter sources

One annotated parameter identifies each high-level boundary:

```python
def user_card(
    params: Annotated[UserCardParams, ViewParams()],
    actor: Annotated[User, Depends(current_user)],
) -> UserCard: ...
```

Only `params` is bindable. `actor` remains owned by dependency injection. `bind(...)` accepts either
a validated model instance or keyword field values and returns the same `BoundFragment` shape from
RFC-0070:

```python
card = user_card.bind(user_id=user.id, tab="activity")
card = user_card.bind(UserCardParams(user_id=user.id, tab="activity"))
```

Both forms pass through the same Pydantic validator and canonical serializer. Missing, extra, and
invalid values fail before route generation or markup emission. Dependency parameters, request
objects, security principals, and framework context are never populated from bound values.

The model adapter implements the binding protocol established in 0.43. It replaces only the
structural adapter for this opted-in handle; URL reversal, instance identity, app ownership,
mounting, target policy, and the normal GET route remain 0.43-owned. Request parsing is registered
through documented FastAPI/Pydantic public APIs rather than a parallel raw-`Request` parser or an
internal dependency-solver call.

`FormBody()` similarly identifies one command input model. FastAPI-native `Path`, `Query`, `Form`,
`Body`, and `Depends` remain supported on explicit function parameters. Hedron does not silently
reinterpret a FastAPI marker. Mixed source styles must either normalize without ambiguity or fail
with a diagnostic that identifies the conflicting parameter.

### Marker vocabulary

Phase 0.44 defines a small immutable marker vocabulary:

| Marker | Valid location | Meaning |
|---|---|---|
| `ViewParams()` | refreshable parameter | Model is the bindable view-parameter boundary. |
| `FormBody()` | command parameter | Model is parsed from an ordinary form/HTMX form request. |
| `Sensitive()` | model field or boundary | Redact values from framework-owned metadata and diagnostics. |
| `InstanceKey()` | view-parameter field | Field contributes to canonical instance identity through a non-reversible fingerprint. |
| `Control(...)` | command-input field | Optional native control hint and human label/help metadata. |
| `Refreshes(...)` | command return annotation | Declares the allowed refresh-handle set. |
| `Updates(...)` | command return annotation | Declares the allowed direct-patch target set. |

Unknown `Annotated` metadata is preserved for other frameworks and ignored by Hedron. Duplicate or
contradictory Hedron markers fail at registration. Markers are data only: parsing them cannot call
application callbacks or weaken route/security policy.

`Sensitive()` is defense in depth for framework-owned output, not a promise that ordinary URLs,
application logs, custom templates, or third-party integrations are safe. `Control()` cannot
override Pydantic validation.

Route and lifecycle policy does not move into annotations. Fallback and cache remain explicit 0.43
decorator/handle configuration (or equivalent class attributes) using the existing validated
types. Parameter/field markers describe inputs; return markers describe allowed effects. This
placement rule prevents type metadata from silently overriding HTTP, CSRF, redirect, or cache
policy.

### Generic handles

The planned typing model is:

```python
FragmentHandle[ParamsModel, Content]
BoundFragment[Content]
ActionHandle[InputModel, Result]
Patch[Content]
```

The decorator overloads retain the handler's boundary and return types in type-checker-visible
signatures. Calling a refreshable handle still mounts a host; `render`/test helpers may expose the
content type where that distinction is useful. A bound fragment no longer requires the parameter
model type because its inputs have already been validated.

The generic slot count and order are inherited from 0.43 and are compatibility requirements:
`FragmentHandle[Bind, Content]`, `ActionHandle[Input, Result]`, `BoundFragment[Content]`, and
`Patch[Content]`. Unmodeled 0.43 handlers keep their coarse mapping input types. Opting into
`ViewParams`/`FormBody` specializes only the appropriate existing input slot.

Typing improvements must work in mypy and pyright fixtures for supported Python versions. A type
checker plugin may be evaluated only if ordinary overloads/protocols cannot express the contract;
no plugin is required for basic correct application code in 0.44.

### Schema-derived forms

An action handle with `FormBody()` may build a native form:

```python
add_note.form(submit_label="Add note")
```

This method is an additive 0.44 capability. The 0.43 explicit path
`Form(action=add_note, explicit_fields...)` remains available and is the required fallback for
unsupported schemas; generated and explicit forms share the same action URL, method, CSRF,
fallback, and response behavior.

Generation is conservative. Phase 0.44 supports a closed inventory of scalar, enum, optional,
bounded collection, date/time, file, and discriminated-union shapes only after each shape has
native semantics, serialization, validation, accessibility, and browser fixtures. Unsupported or
ambiguous fields produce a diagnostic and require an explicit form/control override; they never
degrade to a guessed text input.

Pydantic constraints own validation. `Control` owns presentation hints. The generated form owns
field naming, labels, descriptions, required/optional state, error association, input retention,
CSRF integration, encoding, submit state, and progressive enhancement. Application authors may
replace individual controls or the entire form while keeping the same action/input model.

Server validation remains authoritative. Browser attributes such as `required`, `min`, and
`maxlength` mirror safe constraints for usability but do not replace server validation.

### Effect declarations and runtime verification

Command return metadata makes possible outputs inspectable:

```python
def add_note(...) -> Annotated[
    CommandResult,
    Refreshes(notes, note_count),
]:
    ...
```

The declaration does not cause refreshes. The handler must still return `refresh(...)`, patches, a
typed outcome, a response, or another documented result. When an effect declaration exists,
normalization verifies that actual refresh/patch targets are a subset of the declared app-owned
handles. Undeclared targets fail before response emission. A command without a declaration keeps
the explicit runtime behavior from 0.43 but Explorer labels its effect graph as dynamic.

Adding a valid declaration changes the base descriptor's effect-knowledge projection from
`dynamic` to `declared`; runtime observations remain traces, not inferred declarations.

This provides a useful static graph without pretending to discover data dependencies. Effect
declarations cannot make an unauthorized handle legal; 0.43 ownership and output authorization
remain authoritative.

### Typed outcomes

Commands may return discriminated Pydantic models when an explicit outcome mapping exists:

```python
class Saved(BaseModel):
    kind: Literal["saved"] = "saved"
    note_id: UUID


class Conflict(BaseModel):
    kind: Literal["conflict"] = "conflict"
    current_revision: int


SaveOutcome = Annotated[Saved | Conflict, Field(discriminator="kind")]
```

An action handle or `CommandHandler` registers a closed mapping from variants to status, render
function, refresh/patch effects, and fallback. The mapping is validated at startup for complete and
non-overlapping discriminator coverage. Returning the wrong type, an unmapped variant, or an effect
outside the declared set fails safely with a stable diagnostic.

Typed outcomes are optional. Existing `Response`, `InteractionResult`, `RefreshIntent`, `PatchSet`,
and component return paths remain valid according to their owning contracts. Hedron does not turn
arbitrary `BaseModel` returns into UI automatically.

### Optional class-based views

Applications with separate loading and rendering logic may use:

```python
class UserCardView(RefreshableView[UserCardParams, UserCardData]):
    host = FragmentHost(tag="section")

    async def load(
        self,
        params: Annotated[UserCardParams, ViewParams()],
        actor: Annotated[User, Depends(current_user)],
    ) -> UserCardData:
        return await repository.load_user(actor, params.user_id)

    def render(self, data: UserCardData) -> UserCard:
        return UserCard(data)


user_card = app.refreshable(UserCardView)
```

`load` is the request/DI entrypoint and `render` is a deterministic rendering step. Class
construction is application registration, not request-scoped dependency injection. Mutable
request state may not be stored on a shared handler instance. A documented factory is required for
per-request handler state.

The registered result is the same `FragmentHandle` used by function views. Loading, empty, failure,
host, cache, binding, and inspection behavior uses the same 0.43 machinery.

### Optional class-based commands

Commands may use an explicit lifecycle:

```python
class AddNote(CommandHandler[AddNoteInput, SaveOutcome]):
    async def execute(
        self,
        data: Annotated[AddNoteInput, FormBody()],
        actor: Annotated[User, Depends(current_user)],
    ) -> SaveOutcome:
        ...


add_note = app.command(AddNote)
```

`execute` is the only mutation entrypoint. Outcome mapping, effects, form config, and fallback are
declarative class configuration validated at registration. The class API compiles to the same
`ActionHandle`, action route, CSRF policy, response converter, and no-JavaScript path as a function
command. Inheritance is optional; a runtime-checkable protocol and registration adapter support
plain classes where practical.

### One normalized schema extension

The 0.43 base handle descriptor remains authoritative for runtime routing, identity, hosts,
fallback, targets, and response conversion. Each opted-in 0.44 handler attaches one versioned
redacted `TypeSchema` extension referencing that descriptor's fingerprint. Bind/form validation,
generated controls, effect/outcome validation, Explorer, CLI, OpenAPI extensions, and
`AppScenario` consume the extension; they do not replace the base descriptor.

The extension is produced from:

1. the preserved Python signature and `Annotated` metadata;
2. Pydantic core/JSON schema through documented public APIs;
3. a read-only projection of route/handle/host/effect registration metadata from the base
   descriptor; and
4. a redaction pass before any diagnostic or tooling projection.

The normalized schema records provenance for every field and marker plus the base descriptor
version/fingerprint. Type-aware consumers may not re-introspect handlers independently. A mismatch
fails rather than applying stale type metadata. FastAPI's OpenAPI remains authoritative for HTTP;
Hedron extensions add view/command/form/effect metadata only when schema exposure is enabled.

## Error model

Errors are separated by lifecycle:

- registration errors: ambiguous boundaries, invalid markers, unsupported class signatures,
  incomplete outcome maps, forward-reference failures, or schema conflicts;
- bind/build errors: invalid parameter values, unsupported generated controls, unresolved instance
  identity, or cross-app effect declarations;
- request validation errors: stable field paths/messages and appropriate HTTP 422/form-fragment
  behavior with safe input retention;
- result errors: return type mismatch, undeclared effect, unmapped outcome, or invalid response
  conversion;
- static-tooling findings: syntax-only analysis that never imports the project and clearly labels
  facts it cannot prove.

Development diagnostics name the view/command/model/field, expected boundary, received shape, and
safe remediation. Production responses do not include Python reprs, exception text, model schemas,
registered handles, or sensitive values.

## Alternatives considered

### Decorator keyword configuration only

Decorator keywords are explicit and remain useful for route-level behavior, but they duplicate
model validation and do not preserve parameter-level provenance. They remain an override, not the
only schema source.

### Infer everything from bare Pydantic models

Rejected. A bare model does not say whether it comes from binding, a form, JSON, a dependency, or
application state. `Annotated` source markers make the boundary reviewable.

### Infer effects by observing data reads/writes

Rejected. It creates hidden reactivity, incomplete dependency graphs, surprising fan-out, and
authorization risk. Effects are explicit return values with optional explicit declarations.

### Generate forms for every JSON Schema

Rejected. JSON Schema does not determine accessible interaction design, widget choice, file
semantics, or a useful layout. Generation is limited to a proven closed inventory with explicit
escape hatches.

### Require class-based handlers

Rejected. Functions are clearer for ordinary interactions. Classes are optional for lifecycle
separation and shared configuration.

### Build a mandatory type-checker plugin

Deferred as a fallback only. Public generics, overloads, protocols, and `Annotated` should provide
useful typing in stock mypy/pyright first.

## Security implications

- Annotation/schema parsing runs only for trusted imported application code. Static CLI scans of
  untrusted trees do not import modules or evaluate string annotations.
- Boundary source markers prevent bind/form data from populating dependencies or request context.
- Pydantic validation is input-shape validation, not authorization; all normal authn/authz/tenant
  and CSRF checks remain required.
- `Sensitive` redaction is applied before identity, schemas, Explorer, logs, traces, test failures,
  and error rendering; schema defaults/examples for sensitive fields are rejected.
- Generated forms preserve CSRF, safe URL, encoding, upload, body-size, and redirect policies.
- Effect declarations and outcome mappings contain registered app-owned handles and are normalized
  through the 0.43 output policy.
- Schema size, nesting, union variants, fields, defaults, validation-error count, form controls,
  and generated metadata are bounded before expensive rendering or serialization.
- Arbitrary callables embedded in third-party `Annotated` metadata are neither invoked nor
  serialized by Hedron.

## Accessibility implications

- Generated forms use native controls, visible labels, descriptions, fieldsets/legends for grouped
  choices, programmatic required/invalid state, and error summaries linked to fields.
- Model field names are not automatically converted into adequate accessible labels when no
  explicit label or safe title exists; missing-label diagnostics fail generation.
- Validation retains safe submitted values, moves/announces focus according to existing form
  guidance, and does not rely on color or client validation alone.
- Control hints cannot request inaccessible roles or remove native keyboard behavior.
- Class-based loading/error/outcome rendering inherits 0.43 host semantics and no-JavaScript
  behavior.
- Automated and three-engine evidence does not close the outstanding product-wide human-AT work.

## Performance implications

- Signature and Pydantic schema normalization occurs once per registered handler and is cached by
  stable model/config identity.
- Request parsing uses one compiled validator per boundary; subsystems may not rebuild independent
  adapters per request.
- Registration time, first schema build, cached lookup, bind validation, form rendering, request
  validation, result validation, and Explorer schema payload have explicit budgets.
- Generated schemas and controls are bounded; recursive/unbounded models fail generation while
  remaining usable with explicit manual forms/routes.
- Applications that do not use 0.44 markers/classes pay no material request-path cost and load no
  browser asset.

## Testing strategy

- Unit: marker normalization, generic/runtime metadata, Pydantic adapters, schema provenance,
  redaction, outcome maps, and class lifecycle.
- Static typing: mypy and pyright positive/negative fixtures across supported Python versions.
- Integration: view binding, DI separation, form parsing, validation fragments, effects, outcomes,
  async handlers, mounts, OpenAPI, and progressive enhancement.
- Browser/a11y: native forms, errors, focus, retained input, files, unions, keyboard, no-JS, HTMX,
  reduced motion, forced colors, and zoom in Chromium/Firefox/WebKit.
- Security: dependency injection attempts, sensitive defaults, schema bombs, recursive models,
  forged effects, cross-app handles, uploads, extra fields, and diagnostic leakage.
- Compatibility: unchanged 0.42 and 0.43 applications, incremental annotation adoption, manual-form
  overrides, function/class equivalence, and rollback.
- Performance: registration/schema cold+warm costs, validators, forms, result checking, metadata
  size, allocation, and retained memory.

## Compatibility and migration

Phase 0.44 is additive and cannot begin runtime work until 0.43's handle contracts are implemented
and Verified. Existing function-based refreshable views and commands require no annotations beyond
their current signatures. Authors may adopt boundary models one handler at a time.

Existing Pydantic Hedron models, FastAPI parameter markers, `Form`, `AutoForm`, `Action`, explicit
routes, region APIs, and interaction results retain their current behavior. Phase 0.44 does not
reinterpret an existing annotation unless the handler opts into a Hedron marker or class API.

New symbols begin Beta. Generated form markup and normalized schema carry explicit version fields;
only documented public attributes and behavior are compatibility promises. Rollback removes 0.44
markers/classes or returns handlers to explicit parameters/forms while preserving 0.43 handles.

## Resolved questions (D-072)

1. **Are boundary models required?** No. They are an additive path; ordinary annotated parameters
   and explicit forms remain supported.
2. **Do annotations trigger effects?** No. They declare allowed effects; returned values trigger
   explicit effects.
3. **Can a dependency be bound from a model?** No. Only a `ViewParams` boundary is bindable.
4. **Are classes the preferred beginner API?** No. Function decorators remain primary.
5. **Does every Pydantic model generate a form?** No. Only a closed supported field inventory does;
   other models require overrides/manual forms.
6. **Are Pydantic models automatically response-rendered?** No. Typed outcomes need an explicit,
   complete mapping.
7. **May static tooling import application code to inspect annotations?** No. Importing is an
   explicit runtime/dynamic inspection mode only.
8. **Does `Sensitive` make a value safe everywhere?** No. It controls framework-owned redaction;
   authors remain responsible for application/third-party output.
9. **Is a type-checker plugin required?** No for the core contract; stock typing must be useful.
10. **What is the baseline?** Planning remains honest against Published `v0.42.0`; implementation
    depends on Verified 0.43 and the 0.44 cut baseline is `v0.43.0`.
11. **May 0.44 change the 0.43 handle type arity or descriptor authority?** No. It fills the
    reserved generic input slots and attaches a fingerprint-bound extension; base mechanics remain
    0.43-owned.

## Acceptance criteria

- A boundary model is validated consistently for binding/request parsing and produces one redacted
  extension used by every type-aware consumer while the 0.43 descriptor stays authoritative for
  routing, identity, hosts, targets, fallback, and responses.
- Dependency values cannot be supplied through `bind`, forms, query data, or model extras.
- Decorated handles fill the fixed 0.43 generic slots with useful model/content/result types in
  mypy and pyright fixtures without changing class arity.
- Generated forms pass the locked supported-field, security, a11y, browser, validation, and no-JS
  matrices; unsupported fields fail with actionable overrides.
- Declared effects and typed outcomes are verified against actual app-owned results without hidden
  refresh behavior.
- Function and class handlers compile to the same 0.43 route/handle/response/security machinery.
- Static analysis never imports/evaluates the target project; dynamic analysis is explicit.
- Existing 0.42 and future 0.43 fixtures pass unchanged.
- Every `release-gate-0.44.toml` row is Verified with retained evidence and no 0.44-owned row is
  Deferred before `v0.44.0` is cut.
