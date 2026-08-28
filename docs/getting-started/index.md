---
description: Choose the shortest path from an empty directory to a working Hedron application.
search:
  boost: 1.7
---

# Learn Hedron

!!! note "1.0 documentation"

    These tutorials target the verified `v1.0.0` repository candidate. Until its
    registry publication, use the public `hedron>=0.66.2,<0.67` pin shown in
    [Installation](installation.md); contributors use `uv sync`.

Get from an empty directory to a CSRF-protected form without introducing a frontend
build system. The golden path extends one small application across four pages; each step
has an observable browser result.

**Start now:** [Build your first app](quickstart.md) — scaffold → Hello → Refresh → edit
(~10 minutes after Python + uv/pip are ready).

New to application development, VS Code, or terminals? Choose the slower, fully explained
walkthrough for your environment:

- [Your first application with VS Code](first-app-vscode.md)
- [Your first application in Posit Workbench](first-app-posit-workbench.md) — installs and uses
  `hedron-posit` / `HedronPosit`

## Golden path

| Step | You add | You verify |
|---|---|---|
| 1. [Build your first app](quickstart.md) | A generated FastAPI application | A button refreshes one region without reloading the page |
| 2. [Understand HTMX](what-is-htmx.md) | The request/target/swap mental model | You can explain why the refresh is a fragment request |
| 3. [Add a second region](../guides/htmx-interactions.md) | Another `@app.view` | Each button updates only its view |
| 4. [Post a minimal form](../guides/minimal-form.md) | A form, action, and CSRF field | A valid POST changes the page; a missing token fails closed |
| 5. [Continue through the curriculum](learning-path.md) | Validation, persistence, auth, testing, and deployment | The same app grows along a production-minded path |

Installation extras and adapters (as needed): [Installation](installation.md).
Help: [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md).

Evaluating production use? [What’s ready](../guides/whats-ready.md) ·
[Why Hedron](../guides/why-hedron.md) · [Evaluate Hedron](../guides/evaluate.md) ·
[Maturity labels](how-to-read.md).

## Use the docs by task

| You need to… | Go to |
|---|---|
| Learn the page/fragment model | [Core concepts](core-concepts.md) |
| Decide whether behavior belongs in the browser or on the server | [What is Alpine?](what-is-alpine.md) · [What is HTMX?](what-is-htmx.md) |
| Choose between `@app.view` and the Advanced fragment API | [Which interaction API?](interaction-apis.md) |
| Paste one focused pattern into an existing app | [Cookbook](../guides/cookbook.md) |
| Diagnose an error or unexpected response | [Troubleshooting](../guides/troubleshooting.md) |
| Look up an exact component or signature | [Components](../components/index.md) · [API reference](../api/HEDRON.md) |

## Choose your path

| Starting point | Continue with |
|---|---|
| Know Python, new to application development | [Start with VS Code and terminal basics](first-app-vscode.md) |
| Know Python, developing in Posit Workbench | [Start with `hedron-posit` in Workbench](first-app-posit-workbench.md) |
| New FastAPI app | [Build your first app](quickstart.md) |
| Existing FastAPI app | [Mount Hedron beside existing routes](../guides/plain-fastapi.md) |
| Flask app | [Scaffold or integrate the Flask adapter](flask.md) — no FastAPI dependency |
| Django project | [Integrate the Django adapter](django.md) — Django `>=5.2,<6` |
| Streamlit app | [Migration center](../guides/streamlit-migration.md) — fit check, state mapping, and cutover |
| Evaluating production use | [Evaluate Hedron](../guides/evaluate.md) — readiness, ownership, and operational checks |

FastAPI remains the default `hedron new` path. Full cloud env (slow first boot):
[Try with Codespaces](../examples/try-it.md).
