# Recipes

Short, copy-pasteable apps for common workflows. Prefer these after
[Build your first app](../../getting-started/quickstart.md) and before the kitchen-sink
[reference app](../reference-app.md).

| Recipe | What it shows | Limits |
|---|---|---|
| [Notes + SQLAlchemy](../notes-sqlalchemy.md) | Persist notes with SQLAlchemy + SQLite | Create + list + delete (not a full admin) |
| [Session auth](../session-auth.md) | Login / logout with Starlette sessions | Demo credentials only; `/` redirects to login |
| [File upload](../file-upload.md) | CSRF-safe multipart upload | In-memory / local demo — no durable store |
| [Jobs poll](../jobs-poll.md) | `Poll` + `job_status_response` | In-memory backend — single process only |

Also useful:

- [Live interaction](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction) —
  **polling** is Supported; SSE/WS paths are Experimental
- [CRUD tutorial](../crud-tutorial.md) — guided tour of the reference app
- [Runnable matrix](../runnable.md) — every example folder and how to run it

!!! note "Not recipes"

    [Phase evidence](../phase-evidence.md) and version-stamped dirs (`dashboard-0.17`,
    `model-demo-0.18`, …) are **maintainer exit scenarios**, not product tutorials.
    [Simulated UI patterns](../gallery.md) are Read the Docs simulations — not a live
    Hedron process.
