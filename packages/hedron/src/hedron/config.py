"""[tool.hedron] configuration loader."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from hedron_core.codes import (
    HED_CONFIG_INVALID,
    HED_CONFIG_UNKNOWN_KEY,
    HED_CONFIG_UNSUPPORTED_VERSION,
)
from hedron_core.compat import tomllib
from hedron_core.diagnostics import HedronError, error
from hedron_core.identifiers import content_digest
from hedron_core.manifests import canonical_json
from hedron_core.typing_aliases import JsonObject, is_string_mapping

__all__ = [
    "CONFIG_FORMAT_VERSION",
    "AssetPolicy",
    "HedronSettings",
    "load_hedron_settings",
    "settings_digest",
]

CONFIG_FORMAT_VERSION = 1

_KNOWN_KEYS = frozenset(
    {
        "format_version",
        "component_roots",
        "build_dir",
        "theme",
        "asset_policy",
        "plugins",
        "explorer",
        "compiler_checks",
        "diagnostic_severities",
    }
)

_ASSET_POLICY_KEYS = frozenset(
    {
        "allow_remote",
        "strict_csp",
        "registered_roots",
        "reject_inline_style",
    }
)


@dataclass(frozen=True, slots=True)
class AssetPolicy:
    allow_remote: bool = False
    strict_csp: bool = True
    registered_roots: tuple[str, ...] = ()
    reject_inline_style: bool = True


@dataclass(frozen=True, slots=True)
class HedronSettings:
    format_version: int = CONFIG_FORMAT_VERSION
    component_roots: tuple[str, ...] = ()
    build_dir: str = ".hedron/build"
    theme: str | None = "default"
    asset_policy: AssetPolicy = field(default_factory=AssetPolicy)
    plugins: tuple[str, ...] | None = None
    explorer: str = "off"
    compiler_checks: bool = True
    diagnostic_severities: Mapping[str, str] = field(default_factory=dict[str, str])
    source_path: str | None = None

    def resolved_roots(self, *, base: Path | None = None) -> tuple[Path, ...]:
        root = base or Path.cwd()
        return tuple((root / p).resolve() for p in self.component_roots)

    def resolved_build_dir(self, *, base: Path | None = None) -> Path:
        root = base or Path.cwd()
        return (root / self.build_dir).resolve()


def settings_digest(settings: HedronSettings) -> str:
    payload = cast(
        JsonObject,
        {
            "format_version": settings.format_version,
            "component_roots": list(settings.component_roots),
            "build_dir": settings.build_dir,
            "theme": settings.theme,
            "asset_policy": {
                "allow_remote": settings.asset_policy.allow_remote,
                "strict_csp": settings.asset_policy.strict_csp,
                "registered_roots": list(settings.asset_policy.registered_roots),
                "reject_inline_style": settings.asset_policy.reject_inline_style,
            },
            "plugins": None if settings.plugins is None else list(settings.plugins),
            "explorer": settings.explorer,
            "compiler_checks": settings.compiler_checks,
            "diagnostic_severities": dict(sorted(settings.diagnostic_severities.items())),
        },
    )
    return content_digest(canonical_json(payload))


def _suggest(key: str, known: Sequence[str]) -> str:
    lower = key.lower()
    hits = [k for k in known if lower in k.lower() or k.lower() in lower]
    if hits:
        return f" Did you mean {', '.join(sorted(hits)[:3])}?"
    return ""


def _invalid_type(key: str, expected: str, value: object) -> HedronError:
    return error(
        HED_CONFIG_INVALID,
        title="Invalid configuration value",
        explanation=f"{key} must be {expected}; got {type(value).__name__}.",
        remediation=f"Set {key} to {expected}.",
    )


def _bool_value(raw: Mapping[str, object], key: str, default: bool, *, prefix: str = "") -> bool:
    value = raw.get(key, default)
    if not isinstance(value, bool):
        raise _invalid_type(f"{prefix}{key}", "a boolean", value)
    return value


def _string_list(value: object, key: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise _invalid_type(key, "an array of strings", value)
    items = cast(list[object] | tuple[object, ...], value)
    if any(not isinstance(item, str) for item in items):
        raise _invalid_type(key, "an array of strings", cast(object, value))
    return cast(tuple[str, ...], tuple(items))


def _parse_asset_policy(raw: object | None) -> AssetPolicy:
    if raw is None:
        return AssetPolicy()
    if not is_string_mapping(raw):
        raise _invalid_type("asset_policy", "a table", raw)
    unknown = set(raw) - _ASSET_POLICY_KEYS
    if unknown:
        key = sorted(unknown)[0]
        raise error(
            HED_CONFIG_UNKNOWN_KEY,
            title="Unknown asset_policy key",
            explanation=f"Unknown key {key!r} in asset_policy."
            + _suggest(key, sorted(_ASSET_POLICY_KEYS)),
            remediation="Remove or rename the unknown configuration key.",
        )
    return AssetPolicy(
        allow_remote=_bool_value(raw, "allow_remote", False, prefix="asset_policy."),
        strict_csp=_bool_value(raw, "strict_csp", True, prefix="asset_policy."),
        registered_roots=_string_list(
            raw.get("registered_roots", ()), "asset_policy.registered_roots"
        ),
        reject_inline_style=_bool_value(raw, "reject_inline_style", True, prefix="asset_policy."),
    )


def load_hedron_settings(
    path: Path | str | None = None,
    *,
    overrides: Mapping[str, object] | None = None,
) -> HedronSettings:
    """Load settings from pyproject.toml ``[tool.hedron]`` with optional overrides."""
    pyproject: Path | None
    if path is None:
        candidate = Path.cwd() / "pyproject.toml"
        pyproject = candidate if candidate.is_file() else None
    else:
        pyproject = Path(path)
        if pyproject.is_dir():
            pyproject = pyproject / "pyproject.toml"
        if not pyproject.is_file():
            raise error(
                HED_CONFIG_INVALID,
                title="Configuration file missing",
                explanation=f"No pyproject.toml found at {pyproject}.",
                remediation="Provide a valid project path or create [tool.hedron].",
            )

    raw: dict[str, object] = {}
    source_path: str | None = None
    if pyproject is not None and pyproject.is_file():
        data: object = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        if not is_string_mapping(data):
            raise error(
                HED_CONFIG_INVALID,
                title="Invalid configuration document",
                explanation="pyproject.toml must decode to a table.",
            )
        tool_raw = cast(object, data.get("tool") or dict[str, object]())
        if not is_string_mapping(tool_raw):
            raise error(
                HED_CONFIG_INVALID,
                title="Invalid tool table",
                explanation="[tool] must be a table.",
            )
        hedron_raw = cast(object, tool_raw.get("hedron") or dict[str, object]())
        if not is_string_mapping(hedron_raw):
            raise error(
                HED_CONFIG_INVALID,
                title="Invalid hedron configuration",
                explanation="[tool.hedron] must be a table.",
            )
        raw = dict(hedron_raw)
        source_path = str(pyproject.resolve())

    if overrides:
        raw.update(dict(overrides))

    # Environment deployment overlays (limited).
    env_theme = os.environ.get("HEDRON_THEME")
    if env_theme and "theme" not in (overrides or {}):
        raw["theme"] = env_theme
    env_build = os.environ.get("HEDRON_BUILD_DIR")
    if env_build and "build_dir" not in (overrides or {}):
        raw["build_dir"] = env_build

    if not raw:
        return HedronSettings(source_path=source_path)

    unknown = set(raw) - _KNOWN_KEYS
    if unknown:
        key = sorted(unknown)[0]
        raise error(
            HED_CONFIG_UNKNOWN_KEY,
            title="Unknown configuration key",
            explanation=f"Unknown [tool.hedron] key {key!r}." + _suggest(key, sorted(_KNOWN_KEYS)),
            remediation="Remove or rename the unknown configuration key.",
        )

    format_raw = raw.get("format_version", CONFIG_FORMAT_VERSION)
    if isinstance(format_raw, bool) or not isinstance(format_raw, int):
        raise _invalid_type("format_version", "an integer", format_raw)
    format_version = format_raw
    if format_version != CONFIG_FORMAT_VERSION:
        raise error(
            HED_CONFIG_UNSUPPORTED_VERSION,
            title="Unsupported configuration format",
            explanation=(
                f"format_version {format_version} is not supported "
                f"(expected {CONFIG_FORMAT_VERSION})."
            ),
            remediation="Update Hedron or migrate the configuration schema.",
        )

    component_roots = _string_list(raw.get("component_roots", ()), "component_roots")
    plugins_raw = raw.get("plugins")
    plugins = (
        None
        if "plugins" not in raw or plugins_raw is None
        else _string_list(plugins_raw, "plugins")
    )
    diagnostics_raw = raw.get("diagnostic_severities", {})
    if not is_string_mapping(diagnostics_raw) or any(
        not isinstance(value, str) for value in diagnostics_raw.values()
    ):
        raise _invalid_type("diagnostic_severities", "a string-to-string table", diagnostics_raw)
    build_dir = raw.get("build_dir", ".hedron/build")
    if not isinstance(build_dir, str):
        raise _invalid_type("build_dir", "a string", build_dir)
    explorer = raw.get("explorer", "off")
    if not isinstance(explorer, str):
        raise _invalid_type("explorer", "a string", explorer)
    theme = raw.get("theme", "default")
    if theme is not None and not isinstance(theme, str):
        raise _invalid_type("theme", "a string or null", theme)
    diagnostic_severities = {key: cast(str, value) for key, value in diagnostics_raw.items()}

    return HedronSettings(
        format_version=format_version,
        component_roots=component_roots,
        build_dir=build_dir,
        theme=theme,
        asset_policy=_parse_asset_policy(raw.get("asset_policy")),
        plugins=plugins,
        explorer=explorer,
        compiler_checks=_bool_value(raw, "compiler_checks", True),
        diagnostic_severities=diagnostic_severities,
        source_path=source_path,
    )
