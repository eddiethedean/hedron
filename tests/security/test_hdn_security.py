"""HDN security and bounded fuzz foundations."""

from __future__ import annotations

import time
from contextlib import suppress

import pytest

from hedron_core import HedronError, compile_hdn
from hedron_core.hdn.expr import eval_expr


@pytest.mark.security
def test_hdn_blocks_dunder_and_attr_escape() -> None:
    with pytest.raises(HedronError):
        eval_expr("obj.__class__", {"obj": object()})
    with pytest.raises(HedronError):
        eval_expr("(1).__class__", {})


@pytest.mark.security
def test_hdn_blocks_arbitrary_calls() -> None:
    with pytest.raises(HedronError) as exc:
        compile_hdn("{evil()}")
    assert exc.value.diagnostic.code == "HED-HDN-0007"


def test_hdn_fuzz_bounded() -> None:
    payloads = [
        "<" * 1000,
        "{" * 200 + "}" * 200,
        "<div>" + ("{x}" * 100) + "</div>",
        "<!--" + ("a" * 500),
        "<DivAttr={x}></Div>",
    ]
    start = time.monotonic()
    for payload in payloads:
        with suppress(HedronError):
            compile_hdn(payload)
    assert time.monotonic() - start < 2.0
