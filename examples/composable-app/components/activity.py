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
