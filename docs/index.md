---
hide:
  - navigation
  - toc
---

<div class="hedron-hero" markdown>

<div class="hedron-eyebrow">Python · FastAPI · HTMX · PyPI 0.48.0</div>

# Build interactive web apps in Python.

Routes return components; HTMX updates the page — no Node build, no full-script rerun.
{ .hedron-lede }

**In about 10 minutes after Python 3.11+ and uv or pip:** install → `hedron new` →
open localhost:8000 → click **Refresh status**.
{ .hedron-lede }

**Published in-tree `v0.49.0`.** Git tag and PyPI upload are **deferred**.
In-tree pin `hedron>=0.49.0,<0.50`. The latest on **PyPI** is **`0.48.0`**. Before production, see
[What’s ready](guides/whats-ready.md).
{ .hedron-lede }

<div class="hedron-actions" markdown>
[Get started](getting-started/quickstart.md){ .md-button .md-button--primary }
[Why Hedron](guides/why-hedron.md){ .md-button }
[Evaluate](guides/evaluate.md){ .md-button }
</div>

<div class="hedron-signal-row">
  <span>Python 3.11–3.14</span>
  <span>FastAPI + HTMX</span>
  <span>No Node build</span>
</div>

</div>

## Start here

[Build your first app (~10 minutes)](getting-started/quickstart.md) — the only full
Hello walkthrough (scaffold, Refresh, edit).

Hedron is for FastAPI teams who want typed components and HTMX fragment regions
without assembling a hand-rolled Jinja stack. Prefer Streamlit for notebook-style
rerun dashboards.

**You only need the `hedron` package** (+ uvicorn). Optional adapters and extras:
[Installation](getting-started/installation.md).

| Your starting point | Best next page |
|---|---|
| New Python/FastAPI app | [Build your first app](getting-started/quickstart.md) |
| Existing FastAPI app | [Add Hedron to FastAPI](guides/plain-fastapi.md) |
| Flask or Django project | [Choose a host](getting-started/index.md#choose-your-path) |
| Streamlit application | [Migration center](guides/streamlit-migration.md) |
| Production evaluation | [Evaluate Hedron](guides/evaluate.md) |

## A backend-native way to build UI

<div class="hedron-grid">
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">ϟ</span>
    <strong>FastAPI + HTMX</strong>
    <p>Return full pages or targeted fragments from ordinary routes. Keep dependency injection, OpenAPI, and async I/O.</p>
  </div>
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">⌁</span>
    <strong>Typed composition</strong>
    <p>Compose pages from Python components and validated props. Your editor, type checker, and tests stay in the loop.</p>
  </div>
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">◇</span>
    <strong>Secure-by-default boundaries</strong>
    <p>Contextual escaping, CSRF validation, safe URL types, and conservative cache behavior.</p>
  </div>
  <a class="hedron-card" href="guides/streamlit-migration/">
    <span class="hedron-card__icon" aria-hidden="true">→</span>
    <strong>Migrate from Streamlit</strong>
    <p>Convert one workflow, redesign state safely, map components, test, and cut over.</p>
  </a>
</div>

## Next steps

1. [Build your first app](getting-started/quickstart.md) — celebrate Refresh, then edit Hello
2. [What is HTMX?](getting-started/what-is-htmx.md) — understand regions and HTML swaps
3. [HTMX interactions](guides/htmx-interactions.md) — add a second region
4. [Minimal form POST](guides/minimal-form.md) — form updates the notes counter
5. [Learning path](getting-started/learning-path.md)

<details markdown>
<summary>Package maturity and production pins</summary>

Hedron’s flagship and host-adapter packages are Beta. Pin `hedron>=0.49.0,<0.50`.
Capability readiness and API compatibility are separate: read
[Maturity labels](getting-started/how-to-read.md) before interpreting Supported,
Experimental, `stable`, or `beta`. For production adoption, continue with
[What’s ready](guides/whats-ready.md) and [Evaluate Hedron](guides/evaluate.md).
</details>

## What you get (after Hello)

Typed pages and HTMX fragment regions on FastAPI, with CSRF profiles, dependency
injection, and multi-worker job status — without assembling a hand-rolled Jinja+HTMX
stack. See [Architecture](ARCHITECTURE.md).

## Designed for inspectability

Hedron does not hide the web platform. It gives Python applications a typed component
model while preserving ordinary HTML, CSS, HTTP, and FastAPI boundaries. Automatic
choices (cache, Explorer, assets) are inspectable and overrideable; components become
HTTP endpoints only when you address them explicitly.

[Read the architecture](ARCHITECTURE.md) · [Runnable examples](examples/runnable.md) ·
[What’s next](guides/whats-next.md)
