---
status: historical
phase: "0.44"
---

# Type-driven authoring

!!! note "Current 0.44 contract"

    Published in-tree `v0.44.0` type-driven authoring (D-072 / D-073 / D-076). These symbols are
    **Beta**. They consume the shipped 0.43 handle API
    ([Refreshable views and commands](REFRESHABLE_VIEWS.md)). Pin
    `hedron>=1.0.0,<1.1`.

Type-driven authoring uses Pydantic models and `typing.Annotated` metadata to describe validated
view parameters, command forms, result effects, and optional class lifecycles:

```python
from typing import Annotated, Literal
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel, Field

from hedron import Control, FormBody, Refreshes, ViewParams


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

Annotations identify input boundaries and declared intent. They do not infer authorization,
transactions, retry safety, accessible semantics, or hidden data dependencies.

## Planned symbols

| Symbol | Package | Role |
|---|---|---|
| `ViewParams` | `hedron` | Mark one Pydantic model as a refreshable view's bindable boundary. |
| `FormBody` | `hedron` | Mark one Pydantic model as a command's ordinary form boundary. |
| `Sensitive` | `hedron-core` / `hedron` | Request framework-owned redaction for a model field or boundary. |
| `InstanceKey` | `hedron-core` / `hedron` | Include a field in non-reversible bound-instance identity. |
| `Control` | `hedron` | Give conservative presentation metadata for a generated native control. |
| `Refreshes` | `hedron` | Declare the registered handles a command may refresh. |
| `Updates` | `hedron` | Declare the registered handles a command may patch directly. |
| `CommandResult` | `hedron` | Common command-result protocol/union accepted by the response converter. |
| `RefreshableView` | `hedron` | Optional class-based load/render lifecycle. |
| `CommandHandler` | `hedron` | Optional class-based execute/outcome lifecycle. |
| `OutcomeMap` | `hedron` | Closed mapping from outcome variants to response behavior. |
| `TypeSchema` | `hedron-core` | Versioned normalized, redacted extension attached to a 0.43 base handle descriptor. |

Final import placement is locked by D-076: portable markers and `TypeSchema` in
`hedron-core`; FastAPI source markers and handler APIs in `hedron`. Names and
semantics in this contract may not drift silently during implementation. Phase 0.43
already defines the public generic slot count/order and base descriptor; 0.44
specializes those slots and attaches metadata without changing runtime meaning.
That meaning remains controlled by
[Refreshable views and commands](REFRESHABLE_VIEWS.md).

## Required 0.43 handoff

Before this API can be implemented, 0.43 must remain Verified in-tree with these shipped seams
(D-073 / D-076):

- `FragmentHandle[BindT, ContentT]` and `ActionHandle[InputT, ResultT]` with exactly two slots;
- `BoundFragment[ContentT]` and `Patch[ContentT]` with one content slot;
- one versioned authoritative `BaseHandleDescriptor` and `descriptor_fingerprint`;
- one `BindingAdapter` protocol with `StructuralBindingAdapter` default;
- explicit `Form(action=handle, ...)` action/method/CSRF/fallback wiring; and
- dynamic/observed effect labels plus existing target authority.

`TypeSchema` is a namespaced extension of that contract under `hedron.type`. It cannot override
route/method, app ownership, logical/DOM identity, host, target/output policy, fallback, limits,
or response conversion.

## Boundary model rules

A boundary model is a Pydantic v2 `BaseModel` attached to exactly one supported source marker,
including Hedron `Model` / `FormModel` subclasses:

```python
Annotated[SearchParams, ViewParams()]
Annotated[CreateRecord, FormBody()]
```

Existing `FormModel` / `Field` / `AutoForm` behavior is retained. `Field` presentation
(`label`, `help`, `secret`, `identity`) remains valid. `Control` overrides generated-form
presentation only and cannot weaken Pydantic or `Field` validation. `secret=True` implies
`Sensitive` disposition; `identity=True` implies `InstanceKey`; contradictions fail
registration. `AutoForm`, explicit `Form(action=handle, ...)`, and `@app.action` stay the
universal path. `ActionHandle.form()` is additive and only for opted-in `FormBody`.
0.50 `ActionHandle.effect` / `.after` compile command success to OOB refresh+toast and
`HX-Trigger-After-Swap` — [Interaction API](INTERACTION.md).

Registration must fail when:

- more than one parameter has the same Hedron boundary source;
- one parameter carries contradictory Hedron source markers;
- a source marker is attached to a non-supported model/type shape;
- a field is simultaneously supplied by a Hedron boundary and FastAPI request-source metadata;
- forward references or generics cannot be resolved through documented typing/Pydantic APIs;
- a dependency/request/context parameter is made bindable;
- model configuration permits behavior the selected boundary cannot serialize safely.

Unknown third-party `Annotated` metadata is preserved and ignored. Hedron metadata is immutable,
hashable where practical, side-effect-free, and safe to inspect without invoking callbacks.

### Validation and serialization

The model's Pydantic validator is authoritative for shape conversion and constraints. Hedron adds
source, identity, redaction, routing, form, and effect validation. It does not duplicate Pydantic's
constraint implementation.

The model validator implements the 0.43 binding-adapter protocol for opted-in handles. Request
boundaries are registered through documented FastAPI/Pydantic public APIs; Hedron does not add a
parallel raw-`Request` parser or invoke FastAPI's dependency solver internally.

All entry paths use the same compiled adapter and configuration:

- `FragmentHandle.bind(model)`;
- `FragmentHandle.bind(**fields)`;
- path/query reconstruction of a bound view;
- command form parsing;
- `AppScenario` schema-validated submission;
- Explorer preview validation.

Field aliases, strictness, defaults, extra-field behavior, discriminators, validators, and
serialization modes therefore cannot drift between tools. A schema/adapter fingerprint changes
when material model configuration changes.

## `ViewParams`

Conceptual signature:

```python
@dataclass(frozen=True, slots=True)
class ViewParams:
    source: Literal["path", "query", "path_query"] = "path_query"
