---
description: Machine-oriented instructions for coding agents building and troubleshooting Hedron applications.
search:
  boost: 2
---

# Hedron field guide for coding agents

!!! info "Human readers"

    This page is designed to be given directly to a coding agent. It is intentionally dense,
    explicit, repetitive at important boundaries, and organized for retrieval rather than
    narrative reading. For a human learning path, start with
    [Build your first app](quickstart.md).

## Agent objective

Build and modify Hedron applications using the stable public 1.0 API. Preserve ordinary web
semantics, FastAPI behavior, accessibility, security, and production constraints. Do not invent
Hedron symbols or infer behavior from a similarly named React, template, or Python UI API.

Target the published `hedron>=1.0.0,<1.1` train unless the project lockfile says otherwise.
Inspect the installed version before changing an existing application:

```bash
python -c "import hedron; print(hedron.__version__)"
```

This guide's canonical host is `Hedron`, the FastAPI-native application. If the project uses
`HedronFlask`, `HedronDjango`, or Edron, stop and use that host's documentation; do not paste
FastAPI decorators into an adapter application.

## Operating rules

Apply these rules in order:

1. Read `pyproject.toml`, the application constructor, and existing route/component patterns.
2. Preserve the existing host, security profile, session configuration, theme, and dependency
   injection model.
3. Prefer exports documented under `from hedron import ...`. Use `hedron_core` only when a
   referenced public contract explicitly places a type there, such as `NodeLike`.
4. Use `@app.page` for navigable documents, `@app.view` for safe replaceable reads, and
   `@app.action` for mutations.
5. Compose components; do not call child `.render()`, concatenate HTML, or convert a child to a
   string.
6. Use a view handle's `path`, `dom_id`, and built-in controls. Do not guess an HTMX target.
7. Keep durable state in application-owned storage. Rendering must not perform hidden writes.
8. Use built-in presentation props and components before adding CSS. Never create a React/Vite
   project merely to style a Hedron app.
9. Keep FastAPI dependencies, middleware, lifespan, response models, and JSON routes when they
   already solve the problem.
10. Run focused tests, `hedron check`, and the production build before declaring completion.

## Translate from HTML, CSS, and React

Hedron produces normal HTML and CSS, but its component tree is evaluated on the Python server.
HTMX performs bounded HTTP requests and DOM swaps. Alpine is used for disposable browser-local
presentation state. There is no React runtime, virtual DOM, hydration pass, or general-purpose
client state store.

| Familiar concept | Hedron equivalent | Important difference |
|---|---|---|
| HTML document route | `@app.page("/path")` | The handler returns a component tree; Hedron renders the document. |
| HTML element | `html.div(...)`, `html.button(...)` | Attributes are Python arguments and values are validated/escaped. |
| JSX component | `Component[Props]` or a function returning components | Rendering occurs on the server and must be pure. |
| `children` | Positional component arguments or `children=` | Pass nodes, not rendered HTML strings. |
| React Router page | FastAPI/Hedron route | HTTP is the source of truth; normal middleware and dependencies apply. |
| Server component/read | `@app.view` | Returns a targeted HTML fragment handle for HTMX. |
| Mutation/action | `@app.action` | Unsafe methods are subject to authentication, authorization, validation, and CSRF. |
| `fetch()` then `setState()` | HTMX request and swap | Prefer a generated view/action handle over handwritten request wiring. |
| `useState` for open/selected state | Built-in local component behavior or Alpine | Use only for disposable presentation state, never authoritative business state. |
| Database/query state | Application service called by a route | Keep it server-owned; do not store it in Alpine or the DOM. |
| CSS flex column | `Stack` | Use validated `gap`, alignment, density, and responsive props. |
| CSS flex row | `Inline` | Preserve source and focus order when wrapping. |
| CSS grid/media query | `Grid(columns={"base": 1, "md": 3})` | Responsive maps are mobile-first and use finite breakpoints. |
| CSS module | Component-local `styles.css` and style symbols | Hedron scopes/fingerprints CSS during its build. |
| `className` | `class_` | Built-in classes remain; an application class is an extension hook. |
| `aria-*` / `data-*` | `aria={...}` / `data={...}` | Prefer semantic components that already own the relationship. |
| `dangerouslySetInnerHTML` | `TrustedHtml` at a reviewed trust boundary | Plain strings are escaped. Never wrap untrusted input to silence validation. |
| React effect | FastAPI lifespan, middleware, route, job, or explicit browser behavior | Never start I/O or mutate durable state from `render()`. |

