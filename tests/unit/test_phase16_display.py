"""Phase 0.16 display adapters and recipes."""

from __future__ import annotations

import pytest

from hedron.testing import assert_renders
from hedron_extras.display import DiagramOutput, LogConsole, TokenWeightedText


def test_log_console_rejects_global_capture() -> None:
    with pytest.raises(ValueError):
        LogConsole(producer="stdout")
    html = assert_renders(
        LogConsole([{"text": "hello", "level": "info"}], producer="job:demo"),
        contains="hedron-log-console",
    )
    assert 'data-backpressure="drop-oldest"' in html


def test_token_weighted_and_diagram() -> None:
    assert_renders(
        TokenWeightedText([{"text": "hi", "weight": 0.8}, {"text": " ", "weight": 0.0}]),
        contains="hedron-token-weighted",
    )
    assert_renders(
        DiagramOutput("graph TD; A-->B;", format="mermaid"),
        contains="hedron-diagram-output",
    )
    with pytest.raises(ValueError):
        DiagramOutput("x", format="raw-html")
