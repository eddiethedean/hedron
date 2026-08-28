# What is HTMX?

**[HTMX](https://htmx.org) lets an HTML element make an HTTP request and replace part of
the current page with HTML returned by the server.**

That is the central idea. You keep rendering HTML on the server, as a traditional web
application does, while adding interactions that do not reload the entire page. Hedron
uses HTMX to connect browser events to Python fragment routes.

You do **not** need prior HTMX experience to use Hedron. You also do not need Node.js,
npm, JSX, or a separate frontend application.

## Start with an ordinary web page

Without HTMX, clicking a link usually asks the server for a complete page:

```text
Browser: GET /
Server:  <html> ... the complete document ... </html>
Browser: replaces the current document
```

That model remains available in Hedron. An `@app.page` route returns one presentation
tree, which Hedron renders as a complete HTML document.

HTMX adds a second, smaller interaction model:

```text
Browser: GET /status and says “the target is the status view host”
Server:  <div id="h-view-status">All systems operational</div>
Browser: replaces only that host
```

The small piece of HTML returned by the server is called a **fragment**. The part of the
page it replaces is a **region** (the view’s host). Replacing it is a **swap**.

| | Full-page navigation | HTMX fragment update |
|---|---|---|
| Browser requests | A page URL | A fragment URL |
| Server returns | A complete HTML document | HTML for one region |
| Browser updates | The whole document | The chosen region only |
| Hedron API | `@app.page` | `@app.view` + `status.refresh_button(...)` |

## The Hedron + HTMX request cycle

When someone clicks the scaffold's **Refresh status** button, this is what happens:

```text
User clicks Refresh status
  → HTMX sends GET /status
      HX-Request: true
      HX-Target: the status view host
  → Hedron returns HTML for that host only
  → HTMX replaces that region in the current page
```

1. Hedron renders a button with HTMX attributes such as `hx-get` and `hx-target`.
2. HTMX notices the click and sends a normal HTTP request in the background.
3. HTMX adds request headers so Hedron can identify the request and its intended target.
4. The fragment route returns the new HTML for that target.
5. HTMX swaps the response into the page. The rest of the page stays in place.

There is no hidden connection or client-side copy of your application state. Each
interaction is an inspectable HTTP request and HTML response.

## How Hedron expresses it in Python

This is the complete interaction pattern used by `hedron new`. For a paste-ready file that
includes `Hedron(...)` and `session_secret`, copy the listing on
[Build your first app](quickstart.md).

```python
from datetime import datetime, timezone

from hedron import Hedron, Stack, Text, html

app = Hedron(
    title="Hedron App",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
)


@app.view("/status")
def status():
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home():
    return Stack(
        status(),
        status.refresh_button("Refresh status"),
    )
```

!!! note "Advanced — explicit region control"

    The canonical roles are `@app.page`, `@app.view`, and `@app.action`. Use the lower-level
    `app.region` / `@app.view` API only when you need a distinct custom allowlist.

`status.refresh_button(...)` renders the browser wiring for you. Its relevant output
is equivalent to:

```html
<button
  type="button"
  hx-get="/status"
  hx-target="#h-view-status"
  hx-swap="outerHTML"
>
  Refresh status
</button>
```

You can use HTMX attributes directly when you need them, but handles remove selector
duplication from the common path. The lower-level `app.region` / `@app.view` API is
documented in [Which interaction API?](interaction-apis.md).

## The pieces to remember

| Hedron code | Meaning |
|---|---|
| `@app.view("/status")` | Registers a GET fragment view at `/status` and returns a handle. |
| `status()` | Renders the view host on the page. |
| `status.refresh_button(...)` | Makes a GET request and targets that host when clicked. |

!!! tip "A useful reading trick"

    When you see Hedron interaction code, ask three questions: **What triggers the
    request? Which URL handles it? Which region receives the response?** If those three
    answers agree, you understand the interaction.

## Why targets are allowlisted

HTMX sends the intended target in the `HX-Target` request header. Hedron checks that
target against the view host (or, on the explicit API, declared regions).

- A matching host / region is allowed.
- `HX-Target: another-panel` (or `#another-panel`) receives HTTP **403**.
- A missing target on an ordinary HTMX fragment request also fails closed.

This catches selector mistakes early and prevents a fragment endpoint from being used
to update an undeclared part of the page. Prefer `status.refresh_button(...)` over
repeating a target string by hand.

## Why Hedron uses HTMX

Hedron is a server-rendered Python framework. Its routes return components that
serialize to HTML, so returning HTML fragments is a natural extension of the same model.
HTMX gives those fragments browser-side interaction without requiring a second frontend
codebase.

This is a particularly good fit for dashboards, admin tools, forms, CRUD applications,
and job-status views where the server already owns the data and business rules.

Hedron bundles HTMX **2.0.10** and serves it from `/hedron-static/htmx.min.js`. A standard
Hedron page includes it automatically. Plain FastAPI integrations call
`mount_hedron_static(...)`; you do not install HTMX with npm or add a CDN script.

## What HTMX does—and does not do

HTMX handles browser events, HTTP requests, and HTML swaps. It is not:

- a client-side component framework or single-page application (SPA) framework like
  React or Vue;
- a state management system;
- a replacement for FastAPI, your database, authentication, or deployment;
- a requirement for every interaction—ordinary links and full-page form submissions
  still work;
- the Supported way to push server events continuously. Prefer polling for job status;
  Hedron's SSE and WebSocket helpers are FastAPI-only and experimental.

Use [Alpine](what-is-alpine.md) for disposable behavior that genuinely belongs in the
browser. HTMX means you do not need a SPA for routine server-driven interactions.

## Common questions

### Is HTMX a server or a Python dependency?

No. HTMX is a small JavaScript library that runs in the browser. Hedron is the Python
server framework that renders the pages and fragments HTMX requests.

### Does every route return a fragment?

No. Page routes return complete documents. Fragment routes return replaceable regions.
Action routes commonly handle state-changing POST requests and may also return a
fragment.

### Where is the JSON API?

This interaction does not require one. The server returns presentation-ready HTML.
Your application can still expose ordinary FastAPI JSON endpoints alongside Hedron.

### Will the back button work?

Routine region refreshes normally do not create history entries. HTMX can manage browser
history when an interaction opts into it; use that deliberately for navigation-like
changes rather than incidental refreshes.

### How do I debug an interaction?

Open the browser's developer tools and select **Network**. Click the control, then inspect:

1. the request URL and method;
2. the `HX-Request` and `HX-Target` request headers;
3. the response status;
4. the returned HTML fragment.

A **403** usually means the requested target does not match the fragment route's declared
region. See [Troubleshooting](../guides/troubleshooting.md#htmx-403-on-fragment-request).

## Continue learning

1. [Minimal form POST](../guides/minimal-form.md) — mutate server state with CSRF protection.
2. [HTMX interactions](../guides/htmx-interactions.md) — add a second declared region and test the request.
3. [Interaction API](../api/INTERACTION.md) — redirects, response events, out-of-band updates, and advanced policies.

If you have not scaffolded yet, start with [Build your first app](quickstart.md).
