"""Phase 0.19 CONTRACT-019."""

from __future__ import annotations

import pytest

from hedron_core import reset_registry_for_tests
from hedron_core.a11y import (
    AccessibilityContract,
    AccessibilityContractCatalog,
    default_contract,
    seed_reviewed_contracts,
)


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def test_leaf_never_implies_app_conformance() -> None:
    c = default_contract("Button")
    assert c.implies_application_conformance() is False
    assert c.as_dict()["implies_application_conformance"] is False
    assert c.reviewed is False


def test_assert_complete_does_not_auto_heal() -> None:
    empty = AccessibilityContractCatalog()
    with pytest.raises(AssertionError, match="Missing AccessibilityContract"):
        empty.assert_complete()


def test_catalog_completeness_requires_reviewed_seed() -> None:
    catalog = AccessibilityContractCatalog()
    seed_reviewed_contracts(catalog)
    catalog.ensure_registry()  # stubs for non-curated names
    catalog.assert_complete()
    assert catalog.contracts["Main"].reviewed is True
    assert catalog.contracts["Dialog"].reviewed is True


def test_compose_accumulates_limitations() -> None:
    catalog = AccessibilityContractCatalog()
    catalog.register(AccessibilityContract(component="A", limitations=("a",), notes="A"))
    catalog.register(AccessibilityContract(component="B", limitations=("b",), notes="B"))
    composed = catalog.compose("A", "B")
    assert "a" in composed.limitations and "b" in composed.limitations
    assert composed.implies_application_conformance() is False
