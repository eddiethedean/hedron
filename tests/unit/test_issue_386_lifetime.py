"""#386: DependsOn lifetime strings compile like the enum members."""

from __future__ import annotations

from hedron import DependencyLifetime, DependsOn
from hedron.type_authoring.depends import as_fastapi_depends
from hedron_core.lifetime import compile_fastapi_scope


def test_string_response_lifetime_compiles_to_request_scope() -> None:
    assert compile_fastapi_scope("response") == "request"
    assert compile_fastapi_scope(DependencyLifetime.RESPONSE) == "request"
    dep = as_fastapi_depends(DependsOn("db", lifetime="response"))
    assert dep.scope == "request"
    stream = DependsOn("sse", lifetime="response", streaming=True).plan()
    assert stream.lifetime == DependencyLifetime.RESPONSE