### Equivalent tree construction

HTML/JSX:

```html
<main>
  <h1>Deployments</h1>
  <section aria-label="Current status">
    <p>All systems operational</p>
    <button type="button">Refresh</button>
  </section>
</main>
```

Hedron:

```python
from hedron import Card, Heading, Main, Stack, Text

content = Main(
    Stack(
        Heading("Deployments", level=1),
        Card(
            Text("All systems operational"),
            title="Current status",
        ),
    )
)
```

Add the refresh button only after declaring the server view it calls; unlike an inert JSX
`onClick` placeholder, the interaction must have an HTTP owner.

## Core runtime model

### `Hedron` is still FastAPI

`Hedron` subclasses FastAPI. Use normal FastAPI features beside Hedron pages:

```python
import os

from fastapi import Depends

from hedron import Hedron, Text

app = Hedron(
    title="Operations",
    security="standard",
    explorer="off",
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET",
        "replace-in-production",
    ),
)


def current_user() -> str:
    return "ada"  # Replace with an application-owned authentication dependency.


@app.get("/api/health")
def api_health() -> dict[str, str]:
    return {"status": "ok"}


@app.page("/account")
def account(user: str = Depends(current_user)):
    return Text(f"Signed in as {user}")
```

Do not create a second FastAPI app to add JSON routes. Do not bypass existing dependencies when
adding a page or action.

### Components describe output; the renderer emits output

A component is closer to a pure React function component than to a mutable widget object:

```python
from hedron import Card, Component, Props, Text
from hedron_core import NodeLike


class UserCardProps(Props):
    name: str
    role: str


class UserCard(Component[UserCardProps]):
    props_type = UserCardProps

    def __init__(self, *, name: str, role: str) -> None:
        super().__init__(UserCardProps(name=name, role=role))

    def render(self) -> NodeLike:
        return Card(Text(self.props.role), title=self.props.name)
```

Requirements:

- Declare `props_type` on concrete components.
- Treat props as immutable.
- Return `NodeLike`; do not return a `Response` from `Component.render()`.
- Do not query a database, call a remote service, write state, or enqueue work in `render()`.
- Pass `UserCard(...)` into a parent. Never pass `UserCard(...).render()`.
- Let the top-level request renderer handle escaping, assets, diagnostics, and identity.

## Choose the interaction owner

Use this decision sequence:

```text
Is it a navigable document?
  yes -> @app.page
  no  -> Does it change server or durable state?
           yes -> @app.action
           no  -> Does it fetch/recompute replaceable server content?
                    yes -> @app.view
                    no  -> Is it disposable local presentation state?
                             yes -> built-in local behavior or Alpine
                             no  -> ordinary component composition
```

Examples of server state: database records, permissions, jobs, carts, workflow state, user
preferences, data shared across tabs/users, and anything that must survive navigation.

Examples of local presentation state: whether a disclosure is open, the selected tab before it
affects server data, temporary menu visibility, and transient focus behavior. Prefer built-ins such
as `Tabs`, `Expander`, `Dialog`, `Popover`, and `ColorModeToggle`; they already carry accessibility
and progressive-enhancement behavior.

## Canonical complete application

This is a copy-safe baseline containing a full page, replaceable GET view, classic POST action,
CSRF field, built-in styling, and ordinary FastAPI form parsing:

```python title="app.py"
import os
from datetime import datetime, timezone

from fastapi import Form as FastAPIForm

from hedron import (
    Card,
    CsrfField,
    Form,
    Heading,
    Hedron,
    Page,
    Stack,
    SubmitButton,
    Text,
    TextInput,
    html,
    redirect_local,
)

app = Hedron(
    title="Operations",
    security="standard",
    explorer="off",
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET",
        "replace-in-production",
    ),
)

_NOTES: list[str] = []  # Demo only. Use application-owned durable storage in production.


@app.view("/status")
def status():
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        role="status",
        aria={"live": "polite"},
    )


@app.action("/notes", method="POST")
def add_note(note: str = FastAPIForm(...)):
    value = note.strip()
    if value:
        _NOTES.append(value)
    return redirect_local("/")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Heading("Operations", level=1),
            Card(
                status(),
                status.refresh_button("Refresh status"),
                title="Service status",
            ),
            Card(
                Form(
                    CsrfField(),
                    TextInput("note", required=True),
                    SubmitButton("Save note"),
                    action="/notes",
                    method="post",
                ),
                title=f"Notes ({len(_NOTES)})",
            ),
        ),
        title="Operations",
    )
```

