---
status: current
phase: "0.43"
---

# Refreshable views and commands

**Decision/RFC:** D-071, refined by D-073 /
[RFC-0070](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0070-REFRESHABLE-VIEWS.md)

!!! note "Beta 0.43 contract"

    These symbols are **beta** on the Published 0.43 train, which extends the 0.42
    region/`InteractionResult` stack
    (D-071 / D-073). Existing [Interaction APIs](INTERACTION.md)
    remain the shipped low-level interface. 0.44 may specialize generic bind slots without
    changing arity, routing, or conversion goldens.

Refreshable views and commands are the high-level interface for server-rendered partial updates:

```python
from hedron import Hedron, Page, refresh

app = Hedron(...)


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

The low-level region, selector, and `InteractionResult` APIs remain available for advanced HTMX
work. The high-level interface compiles to those existing contracts.

Phase 0.43 owns the runtime foundation. The planned
[0.44 type-driven contract](TYPE_DRIVEN_AUTHORING.md) (D-076 refine against this published
seam) fills the generic input slots and `hedron.type` descriptor extension defined here; it does
not replace 0.43 routing, binding identity, forms, effects, or target authorization.

## Planned symbols

| Symbol | Package | Role |
|---|---|---|
| `Hedron.refreshable` | `hedron` | Register a GET renderer and return a `FragmentHandle`. |
| `Hedron.command` | `hedron` | Register a mutation and return an `ActionHandle`. |
| `FragmentHandle` | `hedron` | Callable mounted-view, route, target, control, patch, and inspection handle. |
| `BoundFragment` | `hedron` | Parameter-bound fragment instance with a stable instance identity. |
| `FragmentHost` | `hedron-core` / `hedron` | Stable semantic wrapper for initial and refreshed content. |
| `ActionHandle` | `hedron` | Typed command reference for buttons, forms, tests, and inspection. |
| `Refresh` | `hedron` | Native control targeting a fragment handle. |
| `refresh` | `hedron` | Build a bounded refresh intent for one or more views. |
| `Patch` | `hedron-core` / `hedron` | Direct update for one registered target. |
| `PatchSet` | `hedron-core` / `hedron` | One primary plus ordered secondary direct updates. |
| `patches` | `hedron` | Ergonomic `PatchSet` builder. |

Final import placement and signatures must be confirmed by `API-043`; names and semantics in this
contract may not drift silently during implementation.

## `Hedron.refreshable`

Conceptual signatures:

```python
@app.refreshable
def view(...) -> NodeLike: ...

@app.refreshable(
    path: str | None = None,
    *,
    key: str | None = None,
    name: str | None = None,
    host: FragmentHost | None = None,
    loading: NodeLike | None = None,
    error: NodeLike | str | None = None,
    fallback: str | None = None,
    include_in_schema: bool = False,
    dependencies: Sequence[Depends] | None = None,
) -> Callable[[Callable[P, ContentT]], FragmentHandle[Mapping[str, object], ContentT]]: ...
```

The first `FragmentHandle` type slot is deliberately the bind-input type, not the renderer's
`ParamSpec`. In 0.43 it is coarse `Mapping[str, object]`; 0.44 may specialize it to a Pydantic model
without changing generic arity. The original callable signature remains available through renderer
inspection.

### Parameters

| Parameter | Meaning |
|---|---|
| `path` | Optional explicit route. Omitted paths are generated, internal, mount-aware, and not external compatibility promises. |
| `key` | Optional stable DOM/application identity. Omitted keys derive deterministically from the logical route id. |
| `name` | Registry and reverse-route name; defaults to the renderer name. |
| `host` | Semantic tag and safe host attributes shared by initial and refresh rendering. |
| `loading` | Optional visible loading content; previous useful content remains available by default. |
| `error` | Optional safe failure content. It does not replace server-side error handling. |
| `fallback` | Full-page URL for controls that claim no-JavaScript progressive enhancement. |
| `include_in_schema` | Generated/internal routes are hidden by default. |
| `dependencies` | Ordinary FastAPI dependencies applied when the view route runs. |

### Returns

The decorator returns a `FragmentHandle` while registering the original renderer as a component
route. The handle preserves the renderer and its inspection metadata. Calling the handle takes no
renderer/dependency arguments and returns a mounted host; parameterized views use `bind(...)`
first. The renderer's dependencies run only on the registered GET route.

### Errors

| Situation | Result |
|---|---|
| Unsafe or duplicate explicit key | Registration error with a stable `HED-VIEW-*` diagnostic. |
| Duplicate unbound mount in one page | Development/build diagnostic; production render fails safely before duplicate ids are emitted. |
| Missing renderer argument | Normal Python/signature error with handle/route context. |
| Conflicting client `HX-Target` | HTTP 403 through the existing target disagreement policy. |
| Direct navigation without a configured full-page fallback | Fragment response; controls must not claim progressive enhancement. |

## `FragmentHandle`

Conceptual members:

```python
class FragmentHandle(Generic[BindT, ContentT]):
    logical_id: str
    name: str
    path: str
    method: Literal["GET"]
    dom_id: str
    selector: str               # inspectable compatibility detail
    region: FragmentRegion      # low-level compatibility value
    ref: ComponentRef
    renderer: Callable[..., ContentT]
    renderer_signature: Signature

    def __call__(self) -> FragmentHost: ...
    def bind(self, **parameters: object) -> BoundFragment[ContentT]: ...
    def refresh_button(self, label: str = "Refresh", **kwargs: object) -> Refresh: ...
    def replace(self, content: ContentT, **kwargs: object) -> Patch[ContentT]: ...
    def update(self, content: ContentT, **kwargs: object) -> Patch[ContentT]: ...
