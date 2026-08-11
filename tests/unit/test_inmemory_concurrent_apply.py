"""Regression tests for InMemoryDataSource concurrent apply (#114)."""

from __future__ import annotations

import threading

from hedron_data.memory import InMemoryDataSource
from hedron_data.sources import CellUpdate, DataChanges, DataQuery


def test_concurrent_applies_preserve_nonconflicting_updates() -> None:
    """Two threads updating different rows must not silently drop either commit."""
    src = InMemoryDataSource(
        [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}],
        writable_fields=frozenset({"name"}),
        version="1",
    )
    barrier = threading.Barrier(2)
    results: list[bool | None] = [None, None]
    errors: list[BaseException] = []

    def worker(index: int, row_key: str, value: str) -> None:
        try:
            barrier.wait(timeout=5)
            result = src.apply(
                DataChanges(updates=(CellUpdate(row_key=row_key, field="name", value=value),))
            )
            results[index] = result.ok
        except BaseException as exc:  # noqa: BLE001 — collect for main-thread assert
            errors.append(exc)

    threads = [
        threading.Thread(target=worker, args=(0, "1", "A1")),
        threading.Thread(target=worker, args=(1, "2", "B1")),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not errors
    assert results == [True, True]
    page = src.fetch(DataQuery(limit=10))
    by_id = {str(row["id"]): row for row in page.rows}
    assert by_id["1"]["name"] == "A1"
    assert by_id["2"]["name"] == "B1"
    # Two successful commits each bump the dataset version once from "1".
    assert src.dataset_version == "3"
    assert page.version == "3"


def test_concurrent_applies_with_shared_dataset_version_conflict() -> None:
    """Serialized applies: second caller with a stale dataset_version conflicts."""
    src = InMemoryDataSource(
        [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}],
        writable_fields=frozenset({"name"}),
        version="1",
    )
    barrier = threading.Barrier(2)
    outcomes: list[tuple[bool, str]] = []
    lock = threading.Lock()

    def worker(row_key: str, value: str) -> None:
        barrier.wait(timeout=5)
        result = src.apply(
            DataChanges(
                updates=(CellUpdate(row_key=row_key, field="name", value=value),),
                dataset_version="1",
            )
        )
        with lock:
            outcomes.append((result.ok, value))

    threads = [
        threading.Thread(target=worker, args=("1", "A1")),
        threading.Thread(target=worker, args=("2", "B1")),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert len(outcomes) == 2
    ok_count = sum(1 for ok, _ in outcomes if ok)
    assert ok_count == 1
    conflict_count = sum(1 for ok, _ in outcomes if not ok)
    assert conflict_count == 1
    page = src.fetch(DataQuery(limit=10))
    by_id = {str(row["id"]): row for row in page.rows}
    winners = {value for ok, value in outcomes if ok}
    assert len(winners) == 1
    winner = next(iter(winners))
    if winner == "A1":
        assert by_id["1"]["name"] == "A1"
        assert by_id["2"]["name"] == "B"
    else:
        assert by_id["2"]["name"] == "B1"
        assert by_id["1"]["name"] == "A"
