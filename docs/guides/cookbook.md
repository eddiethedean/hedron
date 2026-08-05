# Cookbook

Short, pasteable recipes. Prefer the linked guides when you need full context.

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

```python
from hedron import FragmentRegion, Hedron, InteractionResult, Page, RefreshButton, Text, html

app = Hedron(title="Status", security="standard", session_secret="replace-me")
REGION = FragmentRegion(id="panel", selector="#panel", description="Status panel")


def panel():
    return html.div(Text("ok"), id=REGION.id)


@app.page("/")
def home() -> Page:
    return Page(
        html.div(
            panel(),
            RefreshButton("Refresh", href="/panel", target=REGION.selector, swap="outerHTML"),
        ),
        title="Status",
    )


@app.component("/panel", fragment_regions=(REGION,))
def refresh() -> InteractionResult:
    return InteractionResult(content=panel(), region_id=REGION.id, explanation="Refresh panel")
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

## Polling

```python
from hedron import ComponentRef, FragmentRegion, Hedron, InteractionResult, Page, Poll, Text

app = Hedron(title="Poll", security="standard", session_secret="replace-me")
REGION = FragmentRegion(id="tick", selector="#tick", description="Ticker")
REF = ComponentRef(logical_id="tick", path="/tick", target="#tick")


@app.component("/tick", fragment_regions=(REGION,))
def tick() -> InteractionResult:
    return InteractionResult(content=Text("tick"), region_id=REGION.id, explanation="Tick")


@app.page("/")
def home() -> Page:
    return Page(
        Poll(ref=REF, interval_ms=2000, target_id=REGION.id, content=Text("…")),
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
([utility components](../api/UTILITY_COMPONENTS.md)).

## Charts as fragments

Install `hedron[charts]` (+ backend extra). Follow [Charts and HTMX](charts-and-htmx.md).

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
