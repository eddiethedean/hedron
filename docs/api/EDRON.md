---
status: verified
---

# Edron 1.0 design and compatibility contract

**Status:** Edron `1.0.0` verified in-tree; Beta satellite with tag/PyPI publication deferred<br>
**Target:** Edron `1.0.x`; Hedron `1.0.x` (`>=1.0.0,<1.1`)<br>
**Historical 0.1 target metadata:** Edron `0.1.0`; compatible Hedron train and release phase unassigned<br>
**Roadmap:** [Edron `0.x` release roadmap](../EDRON_ROADMAP.md)<br>
**Authority:** [RFC-0094](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)<br>
**Packaging:** [Edron 0.1 packaging](EDRON_PACKAGING.md)<br>
**Capability inventories:** [Edron 0.1 capability inventories](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_CAPABILITY_INVENTORIES.md)<br>
**Implementation:** [Edron 0.1 implementation specification](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_001.md)<br>
**Acceptance:** [Edron 0.1 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_001.md)<br>
**Executable-design fixtures:** [Edron golden applications](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_GOLDEN_APPS.md)

This document preserves the detailed lowering and compatibility contract behind Edron 1.0.
For task-oriented public reference, start with [Edron API by task](EDRON_REFERENCE.md) and the
[generated symbols](EDRON_AUTODOC.md). The original 0.1 sections remain historical design
foundations; release and migration details are in the [Edron user guide](../guides/edron-user-guide.md)
and [1.0 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_100.md).
Signatures use
Python typing notation; imported native types keep their owning Hedron package and stability level.

## Short example

```python
import edron as ed

app = ed.App(
    title="Sales",
    theme=ed.theme("acme", accent="#635bff"),
)


@app.page("/", title="Sales dashboard")
class SalesPage(ed.Page):
    def render(self) -> None:
        region = self.sidebar.selectbox(
            "Region",
            ("All", "North", "South"),
            name="region",
            default="All",
            updates=self.results,
        )
        self.results(region=region)

    @ed.fragment
    def results(self, region: str) -> None:
        rows = load_sales(region)
        self.line_chart(rows, x="month", y="revenue")
        self.dataframe(rows, name="sales")

    @ed.action
    def reload(self) -> ed.Outcome:
        load_sales.invalidate()
        return ed.refresh(self.results)
```

The conventional import is `import edron as ed`. Documentation does not use or recommend
`import edron as st`.

## Contract language and stability

The words **must**, **must not**, **required**, **should**, and **may** are normative. Edron `1.0.0`
is a Stable distribution. Only the deliberately small root authoring surface listed in the
stable API contract is API tier `stable`; native internals and optional adapters remain non-stable.
Identity re-exports retain the native Hedron symbol's own tier. Experimental third-party adapters
remain explicitly `experimental` even when reached through an Edron method.

The current compatibility promise covers:

- documented import names and signatures;
- lifecycle and request-phase rules;
- native Hedron object identity and registry projection;
- HTTP method, HTMX, fallback, CSRF, and target behavior;
- optional-capability activation and structured error categories;
- styling precedence and native-authority behavior; and
- stable Edron diagnostic codes listed here.

Edron exposes the native Hedron `Interaction`, `Outcome`,
`AlpineFeatureDemand`, `BrowserFeaturePlan`, and `BrowserPlanClosure` contracts. These are identity
re-exports: Edron does not create a parallel browser runtime, request authority, or outcome algebra.
Use `edron.Interaction.local`, `.request`, or `.combined` for declared interactions and
`edron.browser_plan()` for demand-driven browser assets. Edron 1.0 registers page, view, action,
and feature roles through the canonical Hedron 1.0 APIs and does not maintain parallel handle,
router, lifecycle, or outcome-lowering implementations.

Generated internal paths, DOM IDs, private classes, private descriptor/compiler types, buffer
implementation, exact HTML whitespace, and private native Hedron implementation details are not
compatibility promises. Authors needing a persistent URL, route name, component identity, or CSS
hook must provide or use its documented public form.

## Distribution contract

The normative artifact, dependency, capability, extras, and release requirements are defined in
the [Edron packaging contract](EDRON_PACKAGING.md). This section freezes the public installation
surface.

The `edron` distribution supports Python 3.10 through 3.14 on the 1.0 train.

`pip install edron` requires `hedron>=1.0.0,<2.0` and `hedron-data>=1.0.0,<2.0`, plus the
compatible `hedron-charts`, `hedron-maps`, Markdown/sanitization, and Uvicorn dependencies. The
native 1.0 integration is frozen in the
[1.0 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_100.md).

The package publishes `py.typed`, wheel, and source distributions. Importing `edron` must not:

- import optional third-party data/chart/database libraries;
- start a server, register a process-global application, open a file, or contact the network;
- install a dependency; or
- mutate a Hedron registry before an `App` or native application is constructed.

## Root export inventory

The following is the complete intended beginner root inventory for the original Edron foundation. The
0.9 native aliases are documented above. A symbol not listed here is
not promised from `edron`, even when it is available from a native Hedron package.

| Export | Kind | Tier | Contract |
|---|---|---|---|
| `App` | Edron class | beta | ASGI application facade and registration owner |
| `Page` | Edron base class | beta | Fresh request-scoped page controller/output surface |
| `Container` / `FilterScope` | Edron request-local values | beta | Explicit layout and coherent safe-filter scopes |
| `fragment` / `Fragment` / `BoundFragment` | decorator and descriptors | beta | Safe independently refreshable page method |
| `action` / `Action` / `BoundAction` | decorator and descriptors | beta | Unsafe page-method command and explicit binding |
| `Outcome` | type alias | beta | Supported native action result union |
| `success` / `refresh` | functions | beta | Small constructors for native outcomes/effects |
| `dependency` / `Dependency` | function and descriptor | beta | Typed native request dependency on a page |
| `cache_data` / `CachedFunction` | decorator and protocol | beta | Bounded recomputable data cache |
| `Confirm` | immutable value | beta | Accessible confirmation request for an action control |
| `download` / `Download` | function and immutable value | beta | Opaque authorized download reference |
| `JobFlow` | Edron class | beta | Thin composition over native Hedron `TaskFlow` |
| `JobBackend` / `JobScope` | identity re-exports | native tier | Native Hedron job contracts |
| `theme` | function | beta | Small brand constructor returning native `DesignSystem` |
| `Color` / `DesignSystem` / `StyleRecipe` | identity re-exports | native tier | Selected native styling value types |
| `EdronError` | exception | beta | Base for Edron-owned structured failures |
| `RegistrationError` / `PhaseError` / `BindingError` | exceptions | beta | App/page/request-plan contract failures |
| `CapabilityError` | exception | beta | Base optional-capability failure |
| `MissingCapabilityError` | exception | beta | Required third-party distribution absent |
| `IncompatibleCapabilityError` | exception | beta | Installed third-party version unsupported |
| `BrokenCapabilityError` | exception | beta | Dependency present but import/initialization broken |

Identity re-export means object identity, not merely compatible behavior:

