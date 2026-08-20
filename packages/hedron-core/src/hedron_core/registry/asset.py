"""Static asset registry catalog."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

_VALID_PLACEMENTS = frozenset({"head", "after_htmx_core", "body_end"})


@dataclass(frozen=True, slots=True)
class AssetMeta:
    logical_id: str
    kind: str
    path: str
    digest: str
    content_type: str
    attributes: Mapping[str, str] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()
    placement: str = "head"

    def __post_init__(self) -> None:
        if self.placement not in _VALID_PLACEMENTS:
            raise ValueError(
                f"placement must be one of {sorted(_VALID_PLACEMENTS)}; got {self.placement!r}"
            )


def register_asset(
    *,
    logical_id: str,
    kind: str,
    path: str,
    digest: str,
    content_type: str,
    attributes: Mapping[str, str] | None = None,
    depends_on: Sequence[str] | None = None,
    placement: str = "head",
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
            depends_on=tuple(depends_on or ()),
            placement=placement,
        )
    )
