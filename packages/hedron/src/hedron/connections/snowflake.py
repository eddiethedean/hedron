"""Snowflake connection factory helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from importlib import import_module
from typing import Any, Protocol, cast

__all__ = ["snowflake_connection_factory"]


class _SnowflakeConnector(Protocol):
    def connect(self, **kwargs: object) -> object: ...


def snowflake_connection_factory(
    *,
    connection_factory: Callable[[], object] | None = None,
    statement: str | None = None,
    connect_kwargs: Mapping[str, object] | None = None,
    **source_kwargs: Any,  # forwarded host kwargs for SnowflakeDataSource
) -> Callable[[], object]:
    """Lazy factory for a Snowflake connection or :class:`SnowflakeDataSource`.

    With ``statement``, wraps :class:`~hedron_data.snowflake_source.SnowflakeDataSource`.
    Without it, returns a live connection from ``connection_factory`` or
    ``snowflake.connector.connect(**connect_kwargs)``.
    """
    connect_kwargs = dict(connect_kwargs or {})

    def _connect() -> object:
        if connection_factory is not None:
            return connection_factory()
        connector = cast(_SnowflakeConnector, import_module("snowflake.connector"))
        return connector.connect(**connect_kwargs)

    def _factory() -> object:
        if statement is not None:
            from hedron_data.snowflake_source import SnowflakeDataSource

            return SnowflakeDataSource(
                connection_factory=_connect if connection_factory is None else connection_factory,
                statement=statement,
                **source_kwargs,
            )
        return _connect()

    return _factory
