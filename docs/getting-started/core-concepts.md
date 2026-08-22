# Core concepts

Hedron adds a typed interface layer to FastAPI without replacing its application model or
hiding the web platform. Five concepts explain most of the framework.

## Application

`Hedron` is the flagship FastAPI application. It owns security policy, component and
route registration, static assets, and optional Explorer mounting.

```python
from hedron import Hedron

app = Hedron(
    title="Operations",
    security="standard",
    session_secret="replace-in-production",
)
```

Use normal FastAPI middleware, dependencies, JSON endpoints, and lifespan behavior beside
Hedron page, component, and action routes.

## Components

A component is a typed, reusable description of UI. Components return node-like values;
only the top-level renderer produces HTML.

```python
from hedron import Card, Component, Props, Text
from hedron_core import NodeLike


class UserCardProps(Props):
    name: str


class UserCard(Component[UserCardProps]):
    def render(self) -> NodeLike:
        return Card(Text(self.props.name))
```

Text is escaped by default, attributes are normalized, and props stay immutable during
rendering. Components perform no hidden I/O, which makes composition deterministic and
unit tests fast.

## Pages and routes

`@app.screen` declares a navigable HTML route for new golden paths. It returns page
content (for example a `Stack`); Hedron wraps it as a document. Day-to-day fragment
updates use `@app.refreshable` (what `hedron new` generates).

!!! note "Advanced — explicit `@app.page`"

    `@app.screen` lowers to `Page` + `@app.page`. Keep `@app.page` when you need full
    `Page` constructor control. The explicit `app.region` / `@app.fragment` API remains
    for custom allowlists — [Which interaction API?](interaction-apis.md).

That separation matters: rendering a component never silently makes it reachable over
HTTP, and reachability never grants authorization.

## Render modes

Hedron renders the same component tree in a mode appropriate to the request:

| Mode | Intended response |
|---|---|
| `PAGE` | Complete HTML document for navigation or history restoration |
| `FRAGMENT` | Targeted content for an HTMX request |
| `EMBED` | Framework-neutral content embedded by another host |

The renderer returns a `RenderResult` containing HTML plus structured metadata such as
assets and diagnostics. User components do not concatenate response strings themselves.

### Try it (simulated)

=== "Demo"

    Toggle the response shape — docs simulation only.

    <!-- hedron-sim:core-concepts-modes -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    from hedron import Page, RenderMode, html, render

    # PAGE: full HTML document for navigation / history restoration.
    page = Page(html.div("All systems operational", id="service-status"), title="Status")
    page_result = render(page, mode=RenderMode.PAGE)

    # FRAGMENT: targeted content for an HTMX request.
    fragment = html.div(
        "All systems operational · refreshed 12:00:00 UTC",
        id="service-status",
        role="status",
    )
    fragment_result = render(fragment, mode=RenderMode.FRAGMENT)

    assert "<html" in page_result.html.lower()
    assert "<html" not in fragment_result.html.lower()
    ```

## Interaction and security

HTMX owns request-and-swap interaction. Hedron validates targets, normalizes response
headers, and applies CSRF policy to unsafe cookie-authenticated requests. Durable
browser-local behavior belongs in standards-based Web Components rather than a hidden
client runtime.

Handlers may return `InteractionResult` for typed primary content, OOB updates, history,
and cache/`Vary` hints instead of assembling `HX-*` headers by hand. See
[Responses](../api/RESPONSES.md) and [Charts and HTMX](../guides/charts-and-htmx.md).

Use `SafeUrl`, `TrustedHtml` (including `TrustedHtml.nh3`), and `Secret` only at deliberate
trust boundaries. Plain text remains escaped, redirects use explicit local or external
policies, and authenticated fragments receive conservative cache behavior.

## The build boundary

Development can discover component folders, scoped CSS, and assets. A production build fingerprints
those artifacts and seals the registry. Production does not silently compile mutable source at
request time. Typed Python remains the canonical component model. Optional HDJ (`.hdj`) templates
via `hedron[jinja]` are available when you need native HTML/Jinja plus typed Hedron bridges — see
[HDJ authoring](../guides/hdj-authoring.md).

The [project workflow](../guides/project-workflow.md) shows the CLI commands for this
lifecycle. For precise guarantees, use the [public API contracts](../api/README.md).