Run and inspect it:

```bash
python -m pip install "hedron>=1.0.0,<1.1" "uvicorn[standard]"
uvicorn app:app --reload
python -m hedron --app app:app routes
python -m hedron --app app:app check
```

The list is intentionally marked as demo-only. Multiple workers do not share Python process
memory, and a restart erases it.

## Page, view, and action contracts

### Page: equivalent to a server-rendered route component

```python
@app.page("/reports")
def reports():
    return Stack(
        Heading("Reports", level=1),
        Text("Choose a report."),
    )
```

A page should return the document's presentation tree. It may receive FastAPI dependencies,
path/query parameters, and a `Request`. Keep writes out of GET page handlers.

### View: equivalent to a server read plus targeted render

```python
@app.view("/queue-size")
def queue_size():
    return Text("12 jobs waiting")


@app.page("/")
def dashboard():
    return Stack(
        queue_size(),
        queue_size.refresh_button("Refresh queue"),
    )
```

The decorated function becomes a handle:

- `queue_size()` materializes its stable host in the page.
- `queue_size.path` is the registered request path.
- `queue_size.dom_id` is the authorized target ID.
- `queue_size.refresh_button(...)` emits matching HTMX request/target attributes.

Do not replace this with a made-up `hx-target="#queue"` unless you deliberately use the
advanced `FragmentRegion` API and preserve the same region through route, control, and response.

### Action: equivalent to an API mutation, not an event callback

```python
from hedron import refresh


@app.action("/queue/retry", method="POST")
def retry_failed_jobs():
    retry_jobs_in_service_layer()
    return refresh(queue_size).toast("Retry requested")
```

Treat the action like any production API endpoint: authenticate, authorize the specific object,
validate input, make the write idempotent when appropriate, and return an explicit outcome. A UI
control is not an authorization boundary.

## HTML authoring rules

Prefer a semantic built-in when one exists. Use the `html` factory for small native details:

```python
from hedron import Heading, Link, Main, Text, html

tree = Main(
    Heading("Audit log", level=1),
    Text("Recent security events"),
    html.ul(
        html.li("Session created"),
        html.li("Role changed"),
        aria={"label": "Events"},
        data={"source": "audit"},
        class_="audit-events",
    ),
)
```

Rules:

- Plain strings and `Text(...)` are escaped.
- Use `class_`, not `className`.
- Use `aria={"label": ...}` and `data={"name": ...}` for grouped attributes.
- Python-friendly HTMX spellings such as `hx_get=` are supported, but handles and controls are
  safer because they keep the URL and target synchronized.
- Use native links for navigation and buttons/forms for actions. Do not make a clickable `div`.
- Preserve heading order, labels, landmarks, keyboard behavior, focus, and live-region semantics.
- Use `SafeUrl` for deliberate URL trust boundaries and `TrustedHtml` only after reviewed
  sanitization. Never mark user input trusted to make an error disappear.

## CSS and visual design rules

Think of Hedron built-ins as a typed design system over ordinary CSS. Start with semantic
composition rather than recreating a Tailwind or CSS-in-JS layer in Python.

```python
from hedron import Card, Grid, Heading, Metric, Stack, Text

overview = Stack(
    Heading("Overview", level=1),
    Grid(
        Card(Metric("Requests", "18.4k", delta="+7%", delta_tone="up")),
        Card(Text("84 ms"), title="p95 latency"),
        Card(Text("No incidents"), title="Incidents"),
        columns={"base": 1, "md": 3},
    ),
    gap="lg",
)
```

Priority order:

1. Choose the correct semantic/component primitive.
2. Use shared props such as `appearance`, `emphasis`, `size`, `density`, `gap`, `padding`,
   `elevation`, and responsive maps when the component documents them.
