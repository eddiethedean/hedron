"""Phase 0.5 unit coverage: sources, table, editor, cache, Auto, utilities."""

from __future__ import annotations

import asyncio
from pathlib import Path

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
    Text,
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


def test_cache_data_caches_none_results() -> None:
    """#100: cached ``None`` must be a hit, not treated as a miss."""
    reset_cache_for_tests()
    calls = {"n": 0}

    @cache_data(ttl=60, scope="public")
    def maybe_missing() -> None:
        calls["n"] += 1
        return

    assert maybe_missing() is None
    assert maybe_missing() is None
    assert calls["n"] == 1

    async def _async_none() -> None:
        calls["async"] = 0

        @cache_data(ttl=60, scope="public")
        async def async_maybe_missing() -> None:
            calls["async"] += 1
            return

        assert await async_maybe_missing() is None
        assert await async_maybe_missing() is None
        assert calls["async"] == 1

    asyncio.run(_async_none())


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
    @cache_data(ttl=60, tags=("t1",), vary_on=("k",))
    def load(*, k: str = "default") -> str:
        return "x"

    assert load(k="a") == "x"
    assert invalidate_tags("t1") >= 1
    assert load(k="a") == "x"


def test_async_cache() -> None:
    calls = {"n": 0}

    @cache_data(ttl=30, scope="private", vary_on=("x",))
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
    assert 'name="csrf_token"' in render(ColorModeToggle(csrf_token="abc")).html


def test_sidebar_render() -> None:
    from hedron_core import Sidebar

    html = render(Sidebar(Text("nav"), label="Main")).html
    assert "hedron-sidebar" in html
    assert 'aria-label="Main"' in html


def test_async_dataeditor_requires_page() -> None:
    from hedron_data import AsyncInMemoryDataSource

    async_src = AsyncInMemoryDataSource(
        InMemoryDataSource([{"id": "1", "name": "Ada"}], writable_fields=frozenset({"name"}))
    )
    with pytest.raises(HedronError) as exc:
        DataEditor(source=async_src, columns=[Column(name="id"), Column(name="name")])
    assert exc.value.diagnostic.code == "HED-DATA-0006"

    page = asyncio.run(async_src.fetch(DataQuery(limit=10)))
    editor = DataEditor(
        source=async_src,
        page=page,
        columns=[Column(name="id", read_only=True), Column(name="name", writable=True)],
        key_field="id",
    )
    with pytest.raises(HedronError) as apply_exc:
        editor.apply_changes(
            DataChanges(updates=(CellUpdate(row_key="1", field="name", value="Ada2"),))
        )
    assert apply_exc.value.diagnostic.code == "HED-DATA-0006"
    # Close any unawaited coroutine from the sync apply probe without leaking.
    result = asyncio.run(
        editor.apply_changes_async(
            DataChanges(updates=(CellUpdate(row_key="1", field="name", value="Ada2"),))
        )
    )
    assert result.ok


def test_filter_rejects_unauthorized_deletes_and_non_mapping_inserts() -> None:
    cleaned, errors = filter_writable_changes(
        DataChanges(deletes=("1",), inserts=("not-a-mapping",)),  # type: ignore[arg-type]
        writable_fields=frozenset({"name"}),
        read_only_fields=frozenset({"id"}),
        hidden_fields=frozenset(),
        allow_deletes=False,
    )
    assert cleaned.deletes == ()
    assert cleaned.inserts == ()
    assert len(errors) == 2


def test_cache_sensitive_scope_requires_vary_on() -> None:
    reset_cache_for_tests()

    @cache_data(ttl=60, scope="user")
    def load(user_id: int) -> int:
        return user_id

    assert load(user_id=1) == 1
    assert any(e.kind == "reject" for e in get_cache_traces())


def test_cache_single_flight_concurrent_waiters() -> None:
    import threading
    import time

    from hedron_core.cache import InMemoryCacheBackend

    backend = InMemoryCacheBackend()
    calls = {"n": 0}
    barrier = threading.Barrier(4)

    def loader() -> str:
        calls["n"] += 1
        time.sleep(0.05)
        return "ok"

    results: list[str] = []

    def worker() -> None:
        barrier.wait()
        results.append(backend.single_flight("k", loader))

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert results == ["ok", "ok", "ok", "ok"]
    assert calls["n"] == 1


