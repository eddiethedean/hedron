# Build an HTMX interaction

HTMX swaps a page region when you click a link or button, without a full reload. Hedron
keeps that boundary explicit: a control makes an ordinary HTTP request, the handler
returns typed content, and HTMX swaps the resulting HTML into a declared region—without
client-side application code.

## 60-second HTMX primer

1. The page includes a button with `hx-get="/status"`, `hx-target="#service-status"`,
   and `hx-swap="outerHTML"` (Hedron’s `RefreshButton` emits these for you).
2. The browser requests `/status` with HTMX headers (`HX-Request`, `HX-Target`, …).
3. The server returns **only the HTML for that region**, not a full document.
4. HTMX replaces `#service-status` with the response body.

You will build that loop next. Copy the snippets as written—names like
`FragmentRegion` and `InteractionResult` are explained **after** your first click works.

## What you will build

A status panel and a **Refresh status** button. Clicking the button replaces only the
panel; direct navigation still returns a complete document.

**If you used `hedron new`:** open the scaffold `app.py`. Keep the existing `Hedron(...)`
app and the scaffold `home` route. Add the imports and `/status` route below, then **edit**
`home()` so it renders the status panel (do not create a second app file). If you are on
Path B (manual `app.py`), create the file as shown in the complete listing at the end of
this section.

!!! tip "Goal: click first"

    Get the timestamp updating in the browser before reading the contract table below.
    A wrong `HX-Target` returns **403** by design (not a bug)—fix typos in `target=` /
    `selector=` if that happens.

### 1. Add imports and a status panel

At the top of `app.py`, extend the imports (keep your existing `Hedron` import and
`app = Hedron(...)` block):

```python
from datetime import UTC, datetime

from hedron import (
    FragmentRegion,
    InteractionResult,
    Page,
    RefreshButton,
    Stack,
    Text,
    html,
)

# Keep your existing app = Hedron(...) from the scaffold.

STATUS_REGION = FragmentRegion(
    id="service-status",
    selector="#service-status",
    description="Live service status panel",
)


def status_panel():
    checked_at = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · checked {checked_at}"),
        id=STATUS_REGION.id,
        role="status",
        aria={"live": "polite"},
    )
```

### 2. Edit `home()` and add `/status`

Replace only the body of the scaffold `home()` (or keep a greeting above the stack), then
add the component route **below** it:

```python
@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from hedron new"),
            status_panel(),
            RefreshButton(
                "Refresh status",
                href="/status",
                target=STATUS_REGION.selector,
                swap="outerHTML",
            ),
        ),
        title="Home",
    )


@app.component("/status", fragment_regions=(STATUS_REGION,))
def refresh_status() -> InteractionResult:
    return InteractionResult(
        content=status_panel(),
        region_id=STATUS_REGION.id,
        explanation="Refresh the declared service status region",
    )
```

That is enough for the first click. Cache/vary and triggers are optional polish covered
below under [Understand the contracts](#understand-the-contracts-after-the-click).

### Complete file (Path B / reference)

```python title="app.py"
from datetime import UTC, datetime

from hedron import (
    FragmentRegion,
    Hedron,
    InteractionResult,
    Page,
    RefreshButton,
    Stack,
    Text,
    html,
)

app = Hedron(
    title="Service status",
    security="standard",
    session_secret="replace-in-production",
)

STATUS_REGION = FragmentRegion(
    id="service-status",
    selector="#service-status",
    description="Live service status panel",
)


def status_panel():
    checked_at = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · checked {checked_at}"),
        id=STATUS_REGION.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            status_panel(),
            RefreshButton(
                "Refresh status",
                href="/status",
                target=STATUS_REGION.selector,
                swap="outerHTML",
            ),
        ),
        title="Service status",
    )


@app.component("/status", fragment_regions=(STATUS_REGION,))
def refresh_status() -> InteractionResult:
    return InteractionResult(
        content=status_panel(),
        region_id=STATUS_REGION.id,
        explanation="Refresh the declared service status region",
    )
```

Run it:

=== "uv"

    ```bash
    uv run uvicorn app:app --reload
    ```

=== "Activated virtualenv (pip)"

    ```bash
    uvicorn app:app --reload
    ```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), then click **Refresh status**.
