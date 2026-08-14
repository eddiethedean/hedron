from pathlib import Path

from scripts.check_package_docs_inventory import (
    catalog_mentions,
    declared_maturity,
    load_package_facts,
    metadata_maturity,
)


def test_declared_maturity_reads_documentation_label() -> None:
    assert declared_maturity("**Package maturity:** Beta tooling-grade") == "beta"
    assert declared_maturity("**Maturity:** Alpha · incubator") == "alpha"
    assert declared_maturity("No maturity here") is None


def test_catalog_mentions_requires_exact_package_name() -> None:
    assert catalog_mentions("Use `hedron-core`.", "hedron-core")
    assert not catalog_mentions("Use `hedron-core`.", "hedron")


def test_metadata_maturity_reads_development_classifier(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "demo"\nversion = "1.0.0"\n'
        'classifiers = ["Development Status :: 5 - Production/Stable"]\n',
        encoding="utf-8",
    )
    assert metadata_maturity(pyproject) == "stable"


def test_living_fleet_inventory_has_unique_packages() -> None:
    facts = load_package_facts()
    names = [fact.name for fact in facts]
    assert len(names) == len(set(names))
