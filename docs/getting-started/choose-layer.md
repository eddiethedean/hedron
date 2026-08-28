---
description: Decide whether Edron or Hedron is the right public API for your application.
search:
  boost: 2
---

# Choose Edron or Hedron

Edron and Hedron are two authoring layers over the same server-rendered runtime. They are
designed to compose; choosing Edron does not close off Hedron's lower-level APIs.

<!-- hedron-release-status -->

## The short answer

Choose **Edron** for a new dashboard, internal tool, CRUD application, or data workflow.
It provides a compact, class-oriented page API and coordinated application features.

Choose **Hedron** when you want direct FastAPI route functions, explicit component-tree
composition, a Flask or Django host, or framework-extension work.

<!-- hedron-install-matrix -->

## Compare the authoring models

=== "Edron"

    ```python
    import edron as ed

    app = ed.App(title="Sales", security="standard")

    @app.page("/", title="Sales dashboard")
    class Home(ed.Page):
        def render(self) -> None:
            self.metric("Orders", 128, delta="+12")
            self.text("A complete page from a small Python class.")
    ```

=== "Hedron"

    ```python
    from hedron import Hedron, Stack, Text

    app = Hedron(title="Operations", security="standard")

    @app.page("/")
    def home():
        return Stack(Text("Operations"), Text("Direct component composition."))
    ```

## Decision table

| Requirement | Start with |
|---|---|
| Fastest path to a complete Python application | Edron |
| Familiar page, metric, input, table, and chart vocabulary | Edron |
| Data workspace, resource, cache, and job conventions | Edron |
| Direct control over FastAPI dependencies and routes | Hedron |
| Reusable component or integration package | Hedron |
| Flask or Django runtime without FastAPI | Hedron |
| Mix high-level pages with low-level components | Edron, then use `self.include(...)` and `app.native` |

## What stays the same

Both layers use server-rendered HTML, HTMX for bounded partial updates, ordinary HTTP
fallbacks, explicit trust boundaries, and one native application authority. Neither layer
requires Node.js, owns your database, or replaces application authorization.

## Continue

- [Build your first Edron app](edron-quickstart.md)
- [Build your first Hedron app](quickstart.md)
- [Understand the architecture](../ARCHITECTURE.md)
- [Compare production fit](../guides/evaluate.md)