```

`selector` and `region` exist for inspection and advanced interoperation; beginner examples do not
copy them into markup or route policy. The two generic slots and their order are fixed by 0.43;
their precision may improve in 0.44 without changing the runtime class.

## Bound fragments

```python
card = user_card.bind(user_id=user.id)

Page(card(), card.refresh_button())
```

0.43 binding is structural. It must:

- accept only registered bindable path/query names and validate required/extra parameters;
- resolve path parameters and encode query parameters through safe URL helpers;
- derive a deterministic instance id without exposing secret values;
- preserve the base handle's app ownership and policy;
- reject unresolved parameters before render;
- allow the same bound object to drive mounting, controls, patches, tests, and diagnostics.

It does not call dependency injection or perform full Pydantic/domain validation. The normal GET
route remains authoritative and may return its ordinary validation error. The 0.44 model adapter
may add eager validation for explicitly modeled views through the same binding protocol.

Two instances with the same canonical binding have the same identity. Authors mounting the same
binding twice must provide an explicit instance key or restructure the page.

## Fragment hosts

The default host is neutral and owns interaction state. A conceptual configuration is:

```python
FragmentHost(
    tag="section",
    role="status",
    aria_live="polite",
    attrs={"class": "status-panel"},
)
```

Only safe ordinary HTML/ARIA attributes are accepted. The host must preserve its tag, attributes,
identity, focus contract, and accessible name across initial and replacement renders. The framework
does not add `role="status"` or a landmark automatically.

## Refresh controls

Equivalent forms:

```python
status.refresh_button("Refresh")
Refresh(status, label="Refresh")
```

`Refresh` renders a native control and derives its URL, target, swap, synchronization, indicator,
and fallback behavior from the handle. An explicit caller override may narrow presentation but may
not redirect the control to a different unregistered target.

## Commands and `ActionHandle`

Conceptual signatures:

```python
@app.command
def save_note(...): ...

@app.command(
    path: str | None = None,
    *,
    method: str = "POST",
    name: str | None = None,
    fallback: str | None = None,
    include_in_schema: bool = False,
    dependencies: Sequence[Depends] | None = None,
) -> Callable[[Callable[P, ResultT]], ActionHandle[Mapping[str, object], ResultT]]: ...
```

`ActionHandle` has the same fixed two-slot convention: command input, then result. Phase 0.43 uses a
coarse mapping input; 0.44 may specialize it to a `FormBody` model.

`ActionHandle` provides at least:

```python
save_note.button("Save")
Form(action=save_note, ...)
scenario.run(save_note, note="Hello")
```

Conceptual members:

```python
class ActionHandle(Generic[InputT, ResultT]):
    logical_id: str
    name: str
    path: str
    method: str
    result_type: object
    handler: Callable[..., ResultT]
    handler_signature: Signature

    def button(self, label: str, **kwargs: object) -> NodeLike: ...
```

Commands default to POST. Unsafe methods follow the active CSRF strategy; action handles do not
embed or bypass application authorization. Generated routes are hidden from OpenAPI by default.

### Explicit forms in 0.43

`Form(action=save_note, ...)` still requires explicit fields/controls. The handle supplies the
registered URL, method, CSRF/fallback integration, identity, and testing metadata. Phase 0.43 does
not expose `ActionHandle.form()` or infer fields from annotations. Those capabilities begin in 0.44
only for an explicit `FormBody` model.

## `refresh`

```python
return refresh(status)
return refresh(notes, note_count).toast("Saved")
```

`refresh` returns a typed refresh-intent result. After a successful enhanced command response, each
mounted target performs its normal GET route. This preserves route dependencies and avoids invoking
FastAPI dependency injection from application code.

Requirements:

- targets are registered handles or bound fragments from the active app;
- duplicate targets are coalesced in deterministic order;
- target count and serialized event size are bounded;
- disconnected or absent targets do nothing safely;
- host request synchronization prevents an unbounded queue;
- non-HTMX requests follow the command fallback/redirect path;
- a refresh intent is not a business transaction or cache invalidation protocol.

## Direct patches

```python
return status.replace(StatusPanel(...))

