"""RESEARCH-049 quarantined experimental features with no Supported leakage."""

from __future__ import annotations

import hedron
import hedron_core
from hedron_core.research_disposition import (
    EXPERIMENTAL_SYMBOLS,
    RESEARCH_CANDIDATES,
    RESEARCH_DISPOSITIONS,
    RESEARCH_SUPPORTED,
)


def test_research_is_not_supported() -> None:
    assert RESEARCH_SUPPORTED == ()
    assert set(RESEARCH_CANDIDATES) == {"partial-validation", "missing-sentinel", "fail-fast"}
    assert RESEARCH_DISPOSITIONS["missing-sentinel"] == "exclude"
    public = set(hedron.__all__) | set(hedron_core.__all__)
    for name in EXPERIMENTAL_SYMBOLS:
        assert name not in public
        assert not hasattr(hedron, name)