```python
ed.Color is hedron.Color
ed.DesignSystem is hedron.DesignSystem
ed.StyleRecipe is hedron.StyleRecipe
ed.JobBackend is hedron_core.jobs.JobBackend
ed.JobScope is hedron.JobScope
```

The contract does not re-export `hedron.Page`, arbitrary components, raw HTML, FastAPI, or every
Hedron handle. Advanced users import those symbols from their native package and compose them
directly.

## Common types

The conceptual aliases below are used throughout the signatures:

```python
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from inspect import Signature
from pathlib import Path
from types import TracebackType
from typing import Any, Generic, Literal, ParamSpec, Protocol, TypeAlias, TypeVar, overload

from fastapi.params import Depends
from hedron import (
    ActionHandle,
    BoundFragment as NativeBoundFragment,
    Color,
    ComponentRef,
    DesignSystem,
    FragmentHandle,
    Hedron,
    InteractionResult,
    JobScope,
    Patch,
    PatchSet,
    RefreshIntent,
    ScreenHandle,
    SecurityPolicy,
    StyleRecipe,
    StyleContext,
    Theme,
    ThemeSpec,
)
from hedron_core.component import NodeLike
from hedron_core.bundles import FeatureBundle, FeatureProvider
from hedron_core.diagnostics import Diagnostic as HedronDiagnostic
from hedron_core.jobs import JobBackend
from hedron_core.registry import ApplicationStyleMeta
from hedron_core.typing_aliases import JsonValue
from pydantic import BaseModel
from starlette.responses import Response

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")
OptionT = TypeVar("OptionT")
ModelT = TypeVar("ModelT", bound=BaseModel)
PageT = TypeVar("PageT", bound="Page")
InputT = TypeVar("InputT", bound=BaseModel)
ResultT = TypeVar("ResultT")

Outcome: TypeAlias = InteractionResult | RefreshIntent | Patch[Any] | PatchSet | Response
NativeTheme: TypeAlias = str | Theme | ThemeSpec | DesignSystem
UpdateTarget: TypeAlias = (
    Fragment[Any]
    | BoundFragment[Any]
    | FragmentHandle[Any, Any]
    | NativeBoundFragment[Any]
    | ComponentRef
)
UpdateTargets: TypeAlias = UpdateTarget | Sequence[UpdateTarget]
```

`Any` in these explanatory aliases does not make runtime binding permissive. Registered
signatures, Pydantic, native handles, and component contracts remain authoritative.

## Execution phases and instance lifetime

Edron has four explicit execution phases:

| Phase | Entered by | Output methods | Mutation |
|---|---|---|---|
| `registration` | Import/app setup | Forbidden | Forbidden |
| `page` | Full page `GET` | Allowed | Forbidden |
| `fragment` | Initial materialization or fragment `GET` | Allowed | Forbidden |
| `action` | Unsafe action request/test invocation | Forbidden | Application-owned mutation allowed |

For each full page, standalone fragment, or action HTTP request, Edron constructs a fresh instance
of the registered page class. Page objects and output containers are never shared between requests.
An initial fragment mounted while `render()` runs executes exactly once on that page request's
instance inside a nested fragment buffer. A later fragment HTTP request constructs a new instance
and invokes only that fragment; it does not invoke `render()` first.

`self` may hold temporary values during one invocation, but it is not session or durable state.
Edron enters the current request/output context with an async-safe context-local mechanism and
clears it in `finally`, including cancellation and error paths. A child task may inherit context
only while awaited inside the active request. Detached/background tasks must not emit output.

Only three author-controlled method roles exist in 0.1:

- `render()` for the full page;
- `@ed.fragment` for safe independently refreshable output; and
- `@ed.action` for unsafe work.

There are no `setup`, `mounted`, `rerun`, `before_render`, or `after_render` hooks.
`render`, fragment, and action methods may be synchronous or asynchronous. The active request and
output container remain correct across an awaited call; output from an un-awaited/detached task is
rejected after the owning phase closes.

## `App`

### Signature and members

```python
class App:
    def __init__(
        self,
        *,
        title: str,
        theme: NativeTheme | None = None,
        security: SecurityPolicy | Literal["development", "standard", "strict"] = "standard",
        session_secret: str | None = None,
        production: bool | None = None,
        build_dir: str | Path | None = None,
        root_path: str = "",
        debug: bool = False,
    ) -> None: ...

    @classmethod
    def from_hedron(cls, hedron: Hedron) -> App: ...

    @property
    def hedron(self) -> Hedron: ...

    def page(
        self,
        path: str,
        *,
        title: str,
        name: str | None = None,
        show_title: bool = True,
        dependencies: Sequence[Depends | object] = (),
    ) -> Callable[[type[PageT]], type[PageT]]: ...

    def include(
        self,
        feature: JobFlow[Any, Any] | FeatureProvider | FeatureBundle,
    ) -> None: ...

    def styles(
        self,
        name: str,
        source: str | Path,
        *,
        scope: str | None = None,
        layer: Literal["application", "overrides"] = "application",
        global_: bool = False,
        media: tuple[str, ...] = (),
        allowed_roots: Sequence[str | Path] | None = None,
    ) -> ApplicationStyleMeta: ...

    @overload
    def native(self, surface: type[Page]) -> ScreenHandle[Any]: ...

    @overload
    def native(
        self,
        surface: Fragment[Any] | BoundFragment[Any],
    ) -> FragmentHandle[Any, Any] | NativeBoundFragment[Any]: ...

    @overload
    def native(
        self,
        surface: Action[Any, Any] | BoundAction[Any, Any],
    ) -> ActionHandle[Any, Any]: ...

    @overload
    def native(self, surface: JobFlow[Any, Any]) -> FeatureBundle: ...

    async def __call__(self, scope: object, receive: object, send: object) -> None: ...
```

`App(...)` constructs one native `Hedron` application. `App.from_hedron(...)` attaches Edron to an
existing unsealed native application and uses that application's title, theme, security, root path,
middleware, and dependency configuration. It never copies the native app. Registration fails if
the native registry or OpenAPI schema is already sealed.

`session_secret`, `production`, and `build_dir` are the small construction-time production surface
and preserve the corresponding native Hedron meaning. With `session_secret=None`, Edron may use
the native development default only outside production; strict security or the production gate
requires an explicit application secret. `production=None` follows the native environment policy.
Applications needing different session enablement, a custom lifespan, Explorer construction, or
other FastAPI/Hedron constructor options construct `Hedron(...)` explicitly and use
`App.from_hedron(...)`. These settings cannot be retrofitted later through `app.hedron`.

`app.hedron` is the canonical underlying-app property. There is no `native_app` synonym in 0.1.
The `App` object itself is ASGI-callable and delegates to that exact instance, so both commands are
supported:

```bash
edron run app.py
uvicorn app:app
```

`App.include(...)` accepts only documented feature/provider types. In 0.1 that includes `JobFlow`
and compatible native Hedron `FeatureProvider`/`FeatureBundle` values. It returns `None`; the native
registered bundle for an Edron `JobFlow` is available through `app.native_surface(flow)`. A directly
included native `FeatureBundle` already is the native object and remains available through the
Hedron catalog.

