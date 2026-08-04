---
hide:
  - navigation
  - toc
---

<div class="hedron-hero" markdown>

<div class="hedron-eyebrow">Python-first UI framework · 0.10.0 live interaction</div>

# Ship the interface.<br><span class="hedron-gradient-text">Keep the Python.</span>

Hedron turns typed Python components into secure, server-rendered applications with
FastAPI and HTMX. Build dashboards, admin tools, and CRUD workflows without adopting
a JavaScript application stack.
{ .hedron-lede }

<div class="hedron-actions" markdown>
[Build your first app](getting-started/quickstart.md){ .md-button .md-button--primary }
[Browse component gallery](examples/index.md){ .md-button }
</div>

<p class="hedron-lede" style="margin-top:0.5rem;font-size:0.95rem;opacity:0.85">
Gallery demos are simulated in the docs browser. Clone the
<a href="https://github.com/eddiethedean/hedron/tree/main/examples/reference-app">reference app</a>
to run a live Hedron server.
</p>

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
    <strong>Security by construction</strong>
    <p>Contextual escaping, CSRF validation, safe URL types, and conservative cache behavior are framework boundaries.</p>
  </div>
</div>

## From zero to a rendered page

=== "1 · Create a project"

    ```bash
    uv init my-hedron-app
    cd my-hedron-app
    uv add hedron "uvicorn[standard]"
    ```

    Or scaffold with the CLI: `hedron new my-hedron-app`. See
    [installation](getting-started/installation.md).

=== "2 · Create `app.py`"

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

=== "3 · Run"

    ```bash
    uv run uvicorn app:app --reload
    ```

    Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The same route can
    return an HTMX fragment when the request asks for one.

<div class="hedron-availability">
  <p><strong>Ready to try it?</strong><br>
  The flagship package includes pages, routing, security, state, CLI tooling,
  plugins, testing helpers, and optional charts / content extras.</p>
  <p><code>pip install hedron</code> ·
  <code>pip install "hedron[charts]"</code> ·
  <a href="getting-started/installation/">Install options →</a> ·
  <a href="examples/">Interactive demos →</a></p>
</div>

## Choose your path

<div class="hedron-path">
  <a href="getting-started/installation/">
    <strong>Start fresh</strong>
    Install Hedron and understand the package choices.
  </a>
  <a href="getting-started/core-concepts/">
    <strong>Learn the model</strong>
    See how apps, pages, components, rendering, and HTMX fit together.
  </a>
  <a href="getting-started/flask/">
    <strong>Flask adapter</strong>
    Render the same components on native Flask.
  </a>
  <a href="getting-started/django/">
    <strong>Django adapter</strong>
    Native Django URLconfs with CSRF alignment notes.
  </a>
  <a href="guides/htmx-interactions/">
    <strong>Add interaction</strong>
    Refresh declared regions with typed, validated HTMX responses.
  </a>
  <a href="guides/security/">
    <strong>Secure defaults</strong>
    CSRF, SafeUrl, Explorer, and host-framework notes.
  </a>
  <a href="guides/deployment/">
    <strong>Deploy</strong>
    Production secrets, ASGI/WSGI runners, and env vars.
  </a>
  <a href="guides/project-workflow/">
    <strong>Build with confidence</strong>
    Scaffold, inspect, check, test, and package a real project.
  </a>
</div>

## Designed for inspectability

Hedron does not hide the web platform. It gives Python applications a typed component
model while preserving ordinary HTML, CSS, HTTP, and FastAPI boundaries. Inference is
explainable, resources are explicitly addressable, and production builds are sealed and
reproducible.

[Read the architecture](ARCHITECTURE.md) · [See project status](STATUS.md) ·
[View the roadmap](ROADMAP.md)