```

`ViewParams` identifies the only parameter model that `bind(...)` may populate. `source` constrains
where model fields may appear but does not guess or invent a route mapping. Path placeholders on
the handle's 0.43 path own path fields; remaining serializable fields use query parameters.
Ambiguous aliases or two fields mapped to the same route name fail registration. `bind(model)`
serializes through the Pydantic adapter then into existing `BoundValues`. Unmodeled handlers keep
`StructuralBindingAdapter`; modeled handlers replace only that adapter.

Calling forms:

```python
card = user_card.bind(UserCardParams(user_id=user.id))
card = user_card.bind(user_id=user.id)
```

Both return `BoundFragment[UserCard]`. Keyword binding is rejected when aliases make it ambiguous;
passing a model instance remains available.

### Errors

| Situation | Result |
|---|---|
| Invalid/missing/extra field | Build-time validation error with stable model field paths. |
| Dependency name supplied to `bind` | `HED-TYPE-BIND-SOURCE` (Planned `HED-TYPE-*` family); value is not accepted. |
| Ambiguous path/query mapping | Registration error. |
| Sensitive value would enter public URL | Registration/build error unless the author explicitly uses a safe non-secret representation. |
| Cross-model instance passed | Type-checker error where visible and runtime validation error. |

## `FormBody`

Conceptual signature:

```python
@dataclass(frozen=True, slots=True)
class FormBody:
    encoding: Literal["urlencoded", "multipart", "auto"] = "auto"
```

`FormBody` parses one ordinary form body into the command input model. Encoding is derived only
when unambiguous; file fields require multipart and contradictory explicit encoding fails at
registration/build time. Existing body-size, file-count, upload, CSRF, method, and content-type
policies remain authoritative.

JSON command bodies continue to use FastAPI's documented `Body`/model conventions. `FormBody`
accepts only `application/x-www-form-urlencoded` or `multipart/form-data` matching the compiled
encoding. Other content types, including JSON and `text/plain`, fail closed with HTTP 415.

### Validation response

Enhanced form requests receive the documented validation fragment/status/header behavior. Ordinary
HTTP requests receive a full-page or redirect/error response according to the command fallback.
Safe submitted values are retained; passwords, tokens, file bytes, and `Sensitive` fields are not
echoed by default.

## Field markers

### `Sensitive`

Conceptual signature:

```python
@dataclass(frozen=True, slots=True)
class Sensitive:
    redact_as: str = "[redacted]"
