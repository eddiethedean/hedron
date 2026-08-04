# Learning path

A suggested order from first page to production-minded apps. Start with
[Get started](index.md) if you have not installed yet.

## 1. Ship a page (30 minutes)

1. [Installation](installation.md)
2. [Build your first app](quickstart.md)
3. [HTMX interactions](../guides/htmx-interactions.md) — GET refresh into a region (browser click)
4. [Minimal form POST](../guides/minimal-form.md) — CSRF-safe classic form (~40 lines)

Then read [Core concepts](core-concepts.md) if you want the page/fragment model explained
(optional — skip until after a working form if you prefer).

## 2. Interact without a SPA (next hour)

1. [Mutations](../guides/mutations.md) — `@action` vs `@component` POST
2. [Forms and actions](../guides/forms-and-actions.md) — validation fragments and HTMX POST
3. [Security](../guides/security.md) — CSRF profiles and headers
4. Optional: open `/hedron-explorer/` with `hedron[dev]` and `explorer="development"`

## 3. Pick your host

| If you… | Read |
|---|---|
| Stay on FastAPI | Continue with guides below |
| Use Flask | [Flask adapter](flask.md) |
| Use Django | [Django adapter](django.md) (PyPI first; optional reference clone) |
| Prefer Jinja/HTML templates | [HDJ authoring](../guides/hdj-authoring.md) + `hedron[jinja]` |

## 4. Data, charts, and live updates

1. [Data applications](../guides/data-apps.md) / [Charts and HTMX](../guides/charts-and-htmx.md)
2. [Live interaction](../guides/live-interaction.md) (0.10 FastAPI; polling elsewhere)
3. [What's new in 0.10](../guides/whats-new-0.10.md)

## 5. Harden and deploy

1. [Deployment](../guides/deployment.md)
2. [Production readiness](../guides/production-readiness.md)
3. [Testing](../guides/testing.md) · [Troubleshooting](../guides/troubleshooting.md)

## 6. Evaluate (optional)

[Evaluate Hedron](../guides/evaluate.md) · [What’s ready](../guides/whats-ready.md) ·
[Architecture](../ARCHITECTURE.md) · [Enterprise diligence](../guides/enterprise-diligence.md)

## 7. Contribute (optional)

[Contributing](../CONTRIBUTING.md) · [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md)

Stuck? [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md) ·
[How to read these docs](how-to-read.md)
