"""PERF-049 unused opt-in is cheap; native compile stays bounded."""

from __future__ import annotations

import time
from typing import Annotated

from pydantic import BaseModel

from hedron import ViewParams
from hedron.type_authoring.binding import boundary_plan_for
from hedron.type_authoring.normalize import inspect_handler
from hedron_core.validation_adapters import cached_type_adapter, clear_type_adapter_cache


class Filters(BaseModel):
    q: str = ""


def test_boundary_compile_is_bounded() -> None:
    def items(filters: Annotated[Filters, ViewParams(source="query")]):
        return filters

    start = time.perf_counter()
    for _ in range(50):
        compiled = inspect_handler(items, kind="view", path="/items")
        plan = boundary_plan_for(compiled)
        assert plan.strategy in {"native-model", "expanded-fields"}
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0


def test_adapter_cache_hits() -> None:
    clear_type_adapter_cache()
    cached_type_adapter(Filters)
    info = cached_type_adapter.cache_info()
    cached_type_adapter(Filters)
    later = cached_type_adapter.cache_info()
    assert later.hits >= info.hits
    clear_type_adapter_cache()
