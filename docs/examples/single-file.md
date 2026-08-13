# Single-file apps (pip evaluators)

Run these without cloning the monorepo. Requires Python 3.11+ and a working network for
`pip install`. Prefer [Build your first app](../getting-started/quickstart.md)
(`hedron new`) for the interactive Hello + Refresh first-hour path.

## Hello + Refresh (recommended)

Same scaffold as `hedron new` — includes HTMX Refresh.

=== "Demo"

    Docs simulation — click Refresh status for an HTMX-style fragment swap (no server).

    <!-- hedron-sim:hello-refresh -->

=== "Code"

    What `hedron new` writes as `app.py` (the real app, not the docs simulator):

    ```python title="app.py"
    import os
    from datetime import UTC, datetime

    from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

    app = Hedron(
        title="Hedron App",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
    )

    status = app.region("service-status", description="Live status panel")


    def status_panel():
        stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
        return html.div(
            Text(f"All systems operational · refreshed {stamp}"),
            id=status.id,
            role="status",
            aria={"live": "polite"},
        )


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

```bash
pip install "hedron>=0.34.0,<0.35" "uvicorn[standard]"
# paste the Code tab into app.py, then:
uvicorn app:app --reload
```

## Static Hello only (no Refresh)

Minimal page with **no** HTMX Refresh — use only if you want the smallest possible file.

```bash
pip install "hedron>=0.34.0,<0.35" "uvicorn[standard]"
```

Save as `app.py`:

```python
from hedron import Hedron, Page, Text

app = Hedron(title="Demo", security="standard", session_secret="replace-me")


@app.page("/")
def home() -> Page:
    return Page(Text("Hello, Hedron"), title="Demo")
```

```bash
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## CSRF form

Follow the pasteable app in [Minimal form POST](../guides/minimal-form.md).

## Live clock (polling)

Follow the pasteable app in [Live interaction](../guides/live-interaction.md)
(“poll a clock”).

## When you need the monorepo

Clone for Flask/Django reference apps, the team-admin reference app, and HDJ progressive
examples: [Runnable examples](runnable.md).