3. Use `Theme`, `DesignSystem`, `StyleScope`, or a documented theme token for product-wide
   presentation.
4. For a project-owned component with unique visual detail, colocate `styles.css` in its component
   folder and use Hedron's scoped style-symbol/build path.
5. Use `class_` as a stable extension hook when a stylesheet owns that class.

Do not:

- invent unsupported props because they resemble CSS properties;
- pass arbitrary inline `style` dictionaries as the primary styling system;
- inject runtime `<style>` elements;
- copy CSS used by documentation simulations into an application;
- target undocumented private descendant selectors;
- add React, npm, Vite, or a client CSS framework unless the project explicitly owns that separate
  frontend architecture.

Hedron's production build compiles and fingerprints component CSS and assets. Node.js is not
required for the normal Hedron build.

## State ownership

| State | Owner | Wrong owner |
|---|---|---|
| Open menu/tab/disclosure | Built-in local behavior or Alpine | Database/session round trip for every toggle |
| Form draft before submit | Native browser form controls | Global Python variable |
| Authenticated identity | Host session/identity provider | DOM, Alpine, hidden field |
| Record or workflow state | Database/service layer | Component instance or module list |
| Job progress | Durable job backend, polled by a view | Unbounded in-memory task registry in production |
| Cache | Configured bounded backend and explicit policy | Unbounded module dictionary |
| Request-specific values | FastAPI request/dependencies | Mutable process-global singleton |

Assume multiple processes and concurrent requests. A component object is not a React component
instance with a persistent lifecycle. Reconstruct the UI from authoritative state on each request.

## Forms and security

For a cookie-authenticated FastAPI/Flask form:

- use `@app.action` for the unsafe route;
- render `CsrfField()` inside the form;
- perform a safe GET before testing POST so the client receives the CSRF cookie;
- validate with FastAPI/Pydantic or `FormBody`;
- authenticate and authorize in dependencies or the service boundary;
- never trust hidden fields for identity, tenant, price, role, or permission;
- redirect after a classic successful POST, or return a validated fragment outcome for HTMX.

Hedron's CSRF protection does not replace authorization. Escaping does not make a URL, redirect,
or raw HTML trusted. A signed cookie prevents tampering; it does not provide server-side revocation
or make secrets safe to store in the cookie.

## Testing pattern

Test documents and fragments separately. Use the handle as the target authority:

```python title="test_app.py"
from fastapi.testclient import TestClient

from app import app, status


def test_home_and_status_fragment() -> None:
    with TestClient(app) as client:
        page = client.get("/")
        fragment = client.get(
            status.path,
            headers={
                "HX-Request": "true",
                "HX-Target": status.dom_id,
            },
        )

    assert page.status_code == 200
    assert "<html" in page.text.lower()
    assert fragment.status_code == 200
    assert "<html" not in fragment.text.lower()
    assert "All systems operational" in fragment.text
```

Also test:

- unknown HTMX targets fail with `403`;
- unauthenticated and unauthorized callers fail closed;
- invalid form data produces the documented validation response;
- loading, empty, success, and recoverable-error branches preserve the target boundary;
- keyboard/focus behavior and announcements in a real browser for interactive components;
- production construction/build with the actual deployment settings.

## Troubleshooting algorithm

Diagnose in this order:

1. Confirm interpreter and version: `python -c "import hedron; print(hedron.__version__)"`.
2. Run `python -m hedron --app module:app routes` and verify path/method ownership.
3. Run `python -m hedron --app module:app check`; follow the `HED-*` remediation.
4. Inspect browser Network data: request URL, method, status, `HX-Request`, `HX-Target`, response
   body, and response `HX-*` headers.
5. Inspect rendered HTML for the expected host ID and static asset URLs.
6. Reproduce with `TestClient` using the same cookies, headers, and form fields.
7. Only then inspect lower-level renderer or framework internals.

