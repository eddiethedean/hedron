"""ABI-036: element registry schema, conflicts, frozen markup."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_core.registry import (
    ElementFieldOwnership,
    get_registry,
    register_element_definition,
    reset_registry_for_tests,
)
from hedron_elements.markup import encode_structured_input, render_element_markup


@pytest.fixture(autouse=True)
def _reset_registry() -> None:
    reset_registry_for_tests()
    yield
    reset_registry_for_tests()


def test_register_example_definition() -> None:
    register_element_definition(
        logical_id="hedron-example",
        tag_name="hedron-example",
        abi_version=1,
        module_asset_id="hedron-elements:example.mjs",
        attributes=("status",),
        state_ownership=(
            ElementFieldOwnership(name="status", mode="controlled"),
            ElementFieldOwnership(name="expanded", mode="local"),
        ),
        server_regions=("content",),
    )
    # idempotent
    register_element_definition(
        logical_id="hedron-example",
        tag_name="hedron-example",
        abi_version=1,
        module_asset_id="hedron-elements:example.mjs",
        attributes=("status",),
        state_ownership=(
            ElementFieldOwnership(name="status", mode="controlled"),
            ElementFieldOwnership(name="expanded", mode="local"),
        ),
        server_regions=("content",),
    )
    meta = get_registry().get_element_definition("hedron-example")
    assert meta is not None
    assert meta.tag_name == "hedron-example"
    assert meta.abi_version == 1
    assert meta.form_contract is None


def test_conflict_on_different_definition() -> None:
    register_element_definition(
        logical_id="hedron-example",
        tag_name="hedron-example",
        abi_version=1,
        module_asset_id="a",
    )
    with pytest.raises(HedronError) as exc:
        register_element_definition(
            logical_id="hedron-example",
            tag_name="hedron-example",
            abi_version=1,
            module_asset_id="b",
        )
    assert exc.value.diagnostic.code == "HED-ELEMENT-0001"


def test_first_party_prefix() -> None:
    with pytest.raises(HedronError) as exc:
        register_element_definition(
            logical_id="x",
            tag_name="nothedron-x",
            abi_version=1,
            module_asset_id="a",
            first_party=True,
        )
    assert exc.value.diagnostic.code == "HED-ELEMENT-0003"


def test_abi_skew_on_tag() -> None:
    register_element_definition(
        logical_id="hedron-example",
        tag_name="hedron-example",
        abi_version=1,
        module_asset_id="a",
    )
    with pytest.raises(HedronError) as exc:
        register_element_definition(
            logical_id="hedron-example-v2",
            tag_name="hedron-example",
            abi_version=2,
            module_asset_id="b",
        )
    assert exc.value.diagnostic.code == "HED-ELEMENT-0002"


def test_frozen_markup() -> None:
    html = render_element_markup(
        tag_name="hedron-example",
        abi_version=1,
        element_id="hedron-example",
        attributes={"status": "Ready"},
        server_content="Ready",
    )
    assert 'data-hedron-abi="1"' in html
    assert 'data-hedron-element="hedron-example"' in html
    assert 'data-hedron-server-region="content"' in html
    assert "<hedron-example" in html


def test_structured_input_bounds() -> None:
    enc = encode_structured_input({"a": 1}, instance_id="i1")
    assert 'data-hedron-input-for="i1"' in enc
    assert "application/json" in enc
    with pytest.raises(HedronError) as exc:
        encode_structured_input({"x": "y" * 9000}, instance_id="i2")
    assert exc.value.diagnostic.code == "HED-ELEMENT-0005"
