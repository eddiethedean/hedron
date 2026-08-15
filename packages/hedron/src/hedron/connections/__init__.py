"""Named resource/connection registry over host DI and lifespan.

Owned per-app via ``app.state.hedron_connections`` — not a process-global locator.
Secret values stay as opaque refs/strings; Hedron does not store a secret manager.
"""

from __future__ import annotations

from hedron.connections.registry import ClosableConnection as ClosableConnection
from hedron.connections.registry import ConnectionKind as ConnectionKind
from hedron.connections.registry import ConnectionRegistry as ConnectionRegistry
from hedron.connections.registry import ConnectionSpec as ConnectionSpec
from hedron.connections.registry import _dispose_instance_async as _dispose_instance_async
from hedron.connections.registry import bind_connection_fixture as bind_connection_fixture
from hedron.connections.registry import connection_dependency as connection_dependency
from hedron.connections.registry import get_connection as get_connection
from hedron.connections.registry import install_connections as install_connections
from hedron.connections.snowflake import (
    snowflake_connection_factory as snowflake_connection_factory,
)
from hedron.connections.sqlalchemy import (
    sqlalchemy_connection_factory as sqlalchemy_connection_factory,
)

__all__ = [
    "ClosableConnection",
    "ConnectionKind",
    "ConnectionRegistry",
    "ConnectionSpec",
    "bind_connection_fixture",
    "connection_dependency",
    "get_connection",
    "install_connections",
    "snowflake_connection_factory",
    "sqlalchemy_connection_factory",
]
