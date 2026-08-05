---
hide:
  - navigation
  - toc
---

<div class="hedron-hero" markdown>

<div class="hedron-eyebrow">Python-first UI framework · v0.11.0</div>

# Ship the interface.<br><span class="hedron-gradient-text">Keep the Python.</span>

Hedron turns typed Python components into server-rendered HTML with FastAPI and HTMX.
Build dashboards, admin tools, and CRUD workflows without a Node.js frontend stack.
Escaping and CSRF profiles ship as Beta secure defaults — pin versions and read
[What’s ready](guides/whats-ready.md).
{ .hedron-lede }

<div class="hedron-actions" markdown>
[Install Hedron](getting-started/installation.md){ .md-button .md-button--primary }
[Build your first app](getting-started/quickstart.md){ .md-button }
[Try in Codespaces](examples/try-it.md){ .md-button }
</div>

<p class="hedron-lede" markdown>Evaluating production use? See
[What’s ready today](guides/whats-ready.md) · [Why Hedron](guides/why-hedron.md).</p>

<div class="hedron-signal-row">
  <span>Python 3.11–3.14</span>
  <span>FastAPI native</span>
  <span>Beta · pin versions</span>
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
    <strong>Secure-by-default boundaries</strong>
    <p>Contextual escaping, CSRF validation, safe URL types, and conservative cache behavior — Beta package maturity; pin versions.</p>
  </div>
</div>

## From zero to a rendered page

**Recommended:** use the CLI scaffold. Do not also hand-write a second `app.py`.

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install "hedron>=0.11.0" "uvicorn[standard]"
python -m hedron new my-hedron-app
cd my-hedron-app
python -m pip install -e .
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). You should see **Hello from hedron new**.
Prefer [uv](https://docs.astral.sh/uv/)? Full steps:
[installation](getting-started/installation.md).

**Manual single-file (not using `hedron new`):** create a project directory, save
`app.py` from the [single-file examples](examples/single-file.md), install
`hedron>=0.11.0` and `uvicorn[standard]`, then run `uvicorn app:app --reload`.

## Next steps

1. [HTMX interactions](guides/htmx-interactions.md)
2. [Minimal form](guides/minimal-form.md)
3. [Learning path](getting-started/learning-path.md)

Then: [Try with Codespaces](examples/try-it.md) · [runnable examples](examples/runnable.md) ·
[What's ready](guides/whats-ready.md) · [Evaluate Hedron](guides/evaluate.md)

## Designed for inspectability

Hedron does not hide the web platform. It gives Python applications a typed component
model while preserving ordinary HTML, CSS, HTTP, and FastAPI boundaries. Automatic
choices (cache, Explorer, assets) are inspectable and overrideable; components become
HTTP endpoints only when you address them explicitly.

[Read the architecture](ARCHITECTURE.md) · [What's ready today](guides/whats-ready.md) ·
[Public roadmap](guides/roadmap.md)
