# Get started

Build and run a small Hedron application, then continue through HTMX and forms.

## Path

1. [Install](installation.md) — `pip install "hedron>=0.10.1"` (and uvicorn)
2. [Build your first app](quickstart.md) — scaffold or manual page, then run and verify
3. [HTMX interactions](../guides/htmx-interactions.md) — refresh a declared region in the browser
4. [Minimal form](../guides/minimal-form.md) — CSRF-safe POST
5. [Learning path](learning-path.md) — continue toward data, auth, and deploy

Then: [What’s ready](../guides/whats-ready.md) · [Why Hedron](../guides/why-hedron.md) ·
[Evaluate Hedron](../guides/evaluate.md).

Maturity labels (Beta / Supported / Deferred) are explained under
[Decide → Understanding maturity labels](how-to-read.md) when you need them — you do not
need that vocabulary to install.

<div class="hedron-grid">
  <a class="hedron-card" href="installation/">
    <span class="hedron-card__icon" aria-hidden="true">01</span>
    <strong>1. Install</strong>
    <p>Minimum flagship install, then optional extras when you need them.</p>
  </a>
  <a class="hedron-card" href="quickstart/">
    <span class="hedron-card__icon" aria-hidden="true">02</span>
    <strong>2. First app</strong>
    <p>Run the scaffold (or a manual page), open the browser, and verify fragment rendering.</p>
  </a>
  <a class="hedron-card" href="../guides/htmx-interactions/">
    <span class="hedron-card__icon" aria-hidden="true">03</span>
    <strong>3. HTMX</strong>
    <p>Refresh a declared region with a button click — the first interactive win.</p>
  </a>
  <a class="hedron-card" href="../guides/minimal-form/">
    <span class="hedron-card__icon" aria-hidden="true">04</span>
    <strong>4. Minimal form</strong>
    <p>CSRF-safe classic form POST — golden path step 4.</p>
  </a>
  <a class="hedron-card" href="learning-path/">
    <span class="hedron-card__icon" aria-hidden="true">05</span>
    <strong>5. Learning path</strong>
    <p>What to read next after your first interactive pages.</p>
  </a>
</div>

## Prerequisites

- Python 3.11 through 3.14
- A Python package manager; examples use [uv](https://docs.astral.sh/uv/), with
  equivalent `pip` commands alongside it
- Familiarity with Python functions and basic HTML concepts

No Node.js installation or frontend build tool is required.

[Install Hedron :material-arrow-right:](installation.md){ .md-button .md-button--primary }
