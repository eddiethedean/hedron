---
description: Find the Hedron API by the job you are trying to do.
search:
  boost: 1.8
---

# API by task

Use this page when you know what you want to build but not which Hedron symbol to use.
The [full API reference](README.md) is organized by contract and package; this page is
organized by intent.

## Start here

| I want to… | Start with | Then read |
|---|---|---|
| Create an application | [`Hedron`](HEDRON.md), `@app.screen` | [Build your first app](../getting-started/quickstart.md) |
| Render a complete page | [`Page`](PAGE.md), `@app.page` | [Core concepts](../getting-started/core-concepts.md) |
| Update one part of a page | `@app.refreshable`, `status.refresh_button(...)` | [What is HTMX?](../getting-started/what-is-htmx.md) |
| Add a second interaction | `@app.refreshable`, `@app.command` | [HTMX interactions](../guides/htmx-interactions.md) |
| Accept a form safely | `@app.form_command`, `FormBody`, `CsrfField` | [Minimal form POST](../guides/minimal-form.md) |
| Choose a lower-level interaction API | `region`, `@app.fragment`, `InteractionResult` | [Which interaction API?](../getting-started/interaction-apis.md) |
| Build a reusable typed component | `Component`, `Props`, `NodeLike` | [Component demos](../components/index.md) |
| Style a product surface | `DesignSystem`, `StyleRecipe`, `StyleScope` | [Presentation](PRESENTATION.md) · [Modern CSS in 0.60](../guides/modern-css-0.60.md) |
| Add data and tables | `DataWorkspace`, `DataTable`, `Auto` | [Data applications](../guides/data-apps.md) · [Data API](DATA.md) |
| Add authentication | `SessionAuthFlow`, `AuthResult` | [Authentication](../guides/authentication.md) · [Auth API](AUTH.md) |
| Test requests and fragments | `AppScenario`, `TestClient`, HTMX assertions | [Testing API](TESTING.md) |
| Inspect routes or diagnose a build | `hedron routes`, `hedron check`, `hedron style` | [CLI](CLI.md) · [Troubleshooting](../guides/troubleshooting.md) |
| Deploy behind a proxy | `mount_hedron_static`, path-prefix configuration | [Deployment](../guides/deployment.md) · [Mount API](MOUNT.md) |

## Choose the right level

Start with the highest-level contract that solves the problem:

1. Use a guide and a facade such as `@app.screen`, `@app.refreshable`, or
   `@app.form_command` for a new application.
2. Use a component page when you need an exact constructor, prop, or accessibility
   contract.
3. Use the API reference when you need return types, errors, response headers, or
   stability information.
4. Use Autodoc for the complete signature surface after the hand-maintained contract
   page has answered the design question.

Do not begin with the largest catalog unless you are auditing an existing application.
The [learning path](../getting-started/learning-path.md) is the better starting point
for a new project.

## A useful API page should answer

For any symbol, look for these six pieces:

- a short, runnable example;
- the signature or members;
- parameters and defaults;
- return values and response behavior;
- errors, HTTP status, and `HED-*` diagnostics;
- related guides and the next abstraction to consider.

If a page does not answer one of those questions, use the linked guide or [Autodoc](AUTODOC.md)
and treat the omission as a documentation issue worth reporting.

## Related entry points

- [Build a notes app](../examples/build-notes-app.md) — one progressive application path.
- [Public API](README.md) — the complete hand-maintained catalog.
- [Stability](STABILITY.md) — stable, beta, experimental, and deferred meanings.
- [API coverage map](COVERAGE.md) — where public exports are documented.
