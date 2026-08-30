"""Hedron Showcase: a polished, server-rendered operations console.

Run with::

    uv run uvicorn --app-dir examples/showcase app:app --reload

This is intentionally a single-file tour of Hedron's stable building blocks.
The data is synthetic; the boundaries are real.
"""

from __future__ import annotations

import os

from hedron import (
    AccountSummary,
    ActionGroup,
    Alert,
    AppFooter,
    AppShell,
    AppShellChrome,
    Badge,
    Brand,
    Button,
    Card,
    EnvironmentBanner,
    FlowStep,
    Grid,
    Hedron,
    Link,
    Metric,
    NavStatus,
    Page,
    PageHeader,
    ProcessFlow,
    Progress,
    ResourceList,
    ResourceRow,
    Stack,
    Status,
    Table,
    TableColumn,
    Text,
    Theme,
    Timeline,
    compile_palette,
    html,
    swap,
)
from hedron_core import NodeLike
from hedron_core.theme import default_theme, register_theme_instance

PANEL_ID = "showcase-panel"

# The showcase deliberately uses the public theme authoring surface: one brand
# seed drives the accessible light/dark tokens, while Hedron owns the CSS.
BRAND = compile_palette("#0d9488")
THEME: Theme = default_theme().extend(
    "showcase",
    tokens=BRAND,
    palette={"brand.seed": "#0d9488", "brand.soft": BRAND["color.accent-soft"]},
    density="comfortable",
    shape={"radius": "0.65rem", "radius-lg": "1rem"},
    nav_width="13rem",
    elevation={"raised": "0 1px 2px rgb(15 23 42 / 8%)"},
)
register_theme_instance(THEME)

app = Hedron(
    title="Hedron Showcase",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "showcase-local-only"),
    theme=THEME.name,
    default_styles=True,
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
            banner=EnvironmentBanner(
                "Synthetic workspace · no customer data leaves this process",
                tone="info",
            ),
            brand=Brand("Hedron", href="/", mark_text="H"),
            env_badge=Text("SHOWCASE", role="label"),
            account=AccountSummary("alex@northstar.test", detail="Platform lead"),
            nav_groups=_nav_groups(current),
            nav_footer=Stack(
                NavStatus("All systems operational", tone="success"),
                Text("v1.0 stable surface", as_="small"),
                gap="sm",
            ),
            app_footer=AppFooter("Built with Python · rendered on the server"),
            content_width="wide",
            chrome=AppShellChrome(
                preset="editorial",
                header_behavior="sticky",
                nav_behavior="sticky",
                nav_offset="banner",
                shell_gap="editorial",
                content_inset="wide",
                banner_spacing="standard",
                header_density="spacious",
            ),
            panel_id=PANEL_ID,
            body=Stack(*content, gap="lg"),
        ),
        title=f"{title} · Hedron Showcase",
        data_hedron_theme=THEME.name,
    )


def _metrics() -> Grid:
    return Grid(
        Metric("Monthly volume", "1.28M", delta="+18.4%", delta_tone="up"),
        Metric("Successful runs", "98.7%", delta="+2.1%", delta_tone="up"),
        Metric("Open incidents", "7", delta="-3", delta_tone="up"),
        Metric("Time to deploy", "11m", delta="-24%", delta_tone="up"),
        columns=4,
    )


def _pipeline_card(*, refreshed: bool = False) -> Card:
    flow = ProcessFlow(
        FlowStep("Ingest", status="complete", description="1,284 sources connected"),
        FlowStep("Validate", status="complete", description="Zero schema drift detected"),
        FlowStep("Transform", status="current", description="18 of 24 partitions applied"),
        FlowStep("Publish", status="pending", description="Awaiting release approval"),
        label="Data release pipeline",
        direction="horizontal",
    )
    return Card(
        flow,
        Status(
            "Transform in progress · refreshed just now" if refreshed else "Transform in progress",
            variant="compact",
            tone="info",
        ),
        id=pipeline_region.id,
        title="Data release pipeline",
        footer=ActionGroup(
            html.button(
                "Refresh pipeline",
                type="button",
                **{
                    "hx-get": "/pipeline/refresh",
                    "hx-target": pipeline_region.selector,
                    "hx-swap": "outerHTML",
                },
            ),
            align="end",
        ),
    )


def _approval_card(*, approved: bool = False) -> Card:
    body: list[NodeLike] = [
        Text(
            "The production release is ready for the final owner check."
            if not approved
            else "Release approved. The publish step is now queued for the worker pool."
        ),
        Badge("Approved", tone="success") if approved else Badge("Needs review", tone="warning"),
    ]
    if not approved:
        body.append(approve.button("Approve release"))  # pyright: ignore[reportCallIssue]
    return Card(*body, id=approval_region.id, title="Release gate")


@app.action("/approve", fallback="/", fragment_regions=(approval_region,))
def approve():
    return swap(_approval_card(approved=True))


def _activity_card() -> Card:
    return Card(
        Timeline(
            [
                ("09:42", "Release candidate built", Text("v1.0.4 · 42 checks passed")),
                ("09:18", "Workspace upgraded", Text("Northstar moved to the Scale plan")),
                ("08:55", "Risk signal resolved", Text("Webhook latency returned to baseline")),
            ],
            label="Recent activity",
        ),
        title="Recent activity",
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
                TableColumn(header="Run", size="wide"),
                TableColumn(header="Status", kind="status"),
                TableColumn(header="Duration", align="end"),
                TableColumn(header="Rows", align="end", numeric=True),
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
            zebra=True,
        ),
        title="Recent runs",
    )


@app.page("/")
def overview() -> Page:
    return _chrome(
        "Overview",
        "/",
        PageHeader(
            "Command center",
            eyebrow="HEDRON / SHOWCASE",
            description="A complete server-rendered workspace composed from Python values.",
            actions=ActionGroup(
                Button("Export report", variant="secondary"),
                Button("New pipeline"),
                label="Overview actions",
                align="end",
            ),
        ),
        Alert(
            "Everything is operating normally. The transform pipeline is the only active change.",
            title="Workspace health",
            tone="success",
        ),
        _metrics(),
        Grid(
            _pipeline_card(),
            Stack(_approval_card(), Progress(64, label="64 percent of release checklist complete")),
            columns=2,
        ),
        Grid(_runs_card(), Stack(_transfers_card(), _activity_card(), gap="lg"), columns=2),
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
