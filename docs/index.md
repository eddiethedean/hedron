---
hide:
  - navigation
  - toc
---

<div class="hedron-hero" markdown>

<div class="hedron-eyebrow">Python-first UI framework · v0.18.0</div>

# Build web UIs in Python.<br><span class="hedron-gradient-text">No Node.js required.</span>

Hedron turns typed Python components into server-rendered HTML with FastAPI and HTMX.
Build dashboards, admin tools, forms, and CRUD apps without a frontend build chain.
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
uvx --from "hedron>=0.18.0,<0.19" hedron new my-hedron-app
cd my-hedron-app
uv sync
uv run uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). You should see **Hello from hedron new**.
Click **Refresh status** — the page updates without a full reload. Hedron returns a small
HTML fragment; [HTMX](https://htmx.org) swaps it into the declared region.

<figure class="hedron-browser-sim" data-hedron-hello-refresh>
  <div class="hedron-browser-sim__chrome">
    <div class="hedron-browser-sim__titlebar">
      <div class="hedron-browser-sim__traffic" aria-hidden="true"><span></span><span></span><span></span></div>
      <div class="hedron-browser-sim__nav" aria-hidden="true">
        <span class="hedron-browser-sim__nav-btn">←</span>
        <span class="hedron-browser-sim__nav-btn">→</span>
        <span class="hedron-browser-sim__nav-btn hedron-browser-sim__nav-btn--keep">↻</span>
        <div class="hedron-browser-sim__url"><span>ⓘ</span><code>127.0.0.1:8000</code></div>
      </div>
    </div>
    <div class="hedron-browser-sim__viewport">
      <header class="hedron-browser-sim__brand">
        <img class="hedron-browser-sim__logo" src="assets/hedron-mark.svg" alt="" width="28" height="28" decoding="async" />
        <span class="hedron-browser-sim__wordmark">Hedron</span>
      </header>
      <div class="hedron-browser-sim__page">
        <h2 class="hedron-browser-sim__heading">Hello from hedron new</h2>
        <div class="hedron-browser-sim__status" id="service-status" role="status" aria-live="polite"><span class="hedron-browser-sim__status-icon" aria-hidden="true">✓</span><span data-hbs-stamp>All systems operational · refreshed --:--:-- UTC</span></div>
        <div class="hedron-browser-sim__actions">
          <button type="button" class="hedron-browser-sim__refresh" data-hbs-refresh hx-get="/status" hx-target="#service-status" hx-swap="outerHTML">Refresh status</button>
          <span class="hedron-browser-sim__hint" data-hbs-hint><span class="hedron-browser-sim__hint-arrow" aria-hidden="true">→</span> Click — timestamp updates</span>
        </div>
        <p class="hedron-browser-sim__trace" data-hbs-trace aria-live="polite"></p>
      </div>
    </div>
  </div>
  <figcaption class="hedron-browser-sim__caption">Docs simulation of <code>127.0.0.1:8000</code> — click <strong>Refresh status</strong> for an HTMX-style fragment swap (no server).</figcaption>
</figure>

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

Hedron **0.18** packages are **Beta** on PyPI — pin versions for production
(`hedron>=0.18.0,<0.19`). **Supported** means the capability works on the current train
when pinned; most public APIs remain compatibility level **`beta`** until listed in the
small **stable** table — see [Understanding maturity labels](getting-started/how-to-read.md).
Capability readiness: [What’s ready today](guides/whats-ready.md) ·
[Why Hedron](guides/why-hedron.md) · [Evaluate Hedron](guides/evaluate.md).
</details>

## Designed for inspectability

Hedron does not hide the web platform. It gives Python applications a typed component
model while preserving ordinary HTML, CSS, HTTP, and FastAPI boundaries. Automatic
choices (cache, Explorer, assets) are inspectable and overrideable; components become
HTTP endpoints only when you address them explicitly.

[Read the architecture](ARCHITECTURE.md) · [Runnable examples](examples/runnable.md) ·
[Public roadmap](guides/roadmap.md)
