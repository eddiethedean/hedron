# Extend the HTMX scaffold

!!! note "FastAPI scaffold"

    This page extends `@app.view` from
    [Build your first app](../getting-started/quickstart.md). Flask and Django adapters
    keep their own `HedronBlueprint` / `@hedron_view` APIs — do not paste this onto an
    adapter scaffold.

You already have a working Refresh loop from
[Build your first app](../getting-started/quickstart.md). This page **extends that same
`app.py`** — do not paste a second full scaffold.

Default vs explicit APIs: [Which interaction API?](../getting-started/interaction-apis.md).
0.50 authoring (`ActionHandle.effect` / `.after(load=)`, `Select.depends_on`, `Lazy` error
templates, danger `Toast` dismiss) is documented on [Interaction API](../api/INTERACTION.md).

## What you already have

`hedron new` registered:

- `@app.view("/status")` as `status`
- `status()` on the home page
- `status.refresh_button("Refresh status")`

Click **Refresh status** once to confirm the UTC timestamp updates. If that works, the
generated `/status` route is correct — continue below.

## 60-second mental model

1. `status.refresh_button(...)` emits `hx-get="/status"`, `hx-target`, and `hx-swap`.
2. The browser requests `/status` with HTMX headers (`HX-Request`, `HX-Target`).
3. The server returns **only the region HTML**, not a full document.
4. HTMX swaps that HTML into the target.

A wrong `HX-Target` returns **403** by design.

### Try it (simulated)

=== "Demo"

    Two refreshable regions on the Hello scaffold — docs simulation (no live server).

    <!-- hedron-sim:htmx-interactions -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os
    from datetime import UTC, datetime

    from hedron import Hedron, Page, Stack, Text, html

    app = Hedron(
        title="HTMX interactions",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    _NOTES: list[str] = []


    @app.view("/status")
    def status():
        stamp = datetime.now(UTC).strftime("%H:%M:%S")
        return html.div(
            Text(f"All systems operational · refreshed {stamp}"),
            role="status",
            aria={"live": "polite"},
        )


    @app.view("/notes-count")
    def notes():
        return html.div(
            Text(f"Notes saved: {len(_NOTES)}"),
            role="status",
            aria={"live": "polite"},
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                Text("Hello from hedron new"),
                status(),
                status.refresh_button("Refresh status"),
                notes(),
                notes.refresh_button("Refresh notes count"),
            ),
            title="Home",
        )
    ```

## Delta: add a second refreshable view

Keep the existing `status` view. Add a **second** refreshable that counts notes in memory.

### 1. Add a notes view (below your existing `status` function)

```python
_NOTES: list[str] = []


@app.view("/notes-count")
def notes():
    return html.div(
        Text(f"Notes saved: {len(_NOTES)}"),
        role="status",
        aria={"live": "polite"},
    )
```

### 2. Extend `home()` — keep the greeting and status controls

```python
@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from hedron new"),
            status(),
            status.refresh_button("Refresh status"),
            notes(),
            notes.refresh_button("Refresh notes count"),
        ),
        title="Home",
    )
```

Reload the app, click **Refresh notes count**. The count stays at `0` until you add a
form in [Minimal form POST](minimal-form.md) that appends to `_NOTES` (same scaffold).

**Stuck with 403?** The `HX-Target` did not match the view’s host. See
[Troubleshooting](troubleshooting.md#htmx-403-on-fragment-request).

## Contracts (after the second click)

| Contract | Responsibility |
|---|---|
| `@app.view("/path")` | Registers a GET fragment view and returns a handle. |
| `status()` | Renders the view (and its host) on the page. |
| `status.refresh_button(...)` | Wires `hx-get` / `hx-target` / `hx-swap` from that handle. |

## Explicit allowlist (`region` / `@fragment`)

`hedron new` does **not** generate `app.region` or `@app.fragment`. Those remain the
lower-level API when you need an explicit selector allowlist. See
[Which interaction API?](../getting-started/interaction-apis.md) and
[Interaction](../api/INTERACTION.md).

## Flask / Django

Wire the same Refresh pattern through `hedron_route` / `hedron_view` and
`interaction_response` — see [Flask](../getting-started/flask.md) and
[Django](../getting-started/django.md). Prefer polling for job status; FastAPI-only
SSE/WebSocket helpers are **experimental**.

## Inspect / test

```bash
curl \
  -H 'HX-Request: true' \
  -H 'HX-Target: #h-view-notes' \
  http://127.0.0.1:8000/notes-count
```

```python title="test_app.py"
from fastapi.testclient import TestClient

from app import app


def test_notes_count_fragment() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/notes-count",
            headers={"HX-Request": "true", "HX-Target": "#h-view-notes"},
        )
    assert response.status_code == 200
    assert "Notes saved:" in response.text
    assert "<html" not in response.text


def test_status_rejects_an_unknown_target() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/status",
            headers={"HX-Request": "true", "HX-Target": "#other-panel"},
        )
    assert response.status_code == 403
```

Confirm the host id in the page HTML if `#h-view-notes` does not match your build.

## When the interaction mutates state

Use `@app.action` for a mutation. Built-in
security profiles validate CSRF on unsafe methods automatically after a safe GET seeds
the cookie.

**Next:** [Minimal form POST](minimal-form.md) — add a POST that appends to `_NOTES`
(same scaffold).

Also: [Which interaction API?](../getting-started/interaction-apis.md) ·
[Security](security.md) · [Test your UI](testing.md) ·
[Interaction API](../api/INTERACTION.md) · [Hedron API](../api/HEDRON.md)