```

The replacement text is bounded plain text. It cannot contain raw HTML or the original value.
Hedron applies redaction before framework-owned logs, traces, Explorer schemas, error messages,
snapshots, event metadata, instance identity input, and diagnostic context are emitted.

This marker does not intercept application logging, custom renderers, Pydantic custom serializers,
or third-party tools. Secrets should not be put in paths/query strings regardless of this marker.

### `InstanceKey`

Conceptual signature:

```python
@dataclass(frozen=True, slots=True)
class InstanceKey:
    include: bool = True
```

Selected validated fields participate in the bound-fragment identity fingerprint. Raw field values
never become DOM ids or event names. If no fields are selected, the complete safe canonical
binding drives identity as defined by 0.43. Sensitive fields cannot be selected.

### `Control`

Conceptual signature:

```python
@dataclass(frozen=True, slots=True)
class Control:
    kind: str | None = None
    label: str | None = None
    help: str | None = None
    autocomplete: str | None = None
    rows: int | None = None
```

The final supported `kind` values are the closed set in
[type-form-inventory-044.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/type-form-inventory-044.toml):
`text`, `textarea`, `password`, `number`, `checkbox`, `select`, `radio`, `date`,
`time`, `datetime-local`, `file`, `email`, `url`. Unknown values,
unsafe autocomplete tokens, missing usable labels, invalid row bounds, or a hint incompatible with
the field schema fail form generation. `Control` does not accept arbitrary attributes, JavaScript,
raw HTML, roles, event handlers, or validation expressions.

Pydantic `Field` owns title/description/constraints. An explicit `Control` label/help overrides
presentation only. A project may replace generated controls explicitly without changing the model.

## Generated forms

An action handle whose input is marked `FormBody` exposes:

```python
class ActionHandle(Generic[InputModel, Result]):
    def form(
        self,
        *,
        value: InputModel | Mapping[str, object] | None = None,
        errors: Sequence[FieldError] = (),
        submit_label: str = "Submit",
        controls: Mapping[str, NodeLike | Control] | None = None,
        fallback: str | None = None,
        **safe_form_attrs: object,
    ) -> Form: ...
```

Generation requirements:

- one deterministic field/control id namespace per form instance;
- visible labels and linked descriptions/errors;
- fieldsets/legends for grouped choices and discriminated variants;
- safe constraint reflection into native HTML attributes;
- Pydantic alias and nested-field serialization matching request parsing;
- deterministic ordering from model definition plus explicit overrides;
- current CSRF field and action/method/fallback wiring;
- correct URL-encoded or multipart encoding;
- safe value retention and error summary/focus behavior;
- no arbitrary schema-to-HTML interpretation.

The supported-field inventory is locked in
[type-form-inventory-044.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/type-form-inventory-044.toml).
Strings, numbers, booleans, enums/literals, optional scalars, bounded lists/sets of scalars,
date/time types, UUIDs, uploads, and `Secret` (password, never echoed) are Supported.
Nested models, discriminated unions, and lists of models are override-only. Unconstrained
dicts, recursive models, `Any`, callbacks, `TrustedHtml`, component nodes, and arbitrary JSON
Schema are rejected for generation. “Dispositioned” does not mean every shape must be
auto-generated.

## Effect markers

### `Refreshes` and `Updates`

Conceptual signatures:

```python
class Refreshes:
    targets: tuple[FragmentHandle | BoundFragment, ...]

    def __init__(self, *targets: FragmentHandle | BoundFragment): ...


class Updates:
    targets: tuple[FragmentHandle | BoundFragment, ...]

    def __init__(self, *targets: FragmentHandle | BoundFragment): ...
