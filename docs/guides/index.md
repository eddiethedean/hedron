---
description: Task-oriented Hedron guides for interactions, data, security, operations, and extensions.
search:
  boost: 1.4
---

# Guides

!!! note "Release context"

    Guides describe the published 1.0 release. See
    [Current release and support](current-release.md) for PyPI pins,
    the migration baseline, package maturity, and support status.

Task-oriented guidance from a working page to a maintainable Hedron project.

Complete **Start** first ([Learning path](../getting-started/learning-path.md):
First app → HTMX → Minimal form). This section continues with polling, data, security,
and ops.

**Help:** [FAQ](faq.md) · [Troubleshooting](troubleshooting.md).
Evaluating adoption? [What’s ready](whats-ready.md) · [Evaluate](evaluate.md).
Shipping? [Ship](ship.md).

## Find the shortest answer

| If you need… | Use |
|---|---|
| One pasteable pattern | [Cookbook](cookbook.md) |
| A fix organized by symptom | [Troubleshooting](troubleshooting.md) |
| The meaning and remediation for `HED-*` | [Error codes](error-codes.md) |
| An exact component prop or example | [Component reference](../components/index.md) |
| An exact public API signature | [API reference](../api/HEDRON.md) |

## Build interactions

- [HTMX interactions](htmx-interactions.md) — add a second refreshable view
- [Post a minimal form](minimal-form.md) — golden-path `@app.action` + CSRF
- [Forms and actions](forms-and-actions.md) — advanced region / `InteractionResult` path
- [Mutations](mutations.md) — canonical `@app.action` mutation routes
- [Live updates (polling)](live-interaction.md) — `Poll` is Supported; SSE/WS experimental
- [HTMX extensions](htmx-extensions.md) — declared SSE, head-support, preload

## Style an interface

- [Comprehensive styling](styling.md) — visual tour of presentation tokens, layout,
  themes, recipes, scoped CSS, and styling checks
- [Modern CSS](modern-css.md) — application styling boundary, production checklist,
  progressive CSS tiers, overlays, media, controls, and fallbacks

## Add data and visuals

- [Data applications](data-apps.md)
- [Charts and HTMX](charts-and-htmx.md)
- [Maps](maps.md)
- [Dashboards](dashboards.md)
- [Compose built-ins](component-composition.md)

## Secure an app

- [Authentication](authentication.md)
- [OIDC](oidc.md)
- [Security](security.md)
- [Threat model](threat-model.md)
- [Hardened sessions](hardened-sessions.md)
- [Multi-tenant isolation](multi-tenant.md)
- [Accessibility](accessibility.md)

## Operate an app

- [Ship an app](ship.md)
- [Deployment](deployment.md)
- [Secrets and workers](secrets-and-workers.md)
- [Durable jobs](jobs-celery-rq.md)
- [Test your UI](testing.md)
- [Performance](performance.md)
- [Observability](observability.md)
- [Best practices](best-practices.md)

## Extend Hedron

- [Use plugins](plugin-consumer.md)
- [Author plugins](plugin-authoring.md)
- [Curated extras](../api/EXTRAS.md)

## Other

- [Migrate from Streamlit](streamlit-migration.md)
- [FAQ](faq.md)
