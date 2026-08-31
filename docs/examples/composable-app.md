---
title: Compose an app across files
description: Split a Hedron app into importable component modules without losing its component-tree model.
---

# Compose an app across files

Hedron components are ordinary Python values. A component can live beside the page
that uses it, in another module, or in a separately versioned package—the parent still
composes the returned value into one checked component tree.

This example splits an operations page into focused files and uses
`components/__init__.py` as its deliberate import surface. It uses only Hedron's
built-in styling, including responsive layouts and light/dark appearance; there is no
application CSS.

```text
composable-app/
├── app.py
└── components/
    ├── __init__.py
    ├── activity.py
    ├── deployments.py
    ├── metrics.py
    └── status.py
```

## Source files

Each tab below is a real file from the runnable example.

=== "app.py"

    ```python title="app.py"
    """A multi-file Hedron app composed entirely from built-in styling."""

    from __future__ import annotations

    import os
    from datetime import datetime, timezone

    from components import (
        ActivityEvent,
        MetricValue,
        activity_feed,
        deployment_panel,
        metrics_overview,
        service_status,
    )

    from hedron import (
        Container,
        Heading,
        Hedron,
        Page,
        SafeUrl,
        Stack,
        Tabs,
        Text,
        UrlPurpose,
        html,
    )

    METRICS: tuple[MetricValue, ...] = (
        ("Successful runs", "98.7%", "+2.1%"),
        ("Deploy frequency", "24 / week", "+4"),
        ("Time to recovery", "11 min", "-18%"),
    )
    EVENTS: tuple[ActivityEvent, ...] = (
        ("Production deployment completed", "8 minutes ago"),
        ("Schema checks passed", "21 minutes ago"),
        ("Release approved by Maya", "34 minutes ago"),
    )

    app = Hedron(
        title="Composable operations",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
    )


    @app.view("/status")
    def status():
        stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        return service_status(stamp)


    @app.page("/")
    def home() -> Page:
        return Page(
            Container(
                Stack(
                    Heading("Composable operations", level=1),
                    Text("Each section comes from an importable Python component module."),
                    status(),
                    html.form(
                        html.button("Refresh status", type="submit"),
                        method="get",
                        action=SafeUrl.parse(
                            status.path,
                            purpose=UrlPurpose.FORM_ACTION,
                        ),
                        **status.ref.htmx_attributes(
                            target=status.selector,
                            swap="outerHTML",
                        ),
                    ),
                    metrics_overview(METRICS),
                    Tabs(
                        ("Activity", activity_feed(EVENTS)),
                        (
                            "Deployment",
                            deployment_panel(environment="production", progress=72),
                        ),
                        appearance="underline",
                        responsive="scroll",
                    ),
                    gap="lg",
                ),
                max_width="xl",
                padding="lg",
            ),
            title="Composable operations",
        )
    ```

=== "components/__init__.py"

    ```python title="components/__init__.py"
    """The app's deliberate component import surface."""

    from .activity import ActivityEvent, activity_feed
    from .deployments import deployment_panel
    from .metrics import MetricValue, metrics_overview
    from .status import service_status

    __all__ = [
        "ActivityEvent",
        "MetricValue",
        "activity_feed",
        "deployment_panel",
        "metrics_overview",
        "service_status",
    ]
    ```

=== "components/metrics.py"

    ```python title="components/metrics.py"
    """Reusable metric components for the overview page."""

    from __future__ import annotations

    from collections.abc import Sequence

    from hedron import Card, Grid, Metric

    MetricValue = tuple[str, str, str]


    def metrics_overview(values: Sequence[MetricValue], *, class_: str | None = None) -> Grid:
        """Build a responsive metric grid from application data."""
        return Grid(
            *(
                Card(Metric(label, value, delta=delta, delta_tone="up"))
                for label, value, delta in values
            ),
            columns={"base": 1, "md": 3},
            class_=class_,
        )
    ```

=== "components/activity.py"

    ```python title="components/activity.py"
    """Activity-feed components."""

    from __future__ import annotations

    from collections.abc import Sequence

    from hedron import Card, Stack, Status

    ActivityEvent = tuple[str, str]


    def activity_feed(events: Sequence[ActivityEvent]) -> Card:
        """Build an activity card without knowing where it will be rendered."""
        return Card(
            Stack(
                *(Status(f"{message} · {when}", variant="activity") for message, when in events),
                gap="sm",
            ),
            title="Recent activity",
        )
    ```

