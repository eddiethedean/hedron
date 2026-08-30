#!/usr/bin/env python3
"""Keep package catalogs, READMEs, and maturity labels aligned with fleet inventory."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
RELEASE_FILE = ROOT / "docs" / "release.toml"
CATALOG = ROOT / "docs" / "packages" / "index.md"


@dataclass(frozen=True, slots=True)
class PackageFact:
    name: str
    maturity: str


def inventory_path() -> Path:
    release = tomllib.loads(RELEASE_FILE.read_text(encoding="utf-8"))["release"]
    phase = str(release["train"]).replace(".", "")
    return ROOT / "docs" / "acceptance" / f"production-grade-inventory-{phase}.toml"


def load_package_facts(path: Path | None = None) -> list[PackageFact]:
    data = tomllib.loads((path or inventory_path()).read_text(encoding="utf-8"))
    facts: list[PackageFact] = []
    for name in data["packages"]:
        package = data[name]
        facts.append(PackageFact(name=name, maturity=str(package["maturity"]).lower()))
    return facts


def declared_maturity(markdown: str) -> str | None:
    match = re.search(
        r"\*\*(?:Package maturity|Maturity):\*\*\s*(Stable|Beta|Alpha)\b",
        markdown,
        flags=re.IGNORECASE,
    )
    return match.group(1).lower() if match else None


def catalog_mentions(markdown: str, package: str) -> bool:
    return bool(re.search(rf"(?<![A-Za-z0-9_-]){re.escape(package)}(?![A-Za-z0-9_-])", markdown))


def metadata_maturity(pyproject: Path) -> str | None:
    project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
    classifiers = project.get("classifiers", [])
    levels = {
        "Development Status :: 3 - Alpha": "alpha",
        "Development Status :: 4 - Beta": "beta",
        "Development Status :: 5 - Production/Stable": "stable",
    }
    found = [levels[item] for item in classifiers if item in levels]
    if len(found) > 1:
        raise ValueError(f"{pyproject}: multiple development-status classifiers")
    return found[0] if found else None


def main() -> int:
    facts = load_package_facts()
    catalog = CATALOG.read_text(encoding="utf-8")
    failures: list[str] = []

    for fact in facts:
        if not catalog_mentions(catalog, fact.name):
            failures.append(f"docs/packages/index.md does not list {fact.name}")

        package_dir = ROOT / "packages" / fact.name
        readme = package_dir / "README.md"
        if not readme.is_file():
            failures.append(f"{readme.relative_to(ROOT)} is missing")
        else:
            actual = declared_maturity(readme.read_text(encoding="utf-8"))
            if actual != fact.maturity:
                failures.append(
                    f"{readme.relative_to(ROOT)} maturity is {actual or 'missing'}; "
                    f"fleet inventory says {fact.maturity}"
                )

        pyproject = package_dir / "pyproject.toml"
        if pyproject.is_file():
            actual = metadata_maturity(pyproject)
            if actual != fact.maturity:
                failures.append(
                    f"{pyproject.relative_to(ROOT)} classifier is {actual or 'missing'}; "
                    f"fleet inventory says {fact.maturity}"
                )

        package_page = ROOT / "docs" / "packages" / f"{fact.name}.md"
        if package_page.is_file():
            actual = declared_maturity(package_page.read_text(encoding="utf-8"))
            if actual != fact.maturity:
                failures.append(
                    f"{package_page.relative_to(ROOT)} maturity is {actual or 'missing'}; "
                    f"fleet inventory says {fact.maturity}"
                )

    if failures:
        raise SystemExit("\n".join(failures))
    print(
        f"ok: catalog, READMEs, metadata, and package pages agree for {len(facts)} "
        f"fleet entries ({inventory_path().name})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
