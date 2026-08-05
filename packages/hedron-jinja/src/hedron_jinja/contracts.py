"""Typed contracts for the HDJ source format and render boundary."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Generic, TypeVar

from hedron_core import Model, RenderMode, SafeUrl, TrustedHtml
from hedron_core.typing_aliases import JsonValue

ViewT = TypeVar("ViewT", bound=Model)
_LOGICAL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
_REGION_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]*$")


class TemplateSource(StrEnum):
    APPLICATION = "application"
    PACKAGE = "package"


class TemplateKind(StrEnum):
    PAGE = "page"
    FRAGMENT = "fragment"
    LIBRARY = "library"

    @property
    def render_mode(self) -> RenderMode | None:
        if self is TemplateKind.PAGE:
            return RenderMode.PAGE
        if self is TemplateKind.FRAGMENT:
            return RenderMode.FRAGMENT
        return None


@dataclass(frozen=True, slots=True)
class TemplateSpec(Generic[ViewT]):
    """Application-side assertion about one HDJ entry point.

    Source kind, features, and unconditional assets remain owned by the source
    prologue. Application fields may tighten or add to that contract but cannot
    override it.
    """

    name: str
    view_type: type[ViewT] | None = None
    mode: RenderMode | None = None
    source: TemplateSource = TemplateSource.APPLICATION
    logical_id: str | None = None
    assets: tuple[str, ...] = ()
    fragment_regions: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))
    strict: bool = True

    def __post_init__(self) -> None:
        validate_template_name(self.name)
        if not self.name.endswith(".hdj"):
            raise ValueError("HDJ template names must end with '.hdj'")
        if self.view_type is not None and (
            not isinstance(self.view_type, type) or not issubclass(self.view_type, Model)
        ):
            raise TypeError("view_type must be a Hedron Model subclass")
        if self.mode is not None and not isinstance(self.mode, RenderMode):
            raise TypeError("mode must be a RenderMode")
        if not isinstance(self.source, TemplateSource):
            raise TypeError("source must be a TemplateSource")
        if not isinstance(self.strict, bool):
            raise TypeError("strict must be a bool")
        if self.logical_id is None:
            object.__setattr__(self, "logical_id", f"{self.source.value}:{self.name}")
        if not isinstance(self.logical_id, str) or not _LOGICAL_ID_RE.fullmatch(self.logical_id):
            raise ValueError("logical_id must be a canonical non-empty ID")
        assets = tuple(self.assets)
        invalid_assets = any(
            not isinstance(asset, str) or not _LOGICAL_ID_RE.fullmatch(asset) for asset in assets
        )
        if invalid_assets or len(assets) != len(set(assets)):
            raise ValueError("assets must contain unique canonical logical IDs")
        regions = dict(self.fragment_regions)
        if any(
            not isinstance(region_id, str)
            or not _REGION_ID_RE.fullmatch(region_id)
            or not isinstance(selector, str)
            or not selector.strip()
            for region_id, selector in regions.items()
        ):
            raise ValueError("fragment_regions must map canonical IDs to non-empty selectors")
        object.__setattr__(self, "assets", assets)
        object.__setattr__(
            self,
            "fragment_regions",
            MappingProxyType(regions),
        )


@dataclass(frozen=True, slots=True)
class TemplateDeclaration:
    name: str
    format_version: int
    kind: TemplateKind
    profile: str
    declared_features: frozenset[str]
    effective_features: frozenset[str]
    requires: frozenset[str]
    assets: tuple[str, ...]
    regions: tuple[str, ...]
    source_digest: str
    body_start_line: int


@dataclass(frozen=True, slots=True)
class TemplateCapabilities:
    name: str
    declared: frozenset[str]
    inferred: frozenset[str]
    dependencies: tuple[str, ...] = ()

    @property
    def missing_declarations(self) -> frozenset[str]:
        return self.inferred - self.declared

    @property
    def unused_declarations(self) -> frozenset[str]:
        return self.declared - self.inferred


@dataclass(frozen=True, slots=True)
class HdjContext:
    """Small immutable presentation facade exposed as ``hdj``."""

    mode: RenderMode
    locale: str
    theme: str | None
    htmx: Mapping[str, JsonValue] = field(default_factory=lambda: MappingProxyType({}))
    _url_builder: Callable[..., SafeUrl] | None = field(default=None, repr=False, compare=False)
    _asset_builder: Callable[[str], SafeUrl] | None = field(default=None, repr=False, compare=False)
    _csrf_builder: Callable[[], TrustedHtml] | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "htmx", MappingProxyType(dict(self.htmx)))

    @property
    def is_fragment(self) -> bool:
        return self.mode is RenderMode.FRAGMENT

    def url(self, ref: object, **params: JsonValue) -> SafeUrl:
        if self._url_builder is None:
            raise RuntimeError("No framework URL builder is configured for this HDJ binding")
        return self._url_builder(ref, **params)

    def asset_url(self, logical_id: str) -> SafeUrl:
        if self._asset_builder is None:
            raise RuntimeError("No asset URL builder is configured for this HDJ binding")
        return self._asset_builder(logical_id)

    def csrf_input(self) -> TrustedHtml:
        if self._csrf_builder is None:
            raise RuntimeError("No framework CSRF builder is configured for this HDJ binding")
        return self._csrf_builder()


def validate_template_name(name: str) -> None:
    if not name or "\x00" in name or "\\" in name or name.startswith("/"):
        raise ValueError(f"invalid canonical template name: {name!r}")
    segments = name.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise ValueError(f"invalid canonical template name: {name!r}")
