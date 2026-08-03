"""Phase 0.5 unit coverage: sources, table, editor, cache, Auto, utilities."""

from __future__ import annotations

import asyncio

import pytest

from hedron import cache_component, cache_data
from hedron.builtins.files import validate_upload_filename
from hedron_core import (
    Auto,
    CodeViewer,
    ColorMode,
    Expander,
    JSONViewer,
    Metric,
    Progress,
    Status,
    Tabs,
    Toast,
    render,
    resolve_color_mode,
)
from hedron_core.auto import clear_renderers_for_tests, get_last_auto_decision, inspect_data
from hedron_core.cache import (
    build_cache_key,
    get_cache_traces,
    invalidate_tags,
    reset_cache_for_tests,
)
from hedron_core.color_mode import ColorModeToggle
from hedron_core.diagnostics import HedronError
from hedron_core.security import Secret
from hedron_data import (
    CellUpdate,
    Column,
    DataChanges,
    DataEditor,
    DataQuery,
    DataTable,
    InMemoryDataSource,
    filter_writable_changes,
    normalize_rows,
)


@pytest.fixture(autouse=True)
def _reset_cache_and_auto() -> None:
    reset_cache_for_tests()
    clear_renderers_for_tests()


def test_normalize_list_dict() -> None:
    rows = normalize_rows([{"id": 1, "name": "a"}, {"id": 2, "name": "b"}])
    assert rows == [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]


def test_normalize_refuses_lazy_queryset_like() -> None:
    class FakeQuerySet:
        def __iter__(self):  # pragma: no cover
            yield {"id": 1}

    with pytest.raises(HedronError):
        normalize_rows(FakeQuerySet())


def test_data_query_bounds_and_allowlist() -> None:
    q = DataQuery(
        offset=0,
        limit=10_000,
        sort=(("name", "asc"),),
        allowlisted_sort_fields=frozenset({"name"}),
    ).validated(max_page_size=50)
    assert q.limit == 50
    with pytest.raises(ValueError):
        DataQuery(
            sort=(("secret", "asc"),),
            allowlisted_sort_fields=frozenset({"name"}),
        ).validated()


def test_in_memory_source_paging_and_conflict() -> None:
    src = InMemoryDataSource(
        [{"id": "1", "name": "Ada"}, {"id": "2", "name": "Grace"}],
        writable_fields=frozenset({"name"}),
        schema=(Column(name="id", read_only=True).to_schema(), Column(name="name").to_schema()),
        version="1",
    )
    page = src.fetch(DataQuery(limit=1))
    assert len(page.rows) == 1
    assert page.total == 2
    ok = src.apply(
        DataChanges(updates=(CellUpdate(row_key="1", field="name", value="Ada2", row_version="1"),))
    )
    assert ok.ok
    stale = src.apply(
        DataChanges(updates=(CellUpdate(row_key="1", field="name", value="x", row_version="1"),))
    )
    assert not stale.ok
    assert stale.conflicts


def test_forged_readonly_rejected() -> None:
    cleaned, errors = filter_writable_changes(
        DataChanges(updates=(CellUpdate(row_key="1", field="id", value="hack"),)),
        writable_fields=frozenset({"name"}),
        read_only_fields=frozenset({"id"}),
        hidden_fields=frozenset(),
    )
    assert errors
    assert cleaned.updates == ()


def test_datatable_and_csv() -> None:
    table = DataTable(
        [{"id": "1", "name": "Ada", "secret": "x"}],
        columns=[
            Column(name="id", read_only=True),
            Column(name="name"),
            Column(name="secret", secret=True, hidden=True),
        ],
        caption="People",
    )
    html = render(table).html
    assert "<table" in html
    assert "Ada" in html
    assert "People" in html
    csv = table.to_csv()
    assert "name" in csv
    assert "secret" not in csv.splitlines()[0]


