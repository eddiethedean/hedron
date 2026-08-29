---
description: Build server-rendered Python applications with FastAPI and HTMX—without a frontend build chain.
hide:
  - navigation
  - toc
search:
  boost: 2
---

<div class="hedron-hero" markdown>

<div class="hedron-eyebrow">Python-first application platform · stable 1.0 · Python 3.10–3.14</div>

# Stay in Python. Build the whole application.

Move with the speed of Streamlit. Get the structure and composability teams reach for
React to provide—without creating a separate frontend stack.
{ .hedron-lede }

<div class="hedron-actions" markdown>
[Choose your layer](getting-started/choose-layer.md){ .md-button .md-button--primary }
[Migrate from Streamlit](guides/streamlit-migration.md){ .md-button }
[Evaluate Hedron](guides/evaluate.md){ .md-button }
</div>

Composable interfaces. Explicit interactions. Production-minded application architecture.
All in Python.
{ .hedron-proof }

<div class="hedron-signal-row">
  <span>Python UI</span>
  <span>FastAPI foundation</span>
  <span>Server-driven interactions</span>
  <span>Strict core typing</span>
</div>

The `hedron-core` renderer and `hedron` FastAPI runtime are Pyright-strict. Type errors block
release; warning-level cleanup is tracked as a separate migration until the existing workspace
backlog is retired.

<div class="hedron-choice-grid">
  <a class="hedron-choice" href="guides/streamlit-migration/">
    <span>Coming from Streamlit</span>
    <strong>Keep Python. Gain application structure.</strong>
    <p>Move one workflow at a time from script reruns to explicit state, actions, and routes.</p>
  </a>
  <a class="hedron-choice" href="guides/why-hedron/">
    <span>Considering React</span>
    <strong>Keep composability. Skip the split stack.</strong>
    <p>Build reusable interfaces without creating a second frontend application and toolchain.</p>
  </a>
</div>

<div class="hedron-quickstart-label">Create an Edron app in about 5 minutes</div>

About five minutes after Python 3.10+ and uv are ready:

```bash
# Need uv? https://docs.astral.sh/uv/
uvx --from "edron>=0.9.0,<0.10" edron new my-app --template minimal
cd my-app && uv sync && uv run edron run app:app --reload
# Open http://127.0.0.1:8000
```

Release status: [Current release and support](guides/current-release.md). Pins and extras:
[Installation](getting-started/installation.md). Before production:
[What’s ready](guides/whats-ready.md).

<!-- hedron-release-status -->

![Hello from Hedron with Refresh status](assets/hello-refresh.jpg){ .hedron-hero-shot }

</div>

## Choose your starting point

Start with the authoring layer that matches the application you have today.

<div class="hedron-path">
  <a href="getting-started/edron-quickstart/">
    <strong>Start a complete application with Edron</strong>
    Scaffold a page-oriented dashboard, CRUD app, or data workflow.
  </a>
  <a href="getting-started/quickstart/">
    <strong>Use Hedron directly</strong>
    Compose components and FastAPI-native page, view, and action routes.
  </a>
  <a href="guides/streamlit-migration/">
    <strong>Move beyond Streamlit</strong>
    Check fit, map state, convert a workflow, and plan an incremental cutover.
  </a>
  <a href="guides/plain-fastapi/">
    <strong>Add Hedron to FastAPI</strong>
    Mount Python pages and interactions beside routes you already operate.
  </a>
  <a href="guides/evaluate/">
    <strong>Evaluate for production</strong>
    Review maturity, security, ownership, deployment, and upgrade expectations.
  </a>
</div>

Using Flask, Django, VS Code, or Posit Workbench? [Choose your host and environment](getting-started/index.md#choose-your-path).
Need a focused pattern or fix? Open the [Cookbook](guides/cookbook.md) or [Troubleshooting](guides/troubleshooting.md).

## Python velocity, application architecture

<div class="hedron-grid">
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">ϟ</span>
    <strong>FastAPI-native foundation</strong>
    <p>Keep dependency injection, OpenAPI, async I/O, ordinary routes, and explicit request boundaries.</p>
  </div>
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">⌁</span>
    <strong>Composable Python UI</strong>
    <p>Build screens from reusable components and validated props. Your editor, type checker, and tests stay in the loop.</p>
  </div>
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">◇</span>
    <strong>Production-minded boundaries</strong>
    <p>Contextual escaping, CSRF validation, safe URL types, and conservative cache behavior.</p>
  </div>
  <a class="hedron-card" href="guides/streamlit-migration/">
    <span class="hedron-card__icon" aria-hidden="true">→</span>
    <strong>Grow without a rewrite</strong>
    <p>Convert one Streamlit workflow at a time or start with a structure designed to grow from day one.</p>
  </a>
</div>

## Next steps

1. [Choose Edron or Hedron](getting-started/choose-layer.md)
2. [Build your first Edron app](getting-started/edron-quickstart.md) or
   [first Hedron app](getting-started/quickstart.md)
3. [What is HTMX?](getting-started/what-is-htmx.md) — understand regions and HTML swaps
4. [Minimal form POST](guides/minimal-form.md) — submit data across an explicit boundary
5. [Learning path](getting-started/learning-path.md)

Already building? Jump to the [Cookbook](guides/cookbook.md) for focused snippets or
[Troubleshooting](guides/troubleshooting.md) for symptom-first fixes.

<details markdown>
<summary>Package maturity and production pins</summary>

Hedron **1.0.0** is the in-tree release candidate; its Git tag and PyPI upload are deferred.
PyPI currently resolves Hedron `0.67.0` and Edron `0.9.0`. Edron remains a Beta satellite on
the future version line.
Pin applications to `>=0.67.0,<0.68` until the 1.0 cut is published, then review
capability-specific maturity before production adoption: [What’s ready](guides/whats-ready.md) and
[Evaluate Hedron](guides/evaluate.md).
</details>

## What you get (after Hello)

Python pages and HTMX fragment regions on FastAPI, with CSRF profiles, dependency
injection, and multi-worker job status — without assembling a hand-rolled Jinja+HTMX
stack. See [Architecture](ARCHITECTURE.md).

## Designed for inspectability

Hedron does not hide the web platform. It gives Python applications a component
model while preserving ordinary HTML, CSS, HTTP, and FastAPI boundaries. Automatic
choices (cache, Explorer, assets) are inspectable and overrideable; components become
HTTP endpoints only when you address them explicitly.

[Read the architecture](ARCHITECTURE.md) · [Runnable examples](examples/runnable.md) ·
[What’s next](guides/whats-next.md)
