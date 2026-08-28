---
description: Find the Edron 1.0 API by application task.
search:
  boost: 1.8
---

# Edron API by task

This is the public entry point for Edron's 1.0 API. Use the
[generated symbol reference](EDRON_AUTODOC.md) for exact signatures and the
[design contract](EDRON.md) when you need lowering or compatibility details.

## Application and pages

| Task | Start with |
|---|---|
| Create an application | `App` |
| Register a page | `App.page()` and `Page` |
| Add content | `Page.text()`, `heading()`, `markdown()`, `code()`, `metric()` |
| Compose layout | `container()`, `columns()`, `tabs()`, `expander()`, `card()` |
| Include a Hedron component | `Page.include()` |
| Access the underlying application | `App.native` or its alias `App.hedron` |
| Resolve a registered native surface | `App.native_surface(surface)` |

## Inputs and interactions

| Task | Start with |
|---|---|
| Render an independently refreshable read surface | `@fragment` |
| Handle an unsafe request | `@action` |
| Refresh a fragment | `refresh(fragment)` |
| Report success or navigate | `success(...)`, `navigate(...)` |
| Bind a typed form | `Page.form()` and a Pydantic model |
| Render basic controls | `text_input()`, `number_input()`, `selectbox()`, `checkbox()` |

Fragments read; actions change state. Keep authorization, validation, transactions, and
idempotency in the action boundary or application services.

## Data applications

| Task | Start with |
|---|---|
| Describe records and keys | `DataSource` |
| Declare visible/editable fields | `Column`, `EditPolicy` |
| Add bounded paging/filtering/export | `DataWorkspace` |
| Represent a requested edit | `EditIntent` |
| Export approved data | `DataExport` |

## Resources, caching, and jobs

| Task | Start with |
|---|---|
| Register a lazy service | `App.resource()` and `Resource` |
| Cache derived data | `cache_data()` |
| Describe durable work | `JobFlow` |
| Publish bounded status updates | `job_status_events()` |

Process-local caches and jobs are development defaults. Multi-worker deployments need shared
backends selected by the application.

## Diagnostics and deployment

| Task | API or command |
|---|---|
| Check source without importing it | `edron check app.py` |
| Inspect registrations | `edron explain app:app` |
| Diagnose capabilities | `edron doctor app:app` |
| Resolve a deployment profile | `resolve_deployment_profile()` |
| Validate deployment facts | `check_deployment()` or `edron deploy-check` |
| Produce deterministic application evidence | `App.manifest()` and `App.conformance()` |

## Exceptions

Public configuration and registration errors derive from ordinary `ValueError`, `TypeError`,
or the documented Edron deployment/package exceptions. CLI failures return non-zero and emit a
stable `EDR-*` diagnostic when a structured diagnostic exists. Exact exception declarations are
listed in the [generated symbol reference](EDRON_AUTODOC.md).
