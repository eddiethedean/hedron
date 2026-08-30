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
