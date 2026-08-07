# Learn Hedron

**Goal in 10 minutes:** Hello + click **Refresh status**. Ignore Beta/Supported labels
until that works. Then: HTMX second region → `/notes` form → pick one recipe (auth or
SQLite).

## Path

1. [Installation](installation.md) — prerequisites, extras, common problems (as needed)
2. [Build your first app](quickstart.md) — scaffold → Hello → Refresh → edit
3. [Core concepts](core-concepts.md) (optional) · [Maturity labels](how-to-read.md)
4. [HTMX interactions](../guides/htmx-interactions.md) — extend the Refresh pattern
5. [Minimal form](../guides/minimal-form.md) — CSRF-safe POST
6. [Learning path](learning-path.md) — continue toward data, auth, and deploy

Help: [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md).

Evaluating production use later? [What’s ready](../guides/whats-ready.md) ·
[Why Hedron](../guides/why-hedron.md) · [Evaluate Hedron](../guides/evaluate.md).

<div class="hedron-grid">
  <a class="hedron-card" href="installation/">
    <span class="hedron-card__icon" aria-hidden="true">01</span>
    <strong>1. Installation</strong>
    <p>Prerequisites, extras, and troubleshooting before you scaffold.</p>
  </a>
  <a class="hedron-card" href="quickstart/">
    <span class="hedron-card__icon" aria-hidden="true">02</span>
    <strong>2. First app</strong>
    <p>Scaffold, Hello, Refresh click, then edit a string.</p>
  </a>
  <a class="hedron-card" href="../guides/htmx-interactions/">
    <span class="hedron-card__icon" aria-hidden="true">03</span>
    <strong>3. HTMX</strong>
    <p>Extend the scaffold Refresh pattern with more regions.</p>
  </a>
  <a class="hedron-card" href="../guides/minimal-form/">
    <span class="hedron-card__icon" aria-hidden="true">04</span>
    <strong>4. Minimal form</strong>
    <p>CSRF-safe POST with a typed action.</p>
  </a>
  <a class="hedron-card" href="learning-path/">
    <span class="hedron-card__icon" aria-hidden="true">05</span>
    <strong>5. Learning path</strong>
    <p>Data, auth, deploy, and optional evaluator reading.</p>
  </a>
</div>

## Other hosts

- [Flask](flask.md) — `hedron-flask` (no FastAPI)
- [Django](django.md) — `hedron-django` (Django `>=5.2,<6`)

There is no `hedron new --flask` / `--django` yet. Codespaces path:
[Try with Codespaces](../examples/try-it.md).
