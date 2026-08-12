# Learning path

A suggested order from first page to production-minded apps. Start with
[Build your first app](quickstart.md), then [What is HTMX?](what-is-htmx.md). Use
[Installation](installation.md) when you need prerequisites, adapter choices, or
troubleshooting.

**Skills assumed:** Python 3.11+, basic FastAPI (routes / `Form`), and HTML forms.
No SPA or prior HTMX background is required.

Coming from Streamlit? Keep this foundation, then use the
[Streamlit migration center](../guides/streamlit-migration.md) to translate reruns,
Session State, caching, components, tests, and deployment.

## 1. Hello page (~10 minutes)

1. [Build your first app](quickstart.md)
2. [Installation](installation.md) (extras / troubleshooting as needed)
3. [What is HTMX?](what-is-htmx.md) — browser / fragment / region / swap mental model
4. Optional later (evaluators only): [Maturity labels](how-to-read.md)

That is the first success. Extend the **same** app in the next section; do not start a
second project.

## 2. First interaction (~20–30 minutes)

1. [HTMX interactions](../guides/htmx-interactions.md) — GET refresh into a region
   (edit the scaffold; browser click)
2. [Minimal form POST](../guides/minimal-form.md) — `CsrfField` form that increments
   the notes counter (same scaffold)

Then read [Core concepts](core-concepts.md) if you want the page/fragment model explained
(optional — skip until after a working form if you prefer).

## 3. Interact without a SPA (next hour)

1. [Mutations](../guides/mutations.md) — `@action` vs `@component` POST
2. [Forms and actions](../guides/forms-and-actions.md) — validation fragments and HTMX POST
3. [Security](../guides/security.md) — CSRF profiles and headers
4. Optional: open `/hedron-explorer/` with `hedron[dev]` and `explorer="development"`

## 4. Pick your host

| If you… | Read |
|---|---|
| Stay on FastAPI | Continue with guides below |
| Use Flask | [Add to an existing Flask app](flask.md) |
| Use Django | [Add to an existing Django project](django.md) |
| Prefer Jinja/HTML templates | [HDJ authoring](../guides/hdj-authoring.md) + `hedron[jinja]` |

## 5. Internal admin path, then data / live updates

**Recommended second hour:** [Session auth](../examples/session-auth.md) →
[Notes + SQLAlchemy](../examples/notes-sqlalchemy.md) →
[Ship a Hedron app](../guides/ship.md). The
[reference app](../examples/reference-app.md) is an optional kitchen sink after that.

1. [Data applications](../guides/data-apps.md) / [Charts and HTMX](../guides/charts-and-htmx.md)
   (`hedron[charts]>=0.31.0,<0.32`; static Matplotlib is the conservative default)
2. More recipes: [File upload](../examples/file-upload.md) ·
   [Jobs poll](../examples/jobs-poll.md)
3. Optional: [Dashboards](../guides/dashboards.md) · [Model demos](../guides/model-demos.md) ·
   [Jobs poll](../examples/jobs-poll.md) / [Celery / RQ](../guides/jobs-celery-rq.md)
4. [Live interaction](../guides/live-interaction.md) (FastAPI live helpers; polling
   Supported on every host) —
   [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
   covers poll, token stream, SSE ping, Job SSE, WebSocket accept, and preload. Prefer
   polling until you have your own ops proof for SSE/WebSocket behind proxies
   (see [What's ready](../guides/whats-ready.md))
5. [Release notes](../guides/release-notes.md) (current train)

## 6. Harden and deploy

1. [Ship a Hedron app](../guides/ship.md) — adopter checklist
2. [Deployment](../guides/deployment.md) — env / Docker / proxy deep dive
3. [Testing](../guides/testing.md) · [Troubleshooting](../guides/troubleshooting.md)

## 7. Evaluate (optional)

[Evaluate Hedron](../guides/evaluate.md) · [What’s ready](../guides/whats-ready.md) ·
[Architecture](../ARCHITECTURE.md) · [Enterprise diligence](../guides/enterprise-diligence.md)

## 8. Contribute (optional)

[Contributing](../CONTRIBUTING.md) · [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md)

Stuck? [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md) ·
[Maturity labels (evaluators)](how-to-read.md)
