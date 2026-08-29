#!/usr/bin/env python3
"""Validate the 1.0 support and stable API contract."""

from __future__ import annotations

import importlib
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

    api = tomllib.loads((ROOT / "release/stable-api.toml").read_text())
    for distribution, contract in api["packages"].items():
        module = distribution.replace("-", "_")
        try:
            loaded = importlib.import_module(module)
        except (ImportError, AttributeError, RuntimeError) as exc:  # pragma: no cover
            errors.append(f"{distribution}: stable API import failed: {exc}")
            continue
        for symbol in contract["symbols"]:
            if not hasattr(loaded, symbol):
                errors.append(f"{distribution}: missing stable symbol {symbol}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: 1.0 support matrix and stable API contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
