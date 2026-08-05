import pytest

from hedron_charts.annotations import apply_annotations
from hedron_core.diagnostics import HedronError
from hedron_core.visualization import (
    ChartAccessibility,
    ChartAnnotation,
    ChartOutput,
    validate_annotation,
)


def test_annotations() -> None:
    ann = validate_annotation(ChartAnnotation(kind="point", label="P", payload={"x": 1}))
    out = ChartOutput(
        kind="svg", body="<svg></svg>", accessibility=ChartAccessibility(title="t", description="d")
    )
    merged = apply_annotations(out, [ann])
    assert merged.metadata["annotations"]
    with pytest.raises(HedronError):
        validate_annotation(ChartAnnotation(kind="point", label="x", payload={"html": "<b>"}))
