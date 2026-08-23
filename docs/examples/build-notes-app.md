---
description: A progressive tutorial path from a generated Hedron app to a production-minded notes application.
search:
  boost: 1.7
---

# Build a notes app

Build one small application across a sequence of checkpoints instead of starting a new
example for every concept. You will begin with a generated Hello page, add a live region,
post a validated form, persist notes, and finish with a deployment checklist.

## What you will learn

- how a typed page becomes a complete HTML document;
- how a refreshable view returns a targeted fragment;
- how forms, validation, and CSRF fit into the same request model;
- when to use an in-memory example, `DataWorkspace`, or a durable database;
- how authentication, testing, and deployment change the application boundary.

## Before you start

Use [Build your first app](../getting-started/quickstart.md) to create the project. You
need Python **3.11–3.14** and either `uv` or an activated virtual environment. Each step
edits the same application and should take 5–20 minutes.

## The tutorial path

| Step | Add | Verify | Continue with |
|---|---|---|---|
| 0 | A generated FastAPI application | Hello loads and **Refresh status** changes one region | [Quickstart](../getting-started/quickstart.md) |
| 1 | The page / component / fragment mental model | You can identify the route, view host, and response mode | [Core concepts](../getting-started/core-concepts.md) |
| 2 | A second refreshable region | Two controls update independent regions | [HTMX interactions](../guides/htmx-interactions.md) |
| 3 | A typed note form | A valid POST saves a note; an invalid or missing-CSRF request fails safely | [Minimal form POST](../guides/minimal-form.md) |
| 4 | A durable notes table | Notes survive a restart and delete is authorized | [Notes + SQLAlchemy](notes-sqlalchemy.md) |
| 5 | A composed data surface | List, create, and edit behavior use the data contract | [Notes list tutorial](crud-tutorial.md) |
| 6 | Session authentication | The notes page is gated and the user boundary is explicit | [Session authentication](session-auth.md) |
| 7 | Production checks | Configuration, assets, tests, and proxy behavior are reviewed | [Ship a Hedron app](../guides/ship.md) |

## The first three checkpoints

If you only have 30 minutes, complete steps 0–3. That gives you the core Hedron model:

```text
typed page → refreshable view → HTML fragment → validated form POST
```

At each checkpoint, keep the browser open and verify the visible result before moving on.
When something fails, inspect the request URL, `HX-Target`, response status, and returned
HTML before changing the Python code. [Troubleshooting](../guides/troubleshooting.md)
has the symptom-first fixes.

## Choose the storage path

The tutorial deliberately shows three levels:

- **In memory:** fastest way to learn the interaction contract; data disappears on restart.
- **`DataWorkspace`:** composed list/detail/create/edit surfaces with explicit policy.
- **SQLAlchemy:** durable persistence when you own the schema, transactions, and authorization.

Do not treat the in-memory version as production storage. The [SQLAlchemy example](notes-sqlalchemy.md)
and [data guide](../guides/data-apps.md) call out the boundary explicitly.

## Finish with the production path

After the notes app works, continue in this order:

1. [Test your UI](../guides/testing.md), including a successful fragment request and a rejected target.
2. [Authentication](../guides/authentication.md), then [enterprise diligence](../guides/enterprise-diligence.md)
   if the app will handle real users or sensitive data.
3. [Deployment](../guides/deployment.md) and [Ship a Hedron app](../guides/ship.md).
4. [Current release and support](../guides/current-release.md) before pinning an upgrade.

## Prefer a single runnable listing?

Use [Notes + SQLAlchemy](notes-sqlalchemy.md) for a complete durable example, or
[Notes list tutorial](crud-tutorial.md) for the higher-level data facade. Both are
follow-up implementations of the same path above, not replacements for the first three
concept checkpoints.
