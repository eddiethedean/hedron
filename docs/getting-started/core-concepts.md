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

`@app.page` declares a navigable HTML route. A `Page` carries document metadata and page
content. App-local fragments use explicit component routes, while reusable packages can
declare addressable components that an application must opt into.

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
request time. Typed Python remains the canonical component model; phase 0.9 also provides the
separate optional `hedron-jinja` adapter for trusted application templates. HDN has been removed.

The [project workflow](../guides/project-workflow.md) shows the CLI commands for this
lifecycle. For precise guarantees, use the [public API contracts](../api/README.md).
