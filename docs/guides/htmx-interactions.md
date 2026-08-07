# Extend the HTMX scaffold

You already have a working Refresh loop from
[Build your first app](../getting-started/quickstart.md). This page **extends that same
`app.py`** — do not paste a second full scaffold, and do not re-declare
`service-status` if it already exists.

## What you already have

`hedron new` registered:

- `status = app.region("service-status", …)`
- `status_panel()` returning a div with `id=status.id`
- `@app.fragment("/status", region=status)` returning `swap(status_panel())`
- `RefreshButton.for_region(status, href="/status", …)` on the home page

Click **Refresh status** once to confirm the UTC timestamp updates. If that works, the
region allowlist is correct — continue below.

## 60-second mental model

1. The button emits `hx-get`, `hx-target`, and `hx-swap` (`RefreshButton.for_region`).
2. The browser requests the fragment URL with HTMX headers (`HX-Request`, `HX-Target`).
3. The server returns **only the region HTML**, not a full document.
4. HTMX swaps that HTML into the target.

A wrong `HX-Target` returns **403** by design — fix typos in the region id / selector.

### Try it (simulated)

=== "Demo"

    Multi-region refresh plus an allowlist miss — docs simulation (no live server).

    <!-- hedron-sim:htmx-interactions -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os
    from datetime import UTC, datetime

    from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

    app = Hedron(
        title="HTMX interactions",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    status = app.region("hx-guide-status", description="Status panel")
    notes = app.region("hx-guide-notes", description="Notes counter")
    probe = app.region("hx-guide-probe", description="Allowlist probe")


    def status_panel():
        stamp = datetime.now(UTC).strftime("%H:%M:%S")
        return html.div(
            html.strong("Service healthy"),
            html.span(f"Checked at {stamp}"),
            id=status.id,
            role="status",
            aria={"live": "polite"},
        )


    def notes_panel():
        return html.div(
            Text("Sample notes region"),
            html.span("Allowlisted #hx-guide-notes — count stays 0 in this example"),
            id=notes.id,
            role="status",
            aria={"live": "polite"},
        )


    def probe_panel():
        return html.div(
            html.strong("Allowlisted swap"),
            html.span("HX-Target matched the declared probe region"),
            id=probe.id,
            role="status",
            aria={"live": "polite"},
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                status_panel(),
                RefreshButton.for_region(status, href="/status", label="Refresh status"),
                notes_panel(),
                RefreshButton.for_region(notes, href="/notes-count", label="Refresh sample region"),
                html.div(
                    html.button(
                        "Correct target → 200",
                        type="button",
                        **{
                            "hx-get": "/probe",
                            "hx-target": probe.selector,
                            "hx-swap": "outerHTML",
                        },
                    ),
                    html.button(
                        "Wrong #panel → 403",
                        type="button",
                        **{
                            "hx-get": "/probe",
                            "hx-target": "#panel",
                            "hx-swap": "outerHTML",
                        },
                    ),
                    probe_panel(),
                ),
            ),
            title="HTMX",
        )


    @app.fragment("/status", region=status)
    def refresh_status():
        return swap(status_panel())


    @app.fragment("/notes-count", region=notes)
    def refresh_notes():
        return swap(notes_panel())


    @app.fragment("/probe", region=probe)
    def refresh_probe():
        return swap(probe_panel())
    ```

## Delta: add a second region (notes count)

Keep the existing status panel. Add a **second** region that counts notes in memory so
you learn multi-region wiring without rebuilding Hello.

### 1. Add a notes region and panel (below your existing `status` block)

```python
notes_region = app.region("notes-count", description="Notes counter")
_NOTES: list[str] = []


def notes_panel():
    return html.div(
        Text(f"Notes saved: {len(_NOTES)}"),
        id=notes_region.id,
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
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
            notes_panel(),
            RefreshButton.for_region(
                notes_region, href="/notes-count", label="Refresh notes count"
            ),
        ),
        title="Home",
    )
```

### 3. Add one fragment route (do not duplicate `/status`)

```python
@app.fragment("/notes-count", region=notes_region)
def refresh_notes_count():
    return swap(notes_panel())
```

Reload the app, click **Refresh notes count**. The count stays at `0` until you add a
form in [Minimal form POST](minimal-form.md) — the point of this delta is a second
allowlisted region, not persistence yet.

**Stuck with 403?** The `HX-Target` did not match a declared region. See
[Troubleshooting](troubleshooting.md#htmx-403-on-fragment-request).

## Contracts (after the second click)

| Contract | Responsibility |
|---|---|
| `app.region(...)` | Declares one fragment region (`id` + default `#id` selector). |
| `RefreshButton.for_region` | Wires `hx-target` from that region. |
| `@app.fragment` | Registers a fragment endpoint and allowlists the region. |
| `swap(...)` | Builds the typed fragment response. |

Route-declared regions are authoritative. A request whose `HX-Target` is not allowlisted
receives `403`.

Optional polish on either handler:

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

## Path B only — no scaffold yet

If you skipped `hedron new`, copy the complete listing from
[Build your first app](../getting-started/quickstart.md) first, confirm Refresh works,
then return here for the notes-count delta. A full-file dump on this page would fight the
scaffold you already have.

## Flask / Django

Wire the same `Poll` / `RefreshButton` pattern through `hedron_route` / `hedron_view` and
`interaction_response` — see [Flask](../getting-started/flask.md) and
[Django](../getting-started/django.md). Prefer polling for job status; FastAPI-only
SSE/WebSocket helpers are **experimental**.

## Inspect / test

```bash
curl \
  -H 'HX-Request: true' \
  -H 'HX-Target: #notes-count' \
  http://127.0.0.1:8000/notes-count
```

```python title="test_app.py"
from fastapi.testclient import TestClient

from app import app


def test_notes_count_fragment() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/notes-count",
            headers={"HX-Request": "true", "HX-Target": "#notes-count"},
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

## When the interaction mutates state

Use `@app.action(..., method="POST")` for a mutation. Built-in security profiles validate
CSRF on unsafe methods automatically after a safe GET seeds the cookie.

**Next:** [Minimal form POST](minimal-form.md) — CSRF-safe create on `/notes` (same app).

Also: [Security](security.md) · [Test your UI](testing.md) ·
[Interaction API](../api/INTERACTION.md) · [Hedron API](../api/HEDRON.md)
