"""Closed HTMX extension catalog, declaration, and render planning (0.10 / 0.48)."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from contextvars import ContextVar, Token
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Literal, TypedDict

from hedron_core.codes import (
    HED_EXT_0001,
    HED_EXT_0002,
    HED_EXT_0003,
    HED_EXT_0004,
    HED_EXT_0007,
    HED_EXT_0008,
    HED_EXT_0009,
)
from hedron_core.diagnostics import Diagnostic, DiagnosticSeverity, error, make_diagnostic

__all__ = [
    "ASSET_NAME_BY_PUBLIC_ID",
    "CLOSED_PUBLIC_IDS",
    "COMPAT_DEFAULT_IDS",
    "CONDITIONAL_PUBLIC_IDS",
    "EXCLUDED_PUBLIC_IDS",
    "ExtensionAsset",
    "ExtensionPlan",
    "ExtensionSet",
    "HDJ_FEATURE_PREFIX",
    "HtmxExtension",
    "MORPH_ADMITTED",
    "PRELOAD_INITIATION_MODES",
    "PUBLIC_ID_BY_ASSET_NAME",
    "SSE_EXTENSION_DEFERRED",
    "begin_extension_collect",
    "catalog_evidence_rows",
    "catalog_facts",
    "compile_extension_plan",
    "declare_page_extensions",
    "finish_extension_plan",
    "known_extensions",
    "normalize_public_id",
    "parse_htmx_extensions",
    "require_htmx_extension",
    "reset_extension_collect",
]

# Official SSE is Supported as an asset in 0.10; polling remains the required fallback.
SSE_EXTENSION_DEFERRED = False
# Idiomorph is not admitted on the 0.48 cut (MORPH-048 Deferred).
MORPH_ADMITTED = False

HDJ_FEATURE_PREFIX = "htmx.extension:"
PRELOAD_INITIATION_MODES = frozenset({"mousedown", "mouseover", "touchstart"})
COMPAT_DEFAULT_IDS = ("head-support", "sse")
EXCLUDED_PUBLIC_IDS = frozenset(
    {
        "response-targets",
        "multi-swap",
        "loading-states",
        "ws",
        "htmx-ws",
        "client-templates",
        "json-enc",
        "event-header",
        "htmx-1-compat",
        "htmx-1",
    }
)


class HtmxExtension(StrEnum):
    """Closed public identifiers used by ``hx-ext`` and HDJ ``extension_id``."""

    SSE = "sse"
    HEAD_SUPPORT = "head-support"
    PRELOAD = "preload"
    MORPH = "morph"
    HEDRON = "hedron"


CLOSED_PUBLIC_IDS = frozenset(
    {HtmxExtension.SSE, HtmxExtension.HEAD_SUPPORT, HtmxExtension.PRELOAD, HtmxExtension.HEDRON}
)
CONDITIONAL_PUBLIC_IDS = frozenset({HtmxExtension.MORPH})
ALL_PUBLIC_IDS = CLOSED_PUBLIC_IDS | CONDITIONAL_PUBLIC_IDS

ASSET_NAME_BY_PUBLIC_ID: Mapping[str, str] = MappingProxyType(
    {
        "sse": "htmx-ext-sse",
        "head-support": "htmx-ext-head-support",
        "preload": "htmx-ext-preload",
        "morph": "htmx-ext-idiomorph",
        "hedron": "htmx-ext-hedron",
    }
)
PUBLIC_ID_BY_ASSET_NAME: Mapping[str, str] = MappingProxyType(
    {asset: public for public, asset in ASSET_NAME_BY_PUBLIC_ID.items()}
)


@dataclass(frozen=True, slots=True)
class ExtensionAsset:
    name: str
    version: str
    digest: str
    path: str
    csp: str
    load_order: int
    deferred: bool = False
    notes: str = ""
    public_id: str = ""

    def __post_init__(self) -> None:
        if not self.public_id:
            mapped = PUBLIC_ID_BY_ASSET_NAME.get(self.name, "")
            object.__setattr__(self, "public_id", mapped)


def known_extensions() -> tuple[ExtensionAsset, ...]:
    return (
        ExtensionAsset(
            name="htmx-ext-head-support",
            version="2.0.5",
            digest="sha256-207f449ba70ad0d384b1734288ddae8493d26737bd74d8510829c0be5b737568",
            path="/hedron-static/ext/head-support.js",
            csp="script-src 'self'",
            load_order=10,
            deferred=False,
            notes="Optional head merge for registered fragment assets (RFC-0032).",
            public_id="head-support",
        ),
        ExtensionAsset(
            name="htmx-ext-preload",
            version="2.1.2",
            digest="sha256-7504ccd4c10e44b0aed3d62f30156e8a0abc7b9f18f3980f0fad58b465563466",
            path="/hedron-static/ext/preload.js",
            csp="script-src 'self'",
            load_order=20,
            deferred=False,
            notes="Official GET preload; never a compatibility default (D-083).",
            public_id="preload",
        ),
        ExtensionAsset(
            name="htmx-ext-sse",
            version="2.2.4",
            digest="sha256-3b5992a541619babefc4c169505af474df5c3039da51e59b96ccf9241ecd61d2",
            path="/hedron-static/ext/sse.js",
            csp="script-src 'self'",
            load_order=50,
            deferred=False,
            notes="Official SSE extension; polling remains Supported fallback (D-044).",
            public_id="sse",
        ),
        ExtensionAsset(
            name="htmx-ext-hedron",
            version="0.64.0",
            digest="sha256-02166a5a484eae08baa56215d9255077b0fc5fcd0eead28b13a178c62c31f23f",
            path="/hedron-static/ext/hedron.js",
            csp="script-src 'self'",
            load_order=60,
            deferred=False,
            notes="Opt-in Hedron lifecycle projection; no eval, network, or DOM ownership.",
            public_id="hedron",
        ),
    )


def _assets_by_public_id() -> dict[str, ExtensionAsset]:
    return {ext.public_id: ext for ext in known_extensions() if ext.public_id}


class ExtensionSet:
    """Immutable declared HTMX extension set (unset / empty / declared)."""

    __slots__ = ("_ids", "_kind")

    def __init__(self, ids: tuple[str, ...] = (), *, kind: Literal["unset", "empty", "declared"]):
        object.__setattr__(self, "_ids", ids)
        object.__setattr__(self, "_kind", kind)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("ExtensionSet is immutable")

    @classmethod
    def unset(cls) -> ExtensionSet:
        return cls((), kind="unset")

    @classmethod
    def empty(cls) -> ExtensionSet:
        return cls((), kind="empty")

    @classmethod
    def of(cls, ids: Iterable[str]) -> ExtensionSet:
        normalized = _normalize_id_tuple(ids)
        if not normalized:
            return cls.empty()
        return cls(normalized, kind="declared")

    @property
    def is_unset(self) -> bool:
        return self._kind == "unset"

    @property
    def is_empty(self) -> bool:
        return self._kind == "empty"

    @property
    def kind(self) -> Literal["unset", "empty", "declared"]:
        return self._kind

    @property
    def public_ids(self) -> tuple[str, ...]:
        return self._ids

    def __iter__(self) -> Iterator[str]:
        return iter(self._ids)

    def __len__(self) -> int:
        return len(self._ids)

    def __bool__(self) -> bool:
        return self._kind == "declared" and bool(self._ids)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExtensionSet):
            return NotImplemented
        return self._kind == other._kind and self._ids == other._ids

    def __hash__(self) -> int:
        return hash((self._kind, self._ids))

    def __repr__(self) -> str:
        if self.is_unset:
            return "ExtensionSet.unset()"
        if self.is_empty:
            return "ExtensionSet.empty()"
        return f"ExtensionSet.of({list(self._ids)!r})"


@dataclass(frozen=True, slots=True)
class ExtensionPlan:
    """Compiled PAGE/FRAGMENT extension activation for one render."""

    ids: tuple[str, ...]
    source: Literal["compat-default", "opt-out", "declared"]
    diagnostics: tuple[Diagnostic, ...] = ()
    inject: bool = True

    @property
    def hx_ext(self) -> str:
        return ",".join(self.ids)

    @property
    def assets(self) -> tuple[ExtensionAsset, ...]:
        by_id = _assets_by_public_id()
        out: list[ExtensionAsset] = []
        for public_id in self.ids:
            asset = by_id.get(public_id)
            if asset is not None and not asset.deferred:
                out.append(asset)
        return tuple(sorted(out, key=lambda item: item.load_order))

    def facts(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "public_ids": self.ids,
                "source": self.source,
                "hx_ext": self.hx_ext,
                "inject": self.inject,
                "assets": tuple(
                    {
                        "public_id": a.public_id,
                        "name": a.name,
                        "version": a.version,
                        "digest": a.digest,
                    }
                    for a in self.assets
                ),
            }
        )


def _compat_diagnostic() -> Diagnostic:
    return make_diagnostic(
        HED_EXT_0001,
        severity=DiagnosticSeverity.INFORMATION,
        title="Compatibility HTMX extension default",
        explanation=(
            "Unset Page.htmx_extensions injects the pinned 0.47 pair "
            "(sse and head-support) after HTMX core."
        ),
        remediation=(
            "Pass htmx_extensions=() or ExtensionSet.empty() to load zero extension "
            "bytes, or declare an explicit non-empty set."
        ),
    )


def _looks_like_url(value: str) -> bool:
    lowered = value.strip().lower()
    return (
        "://" in lowered
        or lowered.startswith("//")
        or lowered.startswith("http:")
        or lowered.startswith("https:")
        or "cdn." in lowered
    )


def normalize_public_id(value: str, *, allow_morph: bool = MORPH_ADMITTED) -> str:
    raw = str(value).strip()
    if not raw:
        raise error(
            HED_EXT_0002,
            title="Unknown HTMX extension id",
            explanation="Empty public id is not in the closed catalog.",
            remediation="Declare sse, head-support, preload, or (when admitted) morph.",
        )
    if _looks_like_url(raw):
        raise error(
            HED_EXT_0009,
            title="Request-derived or CDN extension id rejected",
            explanation=f"{raw!r} is a URL, not a closed public identifier.",
            remediation=(
                "Use a catalog public id and a pinned local asset; Hedron does not fetch CDNs."
            ),
        )
    mapped = PUBLIC_ID_BY_ASSET_NAME.get(raw, raw)
    if mapped in EXCLUDED_PUBLIC_IDS:
        raise error(
            HED_EXT_0002,
            title="Excluded HTMX extension id",
            explanation=f"{mapped!r} is out of the 0.48 inventory.",
            remediation="Use InteractionResult, OOB, indicators, or polling instead.",
        )
    if mapped == "morph" and not allow_morph:
        raise error(
            HED_EXT_0003,
            title="Morph HTMX extension is not admitted",
            explanation="MORPH-048 is Deferred; Idiomorph is not a Supported swap style.",
            remediation=(
                "Omit morph and keep innerHTML/outerHTML (or wait for a later admitting train)."
            ),
        )
    if mapped not in ALL_PUBLIC_IDS:
        raise error(
            HED_EXT_0002,
            title="Unknown HTMX extension id",
            explanation=f"{raw!r} is not a closed public id.",
            remediation="Declare hedron, sse, head-support, or preload.",
        )
    return mapped


def _normalize_id_tuple(ids: Iterable[str]) -> tuple[str, ...]:
    seen: dict[str, None] = {}
    for item in ids:
        seen[normalize_public_id(item)] = None
    by_id = _assets_by_public_id()
    return tuple(
        public_id
        for public_id, _asset in sorted(
            ((pid, by_id.get(pid)) for pid in seen),
            key=lambda pair: (pair[1].load_order if pair[1] is not None else 10_000, pair[0]),
        )
        if public_id
    )


def parse_htmx_extensions(value: object) -> ExtensionSet:
    """Parse ``Page(..., htmx_extensions=...)``. ``None`` is the UNSET sentinel."""
    if value is None:
        return ExtensionSet.unset()
    if isinstance(value, ExtensionSet):
        if value.is_unset or value.is_empty:
            return value
        return ExtensionSet.of(value.public_ids)
    if isinstance(value, str):
        return ExtensionSet.of((value,))
    if isinstance(value, Iterable):
        items = tuple(value)
        if not items:
            return ExtensionSet.empty()
        return ExtensionSet.of(str(item) for item in items)
    raise error(
        HED_EXT_0007,
        title="Invalid htmx_extensions declaration",
        explanation=f"Cannot parse htmx_extensions from {type(value).__name__}.",
        remediation="Pass None, (), a sequence of public ids, or an ExtensionSet.",
    )


def _is_page_mode(mode: object) -> bool:
    value = getattr(mode, "value", mode)
    return str(value) == "page"


def compile_extension_plan(
    *,
    declaration: ExtensionSet,
    required: Iterable[str] = (),
    mode: object = "page",
) -> ExtensionPlan:
    required_ids = _normalize_id_tuple(required)
    inject = _is_page_mode(mode)
    if declaration.is_empty:
        if required_ids:
            raise error(
                HED_EXT_0004,
                title="Opt-out conflicts with required HTMX extension",
                explanation=(
                    f"Page.htmx_extensions is empty but the tree requires {list(required_ids)!r}."
                ),
                remediation="Declare the required public ids or remove the requiring component.",
            )
        return ExtensionPlan(ids=(), source="opt-out", inject=inject)
    if declaration.is_unset:
        ids = _normalize_id_tuple((*COMPAT_DEFAULT_IDS, *required_ids))
        # Compatibility injection is a PAGE fact; fragments must not invent the diagnostic.
        diagnostics = (_compat_diagnostic(),) if inject else ()
        return ExtensionPlan(
            ids=ids,
            source="compat-default",
            diagnostics=diagnostics,
            inject=inject,
        )
    declared = declaration.public_ids
    missing = tuple(pid for pid in required_ids if pid not in declared)
    if missing and not _is_page_mode(mode):
        raise error(
            HED_EXT_0008,
            title="Undeclared fragment HTMX extension requirement",
            explanation=(
                f"Fragment requires {list(missing)!r} but Page.htmx_extensions "
                f"declared {list(declared)!r}."
            ),
            remediation="Declare the public ids on the document shell.",
        )
    ids = _normalize_id_tuple((*declared, *required_ids))
    return ExtensionPlan(ids=ids, source="declared", inject=inject)


_declaration: ContextVar[ExtensionSet | None] = ContextVar(
    "hedron_htmx_extension_declaration", default=None
)
_requirements: ContextVar[frozenset[str] | None] = ContextVar(
    "hedron_htmx_extension_requirements", default=None
)


def begin_extension_collect() -> tuple[Token[ExtensionSet | None], Token[frozenset[str] | None]]:
    return _declaration.set(None), _requirements.set(frozenset())


def reset_extension_collect(
    tokens: tuple[Token[ExtensionSet | None], Token[frozenset[str] | None]],
) -> None:
    _declaration.reset(tokens[0])
    _requirements.reset(tokens[1])


def declare_page_extensions(declaration: ExtensionSet) -> None:
    current = _declaration.get()
    if current is None:
        _declaration.set(declaration)


def require_htmx_extension(public_id: str) -> None:
    normalized = normalize_public_id(public_id)
    current = _requirements.get()
    if current is None:
        return
    _requirements.set(current | {normalized})


def finish_extension_plan(*, mode: object = "page") -> ExtensionPlan:
    declaration = _declaration.get()
    if declaration is None:
        declaration = ExtensionSet.unset()
    required = _requirements.get() or frozenset()
    return compile_extension_plan(declaration=declaration, required=required, mode=mode)


@dataclass(frozen=True, slots=True)
class HtmxCatalogFact:
    public_id: str
    asset_name: str
    version: str
    digest: str
    csp: str
    load_order: int
    deferred: bool
    kind: str = "htmx"


def catalog_evidence_rows() -> tuple[HtmxCatalogFact, ...]:
    return tuple(
        HtmxCatalogFact(
            public_id=ext.public_id,
            asset_name=ext.name,
            version=ext.version,
            digest=ext.digest,
            csp=ext.csp,
            load_order=ext.load_order,
            deferred=ext.deferred,
        )
        for ext in sorted(known_extensions(), key=lambda item: item.load_order)
        if ext.public_id
    )


class HtmxCatalogExtensionFact(TypedDict):
    public_id: str
    asset_name: str
    version: str
    digest: str
    csp: str
    load_order: int
    hdj_extension_id: str
    feature: str
    executes_untrusted_code: Literal[False]


class HtmxCatalogFacts(TypedDict):
    kind: Literal["htmx-extension-catalog"]
    new_catalog_kind: bool
    feature_bundle_executor: bool
    fourth_fingerprint_authority: bool
    hx_ext_never_installs: bool
    hdj_feature_prefix: str
    closed_public_ids: tuple[str, ...]
    conditional_public_ids: tuple[str, ...]
    morph_admitted: bool
    compat_default: tuple[str, ...]
    extensions: tuple[HtmxCatalogExtensionFact, ...]


def catalog_facts() -> HtmxCatalogFacts:
    """Inert catalog facts for Explorer, CLI, manifests, and HDJ projection."""
    payload: HtmxCatalogFacts = {
        "kind": "htmx-extension-catalog",
        "new_catalog_kind": False,
        "feature_bundle_executor": False,
        "fourth_fingerprint_authority": False,
        "hx_ext_never_installs": True,
        "hdj_feature_prefix": HDJ_FEATURE_PREFIX,
        "closed_public_ids": tuple(sorted(str(item) for item in CLOSED_PUBLIC_IDS)),
        "conditional_public_ids": tuple(sorted(str(item) for item in CONDITIONAL_PUBLIC_IDS)),
        "morph_admitted": MORPH_ADMITTED,
        "compat_default": COMPAT_DEFAULT_IDS,
        "extensions": tuple(
            {
                "public_id": row.public_id,
                "asset_name": row.asset_name,
                "version": row.version,
                "digest": row.digest,
                "csp": row.csp,
                "load_order": row.load_order,
                "hdj_extension_id": row.public_id,
                "feature": f"{HDJ_FEATURE_PREFIX}{row.public_id}",
                "executes_untrusted_code": False,
            }
            for row in catalog_evidence_rows()
        ),
    }
    return payload