`App.styles(...)` has the same arguments and return object as `app.hedron.styles(...)` and delegates
once. Registration order, source roots, scope, cascade layer, CSP, and late-registration checks are
native Hedron behavior.

### Page registration

`@app.page(...)` accepts a class, not an instance. The class must directly subclass `ed.Page`,
declare `render`, have no custom `__init__`, and declare no duplicate decorated surface name.
Decorated actions/fragments inherited from a base class are not exposed. Ordinary inherited helper
methods are allowed.

The decorator returns the same class object:

```python
decorated is OriginalClass
```

`title` supplies document title, the default navigation label when another native navigation
surface includes the page, and one visible `h1` when `show_title=True`. Edron never guesses it from
the path or class name. `name` defaults to the class name normalized under native route rules.

Page-route dependencies are ordinary native/FastAPI dependency declarations. They may authorize a
request, but page visibility, registration, navigation presence, and generated paths are not
authorization evidence.

## `Page` and output containers

`Page` is a request-scoped controller with output methods. It is not a Hedron component and must not
be passed to `self.include(...)` or native renderers.

All signatures below whose first parameter is `self` are methods on both `Page` and `Container`
unless the surrounding section says otherwise. `sidebar` exists only on `Page`.

```python
class Container:
    def __enter__(self) -> Container: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]: ...

class FilterScope:
    def __enter__(self) -> FilterScope: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]: ...

class Page:
    def render(self) -> None | Awaitable[None]: ...

    @property
    def sidebar(self) -> Container: ...

    def include(self, value: NodeLike) -> None: ...
    def container(self, *, border: bool = False) -> Container: ...
    def card(
        self,
        *,
        variant: Literal["plain", "outlined", "raised"] | None = None,
        recipe: str | StyleRecipe | None = None,
        density: str | None = None,
        padding: str | None = None,
    ) -> Container: ...
    def columns(
        self,
        spec: int | Sequence[int | float],
        *,
        gap: Literal["sm", "md", "lg"] = "md",
        vertical_alignment: Literal["top", "center", "bottom", "stretch"] = "top",
    ) -> tuple[Container, ...]: ...
    def tabs(self, labels: Sequence[str]) -> tuple[Container, ...]: ...
    def expander(self, label: str, *, expanded: bool = False) -> Container: ...
    def style_scope(
        self,
        *,
        theme: NativeTheme | None = None,
        color_mode: Literal["light", "dark", "system"] | None = None,
        density: Literal["compact", "comfortable", "spacious"] | None = None,
        context: StyleContext | None = None,
    ) -> Container: ...
```

`Container` supports the same output, input, action-control, and nested-layout methods as `Page`,
except `sidebar`. It is a context manager. Entering it makes that container current; leaving it
restores the previous container even after an exception. A container may be used explicitly:

```python
left, right = self.columns(2)
left.metric("Revenue", revenue)
right.metric("Orders", orders)
```

or as a scope:

```python
with self.card(variant="raised"):
    self.metric("Revenue", revenue)
```

Containers are request-local and cannot be cached, stored in session, reused by another request,
or entered concurrently. An empty container is permitted only when the corresponding native
component permits it.

### Body-level native composition

`include(value)` is the sole canonical body-level escape hatch in 0.1. There is no
`self.hedron(...)` synonym. It accepts every public native Hedron `NodeLike` and public
`__hedron_node__`-compatible value, including a mounted native fragment or an action control.

Edron preserves the original native object/result, identity, assets, theme metadata, trust marker,
and accessibility contract. A full native `hedron.Page`, Starlette/FastAPI `Response`, router, app,
or unresolved handle is invalid inside a body. Full native pages and responses are registered
through `app.hedron`.

## Display methods

All display methods append exactly one logical native output to the current container and return
`None`. They do not return a component reference. Advanced authors construct/import a native
component and pass it to `include` when they need an object.

### Text and feedback

```python
def heading(self, text: str, *, level: Literal[2, 3, 4, 5, 6] = 2) -> None: ...
def subheader(self, text: str) -> None: ...
def text(self, text: str) -> None: ...
def caption(self, text: str) -> None: ...
def markdown(self, source: str) -> None: ...
def code(self, source: str, *, language: str | None = None) -> None: ...
def divider(self) -> None: ...
def success(self, message: str) -> None: ...
def info(self, message: str) -> None: ...
def warning(self, message: str) -> None: ...
def error(self, message: str) -> None: ...
def empty(self, message: str) -> None: ...
```

`markdown` always uses the bundled native Markdown/sanitization policy. It has no
`unsafe_allow_html` flag. Trusted HTML remains an explicit native Hedron type and trust boundary.
`subheader(text)` is exactly `heading(text, level=2)` and exists because the vocabulary is familiar;
it is not a distinct semantic component.

### Metrics, tables, charts, and maps

```python
def metric(
    self,
    label: str,
    value: str | int | float,
    *,
    delta: str | int | float | None = None,
    format: str | None = None,
    help: str | None = None,
) -> None: ...

def table(
    self,
    data: object,
    *,
    name: str | None = None,
    caption: str | None = None,
) -> None: ...

def dataframe(
    self,
    data: object,
    *,
    name: str,
    page_size: int = 25,
    height: Literal["sm", "md", "lg", "auto"] = "auto",
    variant: Literal["compact"] | None = None,
    recipe: str | StyleRecipe | None = None,
) -> None: ...

def line_chart(self, data: object, *, x: str, y: str | Sequence[str], title: str | None = None, description: str | None = None) -> None: ...
def area_chart(self, data: object, *, x: str, y: str | Sequence[str], title: str | None = None, description: str | None = None) -> None: ...
def bar_chart(self, data: object, *, x: str, y: str | Sequence[str], title: str | None = None, description: str | None = None) -> None: ...
def scatter_chart(self, data: object, *, x: str, y: str, color: str | None = None, title: str | None = None, description: str | None = None) -> None: ...

def map(
    self,
    data: object,
    *,
    latitude: str = "latitude",
    longitude: str = "longitude",
    label: str | None = None,
    description: str | None = None,
) -> None: ...
```

`table` is a bounded static semantic table. `dataframe` is the first-party `hedron-data` data-view
path and requires a stable `name`. Neither implies editability. Editing begins with an explicit
Pydantic model and native/accepted Edron data-editor contract; it is deferred from the 0.1 root
surface rather than hidden behind `dataframe`.

The four generic chart methods use first-party `hedron-charts` and require no third-party plotting
library. They must provide a semantic description and accessible data fallback for a Supported
claim. `map` uses `hedron-maps` and follows its geometry, tile, CSP, offline, and accessibility
limits.

### Third-party display adapters

```python
def plotly_chart(
    self,
    data_or_figure: object,
    *,
    x: str | None = None,
    y: str | Sequence[str] | None = None,
    mark: Literal["line", "area", "bar", "scatter"] | None = None,
    title: str | None = None,
    description: str | None = None,
) -> None: ...

def altair_chart(self, chart: object, *, description: str | None = None) -> None: ...
def matplotlib_chart(self, figure: object, *, description: str | None = None) -> None: ...
```

