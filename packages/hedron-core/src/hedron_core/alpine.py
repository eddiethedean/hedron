"""Typed, CSP-aware Alpine authoring and document-plan contracts.

The module deliberately contains no browser runtime.  It is the framework-neutral
representation shared by Python components, HDJ, asset planning, diagnostics, and
the browser projection.  Expressions are data until a reviewed browser module
consumes them; ordinary strings never become executable Alpine expressions.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Final, TypeAlias, cast

__all__ = [
    "ALPINE_PLAN_SCHEMA",
    "AlpineAttrs",
    "AlpineDirective",
    "AlpineExpression",
    "AlpineFeatureDemand",
    "AlpineMaturity",
    "BrowserPlanError",
    "BrowserFeaturePlan",
    "BrowserPlanClosure",
    "browser_assets_for_features",
    "ReviewedExpression",
]

ALPINE_PLAN_SCHEMA: Final = "hedron.alpine-plan/1"
_NAME = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*$")
_DIRECTIVE = re.compile(r"^x-[a-z][a-z0-9-]*(?::[A-Za-z0-9_.-]+)?(?:\.[a-z0-9-]+)*$")
_EVENT = re.compile(r"^[a-z][a-z0-9:.-]{0,63}$")
_REVIEWED = re.compile(
    r"^[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*(?:\([^;{}<>]*\))?$"
)
_FOR = re.compile(
    r"^[A-Za-z_$][A-Za-z0-9_$]*\s+in\s+[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*$"
)
_MODIFIER = re.compile(r"^(?:[a-z][a-z0-9-]*|(?:0|[1-9][0-9]{0,3})(?:ms|s))$")
_KNOWN_MODIFIERS = frozenset(
    {
        "prevent", "stop", "outside", "window", "document", "once", "self",
        "camel", "dot", "passive", "capture", "debounce", "throttle", "enter",
        "escape", "tab", "space", "shift", "ctrl", "alt", "meta", "up", "down",
        "left", "right", "home", "end", "page-up", "page-down", "delete", "backspace",
        "lazy", "change", "blur", "number", "boolean", "fill",
    }
)
_KEY_MODIFIERS = frozenset(
    {"f" + str(index) for index in range(1, 13)}
    | {chr(code) for code in range(ord("a"), ord("z") + 1)}
    | {str(index) for index in range(10)}
)
_FORBIDDEN_GLOBALS = re.compile(
    r"(?:^|[^A-Za-z0-9_$])(window|document|globalThis|fetch|XMLHttpRequest|location|history|"
    r"eval|Function|constructor|prototype|__proto__)(?:$|[^A-Za-z0-9_$])"
)
_UNSAFE_BIND_TARGETS = frozenset(
    {"class", "style", "href", "src", "action", "formaction", "poster", "ping"}
)
_ALPINE_PLUGIN_ASSETS = {
    "anchor": "/hedron-static/alpine/anchor-3.16.3.js",
    "collapse": "/hedron-static/alpine/collapse-3.16.3.js",
    "focus": "/hedron-static/alpine/focus-3.16.3.js",
    "intersect": "/hedron-static/alpine/intersect-3.16.3.js",
    "mask": "/hedron-static/alpine/mask-3.16.3.js",
    "morph": "/hedron-static/alpine/morph-3.16.3.js",
    "persist": "/hedron-static/alpine/persist-3.16.3.js",
    "resize": "/hedron-static/alpine/resize-3.16.3.js",
    "sort": "/hedron-static/alpine/sort-3.16.3.js",
    "ui": "/hedron-static/alpine/ui-3.16.3.js",
}
_ALPINE_CORE_ASSET = "/hedron-static/alpine/csp-3.16.3.js"
_HEDRON_BRIDGE_ASSET = "/hedron-static/hedron-alpine.mjs"


def _asset_sort_key(asset: str) -> tuple[int, str]:
    """Load plugins before CSP core, then install the HTMX bridge."""
    if asset == _ALPINE_CORE_ASSET:
        return (1, asset)
    if asset == _HEDRON_BRIDGE_ASSET:
        return (2, asset)
    return (0, asset)

JsonValue: TypeAlias = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


def browser_assets_for_features(features: Iterable[str]) -> tuple[str, ...]:
    """Resolve feature names to deterministic local plugin paths."""
    selected: set[str] = set()
    for feature in features:
        normalized = str(feature).strip().lower()
        if normalized in _ALPINE_PLUGIN_ASSETS:
            selected.add(_ALPINE_PLUGIN_ASSETS[normalized])
        elif normalized.startswith("ui."):
            selected.add(_ALPINE_PLUGIN_ASSETS["ui"])
    return tuple(sorted(selected))


def _validate_modifiers(name: str) -> None:
    if ":" in name:
        suffix = name.split(":", 1)[1].split(".")[1:]
    elif "." in name:
        suffix = name.split(".", 1)[1:]
    else:
        return
    previous = ""
    for modifier in suffix:
        if not _MODIFIER.fullmatch(modifier) or (
            modifier not in _KNOWN_MODIFIERS and modifier not in _KEY_MODIFIERS
        ):
            raise ValueError(f"unsupported Alpine directive modifier {modifier!r}")
        if modifier.endswith(("ms", "s")) and previous not in {"debounce", "throttle"}:
            raise ValueError("duration modifiers must follow debounce or throttle")
        previous = modifier


class AlpineMaturity(StrEnum):
    """Maturity labels used by the 0.67 capability inventory."""

    SUPPORTED = "Supported"
    PROGRESSIVE = "Progressive"
    EXPERIMENTAL = "Experimental"
    EXCLUDED = "Excluded"


class BrowserPlanError(ValueError):
    """Deterministic diagnostic raised for an invalid document feature plan."""

    code = "HED-BROWSER-0671"

    def __init__(
        self,
        message: str,
        *,
        missing_features: Sequence[str] = (),
        missing_assets: Sequence[str] = (),
    ) -> None:
        self.missing_features = tuple(sorted(set(missing_features)))
        self.missing_assets = tuple(sorted(set(missing_assets)))
        super().__init__(message)


def _json_value(value: object, *, path: str = "value") -> JsonValue:
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and (value != value or value in {float("inf"), float("-inf")}):
            raise ValueError(f"{path} must be finite")
        return value
    if isinstance(value, Mapping):
        result: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"{path} mapping keys must be non-empty strings")
            result[key] = _json_value(item, path=f"{path}.{key}")
        return result
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [_json_value(item, path=f"{path}[{index}]") for index, item in enumerate(value)]
    raise TypeError(f"{path} must be JSON-compatible, got {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class AlpineFeatureDemand:
    """One typed request for a browser-local Alpine capability."""

    feature: str
    source: str
    maturity: AlpineMaturity = AlpineMaturity.SUPPORTED

    def __post_init__(self) -> None:
        feature = self.feature.strip()
        source = self.source.strip()
        if not feature or not _NAME.fullmatch(feature.replace("-", "_")):
            raise ValueError("feature must be a non-empty identifier")
        if not source:
            raise ValueError("feature demand source is required")
        object.__setattr__(self, "feature", feature)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "maturity", AlpineMaturity(self.maturity))

    def to_dict(self) -> dict[str, str]:
        return {
            "feature": self.feature,
            "source": self.source,
            "maturity": self.maturity.value,
        }


@dataclass(frozen=True, slots=True)
class BrowserFeaturePlan:
    """Immutable feature/asset plan for one PAGE document."""

    demands: tuple[AlpineFeatureDemand, ...] = ()
    assets: tuple[str, ...] = ()
    schema: str = ALPINE_PLAN_SCHEMA

    def __post_init__(self) -> None:
        if self.schema != ALPINE_PLAN_SCHEMA:
            raise ValueError(f"unsupported browser plan schema {self.schema!r}")
        demands = tuple(self.demands)
        by_key: dict[tuple[str, str], AlpineFeatureDemand] = {}
        for demand in demands:
            if not isinstance(demand, AlpineFeatureDemand):
                raise TypeError("demands must contain AlpineFeatureDemand values")
            by_key[(demand.feature, demand.source)] = demand
        requested_assets = tuple(
            sorted(
                {str(asset).strip() for asset in self.assets if str(asset).strip()},
                key=_asset_sort_key,
            )
        )
        # A plan is a capability closure, not a bag of caller-managed script tags.
        # Any Alpine demand owns the local CSP runtime and the exact plugin asset
        # implied by that capability.
        demanded_features = {demand.feature for demand in demands}
        derived_assets = set(requested_assets)
        if demanded_features:
            derived_assets.update({_ALPINE_CORE_ASSET, _HEDRON_BRIDGE_ASSET})
            derived_assets.update(browser_assets_for_features(demanded_features))
        assets = tuple(sorted(derived_assets, key=_asset_sort_key))
        if any(
            not asset.startswith("/hedron-static/")
            or any(character.isspace() for character in asset)
            for asset in assets
        ):
            raise ValueError("browser plan assets must be same-origin /hedron-static paths")
        object.__setattr__(self, "demands", tuple(by_key[key] for key in sorted(by_key)))
        object.__setattr__(self, "assets", assets)

    @classmethod
    def from_demands(
        cls,
        demands: Sequence[AlpineFeatureDemand] = (),
        *,
        assets: Sequence[str] = (),
    ) -> BrowserFeaturePlan:
        return cls(tuple(demands), tuple(assets))

    @property
    def features(self) -> tuple[str, ...]:
        return tuple(sorted({demand.feature for demand in self.demands}))

    @property
    def feature_off(self) -> bool:
        return not self.demands and not self.assets

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(
            self.to_dict(include_fingerprint=False), sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def requires(self, feature: str) -> bool:
        return feature in self.features

    def add(self, *demands: AlpineFeatureDemand, assets: Sequence[str] = ()) -> BrowserFeaturePlan:
        return BrowserFeaturePlan(
            demands=self.demands + tuple(demands),
            assets=self.assets + tuple(assets),
            schema=self.schema,
        )

    def merge(self, other: BrowserFeaturePlan) -> BrowserFeaturePlan:
        if not isinstance(other, BrowserFeaturePlan):
            raise TypeError("can only merge another BrowserFeaturePlan")
        return self.add(*other.demands, assets=other.assets)

    def is_subset_of(self, installed: BrowserFeaturePlan) -> bool:
        # ``source`` is provenance, not capability identity.  A fragment rendered by
        # another view may legitimately name the same capability from a different
        # component/HDJ source.  Maturity remains fail-closed: an Excluded provider
        # cannot satisfy a demand.
        available = {
            demand.feature: demand.maturity
            for demand in installed.demands
            if demand.maturity is not AlpineMaturity.EXCLUDED
        }
        return all(
            demand.feature in available and available[demand.feature] is not AlpineMaturity.EXCLUDED
            for demand in self.demands
        ) and set(self.assets).issubset(installed.assets)

    def assert_subset_of(self, installed: BrowserFeaturePlan) -> None:
        if self.is_subset_of(installed):
            return
        missing_features = sorted(
            {d.feature for d in self.demands} - {d.feature for d in installed.demands}
        )
        missing_assets = sorted(set(self.assets) - set(installed.assets))
        raise BrowserPlanError(
            "browser feature plan is not a subset of the PAGE plan: "
            f"missing_features={missing_features!r}, missing_assets={missing_assets!r}",
            missing_features=missing_features,
            missing_assets=missing_assets,
        )

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        result: dict[str, object] = {
            "schema": self.schema,
            "demands": [demand.to_dict() for demand in self.demands],
            "assets": list(self.assets),
        }
        if include_fingerprint:
            result["fingerprint"] = self.fingerprint
        return result

    def with_fragment(self, name: str, plan: BrowserFeaturePlan) -> BrowserPlanClosure:
        """Start a statically declared fragment closure from this plan."""
        return BrowserPlanClosure(initial=self, fragments=((name, plan),))


@dataclass(frozen=True, slots=True)
class BrowserPlanClosure:
    """Immutable PAGE plan plus statically reachable fragment requirements.

    The closure is compiled before a PAGE response is emitted.  ``document_plan``
    is the only plan allowed to reach asset injection; ``fragment(name)`` verifies
    that a later fragment is covered by that installed plan without registering
    response-time modules or plugins.
    """

    initial: BrowserFeaturePlan = field(default_factory=BrowserFeaturePlan)
    fragments: tuple[tuple[str, BrowserFeaturePlan], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.initial, BrowserFeaturePlan):
            raise TypeError("initial must be a BrowserFeaturePlan")
        normalized: dict[str, BrowserFeaturePlan] = {}
        for name, plan in self.fragments:
            key = str(name).strip()
            if not key:
                raise ValueError("fragment name is required")
            if not isinstance(plan, BrowserFeaturePlan):
                raise TypeError("fragment plans must be BrowserFeaturePlan values")
            if key in normalized:
                raise ValueError(f"duplicate browser fragment declaration {key!r}")
            normalized[key] = plan
        object.__setattr__(
            self,
            "fragments",
            tuple((key, normalized[key]) for key in sorted(normalized)),
        )

    @property
    def document_plan(self) -> BrowserFeaturePlan:
        plan = self.initial
        for _, fragment in self.fragments:
            plan = plan.merge(fragment)
        return plan

    @property
    def fingerprint(self) -> str:
        return self.document_plan.fingerprint

    def add_fragment(self, name: str, plan: BrowserFeaturePlan) -> BrowserPlanClosure:
        return BrowserPlanClosure(self.initial, self.fragments + ((name, plan),))

    def fragment(self, name: str) -> BrowserFeaturePlan:
        key = str(name).strip()
        for fragment_name, plan in self.fragments:
            if fragment_name == key:
                plan.assert_subset_of(self.document_plan)
                return plan
        raise KeyError(f"unknown declared browser fragment {key!r}")

    def assert_fragment_subset(self, plan: BrowserFeaturePlan) -> None:
        plan.assert_subset_of(self.document_plan)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.document_plan.schema,
            "initial": self.initial.to_dict(),
            "fragments": {name: plan.to_dict() for name, plan in self.fragments},
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True, slots=True)
class AlpineExpression:
    """Small data-only expression AST accepted by the CSP authoring lane."""

    kind: str
    value: object = None
    args: tuple[AlpineExpression, ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in {"name", "literal", "call", "binary", "assign"}:
            raise ValueError("unsupported Alpine expression node")
        if self.kind == "name":
            if not isinstance(self.value, str) or _NAME.fullmatch(self.value) is None:
                raise ValueError("expression names must be simple identifiers or member paths")
        elif self.kind == "literal":
            object.__setattr__(self, "value", _json_value(self.value))
        elif self.kind == "call":
            if not isinstance(self.value, str) or _NAME.fullmatch(self.value) is None:
                raise ValueError("expression calls must target a named local method")
        elif self.kind == "binary":
            if self.value not in {
                "===",
                "!==",
                "==",
                "!=",
                "&&",
                "||",
                ">",
                ">=",
                "<",
                "<=",
                "+",
                "-",
            }:
                raise ValueError("unsupported expression operator")
            if len(self.args) != 2:
                raise ValueError("binary expressions require two operands")
        elif self.kind == "assign":
            if not isinstance(self.value, str) or _NAME.fullmatch(self.value) is None:
                raise ValueError("assignment targets must be named local state")
            if len(self.args) != 1:
                raise ValueError("assign expressions require one value")

    @classmethod
    def name(cls, value: str) -> AlpineExpression:
        return cls("name", value)

    @classmethod
    def literal(cls, value: object) -> AlpineExpression:
        return cls("literal", value)

    @classmethod
    def call(cls, name: str, *args: AlpineExpression) -> AlpineExpression:
        return cls("call", name, tuple(args))

    @classmethod
    def binary(
        cls, operator: str, left: AlpineExpression, right: AlpineExpression
    ) -> AlpineExpression:
        return cls("binary", operator, (left, right))

    @classmethod
    def assign(cls, name: str, value: AlpineExpression) -> AlpineExpression:
        return cls("assign", name, (value,))

    def to_source(self) -> str:
        if self.kind == "name":
            return str(self.value)
        if self.kind == "literal":
            return json.dumps(self.value, sort_keys=True, separators=(",", ":"))
        if self.kind == "call":
            return f"{self.value}({', '.join(arg.to_source() for arg in self.args)})"
        if self.kind == "binary":
            return f"({self.args[0].to_source()} {self.value} {self.args[1].to_source()})"
        return f"{self.value} = {self.args[0].to_source()}"

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {"kind": self.kind}
        if self.kind in {"name", "literal", "binary", "assign"}:
            result["value"] = self.value
        if self.args:
            result["args"] = [arg.to_dict() for arg in self.args]
        return result


@dataclass(frozen=True, slots=True)
class ReviewedExpression:
    """Explicit Advanced expression escape hatch.

    The value is still checked against the pinned, deliberately small grammar;
    marking an expression reviewed does not turn arbitrary JavaScript into a
    supported authoring path.
    """

    source: str
    provenance: str

    def __post_init__(self) -> None:
        if not self.source.strip() or _REVIEWED.fullmatch(self.source.strip()) is None:
            raise ValueError("reviewed expression is outside the CSP-safe grammar")
        if not self.provenance.strip():
            raise ValueError("reviewed expression provenance is required")
        if _FORBIDDEN_GLOBALS.search(self.source):
            raise ValueError("reviewed expression references a forbidden browser global")
        object.__setattr__(self, "source", self.source.strip())
        object.__setattr__(self, "provenance", self.provenance.strip())

    def to_source(self) -> str:
        return self.source


@dataclass(frozen=True, slots=True)
class AlpineDirective:
    """One normalized long-form Alpine directive."""

    name: str
    value: str | AlpineExpression | ReviewedExpression = ""
    features: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        name = self.name.strip()
        if name.startswith("@") or name.startswith(":") or _DIRECTIVE.fullmatch(name) is None:
            raise ValueError("Alpine directives must use normalized long-form x-* names")
        if name == "x-html":
            raise ValueError("x-html is excluded from the canonical Hedron Alpine API")
        if name.startswith("x-bind:"):
            target = name[7:].split(".", 1)[0].lower()
            if target in _UNSAFE_BIND_TARGETS:
                raise ValueError(
                    f"dynamic x-bind:{target} is not a typed safe sink; "
                    "use a Hedron URL/style binding"
                )
        if name.startswith("x-on:"):
            event = name[5:].split(".", 1)[0]
            if _EVENT.fullmatch(event) is None:
                raise ValueError("x-on event names must be bounded DOM event tokens")
        _validate_modifiers(name)
        if isinstance(self.value, (AlpineExpression, ReviewedExpression)):
            value = self.value.to_source()
        elif isinstance(self.value, str):
            value = self.value
            if value.strip():
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError:
                    parsed = None
                    if (
                        _REVIEWED.fullmatch(value.strip()) is None
                        and not (name == "x-for" and _FOR.fullmatch(value.strip()))
                    ):
                        raise ValueError(
                            "string Alpine expressions must use the reviewed CSP-safe grammar"
                        ) from None
                else:
                    _json_value(parsed, path=f"directive {name}")
        else:
            raise TypeError("directive value must be a string or typed expression")
        if any(token in value for token in ("<script", "javascript:", "data:text/html")):
            raise ValueError("directive value contains an executable or HTML-injection token")
        if _FORBIDDEN_GLOBALS.search(value):
            raise ValueError("directive value references a forbidden browser global")
        features = tuple(sorted({feature.strip() for feature in self.features if feature.strip()}))
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "features", features)

    @property
    def event(self) -> str | None:
        if not self.name.startswith("x-on:"):
            return None
        event = self.name[5:].split(".", 1)[0]
        return event if _EVENT.fullmatch(event) else None

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "value": str(self.value), "features": list(self.features)}


@dataclass(frozen=True, slots=True)
class AlpineAttrs:
    """Typed Alpine attributes accepted by Python components and ``html.*``."""

    directives: Mapping[str, object] | Sequence[AlpineDirective] = field(default_factory=dict)
    state: Mapping[str, object] = field(default_factory=dict)
    features: tuple[str, ...] = ()
    source: str = "python"

    def __post_init__(self) -> None:
        if isinstance(self.directives, Mapping):
            normalized = tuple(
                AlpineDirective(
                    str(name),
                    cast(str | AlpineExpression | ReviewedExpression, value),
                )
                for name, value in sorted(self.directives.items(), key=lambda item: str(item[0]))
            )
        else:
            normalized = tuple(self.directives)
            if not all(isinstance(item, AlpineDirective) for item in normalized):
                raise TypeError("directives must contain AlpineDirective values")
        by_name: dict[str, AlpineDirective] = {}
        for directive in normalized:
            if directive.name in by_name:
                raise ValueError(f"duplicate Alpine directive {directive.name!r}")
            by_name[directive.name] = directive
        state = _json_value(self.state, path="state")
        if not isinstance(state, dict):
            raise TypeError("Alpine state must be a mapping")
        features = set(str(feature).strip() for feature in self.features if str(feature).strip())
        if state:
            features.add("data")
        for directive in normalized:
            features.update(directive.features)
            if directive.name == "x-model" or directive.name.startswith("x-model."):
                features.add("model")
            elif directive.name == "x-modelable":
                features.add("modelable")
            elif directive.name.startswith("x-on:"):
                features.add("on")
            elif directive.name.startswith("x-bind:"):
                features.add("bind")
            elif directive.name.startswith("x-data"):
                features.add("data")
            else:
                base = directive.name.split(":", 1)[0].split(".", 1)[0]
                inferred = {
                    "x-show": "show",
                    "x-if": "if",
                    "x-for": "for",
                    "x-text": "text",
                    "x-transition": "transition",
                    "x-cloak": "cloak",
                    "x-init": "init",
                    "x-effect": "effect",
                    "x-ignore": "ignore",
                    "x-id": "id",
                    "x-teleport": "teleport",
                    "x-modelable": "modelable",
                }.get(base)
                if inferred:
                    features.add(inferred)
        if "x-data" in by_name and state:
            raise ValueError(
                "provide Alpine state either through state= or an x-data directive, not both"
            )
        object.__setattr__(self, "directives", tuple(by_name.values()))
        object.__setattr__(self, "state", MappingProxyType(state))
        object.__setattr__(self, "features", tuple(sorted(features)))
        if not self.source.strip():
            raise ValueError("AlpineAttrs source is required")

    @classmethod
    def data(cls, state: Mapping[str, object], *, source: str = "python") -> AlpineAttrs:
        return cls(state=state, source=source)

    @classmethod
    def on(
        cls,
        event: str,
        expression: AlpineExpression | ReviewedExpression,
        *,
        modifiers: Sequence[str] = (),
        features: Sequence[str] = (),
        source: str = "python",
    ) -> AlpineAttrs:
        if _EVENT.fullmatch(event.strip()) is None:
            raise ValueError("event must be a bounded DOM event name")
        suffix = "".join(f".{modifier}" for modifier in modifiers)
        return cls(
            directives=(
                AlpineDirective(f"x-on:{event.strip()}{suffix}", expression, tuple(features)),
            ),
            source=source,
        )

    @classmethod
    def bind(
        cls,
        name: str,
        value: object,
        *,
        features: Sequence[str] = (),
        source: str = "python",
    ) -> AlpineAttrs:
        if (
            not name
            or name.startswith(("@", ":"))
            or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]*", name)
        ):
            raise ValueError("bound attribute name must be a safe token")
        if isinstance(value, (AlpineExpression, ReviewedExpression)):
            directive_value: object = value
        else:
            directive_value = json.dumps(_json_value(value), sort_keys=True, separators=(",", ":"))
        return cls(
            directives=(AlpineDirective(f"x-bind:{name}", directive_value, tuple(features)),),
            source=source,
        )

    @classmethod
    def model(
        cls,
        name: str,
        *,
        modifiers: Sequence[str] = (),
        source: str = "python",
    ) -> AlpineAttrs:
        if _NAME.fullmatch(name.strip()) is None:
            raise ValueError("x-model must target a bounded local state path")
        suffix = "".join(f".{modifier.strip().lower()}" for modifier in modifiers)
        return cls(
            directives=(AlpineDirective(f"x-model{suffix}", name.strip()),),
            source=source,
        )

    @classmethod
    def text(
        cls,
        expression: AlpineExpression | ReviewedExpression,
        *,
        source: str = "python",
    ) -> AlpineAttrs:
        return cls(directives=(AlpineDirective("x-text", expression),), source=source)

    @classmethod
    def show(
        cls,
        expression: AlpineExpression | ReviewedExpression,
        *,
        source: str = "python",
    ) -> AlpineAttrs:
        return cls(directives=(AlpineDirective("x-show", expression),), source=source)

    def merge(self, other: AlpineAttrs) -> AlpineAttrs:
        """Compose typed attributes while rejecting duplicate writers."""
        if not isinstance(other, AlpineAttrs):
            raise TypeError("can only merge another AlpineAttrs value")
        overlap = set(self.state).intersection(other.state)
        for key in overlap:
            if self.state[key] != other.state[key]:
                raise ValueError(f"conflicting Alpine state writer for {key!r}")
        names = {
            directive.name
            for directive in cast(tuple[AlpineDirective, ...], self.directives)
        }
        other_directives = cast(tuple[AlpineDirective, ...], other.directives)
        duplicate = names.intersection(directive.name for directive in other_directives)
        if duplicate:
            raise ValueError(f"duplicate Alpine directive writer(s): {sorted(duplicate)!r}")
        return AlpineAttrs(
            directives=(
                *cast(tuple[AlpineDirective, ...], self.directives),
                *other_directives,
            ),
            state={**dict(self.state), **dict(other.state)},
            features=(*self.features, *other.features),
            source=f"{self.source}+{other.source}",
        )

    def to_attributes(self) -> dict[str, str]:
        result: dict[str, str] = {}
        if self.state:
            result["x-data"] = json.dumps(dict(self.state), sort_keys=True, separators=(",", ":"))
        for directive in cast(tuple[AlpineDirective, ...], self.directives):
            result[directive.name] = str(directive.value)
        return result

    def demands(self) -> tuple[AlpineFeatureDemand, ...]:
        return tuple(AlpineFeatureDemand(feature, self.source) for feature in self.features)

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "state": dict(self.state),
            "directives": [
                directive.to_dict()
                for directive in cast(tuple[AlpineDirective, ...], self.directives)
            ],
            "features": list(self.features),
        }