def test_cache_single_flight_cross_generation_isolation() -> None:
    """#576: waiters keep a per-generation flight object; gen-2 cannot overwrite gen-1."""
    import threading

    from hedron_core.cache import InMemoryCacheBackend
    from hedron_core.cache.memory import _SyncFlight

    backend = InMemoryCacheBackend()
    results: list[tuple[str, str]] = []
    owner_in_loader = threading.Event()
    waiter_joined = threading.Event()
    release_loader = threading.Event()
    gen1_flight: list[_SyncFlight] = []

    def owner() -> None:
        def loader() -> str:
            with backend._lock:
                gen1_flight.append(backend._flights["k"])
            owner_in_loader.set()
            assert waiter_joined.wait(2)
            release_loader.wait(2)
            return "v1"

        results.append(("o1", backend.single_flight("k", loader)))

    def waiter() -> None:
        assert owner_in_loader.wait(2)

        # Ensure we are counted as a waiter on gen-1 before releasing the owner loader.
        def mark_joined() -> None:
            deadline = __import__("time").monotonic() + 2
            while __import__("time").monotonic() < deadline:
                with backend._lock:
                    flight = backend._flights.get("k")
                    if flight is not None and flight.waiters >= 1:
                        waiter_joined.set()
                        return
                __import__("time").sleep(0.001)
            waiter_joined.set()

        __import__("threading").Thread(target=mark_joined, daemon=True).start()
        results.append(("w1", backend.single_flight("k", lambda: "bad")))

    t_owner = threading.Thread(target=owner)
    t_waiter = threading.Thread(target=waiter)
    t_owner.start()
    t_waiter.start()
    assert waiter_joined.wait(2)
    # Start gen-2 while gen-1 waiters still exist: clear store and begin a new flight.
    with backend._lock:
        backend._store.clear()
        # gen-1 should still be the mapped flight until owner finishes
        assert backend._flights.get("k") is gen1_flight[0]

    def owner2() -> None:
        # Block until gen-1 owner releases the map slot by finishing.
        release_loader.set()
        deadline = __import__("time").monotonic() + 2
        while __import__("time").monotonic() < deadline:
            with backend._lock:
                if "k" not in backend._flights:
                    break
            __import__("time").sleep(0.001)
        results.append(("o2", backend.single_flight("k", lambda: "v2")))

    t2 = threading.Thread(target=owner2)
    t2.start()
    for t in (t_owner, t_waiter, t2):
        t.join(5)

    assert dict(results) == {"o1": "v1", "w1": "v1", "o2": "v2"}
    assert gen1_flight[0].result == "v1"
    assert gen1_flight[0].has_result is True


def test_upload_filename_validation() -> None:
    from hedron.builtins.files import validate_upload_size

    assert validate_upload_filename("roster.csv") == "roster.csv"
    with pytest.raises(ValueError):
        validate_upload_filename("../etc/passwd")
    with pytest.raises(ValueError):
        validate_upload_filename("")
    assert validate_upload_size(10, maximum_size=100) == 10
    with pytest.raises(ValueError):
        validate_upload_size(200, maximum_size=100)


def test_safe_download_requires_auth(tmp_path: Path) -> None:
    from hedron.builtins.files import safe_download_response

    path = tmp_path / "roster.csv"
    path.write_text("id,name\n1,Ada\n", encoding="utf-8")
    with pytest.raises(PermissionError):
        safe_download_response(path, root=tmp_path, filename="roster.csv", authorized=False)
    response = safe_download_response(path, root=tmp_path, filename="roster.csv", authorized=True)
    assert response.media_type == "text/csv" or "octet-stream" in (response.media_type or "")


def test_theme_light_override_emitted() -> None:
    from hedron_core.theme import default_theme, emit_theme_css

    css = emit_theme_css(default_theme())
    assert ':root[data-theme="light"]' in css
    assert ':root:not([data-theme="light"])' in css