These methods are always importable and type-checkable. They are `experimental` until their native
adapter is promoted. An explicit backend request never silently falls back to a different backend.
Optional-capability behavior is specified below.

## Safe inputs and filter binding

Inputs are rendered safe controls whose resolved values come from the current request's query
parameters or their declared defaults. Every input requires an explicit stable `name`; visible
labels are never identity.

```python
def text_input(
    self,
    label: str,
    *,
    name: str,
    default: str = "",
    placeholder: str | None = None,
    help: str | None = None,
    max_length: int | None = None,
    updates: UpdateTargets | None = None,
    disabled: bool = False,
) -> str: ...

def number_input(
    self,
    label: str,
    *,
    name: str,
    default: int | float = 0,
    minimum: int | float | None = None,
    maximum: int | float | None = None,
    step: int | float = 1,
    updates: UpdateTargets | None = None,
    disabled: bool = False,
) -> int | float: ...

def selectbox(
    self,
    label: str,
    options: Sequence[OptionT],
    *,
    name: str,
    default: OptionT | None = None,
    format_func: Callable[[OptionT], str] = str,
    updates: UpdateTargets | None = None,
    disabled: bool = False,
) -> OptionT: ...

def multiselect(
    self,
    label: str,
    options: Sequence[OptionT],
    *,
    name: str,
    default: Sequence[OptionT] = (),
    format_func: Callable[[OptionT], str] = str,
    updates: UpdateTargets | None = None,
    disabled: bool = False,
) -> tuple[OptionT, ...]: ...

def slider(
    self,
    label: str,
    *,
    name: str,
    minimum: int | float,
    maximum: int | float,
    default: int | float,
    step: int | float = 1,
    updates: UpdateTargets | None = None,
    disabled: bool = False,
) -> int | float: ...

def checkbox(
    self,
    label: str,
    *,
    name: str,
    default: bool = False,
    updates: UpdateTargets | None = None,
    disabled: bool = False,
) -> bool: ...

def date_input(self, label: str, *, name: str, default: date | None = None, updates: UpdateTargets | None = None, disabled: bool = False) -> date | None: ...
```

`options` must be finite and request-serializable through a registered native codec. `format_func`
is presentation only and never parses or authorizes a submitted value. `selectbox` requires at
least one option; `default=None` selects the first canonical option, while an explicit default must
match one canonical option value. Submitted values must also match one canonical option value.

### Coherent filter groups

Inputs that update the same fragment are placed in one generated safe `GET` form. The form submits
every named input required by that fragment, including unchanged controls, so one change cannot
erase another filter. Connected input/target graphs form one group. Ambiguous overlapping groups or
duplicate names fail registration/check rather than generating nested or competing forms.

The default full-page fallback submits the same query values to the owning page. HTMX enhancement
targets only registered fragment hosts. Input values are validated from the fragment method's
annotations and defaults before application code runs. Missing required, extra bound, invalid,
duplicate, or ambiguous values produce a native validation response with Edron source context.

For multiple independent forms, an explicit scope is available:

```python
def filters(
    self,
    *,
    name: str,
    updates: UpdateTargets,
    submit_label: str | None = None,
) -> FilterScope: ...
```

`FilterScope` is a request-local context manager for grouping safe controls; it is not a body or
form container and exposes no output/action methods. `submit_label=None` uses native change-trigger
enhancement plus an ordinary submit control in the no-JavaScript path. Supplying a label makes the
submit control visible in both paths. Filter scopes use `GET` only and cannot contain actions, file
uploads, nested forms, or mutation callbacks.

## `fragment`, `Fragment`, and `BoundFragment`

### Decorator signature

```python
@overload
def fragment(fn: Callable[..., None | Awaitable[None]]) -> Fragment[Any]: ...

@overload
def fragment(
    *,
    name: str | None = None,
    path: str | None = None,
    fallback: str | None = None,
    dependencies: Sequence[Depends | object] = (),
) -> Callable[[Callable[..., None | Awaitable[None]]], Fragment[Any]]: ...
```

The decorated class attribute is an Edron descriptor. Its application registration produces
exactly one native `FragmentHandle`. A generated path is internal and mount-aware; an explicit
`path` is required for external linking. The method is safe and registered as `GET` only.

Calling a bound fragment during `render()` or another allowed output phase binds its application
arguments, mounts the native host, and materializes its initial output exactly once. It returns
`None` because the host is appended to the current container:

```python
self.results(region=region)
```

On a standalone fragment request, Edron creates a fresh page instance and invokes only the addressed
method. Request dependencies run through the native route. A fragment method cannot mutate, return
an output value, access action-only input, or invoke another request endpoint as ordinary Python.

Conceptual descriptor members:

```python
class Fragment(Generic[P]):
    name: str
    signature: Signature
    source: SourceLocation

    def bind(self, **parameters: object) -> BoundFragment[P]: ...

class BoundFragment(Generic[P]):
    fragment: Fragment[P]
    parameters: Mapping[str, object]
```

Access through `self` returns a page-bound view of the descriptor. `.bind(...)` is useful when a
target value is passed without mounting it. `app.native_surface(PageClass.fragment_member)` returns the
exact native `FragmentHandle`; a bound value returns the native bound fragment/reference.

## `action`, `Action`, and `BoundAction`

### Decorator signature

```python
@overload
def action(fn: Callable[..., Outcome | Awaitable[Outcome]]) -> Action[Any, Outcome]: ...

@overload
def action(
    *,
    name: str | None = None,
    path: str | None = None,
    method: Literal["POST", "PUT", "PATCH", "DELETE"] = "POST",
    fallback: str | None = None,
    updates: UpdateTargets | None = None,
    dependencies: Sequence[Depends | object] = (),
    idempotency: Literal["application", "required"] = "application",
) -> Callable[[Callable[..., Outcome | Awaitable[Outcome]]], Action[Any, Outcome]]: ...
```

The decorated attribute produces exactly one native `ActionHandle`. Generated paths are internal;
the default method is `POST`; native CSRF behavior applies to every supported unsafe method. When
`fallback` is omitted, the owning page is the ordinary HTTP fallback. A supplied fallback must be a
safe local URL and must not change the unsafe request into `GET`.

An action is passed as a value:

```python
self.button("Reload", action=self.reload)
self.button("Delete", action=self.delete.bind(customer_id=customer.id))
```

It is never used as `if self.button(...)` and cannot be invoked during render. `.bind(...)` accepts
only named application parameters from the registered action signature. Values are encoded into the
native form/binding plan and remain untrusted client input; binding is not authorization or signing.
Dependency values cannot be bound or shadowed.

`updates=` declares the default native refresh effect after a successful action outcome. It is not
run on validation, authorization, CSRF, conflict, or exception outcomes. A returned explicit
refresh/patch effect must be compatible with the declared native target/effect plan; duplicate
targets are coalesced, while an undeclared or conflicting target fails closed. Omitting `updates=`
does not infer which fragments may have read mutated data.

