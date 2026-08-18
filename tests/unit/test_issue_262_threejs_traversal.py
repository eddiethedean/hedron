"""#262: ThreeJsAdapter must reject percent-encoded path traversal."""

from __future__ import annotations

import pytest

from hedron_charts.optional_adapters import ThreeJsAdapter
from hedron_core.visualization import ChartAccessibility


def _acc() -> ChartAccessibility:
    return ChartAccessibility(title="t", alt="a")


@pytest.mark.parametrize(
    "url",
    [
        "%2e%2e/models/x.glb",
        "%2E%2E/models/x.glb",
        "models/%2e%2e/x.glb",
        "../models/x.glb",
    ],
)
def test_encoded_and_literal_model_traversal_rejected(url: str) -> None:
    with pytest.raises(ValueError, match="traversal"):
        ThreeJsAdapter().compile({"model_url": url, "bytes": 1}, accessibility=_acc())
