# Build an HTMX interaction

Hedron keeps the browser/server boundary explicit: a control makes an ordinary HTTP
request, the handler returns typed content, and HTMX swaps the resulting HTML into a
declared region. This guide builds that loop without adding client-side application code.

## What you will build

The page below contains a status panel and a refresh button. Clicking the button requests
only a replacement panel, while direct navigation still returns a complete document.

**If you used `hedron new`:** open the scaffold `app.py`. Keep the existing `Hedron(...)`
app and the scaffold `home` route. Add the imports and `/status` route below, then **edit**
`home()` so it renders the status panel (do not create a second app file). If you are on
Path B (manual `app.py`), create the file as shown in the complete listing at the end of
this section.

### 1. Add imports and the status region

At the top of `app.py`, extend the imports and add the region helper (keep your existing
`Hedron` import and `app = Hedron(...)` block):

```python
from datetime import UTC, datetime

from hedron import (
    FragmentRegion,
    Hedron,
    InteractionPolicy,
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
        trigger={"statusRefreshed": True},
        cache="vary-htmx",
        policy=InteractionPolicy(vary_on_target=True),
        explanation="Refresh the declared service status region",
    )
```

### Complete file (Path B / reference)

```python title="app.py"
from datetime import UTC, datetime

from hedron import (
    FragmentRegion,
    Hedron,
    InteractionPolicy,
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
        trigger={"statusRefreshed": True},
        cache="vary-htmx",
        policy=InteractionPolicy(vary_on_target=True),
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
`RefreshButton` emits a local `hx-get`, `hx-target`, and `hx-swap`; the component route
returns a fragment rather than a second document shell. That browser click is the first
interactive win—prefer it over `curl` when learning.

## Understand the contracts

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

The body contains the replacement panel. The response also includes `HX-Trigger` and a
`Vary` value that separates page, fragment, history-restore, and target-specific cache
variants.

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
    assert "HX-Target" in response.headers["Vary"]


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
