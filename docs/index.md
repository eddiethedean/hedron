---
hide:
  - navigation
  - toc
---

<div class="hedron-hero" markdown>

<div class="hedron-eyebrow">Python-first UI framework · v0.10.0</div>

# Ship the interface.<br><span class="hedron-gradient-text">Keep the Python.</span>

Hedron turns typed Python components into secure, server-rendered applications with
FastAPI and HTMX. Build dashboards, admin tools, and CRUD workflows without adopting
a JavaScript application stack.
{ .hedron-lede }

<div class="hedron-actions" markdown>
[Install Hedron](getting-started/installation.md){ .md-button .md-button--primary }
[Build your first app](getting-started/quickstart.md){ .md-button }
[What's ready](guides/whats-ready.md){ .md-button }
</div>

<div class="hedron-signal-row">
  <span>Python 3.11–3.14</span>
  <span>FastAPI native</span>
  <span>Secure defaults</span>
  <span>No Node.js required</span>
</div>

</div>

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
    <strong>Secure defaults</strong>
    <p>Contextual escaping, CSRF validation, safe URL types, and conservative cache behavior are framework boundaries.</p>
  </div>
</div>

## From zero to a rendered page

Pick **one** path — scaffold (recommended) or a hand-written `app.py`. Do not follow both.

=== "Scaffold (recommended)"

    ```bash
    pip install "hedron>=0.10.0" "uvicorn[standard]"
    hedron new my-hedron-app
    cd my-hedron-app
    pip install -e .   # or: uv sync
    uvicorn app:app --reload
    ```

    Open [http://127.0.0.1:8000](http://127.0.0.1:8000). You should see the scaffold home
    page. The scaffold already includes `app.py` — do not recreate it. Prefer
    [uv](https://docs.astral.sh/uv/)? See [installation](getting-started/installation.md).

=== "Manual `app.py`"

    Use this only if you are **not** using `hedron new`.

    ```python
    from hedron import Card, Heading, Hedron, Page, Stack, Text

    app = Hedron(
        title="Acme Console",
        security="standard",
        session_secret="replace-in-production",
    )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                Heading("Acme Console", level=1),
                Card(Text("Your first typed, server-rendered page.")),
            ),
            title="Home",
        )
    ```

    ```bash
    pip install "hedron>=0.10.0" "uvicorn[standard]"
    uvicorn app:app --reload
    ```

    Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Next steps

1. [Installation](getting-started/installation.md)
2. [Build your first app](getting-started/quickstart.md)
3. [HTMX interactions](guides/htmx-interactions.md)
4. [Minimal form](guides/minimal-form.md)
5. [Learning path](getting-started/learning-path.md)

Then: [runnable examples](examples/runnable.md) · [What's ready](guides/whats-ready.md) ·
[Why Hedron](guides/why-hedron.md) · [Evaluate Hedron](guides/evaluate.md)

## Designed for inspectability

Hedron does not hide the web platform. It gives Python applications a typed component
model while preserving ordinary HTML, CSS, HTTP, and FastAPI boundaries. Automatic
choices (cache, Explorer, assets) are inspectable and overrideable; components become
HTTP endpoints only when you address them explicitly.

[Read the architecture](ARCHITECTURE.md) · [What's ready today](guides/whats-ready.md) ·
[Public roadmap](guides/roadmap.md)
