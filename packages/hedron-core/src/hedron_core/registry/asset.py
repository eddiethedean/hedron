"""Static asset registry catalog."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AssetMeta:
    logical_id: str
    kind: str
    path: str
    digest: str
    content_type: str
    attributes: Mapping[str, str] = field(default_factory=dict)


def register_asset(
    *,
    logical_id: str,
    kind: str,
    path: str,
    digest: str,
    content_type: str,
    attributes: Mapping[str, str] | None = None,
) -> None:
    from hedron_core.registry.builder import active_builder

    active_builder().register_asset(
        AssetMeta(
            logical_id=logical_id,
            kind=kind,
            path=path,
            digest=digest,
            content_type=content_type,
            attributes=dict(attributes or {}),
        )
    )
