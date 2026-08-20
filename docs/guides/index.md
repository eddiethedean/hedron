---
description: Task-oriented Hedron guides for interactions, data, security, operations, and extensions.
search:
  boost: 1.4
---

# Guides

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
- [Post a minimal form](minimal-form.md) — golden-path `@app.command` + CSRF
- [Forms and actions](forms-and-actions.md) — advanced region / `InteractionResult` path
- [Mutations](mutations.md) — when to use `@action` vs `@component` POST
- [Live updates (polling)](live-interaction.md) — `Poll` is Supported; SSE/WS experimental
- [HTMX extensions](htmx-extensions.md) — declared SSE, head-support, preload

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

## Other

- [Migrate from Streamlit](streamlit-migration.md)
- [FAQ](faq.md)
