"""SECURITY-036: CSP/event/payload adversarial unit checks."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_elements.markup import encode_structured_input, render_element_markup


def test_structured_input_rejects_oversize() -> None:
    with pytest.raises(HedronError) as exc:
        encode_structured_input({"x": "y" * 9000}, instance_id="i")
    assert exc.value.diagnostic.code == "HED-ELEMENT-0005"


def test_markup_never_embeds_handlers() -> None:
    html = render_element_markup(
        tag_name="hedron-example",
        abi_version=1,
        element_id="hedron-example",
        attributes={"status": "Ready"},
        server_content="Ready",
    )
    assert "onclick" not in html.lower()
    assert "onerror" not in html.lower()
    assert "javascript:" not in html.lower()


def test_closing_tag_injection_escaped() -> None:
    html = render_element_markup(
        tag_name="hedron-example",
        abi_version=1,
        element_id="hedron-example",
        server_content="</hedron-example><script>x</script>",
    )
    assert html.count("<hedron-example") == 1
    assert "<script>x</script>" not in html


def test_json_payload_not_executable() -> None:
    enc = encode_structured_input({"status": "ok"}, instance_id="i1")
    assert 'type="application/json"' in enc
    assert "text/javascript" not in enc
