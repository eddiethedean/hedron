"""Governed example sets for model demos."""

from __future__ import annotations

import hashlib
import math
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import cast

from hedron_core.typing_aliases import JsonValue


@dataclass(frozen=True, slots=True)
class ExampleItem:
    example_id: str
    label: str
    inputs: Mapping[str, JsonValue]
    provenance: str = ""
    partial: bool = False
    authorized_roles: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CachedExampleResult:
    cache_key: str
    example_id: str
    outputs: Mapping[str, JsonValue]
    generated_at: float
    cost_units: float = 0.0
    stale: bool = False
    retention_seconds: float | None = None


@dataclass
class ExampleSet:
    """Versioned sample inputs with provenance and inspectable cached results."""

    set_id: str
    action_id: str
    model_version: str = "1"
    schema_version: str = "1"
    code_version: str = "1"
    preprocessing_version: str = "1"
    page_size: int = 10
    _items: list[ExampleItem] = field(default_factory=list[ExampleItem], init=False)
    _cache: dict[str, CachedExampleResult] = field(
        default_factory=dict[str, CachedExampleResult], init=False
    )

    def add(self, item: ExampleItem) -> None:
        self._items.append(item)

    def cache_key_for(self, example_id: str) -> str:
        material = "|".join(
            [
                self.action_id,
                self.model_version,
                self.schema_version,
                self.code_version,
                self.preprocessing_version,
                example_id,
            ]
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]

    def store_result(
        self,
        example_id: str,
        outputs: Mapping[str, JsonValue],
        *,
        cost_units: float = 0.0,
        retention_seconds: float | None = 86400.0,
    ) -> CachedExampleResult:
        retention = cast(object, retention_seconds)
        if retention is not None and (
            isinstance(retention, bool)
            or not isinstance(retention, (int, float))
            or not math.isfinite(float(retention))
        ):
            raise ValueError("retention_seconds must be finite or None")
        key = self.cache_key_for(example_id)
        result = CachedExampleResult(
            cache_key=key,
            example_id=example_id,
            outputs=dict(outputs),
            generated_at=time.time(),
            cost_units=cost_units,
            retention_seconds=retention_seconds,
        )
        self._cache[key] = result
        return result

    def get_cached(
        self, example_id: str, *, now: float | None = None
    ) -> CachedExampleResult | None:
        key = self.cache_key_for(example_id)
        result = self._cache.get(key)
        if result is None:
            return None
        clock = time.time() if now is None else now
        if result.retention_seconds is not None:
            age = clock - result.generated_at
            if age > result.retention_seconds:
                return CachedExampleResult(
                    cache_key=result.cache_key,
                    example_id=result.example_id,
                    outputs=result.outputs,
                    generated_at=result.generated_at,
                    cost_units=result.cost_units,
                    stale=True,
                    retention_seconds=result.retention_seconds,
                )
        return result

    def invalidate(self, *, reason: str = "version") -> int:
        count = len(self._cache)
        self._cache.clear()
        return count

    def page(
        self, *, offset: int = 0, limit: int | None = None, role: str | None = None
    ) -> list[ExampleItem]:
        size = self.page_size if limit is None else limit
        items = [
            item
            for item in self._items
            if not item.authorized_roles or (role is not None and role in item.authorized_roles)
        ]
        return items[offset : offset + size]

    @property
    def size(self) -> int:
        return len(self._items)
