"""#377: structural_bind encodes and rejects unsafe path params."""

from __future__ import annotations

import pytest

from hedron_core.codes import HED_VIEW_0004
from hedron_core.diagnostics import HedronError
from hedron_core.updates import BindingPlan, StructuralBindingAdapter, structural_bind


def test_path_params_are_percent_encoded() -> None:
    plan = BindingPlan(path_params=("item_id",), required=("item_id",))
    bound = StructuralBindingAdapter().bind(plan, {"item_id": "v1.2"}, path="/v/{item_id}")
    assert bound.path == "/v/v1.2"


def test_slash_query_and_dotdot_path_values_fail_closed() -> None:
    plan = BindingPlan(path_params=("item_id",), required=("item_id",))
    for value in ("a/b", "x?q=evil", "../x", "a..b"):
        with pytest.raises(HedronError) as exc:
            structural_bind(plan, {"item_id": value}, path="/v/{item_id}")
        assert exc.value.diagnostic.code == HED_VIEW_0004
