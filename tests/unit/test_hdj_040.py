"""HDJ-040 element declaration parity."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_core.registry import get_registry, register_element_definition, reset_registry_for_tests
from hedron_jinja.source import parse_hdj_source, validate_element_declarations


def _hdj(*, elements: str = "", body: str = "<p>ok</p>") -> str:
    return f"""---hdj
version = 1
kind = "page"
profile = "full"
{elements}---
{body}
"""


def test_hdj_parses_element_metadata() -> None:
    source = _hdj(
        elements="""
elements = ["ext-probe"]
element_abi = { "ext-probe" = 1 }
element_modules = { "ext-probe" = "demo:ext-probe.mjs" }
element_events = { "ext-probe" = ["ext-probe-change"] }
"""
    )
    parsed = parse_hdj_source("probe.hdj", source)
    assert parsed.declaration.elements == ("ext-probe",)
    assert parsed.declaration.element_abi["ext-probe"] == 1
    assert parsed.declaration.element_modules["ext-probe"] == "demo:ext-probe.mjs"
    assert parsed.declaration.element_events["ext-probe"] == ("ext-probe-change",)


def test_hdj_requires_custom_elements_feature() -> None:
    source = """---hdj
version = 1
kind = "page"
profile = "minimal"
elements = ["ext-probe"]
---
<p>ok</p>
"""
    with pytest.raises(HedronError):
        parse_hdj_source("bad.hdj", source)


def test_hdj_fails_closed_on_unknown_key() -> None:
    source = """---hdj
version = 1
kind = "page"
profile = "full"
element_secret = true
---
<p>ok</p>
"""
    with pytest.raises(HedronError):
        parse_hdj_source("unknown.hdj", source)


def test_validate_element_declarations_against_registry() -> None:
    reset_registry_for_tests()
    register_element_definition(
        logical_id="demo:ext-probe",
        tag_name="ext-probe",
        abi_version=1,
        module_asset_id="demo:ext-probe.mjs",
        first_party=False,
    )
    parsed = parse_hdj_source(
        "ok.hdj",
        _hdj(elements='elements = ["ext-probe"]\nelement_abi = { "ext-probe" = 1 }\n'),
    )
    validate_element_declarations(parsed.declaration, registry=get_registry())
    missing = parse_hdj_source(
        "missing.hdj",
        _hdj(elements='elements = ["ext-missing"]\n'),
    )
    with pytest.raises(ValueError, match="unregistered"):
        validate_element_declarations(missing.declaration, registry=get_registry())
