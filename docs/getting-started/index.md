# Learn Hedron

Build and run a small Hedron application, then continue through HTMX and forms.

## Path

1. [Build your first app](quickstart.md) — scaffold → Hello → Refresh → edit
2. [HTMX interactions](../guides/htmx-interactions.md) — extend the Refresh pattern
3. [Minimal form](../guides/minimal-form.md) — CSRF-safe POST
4. [Installation](installation.md) — extras, Flask/Django, common problems (as needed)
5. [Learning path](learning-path.md) — continue toward data, auth, and deploy

Help: [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md).

Then (when evaluating): [What’s ready](../guides/whats-ready.md) ·
[Why Hedron](../guides/why-hedron.md) · [Evaluate Hedron](../guides/evaluate.md)
(**Adopt** nav).

Maturity labels (Beta / Supported / Deferred) are explained under
[Understanding maturity labels](how-to-read.md) when you need them — you do not
need that vocabulary to install.

<div class="hedron-grid">
  <a class="hedron-card" href="quickstart/">
    <span class="hedron-card__icon" aria-hidden="true">01</span>
    <strong>1. First app</strong>
    <p>Scaffold, Hello, Refresh click, then edit a string.</p>
  </a>
  <a class="hedron-card" href="../guides/htmx-interactions/">
    <span class="hedron-card__icon" aria-hidden="true">02</span>
    <strong>2. HTMX</strong>
    <p>Extend the scaffold Refresh pattern with more regions.</p>
  </a>
  <a class="hedron-card" href="../guides/minimal-form/">
    <span class="hedron-card__icon" aria-hidden="true">03</span>
    <strong>3. Minimal form</strong>
    <p>CSRF-safe POST with a typed action.</p>
  </a>
  <a class="hedron-card" href="installation/">
    <span class="hedron-card__icon" aria-hidden="true">04</span>
    <strong>4. Installation hub</strong>
    <p>Extras, other hosts, and common install problems.</p>
  </a>
</div>

## Other hosts

- [Flask](flask.md) — `hedron-flask` (no FastAPI)
- [Django](django.md) — `hedron-django` (Django `>=5.2,<6`)

There is no `hedron new --flask` / `--django` yet. Codespaces path:
[Try with Codespaces](../examples/try-it.md).
