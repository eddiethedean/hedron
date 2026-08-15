"""Theme registry catalog."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ThemeMeta:
    logical_id: str
    name: str
    tokens: Mapping[str, str]
    modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    variants: Mapping[str, Mapping[str, str]] = field(default_factory=dict)


def register_theme(
    *,
    logical_id: str,
    name: str,
    tokens: Mapping[str, str],
    modes: Mapping[str, Mapping[str, str]] | None = None,
    variants: Mapping[str, Mapping[str, str]] | None = None,
) -> None:
    from hedron_core.registry.builder import active_builder

    active_builder().register_theme(
        ThemeMeta(
            logical_id=logical_id,
            name=name,
            tokens=dict(tokens),
            modes={k: dict(v) for k, v in (modes or {}).items()},
            variants={k: dict(v) for k, v in (variants or {}).items()},
        )
    )
