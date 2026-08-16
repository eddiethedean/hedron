"""Upgrade 0.36.0 → 0.37.0: hedron-example ABI unchanged."""

from __future__ import annotations

from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_core.rendering import render
from hedron_elements.example import (
    ABI_VERSION,
    ELEMENT_ID,
    EXAMPLE_OWNERSHIP,
    TAG_NAME,
    Example,
)
from hedron_elements.plugin import register


def setup_function() -> None:
    reset_registry_for_tests()


def teardown_function() -> None:
    reset_registry_for_tests()


def test_example_abi_constants_unchanged() -> None:
    assert TAG_NAME == "hedron-example"
    assert ELEMENT_ID == "hedron-example"
    assert ABI_VERSION == 1
    assert len(EXAMPLE_OWNERSHIP) == 2
    assert EXAMPLE_OWNERSHIP[0].name == "status"
    assert EXAMPLE_OWNERSHIP[0].mode == "controlled"
    assert EXAMPLE_OWNERSHIP[1].name == "expanded"
    assert EXAMPLE_OWNERSHIP[1].mode == "local"


def test_example_registry_still_no_form_contract() -> None:
    class _Ctx:
        def register_diagnostic_owner(self, prefix: str) -> None:
            return None

        def register_feature(self, **kwargs: object) -> None:
            return None

        def register_explorer_panel(self, **kwargs: object) -> None:
            return None

        def register_projection_provider(self, provider: object) -> None:
            return None

    register(_Ctx())  # type: ignore[arg-type]
    meta = get_registry().get_element_definition("hedron-example")
    assert meta is not None
    assert meta.tag_name == "hedron-example"
    assert meta.abi_version == 1
    assert meta.form_contract is None


def test_example_ssr_markup_unchanged() -> None:
    html = render(Example(status="Online")).html
    assert "hedron-example" in html
    assert 'data-hedron-abi="1"' in html
    assert 'data-hedron-element="hedron-example"' in html
    assert 'data-hedron-server-region="content"' in html
    assert "Online" in html
    assert 'type="button"' in html
    assert "Details" in html
