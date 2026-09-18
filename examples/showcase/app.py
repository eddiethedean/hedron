"""Hedron Showcase: a polished, server-rendered operations console.

Run with::

    uv run uvicorn --app-dir examples/showcase app:app --reload

This is intentionally a single-file tour of Hedron's stable building blocks.
The data is synthetic; the boundaries are real.
"""

from __future__ import annotations

import os
from pathlib import Path

from starlette.staticfiles import StaticFiles

from hedron import (
    AccountSummary,
    ActionGroup,
    Alert,
    AppFooter,
    AppShell,
    AppShellChrome,
    Badge,
    Brand,
    Card,
    FlowStep,
    Grid,
    Hedron,
    Link,
    LinkButton,
    Metric,
    NavStatus,
    Page,
    PageHeader,
    ProcessFlow,
    Progress,
    ResourceList,
    ResourceRow,
    SafeUrl,
    SplitView,
    Stack,
    Status,
    Table,
    TableColumn,
    Text,
    Timeline,
    UrlPurpose,
    html,
    swap,
)
from hedron_core import NodeLike
from hedron_core.theme import folio_theme

PANEL_ID = "showcase-panel"

THEME = folio_theme()

app = Hedron(
    title="Hedron Showcase",
    security="standard",
    explorer="development",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "showcase-local-only"),
    theme="folio",
    accent=os.environ.get("HEDRON_ACCENT"),
    default_styles=True,
)
app.mount(
    "/showcase-assets",
    StaticFiles(directory=Path(__file__).parent / "assets"),
    name="showcase-assets",
)

pipeline_region = app.region("pipeline-card", description="Pipeline status")
approval_region = app.region("approval-card", description="Release approval")


def _nav_groups(current: str) -> dict[str, list[Link]]:
    entries = {
        "Operate": (("Overview", "/"), ("Deployments", "/deployments")),
        "Explore": (("Components", "/components"), ("Settings", "/settings")),
    }
    return {
        label: [
            Link(
                title,
                path,
                class_="hedron-nav-link active" if path == current else "hedron-nav-link",
            )
            for title, path in items
        ]
        for label, items in entries.items()
    }


def _chrome(title: str, current: str, *content: NodeLike) -> Page:
    return Page(
        AppShell(
            brand=Brand("Hedron", href="/", mark_text="H"),
            env_badge=Badge("Northstar workspace", tone="neutral"),
            account=AccountSummary("Alex Morgan", detail="Platform lead"),
            nav_groups=_nav_groups(current),
            nav_footer=Stack(
                NavStatus("All systems operational", tone="success"),
                Text("Live demo · synthetic data", as_="small"),
                gap="sm",
            ),
            app_footer=AppFooter("Hedron / Folio", "Built with Python · rendered on the server"),
            content_width="wide",
            chrome=AppShellChrome(
                preset="editorial",
                header_behavior="sticky",
                nav_behavior="sticky",
                nav_offset="header",
                shell_gap="standard",
                content_inset="none",
                banner_spacing="standard",
                header_density="compact",
            ),
            panel_id=PANEL_ID,
            body=Stack(*content, gap="lg"),
            class_="showcase-shell",
        ),
        title=f"{title} · Hedron Showcase",
        data_hedron_theme=app.hedron_theme,
        head=html.link(
            rel="stylesheet",
            href=SafeUrl.parse("/showcase-assets/showcase.css", purpose=UrlPurpose.NAVIGATION),
        ),
    )


def _metrics() -> Grid:
    return Grid(
        Metric("Rows processed", "1.28M", delta="↑ 18.4% this month", delta_tone="up"),
        Metric("Success rate", "98.7%", delta="↑ 2.1% this month", delta_tone="up"),
        Metric("Active pipelines", "24", delta="3 running now", delta_tone="neutral"),
        Metric("Median deploy", "11m", delta="↓ 24% this month", delta_tone="up"),
        columns=4,
        class_="showcase-metrics",
    )


def _pipeline_card(*, refreshed: bool = False) -> Card:
    flow = ProcessFlow(
        FlowStep("Ingest", status="complete", description="1,284 sources"),
        FlowStep("Validate", status="complete", description="42 checks passed"),
        FlowStep("Transform", status="current", description="18 / 24 partitions"),
        FlowStep("Publish", status="pending", description="Awaiting approval"),
        label="Data release pipeline",
        direction="horizontal",
        density="compact",
    )
    return Card(
        ActionGroup(
            Text("Warehouse sync", as_="strong"),
            Badge("Running", tone="info"),
            align="between",
        ),
        flow,
        id=pipeline_region.id,
        title="Data release pipeline",
        class_="showcase-pipeline",
        footer=ActionGroup(
            Text(
                "Transform in progress · refreshed just now"
                if refreshed
                else "Transform in progress · started 18m ago",
                as_="small",
            ),
            html.button(
                "Refresh pipeline",
                type="button",
                **{
                    "hx-get": "/pipeline/refresh",
                    "hx-target": pipeline_region.selector,
                    "hx-swap": "outerHTML",
                },
            ),
            align="between",
        ),
    )


def _approval_card(*, approved: bool = False) -> Card:
    body: list[NodeLike] = [
        ActionGroup(
            Text("v1.0.5-rc1", as_="strong"),
            Badge("Approved", tone="success")
            if approved
            else Badge("Needs review", tone="warning"),
            align="between",
        ),
        Text(
            "All checks passed. One final owner review before production."
            if not approved
            else "Release approved. The publish step is now queued for the worker pool."
        ),
        Progress(100 if approved else 75, label="Release readiness"),
        Text("Release approved" if approved else "3 of 4 release stages complete", as_="small"),
    ]
    if not approved:
        body.append(approve.button("Approve release"))
    return Card(*body, id=approval_region.id, title="Release gate", class_="showcase-approval")