`idempotency="application"` leaves replay handling to the application/native action policy and
makes no idempotency claim. `idempotency="required"` refuses to run until the native request carries
a valid bounded idempotency key and the application configures a compatible authoritative store or
policy. Edron-rendered controls/forms obtain a server-issued native key automatically, retain it for
retries of that rendered logical submission, and use the same semantics with HTMX or ordinary
forms. A newly rendered logical command receives a new key. Edron never treats a CSRF token as an
idempotency key.

Conceptual descriptor members:

```python
class Action(Generic[P, R]):
    name: str
    signature: Signature
    source: SourceLocation

    def bind(self, **parameters: object) -> BoundAction[P, R]: ...

class BoundAction(Generic[P, R]):
    action: Action[P, R]
    parameters: Mapping[str, object]
```

Only actions declared directly on the registered page class are exposed in 0.1. An ordinary helper
may be inherited; an inherited decorated action/fragment produces a registration diagnostic with a
remediation to redeclare it explicitly.

## Action controls, forms, and outcomes

### Buttons and confirmation

```python
@dataclass(frozen=True, slots=True)
class Confirm:
    message: str
    confirm_label: str = "Confirm"
    cancel_label: str = "Cancel"

def button(
    self,
    label: str,
    *,
    action: Action[Any, Any] | BoundAction[Any, Any] | ActionHandle[Any, Any],
    size: Literal["sm", "md", "lg"] = "md",
    variant: Literal["primary", "secondary", "danger", "quiet"] | None = None,
    recipe: str | StyleRecipe | None = None,
    confirm: str | Confirm | None = None,
    disabled: bool = False,
    width: Literal["content", "field", "full"] = "content",
) -> None: ...
```

`button` appends a native action control and returns `None`. `variant="danger"` is presentation
only. `confirm` requests the native accessible confirmation flow and preserves an unsafe,
CSRF-protected no-JavaScript submission. Confirmation never grants authorization or idempotency.

### Pydantic forms

```python
def form(
    self,
    model: type[ModelT],
    *,
    action: Action[Any, Any] | BoundAction[Any, Any] | ActionHandle[Any, Any],
    name: str | None = None,
    submit_label: str = "Submit",
    controls: Mapping[str, object] | None = None,
    confirm: str | Confirm | None = None,
    clear_on_success: bool = False,
) -> None: ...
```

One Pydantic `BaseModel` is the form boundary. The action must declare exactly one compatible model
parameter; remaining application parameters must already be bound. `controls` may override only
fields in the model with compatible native Hedron controls. Unknown, missing required, duplicate,
or incompatible fields fail registration.

Edron delegates parsing, validation, multipart handling, control generation, error summaries,
safe-value retention, sensitive-value redaction, CSRF, and response compilation to Hedron/Pydantic.
Nested forms are forbidden. `clear_on_success` affects presentation after an authoritative success;
it cannot clear a failed or ambiguous submission.

### Outcomes

`Outcome` is a typing alias for the documented native result union, not an Edron runtime base
class. Native outcome objects may be returned directly.

```python
def refresh(*targets: UpdateTarget) -> RefreshIntent: ...

def success(
    message: str | None = None,
    *,
    status_code: int = 200,
) -> InteractionResult: ...
```

`refresh(...)` resolves Edron descriptors through the active app and returns the native Hedron
`RefreshIntent`. Its `.toast(message)` method is the native method. Duplicate targets are coalesced
in order and native fan-out limits apply.

`success(...)` returns a native `InteractionResult` with an accessible success presentation when a
message is present. The native response compiler preserves equivalent meaning on HTMX and ordinary
HTTP paths; exact toast versus inline placement is presentation, not action success authority.

An action may return a documented native response/result. Arbitrary models, dictionaries, strings,
or Boolean values are not guessed into outcomes. An uncaught exception remains a failure and is
never converted to success.

## Dependencies, caching, and state

### `dependency`

```python
class Dependency(Generic[T]):
    provider: Callable[..., T] | Depends
    use_cache: bool | None

    def __get__(self, instance: Page | None, owner: type[Page]) -> T | Dependency[T]: ...

def dependency(
    provider: Callable[..., T] | Depends,
    *,
    use_cache: bool | None = None,
) -> Dependency[T]: ...
```

A dependency is declared on a page class:

```python
class Customers(ed.Page):
    repository: CustomerRepository = ed.dependency(get_repository)
```

The descriptor compiles to the native request dependency system. A native `Depends` declaration is
accepted by identity so `session_state(...)` and other native dependencies do not need wrappers.
`use_cache=None` preserves the native declaration or native default; an explicit Boolean selects
the normal native per-request behavior. The descriptor does not call the provider at
class definition, registration, static check, or explanation time. `use_cache=True` means native
per-request dependency caching, not process caching. Async providers and generator cleanup follow
native FastAPI/Hedron lifetime rules. Test overrides use `app.hedron.dependency_overrides` or a
documented Edron delegation to that same mapping.

Access on the class returns the descriptor. Access on an active page instance returns the resolved
request value. Access without an active request raises `PhaseError`. Dependency names are reserved
from query/form/action binding and cannot be client-shadowed.

### `cache_data`

```python
class CachedFunction(Protocol[P, R]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def invalidate(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def invalidate_all(self) -> None: ...

def cache_data(
    *,
    ttl: int | float | None = None,
    scope: Literal["request", "private", "tenant", "public"] = "private",
    max_entries: int = 128,
) -> Callable[[Callable[P, R]], CachedFunction[P, R]]: ...
```

This decorator is for deterministic/recomputable data. It lowers to the native bounded cache and
retains the wrapped signature. `public` requires an application review that arguments and results
are safe across users/tenants. `tenant` requires an authoritative native tenant key. Secrets and
unbounded request objects are rejected cache keys. `cache_data` is not a connection/resource
manager, database, session, transaction, or job store.

### State ownership

Edron 0.1 has no `session_state`, magic persistent page fields, or `cache_resource`:

| Need | Public 0.1 owner |
|---|---|
| Shareable safe filter | Named query input / filter scope |
| One submission | Pydantic form model |
| Request dependency/resource | `ed.dependency(...)` |
| Recomputable cached data | `ed.cache_data(...)` |
| Typed user session | Native Hedron session contract through a dependency |
| Durable/domain state | Application service/database through a dependency |
| Browser presentation preference | Native Hedron preference component/contract |

This explicit table is part of the compatibility contract. Edron will not later reinterpret page
attributes as persistent state without a new accepted RFC and migration path.

## Styling

### Theme constructor

```python
def theme(
    name: str,
    *,
    accent: str | Color,
    base: str | Theme = "default",
    density: Literal["compact", "comfortable", "spacious"] = "comfortable",
    geometry: Literal["square", "soft", "rounded"] = "soft",
    typography: Literal["system-sans", "system-serif", "system-mono"] = "system-sans",
    elevation: Literal["flat", "subtle", "layered"] = "subtle",
    motion: Literal["standard", "calm", "none"] = "standard",
    navigation: Literal["compact", "default", "wide"] = "default",
) -> DesignSystem: ...
```

