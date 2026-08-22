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

    from hedron import Hedron, Page, Stack, Text, html

    app = Hedron(
        title="Hedron App",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
    )


    @app.refreshable("/status")
    def status():
        stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
        return html.div(
            Text(f"All systems operational · refreshed {stamp}"),
            role="status",
            aria={"live": "polite"},
        )


    @app.command(fallback="/")
    def ping():
        from hedron import refresh

        return refresh(status).toast("Refreshed")


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                Text("Hello from hedron new"),
                status(),
                status.refresh_button("Refresh status"),
                ping.button("Ping"),
            ),
            title="Home",
        )
    ```

Prefer `@app.screen` for new apps. Use explicit `Page` + `@app.page` only when you need
full `Page` constructor control — see the
[Hedron API](../api/HEDRON.md).

```bash
pip install "hedron>=0.58.0,<0.59" "uvicorn[standard]"
# paste the Code tab into app.py, then:
uvicorn app:app --reload
```

## Static Hello only (no Refresh)

Minimal page with **no** HTMX Refresh — use only if you want the smallest possible file.

```bash
pip install "hedron>=0.58.0,<0.59" "uvicorn[standard]"
```

Save as `app.py`:

```python
from hedron import Hedron, Text

app = Hedron(title="Demo", security="standard", session_secret="replace-me")


@app.screen("/", title="Demo")
def home():
    return Text("Hello, Hedron")
```

```bash
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## CSRF form

Prefer `@app.form_command` for typed forms (see [quickstart](../getting-started/quickstart.md)
CRUD scaffold). Follow the pasteable advanced form in
[Minimal form POST](../guides/minimal-form.md) when you need explicit `Form` / `CsrfField`.

## Live clock (polling)

Follow the pasteable app in [Live interaction](../guides/live-interaction.md)
(“poll a clock”).

## When you need the monorepo

Clone for Flask/Django reference apps, the team-admin reference app, and HDJ progressive
examples: [Runnable examples](runnable.md).