return patches(
    notes.replace(notes_panel()),
    note_count.update(count_panel()),
    toast="Saved",
)
```

`replace` uses `outerHTML`; `update` uses `innerHTML`. `patches` uses its first positional patch as
the primary response and later patches as ordered OOB updates.

Conceptual types:

```python
@dataclass(frozen=True, slots=True)
class Patch(Generic[ContentT]):
    target: FragmentHandle | BoundFragment
    content: ContentT
    swap: Literal["outerHTML", "innerHTML"]


@dataclass(frozen=True, slots=True)
class PatchSet:
    primary: Patch
    secondary: tuple[Patch, ...] = ()
    status_code: int = 200
    toast: NodeLike | str | None = None
    cache: CacheHint | None = "vary-htmx"
```

Additional typed `InteractionResult` fields may be exposed where they retain identical validation.
Arbitrary `headers`, selector strings, and untyped event JavaScript stay on the advanced API.

### Patch errors

| Situation | Result |
|---|---|
| No primary patch | Construction error. |
| Duplicate target | Construction error; never emit two mechanisms for one target. |
| Foreign-app or unregistered handle | Authorization/contract error before render. |
| Unbound parameterized handle | Binding error. |
| OOB content with status 204 | Rejected like `InteractionResult`. |
| Unsafe/unknown swap | Construction error. |
| Content exceeds existing render/payload bounds | Existing rendering/response failure. |

## Testing API

Planned `AppScenario` additions:

```python
scenario.refresh(status)
scenario.expect(status).to_contain("Healthy")
scenario.run(save_note, note="Hello")
scenario.expect(notes).to_contain("Hello")
scenario.expect_refreshes(notes, note_count)
scenario.expect_patch(note_count, swap="innerHTML")
```

Assertions resolve route, target, and instance identity through handles. Existing raw request,
fragment, header, OOB, and selector assertions remain supported.

## Compatibility layer

| High-level operation | Existing low-level translation |
|---|---|
| Refreshable handle | Component route + `FragmentRegion` + `ComponentRef` |
| Mounted view | Stable id host + HTMX attributes |
| Refresh control | `RefreshButton`/native control with derived target and route |
| Direct patch | `InteractionResult` primary content and canonical `region_id`/retarget |
| Secondary patch | Authorized `OobUpdate` |
| Refresh intent | Typed bounded HTMX trigger consumed by registered hosts |
| Command | Existing action route, CSRF policy, and response conversion |

## Base handle descriptor and 0.44 extensions

Runtime, Explorer, CLI, `AppScenario`, and adapters consume one versioned base handle descriptor.
It records handle kind, logical/app identity, route/method, host/target/output mechanics, structural
binding plan, fallback, limits, stability, and extension namespaces. The base descriptor is
authoritative; tools must not re-inspect the handler to reconstruct these facts independently.

In 0.43, command effect knowledge is one of:

- `dynamic`: possible targets are unknown until execution;
- `observed`: a development trace recorded actual targets, but this is not a declaration.

Phase 0.44 may attach a versioned redacted `TypeSchema` extension and change effect knowledge to
`declared`. The extension references the base descriptor fingerprint and may narrow validation or
improve tooling. It cannot override the route, app ownership, target authority, host, fallback, or
response conversion. Unknown extension namespaces do not alter base behavior.

The 0.43 binding adapter performs structural binding. Its protocol is the only supported extension
point for the 0.44 Pydantic adapter; consumers do not create a second binding path.

## Stability

All new 0.43 symbols begin at `beta`. Existing region and interaction symbols keep their current
stability. Stable promotion requires an explicit inventory update and every phase gate Verified;
documentation preference alone does not change API stability.

## See also

- [RFC-0070](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0070-REFRESHABLE-VIEWS.md)
- [0.43 implementation requirements](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/INTERACTION_HANDLES_043.md)
- [Interaction APIs](INTERACTION.md)
- [Actions](ACTION.md)
- [Progressive enhancement](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0053-PROGRESSIVE-ENHANCEMENT.md)
- [0.43 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_43.md)
- [Planned 0.44 type-driven extension](TYPE_DRIVEN_AUTHORING.md)