def test_dataeditor_apply_policy() -> None:
    editor = DataEditor(
        [{"id": "1", "name": "Ada"}],
        columns=[Column(name="id", read_only=True), Column(name="name")],
        key_field="id",
        on_save=lambda changes: __import__("hedron_data").DataSaveResult(
            ok=True, accepted=changes, version="1"
        ),
    )
    result = editor.apply_changes(
        DataChanges(updates=(CellUpdate(row_key="1", field="id", value="9"),))
    )
    assert not result.ok
    html = render(editor).html
    assert "hedron-data-editor" in html
    assert "data-hedron-module" in html


def test_cache_data_hit_miss_and_scope_isolation() -> None:
    calls = {"n": 0}

    @cache_data(ttl=60, scope="tenant", vary_on=("tenant_id",))
    def load(tenant_id: int) -> int:
        calls["n"] += 1
        return tenant_id * 10

    assert load(tenant_id=1) == 10
    assert load(tenant_id=1) == 10
    assert calls["n"] == 1
    assert load(tenant_id=2) == 20
    assert calls["n"] == 2
    kinds = [e.kind for e in get_cache_traces()]
    assert "miss" in kinds and "hit" in kinds


def test_cache_rejects_public_user_specific() -> None:
    @cache_component(ttl=10, scope="public")
    def user_card(user_id: int) -> str:
        return f"user-{user_id}"

    assert user_card(user_id=1) == "user-1"
    assert any(e.kind == "reject" for e in get_cache_traces())


def test_cache_secret_not_in_key_plaintext() -> None:
    key = build_cache_key(
        identity="fn",
        kwargs={"token": Secret("super-secret")},
        scope="private",
    )
    assert "super-secret" not in key


def test_cache_invalidation_tags() -> None:
    @cache_data(ttl=60, tags=("t1",))
    def load() -> str:
        return "x"

    assert load() == "x"
    assert invalidate_tags("t1") >= 1
    assert load() == "x"


def test_async_cache() -> None:
    calls = {"n": 0}

    @cache_data(ttl=30, scope="private")
    async def load(x: int) -> int:
        calls["n"] += 1
        return x

    assert asyncio.run(load(3)) == 3
    assert asyncio.run(load(3)) == 3
    assert calls["n"] == 1


def test_auto_tabular_and_mapping() -> None:
    node = Auto([{"id": 1, "name": "Ada"}])
    html = render(node).html
    assert "<table" in html
    decision = get_last_auto_decision()
    assert decision is not None
    assert decision.selected == "datatable"
    html2 = render(Auto({"a": 1, "b": 2})).html
    assert "<dl" in html2 or "a" in html2


def test_auto_override_and_chart_reject() -> None:
    class FakeFigure:
        pass

    FakeFigure.__module__ = "matplotlib.figure"
    with pytest.raises(HedronError):
        render(Auto(FakeFigure()))
    html = render(Auto("hello", as_="text")).html
    assert "hello" in html


def test_inspect_data_bounded() -> None:
    report = inspect_data([{"id": i, "lat": 1.0} for i in range(10)])
    assert report.bounded
    assert "id" in report.columns
    assert "lat" in report.geospatial_columns


def test_utilities_render() -> None:
    assert "Team" in render(Metric("Team", 3, delta="+1", delta_tone="up")).html
    assert "print" in render(CodeViewer("print(1)", language="python")).html
    assert "***" in render(JSONViewer({"password": "x", "ok": True})).html
    assert "<progress" in render(Progress(50, maximum=100)).html
    assert 'role="status"' in render(Status("Ready")).html
    assert "Toast" in render(Toast("Toast")).html or "aria-live" in render(Toast("Hi")).html
    assert "<details" in render(Expander("More", "body")).html
    assert 'role="tablist"' in render(Tabs(("One", "a"), ("Two", "b"), active="One")).html
    assert resolve_color_mode(ColorMode.SYSTEM, system_dark=True) == "dark"
    assert "data-hedron-color-mode" in render(ColorModeToggle()).html


def test_upload_filename_validation() -> None:
    assert validate_upload_filename("roster.csv") == "roster.csv"
    with pytest.raises(ValueError):
        validate_upload_filename("../etc/passwd")
    with pytest.raises(ValueError):
        validate_upload_filename("")
