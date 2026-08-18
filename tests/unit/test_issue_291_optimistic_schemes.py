"""#291: OptimisticMutation must reject executable URL schemes, not only javascript:."""

from __future__ import annotations

import pytest

from hedron_data.optimistic import OptimisticMutation, OptimisticPatch


def _mutate(value: str) -> OptimisticMutation:
    return OptimisticMutation.from_cell_edits(
        action_id="dataeditor.save",
        base_revision="1",
        patches=[OptimisticPatch(row_key="1", field="href", value=value)],
        allowed_fields=frozenset({"href"}),
    )


@pytest.mark.parametrize(
    "value",
    [
        "javascript:alert(1)",
        "  javascript:alert(1)",
        "vbscript:msgbox(1)",
        "data:text/html,hi",
        "blob:https://evil.example/1",
    ],
)
def test_optimistic_rejects_dangerous_schemes(value: str) -> None:
    with pytest.raises(ValueError, match="executable URLs"):
        _mutate(value)