`ed.theme(...)` resolves a string base through the native theme registry and calls the native brand
compiler. It always returns `hedron.DesignSystem`. It performs no I/O and creates no Edron theme
registry. Advanced authors may pass native `Theme`, `ThemeSpec`, or `DesignSystem` directly to
`App`, construct native themes/builders, and use native packages/preferences.

### Variants and recipes

The 0.1 finite variant mapping is:

| Family | Edron variant | Native recipe/intent |
|---|---|---|
| action | `primary` | `primary_action` |
| action | `secondary` | `secondary_action` |
| action | `danger` | `destructive_action` |
| action | `quiet` | native ghost/neutral control recipe frozen by registry metadata |
| surface | `plain` | native baseline surface recipe |
| surface | `outlined` | native outlined surface recipe |
| surface | `raised` | `dashboard_panel` |
| data | `compact` | `dense_data` |

The actual mapping is registered once in Hedron metadata and projected by Edron; Edron may not keep
a divergent hard-coded registry. `variant` and `recipe` are mutually exclusive. Explicit native
appearance props override recipe defaults under Hedron precedence. A danger variant never changes
action method, authorization, confirmation, or destructive meaning.

`self.style_scope(...)` lowers to native `StyleScope` and, when `context` is supplied, requires a
native `StyleContext`. No mapping/dictionary is guessed into a context in 0.1.

### Local CSS and precedence

`app.styles(...)` is the full-power path and delegates to native application stylesheet
registration. Edron accepts no `style={...}` component dictionary, arbitrary inline CSS string,
request-derived token, or utility-class DSL.

Edron inherits native precedence. The beginner explanation presents:

1. explicit component presentation prop;
2. explicit recipe or variant;
3. nearest explicit style scope/context;
4. application `DesignSystem`;
5. resolved native theme; and
6. first-party baseline.

Registered CSS participates through the native cascade layer order and public hook manifest; it is
not forced into the Python-side order. Styling cannot change semantics, DOM/focus order,
authorization, routes, effects, or state authority.

## Optional dependency capabilities

Optional methods are defined regardless of installed packages. Activation depends only on the
actual compatible distribution/import, never on whether an Edron extra name was used.

The initial shortcut registry is:

| Capability | Direct dependencies | Equivalent shortcut | Maturity |
|---|---|---|---|
| pandas input | `pandas>=2.0` and `narwhals>=1.1` | `edron[pandas]` | beta data adapter |
| Polars input | `polars>=1.0` and `narwhals>=1.1` | `edron[polars]` | beta data adapter |
| PyArrow input | `pyarrow>=15.0` and `narwhals>=1.1` | `edron[pyarrow]` | beta data adapter |
| Plotly | `plotly>=5.18,<7` | `edron[plotly]` | experimental |
| Altair | `altair>=6,<7` and `vl-convert-python>=1.0` | `edron[altair]` | experimental |
| Matplotlib | `matplotlib>=3.8,<4` | `edron[matplotlib]` | beta/static Supported scope |
| SQLAlchemy source | `sqlalchemy>=2,<3` | `edron[sqlalchemy]` | beta data source |

The final package ranges must equal the compatible owning-package adapter ranges at release. If an
upstream range changes before Edron 0.1, both the direct command and shortcut metadata change
together in the acceptance packet.

There is no `edron[all]`. Installing a shortcut may install several required distributions, but it
cannot activate another code path. Edron never invokes an installer.

### Capability errors

```python
class CapabilityError(EdronError):
    capability: str
    distributions: tuple[str, ...]
    direct_command: str
    shortcut_command: str
    call_site: SourceLocation | None

class MissingCapabilityError(CapabilityError): ...
class IncompatibleCapabilityError(CapabilityError):
    installed_versions: Mapping[str, str]

class BrokenCapabilityError(CapabilityError):
    cause: BaseException
```

Missing means distribution metadata is absent. Incompatible means it is present but outside the
accepted range. Broken means compatible metadata is present but import or adapter initialization
fails. Broad `ImportError` handling must not misclassify an internal dependency failure as absent.
Messages include exact quoted `pip` and `uv add` direct/shortcut commands plus an offline docs link.

## `JobFlow`

`JobFlow` is beta and release-blocked until its required native `TaskFlow` enablement passes. The
public shape is nevertheless frozen so the golden application does not depend on an Edron-owned
queue or worker.

```python
class JobFlow(Generic[InputT, ResultT]):
    def __init__(
        self,
        *,
        name: str,
        input_model: type[InputT],
        job_type: str,
        payload: Callable[[InputT], Mapping[str, JsonValue]],
        backend: Dependency[JobBackend] | JobBackend,
        scope: Callable[..., JobScope] | Dependency[JobScope],
        result: Callable[[Page, ResultT], None | Awaitable[None]],
        authorize_submit: Depends | object | None = None,
        authorize_cancel: Depends | object | None = None,
        poll_interval_ms: int = 2000,
    ) -> None: ...
```

`App.include(flow)` lowers one flow to one native Hedron `TaskFlow`/`FeatureBundle` with typed submit,
status, cancel (when configured), and result surfaces. `Page.job(...)` mounts it:

```python
def job(
    self,
    flow: JobFlow[Any, Any],
    *,
    submit_label: str = "Submit",
    show_cancel: bool = False,
) -> None: ...
```

The application supplies the backend, job type handled by its worker, authoritative scope, payload
conversion, and result renderer. Edron supplies no production worker or scheduler. An in-memory
development backend, if shipped, is a separate explicitly named testing/development object and is
rejected by the production gate.

Submission and cancellation are unsafe and CSRF protected. Submit, status, cancel, and result use
the same authoritative `JobScope`. Unknown or cross-scope job IDs return the native fail-closed
response. Polling is the Supported default and stops on every terminal/expired/unrecoverable state.
SSE/WebSocket observation remains experimental and is not part of `JobFlow` 0.1.

## Download controls

```python
@dataclass(frozen=True, slots=True)
class Download:
    identifier: str

def download(identifier: str) -> Download: ...

def download_button(
    self,
    value: bytes | Download,
    *,
    label: str,
    filename: str | None = None,
    media_type: str | None = None,
) -> None: ...
```

Bytes require an explicit safe filename and media type. `ed.download(identifier)` creates an opaque
reference resolved only through a registered authorized download provider; the identifier is never
opened as a local filesystem path. Constructing the reference does not authorize access. Native
`FileResponse` or download handles may be composed through documented Hedron routes. Filenames,
headers, ranges, size limits, authorization, and content disposition remain native policy.

## Native Hedron interoperability

Every Edron registration has one native authority:

| Edron surface | Exact native projection |
|---|---|
| Page class | one `ScreenHandle`/page route |
| `Fragment` | one `FragmentHandle` |
| `BoundFragment` | native bound fragment/reference |
| `Action` | one `ActionHandle` |
| `BoundAction` | native structural binding for that action |
| `Outcome` | native result object; no Edron response runtime |
| `ed.theme(...)` | native `DesignSystem` |
| `ed.StyleRecipe` / `Color` | identity re-export |
| `style_scope` | native `StyleScope`/`StyleContext` |
| `app.styles` | native `ApplicationStyleMeta` and asset graph |
| `JobFlow` | native `TaskFlow`/`FeatureBundle` |

