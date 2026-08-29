#!/usr/bin/env python3
"""Validate the 1.0 support and stable API contract."""

from __future__ import annotations

import importlib
import inspect
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STABLE = "Development Status :: 5 - Production/Stable"
BETA = "Development Status :: 4 - Beta"


def main() -> int:
    support = tomllib.loads((ROOT / "release/support-matrix.toml").read_text())
    packages = support["packages"]
    errors: list[str] = []
    stable_packages = {
        name for name, item in packages.items() if item.get("maturity") == "stable"
    }
    stable_api = tomllib.loads((ROOT / "release/stable-api.toml").read_text())
    stable_api_packages = set(stable_api["packages"])
    if stable_packages != stable_api_packages:
        errors.append(
            "stable package/API boundary disagrees: "
            f"support={sorted(stable_packages)!r}, api={sorted(stable_api_packages)!r}"
        )
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
            for beta in (
                name
                for name, item in packages.items()
                if item["maturity"] == "beta"
            ):
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
            expected_signature = signatures.get(symbol)
            if expected_signature is None:
                continue
            expected_signature = str(expected_signature).strip()
            try:
                actual_signature = str(inspect.signature(getattr(loaded, symbol))).strip()
            except (TypeError, ValueError) as exc:
                errors.append(f"{distribution}.{symbol}: signature inspection failed: {exc}")
                continue
            if actual_signature != expected_signature:
                errors.append(
                    f"{distribution}.{symbol}: signature drifted; "
                    f"expected {expected_signature!r}, got {actual_signature!r}"
                )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: 1.0 support matrix and stable API contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
