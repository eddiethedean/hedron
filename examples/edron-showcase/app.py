"""Edron Showcase: a complete dashboard built with Edron's public API only.

Run with::

    uv run edron run app:app --reload

The data is synthetic and local. The example intentionally stays inside Edron's
class-oriented page, layout, fragment, action, chart, and data vocabulary.
"""

from __future__ import annotations

import os

import edron as ed

THEME = ed.theme(
    "edron-showcase",
    accent="#0d9488",
    density="comfortable",
    geometry="soft",
    elevation="subtle",
    navigation="default",
)

app = ed.App(
    title="Edron Showcase",
    security="standard",
    session_secret=os.environ.get("EDRON_SESSION_SECRET", "edron-showcase-local-only"),
    theme=THEME,
)

RUNS = [
    {"run": "nightly-warehouse", "status": "Running", "duration": "18m", "rows": "1,284,012"},
    {"run": "crm-backfill", "status": "Succeeded", "duration": "42m", "rows": "96,410"},
    {"run": "events-replay", "status": "Failed", "duration": "4m", "rows": "0"},
    {"run": "lookup-refresh", "status": "Queued", "duration": "—", "rows": "—"},
]

RUN_VOLUME = [
    {"day": "Mon", "runs": 42},
    {"day": "Tue", "runs": 58},
    {"day": "Wed", "runs": 51},
    {"day": "Thu", "runs": 74},
    {"day": "Fri", "runs": 68},
    {"day": "Sat", "runs": 39},
    {"day": "Sun", "runs": 47},
]


class ShowcasePage(ed.Page):
    """Shared Edron-only chrome for the showcase pages."""

    def shell(self, current: type[ed.Page]) -> ed.Container:
        with self.layout(ed.layout("grid", columns=2, gap="lg")):
            with self.sidebar:
                self.heading("EDRON", level=3)
                self.caption("Operations workspace")
                self.text("OPERATE")
                self.include(app.navigation_target(Overview).link("Overview"))
                self.include(app.navigation_target(Deployments).link("Deployments"))
                self.text("EXPLORE")
                self.include(app.navigation_target(Components).link("Components"))
                self.include(app.navigation_target(Settings).link("Settings"))
                self.divider()
                self.success("All systems operational")
                self.caption("Edron 1.0 stable surface")

            body = self.container()

        body.heading("Command center" if current is Overview else current.__name__)
        body.caption("A complete operations workspace composed from Edron page methods.")
        return body

    def metric_grid(self) -> None:
        columns = self.columns(4, gap="sm")
        values = (
            ("Monthly volume", "1.28M", "+18.4%"),
            ("Successful runs", "98.7%", "+2.1%"),
            ("Open incidents", "7", "−3"),
            ("Time to deploy", "11m", "−24%"),
        )
        for column, (label, value, delta) in zip(columns, values, strict=True):
            column.metric(label, value, delta=delta, delta_tone="up")


@app.page("/", title="Edron command center")
class Overview(ShowcasePage):
    @ed.fragment(path="/pipeline/refresh")
    def pipeline(self) -> None:
        with self.card(title="Data release pipeline") as card:
            card.info("Transform in progress · 18 of 24 partitions applied")
            card.text("Compose → validate → transform → publish")

    @ed.action(path="/pipeline/refresh", fallback="/")
    def refresh_pipeline(self) -> ed.Outcome:
        return ed.refresh(self.pipeline)

    @ed.action(path="/approve", fallback="/")
    def approve_release(self) -> ed.Outcome:
        return ed.success("Publish queued for the worker pool.")

    def render(self) -> None:
        with self.shell(Overview):
            self.success(
                "Everything is operating normally. The transform pipeline is the only active "
                "change."
            )
            self.metric_grid()

            workflow, release = self.columns(2, gap="md")
            with workflow.card(title="Pipeline visibility") as pipeline_card:
                self.pipeline()
                pipeline_card.button("Refresh pipeline", action=self.refresh_pipeline)
            with release.card(title="Release gate"):
                release.metric("Checklist", "64%", delta="42 checks passed", delta_tone="up")
                release.warning("Owner approval required before production publish.")
                release.button("Approve release", action=self.approve_release)

            runs, activity = self.columns(2, gap="md")
            with runs.card(title="Recent runs") as runs_card:
                runs_card.table(RUNS, caption="Bounded result set")
            with activity.card(title="Run volume") as activity_card:
                activity_card.line_chart(
                    RUN_VOLUME,
                    x="day",
                    y="runs",
                    title="Seven-day throughput",
                    description="Synthetic daily run volume for the current workspace.",
                )

            with self.card(title="What this showcases") as inventory:
                inventory.text(
                    "Pages, layouts, fragments, actions, metrics, tables, charts, and outcomes."
                )
                inventory.info("Every surface in this example is authored through Edron.")


@app.page("/deployments", title="Edron deployments")
class Deployments(ShowcasePage):
    def render(self) -> None:
        with self.shell(Deployments):
            current, next_release = self.columns(2, gap="md")
            with current.card(title="Current release") as card:
                card.success("Production")
                card.heading("v1.0.4", level=3)
                card.text("Deployed 18 minutes ago · 42 checks passed")
                card.metric("Readiness", "100%", delta="Healthy", delta_tone="up")
            with next_release.card(title="Next release") as card:
                card.info("Staging")
                card.heading("v1.0.5-rc1", level=3)
                card.text("Waiting for release owner approval")
                card.metric("Checklist", "64%", delta="Needs review", delta_tone="neutral")
            with self.card(title="Release history") as history:
                history.table(RUNS, caption="Recent release activity")


@app.page("/components", title="Edron components")
class Components(ShowcasePage):
    def render(self) -> None:
        with self.shell(Components):
            overview, feedback = self.tabs(("Composition", "Feedback"))
            overview.heading("A compact page vocabulary", level=2)
            overview.text(
                "Edron turns ordinary page methods into bounded, inspectable component trees."
            )
            overview.metric("Public methods", "30+", delta="Page vocabulary", delta_tone="up")
            overview.text("Layouts · data · charts · forms · jobs · downloads · browser plans")
            feedback.heading("Operational states", level=2)
            feedback.success("Healthy service")
            feedback.info("Queued worker")
            feedback.warning("Needs attention")
            feedback.error("Failed run")


@app.page("/settings", title="Edron settings")
class Settings(ShowcasePage):
    def render(self) -> None:
        with self.shell(Settings):
            with self.card(title="Workspace configuration") as config:
                config.text("Workspace · Northstar Operations")
                config.text("Data region · us-east")
                config.text("Session policy · Standard with CSRF protection")
                config.text("State model · Explicit application-owned resources")
            self.info(
                "Authentication, authorization, persistence, tenancy, and audit storage remain "
                "application responsibilities."
            )
            self.caption("Preview clock · 12:42:18 UTC · synthetic showcase data")
