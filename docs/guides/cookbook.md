# Cookbook

Short, pasteable **snippets** for an existing app. Prefer the linked guides when you need
full context. For standalone mini-apps (pip + `app.py`), use
[Examples → Recipes](../examples/recipes/index.md).

## CSRF-safe POST (classic form)

```python
from fastapi import Form, Request

from hedron import Hedron, Page, SubmitButton, Text, TextInput, html
from hedron.security import csrf_token_for_request

app = Hedron(title="Notes", security="standard", session_secret="replace-me")


@app.page("/")
def home(request: Request) -> Page:
    token = csrf_token_for_request(request, request.app.state.hedron_security)
    return Page(
        html.form(
            html.input(type="hidden", name="csrf_token", value=token),
            TextInput("note", value="", required=True),
            SubmitButton("Save"),
            action="/save",
            method="post",
        ),
        title="Notes",
    )


@app.action("/save", method="POST")
def save(note: str = Form(...)) -> Page:
    return Page(Text(f"Saved: {note}"), title="Saved")
```

Full walkthrough: [Minimal form POST](minimal-form.md).

## Refresh a region (GET)

Preferred Path-A helpers (`app.region`, `@app.fragment`, `RefreshButton.for_region`,
`swap`). Older `FragmentRegion` + `@app.component` + `InteractionResult` still work —
see [Interaction API](../api/INTERACTION.md).

```python
from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

app = Hedron(title="Status", security="standard", session_secret="replace-me")
panel = app.region("panel", description="Status panel")


def panel_view():
    return html.div(Text("ok"), id=panel.id)


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            panel_view(),
            RefreshButton.for_region(panel, href="/panel", label="Refresh"),
        ),
        title="Status",
    )


@app.fragment("/panel", region=panel)
def refresh():
    return swap(panel_view())
```

Full walkthrough: [HTMX interactions](htmx-interactions.md).

## Out-of-band swap

```python
from hedron import InteractionResult, OobUpdate, Text

return InteractionResult(
    content=Text("Primary region"),
    region_id="main",
    oob=(OobUpdate(content=Text("Updated"), select="#badge"),),
    explanation="Update main and badge",
)
```

Keep every OOB selector inside the route’s `fragment_regions` allowlist.
See [Interaction API](../api/INTERACTION.md).

### Try it (simulated)

=== "Demo"

    One click updates the primary region and an OOB host — docs simulation.

    <!-- hedron-sim:cookbook-oob -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import (
        Hedron,
        InteractionResult,
        OobHost,
        OobUpdate,
        Page,
        Stack,
        html,
    )
    from hedron_core.interaction import InteractionPolicy

    app = Hedron(
        title="OOB swap",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    main = app.region("settings-main", description="Primary settings")
    host = app.region("toast-host", description="OOB toast host")


    def primary(draft: bool = True):
        return html.div(
            html.strong("Draft settings" if draft else "Settings saved"),
            html.span("Primary region — not saved yet." if draft else "Primary region updated."),
            id=main.id,
            role="status",
        )


    def oob_idle():
        return OobHost(
            html.span("Idle"),
            html.span(
                html.strong("#toast-host"),
                html.small("Stable OOB swap root"),
                class_="hedron-sim-oob-label",
            ),
            id=host.id,
        )


    def oob_saved():
        return OobHost(
            html.span("Saved"),
            html.span(
                html.strong("#toast-host"),
                html.small("Out-of-band update"),
                class_="hedron-sim-oob-label",
            ),
            id=host.id,
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                primary(True),
                oob_idle(),
                html.button(
                    "Save settings",
                    type="button",
                    **{
                        "hx-post": "/settings",
                        "hx-target": main.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
            ),
            title="OOB",
        )


    @app.component("/settings", methods=["POST"], fragment_regions=(main, host))
    def save() -> InteractionResult:
        return InteractionResult(
            content=primary(False),
            region_id=main.id,
            oob=(OobUpdate(content=oob_saved(), element_id=host.id),),
            policy=InteractionPolicy(declared_regions=(main, host)),
            explanation="Update main and OOB host",
        )
    ```

## Polling

```python
from hedron import ComponentRef, Hedron, Page, Poll, Text, swap

app = Hedron(title="Poll", security="standard", session_secret="replace-me")
tick = app.region("tick", description="Ticker")
REF = ComponentRef(logical_id="tick", path="/tick", target="#tick")


@app.fragment("/tick", region=tick)
def tick_fragment():
    return swap(Text("tick", id=tick.id))


@app.page("/")
def home() -> Page:
    return Page(
        Poll(ref=REF, interval_ms=2000, target_id=tick.id, content=Text("…", id=tick.id)),
        title="Poll",
    )
```

Prefer polling on every host — SSE helpers are **experimental**
([What’s ready](whats-ready.md), [live interaction](live-interaction.md)).

## File upload / download

```python
from hedron import DownloadButton, FileUpload, Page, SafeUrl, UrlPurpose

Page(
    FileUpload(name="roster", accept=".csv"),
    DownloadButton(
        "Download template",
        href=SafeUrl.parse("/downloads/template.csv", purpose=UrlPurpose.NAVIGATION),
    ),
)
```

Validate size/type in the action handler. Prefer `safe_download_response` for downloads
([utility components](../api/UTILITY_COMPONENTS.md)). For ranged media / PDF players and
download-all budgets, see [Media downloads](media-downloads.md).

## Charts as fragments

Install `hedron[charts]>=0.28.1,<0.29`, then return charts through the same declared
fragment regions used by `Metric` / `Table` / `DataTable`. See
[Charts and HTMX](charts-and-htmx.md) and
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

## Turn Explorer off in production

```python
app = Hedron(
    title="Prod",
    security="standard",
    session_secret="from-secret-store",
    explorer="off",
    production=True,
)
```

Or set `HEDRON_ENV=production`. Never ship `explorer="development"`.

## Multi-worker sessions

Use sticky sessions or an external session store. Do not assume in-memory session affinity.
Job backends that need Redis set `HEDRON_REDIS_URL` explicitly.

## Production start failure `HED-BUILD-0003`

```bash
hedron build
HEDRON_ENV=production uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

See [Deployment](deployment.md) · [Error codes](error-codes.md).

## Protect a route prefix

```python
from typing import Annotated

from fastapi import Depends, Request

from hedron import HedronRouter


def require_user(request: Request) -> str:
    ...


users = HedronRouter(prefix="/users", dependencies=[Depends(require_user)])
```

See [Authentication](authentication.md).
