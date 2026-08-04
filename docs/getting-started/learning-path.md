# Learning path

A suggested order from first page to production-minded apps.

**Golden path (start here):** Install → First app → HTMX interactions → Minimal form →
(then continue below)

## 1. Ship a page (30 minutes)

1. [Installation](installation.md)
2. [Build your first app](quickstart.md)
3. [HTMX interactions](../guides/htmx-interactions.md) — GET refresh into a region (browser click)
4. [Minimal form POST](../guides/minimal-form.md) — CSRF-safe classic form (~40 lines)

Then read [Core concepts](core-concepts.md) if you want the page/fragment model explained.

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

1. [Authentication](../guides/authentication.md) · [Testing](../guides/testing.md)
2. [Deployment](../guides/deployment.md)
3. [Best practices](../guides/best-practices.md)
4. [Upgrade](../guides/upgrade.md) when changing trains

## 6. Contribute or evaluate deeply

- [What’s ready today](../guides/whats-ready.md) · [Why Hedron](../guides/why-hedron.md) ·
  [Evaluate Hedron](../guides/evaluate.md)
- [Production readiness](../guides/production-readiness.md) · [Support](../guides/support.md)
- [CRUD tutorial](../examples/crud-tutorial.md) · [Try with Codespaces](../examples/try-it.md)
- [Contributing](../CONTRIBUTING.md) · [Architecture](../ARCHITECTURE.md)

Stuck? [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md) ·
[How to read these docs](how-to-read.md)
