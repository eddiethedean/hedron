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


def _deep_freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(item) for item in value)
    return value


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
    elements: tuple[str, ...] = ()
    element_abi: Mapping[str, int] = field(default_factory=lambda: MappingProxyType({}))
    element_modules: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))
    element_events: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "elements", tuple(self.elements))
        object.__setattr__(self, "element_abi", MappingProxyType(dict(self.element_abi)))
        object.__setattr__(self, "element_modules", MappingProxyType(dict(self.element_modules)))
        object.__setattr__(
            self,
            "element_events",
            MappingProxyType({tag: tuple(events) for tag, events in self.element_events.items()}),
        )


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
    htmx: Mapping[str, object] = field(default_factory=lambda: MappingProxyType({}))
    app_id: str | None = None
    binding_fingerprint: str | None = None
    themes: tuple[str, ...] = ()
    application_styles: tuple[Mapping[str, object], ...] = ()
    providers: Mapping[str, Mapping[str, object]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    _url_builder: Callable[..., SafeUrl] | None = field(default=None, repr=False, compare=False)
    _asset_builder: Callable[[str], SafeUrl] | None = field(default=None, repr=False, compare=False)
    _csrf_builder: Callable[[], TrustedHtml] | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "htmx", _deep_freeze(self.htmx))
        object.__setattr__(self, "themes", tuple(self.themes))
        object.__setattr__(
            self,
            "application_styles",
            tuple(_deep_freeze(item) for item in self.application_styles),
        )
        object.__setattr__(
            self,
            "providers",
            _deep_freeze(self.providers),
        )

    @property
    def is_fragment(self) -> bool:
        return self.mode is RenderMode.FRAGMENT

    def has_provider(self, feature_id: str) -> bool:
        """Return whether the frozen app binding includes a provider feature."""
        return feature_id in self.providers

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

    def scoped_style(self, declarations: str) -> str:
        """Emit a scoped-style helper string for template use (phase 0.14).

        Only layout custom properties are accepted (matching serializer policy).
        """
        text = declarations.strip().rstrip(";")
        if not text:
            return ""
        # Allow ``--hedron-*`` custom properties only.
        for part in text.split(";"):
            part = part.strip()
            if not part:
                continue
            if ":" not in part:
                raise ValueError(f"invalid scoped style declaration: {part!r}")
            name, _, value = part.partition(":")
            name = name.strip()
            if not name.startswith("--hedron-"):
                raise ValueError(
                    f"scoped_style only allows --hedron-* custom properties, got {name!r}"
                )
            if not value.strip():
                raise ValueError(f"empty value for {name!r}")
        return text

    def validate_attr(self, name: str, value: object) -> str:
        """Validate a static attribute name/value for template helpers (phase 0.14)."""
        import re

        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][\w.-]*", name):
            raise ValueError(f"unsafe attribute name: {name!r}")
        lower = name.lower()
        if lower.startswith("on") or lower in {"style", "srcdoc"}:
            raise ValueError(f"forbidden attribute for validate_attr: {name!r}")
        if value is None or value is False:
            return ""
        if value is True:
            return lower
        text = str(value)
        if "\x00" in text:
            raise ValueError("attribute value must not contain NUL")
        from html import escape

        return f'{lower}="{escape(text, quote=True)}"'


def validate_template_name(name: str) -> None:
    if not name or "\x00" in name or "\\" in name or name.startswith("/"):
        raise ValueError(f"invalid canonical template name: {name!r}")
    segments = name.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise ValueError(f"invalid canonical template name: {name!r}")
