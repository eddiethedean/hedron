"""Phase 0.18 EXAMPLE-018: ExampleSet cache provenance and invalidation."""

from __future__ import annotations

from hedron_core import ExampleItem, ExampleSet


def test_example_set_cache_key_and_stale() -> None:
    s = ExampleSet(set_id="samples", action_id="classify", model_version="1", code_version="1")
    s.add(ExampleItem(example_id="e1", label="cat", inputs={"text": "meow"}, provenance="synth"))
    s.add(
        ExampleItem(
            example_id="e2",
            label="secret",
            inputs={"text": "x"},
            authorized_roles=("admin",),
        )
    )
    assert s.page(role="user") == [s._items[0]]
    assert len(s.page(role="admin")) == 2

    key1 = s.cache_key_for("e1")
    result = s.store_result("e1", {"label": "cat"}, cost_units=1.5, retention_seconds=10)
    assert result.cache_key == key1
    assert result.cost_units == 1.5
    cached = s.get_cached("e1")
    assert cached is not None and not cached.stale

    stale = s.get_cached("e1", now=result.generated_at + 11)
    assert stale is not None and stale.stale

    s.model_version = "2"
    key2 = s.cache_key_for("e1")
    assert key1 != key2
    assert s.invalidate() == 1
    assert s.get_cached("e1") is None
