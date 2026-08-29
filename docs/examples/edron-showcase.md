---
description: A full-feature Edron operations console, available as a real app and an offline simulation.
---

# Edron Showcase

Meet Edron through a complete operations console authored with its class-oriented API. The
showcase source uses only `edron`: no direct Hedron imports, native escape hatches, or component
tree authoring are required.

## Run the real Edron app

From a repository checkout:

```bash
uv sync
uv run edron run app:app --app-dir examples/edron-showcase --reload
```

Open <http://127.0.0.1:8000/>. The data is synthetic and local, but the Edron page lifecycle,
sidebar composition, layouts, fragments, actions, charts, tables, tabs, theme, CSRF boundary,
and native lowering are real.

The complete source is [`examples/edron-showcase/app.py`](https://github.com/eddiethedean/hedron/blob/v1.0/examples/edron-showcase/app.py).
Edron's generated theme includes coordinated light/dark tokens that follow the browser preference,
and the request-local shell stacks its layouts for narrow screens.

## Explore the offline simulation

The simulator mirrors the user-visible Edron contracts without starting a server. Try refreshing
the pipeline, filtering recent runs, approving the release, and inspecting the Edron surface map.

=== "Demo"

    Full Edron operations console — pages, layouts, fragments, actions, charts, and outcomes. Docs simulation.

    <!-- hedron-sim:edron-showcase-dashboard -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    """Minimal Edron-only source companion for the interactive showcase."""

    import edron as ed

    theme = ed.theme("edron-showcase", accent="#0d9488")
    app = ed.App(
        title="Edron Showcase",
        security="standard",
        session_secret="replace-in-production",
        theme=theme,
    )


    @app.page("/", title="Edron Showcase")
    class Showcase(ed.Page):
        @ed.fragment(path="/pipeline/refresh")
        def pipeline(self) -> None:
            with self.card(title="Pipeline") as card:
                card.info("Transform in progress")
                card.text("Compose → validate → transform → publish")

        @ed.action(path="/approve", fallback="/")
        def approve(self) -> ed.Outcome:
            return ed.success("Publish queued")

        def render(self) -> None:
            self.heading("Command center")
            self.caption("A complete workspace composed from Edron page methods.")
            self.metric("Successful runs", "98.7%", delta="+2.1%", delta_tone="up")
            self.pipeline()
            self.button("Refresh pipeline", action=self.pipeline)
            self.button("Approve release", action=self.approve)
    ```

The simulator is intentionally not a replacement for Edron's runtime. It provides a safe,
serverless tour of the browser experience and request contracts.

## What this showcases

| Surface | Edron API |
|---|---|
| Application shell | `App`, `Page`, sidebar composition, named theme |
| Layout and content | `columns`, `card`, `metric`, `heading`, `tabs` |
| Data and visuals | `table`, `line_chart`, bounded synthetic data |
| Server interaction | `@ed.fragment`, `@ed.action`, `ed.refresh`, `ed.success` |
| Public boundary | Edron-only source with no Hedron escape hatches |

For the lower-level component version, see the [Hedron Showcase](showcase.md). For the Edron
programming model, continue to the [Edron user guide](../guides/edron-user-guide.md).
