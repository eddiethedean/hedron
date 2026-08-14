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


@pytest.mark.parametrize(
    "tag_name",
    [
        'hedron-x"><img src=x onerror=alert(1)><x x',
        "hedron-example/><script>x</script><hedron-x",
        "hedron example",
        "hedron_example",
        "div",
        "hedron-",
    ],
)
def test_markup_rejects_adversarial_tag_names(tag_name: str) -> None:
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name=tag_name,
            abi_version=1,
            element_id="hedron-example",
            server_content="ok",
        )
    assert exc.value.diagnostic.code == "HED-ELEMENT-0003"


def test_markup_rejects_space_bearing_attribute_names() -> None:
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name="hedron-example",
            abi_version=1,
            element_id="hedron-example",
            attributes={"foo onclick=alert(1)": "x"},
            server_content="ok",
        )
    assert exc.value.diagnostic.code == "HED-SEC-0010"


def test_markup_rejects_quote_breakout_attribute_names() -> None:
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name="hedron-example",
            abi_version=1,
            element_id="hedron-example",
            attributes={'foo" onclick="alert(1)': "x"},
            server_content="ok",
        )
    assert exc.value.diagnostic.code == "HED-SEC-0010"


def test_markup_rejects_on_handler_attribute_names() -> None:
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name="hedron-example",
            abi_version=1,
            element_id="hedron-example",
            attributes={"onclick": "alert(1)"},
            server_content="ok",
        )
    assert exc.value.diagnostic.code == "HED-SEC-0002"


@pytest.mark.parametrize(
    "attributes",
    [
        {"data-hedron-abi": "999"},
        {"data-hedron-element": "other"},
        {"data-hedron-input": "hijack"},
    ],
)
def test_markup_rejects_overriding_frozen_abi_attributes(
    attributes: dict[str, str],
) -> None:
    with pytest.raises(HedronError) as exc:
        render_element_markup(
            tag_name="hedron-example",
            abi_version=1,
            element_id="hedron-example",
            attributes=attributes,
            server_content="ok",
            instance_id="i1",
        )
    assert exc.value.diagnostic.code == "HED-ELEMENT-0003"


def test_markup_frozen_abi_attributes_win_over_caller_order() -> None:
    html = render_element_markup(
        tag_name="hedron-example",
        abi_version=1,
        element_id="hedron-example",
        attributes={"status": "Ready"},
        server_content="Ready",
        instance_id="i1",
    )
    assert 'data-hedron-abi="1"' in html
    assert 'data-hedron-element="hedron-example"' in html
    assert 'data-hedron-input="i1"' in html
    assert html.count("data-hedron-abi=") == 1


def test_markup_strips_nul_from_content_and_values() -> None:
    html = render_element_markup(
        tag_name="hedron-example",
        abi_version=1,
        element_id="hedron-example",
        attributes={"status": "Re\x00ady"},
        server_content="ok\x00<script>",
    )
    assert "\x00" not in html
    assert 'status="Ready"' in html
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
