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
