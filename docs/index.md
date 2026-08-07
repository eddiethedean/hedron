---
hide:
  - navigation
  - toc
---

<div class="hedron-hero" markdown>

<div class="hedron-eyebrow">Python-first UI framework · v0.20.0</div>

# Build modern web UIs in Python.<br><span class="hedron-gradient-text">No Node.js required.</span>

Hedron turns typed Python components into server-rendered HTML with FastAPI and HTMX.
Build dashboards, admin tools, forms, and CRUD apps without a frontend build chain.
{ .hedron-lede }

Unlike Streamlit’s script-rerun model, Hedron returns typed components from FastAPI routes
and swaps HTML fragments with HTMX — no Node.js build step.
{ .hedron-lede }

**~5–10 minutes:** install → `hedron new` → open localhost:8000 → **Hello from hedron new** →
click **Refresh status** (the time updates).
{ .hedron-lede }

<div class="hedron-actions" markdown>
[Get started](getting-started/quickstart.md){ .md-button .md-button--primary }
[Try in Codespaces](examples/try-it.md){ .md-button }
[Why Hedron](guides/why-hedron.md){ .md-button }
</div>

<div class="hedron-signal-row">
  <span>Python 3.11–3.14</span>
  <span>FastAPI native</span>
  <span>No Node.js required</span>
</div>

</div>

## From zero to a rendered page

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first if you do not
have it (`curl -LsSf https://astral.sh/uv/install.sh | sh` on macOS/Linux).

```bash
uvx --from "hedron>=0.20.0,<0.21" hedron new my-hedron-app
cd my-hedron-app
uv sync
uv run uvicorn app:app --reload
```

!!! note "Install pin"

    Pin production installs with `hedron>=0.20.0,<0.21`. Prefer a clean virtualenv —
    Hedron requires FastAPI `>=0.141.1,<0.142` (see [troubleshooting](guides/troubleshooting.md)).

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). You should see **Hello from hedron new**.
Click **Refresh status** — the page updates without a full reload. Hedron returns a small
HTML fragment; [HTMX](https://htmx.org) swaps it into the declared region.

### Try it (simulated)

=== "Demo"

    Docs simulation — no live server. Click **Refresh status** to swap the fragment.

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

Extras and troubleshooting: [installation](getting-started/installation.md).

## A backend-native way to build UI

<div class="hedron-grid">
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">⌁</span>
    <strong>Typed composition</strong>
    <p>Compose pages from Python components and validated props. Your editor, type checker, and tests stay in the loop.</p>
  </div>
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">ϟ</span>
    <strong>FastAPI + HTMX</strong>
    <p>Return full pages or targeted fragments from ordinary routes. Keep dependency injection, OpenAPI, and async I/O.</p>
  </div>
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">◇</span>
    <strong>Secure-by-default boundaries</strong>
    <p>Contextual escaping, CSRF validation, safe URL types, and conservative cache behavior.</p>
  </div>
</div>

## Next steps

1. [Build your first app](getting-started/quickstart.md) — celebrate Refresh, then edit Hello
2. [HTMX interactions](guides/htmx-interactions.md)
3. [Minimal form POST](guides/minimal-form.md)
4. [Learning path](getting-started/learning-path.md)

<details markdown>
<summary>Package maturity and production pins</summary>

Hedron **0.20.0** is **Published** on PyPI/git (`v0.20.0`).
Pin production installs with `hedron>=0.20.0,<0.21`.
Package maturity is **Beta**; **Supported** means the capability works on this train when pinned
(not the same as API `stable`) — see [Understanding maturity labels](getting-started/how-to-read.md)
and [What’s ready today](guides/whats-ready.md).
Also: [Why Hedron](guides/why-hedron.md) · [Evaluate Hedron](guides/evaluate.md).
</details>

## Designed for inspectability

Hedron does not hide the web platform. It gives Python applications a typed component
model while preserving ordinary HTML, CSS, HTTP, and FastAPI boundaries. Automatic
choices (cache, Explorer, assets) are inspectable and overrideable; components become
HTTP endpoints only when you address them explicitly.

[Read the architecture](ARCHITECTURE.md) · [Runnable examples](examples/runnable.md) ·
[Public roadmap](guides/roadmap.md)