| Symptom | Likely cause | Correct response |
|---|---|---|
| `ModuleNotFoundError: hedron` | Wrong environment/interpreter | Activate the project environment; install/sync with that interpreter. |
| `hedron: command not found` | Console script not on `PATH` | Use `python -m hedron`. |
| Blank/unstyled page | Static assets not mounted or proxy path stripped | Use `Hedron()` or `mount_hedron_static`; preserve `/hedron-static/` and `/hedron-assets/`. |
| Button does nothing | No executable route/HTMX attributes, JS asset failure, or disabled control | Use a handle control; inspect HTML and Network. |
| Fragment returns `403` | `HX-Target` does not match the declared host/region | Use `handle.dom_id` or the handle's built-in control. Do not weaken the allowlist. |
| POST returns `403` | Missing/mismatched CSRF cookie and token, or authorization denial | GET first, send `CsrfField()` value, then distinguish CSRF from authz. |
| Request returns `422` | Input names/types do not match FastAPI/Pydantic boundary | Align form names and model fields; render validation errors. |
| Full document appears inside a panel | A view/action returned a page or the wrong route was called | Return only the fragment tree for the target. |
| Replacement loses future refreshes | `outerHTML` response did not preserve the host boundary | Return the complete target host or use the generated view handle contract. |
| Works with one worker only | Process-local state/cache/jobs/session assumption | Move authoritative state to shared durable infrastructure. |
| CSS change missing in production | Build manifest/assets are stale | Run `hedron build` and deploy the generated build directory. |
| Production startup refuses to run | Missing build, weak secret, in-memory backend, unsafe plugin/explorer setting | Fix the named gate; do not casually suppress it. |

Never “fix” a `403`, CSRF error, safe URL error, or production gate by disabling the policy before
identifying the violated contract.

## Production completion criteria

Before claiming a Hedron app is production-ready:

- pin Hedron and optional packages to compatible bounded ranges;
- use `security="standard"` or `"strict"` and an explicit strong `session_secret`;
- turn Explorer off or secure it with real authorization;
- run `hedron build` and deploy its manifest/assets;
- configure durable cache/job backends for production and multi-worker operation;
- use shared session infrastructure or a deliberate affinity model when required;
- keep authentication, object authorization, tenant isolation, CSRF, and validation explicit;
- bound uploads, caches, job payloads, tables, streams, and in-memory collections;
- preserve static paths and root-path behavior through the reverse proxy;
- run tests plus `hedron check`; smoke the real proxy path and an unsafe form action.

Use [Ship a Hedron app](../guides/ship.md) as the release checklist.

## Forbidden substitutions

Do not substitute these patterns unless the user explicitly requests a different architecture:

- React component state for server-authoritative state;
- client-side fetching for an existing `@app.view` handle;
- a generic `<div>` tree for available semantic Hedron components;
- raw string HTML for components or `html.*` nodes;
- manual `HX-*` response headers for `InteractionResult`/response helpers;
- guessed CSS properties as component kwargs;
- process-local dictionaries for production persistence;
- a GET route for a mutation;
- hidden form values for authorization;
- private FastAPI, Starlette, HTMX, Alpine, or Hedron internals for a documented public API.

## Retrieval map

When this page is insufficient, read only the smallest relevant authority:

| Need | Authority |
|---|---|
| First runnable application | [Build your first app](quickstart.md) |
| Route/component mental model | [Core concepts](core-concepts.md) |
| API selection | [Choose an interaction API](interaction-apis.md) |
| Exact symbol by task | [API by task](../api/by-task.md) |
| Components and constructor contracts | [Component catalog](../components/index.md) |
| HTMX requests and targets | [HTMX interactions](../guides/htmx-interactions.md) |
| Local browser state | [What is Alpine?](what-is-alpine.md) |
| Forms and CSRF | [Minimal form](../guides/minimal-form.md) · [Forms and actions](../guides/forms-and-actions.md) |
| Styling and component CSS | [Comprehensive styling](../guides/styling.md) |
| Tests | [Test your UI](../guides/testing.md) |
| Failure lookup | [Troubleshooting](../guides/troubleshooting.md) · [Error codes](../guides/error-codes.md) |
| Deployment | [Ship](../guides/ship.md) · [Deployment](../guides/deployment.md) |
| Exact signatures | [Autodoc](../api/AUTODOC.md) |
| Stability/support | [Stability](../api/STABILITY.md) · [Current release](../guides/current-release.md) |

When source code and public documentation appear to disagree, do not silently depend on an
internal behavior. Verify the installed version, prefer the stable documented contract, and report
the discrepancy.
