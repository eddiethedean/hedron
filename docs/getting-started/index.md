# Learn Hedron

**Goal (often ~5–10 minutes after Python + uv/pip are ready):** Hello + click
**Refresh status**. Then: HTMX second region → `/notes` form → pick one recipe
(auth or SQLite).

## Path

1. [Build your first app](quickstart.md) — scaffold → Hello → Refresh → edit
2. [Installation](installation.md) — extras, Flask/Django, common problems (as needed)
3. [HTMX interactions](../guides/htmx-interactions.md) — extend the Refresh pattern
4. [Minimal form](../guides/minimal-form.md) — CSRF-safe POST
5. [Learning path](learning-path.md) — continue toward data, auth, and deploy
6. [Core concepts](core-concepts.md) (optional after Hello works)

Help: [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md).
Optional packages (data, charts, Explorer, …): [Package catalog](../packages/index.md).

Evaluating production use later? [What’s ready](../guides/whats-ready.md) ·
[Why Hedron](../guides/why-hedron.md) · [Evaluate Hedron](../guides/evaluate.md).

<div class="hedron-grid">
  <a class="hedron-card" href="quickstart/">
    <span class="hedron-card__icon" aria-hidden="true">01</span>
    <strong>1. First app</strong>
    <p>Scaffold, Hello, Refresh click, then edit a string.</p>
  </a>
  <a class="hedron-card" href="installation/">
    <span class="hedron-card__icon" aria-hidden="true">02</span>
    <strong>2. Installation</strong>
    <p>Extras, adapters, and troubleshooting after Hello.</p>
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
  <a class="hedron-card" href="../examples/recipes/">
    <span class="hedron-card__icon" aria-hidden="true">06</span>
    <strong>Second hour — recipes</strong>
    <p>Notes + SQLAlchemy, session auth, upload, jobs poll.</p>
  </a>
</div>

## Other hosts

- [Flask](flask.md) — `hedron new --flask` then `hedron-flask` (no FastAPI)
- [Django](django.md) — `hedron new --django` then `hedron-django` (Django `>=5.2,<6`)
- [Plain FastAPI](../guides/plain-fastapi.md) — mount Hedron beside an existing FastAPI app

FastAPI remains the default `hedron new` path. Codespaces:
[Try with Codespaces](../examples/try-it.md).
