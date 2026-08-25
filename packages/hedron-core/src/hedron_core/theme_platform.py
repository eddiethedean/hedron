"""Canonical custom-theme platform primitives for phase 0.60.

The 0.59 :class:`~hedron_core.theme.Theme` API remains the compatibility
surface.  This module adds the stricter authoring model used by 0.60:
validated colors, immutable specs and patches, registry-derived contracts,
categorical validation, and deterministic data-only packages.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import zipfile
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from io import BytesIO
from types import MappingProxyType
from typing import Any, Literal, cast

__all__ = [
    "Color",
    "ComponentThemeContract",
    "CoverageProfile",
    "RecipeFamily",
    "StyleContext",
    "THEME_PACKAGE_COMPATIBILITY",
    "THEME_COVERAGE_PROFILES",
    "ThemeBuilder",
    "ThemePackage",
    "ThemePatch",
    "ThemeSpec",
    "ThemeValidationReport",
    "conformance_report",
    "diff_theme_specs",
    "explain_theme_spec",
    "load_theme_package",
    "package_theme",
    "register_component_theme_contract",
    "registered_component_theme_contracts",
    "register_recipe_family",
    "registered_recipe_families",
    "register_theme_package",
    "validate_theme_spec",
]


_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")
_MODE_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_FUNCTION = re.compile(r"^(?P<name>[A-Za-z][A-Za-z0-9-]*)\((?P<body>.*)\)$", re.S)
_UNSAFE_CSS_VALUE = re.compile(r"[;{}<>@\\]|url\s*\(|/\*", re.IGNORECASE)
THEME_PACKAGE_COMPATIBILITY = ">=0.60,<0.64"


def _canonical(value: object) -> str:
    def thaw(item: Any) -> Any:
        if isinstance(item, Mapping):
            return {str(key): thaw(child) for key, child in item.items()}
        if isinstance(item, (tuple, list, set, frozenset)):
            return [thaw(child) for child in item]
        return item

    return json.dumps(thaw(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _freeze_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(
        {str(key): _freeze_value(item) for key, item in sorted((value or {}).items())}
    )


def _freeze_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _freeze_mapping(cast(Mapping[str, Any], value))
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(_freeze_value(item) for item in value)
    return value


def _validate_mode_values(
    modes: Mapping[str, Mapping[str, str]],
    *,
    allow_aliases: bool = False,
    field_name: str,
) -> None:
    for mode, values in modes.items():
        if not isinstance(mode, str) or not _MODE_NAME.fullmatch(mode):
            raise ValueError(f"{field_name} name must be a safe identifier: {mode!r}")
        if not isinstance(values, Mapping):
            raise ValueError(f"{field_name}[{mode!r}] must be a mapping")
        for key, value in values.items():
            if not isinstance(key, str) or not _NAME.fullmatch(key):
                raise ValueError(f"invalid {field_name}[{mode!r}] token key: {key!r}")
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name}[{mode!r}][{key!r}] must be a non-empty string")
            if allow_aliases and value.startswith("@") and _NAME.fullmatch(value[1:]):
                continue
            if _UNSAFE_CSS_VALUE.search(value):
                raise ValueError(f"unsafe theme value for {field_name}[{mode!r}][{key!r}]")


def _number(raw: str, *, scale: float = 1.0, percent: bool = False) -> float:
    text = raw.strip().lower()
    if text.endswith("%"):
        if not percent:
            raise ValueError(f"percentage is not valid here: {raw!r}")
        return float(text[:-1]) / 100.0 * scale
    return float(text) / scale


def _alpha(raw: str) -> float:
    value = _number(raw, percent=True)
    if not 0.0 <= value <= 1.0:
        raise ValueError("alpha must be between 0 and 1")
    return value


def _parts(body: str) -> tuple[list[str], str | None]:
    # CSS Color 4 permits either comma-separated legacy syntax or whitespace
    # syntax with an optional slash alpha channel.
    body = body.strip()
    if "/" in body:
        before, slash, alpha = body.rpartition("/")
        if not slash or not alpha.strip():
            raise ValueError("malformed alpha channel")
        alpha_value = alpha.strip()
    else:
        before, alpha_value = body, None
    raw = before.replace(",", " ").split()
    return raw, alpha_value


def _hue(raw: str) -> float:
    value = raw.strip().lower()
    if value.endswith("deg"):
        return float(value[:-3]) % 360.0
    if value.endswith("grad"):
        return float(value[:-4]) * 0.9 % 360.0
    if value.endswith("rad"):
        return math.degrees(float(value[:-3])) % 360.0
    if value.endswith("turn"):
        return float(value[:-4]) * 360.0 % 360.0
    return float(value) % 360.0


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _hsl_to_rgb(hue: float, saturation: float, lightness: float) -> tuple[float, float, float]:
    import colorsys

    return colorsys.hls_to_rgb((hue % 360.0) / 360.0, lightness, saturation)


def _oklab_to_rgb(lightness: float, a: float, b: float) -> tuple[float, float, float]:
    l_comp = lightness + 0.3963377774 * a + 0.2158037573 * b
    m_comp = lightness - 0.1055613458 * a - 0.0638541728 * b
    s_comp = lightness - 0.0894841775 * a - 1.2914855480 * b
    l3, m3, s3 = l_comp**3, m_comp**3, s_comp**3
    return (
        +4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3,
        -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3,
        -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3,
    )


def _lab_to_rgb(lightness: float, a: float, b: float) -> tuple[float, float, float]:
    # CIE Lab D50 -> XYZ D50 -> Bradford-adapted XYZ D65 -> sRGB.
    fy = (lightness + 16.0) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0
    epsilon = 216.0 / 24389.0
    kappa = 24389.0 / 27.0

    def inv(value: float) -> float:
        return value**3 if value**3 > epsilon else (116.0 * value - 16.0) / kappa

    xd, yd, zd = 0.96422 * inv(fx), 1.0 * inv(fy), 0.82521 * inv(fz)
    x = 1.0479298 * xd + 0.0229468 * yd - 0.0501922 * zd
    y = 0.0296278 * xd + 0.9904345 * yd - 0.0170738 * zd
    z = -0.0092430 * xd + 0.0150552 * yd + 0.7518743 * zd
    return (
        3.2404542 * x - 1.5371385 * y - 0.4985314 * z,
        -0.9692660 * x + 1.8760108 * y + 0.0415560 * z,
        0.0556434 * x - 0.2040259 * y + 1.0572252 * z,
    )


@dataclass(frozen=True, slots=True)
class Color:
    """Safe immutable absolute CSS color.

    Coordinates are normalized to the source space.  Conversion is pure
    Python and the serialized fallback is always canonical sRGB hex.
    Relative colors, variables, URLs, gradients, and arbitrary CSS are not
    accepted because they cannot produce deterministic theme evidence.
    """

    space: Literal["srgb", "hsl", "hwb", "oklab", "oklch", "lab", "lch"]
    coords: tuple[float, float, float]
    alpha: float = 1.0

    def __post_init__(self) -> None:
        if self.space not in {"srgb", "hsl", "hwb", "oklab", "oklch", "lab", "lch"}:
            raise ValueError(f"unsupported absolute color space: {self.space!r}")
        if len(self.coords) != 3 or not all(math.isfinite(v) for v in self.coords):
            raise ValueError("color coordinates must be finite")
        if not math.isfinite(self.alpha) or not 0.0 <= self.alpha <= 1.0:
            raise ValueError("color alpha must be between 0 and 1")

    @classmethod
    def srgb(cls, red: float, green: float, blue: float, *, alpha: float = 1.0) -> Color:
        return cls("srgb", (red, green, blue), alpha)

    @classmethod
    def rgb(cls, red: float, green: float, blue: float, *, alpha: float = 1.0) -> Color:
        """Construct an sRGB color using the CSS-facing constructor name."""
        return cls.srgb(red, green, blue, alpha=alpha)

    @classmethod
    def hsl(cls, hue: float, saturation: float, lightness: float, *, alpha: float = 1.0) -> Color:
        if not 0.0 <= saturation <= 1.0 or not 0.0 <= lightness <= 1.0:
            raise ValueError("hsl saturation and lightness must be between 0 and 1")
        return cls("hsl", (hue % 360.0, saturation, lightness), alpha)

    @classmethod
    def hwb(cls, hue: float, whiteness: float, blackness: float, *, alpha: float = 1.0) -> Color:
        if not 0.0 <= whiteness <= 1.0 or not 0.0 <= blackness <= 1.0:
            raise ValueError("hwb whiteness and blackness must be between 0 and 1")
        if whiteness + blackness > 1.0:
            raise ValueError("hwb whiteness plus blackness cannot exceed 1")
        return cls("hwb", (hue % 360.0, whiteness, blackness), alpha)

    @classmethod
    def lab(cls, lightness: float, a: float, b: float, *, alpha: float = 1.0) -> Color:
        return cls("lab", (lightness, a, b), alpha)

    @classmethod
    def lch(cls, lightness: float, chroma: float, hue: float, *, alpha: float = 1.0) -> Color:
        return cls("lch", (lightness, chroma, hue % 360.0), alpha)

    @classmethod
    def oklab(cls, lightness: float, a: float, b: float, *, alpha: float = 1.0) -> Color:
        return cls("oklab", (lightness, a, b), alpha)

    @classmethod
    def hex(cls, value: str) -> Color:
        if not isinstance(value, str) or not _HEX.fullmatch(value.strip()):
            raise ValueError(f"invalid hex color: {value!r}")
        digits = value.strip()[1:]
        if len(digits) in (3, 4):
            digits = "".join(char * 2 for char in digits)
        alpha = int(digits[6:8], 16) / 255.0 if len(digits) == 8 else 1.0
        return cls.srgb(*(int(digits[i : i + 2], 16) / 255.0 for i in (0, 2, 4)), alpha=alpha)

    @classmethod
    def oklch(cls, lightness: float, chroma: float, hue: float, *, alpha: float = 1.0) -> Color:
        return cls("oklch", (lightness, chroma, hue % 360.0), alpha)

    @classmethod
    def parse(cls, value: str | Color) -> Color:
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise ValueError("color must be a Color or string")
        text = value.strip()
        if _HEX.fullmatch(text):
            return cls.hex(text)
        match = _FUNCTION.fullmatch(text)
        if match is None:
            raise ValueError(f"unsupported or unsafe absolute color: {value!r}")
        name = match.group("name").lower()
        raw, alpha_raw = _parts(match.group("body"))
        if name in {"rgb", "rgba"}:
            if len(raw) not in (3, 4) or (len(raw) == 4 and alpha_raw is not None):
                raise ValueError("rgb() requires three channels and optional alpha")
            channels = tuple(
                float(item.strip()[:-1]) / 100.0
                if item.strip().endswith("%")
                else float(item.strip()) / 255.0
                for item in raw[:3]
            )
            if not all(0.0 <= channel <= 1.0 for channel in channels):
                raise ValueError("rgb channels must be between 0 and 255 or 0% and 100%")
            alpha = _alpha(raw[3]) if len(raw) == 4 else (_alpha(alpha_raw) if alpha_raw else 1.0)
            return cls("srgb", (channels[0], channels[1], channels[2]), alpha)
        if name in {"hsl", "hsla"}:
            if len(raw) not in (3, 4) or (len(raw) == 4 and alpha_raw is not None):
                raise ValueError("hsl() requires hue, saturation, lightness, and optional alpha")
            channels = (_hue(raw[0]), _number(raw[1], percent=True), _number(raw[2], percent=True))
            alpha = _alpha(raw[3]) if len(raw) == 4 else (_alpha(alpha_raw) if alpha_raw else 1.0)
            if not 0.0 <= channels[1] <= 1.0 or not 0.0 <= channels[2] <= 1.0:
                raise ValueError("hsl saturation and lightness must be percentages")
            return cls("hsl", channels, alpha)
        if name == "hwb":
            if len(raw) != 3:
                raise ValueError("hwb() requires hue, whiteness, and blackness")
            white, black = _number(raw[1], percent=True), _number(raw[2], percent=True)
            if white + black > 1.0:
                raise ValueError("hwb whiteness plus blackness cannot exceed 100%")
            return cls("hwb", (_hue(raw[0]), white, black), _alpha(alpha_raw) if alpha_raw else 1.0)
        if name in {"oklab", "oklch", "lab", "lch"}:
            if len(raw) != 3:
                raise ValueError(f"{name}() requires three coordinates")
            if name == "oklab":
                coords = (_number(raw[0], percent=True), float(raw[1]), float(raw[2]))
            elif name == "oklch":
                coords = (_number(raw[0], percent=True), float(raw[1]), _hue(raw[2]))
            elif name == "lab":
                lightness = float(raw[0].strip().removesuffix("%"))
                coords = (lightness, float(raw[1]), float(raw[2]))
            else:
                lightness = float(raw[0].strip().removesuffix("%"))
                coords = (lightness, float(raw[1]), _hue(raw[2]))
            return cls(name, coords, _alpha(alpha_raw) if alpha_raw else 1.0)  # type: ignore[arg-type]
        if name in {"url", "image", "linear-gradient", "radial-gradient"}:
            raise ValueError(f"unsupported or unsafe absolute color: {value!r}")
        raise ValueError(f"unsupported absolute color function: {name}()")

    def to_srgb(self) -> tuple[float, float, float]:
        if self.space == "srgb":
            return self.coords
        if self.space == "hsl":
            return _hsl_to_rgb(*self.coords)
        if self.space == "hwb":
            hue, white, black = self.coords
            base = _hsl_to_rgb(hue, 1.0, 0.5)
            factor = 1.0 - white - black
            adjusted = tuple(channel * factor + white for channel in base)
            return (adjusted[0], adjusted[1], adjusted[2])
        if self.space == "oklab":
            return _oklab_to_rgb(*self.coords)
        if self.space == "oklch":
            lightness, chroma, hue = self.coords
            radians = math.radians(hue)
            return _oklab_to_rgb(lightness, chroma * math.cos(radians), chroma * math.sin(radians))
        if self.space == "lab":
            return _lab_to_rgb(*self.coords)
        lightness, chroma, hue = self.coords
        radians = math.radians(hue)
        return _lab_to_rgb(lightness, chroma * math.cos(radians), chroma * math.sin(radians))

    @property
    def in_gamut(self) -> bool:
        return all(0.0 <= channel <= 1.0 for channel in self.to_srgb())

    def to_hex(self) -> str:
        channels = tuple(_clamp(channel) for channel in self.to_srgb())
        digits = "".join(f"{round(channel * 255):02x}" for channel in channels)
        if self.alpha < 1.0:
            digits += f"{round(self.alpha * 255):02x}"
        return f"#{digits}"

    def gamut_map(self) -> Color:
        """Return the deterministic clipped sRGB representation of this color."""
        red, green, blue = (_clamp(channel) for channel in self.to_srgb())
        return Color.srgb(red, green, blue, alpha=self.alpha)

    def to_css(self, *, fallback: bool = True) -> str:
        if fallback:
            return self.to_hex()
        if self.space == "srgb":
            return self.to_hex()
        values = " ".join(f"{value:.6g}" for value in self.coords)
        suffix = "" if self.alpha == 1.0 else f" / {self.alpha:.6g}"
        return f"{self.space}({values}{suffix})"


@dataclass(frozen=True, slots=True)
class ThemeSpec:
    """Immutable canonical theme input for 0.60."""

    name: str
    tokens: Mapping[str, str]
    modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    accessibility_modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    aliases: Mapping[str, str] = field(default_factory=dict)
    groups: Mapping[str, str] = field(default_factory=dict)
    recipes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema: str = "hedron.theme-spec/1"
    profile: str = "core"
    provenance: tuple[Mapping[str, Any], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _NAME.fullmatch(self.name):
            raise ValueError("theme spec name must be a safe identifier")
        if self.profile not in THEME_COVERAGE_PROFILES:
            raise ValueError(f"unknown theme coverage profile: {self.profile}")
        for field_name, mapping in (("tokens", self.tokens), ("aliases", self.aliases)):
            for key, value in mapping.items():
                if not isinstance(key, str) or not _NAME.fullmatch(key):
                    raise ValueError(f"invalid {field_name} key: {key!r}")
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{field_name}[{key!r}] must be a non-empty string")
                if any(char in value for char in ";{}<>") or "url(" in value.lower():
                    raise ValueError(f"unsafe theme value for {field_name}[{key!r}]")
        _validate_mode_values(self.modes, allow_aliases=True, field_name="mode")
        _validate_mode_values(self.accessibility_modes, field_name="accessibility mode")
        for key, value in self.groups.items():
            if (
                not _NAME.fullmatch(str(key))
                or not isinstance(value, str)
                or not _NAME.fullmatch(value)
            ):
                raise ValueError("theme groups must use safe identifiers")
        for family, values in self.recipes.items():
            if not _NAME.fullmatch(str(family)) or not isinstance(values, Mapping):
                raise ValueError("theme recipe families must use safe identifiers")
            for key, value in values.items():
                if (
                    not _NAME.fullmatch(str(key))
                    or not isinstance(value, str)
                    or not _NAME.fullmatch(value)
                ):
                    raise ValueError("theme recipe values must use safe identifiers")
        object.__setattr__(self, "tokens", _freeze_mapping(self.tokens))
        object.__setattr__(self, "modes", _freeze_mapping(self.modes))
        object.__setattr__(self, "accessibility_modes", _freeze_mapping(self.accessibility_modes))
        object.__setattr__(self, "aliases", _freeze_mapping(self.aliases))
        object.__setattr__(self, "groups", _freeze_mapping(self.groups))
        object.__setattr__(self, "recipes", _freeze_mapping(self.recipes))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))
        object.__setattr__(
            self,
            "provenance",
            tuple(_freeze_mapping(item) for item in self.provenance),
        )
        # Resolve all aliases during construction so invalid graphs cannot sit
        # in a registry or package waiting for a later render.
        for key in self.aliases:
            self.resolve_token(key)

    def resolve_token(self, key: str, *, mode: str | None = None) -> str:
        source = self.tokens
        if mode is not None:
            source = self.modes.get(mode, {})
            if key not in source:
                source = self.tokens
        value = source.get(key, self.aliases.get(key))
        if value is None:
            raise ValueError(f"unknown theme token: {key}")
        seen: set[str] = set()
        while isinstance(value, str) and value.startswith("@"):
            target = value[1:]
            if target in seen:
                raise ValueError(f"theme token alias cycle at {target!r}")
            seen.add(target)
            value = source.get(target, self.tokens.get(target, self.aliases.get(target)))
            if value is None:
                raise ValueError(f"theme token alias references missing token {target!r}")
        return value

    @property
    def resolved_tokens(self) -> Mapping[str, str]:
        return MappingProxyType({key: self.resolve_token(key) for key in sorted(self.tokens)})

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ThemeSpec:
        """Rehydrate a package payload while checking its canonical fingerprint."""
        if not isinstance(data, Mapping):
            raise ValueError("theme spec payload must be an object")
        spec = cls(
            name=str(data.get("name", "")),
            tokens=cast(Mapping[str, str], data.get("tokens", {})),
            modes=cast(Mapping[str, Mapping[str, str]], data.get("modes", {})),
            accessibility_modes=cast(
                Mapping[str, Mapping[str, str]], data.get("accessibility_modes", {})
            ),
            aliases=cast(Mapping[str, str], data.get("aliases", {})),
            groups=cast(Mapping[str, str], data.get("groups", {})),
            recipes=cast(Mapping[str, Mapping[str, str]], data.get("recipes", {})),
            metadata=cast(Mapping[str, Any], data.get("metadata", {})),
            schema=str(data.get("schema", "hedron.theme-spec/1")),
            profile=str(data.get("profile", "core")),
            provenance=tuple(cast(Iterable[Mapping[str, Any]], data.get("provenance", ()))),
        )
        fingerprint = data.get("fingerprint")
        if fingerprint is not None and str(fingerprint) != spec.fingerprint:
            raise ValueError("theme spec fingerprint does not match canonical payload")
        return spec

    @property
    def fingerprint(self) -> str:
        payload = self.to_dict(include_fingerprint=False)
        return hashlib.sha256(_canonical(payload).encode()).hexdigest()

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema": self.schema,
            "name": self.name,
            "tokens": dict(self.tokens),
            "modes": {key: dict(value) for key, value in self.modes.items()},
            "accessibility_modes": {
                key: dict(value) for key, value in self.accessibility_modes.items()
            },
            "aliases": dict(self.aliases),
            "groups": dict(self.groups),
            "recipes": {key: dict(value) for key, value in self.recipes.items()},
            "metadata": dict(self.metadata),
            "profile": self.profile,
            "provenance": [dict(item) for item in self.provenance],
        }
        if include_fingerprint:
            data["fingerprint"] = self.fingerprint
        return data

    def patch(
        self,
        name: str = "inline",
        *,
        tokens: Mapping[str, str] | None = None,
        modes: Mapping[str, Mapping[str, str]] | None = None,
        accessibility_modes: Mapping[str, Mapping[str, str]] | None = None,
        aliases: Mapping[str, str] | None = None,
        groups: Mapping[str, str] | None = None,
        recipes: Mapping[str, Mapping[str, str]] | None = None,
        base_fingerprint: str | None = None,
        provenance: Iterable[Mapping[str, Any]] = (),
    ) -> ThemeSpec:
        """Apply one bounded immutable patch and return a new specification."""
        return ThemePatch(
            name=name,
            tokens=tokens or {},
            modes=modes or {},
            accessibility_modes=accessibility_modes or {},
            aliases=aliases or {},
            groups=groups or {},
            recipes=recipes or {},
            base_fingerprint=base_fingerprint,
            provenance=tuple(provenance),
        ).apply(self)

    def apply_patches(self, *patches: ThemePatch) -> ThemeSpec:
        """Apply ordered patches without mutating the original specification."""
        result = self
        for patch in patches:
            result = patch.apply(result)
        return result

    def to_theme(self) -> Any:
        """Bridge to the compatible 0.59 ``Theme`` object."""
        from hedron_core.theme import Theme

        return Theme(
            name=self.name,
            tokens=self.resolved_tokens,
            modes={
                mode: {key: self.resolve_token(key, mode=mode) for key in values}
                for mode, values in self.modes.items()
            },
            accessibility_modes={
                mode: dict(values) for mode, values in self.accessibility_modes.items()
            },
        )


@dataclass(frozen=True, slots=True)
class ThemePatch:
    """Bounded overlay that always produces a fully revalidated ThemeSpec."""

    name: str
    base: str | None = None
    tokens: Mapping[str, str] = field(default_factory=dict)
    modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    accessibility_modes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    aliases: Mapping[str, str] = field(default_factory=dict)
    groups: Mapping[str, str] = field(default_factory=dict)
    recipes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    base_fingerprint: str | None = None
    provenance: tuple[Mapping[str, Any], ...] = ()

    def apply(self, spec: ThemeSpec) -> ThemeSpec:
        if self.base is not None and self.base not in {spec.name, spec.fingerprint}:
            raise ValueError(f"patch {self.name!r} is incompatible with theme {spec.name!r}")
        if self.base_fingerprint is not None and self.base_fingerprint != spec.fingerprint:
            raise ValueError(f"patch {self.name!r} base fingerprint does not match theme")
        modes = {key: dict(value) for key, value in spec.modes.items()}
        for mode, values in self.modes.items():
            modes[mode] = {**modes.get(mode, {}), **dict(values)}
        a11y = {key: dict(value) for key, value in spec.accessibility_modes.items()}
        for mode, values in self.accessibility_modes.items():
            a11y[mode] = {**a11y.get(mode, {}), **dict(values)}
        return ThemeSpec(
            name=spec.name,
            tokens={**dict(spec.tokens), **dict(self.tokens)},
            modes=modes,
            accessibility_modes=a11y,
            aliases={**dict(spec.aliases), **dict(self.aliases)},
            groups={**dict(spec.groups), **dict(self.groups)},
            recipes={**dict(spec.recipes), **dict(self.recipes)},
            metadata={**dict(spec.metadata), "last_patch": self.name},
            profile=spec.profile,
            provenance=(*spec.provenance, *self.provenance, {"patch": self.name}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "hedron.theme-patch/1",
            "name": self.name,
            "base": self.base,
            "base_fingerprint": self.base_fingerprint,
            "tokens": dict(self.tokens),
            "modes": {key: dict(value) for key, value in self.modes.items()},
            "accessibility_modes": {
                key: dict(value) for key, value in self.accessibility_modes.items()
            },
            "aliases": dict(self.aliases),
            "groups": dict(self.groups),
            "recipes": {key: dict(value) for key, value in self.recipes.items()},
            "provenance": [dict(item) for item in self.provenance],
        }


class ThemeBuilder:
    """Pure convenience facade that emits one immutable ``ThemeSpec``.

    Each authoring operation returns a new builder.  This keeps the fluent API
    pleasant while making a builder safe to retain as a reusable base.
    """

    def __init__(self, name: str, *, base: ThemeSpec | Any | None = None) -> None:
        if isinstance(base, ThemeSpec):
            source = base
        elif base is not None:
            source = ThemeSpec(
                name=name,
                tokens=dict(getattr(base, "tokens", {})),
                modes=dict(getattr(base, "modes", {})),
                accessibility_modes=dict(getattr(base, "accessibility_modes", {})),
                metadata=dict(getattr(base, "metadata", {})),
            )
        else:
            source = ThemeSpec(name=name, tokens={})
        self._name = name
        self._tokens = dict(source.tokens)
        self._modes = {key: dict(value) for key, value in source.modes.items()}
        self._a11y = {key: dict(value) for key, value in source.accessibility_modes.items()}
        self._aliases = dict(source.aliases)
        self._groups = dict(getattr(source, "groups", {}))
        self._recipes = {key: dict(value) for key, value in getattr(source, "recipes", {}).items()}
        self._metadata = dict(source.metadata)
        self._profile = source.profile
        self._provenance = list(source.provenance)

    def _clone(self) -> ThemeBuilder:
        clone = object.__new__(type(self))
        clone._name = self._name
        clone._tokens = dict(self._tokens)
        clone._modes = {key: dict(value) for key, value in self._modes.items()}
        clone._a11y = {key: dict(value) for key, value in self._a11y.items()}
        clone._aliases = dict(self._aliases)
        clone._groups = dict(self._groups)
        clone._recipes = {key: dict(value) for key, value in self._recipes.items()}
        clone._metadata = dict(self._metadata)
        clone._profile = self._profile
        clone._provenance = list(self._provenance)
        return clone

    @classmethod
    def from_spec(cls, spec: ThemeSpec) -> ThemeBuilder:
        return cls(spec.name, base=spec)

    @classmethod
    def from_theme(cls, theme: Any) -> ThemeBuilder:
        return cls(
            theme.name,
            base=ThemeSpec(
                name=theme.name,
                tokens=dict(theme.tokens),
                modes=dict(theme.modes),
                accessibility_modes=dict(getattr(theme, "accessibility_modes", {})),
            ),
        )

    def token(self, name: str, value: str | Color) -> ThemeBuilder:
        builder = self._clone()
        builder._tokens[name] = value.to_hex() if isinstance(value, Color) else value
        return builder

    def tokens(self, values: Mapping[str, str | Color]) -> ThemeBuilder:
        builder = self._clone()
        for name, value in values.items():
            builder._tokens[name] = value.to_hex() if isinstance(value, Color) else value
        return builder

    def brand(self, *, accent: str | Color, **values: str | Color) -> ThemeBuilder:
        color = Color.parse(accent)
        builder = self._clone()
        builder._tokens["color.accent"] = color.to_hex()
        builder._metadata["brand"] = {
            "requested": color.to_css(fallback=False),
            "space": color.space,
            "fallback": color.to_hex(),
            **{
                key: value.to_hex() if isinstance(value, Color) else value
                for key, value in values.items()
            },
        }
        return builder

    def groups(self, **groups: str) -> ThemeBuilder:
        builder = self._clone()
        for name, value in groups.items():
            if (
                not _NAME.fullmatch(name)
                or not isinstance(value, str)
                or not _NAME.fullmatch(value)
            ):
                raise ValueError("theme groups must use safe identifiers")
            builder._groups[name] = value
        return builder

    def accessibility_mode(
        self,
        name: str,
        values: Mapping[str, str | Color] | None = None,
        **tokens: str | Color,
    ) -> ThemeBuilder:
        merged = dict(values or {})
        merged.update(tokens)
        return self.accessibility(name, **merged)

    def recipe(self, name: str, values: Mapping[str, str]) -> ThemeBuilder:
        if not _NAME.fullmatch(name) or any(
            not _NAME.fullmatch(key) or not _NAME.fullmatch(value) for key, value in values.items()
        ):
            raise ValueError("theme recipes must use safe identifiers")
        builder = self._clone()
        builder._recipes[name] = dict(values)
        return builder

    def alias(self, name: str, target: str) -> ThemeBuilder:
        builder = self._clone()
        reference = target if target.startswith("@") else f"@{target}"
        builder._aliases[name] = reference
        builder._tokens[name] = reference
        return builder

    def mode(self, name: str, **tokens: str | Color) -> ThemeBuilder:
        builder = self._clone()
        builder._modes.setdefault(name, {}).update(
            {
                key: value.to_hex() if isinstance(value, Color) else value
                for key, value in tokens.items()
            }
        )
        return builder

    def accessibility(self, name: str, **tokens: str | Color) -> ThemeBuilder:
        builder = self._clone()
        builder._a11y.setdefault(name, {}).update(
            {
                key: value.to_hex() if isinstance(value, Color) else value
                for key, value in tokens.items()
            }
        )
        return builder

    def metadata(self, **values: Any) -> ThemeBuilder:
        builder = self._clone()
        builder._metadata.update(values)
        return builder

    def profile(self, profile: str) -> ThemeBuilder:
        if profile not in THEME_COVERAGE_PROFILES:
            raise ValueError(f"unknown theme coverage profile: {profile}")
        builder = self._clone()
        builder._profile = profile
        return builder

    def provenance(self, **entry: Any) -> ThemeBuilder:
        builder = self._clone()
        builder._provenance.append(dict(entry))
        return builder

    def build(self) -> ThemeSpec:
        return ThemeSpec(
            name=self._name,
            tokens=self._tokens,
            modes=self._modes,
            accessibility_modes=self._a11y,
            aliases=self._aliases,
            groups=self._groups,
            recipes=self._recipes,
            metadata=self._metadata,
            profile=self._profile,
            provenance=tuple(self._provenance),
        )

    def build_spec(self) -> ThemeSpec:
        return self.build()


@dataclass(frozen=True, slots=True)
class RecipeFamily:
    """Finite, presentation-only extension to the built-in recipe catalog."""

    name: str
    fields: Mapping[str, tuple[str, ...]]
    components: tuple[str, ...]
    extends: str | None = None

    def __post_init__(self) -> None:
        if not _NAME.fullmatch(self.name):
            raise ValueError("recipe family name must be a safe identifier")
        if self.extends == self.name:
            raise ValueError("recipe family cannot extend itself")
        if not self.components or any(not _NAME.fullmatch(item) for item in self.components):
            raise ValueError("recipe family components must be safe logical names")
        normalized: dict[str, tuple[str, ...]] = {}
        for key, values in self.fields.items():
            if (
                not _NAME.fullmatch(key)
                or not values
                or any(not _NAME.fullmatch(value) for value in values)
            ):
                raise ValueError("recipe family fields and values must be bounded identifiers")
            if key.lower() in {
                "behavior",
                "callback",
                "event",
                "handler",
                "href",
                "route",
                "state",
                "permission",
                "authorization",
            }:
                raise ValueError(f"recipe family field {key!r} is not presentation-only")
            normalized[key] = tuple(dict.fromkeys(values))
        object.__setattr__(self, "fields", MappingProxyType(normalized))
        object.__setattr__(self, "components", tuple(dict.fromkeys(self.components)))
        if self.extends is not None and not _NAME.fullmatch(self.extends):
            raise ValueError("recipe family parent must be a safe identifier")


_RECIPE_FAMILIES: dict[str, RecipeFamily] = {}


def register_recipe_family(family: RecipeFamily) -> None:
    if family.extends is not None:
        parent = _RECIPE_FAMILIES.get(family.extends)
        if parent is None:
            raise ValueError(f"recipe family parent is not registered: {family.extends}")
        if family.extends == family.name:
            raise ValueError("recipe family inheritance cycle")
        unknown = set(family.fields) - set(parent.fields)
        if unknown:
            raise ValueError(
                f"recipe family {family.name!r} adds fields outside its parent vocabulary: "
                + ", ".join(sorted(unknown))
            )
    previous = _RECIPE_FAMILIES.get(family.name)
    if previous is not None and previous != family:
        raise ValueError(
            f"recipe family already registered with a different contract: {family.name}"
        )
    _RECIPE_FAMILIES[family.name] = family


def registered_recipe_families() -> tuple[RecipeFamily, ...]:
    return tuple(_RECIPE_FAMILIES[name] for name in sorted(_RECIPE_FAMILIES))


@dataclass(frozen=True, slots=True)
class StyleContext:
    """Serializable recipe context with explicit-component precedence."""

    recipes: Mapping[str, str] = field(default_factory=dict)
    parent: StyleContext | None = None

    def __post_init__(self) -> None:
        cleaned = {str(key): str(value) for key, value in self.recipes.items()}
        if any(
            not _NAME.fullmatch(key) or not _NAME.fullmatch(value) for key, value in cleaned.items()
        ):
            raise ValueError("style context recipe names must be safe identifiers")
        object.__setattr__(self, "recipes", MappingProxyType(dict(sorted(cleaned.items()))))

    def resolve(self, family: str, explicit: str | None = None) -> str | None:
        if explicit is not None:
            return explicit
        current: StyleContext | None = self
        seen: set[int] = set()
        while current is not None:
            marker = id(current)
            if marker in seen:
                raise ValueError("style context parent cycle")
            seen.add(marker)
            if family in current.recipes:
                return current.recipes[family]
            current = current.parent
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipes": dict(self.recipes),
            "parent": self.parent.to_dict() if self.parent is not None else None,
        }


@dataclass(frozen=True, slots=True)
class ComponentThemeContract:
    logical_id: str
    parts: tuple[str, ...] = ()
    states: tuple[str, ...] = ()
    variants: tuple[str, ...] = ()
    required_tokens: tuple[str, ...] = ()
    roles: tuple[str, ...] = ()
    contrast_relationships: tuple[Mapping[str, str], ...] = ()
    accessibility_behavior: Mapping[str, str] = field(default_factory=dict)
    fallback_policy: Mapping[str, str] = field(default_factory=dict)
    profile: str = "core"

    def __post_init__(self) -> None:
        if not _NAME.fullmatch(self.logical_id):
            raise ValueError("component contract id must be a safe identifier")
        if self.profile not in THEME_COVERAGE_PROFILES:
            raise ValueError(f"unknown theme coverage profile: {self.profile}")
        for field_name, values in (
            ("parts", self.parts),
            ("states", self.states),
            ("variants", self.variants),
            ("required_tokens", self.required_tokens),
            ("roles", self.roles),
        ):
            if any(not isinstance(value, str) or not _NAME.fullmatch(value) for value in values):
                raise ValueError(f"component contract {field_name} must use safe identifiers")
        relationships: list[Mapping[str, str]] = []
        for relationship in self.contrast_relationships:
            if not isinstance(relationship, Mapping) or not relationship:
                raise ValueError("contrast relationships must be non-empty mappings")
            normalized = {str(key): str(value) for key, value in relationship.items()}
            if any(
                not _NAME.fullmatch(key) or not _NAME.fullmatch(value)
                for key, value in normalized.items()
            ):
                raise ValueError("contrast relationships must use safe identifiers")
            relationships.append(MappingProxyType(dict(sorted(normalized.items()))))
        object.__setattr__(self, "parts", tuple(dict.fromkeys(self.parts)))
        object.__setattr__(self, "states", tuple(dict.fromkeys(self.states)))
        object.__setattr__(self, "variants", tuple(dict.fromkeys(self.variants)))
        object.__setattr__(self, "required_tokens", tuple(dict.fromkeys(self.required_tokens)))
        object.__setattr__(self, "roles", tuple(dict.fromkeys(self.roles)))
        object.__setattr__(self, "contrast_relationships", tuple(relationships))
        object.__setattr__(
            self, "accessibility_behavior", _freeze_mapping(self.accessibility_behavior)
        )
        object.__setattr__(self, "fallback_policy", _freeze_mapping(self.fallback_policy))

    @property
    def semantic_roles(self) -> tuple[str, ...]:
        """Compatibility spelling used by contract and inventory tooling."""
        return self.roles


@dataclass(frozen=True, slots=True)
class CoverageProfile:
    """Named monotonic validation profile."""

    name: str
    includes: tuple[str, ...]


THEME_COVERAGE_PROFILES: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "core": ("core",),
        "forms": ("core", "forms"),
        "data": ("core", "data"),
        "workflow": ("core", "workflow"),
        "complete": ("core", "forms", "data", "workflow"),
    }
)
_CONTRACTS: dict[str, ComponentThemeContract] = {}


def register_component_theme_contract(contract: ComponentThemeContract) -> None:
    previous = _CONTRACTS.get(contract.logical_id)
    if previous is not None and previous != contract:
        raise ValueError(f"component theme contract already differs: {contract.logical_id}")
    _CONTRACTS[contract.logical_id] = contract


def registered_component_theme_contracts() -> tuple[ComponentThemeContract, ...]:
    return tuple(_CONTRACTS[key] for key in sorted(_CONTRACTS))


@dataclass(frozen=True, slots=True)
class ThemeValidationReport:
    schema: str
    theme: str
    profile: str
    errors: tuple[Mapping[str, Any], ...] = ()
    warnings: tuple[Mapping[str, Any], ...] = ()
    adjustments: tuple[Mapping[str, Any], ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def digest(self) -> str:
        return hashlib.sha256(_canonical(self._without_digest()).encode()).hexdigest()

    def _without_digest(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "theme": self.theme,
            "profile": self.profile,
            "ok": self.ok,
            "errors": [dict(item) for item in self.errors],
            "warnings": [dict(item) for item in self.warnings],
            "adjustments": [dict(item) for item in self.adjustments],
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self._without_digest(), "digest": self.digest}


def validate_theme_spec(
    spec: ThemeSpec,
    *,
    profile: str = "core",
    strict: bool = True,
) -> ThemeValidationReport:
    if profile not in THEME_COVERAGE_PROFILES:
        raise ValueError(f"unknown theme coverage profile: {profile}")
    errors: list[Mapping[str, Any]] = []
    warnings: list[Mapping[str, Any]] = []
    required = {"color.bg", "color.fg", "color.focus", "font.family", "font.size", "space.unit"}
    missing = sorted(required - set(spec.tokens))
    if missing:
        errors.append({"code": "THEME-MISSING-TOKEN", "tokens": missing})
    for contract in registered_component_theme_contracts():
        if contract.profile not in THEME_COVERAGE_PROFILES[profile]:
            continue
        absent = sorted(set(contract.required_tokens) - set(spec.tokens))
        if absent:
            finding = {
                "code": "THEME-CONTRACT-TOKEN",
                "component": contract.logical_id,
                "tokens": absent,
            }
            (errors if strict else warnings).append(finding)
        for relationship in contract.contrast_relationships:
            relationship_tokens = {
                value for value in relationship.values() if value.startswith("color.")
            }
            missing_relationship_tokens = sorted(relationship_tokens - set(spec.tokens))
            if missing_relationship_tokens:
                finding = {
                    "code": "THEME-CONTRACT-RELATIONSHIP",
                    "component": contract.logical_id,
                    "tokens": missing_relationship_tokens,
                    "relationship": dict(relationship),
                }
                (errors if strict else warnings).append(finding)
    for mode_name, values in spec.accessibility_modes.items():
        if mode_name not in {"forced-colors", "more-contrast"}:
            errors.append({"code": "THEME-ACCESSIBILITY-MODE", "mode": mode_name})
        if "color.focus" not in values:
            warnings.append({"code": "THEME-ACCESSIBILITY-FOCUS", "mode": mode_name})
    for mapping_name, mapping in (
        ("mode", spec.modes),
        ("accessibility", spec.accessibility_modes),
    ):
        for mode, values in mapping.items():
            for token, value in values.items():
                if token not in spec.tokens and token not in spec.aliases:
                    warnings.append(
                        {
                            "code": "THEME-UNKNOWN-OVERRIDE",
                            "mapping": mapping_name,
                            "mode": mode,
                            "token": token,
                        }
                    )
                if not isinstance(value, str) or not value.strip():
                    errors.append(
                        {
                            "code": "THEME-EMPTY-VALUE",
                            "mapping": mapping_name,
                            "mode": mode,
                            "token": token,
                        }
                    )
    return ThemeValidationReport(
        schema="hedron.theme-validation/1",
        theme=spec.name,
        profile=profile,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


@dataclass(frozen=True, slots=True)
class ThemePackage:
    manifest: Mapping[str, Any]
    archive: bytes

    @property
    def fingerprint(self) -> str:
        return str(self.manifest["fingerprint"])

    def load(self) -> ThemeSpec:
        return load_theme_package(self.archive)


def package_theme(
    spec: ThemeSpec,
    *,
    profile: str = "core",
    licenses: Iterable[str] = (),
    migrations: Mapping[str, str] | None = None,
) -> ThemePackage:
    normalized_licenses = tuple(sorted(set(licenses)))
    if not normalized_licenses:
        raise ValueError("theme packages require at least one declared license")
    report = validate_theme_spec(spec, profile=profile)
    if not report.ok:
        raise ValueError(f"theme validation failed: {report.to_dict()}")
    payload = _canonical(spec.to_dict()).encode()
    manifest = {
        "schema": "hedron.theme-package/1",
        "name": spec.name,
        "version": "1",
        "profile": profile,
        "compatibility": {"hedron": THEME_PACKAGE_COMPATIBILITY, "theme_schema": spec.schema},
        "specs": ["theme.json"],
        "fingerprint": spec.fingerprint,
        "files": {"theme.json": hashlib.sha256(payload).hexdigest()},
        "licenses": normalized_licenses,
        "migrations": dict(sorted((migrations or {}).items())),
        "validation": report.digest,
        "assets": {},
        "hooks": [],
    }
    manifest_bytes = _canonical(manifest).encode()
    output = BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in (("manifest.json", manifest_bytes), ("theme.json", payload)):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, content)
    return ThemePackage(manifest=MappingProxyType(manifest), archive=output.getvalue())


def load_theme_package(archive: bytes | ThemePackage) -> ThemeSpec:
    """Load and verify a data-only theme package without executing package code."""
    raw = archive.archive if isinstance(archive, ThemePackage) else archive
    if not isinstance(raw, bytes):
        raise ValueError("theme package must be bytes or ThemePackage")
    try:
        with zipfile.ZipFile(BytesIO(raw)) as bundle:
            names = set(bundle.namelist())
            if names != {"manifest.json", "theme.json"}:
                raise ValueError("theme package contains unexpected or missing files")
            manifest = json.loads(bundle.read("manifest.json"))
            payload = bundle.read("theme.json")
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid theme package archive") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != "hedron.theme-package/1":
        raise ValueError("unsupported theme package manifest")
    if manifest.get("version") != "1":
        raise ValueError("unsupported theme package version")
    if not isinstance(manifest.get("name"), str) or not _NAME.fullmatch(manifest["name"]):
        raise ValueError("theme package name is missing or unsafe")
    if not isinstance(manifest.get("specs"), list) or manifest["specs"] != ["theme.json"]:
        raise ValueError("theme package must declare exactly theme.json")
    compatibility = manifest.get("compatibility")
    if (
        not isinstance(compatibility, dict)
        or compatibility.get("hedron") != THEME_PACKAGE_COMPATIBILITY
    ):
        raise ValueError("theme package Hedron compatibility is unsupported")
    if not isinstance(manifest.get("licenses"), list) or not manifest["licenses"]:
        raise ValueError("theme package must declare at least one license")
    if not all(isinstance(item, str) and item.strip() for item in manifest["licenses"]):
        raise ValueError("theme package licenses must be non-empty strings")
    if manifest.get("hooks") != [] or manifest.get("assets") != {}:
        raise ValueError("theme packages cannot contain executable hooks or remote assets")
    files = manifest.get("files")
    if (
        not isinstance(files, dict)
        or files.get("theme.json") != hashlib.sha256(payload).hexdigest()
    ):
        raise ValueError("theme package theme.json hash does not match manifest")
    spec = ThemeSpec.from_dict(cast(Mapping[str, Any], json.loads(payload)))
    if manifest.get("name") != spec.name:
        raise ValueError("theme package name does not match theme.json")
    if manifest.get("fingerprint") != spec.fingerprint:
        raise ValueError("theme package fingerprint does not match theme.json")
    profile = str(manifest.get("profile", "core"))
    if profile not in THEME_COVERAGE_PROFILES:
        raise ValueError(f"theme package uses unknown coverage profile: {profile}")
    report = validate_theme_spec(spec, profile=profile)
    if manifest.get("validation") != report.digest or not report.ok:
        raise ValueError("theme package validation digest or result does not match")
    return spec


def register_theme_package(archive: bytes | ThemePackage) -> ThemeSpec:
    """Verify a package, then register its compatibility ``Theme`` instance."""
    spec = load_theme_package(archive)
    from hedron_core.theme import register_theme_instance

    register_theme_instance(spec.to_theme())
    return spec


def diff_theme_specs(left: ThemeSpec, right: ThemeSpec) -> dict[str, Any]:
    """Return a deterministic, read-only semantic diff for two theme specs."""

    def changes(a: Mapping[str, Any], b: Mapping[str, Any]) -> dict[str, Any]:
        added = {key: b[key] for key in sorted(set(b) - set(a))}
        removed = {key: a[key] for key in sorted(set(a) - set(b))}
        changed = {
            key: {"from": a[key], "to": b[key]}
            for key in sorted(set(a) & set(b))
            if a[key] != b[key]
        }
        return {"added": added, "removed": removed, "changed": changed}

    return {
        "schema": "hedron.theme-diff/1",
        "left": {"name": left.name, "fingerprint": left.fingerprint},
        "right": {"name": right.name, "fingerprint": right.fingerprint},
        "tokens": changes(left.tokens, right.tokens),
        "aliases": changes(left.aliases, right.aliases),
        "modes": changes(left.modes, right.modes),
        "accessibility_modes": changes(left.accessibility_modes, right.accessibility_modes),
        "groups": changes(left.groups, right.groups),
        "recipes": changes(left.recipes, right.recipes),
    }


def explain_theme_spec(spec: ThemeSpec) -> dict[str, Any]:
    """Return source/provenance and resolved-token facts for diagnostics and tooling."""
    return {
        "schema": "hedron.theme-explanation/1",
        "name": spec.name,
        "profile": spec.profile,
        "fingerprint": spec.fingerprint,
        "tokens": dict(spec.resolved_tokens),
        "aliases": dict(spec.aliases),
        "modes": {key: dict(value) for key, value in spec.modes.items()},
        "accessibility_modes": {
            key: dict(value) for key, value in spec.accessibility_modes.items()
        },
        "groups": dict(spec.groups),
        "recipes": {key: dict(value) for key, value in spec.recipes.items()},
        "provenance": [dict(item) for item in spec.provenance],
    }


def conformance_report(spec: ThemeSpec, *, profile: str | None = None) -> dict[str, Any]:
    """Build the portable declared-profile conformance result."""
    selected = profile or spec.profile
    report = validate_theme_spec(spec, profile=selected)
    return {
        "schema": "hedron.theme-conformance/1",
        "theme": spec.name,
        "profile": selected,
        "fingerprint": spec.fingerprint,
        "inventory_digest": hashlib.sha256(
            _canonical(
                [
                    {
                        "logical_id": item.logical_id,
                        "profile": item.profile,
                        "tokens": list(item.required_tokens),
                    }
                    for item in registered_component_theme_contracts()
                ]
            ).encode()
        ).hexdigest(),
        "validation": report.to_dict(),
        "ok": report.ok,
    }
