"""CONF-040 portable element ABI fixtures."""

from __future__ import annotations

import pytest

from hedron_conformance import load_element_abi_fixtures
from hedron_core.diagnostics import HedronError
from hedron_core.element_types import ElementFieldOwnership
from hedron_core.registry import register_element_definition, reset_registry_for_tests


def test_element_abi_fixture_packet_shape() -> None:
    packet = load_element_abi_fixtures()
    assert packet["kind"] == "element_abi"
    assert {row["id"] for row in packet["fixtures"]} >= {
        "positive-minimal-meta",
        "negative-missing-hyphen",
        "negative-capability-ownership",
    }


def test_element_abi_fixtures_execute() -> None:
    packet = load_element_abi_fixtures()
    for row in packet["fixtures"]:
        reset_registry_for_tests()
        meta = dict(row["meta"])
        ownership = meta.pop("state_ownership", None)
        kwargs = dict(meta)
        kwargs["first_party"] = False
        if ownership:
            kwargs["state_ownership"] = tuple(ElementFieldOwnership(**item) for item in ownership)
        if row["expect"] == "pass":
            register_element_definition(**kwargs)
        else:
            with pytest.raises(HedronError) as exc:
                register_element_definition(**kwargs)
            assert row["error_contains"] in str(exc.value)
