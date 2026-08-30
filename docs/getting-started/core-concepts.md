# Core concepts

Hedron adds an explicit interface layer to FastAPI without replacing its application model or
hiding the web platform. Five concepts explain most of the framework.

## You will learn

By the end of this page, you should be able to explain:

- where application configuration and routes live;
- how components become HTML without hidden I/O;
- why a page response and a fragment response are different;
- how HTMX requests map to declared regions;
- where security, assets, and production compilation fit in the boundary.

If you have not run an app yet, complete the [quickstart](quickstart.md) first. The
examples below are easier to understand after you have clicked **Refresh status** once.

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

A component is a reusable description of UI. Components return node-like values;
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

`@app.page` declares a navigable HTML route. It returns one presentation tree (for
example a `Stack` or `Page`) and owns the document response. Day-to-day replaceable
fragment updates use `@app.view` (what `hedron new` generates).

!!! note "Advanced — explicit region control"

    `@app.page` and `@app.view` are the canonical function roles. Use the explicit
    `app.region` / `@app.view` API only for a custom allowlist or another distinct
    lower-level boundary — [Which interaction API?](interaction-apis.md).

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
application state remains on the server; Alpine owns disposable browser-local behavior,
and specialist browser subsystems use bounded Web Components. See
[What is Alpine?](what-is-alpine.md) for the local/server decision rule.

Handlers may return `InteractionResult` for validated primary content, OOB updates, history,
and cache/`Vary` hints instead of assembling `HX-*` headers by hand. See
[Responses](../api/RESPONSES.md) and [Charts and HTMX](../guides/charts-and-htmx.md).

Use `SafeUrl`, `TrustedHtml` (including `TrustedHtml.nh3`), and `Secret` only at deliberate
trust boundaries. Plain text remains escaped, redirects use explicit local or external
policies, and authenticated fragments receive conservative cache behavior.

### Remember this loop

Most Hedron interactions can be read as one inspectable loop:

```text
Python intent → declared route → HTML page or fragment → browser request → declared target
```

If you are unsure which API to choose, start with [API by task](../api/by-task.md) and
return here when you need the underlying model.

## The build boundary

Development can discover component folders, scoped CSS, and assets. A production build fingerprints
those artifacts and seals the registry. Production does not silently compile mutable source at
request time. Python components remain the canonical model. Optional HDJ (`.hdj`) templates
via `hedron[jinja]` are available when you need native HTML/Jinja plus Hedron bridges — see
[HDJ authoring](../guides/hdj-authoring.md).

The [project workflow](../guides/project-workflow.md) shows the CLI commands for this
lifecycle. For precise guarantees, use the [public API contracts](../api/README.md).
