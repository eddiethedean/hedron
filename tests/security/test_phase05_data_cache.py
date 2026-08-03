"""Security corpus for phase 0.5 data/cache surfaces."""

from __future__ import annotations

import pytest

from hedron import cache_data
from hedron_core.cache import build_cache_key, get_cache_traces, reset_cache_for_tests
from hedron_core.security import Secret
from hedron_data import CellUpdate, Column, DataChanges, DataEditor, filter_writable_changes


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_cache_for_tests()


@pytest.mark.security
def test_forged_dataeditor_readonly_and_hidden() -> None:
    editor = DataEditor(
        [{"id": "1", "name": "Ada", "hidden_flag": True}],
        columns=[
            Column(name="id", read_only=True),
            Column(name="name"),
            Column(name="hidden_flag", hidden=True),
        ],
        key_field="id",
        on_save=lambda c: __import__("hedron_data").DataSaveResult(ok=True, accepted=c),
    )
    forged = DataChanges(
        updates=(
            CellUpdate(row_key="1", field="id", value="9"),
            CellUpdate(row_key="1", field="hidden_flag", value=False),
        )
    )
    result = editor.apply_changes(forged)
    assert not result.ok
    assert len(result.errors) == 2


@pytest.mark.security
def test_cache_scope_leak_prevention() -> None:
    @cache_data(ttl=60, scope="tenant", vary_on=("tenant_id", "user_id"))
    def load(tenant_id: int, user_id: int) -> str:
        return f"{tenant_id}:{user_id}"

    assert load(tenant_id=1, user_id=1) == "1:1"
    assert load(tenant_id=1, user_id=2) == "1:2"
    assert load(tenant_id=2, user_id=1) == "2:1"
    # Distinct fingerprints for different tenants/users
    fps = {e.key_fingerprint for e in get_cache_traces() if e.kind in {"miss", "store"}}
    assert len(fps) >= 3


@pytest.mark.security
def test_secret_never_in_cache_key_material() -> None:
    key = build_cache_key(
        identity="secure",
        kwargs={"password": Secret("hunter2"), "ok": 1},
    )
    assert "hunter2" not in key
    assert "password" not in key or "hunter2" not in key


@pytest.mark.security
def test_filter_writable_changes_strips_unauthorized() -> None:
    cleaned, errors = filter_writable_changes(
        DataChanges(
            updates=(
                CellUpdate(row_key="1", field="role", value="admin"),
                CellUpdate(row_key="1", field="name", value="Ada"),
            )
        ),
        writable_fields=frozenset({"name"}),
        read_only_fields=frozenset({"role"}),
        hidden_fields=frozenset(),
    )
    assert len(errors) == 1
    assert cleaned.updates[0].field == "name"


@pytest.mark.security
def test_deletes_require_allow_deletes() -> None:
    cleaned, errors = filter_writable_changes(
        DataChanges(deletes=("1", "2")),
        writable_fields=frozenset({"name"}),
        read_only_fields=frozenset(),
        hidden_fields=frozenset(),
        allow_deletes=False,
    )
    assert cleaned.deletes == ()
    assert len(errors) == 2