The timestamp in the panel should update without a full page reload. That browser click is
the first interactive win—prefer it over `curl` when learning.

**Success?** Continue below to understand the names you pasted. Stuck with **403**? The
`HX-Target` did not match a declared region (often a typo in `target=` / `selector=`). See
[Troubleshooting](troubleshooting.md#htmx-403-on-fragment-request).

## Flask / Django: same poll loop

The clock example above uses portable components. On Flask/Django, wire the same
`Poll` / `RefreshButton` pattern through `hedron_route` / `hedron_view` and
`interaction_response` — see [Flask](../getting-started/flask.md) and
[Django](../getting-started/django.md). Prefer polling for job status and live panels;
FastAPI-only SSE/WebSocket helpers are covered later on this page.

## Understand the contracts (after the click)

| Contract | Responsibility |
|---|---|
| `RefreshButton` | Describes the request URL, target, and swap behavior. |
| `@app.component` | Registers a fragment endpoint. |
| `FragmentRegion` | Names the selectors that the route is allowed to update. |
| `InteractionResult` | Carries content plus validated status, history, cache, and HTMX response behavior. |
| `InteractionPolicy` | Sets interaction defaults such as synchronization and target-aware cache variation. |

Route-declared regions are authoritative. A request whose `HX-Target` is not in the
route's `fragment_regions` allowlist receives `403`, even if a handler constructs a
different policy. This keeps client-provided target selectors from widening the route's
intended update surface.

Optional polish on the same handler:

```python
from hedron import InteractionPolicy

@app.component("/status", fragment_regions=(STATUS_REGION,))
def refresh_status() -> InteractionResult:
    return InteractionResult(
        content=status_panel(),
        region_id=STATUS_REGION.id,
        trigger={"statusRefreshed": True},
        cache="vary-htmx",
        policy=InteractionPolicy(vary_on_target=True),
        explanation="Refresh the declared service status region",
    )
```

!!! tip "Use the typed fields"

    Prefer `trigger=`, `redirect=`, `retarget=`, `history=`, and `cache=` on
    `InteractionResult`. Hedron validates local URLs and safe selectors before emitting
    the corresponding `HX-*` headers. The low-level `headers=` escape hatch accepts only
    the documented response-header allowlist.

## Inspect the response

You can exercise the fragment without a browser:

```bash
curl \
  -H 'HX-Request: true' \
  -H 'HX-Target: #service-status' \
  http://127.0.0.1:8000/status
```

The body contains the replacement panel. With the optional polish above, the response also
includes `HX-Trigger` and a `Vary` value that separates page, fragment, history-restore,
and target-specific cache variants.

## Test the boundary

```python title="test_app.py"
from fastapi.testclient import TestClient

from app import app


def test_status_fragment() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/status",
            headers={
                "HX-Request": "true",
                "HX-Target": "#service-status",
            },
        )

    assert response.status_code == 200
    assert "All systems operational" in response.text
    assert "<html" not in response.text


def test_status_rejects_an_unknown_target() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/status",
            headers={"HX-Request": "true", "HX-Target": "#other-panel"},
        )

    assert response.status_code == 403
```

## When the interaction mutates state

Use `@app.action(..., method="POST")` for a mutation. With a built-in security profile,
unsafe page, component, and action routes validate CSRF automatically: perform a safe GET
to seed the cookie, then submit the matching token in `X-CSRF-Token` or the `csrf_token`
form field. Authentication, authorization, destructive intent, and persistence remain
application responsibilities.

**Next:** [Minimal form POST](minimal-form.md) — CSRF-safe create/update loop (extend the
same app).

Also: [Security](security.md) · [Test your UI](testing.md) ·
[Interaction API](../api/INTERACTION.md)
