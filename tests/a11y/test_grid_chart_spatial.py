from hedron_data.a11y_spatial import SpatialAlternative, spatial_alternatives_for


def test_spatial_alternatives() -> None:
    alts = spatial_alternatives_for("drag", "fill", "resize", "reorder", "chart-select")
    assert len(alts) == 5
    assert all(not a.traps_browse_mode for a in alts)
    assert all(isinstance(a, SpatialAlternative) for a in alts)
    by_op = {a.operation: a for a in alts}
    assert "Arrow" in by_op["drag"].keyboard or "arrow" in by_op["drag"].keyboard.lower()
    assert by_op["chart-select"].single_pointer
    assert by_op["fill"].keyboard
    assert by_op["resize"].keyboard
    assert by_op["reorder"].keyboard