```

They are valid only in a command return annotation or equivalent class configuration. Targets must
be registered in the same app. Duplicates normalize deterministically; excessive targets and
unresolved/foreign handles fail registration.

The actual returned `RefreshIntent`/`PatchSet` is checked against the declaration. The declaration
never executes the refresh/update and cannot widen 0.43 output authorization. A command with no
marker remains explicitly dynamic and is labeled accordingly in tooling. A valid declaration sets
effect knowledge to `declared`; development observations remain non-authoritative traces.

Fallback and cache are not annotation markers. They remain explicit decorator/handle policy (or
equivalent class configuration) using the existing 0.43 validated types.

## Generic handle signatures

Conceptual types:

```python
class FragmentHandle(Generic[ParamsModel, Content]):
    parameter_model: type[ParamsModel] | None
    content_type: object
    schema: TypeSchema

    @overload
    def bind(self, value: ParamsModel, /) -> BoundFragment[Content]: ...

    @overload
    def bind(self, **fields: object) -> BoundFragment[Content]: ...


class BoundFragment(Generic[Content]):
    parameters: BaseModel
    content_type: object
    schema: TypeSchema


class ActionHandle(Generic[InputModel, Result]):
    input_model: type[InputModel] | None
    result_type: object
    schema: TypeSchema

    def form(...) -> Form: ...
```

These are the same generic slots defined in 0.43, not replacement classes or a new arity.
Unmodeled 0.43 handlers keep their coarse `Mapping[str, object]` input slots and `schema is None`
without becoming invalid. The runtime attributes are inspectable, immutable registration metadata.
They contain redacted schema, not current request values. `ActionHandle.form()` is available only
when a supported `FormBody` schema is attached; explicit 0.43 forms remain available for all
actions.

Decorator overloads preserve sync/async callable parameter and return information. The
implementation may use `ParamSpec`, `TypeVar`, protocols, and overloads, but public type-checker
fixtures define the contract. Basic usage cannot require a Hedron-specific mypy/pyright plugin.

## Outcomes and `OutcomeMap`

`OutcomeMap` accepts a discriminated Pydantic union and one mapping per variant.
The frozen builder spelling is:

```python
OutcomeMap[SaveOutcome](
    case(Saved, render=render_saved, status=200, effects=Refreshes(notes)),
    case(Conflict, render=render_conflict, status=409),
)
```

Observable requirements are fixed:

- discriminator variants are finite and resolvable at registration;
- every variant has exactly one mapping;
- mappings declare status, content renderer/response, effects, and fallback where relevant;
- output is validated before mapping;
- renderers receive the validated variant, not raw request data;
- status/effect/fallback values pass existing response/security validation;
- mappings and schemas are redacted and visible in Explorer/tests;
- arbitrary `BaseModel` returns without a mapping are not auto-rendered.

## `RefreshableView`

Conceptual contract:

```python
class RefreshableView(Generic[ParamsModel, Data]):
    host: FragmentHost | None = None
    loading: NodeLike | None = None
    empty: NodeLike | None = None
    error: NodeLike | str | None = None
    cache: CacheHint | None = None

    def load(...) -> Data | Awaitable[Data]: ...
    def render(self, data: Data) -> NodeLike: ...
```

Registration:

```python
view_handle = app.refreshable(ViewClass)
view_handle = app.refreshable(ViewClass(...))
```

Class or instance registration is supported only when lifecycle and concurrency semantics are
unambiguous. The app may construct one immutable/shared handler at registration. Per-request
mutable state requires a documented factory and cannot leak between users. `load` is the route/DI
entrypoint; `render` is not independently dependency-injected.

The return is the same generic `FragmentHandle` as a function view. Path/key/host/fallback
configuration may be supplied by decorator arguments or class attributes; conflicts fail rather
than choose an incidental precedence.

## `CommandHandler`

Conceptual contract:

```python
class CommandHandler(Generic[InputModel, Result]):
    effects: tuple[Refreshes | Updates, ...] = ()
    fallback: str | None = None
    outcomes: OutcomeMap[Result] | None = None

    def execute(...) -> Result | Awaitable[Result]: ...
