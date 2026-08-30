#!/usr/bin/env python3
"""Validate the 1.0 support and stable API contract."""

from __future__ import annotations

import importlib
import inspect
import re
import sys
import tomllib
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STABLE = "Development Status :: 5 - Production/Stable"
BETA = "Development Status :: 4 - Beta"
STABLE_BOUNDARY = (
    "hedron-core",
    "hedron",
    "edron",
    "hedron-data",
    "hedron-charts",
    "hedron-maps",
)


def _canonical_signature(value: object) -> str:
    signature = str(inspect.signature(value)).strip()
    return re.sub(
        r"<object object at 0x[0-9A-Fa-f]+>",
        "<object sentinel>",
        signature,
    )


def _requires_signature(value: object) -> bool:
    return callable(value) and not (inspect.isclass(value) and issubclass(value, Enum))


def _resolve_member(module: object, path: str) -> object:
    value = module
    for part in path.split("."):
        value = getattr(value, part)
    return value


def main() -> int:
    support = tomllib.loads((ROOT / "release/support-matrix.toml").read_text())
    packages = support["packages"]
    errors: list[str] = []
    stable_packages = {name for name, item in packages.items() if item.get("maturity") == "stable"}
    if stable_packages != set(STABLE_BOUNDARY):
        errors.append(
            "1.0 stable package boundary drifted: "
            f"expected={list(STABLE_BOUNDARY)!r}, actual={sorted(stable_packages)!r}"
        )
    stable_api = tomllib.loads((ROOT / "release/stable-api.toml").read_text())
    stable_api_packages = set(stable_api["packages"])
    if stable_packages != stable_api_packages:
        errors.append(
            "stable package/API boundary disagrees: "
            f"support={sorted(stable_packages)!r}, api={sorted(stable_api_packages)!r}"
        )

    release_shape = (ROOT / "docs/acceptance/RELEASE_1_0.md").read_text(encoding="utf-8")
    boundary_sentence = (
        "The Stable 1.0 package boundary is `hedron-core`, `hedron`, `edron`, `hedron-data`,\n"
        "`hedron-charts`, and `hedron-maps`."
    )
    if boundary_sentence not in release_shape:
        errors.append("RELEASE_1_0.md does not publish the exact Stable package boundary")
    support_policy = (ROOT / "docs/acceptance/support-policy-100.md").read_text(encoding="utf-8")
    for distribution in STABLE_BOUNDARY:
        if f"`{distribution}`" not in support_policy:
            errors.append(f"support-policy-100.md omits Stable package {distribution}")
    current_edron_docs = (
        ROOT / "docs/api/EDRON.md",
        ROOT / "docs/api/EDRON_STATE_INTERACTION.md",
        ROOT / "docs/api/EDRON_PACKAGING.md",
    )
    for path in current_edron_docs:
        first_lines = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
        if re.search(r"\bEdron\b[^\n]{0,80}\bBeta\b|\bEdron remains Beta\b", first_lines):
            errors.append(f"{path.relative_to(ROOT)} still labels Stable Edron as Beta")
    for name, contract in packages.items():
        maturity = contract.get("maturity")
        api = contract.get("api")
        if maturity not in {"stable", "beta"} or api not in {"stable", "beta"}:
            errors.append(f"{name}: maturity/api must be stable or beta")
        if maturity == "beta" and api == "stable":
            errors.append(f"{name}: Beta package cannot claim a stable API")
    for distribution, contract in packages.items():
        project_file = ROOT / "packages" / distribution / "pyproject.toml"
        if not project_file.is_file():
            if distribution == "fastapi-workbench":
                continue
            errors.append(f"{distribution}: missing pyproject.toml")
            continue
        project = tomllib.loads(project_file.read_text())["project"]
        classifiers = set(project.get("classifiers", []))
        expected = STABLE if contract["maturity"] == "stable" else BETA
        if expected not in classifiers:
            errors.append(f"{distribution}: missing classifier {expected!r}")
        if contract["maturity"] == "stable":
            dependency_names = {
                re.split(r"[<>=!~;\s]", dependency, maxsplit=1)[0].lower()
                for dependency in project.get("dependencies", [])
            }
            for beta in (name for name, item in packages.items() if item["maturity"] == "beta"):
                if beta.lower() in dependency_names:
                    errors.append(f"{distribution}: stable package depends on Beta {beta}")

    for distribution, contract in stable_api["packages"].items():
        module = distribution.replace("-", "_")
        try:
            loaded = importlib.import_module(module)
        except (ImportError, AttributeError, RuntimeError) as exc:  # pragma: no cover
            errors.append(f"{distribution}: stable API import failed: {exc}")
            continue
        symbols = tuple(contract.get("symbols", ()))
        if len(symbols) != len(set(symbols)):
            errors.append(f"{distribution}: stable API symbol list contains duplicates")
        signatures = contract.get("signatures", {})
        if not isinstance(signatures, dict):
            errors.append(f"{distribution}: signatures must be a table")
            signatures = {}
        if not set(signatures).issubset(set(symbols)):
            errors.append(f"{distribution}: signature table contains a non-stable symbol")
        for symbol in symbols:
            if not hasattr(loaded, symbol):
                errors.append(f"{distribution}: missing stable symbol {symbol}")
                continue
            value = getattr(loaded, symbol)
            expected_signature = signatures.get(symbol)
            if expected_signature is None:
                if _requires_signature(value):
                    errors.append(
                        f"{distribution}.{symbol}: stable callable/class lacks a locked signature"
                    )
                continue
            expected_signature = str(expected_signature).strip()
            try:
                actual_signature = _canonical_signature(value)
            except (TypeError, ValueError) as exc:
                errors.append(f"{distribution}.{symbol}: signature inspection failed: {exc}")
                continue
            if actual_signature != expected_signature:
                errors.append(
                    f"{distribution}.{symbol}: signature drifted; "
                    f"expected {expected_signature!r}, got {actual_signature!r}"
                )
        members = contract.get("members", {})
        if not isinstance(members, dict):
            errors.append(f"{distribution}: members must be a table")
            members = {}
        for path, expected_signature in members.items():
            root_symbol = str(path).split(".", maxsplit=1)[0]
            if root_symbol not in symbols:
                errors.append(f"{distribution}.{path}: member root is not a stable symbol")
                continue
            try:
                value = _resolve_member(loaded, str(path))
                actual_signature = _canonical_signature(value)
            except AttributeError:
                errors.append(f"{distribution}: missing stable member {path}")
                continue
            except (TypeError, ValueError) as exc:
                errors.append(f"{distribution}.{path}: signature inspection failed: {exc}")
                continue
            expected_signature = str(expected_signature).strip()
            if actual_signature != expected_signature:
                errors.append(
                    f"{distribution}.{path}: signature drifted; "
                    f"expected {expected_signature!r}, got {actual_signature!r}"
                )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: 1.0 support matrix and stable API contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
