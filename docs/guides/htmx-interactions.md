# Build an HTMX interaction

HTMX swaps a page region when you click a link or button, without a full reload. Hedron
keeps that boundary explicit: declare one **region**, register a **fragment** route that
returns `swap(...)`, and wire the control with `RefreshButton.for_region`—without
client-side application code.

## 60-second HTMX primer

1. The page includes a button with `hx-get="/status"`, `hx-target="#service-status"`,
   and `hx-swap="outerHTML"` (`RefreshButton.for_region` emits these for you).
2. The browser requests `/status` with HTMX headers (`HX-Request`, `HX-Target`, …).
3. The server returns **only the HTML for that region**, not a full document.
4. HTMX replaces `#service-status` with the response body.

You will build that loop next. Copy the snippets as written—`app.region`,
`@app.fragment`, `swap`, and `RefreshButton.for_region` share one region object so you
do not triple-copy ids. The lower-level `FragmentRegion` / `InteractionResult` envelope
is covered under [Advanced](#advanced-raw-region-and-interactionresult) after the click
works.

## What you will build

A status panel and a **Refresh status** button. Clicking the button replaces only the
panel; direct navigation still returns a complete document.

**If you used `hedron new`:** open the scaffold `app.py`. It already follows this
pattern with a **UTC timestamp** on each Refresh — click **Refresh status** first, then
extend the panel as shown below. If you used the manual (no-scaffold) path, create the
file as shown in the complete listing at the end of this section.

!!! tip "Goal: click first"

    Get the timestamp updating in the browser before reading the contract table below.
    A wrong `HX-Target` returns **403** by design (not a bug)—fix typos in the region
    id / selector if that happens.

### 1. Add imports, a region, and a status panel

At the top of `app.py`, extend the imports (keep your existing `Hedron` import and
`app = Hedron(...)` block):

```python
from datetime import UTC, datetime

from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

# Keep your existing app = Hedron(...) from the scaffold.

status = app.region("service-status", description="Live status panel")


def status_panel():
    checked_at = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · checked {checked_at}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )
```

One `status` object carries `id` and `selector` (`#service-status` by default). Pass it
to the panel, the button, and the fragment route—do not retype the string three times.

### 2. Edit `home()` and add `/status`

Replace only the body of the scaffold `home()` (or keep a greeting above the stack), then
add the fragment route **below** it:

```python
@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from hedron new"),
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
        ),
        title="Home",
    )


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())
```

That is enough for the first click. Cache/vary and triggers are optional polish covered
below under [Understand the contracts](#understand-the-contracts-after-the-click).

### Complete file (Path B / reference)

```python title="app.py"
from datetime import UTC, datetime

from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

app = Hedron(
    title="Service status",
    security="standard",
    session_secret="replace-in-production",
)

status = app.region("service-status", description="Live status panel")


def status_panel():
    checked_at = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · checked {checked_at}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
        ),
        title="Service status",
    )


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())
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
`HX-Target` did not match a declared region (often a typo in the region id). See
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
| `app.region(...)` | Declares one fragment region (`id` + default `#id` selector). |
| `RefreshButton.for_region` | Describes the request URL and wires `hx-target` from that region. |
| `@app.fragment` | Registers a fragment endpoint and allowlists the region. |
| `swap(...)` | Builds the typed fragment response (content plus optional OOB / headers). |
| `InteractionPolicy` | Sets interaction defaults such as synchronization and target-aware cache variation. |

Route-declared regions are authoritative. A request whose `HX-Target` is not in the
route's region allowlist receives `403`, even if a handler constructs a different policy.
This keeps client-provided target selectors from widening the route's intended update
surface.

Optional polish on the same handler:

```python
from hedron import InteractionPolicy, InteractionResult

@app.fragment("/status", region=status)
def refresh_status() -> InteractionResult:
    return swap(
        status_panel(),
        region_id=status.id,
        trigger={"statusRefreshed": True},
        cache="vary-htmx",
        policy=InteractionPolicy(vary_on_target=True),
        explanation="Refresh the declared service status region",
    )
```

!!! tip "Use the typed fields"

    Prefer `trigger=`, `redirect=`, `retarget=`, `history=`, and `cache=` on
    `swap(...)` / `InteractionResult`. Hedron validates local URLs and safe selectors
    before emitting the corresponding `HX-*` headers. The low-level `headers=` escape
    hatch accepts only the documented response-header allowlist.

## Advanced: raw region and InteractionResult

`app.region` returns a `FragmentRegion`. `@app.fragment` is an alias of `@app.component`
that merges `region=` / `regions=` into `fragment_regions=`. `swap(...)` returns an
`InteractionResult`. You can construct those pieces explicitly when you need to inspect
or customize the envelope:

```python
from hedron import FragmentRegion, InteractionResult, RefreshButton

STATUS_REGION = FragmentRegion(
    id="service-status",
    selector="#service-status",
    description="Live service status panel",
)

RefreshButton(
    "Refresh status",
    href="/status",
    target=STATUS_REGION.selector,
    swap="outerHTML",
)

@app.component("/status", fragment_regions=(STATUS_REGION,))
def refresh_status() -> InteractionResult:
    return InteractionResult(
        content=status_panel(),
        region_id=STATUS_REGION.id,
        explanation="Refresh the declared service status region",
    )
```

Prefer the primary path (`app.region` + `@app.fragment` + `swap` +
`RefreshButton.for_region`) unless you are debugging the allowlist or response fields
directly.

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
