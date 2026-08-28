"""Page/session WebSocket channel contracts (phase 0.10)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Literal

from hedron_core.typing_aliases import JsonValue

__all__ = [
    "ChannelBudget",
    "ChannelMessage",
    "ClientStateRead",
    "PageSessionChannel",
    "RegionUpdate",
]


@dataclass(frozen=True, slots=True)
class ChannelBudget:
    max_messages: int = 10_000
    max_message_bytes: int = 64_000
    max_batch: int = 32
    debounce_ms: int = 0
    idle_timeout_seconds: float = 300.0


@dataclass(frozen=True, slots=True)
class ClientStateRead:
    """Declared client component value the channel may read."""

    component_id: str
    field: str


@dataclass(frozen=True, slots=True)
class RegionUpdate:
    region_id: str
    html: str
    swap: str = "innerHTML"


@dataclass(frozen=True, slots=True)
class ChannelMessage:
    kind: Literal["region-update", "client-state-request", "ping", "close", "error"]
    payload: Mapping[str, JsonValue] = field(default_factory=dict)


@dataclass(slots=True)
class PageSessionChannel:
    """Accepted bidirectional channel scoped to a page/session."""

    channel_id: str
    declared_regions: frozenset[str]
    declared_client_reads: tuple[ClientStateRead, ...] = ()
    budget: ChannelBudget = field(default_factory=ChannelBudget)
    fallback: Literal["sse", "poll", "http"] = "sse"
    messages_sent: int = 0

    def validate_region(self, region_id: str) -> None:
        if region_id not in self.declared_regions:
            raise ValueError(f"undeclared region {region_id!r}")

    def validate_client_read(self, component_id: str, field: str) -> None:
        allowed = {(item.component_id, item.field) for item in self.declared_client_reads}
        if (component_id, field) not in allowed:
            raise ValueError(f"undeclared client read {component_id}.{field}")

    def _prepare_region_update(self, update: RegionUpdate) -> ChannelMessage:
        from hedron_core.htmx_contract import safe_hx_swap

        self.validate_region(update.region_id)
        if not safe_hx_swap(update.swap):
            raise ValueError(f"Unsafe HTMX swap value: {update.swap!r}")
        encoded = ChannelMessage(
            kind="region-update",
            payload={
                "region_id": update.region_id,
                "html": update.html,
                "swap": update.swap,
            },
        )
        size = len(update.html.encode("utf-8"))
        if size > self.budget.max_message_bytes:
            raise ValueError("region update exceeds max_message_bytes")
        return encoded

    def encode_region_update(self, update: RegionUpdate) -> ChannelMessage:
        encoded = self._prepare_region_update(update)
        if self.messages_sent >= self.budget.max_messages:
            raise RuntimeError("channel message budget exhausted")
        self.messages_sent += 1
        return encoded

    def batch_updates(self, updates: Sequence[RegionUpdate]) -> list[ChannelMessage]:
        if len(updates) > self.budget.max_batch:
            raise ValueError("batch exceeds max_batch")
        encoded = [self._prepare_region_update(update) for update in updates]
        if self.messages_sent + len(encoded) > self.budget.max_messages:
            raise RuntimeError("channel message budget exhausted")
        self.messages_sent += len(encoded)
        return encoded
