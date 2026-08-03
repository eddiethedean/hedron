# Get started

Build and run a small Hedron application, then learn the few concepts that scale from a
single page to a production UI.

!!! info "Docs vs PyPI"

    These pages describe **0.4.0** on `main`. PyPI still serves **0.3.0**. The
    [installation](installation.md) matrix shows both paths. A hello-page on PyPI 0.3
    takes a few minutes; full CLI/`hedron.testing` need a 0.4 install.

## What you will build

The quickstart creates a FastAPI-native application with a typed page, server-rendered
components, Hedron's standard security profile, and a development server.

<div class="hedron-grid">
  <a class="hedron-card" href="installation/">
    <span class="hedron-card__icon" aria-hidden="true">01</span>
    <strong>1. Install</strong>
    <p>Choose the flagship framework or rendering-core package and set up a project.</p>
  </a>
  <a class="hedron-card" href="quickstart/">
    <span class="hedron-card__icon" aria-hidden="true">02</span>
    <strong>2. Build an app</strong>
    <p>Create a route, compose a page, run it locally, and verify fragment rendering.</p>
  </a>
  <a class="hedron-card" href="core-concepts/">
    <span class="hedron-card__icon" aria-hidden="true">03</span>
    <strong>3. Learn the model</strong>
    <p>Understand the contracts that keep routing, rendering, and interaction explicit.</p>
  </a>
</div>

## Prerequisites

- Python 3.11 through 3.14
- A Python package manager; examples use [uv](https://docs.astral.sh/uv/), with
  equivalent `pip` commands alongside it
- Familiarity with Python functions and basic HTML concepts

No Node.js installation or frontend build tool is required.

[Install Hedron :material-arrow-right:](installation.md){ .md-button .md-button--primary }