`app.native_surface(surface)` returns the exact registered native projection, not a proxy. Page, fragment,
action, and bound surfaces return the handle/reference used for reverse routing, rendering,
target/effect validation, the interaction catalog, Explorer, tests, and explanation. An Edron
`JobFlow` returns the exact included `FeatureBundle` used by the native catalog. A surface from
another app, stale registration, or incompatible Hedron train fails rather than being cloned.

Native Hedron objects work in Edron positions where their public protocol matches:

- `self.include(...)` accepts native body renderables;
- `action=` accepts native `ActionHandle`;
- `updates=` and `ed.refresh(...)` accept native `FragmentHandle`, bound fragments, and compatible
  registered `ComponentRef` targets;
- native registered styles/themes/policies affect Edron-generated components; and
- `app.hedron` accepts native pages, middleware, dependencies, routers, features, tests, and ASGI
  integration alongside Edron registrations.

Edron does not catch and relabel every native `HED-*` failure. A native contract error retains its
code, type, source/cause chain, and native remediation; Edron adds source context when safe.

## Required upstream Hedron contracts

The following Edron signatures are frozen requirements but cannot be implemented as private
Edron-only mechanics. Before the corresponding Edron surface ships, Hedron must either identify an
existing public authority or add the reusable native contract and its own acceptance evidence.

| ID | Edron surface | Required native authority |
|---|---|---|
| `UP-001` | Page member → native handle compilation | Fresh-instance class compiler supporting owning class, inspected signature, async, and exact handles |
| `UP-002` | Coherent query controls | Bounded typed GET filter plan spanning several controls and one/more refreshable handles |
| `UP-003` | `ed.dependency` | Public request dependency descriptor with cleanup, override, static explanation, and client-shadow protection |
| `UP-004` | Default action fallback | Safe owning-screen fallback derivation that preserves unsafe method, CSRF, validation, and redirect policy |
| `UP-005` | `confirm=` | Accessible native confirmation with keyboard, focus, cancellation, unsafe no-JS submission, and no behavior authority from styling |
| `UP-006` | `ed.success` ordinary fallback | Native outcome presentation with equivalent HTMX and ordinary HTTP meaning without unsafe query leakage |
| `UP-007` | `app.native_surface(surface)` | Stable registry lookup from facade source surface/binding to the exact native handle/reference |
| `UP-008` | `JobFlow` | `TaskFlow` support for explicit backend dependency, common scope, Edron result-output adapter, terminal polling, and production gate |
| `UP-009` | `variant=` | Registry-derived family/recipe alias metadata and explanation; no Edron-only recipe registry |
| `UP-010` | Cross-package `ed.theme(...)` guarantee | Shared core/data/charts/maps token, mode, accessibility, and asset contract |
| `UP-011` | Style/registry explanation | Native reports accepting facade source provenance without a second schema |

If a row cannot be satisfied cleanly, that Edron surface is deferred. The implementation must not
approximate it with hidden endpoints, a parallel registry, process globals, browser-only behavior,
or a weaker security/accessibility contract.

## CLI contract

```text
edron run APP [--host HOST] [--port PORT] [--reload]
edron check APP [--register] [--format text|json|sarif] [--fail-on warning|error]
edron explain APP [--format text|json]
edron doctor [APP] [--format text|json]
edron style check APP [--format text|json|sarif]
edron style preview APP --output PATH
edron style explain APP [--format text|json]
edron style diff BASE CANDIDATE [--format text|json]
```

`APP` accepts a Python file containing `app`, or `module:attribute`. `run` and commands requiring a
sealed native registry import trusted application code. Plain `check` statically analyzes source
without importing it; `--register` clearly opts into trusted import/registration checks. Static
checks never call page renderers, fragments, actions, dependency providers, job backends, data
loaders, or network services.

Exit status is `0` for successful operation below the configured finding threshold, `1` for tool,
import, registration, or output failure, and `2` when a report is produced but findings meet the
configured threshold. JSON/SARIF schemas project native diagnostics and include Edron source maps;
they do not become competing diagnostic authorities.

`doctor` inventories compatible required packages and curated optional capabilities as
`available`, `missing`, `incompatible`, or `broken`. It never installs or upgrades anything.
`style preview` uses fixed synthetic content and never executes application callbacks or data.

## Errors and diagnostics

Edron exceptions expose a structured diagnostic with at least `code`, `title`, `explanation`,
`remediation`, `source`, and optional `native_diagnostic`. Sensitive values and absolute paths are
redacted under native policy.

```python
@dataclass(frozen=True, slots=True)
class SourceLocation:
    path: str
    start_line: int
    start_column: int = 1
    end_line: int | None = None
    end_column: int | None = None
    qualname: str | None = None

@dataclass(frozen=True, slots=True)
class EdronDiagnostic:
    code: str
    severity: Literal["error", "warning", "information"]
    title: str
    explanation: str
    remediation: str = ""
    source: SourceLocation | None = None
    native_diagnostic: HedronDiagnostic | None = None
    context: Mapping[str, JsonValue] = field(default_factory=dict)
    docs_url: str | None = None

class EdronError(Exception):
    diagnostic: EdronDiagnostic

class RegistrationError(EdronError): ...
class PhaseError(EdronError): ...
class BindingError(EdronError): ...
```

`EdronDiagnostic` and `SourceLocation` are public read-only records in `edron.diagnostics`, but are
not beginner root re-exports. Source positions are 1-based; absent end positions mean the start
position. Context is bounded/redacted JSON-compatible data, and a retained native diagnostic keeps
its original `HED-*` identity. JSON/SARIF projections follow the shared Hedron diagnostic schema
and unknown-field/version rules. Catch the semantic exception classes in application tools; do not
branch on rendered message text.

### Stable Edron diagnostic codes

