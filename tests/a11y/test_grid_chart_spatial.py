from hedron_data.a11y_spatial import spatial_alternatives_for


def test_spatial_alternatives() -> None:
    alts = spatial_alternatives_for("drag", "fill", "resize", "reorder", "chart-select")
    assert len(alts) == 5
    assert all(not a.traps_browse_mode for a in alts)