@app.view("/pipeline/refresh", fragment_regions=(pipeline_region,))
def refresh_pipeline():
    return swap(_pipeline_card(refreshed=True))


@app.action("/approve", fallback="/", fragment_regions=(approval_region,))
def approve():
    return swap(
        _approval_card(approved=True),
        retarget=approval_region.selector,
        reswap="outerHTML",
    )


def _activity_card() -> Card:
    return Card(
        Timeline(
            [
                ("09:42", "Release candidate built", Text("v1.0.4 · 42 checks passed")),
                ("09:18", "Backfill completed", Text("96,410 customer records synced")),
                ("08:55", "Risk signal resolved", Text("Webhook latency returned to baseline")),
            ],
            label="Recent activity",
        ),
        title="Recent activity",
        class_="showcase-activity",
    )


def _transfers_card() -> Card:
    return Card(
        ResourceList(
            ResourceRow(
                "nightly-warehouse",
                description="Primary warehouse sync",
                meta=Badge("Running", tone="info"),
            ),
            ResourceRow(
                "crm-backfill",
                description="Historical customer import",
                meta=Badge("Succeeded", tone="success"),
            ),
            ResourceRow(
                "events-replay",
                description="Retry queue needs attention",
                meta=Badge("Review", tone="warning"),
            ),
            label="Active transfers",
        ),
        title="Active transfers",
    )


def _runs_card() -> Card:
    return Card(
        Table(
            columns=[
                TableColumn(header="Run", size="wide", priority=1),
                TableColumn(header="Status", kind="status", priority=1),
                TableColumn(header="Duration", align="end", priority=3),
                TableColumn(header="Rows", align="end", numeric=True, priority=4),
            ],
            rows=[
                ["nightly-warehouse", Badge("Running", tone="info"), "18m", "1,284,012"],
                ["crm-backfill", Badge("Succeeded", tone="success"), "42m", "96,410"],
                ["events-replay", Badge("Failed", tone="danger"), "4m", "0"],
                ["lookup-refresh", Badge("Queued", tone="neutral"), "—", "—"],
            ],
            caption="Recent runs",
            density="compact",
            sticky_header=True,
            zebra=False,
            responsive="priority",
        ),
        title="Recent runs",
        class_="showcase-runs",
        footer=ActionGroup(
            Text("4 latest runs · updated just now", as_="small"),
            Link("View deployments →", "/deployments"),
            align="between",
        ),
    )


@app.page("/")
def overview() -> Page:
    return _chrome(
        "Overview",
        "/",
        PageHeader(
            "Workspace overview",
            eyebrow="NORTHSTAR / OPERATIONS",
            description="Your pipelines, releases, and recent activity at a glance.",
            actions=ActionGroup(
                LinkButton("View deployments", "/deployments", appearance="outline"),
                label="Overview actions",
                align="end",
            ),
        ),
        _metrics(),
        SplitView(
            _pipeline_card(),
            _approval_card(),
            ratio="2:1",
            class_="showcase-workflow",
        ),
        SplitView(_runs_card(), _activity_card(), ratio="2:1", class_="showcase-details"),
        _transfers_card(),
    )


@app.page("/deployments")
def deployments() -> Page:
    return _chrome(
        "Deployments",
        "/deployments",
        PageHeader(
            "Deployments",
            eyebrow="OPERATE",
            description="Release history, checks, and environment promotion in one view.",
        ),
        Grid(
            Card(
                Badge("Production", tone="success"),
                Text("v1.0.4", as_="strong"),
                Text("Deployed 18 minutes ago · 42 checks passed", as_="small"),
                Progress(100, label="Deployment complete"),
                title="Current release",
            ),
            Card(
                Badge("Staging", tone="info"),
                Text("v1.0.5-rc1", as_="strong"),
                Text("Waiting for release owner approval", as_="small"),
                Progress(64, label="Release checklist progress"),
                title="Next release",
            ),
            columns=2,
        ),
        _runs_card(),
    )


@app.page("/components")
def components() -> Page:
    return _chrome(
        "Components",
        "/components",
        PageHeader(
            "Component gallery",
            eyebrow="EXPLORE",
            description="The same primitives are ordinary Python values, ready to compose.",
        ),
        Grid(
            Card(
                Badge("Success", tone="success"),
                Badge("Info", tone="info"),
                Badge("Warning", tone="warning"),
                Badge("Danger", tone="danger"),
                title="Feedback states",
            ),
            Card(
                Status("Healthy service", tone="success"),
                Status("Queued worker", tone="info"),
                Status("Needs attention", tone="warning"),
                title="Operational status",
            ),
            columns=2,
        ),
        Grid(
            Card(
                Progress(78, label="78 percent complete"),
                Text("Build manifest · 78% complete"),
                title="Progress",
            ),
            _activity_card(),
            columns=2,
        ),
    )


@app.page("/settings")
def settings() -> Page:
    return _chrome(
        "Settings",
        "/settings",
        PageHeader(
            "Workspace settings",
            eyebrow="EXPLORE",
            description="Typed controls, explicit ownership, and safe server boundaries.",
        ),
        Card(
            html.dl(
                html.dt("Workspace"),
                html.dd("Northstar Operations"),
                html.dt("Data region"),
                html.dd("us-east"),
                html.dt("Session policy"),
                html.dd("Standard · CSRF protected"),
                html.dt("Cache mode"),
                html.dd("Bounded application scope"),
            ),
            title="Runtime configuration",
        ),
        Alert(
            "Authentication, authorization, persistence, tenancy, and audit storage remain "
            "application responsibilities.",
            title="Ownership boundary",
            tone="info",
        ),
    )
