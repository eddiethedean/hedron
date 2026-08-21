"""SENS-056 evidence."""

from __future__ import annotations

import pytest

from hedron_core.security import Secret
from hedron_core.security_plane import (
    SensitivityClass,
    SensitiveLabel,
    SensitiveSinkError,
    SensitiveValue,
    clear_declassification_records,
    declassification_records,
    declassify,
    enforce_sink,
    walk_and_enforce,
)


def test_sens_056_label_enforcement_and_declassification() -> None:
    clear_declassification_records()
    labeled = SensitiveValue(
        "tok_live",
        SensitiveLabel(SensitivityClass.SECRET, source="credential", path="token"),
    )
    with pytest.raises(SensitiveSinkError):
        enforce_sink(labeled, sink="html")
    redacted = enforce_sink(labeled, sink="log")
    assert "tok_live" not in str(redacted)
    public = declassify(
        labeled,
        target=SensitivityClass.PUBLIC,
        reason="reviewed export",
        actor="ops",
    )
    assert public.label.classification is SensitivityClass.PUBLIC
    assert declassification_records()
    nested = walk_and_enforce({"a": Secret("x"), "b": [labeled]}, sink="log")
    assert "x" not in str(nested)