=== "components/deployments.py"

    ```python title="components/deployments.py"
    """Deployment summary components."""

    from __future__ import annotations

    from hedron import Card, Progress, Stack, Status, Text


    def deployment_panel(*, environment: str, progress: float) -> Card:
        """Build a deployment panel from explicit inputs."""
        return Card(
            Stack(
                Status(f"Deploying to {environment}", tone="info", variant="activity"),
                Progress(progress, label=f"{environment} deployment progress"),
                Text(f"{progress:.0f}% complete"),
                gap="sm",
            ),
            title="Current deployment",
        )
    ```

=== "components/status.py"

    ```python title="components/status.py"
    """Service-status components shared by pages and fragment routes."""

    from __future__ import annotations

    from hedron import Alert


    def service_status(refreshed_at: str) -> Alert:
        """Build the replaceable status fragment."""
        return Alert(
            f"All services operational · refreshed {refreshed_at}",
            title="System status",
            tone="success",
        )
    ```

[Full code on GitHub](https://github.com/eddiethedean/hedron/tree/main/examples/composable-app)

## Run it

From a clone of the Hedron repository:

```bash
uv sync
uv run uvicorn --app-dir examples/composable-app app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Resize the browser or switch
your operating-system appearance to see the built-in responsive layout and light/dark
theme behavior.

## Optional: add ordinary CSS

The built-in styling is the fastest path and keeps application code small, but it is
not mandatory. Use ordinary CSS when the built-in visual language is not right for
your product or when you need a presentation feature that Hedron does not provide.
Hedron still owns the semantic component tree and behavior.

Register the local file with `app.styles(...)` instead of injecting a `<style>` tag or
mounting an untracked static file. Registration lets Hedron validate, scope,
fingerprint, and serve the stylesheet through its CSP-aware asset pipeline. Put your
own classes on components, keep request data out of CSS, and do not depend on private
Hedron DOM structure.

This alternate entry point reuses the same imported component modules:

=== "custom_css.py"

    ```python title="custom_css.py"
    """The composable app with an explicitly registered ordinary CSS file."""

    from __future__ import annotations

    import os
    from pathlib import Path

    from components import (
        ActivityEvent,
        MetricValue,
        activity_feed,
        deployment_panel,
        metrics_overview,
    )

    from hedron import Container, Heading, Hedron, Page, Stack, StyleScope, Tabs, Text

    ROOT = Path(__file__).resolve().parent
    METRICS: tuple[MetricValue, ...] = (
        ("Successful runs", "98.7%", "+2.1%"),
        ("Deploy frequency", "24 / week", "+4"),
        ("Time to recovery", "11 min", "-18%"),
    )
    EVENTS: tuple[ActivityEvent, ...] = (
        ("Production deployment completed", "8 minutes ago"),
        ("Schema checks passed", "21 minutes ago"),
        ("Release approved by Maya", "34 minutes ago"),
    )

    app = Hedron(
        title="Custom composable operations",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
    )
    app.styles(
        "composable-custom",
        ROOT / "styles.css",
        scope="custom-dashboard",
        allowed_roots=(ROOT,),
    )


    @app.page("/")
    def home() -> Page:
        content = Container(
            Stack(
                Stack(
                    Text("OPTIONAL APPLICATION CSS", class_="custom-kicker"),
                    Heading("Your components. Your visual voice.", level=1, class_="custom-title"),
                    Text(
                        "Keep Hedron's semantics and behavior, then add ordinary CSS "
                        "where your product needs a distinct presentation.",
                        class_="custom-copy",
                    ),
                    class_="custom-hero",
                    gap="md",
                ),
                metrics_overview(METRICS, class_="custom-metrics"),
                Tabs(
                    ("Activity", activity_feed(EVENTS)),
                    (
                        "Deployment",
                        deployment_panel(environment="production", progress=72),
                    ),
                    appearance="pills",
                    responsive="scroll",
                    class_="custom-tabs",
                ),
                gap="lg",
            ),
            max_width="xl",
            padding="lg",
            class_="custom-shell",
        )
        return Page(
            StyleScope(content, scope="custom-dashboard"),
            title="Custom composable operations",
        )
    ```

=== "styles.css"

    ```css title="styles.css"
    .custom-shell {
      --custom-accent: #6d28d9;
      --custom-accent-soft: #ede9fe;
      --custom-ink: #1e1b4b;
      min-height: 100vh;
      padding-block: clamp(1rem, 4vw, 4rem);
    }

    .custom-hero {
      position: relative;
      overflow: hidden;
      padding: clamp(1.5rem, 5vw, 4.5rem);
      border: 1px solid color-mix(in srgb, var(--custom-accent) 25%, transparent);
      border-radius: clamp(1.25rem, 3vw, 2.5rem);
      background:
        radial-gradient(circle at 90% 10%, rgb(255 255 255 / 85%), transparent 34%),
        linear-gradient(135deg, var(--custom-accent-soft), #fdf4ff 70%);
      box-shadow: 0 2rem 5rem rgb(76 29 149 / 14%);
      color: var(--custom-ink);
    }

    .custom-kicker {
      color: var(--custom-accent);
      font-size: 0.75rem;
      font-weight: 800;
      letter-spacing: 0.16em;
    }

    .custom-title {
      max-width: 13ch;
      font-size: clamp(2.5rem, 8vw, 5.75rem);
      line-height: 0.95;
      letter-spacing: -0.055em;
    }

    .custom-copy {
      max-width: 58ch;
      font-size: clamp(1rem, 2vw, 1.2rem);
      line-height: 1.7;
    }

    .custom-metrics {
      gap: clamp(0.75rem, 2vw, 1.5rem);
    }

    .custom-tabs {
      padding: clamp(0.75rem, 2vw, 1.5rem);
      border: 1px solid color-mix(in srgb, var(--custom-accent) 18%, transparent);
      border-radius: 1.25rem;
      background: color-mix(in srgb, var(--custom-accent-soft) 35%, transparent);
    }

    @media (prefers-color-scheme: dark) {
      .custom-shell {
        --custom-accent: #c4b5fd;
        --custom-accent-soft: #2e1065;
        --custom-ink: #faf5ff;
      }

      .custom-hero {
        background:
          radial-gradient(circle at 90% 10%, rgb(196 181 253 / 22%), transparent 34%),
          linear-gradient(135deg, #2e1065, #111827 72%);
        box-shadow: 0 2rem 5rem rgb(0 0 0 / 35%);
      }
    }

    @media (max-width: 40rem) {
      .custom-title {
        font-size: clamp(2.25rem, 14vw, 4rem);
      }
    }
    ```

=== "pyproject.toml"

    ```toml title="pyproject.toml"
    [project]
    name = "hedron-composable-example"
    version = "0.1.0"
    requires-python = ">=3.10"
    dependencies = [
      "hedron>=1.0.0",
      "uvicorn[standard]>=0.32,<1.0",
    ]

    [tool.hedron]
    format_version = 1
    component_roots = ["components"]
    build_dir = ".hedron/build"
    theme = "default"
    explorer = "off"
    ```

Build the registered stylesheet once, then run the CSS version:

```bash
cd examples/composable-app
uv sync
uv run python -m hedron.cli --app custom_css:app build --dev
uv run uvicorn custom_css:app --reload
```

[Full code on GitHub](https://github.com/eddiethedean/hedron/tree/main/examples/composable-app)

## Why this boundary scales

- `app.py` owns HTTP routes, configuration, and application data.
- Component modules accept explicit inputs and return Hedron trees; they do not hide
  database reads or register routes as an import side effect.
- `components/__init__.py` is a small public surface. Callers do not need to know how
  the internal files are arranged.
- Parents receive components, not rendered HTML. Hedron can still validate, escape,
  style, and enhance the complete tree.

When one app becomes several, move the `components` package into its own distribution
without changing the composition model. Keep app-specific routes in the app and pass
data into the shared components.

[Compose built-ins](../guides/component-composition.md) ·
[Package author handbook](../guides/package-author-handbook.md) ·
[Test your UI](../guides/testing.md)
