import pytest

from hedron_core.diagnostics import HedronError
from hedron_core.visualization import ChartEvent, authorized_chart_event, validate_chart_event
from hedron_data.events import GridEditEvent, authorized_grid_event, validate_grid_event


def test_grid_events() -> None:
    ev = validate_grid_event(GridEditEvent(row_key="r1", field="v", payload={"value": 1}))
    authorized_grid_event(ev, allowed_fields=frozenset({"v"}), can_edit=True)
    with pytest.raises(HedronError):
        authorized_grid_event(ev, allowed_fields=frozenset({"other"}), can_edit=True)


def test_chart_events() -> None:
    ev = validate_chart_event(
        ChartEvent(kind="click", trace_id="0", point_index=1, payload={"x": 1})
    )
    authorized_chart_event(ev, allowed_kinds=frozenset({"click", "hover"}))
    with pytest.raises(HedronError):
        authorized_chart_event(ev, allowed_kinds=frozenset({"hover"}))