| Code | Exception | Situation |
|---|---|---|
| `EDR-APP-0001` | `RegistrationError` | Invalid/incompatible app construction or wrapping |
| `EDR-APP-0002` | `RegistrationError` | Registration after native registry/schema seal |
| `EDR-APP-0003` | `RegistrationError` | Duplicate route/name/logical identity or native collision |
| `EDR-PAGE-0001` | `RegistrationError` | Target is not a valid direct `Page` subclass |
| `EDR-PAGE-0002` | `RegistrationError` | Instance/custom constructor/inherited exposed method rejected |
| `EDR-PAGE-0003` | `RegistrationError` | Missing `render` or conflicting page metadata |
| `EDR-PHASE-0001` | `PhaseError` | Output/dependency access without active request phase |
| `EDR-PHASE-0002` | `PhaseError` | Action invocation during page/fragment render |
| `EDR-PHASE-0003` | `PhaseError` | Non-`None` return from `render`/fragment |
| `EDR-PHASE-0004` | `PhaseError` | Output emission during action/registration |
| `EDR-BIND-0001` | `BindingError` | Duplicate control/filter/binding name |
| `EDR-BIND-0002` | `BindingError` | Missing required or unexpected bound parameter |
| `EDR-BIND-0003` | `BindingError` | Invalid typed/serialized bound value |
| `EDR-BIND-0004` | `BindingError` | Ambiguous/overlapping filter group |
| `EDR-BIND-0005` | `BindingError` | Cross-app, stale, or unauthorized target reference |
| `EDR-FORM-0001` | `RegistrationError` | Missing/ambiguous Pydantic action boundary |
| `EDR-FORM-0002` | `RegistrationError` | Unsupported/incompatible field control |
| `EDR-FORM-0003` | `PhaseError` | Nested/mixed safe and unsafe form boundary |
| `EDR-DEP-0001` | `RegistrationError` | Invalid dependency descriptor/provider |
| `EDR-DEP-0002` | `BindingError` | Client/bound value attempts to shadow dependency |
| `EDR-DEP-0003` | `EdronError` | Dependency resolution/lifetime failure with native cause |
| `EDR-CAP-0001` | `MissingCapabilityError` | Required optional distribution absent |
| `EDR-CAP-0002` | `IncompatibleCapabilityError` | Installed optional distribution outside range |
| `EDR-CAP-0003` | `BrokenCapabilityError` | Compatible distribution cannot import/initialize |
| `EDR-LOWER-0001` | `EdronError` | Value cannot lower to a documented native body/outcome |
| `EDR-LOWER-0002` | `EdronError` | Output/container/target/plan resource limit exceeded |
| `EDR-NATIVE-0001` | `EdronError` | Incompatible native object/protocol/version |
| `EDR-NATIVE-0002` | `EdronError` | Full document/response used in body position |
| `EDR-STYLE-0001` | `RegistrationError` | Unknown/conflicting variant, recipe, or family |
| `EDR-STYLE-0002` | `RegistrationError` | Invalid Edron theme input before native validation |
| `EDR-STYLE-0003` | `PhaseError` | Invalid/stale style scope or context |
| `EDR-JOB-0001` | `RegistrationError` | Invalid flow/backend/scope/result composition |
| `EDR-JOB-0002` | `EdronError` | Backend unavailable or production backend gate failure |
| `EDR-JOB-0003` | `BindingError` | Job operation identity/scope mismatch |

Codes identify Edron's boundary. Native request validation, CSRF, authorization, target policy,
style compiler, assets, components, jobs, and response conversion continue to use their documented
`HED-*` codes and HTTP statuses.

### HTTP behavior

| Failure | Default HTTP behavior |
|---|---|
| Invalid safe query/fragment input | native `422` page/fragment validation response |
| Invalid form input | native `422` semantic form response; application action not invoked |
| Missing/invalid CSRF | native fail-closed CSRF status/policy |
| Authorization denial | application/native dependency status, normally `401` or `403` |
| Target disagreement/cross-app target | native fail-closed target status, normally `403` |
| Unknown scoped job | `404` without existence disclosure |
| Non-terminal/conflicting job result | native `409` or status contract |
| Missing optional dependency during request | application error response with redacted capability ID; install commands appear only in development/authorized diagnostics |
| Unhandled application exception | native server error policy; never an Edron success outcome |

## Security, accessibility, and resource invariants

- Safe filters/fragments use `GET`; mutations use unsafe methods and native CSRF.
- Generated paths, bindings, labels, confirmation, variant, page visibility, and HTMX headers are
  not authorization.
- No user/request value becomes code, HTML trust, CSS, route policy, dependency, asset URL, local
  path, or native object identity.
- Output plans, inputs, options, bound values, targets, forms, rows, chart points, map geometry,
  uploads/downloads, job payload/status, cache entries, styles, and diagnostics have native or Edron
  finite limits frozen in acceptance evidence.
- Default and generated pages retain semantic landmarks, labels, keyboard behavior, focus/error
  handling, live-region discipline, reflow/zoom, RTL, print, reduced motion, forced colors, and
  no-JavaScript operation required by their native maturity claim.
- A visual chart/map requires an accessible description or data alternative for Supported claims.
- Output is discarded on an author-method exception before a partial page/fragment is emitted.
  Application mutations are not rolled back by the output buffer; transaction boundaries remain
  application-owned.

## Historical 0.1 exclusions and deferrals

The following names/semantics are not public Edron 0.1 API:

- `write`, a generic magic display dispatcher, or `unsafe_allow_html`;
- `import edron as st` compatibility claims;
- Boolean-returning buttons or mutation under `if button`;
- module-global output, persistent page instances, whole-script reruns, hooks, signals, or a global
  session dictionary;
- custom `Page.__init__` or constructor dependency injection;
- implicit exposure of inherited decorated methods;
- arbitrary callback positional/keyword argument bags instead of `.bind(...)`;
- arbitrary per-call CSS dictionaries, inline CSS, utility-class generation, or runtime style
  injection;
- editable dataframes without an explicit schema/action contract;
- automatic third-party fallback, `edron[all]`, or runtime installation;
- a production job worker, scheduler, database, ORM, authentication provider, deployment platform,
  or live SSE/WebSocket requirement; and
- Flask/Django parity claims for the Edron page-class facade.

Adding one of these requires an accepted compatibility decision and migration analysis; it cannot
arrive as an undocumented convenience.

## Returns summary

| API kind | Return |
|---|---|
| Display/output method | `None` after appending to current native plan |
| Safe input | Validated typed Python value for current request |
| Container/layout method | Request-local `Container` |
| `filters(...)` | Request-local safe-control `FilterScope` |
| `@app.page` | Original page class unchanged |
| `@ed.fragment` / `@ed.action` | Public Edron descriptor |
| Fragment call in output phase | `None` after native host mount/materialization |
| `.bind(...)` | Immutable bound descriptor value |
| `ed.refresh(...)` | Native `RefreshIntent` |
| `ed.success(...)` | Native `InteractionResult` |
| `ed.theme(...)` | Native `DesignSystem` |
| `app.styles(...)` | Native `ApplicationStyleMeta` |
| `app.native_surface(...)` | Exact native registered handle, bound reference, or `FeatureBundle` projection |
| `App.include(...)` | `None` |

## See also

- [RFC-0094: Edron authoring facade](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)
- [Edron golden applications](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_GOLDEN_APPS.md)
- [Edron state and interaction](EDRON_STATE_INTERACTION.md)
- [Edron packaging](EDRON_PACKAGING.md)
- [Edron capability inventories](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_CAPABILITY_INVENTORIES.md)
- [Edron implementation specification](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_001.md)
- [Edron acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_001.md)
- [Refreshable views and commands](REFRESHABLE_VIEWS.md)
- [Type-driven authoring](TYPE_DRIVEN_AUTHORING.md)
- [Application styling](APPLICATION_STYLING_065.md)
- [Themes](THEME.md)
- [Jobs](JOBS.md)
- [State](STATE.md)
- [Security types](SECURITY_TYPES.md)
- [Accessibility](A11Y.md)
- [Public stability](STABILITY.md)
