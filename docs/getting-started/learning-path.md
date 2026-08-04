# Learning path

A suggested order from first page to production-minded apps. Start with
[Get started](index.md) if you have not installed yet.

## 1. Hello page (~10 minutes)

1. [Installation](installation.md)
2. [Build your first app](quickstart.md) — stop when the browser shows the scaffold
   (or manual) home page

That is the first success. Extend the **same** app in the next section; do not start a
second project.

## 2. First interaction (~20–30 minutes)

1. [HTMX interactions](../guides/htmx-interactions.md) — GET refresh into a region
   (edit the scaffold; browser click)
2. [Minimal form POST](../guides/minimal-form.md) — CSRF-safe classic form on `/notes`

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

## 5. Data, charts, and live updates

1. [Data applications](../guides/data-apps.md) / [Charts and HTMX](../guides/charts-and-htmx.md)
2. [Live interaction](../guides/live-interaction.md) (0.10 FastAPI; polling elsewhere) —
   the first-party sample covers poll + token stream; Job SSE / WebSocket / preload are
   guide/API-oriented until you extend the sample
3. [What's new in 0.10](../guides/whats-new-0.10.md)

## 6. Harden and deploy

1. [Deployment](../guides/deployment.md)
2. [Production readiness](../guides/production-readiness.md)
3. [Testing](../guides/testing.md) · [Troubleshooting](../guides/troubleshooting.md)

## 7. Evaluate (optional)

[Evaluate Hedron](../guides/evaluate.md) · [What’s ready](../guides/whats-ready.md) ·
[Architecture](../ARCHITECTURE.md) · [Enterprise diligence](../guides/enterprise-diligence.md)

## 8. Contribute (optional)

[Contributing](../CONTRIBUTING.md) · [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md)

Stuck? [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md) ·
[How to read these docs](how-to-read.md)
