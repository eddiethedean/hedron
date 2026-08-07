"""Adversarial EVAL-020 cases for hx-vals / hx-headers js: reject."""

from __future__ import annotations

import pytest

from hedron_core import html
from hedron_core.diagnostics import HedronError


@pytest.mark.security
@pytest.mark.parametrize(
    "value",
    [
        "js:1",
        " js:1",
        "{js:1}",
        "JS:{x:1}",
        "foo,js:bar",
    ],
)
def test_adversarial_js_vals_rejected(value: str) -> None:
    with pytest.raises(HedronError) as exc:
        html.span(**{"hx-vals": value})
    assert exc.value.diagnostic.code == "HED-SEC-0011"
