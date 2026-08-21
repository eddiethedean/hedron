"""BUDGET-056 evidence."""

from __future__ import annotations

import pytest

from hedron_core.security_plane import (
    BudgetExceeded,
    RequestBudget,
    RequestBudgetLimits,
    get_request_budget,
    reset_request_budget,
    set_request_budget,
)


def test_budget_056_nested_monotonic_ledger() -> None:
    budget = RequestBudget(limits=RequestBudgetLimits(body_bytes=100, concurrency=2))
    token = set_request_budget(budget)
    try:
        assert get_request_budget() is budget
        budget.charge("body_bytes", 40)
        child = budget.child(RequestBudgetLimits(body_bytes=100, concurrency=1))
        child.charge("body_bytes", 50)
        assert budget.used("body_bytes") == 90
        with pytest.raises(BudgetExceeded):
            child.charge("body_bytes", 20)
        # Nested child cannot loosen concurrency above parent remaining semantics.
        with pytest.raises(BudgetExceeded):
            child.charge("concurrency", 2)
        budget.charge("concurrency", 2)
        with pytest.raises(BudgetExceeded):
            budget.charge("concurrency", 1)
        budget.close()
        with pytest.raises(BudgetExceeded):
            child.charge("form_fields", 1)
    finally:
        reset_request_budget(token)
