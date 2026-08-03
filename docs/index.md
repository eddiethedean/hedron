---
hide:
  - navigation
  - toc
---

<div class="hedron-hero" markdown>

<div class="hedron-eyebrow">Python-first UI framework · v0.4</div>

# Ship the interface.<br><span class="hedron-gradient-text">Keep the Python.</span>

Hedron turns typed Python components into secure, server-rendered applications with
FastAPI and HTMX. Build dashboards, admin tools, and CRUD workflows without adopting
a JavaScript application stack.
{ .hedron-lede }

<div class="hedron-actions" markdown>
[Build your first app](getting-started/quickstart.md){ .md-button .md-button--primary }
[Try the live examples](examples/index.md){ .md-button }
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
    <strong>Security by construction</strong>
    <p>Contextual escaping, CSRF validation, safe URL types, and conservative cache behavior are framework boundaries.</p>
  </div>
</div>

## From zero to a rendered page

=== "1 · Install"

    ```bash
    uv add hedron
    ```

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
  <p><strong>Ready to try it?</strong><br>The flagship package includes pages, routing, security, state, CLI tooling, and testing helpers.</p>
  <p><code>pip install hedron</code> · <a href="examples/">Open interactive examples →</a></p>
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
