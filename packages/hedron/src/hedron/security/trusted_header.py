"""Fail-closed trusted-header identity for identity-aware proxies.

Extracts an identity string from a configured header **only** when
``request.client.host`` is in the peer allowlist. Does not auto-provision users
or invent authorization — applications map the returned identity into their own
session / authorization layer. Flask/Django follow-up: apply the same allowlist
check on ``request.remote_addr`` / ``request.META['REMOTE_ADDR']`` before reading
the header.
"""

from __future__ import annotations

from collections.abc import Callable, Collection, Iterable
from typing import Any

from fastapi import HTTPException, Request, status

__all__ = ["TrustedHeaderIdentity"]


class TrustedHeaderIdentity:
    """Allowlisted-peer header identity adapter (no auto-provisioning)."""

    def __init__(
        self,
        allowlisted_peers: Collection[str],
        header_name: str = "X-Forwarded-User",
        *,
        require_identity: bool = True,
    ) -> None:
        peers = {str(p).strip() for p in allowlisted_peers if str(p).strip()}
        if not peers:
            raise ValueError("allowlisted_peers must contain at least one peer")
        name = header_name.strip()
        if not name:
            raise ValueError("header_name must be a non-empty string")
        self.allowlisted_peers = frozenset(peers)
        self.header_name = name
        self.require_identity = require_identity

    def peer_allowed(self, request: Request) -> bool:
        host = request.client.host if request.client else None
        return bool(host and host in self.allowlisted_peers)

    def extract(self, request: Request) -> str | None:
        """Return header identity when peer is allowlisted; else ``None`` (fail closed)."""
        if not self.peer_allowed(request):
            return None
        raw = request.headers.get(self.header_name)
        if raw is None:
            return None
        value = raw.strip()
        return value or None

    def dependency(self) -> Callable[..., Any]:
        """FastAPI dependency factory returning the identity string."""

        def _dep(request: Request) -> str | None:
            identity = self.extract(request)
            if identity is None and self.require_identity:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Trusted-header identity unavailable",
                )
            return identity

        return _dep

    def as_allowlist(self) -> Iterable[str]:
        return sorted(self.allowlisted_peers)
