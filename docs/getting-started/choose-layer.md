---
description: Understand why Hedron is the primary API and when the alternate Edron facade is appropriate.
search:
  boost: 2
---

# Choose an authoring API

Start with **Hedron** unless you have deliberately chosen the alternate class-oriented
facade. Hedron is the primary documentation, examples, extension, and integration target.
It exposes the FastAPI-native application model directly.

<!-- hedron-release-status -->

## The short answer

Choose **Hedron** for new applications, direct FastAPI route functions, explicit
component-tree composition, Flask or Django hosts, and framework-extension work.

Choose **Edron** only when its class-oriented page vocabulary is itself a requirement.
It lowers into the same Hedron runtime and remains available as an alternate facade.

## Compare the authoring models

=== "Hedron"

    ```python
    from hedron import Hedron, Stack, Text

    app = Hedron(title="Operations", security="standard")

    @app.page("/")
    def home():
        return Stack(Text("Operations"), Text("Direct component composition."))
    ```

=== "Alternate: Edron"

    ```python
    import edron as ed

    app = ed.App(title="Sales", security="standard")

    @app.page("/", title="Sales dashboard")
    class Home(ed.Page):
        def render(self) -> None:
            self.metric("Orders", 128, delta="+12")
            self.text("A complete page from a small Python class.")
    ```

## Decision table

| Requirement | Start with |
|---|---|
| Primary learning path and documentation | Hedron |
| New dashboard, CRUD app, or data workflow | Hedron |
| Data workspace, resource, cache, and job contracts | Hedron |
| Direct control over FastAPI dependencies and routes | Hedron |
| Reusable component or integration package | Hedron |
| Flask or Django runtime without FastAPI | Hedron |
| Class-oriented page vocabulary is a hard requirement | Edron |

## What stays the same

Both layers use server-rendered HTML, HTMX for bounded partial updates, ordinary HTTP
fallbacks, explicit trust boundaries, and one native application authority. Neither layer
requires Node.js, owns your database, or replaces application authorization.

## Continue

- [Build your first Hedron app](quickstart.md)
- [Build with the alternate Edron facade](edron-quickstart.md)
- [Understand the architecture](../ARCHITECTURE.md)
- [Compare production fit](../guides/evaluate.md)
