"""Read-only installed-application fleet diagnosis (FLEET-053).

Complements Explorer ``package_health`` ideas but lives in the ``hedron`` package.
This is not the 0.54 external-author ``hedron package doctor`` (DOCTOR-054).
Never auto-installs packages or enables plugins.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from importlib.metadata import PackageNotFoundError, distributions, entry_points, version
from pathlib import Path
from typing import Any

_SECRET_ENV_RE = re.compile(
    r"(secret|password|passwd|token|api[_-]?key|access[_-]?key|private[_-]?key|"
    r"credential|auth[_-]?token|session[_-]?key|cookie|authorization)",
    re.IGNORECASE,
)

_TRAIN_DISTS = (
    "hedron",
    "hedron-core",
    "hedron-explorer",
    "hedron-data",
    "hedron-flask",
    "hedron-django",
    "hedron-jinja",
    "hedron-conformance",
    "hedron-extras",
    "hedron-workbench",
    "hedron-posit",
    "hedron-elements",
)

_EXTRA_DISTS = (
    "hedron-data",
    "hedron-charts",
    "hedron-extras",
    "hedron-jinja",
    "hedron-flask",
    "hedron-django",
    "hedron-explorer",
    "hedron-conformance",
    "hedron-workbench",
    "hedron-posit",
    "hedron-native",
    "hedron-maps",
    "hedron-mcp",
    "hedron-gradio",
    "hedron-notebook",
)


def looks_like_secret_env(name: str) -> bool:
    """Return True when an environment variable name looks secret-bearing."""
    return bool(_SECRET_ENV_RE.search(name))


def redact_env_mapping(env: Mapping[str, str]) -> dict[str, str]:
    """Return a copy of ``env`` with secret-looking keys redacted."""
    out: dict[str, str] = {}
    for key, value in env.items():
        out[str(key)] = "[redacted]" if looks_like_secret_env(str(key)) else str(value)
    return out


def _dist_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def _find_release_toml() -> Path | None:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "docs" / "release.toml"
        if candidate.is_file():
            return candidate
    cwd = Path.cwd() / "docs" / "release.toml"
    return cwd if cwd.is_file() else None


def _train_skew_note(dist_versions: dict[str, str]) -> dict[str, Any] | None:
    path = _find_release_toml()
    if path is None:
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None
    release = data.get("release") or {}
    published = release.get("published_version")
    development = release.get("development_version")
    expected = str(published or development or "").strip()
    train = str(release.get("train") or "").strip()
    if not expected and not train:
        return None
    hedron_ver = dist_versions.get("hedron")
    skew = bool(hedron_ver and expected and hedron_ver != expected)
    train_versions = {
        name: ver
        for name, ver in dist_versions.items()
        if name.lower() in {d.lower() for d in _TRAIN_DISTS}
    }
    multi = len(set(train_versions.values())) > 1 if train_versions else False
    return {
        "release_toml": str(path),
        "train": train or None,
        "expected_version": expected or None,
        "installed_hedron": hedron_ver,
        "train_version_mismatch": skew,
        "multi_version_train": multi,
        "train_versions": train_versions,
    }


def _selected_extras() -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for name in _EXTRA_DISTS:
        ver = _dist_version(name)
        if ver is not None:
            found.append({"name": name, "version": ver})
    return found


def _plugins_snapshot() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        from hedron_core.plugins import get_explorer_panels, get_feature_manifests

        for panel in get_explorer_panels():
            rows.append(
                {
                    "kind": "explorer_panel",
                    "panel_id": panel.panel_id,
                    "plugin": panel.plugin,
                    "title": panel.title,
                }
            )
        for feature in get_feature_manifests():
            rows.append(
                {
                    "kind": "feature",
                    "name": feature.name,
                    "plugin": feature.plugin,
                    "stability": feature.stability,
                }
            )
    except Exception:  # noqa: BLE001 — best-effort registry read
        return rows
    try:
        for ep in entry_points().select(group="hedron.plugins"):
            rows.append({"kind": "entry_point", "name": ep.name, "value": ep.value})
    except Exception:  # noqa: BLE001 — best-effort entry-point read
        return rows
    return rows


def _assets_snapshot() -> list[dict[str, str]]:
    try:
        from hedron_core.registry import get_registry

        return [
            {
                "logical_id": asset.logical_id,
                "kind": asset.kind,
                "path": asset.path,
            }
            for asset in get_registry().assets()
        ]
    except Exception:  # noqa: BLE001 — best-effort
        return []


def _recommendations(
    *,
    dist_versions: dict[str, str],
    train_skew: dict[str, Any] | None,
) -> list[dict[str, str]]:
    recs: list[dict[str, str]] = []
    if "hedron" not in dist_versions:
        recs.append(
            {
                "evidence": "distribution 'hedron' not found via importlib.metadata",
                "message": "Install the hedron distribution into this environment (manual action).",
            }
        )
    if "hedron-core" not in dist_versions and "hedron" in dist_versions:
        recs.append(
            {
                "evidence": "hedron is installed but hedron-core metadata is missing",
                "message": "Ensure hedron-core is installed alongside hedron (manual action).",
            }
        )
    if train_skew and train_skew.get("train_version_mismatch"):
        recs.append(
            {
                "evidence": (
                    f"installed hedron={train_skew.get('installed_hedron')!s} "
                    f"vs release.toml expected={train_skew.get('expected_version')!s}"
                ),
                "message": (
                    "Align installed train packages with docs/release.toml pins "
                    "(no auto-install)."
                ),
            }
        )
    if train_skew and train_skew.get("multi_version_train"):
        versions = train_skew.get("train_versions") or {}
        recs.append(
            {
                "evidence": f"train packages report multiple versions: {versions}",
                "message": (
                    "Reconcile first-party hedron* package versions on the "
                    "coordinated train."
                ),
            }
        )
    return recs


def diagnose_installed_fleet() -> dict[str, Any]:
    """Return a read-only diagnosis of the installed application fleet.

    Does not dump environment variables by default. Does not install or enable
    anything. Recommendations always cite ``evidence``.
    """
    dist_versions: dict[str, str] = {}
    for name in ("hedron", "hedron-core"):
        ver = _dist_version(name)
        if ver is not None:
            dist_versions[name] = ver
    # Also record other installed hedron* distributions for skew analysis.
    for dist in distributions():
        name = str(dist.name)
        if name.lower().startswith("hedron") and name not in dist_versions:
            dist_versions[name] = dist.version

    train_skew = _train_skew_note(dist_versions)
    extras = _selected_extras()
    plugins = _plugins_snapshot()
    assets = _assets_snapshot()
    recommendations = _recommendations(
        dist_versions=dist_versions,
        train_skew=train_skew,
    )
    return {
        "read_only": True,
        "package_doctor": False,
        "automatic_install": False,
        "distributions": {
            "hedron": dist_versions.get("hedron"),
            "hedron-core": dist_versions.get("hedron-core"),
            "all_hedron": dict(sorted(dist_versions.items())),
        },
        "train_skew": train_skew,
        "selected_extras": extras,
        "plugins": plugins,
        "assets": assets,
        "recommendations": recommendations,
        "environment": None,  # never dump env by default; use redact_env_mapping if needed
    }


__all__ = [
    "diagnose_installed_fleet",
    "looks_like_secret_env",
    "redact_env_mapping",
]
