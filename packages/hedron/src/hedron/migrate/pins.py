"""Living-train dependency pins for generated scaffolds."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from hedron_core.compat import tomllib


@lru_cache(maxsize=1)
def release_pin_bounds() -> tuple[str, str]:
    """Return ``(pin_floor, pin_ceiling)`` matching ``hedron new``."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "docs" / "release.toml"
        if not candidate.is_file():
            continue
        release = tomllib.loads(candidate.read_text(encoding="utf-8")).get("release", {})
        floor = str(release.get("pin_floor", "")).strip()
        ceiling = str(release.get("pin_ceiling", "")).strip()
        if floor and ceiling:
            return floor, ceiling
    from hedron import __version__ as package_version

    return package_version, _next_minor_ceiling(package_version)


def _next_minor_ceiling(package_version: str) -> str:
    parts = package_version.split(".")
    if len(parts) < 2 or not parts[1].isdigit():
        raise RuntimeError(f"cannot derive scaffold pin from version {package_version!r}")
    major = int(parts[0])
    minor = int(parts[1])
    return f"{major}.{minor + 1}"


def scaffold_dep(package: str, *, extras: str = "") -> str:
    floor, ceiling = release_pin_bounds()
    name = f"{package}[{extras}]" if extras else package
    return f"{name}>={floor},<{ceiling}"
