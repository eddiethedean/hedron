#!/usr/bin/env python3
"""Fail when Hedron's vendored HTMX assets lag npm's stable releases."""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CORE_PIN_SOURCE = ROOT / "scripts" / "asset_audit.py"
EXTENSION_PIN_SOURCE = (
    ROOT / "packages" / "hedron-core" / "src" / "hedron_core" / "htmx_extensions.py"
)
REGISTRY_BASE = "https://registry.npmjs.org"


@dataclass(frozen=True, slots=True)
class AssetPin:
    package: str
    version: str
    source: Path


def _literal_string(node: ast.AST | None, *, context: str) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    raise ValueError(f"{context} must be a string literal")


def read_core_pin(path: Path = CORE_PIN_SOURCE) -> AssetPin:
    """Read ``EXPECTED_VERSION`` without importing the audit module."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "EXPECTED_VERSION"
            for target in node.targets
        ):
            return AssetPin(
                "htmx.org", _literal_string(node.value, context="EXPECTED_VERSION"), path
            )
    raise ValueError(f"EXPECTED_VERSION was not found in {path}")


def read_extension_pins(path: Path = EXTENSION_PIN_SOURCE) -> tuple[AssetPin, ...]:
    """Read every literal ``ExtensionAsset(name=..., version=...)`` pin."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    pins: list[AssetPin] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        called = node.func
        if not (isinstance(called, ast.Name) and called.id == "ExtensionAsset"):
            continue
        keywords = {keyword.arg: keyword.value for keyword in node.keywords if keyword.arg}
        name = _literal_string(keywords.get("name"), context="ExtensionAsset.name")
        version = _literal_string(keywords.get("version"), context=f"{name}.version")
        pins.append(AssetPin(name, version, path))
    if not pins:
        raise ValueError(f"no ExtensionAsset pins were found in {path}")
    names = [pin.package for pin in pins]
    if len(names) != len(set(names)):
        raise ValueError(f"duplicate extension package pins in {path}")
    return tuple(sorted(pins, key=lambda pin: pin.package))


def npm_latest(
    package: str,
    *,
    registry_base: str = REGISTRY_BASE,
    open_url: Callable[..., object] = urlopen,
) -> str:
    """Return the npm ``latest`` dist-tag, which represents the stable channel."""
    url = f"{registry_base.rstrip('/')}/{quote(package, safe='')}"
    request = Request(url, headers={"Accept": "application/vnd.npm.install-v1+json"})
    with open_url(request, timeout=20) as response:  # type: ignore[attr-defined]
        payload = json.load(response)  # type: ignore[arg-type]
    latest = payload.get("dist-tags", {}).get("latest") if isinstance(payload, dict) else None
    if not isinstance(latest, str) or not latest.strip():
        raise ValueError(f"npm metadata for {package!r} has no non-empty dist-tags.latest")
    return latest.strip()


def _source_label(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def check_pins(
    pins: tuple[AssetPin, ...],
    *,
    latest_for: Callable[[str], str] = npm_latest,
) -> tuple[list[str], list[str]]:
    """Return human-readable outdated and lookup-error messages."""
    outdated: list[str] = []
    lookup_errors: list[str] = []
    for pin in pins:
        try:
            latest = latest_for(pin.package)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            lookup_errors.append(f"{pin.package}: could not query npm stable version: {exc}")
            continue
        if pin.version != latest:
            outdated.append(
                f"{pin.package}: pinned {pin.version}, latest stable {latest}. "
                f"Upgrade the pin and vendored asset in {_source_label(pin.source)} to {latest}."
            )
    return outdated, lookup_errors


def _github_error(message: str) -> None:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        escaped = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::error title=HTMX stable version check::{escaped}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry-base",
        default=REGISTRY_BASE,
        help="npm registry base URL (primarily for deterministic tests)",
    )
    args = parser.parse_args(argv)

    try:
        pins = (read_core_pin(), *read_extension_pins())
    except (OSError, SyntaxError, ValueError) as exc:
        message = f"could not read HTMX pins: {exc}"
        _github_error(message)
        print(f"HTMX version check failed:\n- {message}", file=sys.stderr)
        return 2

    outdated, lookup_errors = check_pins(
        pins,
        latest_for=lambda package: npm_latest(package, registry_base=args.registry_base),
    )
    failures = [*outdated, *lookup_errors]
    if failures:
        for failure in failures:
            _github_error(failure)
        print("HTMX version check failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1

    versions = ", ".join(f"{pin.package}={pin.version}" for pin in pins)
    print(f"ok: all HTMX pins match npm stable ({versions})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
