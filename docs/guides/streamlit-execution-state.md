# Streamlit execution and state → Hedron

The hardest part of a Streamlit migration is not finding a replacement for `st.metric`
or `st.dataframe`. It is deciding what should happen when a user interacts and where the
resulting state belongs.

Streamlit's default is to rerun the script after a widget interaction; forms batch inputs,
callbacks run before the rerun, and fragments can rerun independently. Hedron does not
simulate that runtime. A browser sends an HTTP request to one route, that route performs
one operation, and the response is either a full page, a fragment, or a redirect.

Official Streamlit references used by this guide:
[execution flow](https://docs.streamlit.io/develop/api-reference/execution-flow) ·
[forms](https://docs.streamlit.io/develop/concepts/architecture/forms) ·
[fragments](https://docs.streamlit.io/develop/concepts/architecture/fragments) ·
[Session State](https://docs.streamlit.io/develop/concepts/architecture/session-state) ·
[caching](https://docs.streamlit.io/develop/concepts/architecture/caching).

## Translate events by intent

Do not translate “rerun” literally. Identify why the rerun happened.

| Streamlit intent | Hedron request | Typical result |
|---|---|---|
| Change a shareable filter | GET page or GET fragment | Page/region rendered from query parameters |
| Submit several inputs together | GET form for filters; POST action for a write | Page, fragment, or 303 redirect |
| Run a button side effect | POST `@app.action` | Persist, then redirect or return a fragment |
| Refresh one expensive panel | GET `@app.fragment` | `swap(...)` into a declared region |
| Poll job progress | Repeated GET from `Poll` | Status fragment |
| Navigate to another screen | GET `@app.page` route | Full `Page` at a stable URL |
| Abort because input is invalid | Validate before work; return an error response/component | 4xx or validation fragment |
| Recompute derived data | Ordinary function, optionally `cache_data` | Validated Python value |

## Filters: widget values → query parameters

Streamlit often obtains the current value directly from a widget call:

```python
region = st.selectbox("Region", ["All", "North", "South"])
minimum = st.slider("Minimum revenue", 0, 5000, 0)
```

In Hedron, a GET form submits values to a page route with validation:

```python
from typing import Annotated, Literal

from fastapi import Query
from hedron import Form, FormField, Page, Select, SubmitButton

Region = Literal["All", "North", "South"]


@app.page("/")
def dashboard(
    region: Annotated[Region, Query()] = "All",
    minimum: Annotated[int, Query(ge=0, le=5000)] = 0,
) -> Page:
    filters = Form(
        FormField(
            name="region",
            label="Region",
            control=Select(
                "region",
                [(value, value) for value in ("All", "North", "South")],
                value=region,
            ),
        ),
        # Add the minimum control here.
        SubmitButton("Apply filters"),
        action="/",
        method="get",
    )
    return Page(filters, title="Dashboard")
```

The browser URL becomes `/?region=North&minimum=1000`. It can be bookmarked, shared,
logged, reproduced in a test, and validated before your application code runs.

Use a GET only for safe, repeatable operations. If the interaction changes server state,
use a POST action.

## Button callbacks → explicit actions

This Streamlit pattern combines the control, event, write, and follow-up rendering:

```python
if st.button("Approve order"):
    approve_order(order_id)
    st.success("Approved")
```

In Hedron, make the mutation boundary visible:

```python
from fastapi import Request
from fastapi.responses import RedirectResponse


@app.action("/orders/{order_id}/approve", method="POST")
async def approve(order_id: int, request: Request):
    # Resolve the user through a FastAPI dependency in a real app.
    # Authorize the order, validate the CSRF-protected form, then persist.
    await orders.approve(order_id)
    return RedirectResponse(f"/orders/{order_id}", status_code=303)
```

Render a normal POST form pointing at that URL. Add HTMX only when you want the response
to replace a declared page region. See [Minimal form POST](minimal-form.md) first, then
[Forms and actions](forms-and-actions.md).

This separation matters because page rendering can happen more than once. Writes belong
to mutation routes, never to a component's `render()` method or a safe GET route.

## `st.fragment` → declared fragment route

The concepts are related but not identical:

- Streamlit `st.fragment` reruns a portion of Python code independently.
- Hedron `@app.fragment` handles a distinct HTTP request and returns replacement HTML.

```python
from hedron import RefreshButton, html, swap

status = app.region("status", description="Order status")


def status_panel():
    return html.div(load_status(), id=status.id)


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())


# Place both on the page:
status_panel()
RefreshButton.for_region(status, href="/status", label="Refresh")
```

Hedron checks the browser's `HX-Target` against the route's declared regions. A mismatched
target receives 403 rather than silently updating an arbitrary part of the page.

## Choose a state owner

`st.session_state` is convenient because it can hold widget and application values in one
dictionary across reruns. Do not replace it with one large Hedron session object. Classify
each key by lifetime, authority, and sharing requirements.

| State | Best owner in Hedron | Examples |
|---|---|---|
| Shareable navigation/filter state | Path or query parameter | report id, region, date range, sort |
| One submitted operation | Validated query/form/body input | search form, create/update command |
| Small per-session workflow state | `SessionState[T]` / host session | wizard step, temporary preference |
| Durable business state | Database or application service | orders, annotations, chat history |
| Expensive derived result | `cache_data` with explicit TTL and scope | aggregate, API response, transform |
| Long-lived connection/model/client | FastAPI lifespan and dependency injection | DB engine, HTTP client, ML model |
| Non-secret browser preference | `BrowserStorage` / cookie where appropriate | density, dismissed hint, color choice |
| Job progress | Job backend; poll a status route | export, inference, batch import |

### Session state with an explicit contract

For the small subset that truly is session-scoped, use the dependency factory:

```python
from hedron import Hedron, Model, Page, SessionState, Text, session_state


class Preferences(Model):
    density: str = "comfortable"


@app.page("/preferences")
def preferences(
    state: SessionState[Preferences] = session_state("preferences", Preferences),
) -> Page:
    return Page(Text(f"Density: {state.value.density}"), title="Preferences")
```

`SessionState` is an explicit facade over the configured host session, not a global store.
Keep values bounded and serializable. Do not put database connections, request objects,
component trees, large dataframes, or durable records in it. See the [State API](../api/STATE.md).

## Cache migration is a design review

Streamlit documents `st.cache_data` as serializing cached values and returning a copy, and
`st.cache_resource` as sharing a singleton-like resource across users and sessions. Hedron's
APIs are not drop-in equivalents.

| Streamlit | Hedron migration |
|---|---|
| `@st.cache_data` | `@cache_data(...)` for derived data, after choosing TTL, scope, version, and key dimensions |
| `@st.cache_resource` | Create resources in FastAPI lifespan and inject them into routes |
| `func.clear()` / global cache clear | Invalidate by tag/version/backend according to application policy |
| User-dependent cached result | Use `scope="user"` or `"tenant"` with mandatory `vary_on` dimensions |
| Truly public immutable result | Use `scope="public"`; never include request/user/session data |

```python
from hedron import cache_data


@cache_data(ttl=300, scope="tenant", vary_on=("tenant_id",))
def load_summary(*, tenant_id: str, month: str) -> dict[str, int]:
    ...
```

Sensitive Hedron cache scopes without usable `vary_on` values run uncached rather than
inventing isolation. A public cache containing user-dependent data is a security bug. Read
the [Cache API](../api/CACHE.md) and [multi-tenant guidance](multi-tenant.md) before porting
cached authenticated queries.

## Other common translations

| Streamlit pattern | Hedron approach |
|---|---|
| `st.rerun()` after a write | Return a fragment, or redirect with 303 after POST |
| `st.stop()` after validation | Return early with a validation component/response; raise an HTTP error when appropriate |
| `on_change=` callback | Submit to a GET fragment/page or POST action based on whether it mutates state |
| `st.query_params` | Path/query parameters owned by the route |
| `st.Page` / `st.navigation` / `pages/` | Explicit `@app.page("/stable-url")` routes plus navigation components |
| `st.secrets` | Environment variables or your deployment platform's secret manager |
| `st.connection` | FastAPI lifespan, dependency injection, or Hedron's connection registry where appropriate |
| `st.context` | FastAPI `Request` plus browser context for client-reported hints |

Streamlit's preferred multipage API uses `st.Page` and `st.navigation`; Hedron routes make
the same page boundaries explicit in HTTP. Preserve stable public URLs during migration,
and enforce authorization in route dependencies—not merely by hiding a navigation link.

## Test the new boundary

Streamlit `AppTest` runs app code, simulates widget input, and inspects elements. Hedron
tests the HTTP contract directly:

```python
from fastapi.testclient import TestClient

from app import app


def test_north_filter() -> None:
    with TestClient(app) as client:
        response = client.get("/?region=North&minimum=4000")

    assert response.status_code == 200
    assert "$8,700" in response.text
    assert "South" not in response.text
```

Use `hedron.testing.AppScenario` for cookie-retaining multi-step flows and fragment
assertions. Reserve Playwright for browser behavior that HTTP tests cannot prove. See
[Test your UI](testing.md).

## Next

[Worked dashboard migration](streamlit-migration.md#worked-migration-sales-dashboard) ·
[Component matrix](streamlit-migration-matrix.md) ·
[Production cutover](streamlit-cutover.md)
