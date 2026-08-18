"""#254: RedisCacheBackend value keys must not collide with tag indexes."""

from __future__ import annotations

import pytest
from tests.ops.test_external_cache import _StubRedis

from hedron_core.redis_cache import RedisCacheBackend


def test_tag_prefixed_value_keys_are_rejected() -> None:
    backend = RedisCacheBackend(_StubRedis())
    with pytest.raises(ValueError, match="tag:"):
        backend.set("tag:foo", {"secret": 1})


def test_value_and_tag_index_namespaces_are_disjoint() -> None:
    client = _StubRedis()
    backend = RedisCacheBackend(client)
    backend.set("real", {"v": 2}, tags=("foo",))
    value_key = backend._key("real")
    tag_key = backend._tag_key("foo")
    assert value_key != tag_key
    assert value_key.startswith(f"{backend._prefix}v:")
    assert tag_key.startswith(f"{backend._prefix}t:")
    assert backend.invalidate(tags=("foo",)) == 1
    assert backend.get("real") is None
