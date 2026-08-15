"""SQLAlchemy connection factory helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

__all__ = ["sqlalchemy_connection_factory"]


def sqlalchemy_connection_factory(
    url_or_engine: object,
    *,
    statement: object | None = None,
    session_factory: Callable[[], object] | None = None,
    **source_kwargs: Any,  # forwarded host kwargs for SQLAlchemyDataSource
) -> Callable[[], object]:
    """Lazy factory for a SQLAlchemy Engine or :class:`SQLAlchemyDataSource`.

    Without ``statement``, returns ``url_or_engine`` when it already looks like an
    engine, otherwise builds one via ``sqlalchemy.create_engine``. With ``statement``,
    lazy-imports ``hedron_data`` and returns a :class:`SQLAlchemyDataSource`.
    """

    def _factory() -> object:
        if statement is not None:
            from hedron_data.sqlalchemy_source import SQLAlchemyDataSource

            if session_factory is not None:
                sf = session_factory
            else:
                engine = url_or_engine
                if isinstance(url_or_engine, str) or not hasattr(url_or_engine, "connect"):
                    from sqlalchemy import create_engine

                    engine = create_engine(
                        url_or_engine if isinstance(url_or_engine, str) else str(url_or_engine)
                    )

                def sf() -> object:
                    return engine.connect()  # type: ignore[union-attr]  # engine from create_engine/connect

            return SQLAlchemyDataSource(
                session_factory=sf,  # type: ignore[arg-type]  # host session factory duck-types _SessionLike
                statement=statement,
                **source_kwargs,
            )

        if not isinstance(url_or_engine, str) and hasattr(url_or_engine, "connect"):
            return url_or_engine
        from sqlalchemy import create_engine

        return create_engine(
            url_or_engine if isinstance(url_or_engine, str) else str(url_or_engine)
        )

    return _factory
