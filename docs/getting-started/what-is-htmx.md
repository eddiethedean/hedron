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

That model remains available in Hedron. An `@app.page` route returns a `Page`, which
Hedron renders as a complete HTML document.

HTMX adds a second, smaller interaction model:

```text
Browser: GET /status and says “the target is #service-status”
Server:  <div id="service-status">All systems operational</div>
Browser: replaces only #service-status
```

The small piece of HTML returned by the server is called a **fragment**. The part of the
page it replaces is a **region**. Replacing it is a **swap**.

| | Full-page navigation | HTMX fragment update |
|---|---|---|
| Browser requests | A page URL | A fragment URL |
| Server returns | A complete HTML document | HTML for one region |
| Browser updates | The whole document | The chosen region only |
| Hedron API | `@app.page` + `Page` | `@app.fragment` + `swap(...)` |

## The Hedron + HTMX request cycle

When someone clicks the scaffold's **Refresh status** button, this is what happens:

```text
User clicks Refresh status
  → HTMX sends GET /status
      HX-Request: true
      HX-Target: service-status
  → Hedron returns HTML for #service-status only
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

This is the complete interaction pattern used by `hedron new`. It assumes the Hedron
`app` has already been created; the [Quick Start](quickstart.md) contains the complete,
runnable file.

```python
from datetime import UTC, datetime

from hedron import Page, RefreshButton, Stack, Text, html, swap

# 1. Declare the region that may be replaced.
status = app.region("service-status", description="Live status panel")


# 2. Return the region's current HTML. Keep its id stable.
def status_panel():
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )


# 3. Put the region and a control that targets it on the full page.
@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            status_panel(),
            RefreshButton.for_region(
                status,
                href="/status",
                label="Refresh status",
            ),
        ),
        title="Home",
    )


# 4. Return only the replacement HTML when HTMX requests it.
@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())
```

`RefreshButton.for_region(...)` renders the browser wiring for you. Its relevant output
is equivalent to:

```html
<button
  type="button"
  hx-get="/status"
  hx-target="#service-status"
  hx-swap="outerHTML"
>
  Refresh status
</button>
```

You can use HTMX attributes directly when you need them, but Hedron's region-aware
components remove selector duplication from the common path.

## The five pieces to remember

| Hedron code | Meaning |
|---|---|
| `app.region("service-status")` | Names a replaceable part of the page and gives it the selector `#service-status`. |
| `id=status.id` | Marks the actual HTML element for that region. The replacement must keep this id when using `outerHTML`. |
| `RefreshButton.for_region(status, href="/status")` | Makes a GET request and targets the declared region when clicked. |
| `@app.fragment("/status", region=status)` | Registers the fragment endpoint and allows it to update that region. |
| `swap(status_panel())` | Returns the replacement HTML as an interaction result. |

!!! tip "A useful reading trick"

    When you see Hedron interaction code, ask three questions: **What triggers the
    request? Which URL handles it? Which region receives the response?** If those three
    answers agree, you understand the interaction.

## Why declare regions?

HTMX sends the intended target in the `HX-Target` request header. Hedron checks that
target against the regions declared on the route.

The browser normally sends the target element's bare id; Hedron also accepts the
equivalent `#id` selector in hand-written requests and tests. For the example above:

- `HX-Target: service-status` (or `#service-status`) is allowed.
- `HX-Target: another-panel` (or `#another-panel`) receives HTTP **403**.
- A missing target on an ordinary HTMX fragment request also fails closed.

This catches selector mistakes early and prevents a fragment endpoint from being used
to update an undeclared part of the page. Prefer `RefreshButton.for_region(...)` over
repeating a target string by hand.

## Why Hedron uses HTMX

Hedron is a server-rendered Python framework. Its routes return typed components that
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

You can still add JavaScript for behavior that genuinely belongs in the browser. HTMX
simply means you do not need a SPA for routine server-driven interactions.

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

1. [Build your first app](quickstart.md) — run this exact Refresh interaction.
2. [HTMX interactions](../guides/htmx-interactions.md) — add a second declared region and test the request.
3. [Minimal form POST](../guides/minimal-form.md) — mutate server state with CSRF protection and refresh the page region.
4. [Interaction API](../api/INTERACTION.md) — redirects, response events, out-of-band updates, and advanced policies.
