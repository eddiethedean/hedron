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
