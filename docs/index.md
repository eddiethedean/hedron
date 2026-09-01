---
description: Build production-minded, server-rendered Python interfaces on FastAPI with Hedron.
hide:
  - navigation
  - toc
search:
  boost: 2
---

<div class="hedron-hero" markdown>

<img class="hedron-theme-wordmark" src="assets/hedron-logo-light.svg" alt="Hedron">

<div class="hedron-eyebrow">FastAPI-native Python UI · stable 1.0 · Python 3.10–3.14</div>

# Build the interface in Python. Keep the web architecture.

Hedron gives FastAPI applications server-rendered components, explicit interactions,
and production-minded boundaries—without introducing a separate frontend project.
{ .hedron-lede }

<div class="hedron-actions" markdown>
[Build your first app](getting-started/quickstart.md){ .md-button .md-button--primary }
[See the showcase](examples/showcase.md){ .md-button }
[Evaluate Hedron](guides/evaluate.md){ .md-button }
</div>

Composable interfaces. Typed routes. Ordinary HTTP. One Python application.
{ .hedron-proof }

<div class="hedron-signal-row">
  <span>FastAPI native</span>
  <span>HTML over the wire</span>
  <span>HTMX + Alpine</span>
  <span>Strict core typing</span>
</div>

<div class="hedron-choice-grid">
  <a class="hedron-choice" href="getting-started/quickstart/">
    <span>Starting a Python application</span>
    <strong>Scaffold a working Hedron app.</strong>
    <p>Go from an empty directory to a typed page and refreshable region in about ten minutes.</p>
  </a>
  <a class="hedron-choice" href="guides/plain-fastapi/">
    <span>Already using FastAPI</span>
    <strong>Add UI without replacing your app.</strong>
    <p>Keep dependencies, middleware, lifespan, JSON routes, and OpenAPI beside Hedron pages.</p>
  </a>
</div>

<div class="hedron-quickstart-label">Create a Hedron app in about 10 minutes</div>

```bash
# Need uv? https://docs.astral.sh/uv/
uvx --from "hedron>=1.0.0" hedron new my-app
cd my-app && uv sync && uv run hedron run app:app --reload
# Open http://127.0.0.1:8000
```

Release status: [Current release and support](guides/current-release.md). Pins and extras:
[Installation](getting-started/installation.md). Before production:
[What’s ready](guides/whats-ready.md).

<!-- hedron-release-status -->

![Hello from Hedron with Refresh status](assets/hello-refresh.jpg){ .hedron-hero-shot }

</div>

## Start from where you are

Every primary route in these docs leads through Hedron's public API.

<div class="hedron-path">
  <a href="getting-started/quickstart/">
    <strong>Build a new application</strong>
    Scaffold the FastAPI runtime, a page, and a refreshable view.
  </a>
  <a href="guides/plain-fastapi/">
    <strong>Extend an existing FastAPI app</strong>
    Include Hedron routes and static assets beside the API you already operate.
  </a>
  <a href="guides/streamlit-migration/">
    <strong>Move beyond Streamlit</strong>
    Translate reruns and session state into explicit routes, state, and interactions.
  </a>
  <a href="getting-started/installation/#other-hosts">
    <strong>Use Flask or Django</strong>
    Adopt the same component model through a first-party host adapter.
  </a>
  <a href="guides/evaluate/">
    <strong>Evaluate for production</strong>
    Review maturity, security, ownership, deployment, and upgrade expectations.
  </a>
</div>

Need a focused pattern? Open the [Cookbook](guides/cookbook.md). Diagnosing a failure?
Start with [Troubleshooting](guides/troubleshooting.md). Building with an AI coding agent?
Give it the [Hedron field guide for coding agents](getting-started/coding-agents.md).

### Prefer a higher-level authoring facade?

[Take the alternate Edron route](getting-started/edron-quickstart.md){ .md-button }

## One application, explicit responsibilities

<div class="hedron-grid">
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">ϟ</span>
    <strong>FastAPI-native foundation</strong>
    <p>Keep dependency injection, OpenAPI, async I/O, middleware, lifespan, and ordinary routes.</p>
  </div>
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">⌁</span>
    <strong>Composable Python UI</strong>
    <p>Build screens from reusable components and validated props with editor and type-checker support.</p>
  </div>
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">↔</span>
    <strong>Server-driven interaction</strong>
    <p>Use HTMX for bounded requests and swaps, Alpine for local presentation state, and HTTP fallbacks.</p>
  </div>
  <div class="hedron-card">
    <span class="hedron-card__icon" aria-hidden="true">◇</span>
    <strong>Production-minded boundaries</strong>
    <p>Rely on contextual escaping, CSRF validation, safe URL types, bounded state, and explicit ownership.</p>
  </div>
</div>

## From first page to production

1. [Build your first app](getting-started/quickstart.md)
2. [Understand the component and request model](getting-started/core-concepts.md)
3. [Add an HTMX interaction](guides/htmx-interactions.md)
4. [Post a CSRF-protected form](guides/minimal-form.md)
5. [Continue through the learning path](getting-started/learning-path.md)
6. [Ship with the production checklist](guides/ship.md)

Already building? Use [API by task](api/by-task.md) to move from an outcome to the right
symbol, or browse the [runnable examples](examples/runnable.md).

<details markdown>
<summary>Release, typing, and maturity</summary>

Hedron **1.0.4** is published on PyPI. Require applications to use `hedron>=1.0.0` and
review capability-specific maturity before production adoption. The `hedron-core` renderer
and `hedron` FastAPI runtime are Pyright-strict; type errors block release.

Stable core packages and independently versioned satellites do not share one maturity claim.
Use [Current release and support](guides/current-release.md),
[What’s ready](guides/whats-ready.md), and [Compatibility](COMPATIBILITY.md) as the authority.
</details>

## Designed for inspectability

Hedron does not hide the web platform. Components render ordinary HTML; interactions remain
ordinary HTTP; FastAPI stays available underneath. Automatic choices around assets, caches,
and diagnostics are inspectable and overrideable, and a component becomes an endpoint only
when you address it explicitly.

[Read the architecture](ARCHITECTURE.md) · [Explore the API](api/HEDRON.md) ·
[See what’s next](guides/whats-next.md)