```

`execute` is the only mutation entrypoint and receives normal dependency injection. Form and
outcome mapping use the same normalized schema. Registration returns the same `ActionHandle` as a
function command and preserves POST/CSRF/fallback/response behavior.

Inheritance is optional at the authoring level when an equivalent class satisfies the documented
protocol. Duck-typed registration must still reject ambiguous method names, mutable shared state,
or unsupported signatures.

## `TypeSchema`

`TypeSchema` is an immutable, versioned extension of a 0.43 `BaseHandleDescriptor` attached at
`extensions["hedron.type"]`. Payload keys and mismatch behavior are locked in
[type-schema-044.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/type-schema-044.toml). At minimum it
exposes:

- schema version, stable handler/model fingerprints, and the referenced 0.43 base-descriptor
  version/fingerprint;
- handler kind, boundary sources, model/field paths, constraints, aliases, and provenance;
- supported control dispositions and explicit overrides;
- sensitive/identity dispositions without values;
- result type, outcome variants, and declared/dynamic effects;
- route/schema visibility and relevant fallback/cache metadata;
- diagnostics for unsupported or partially known static information.

It is not the raw Pydantic JSON Schema and cannot contain application instances, dependency values,
secrets, callbacks, arbitrary reprs, or executable code. Pydantic JSON Schema and FastAPI OpenAPI
remain available for their own purposes. A base-descriptor mismatch invalidates the extension;
tools do not apply it best-effort or use it to reconstruct routing/authorization.

## Static and dynamic inspection

Runtime/dynamic inspection occurs after the trusted application is imported normally. Static CLI
inspection parses source without importing modules or evaluating string annotations. Static
findings distinguish syntactic facts, unresolved names, and runtime-only facts; they do not claim a
complete schema when one cannot be proven.

## Hosts and versions

FastAPI is the complete flagship. Flask, Django, and Jinja either consume portable
`TypeSchema`/results or emit a machine-visible bounded exception. Dispositions:
[`adapter-disposition-044.toml`](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/adapter-disposition-044.toml).
This phase does not implement 0.45 catalogs or 0.46 workflows.

Supported authoring matrix: Python 3.10–3.14, Pydantic v2 public APIs only, FastAPI/Starlette as
pinned on the 0.43 train, stock mypy and pyright. No required type-checker plugin.

The `HED-TYPE-*` diagnostic family, including `HED-TYPE-BIND-SOURCE` (`HED-TYPE-0001`),
is listed in the [error catalog](../guides/error-codes.md#hed-type-044). These codes are
runtime diagnostics on the 0.44 train.

## Common errors

| Situation | Required behavior |
|---|---|
| Multiple or conflicting boundary markers | Registration fails with model/parameter context. |
| Unsupported generated control | Form build fails and recommends an explicit field/form override. |
| Dependency submitted as input | Value is ignored/rejected; dependency injection remains authoritative. |
| Sensitive default/example in tooling schema | Registration/schema check fails; value is not emitted. |
| Actual effect outside `Refreshes`/`Updates` | Response conversion fails safely before output. |
| Unmapped/wrong outcome | Safe server error plus stable diagnostic; no model repr/value leak. |
| Mutable shared class handler state | Registration/check failure or explicit documented factory requirement. |
| Recursive/excessive schema | Generation fails within bounds; explicit manual handler/form remains available. |
| Static scan needs import/evaluation | Finding is marked unknown; no import/evaluation occurs. |

## See also

- [Refreshable views and commands](REFRESHABLE_VIEWS.md)
- [Models](MODELS.md)
- [Forms and actions guide](../guides/forms-and-actions.md)
- [Actions](ACTION.md)
- [FastAPI integration](HEDRON.md)
- [Testing](TESTING.md)
- [RFC-0071](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0071-TYPE-DRIVEN-AUTHORING.md)
- [Phase 0.44 implementation requirements](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/TYPE_DRIVEN_AUTHORING_044.md)
- [Phase 0.44 acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_44.md)
- [Form field inventory](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/type-form-inventory-044.toml)
- [TypeSchema lock](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/type-schema-044.toml)
- [Adapter dispositions](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/adapter-disposition-044.toml)
