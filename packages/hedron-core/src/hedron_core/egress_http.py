"""Standard-library HTTP transport for connection-bound Hedron egress."""

from __future__ import annotations

import http.client
import socket
import ssl
from collections.abc import Iterable, Mapping
from typing import Any, cast
from urllib.parse import urlsplit, urlunsplit

from hedron_core.egress import (
    EgressDecision,
    EgressResponse,
    EgressTransportError,
)

_SINGLETON_HEADERS = frozenset({"content-encoding", "content-length", "content-type", "location"})


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection whose TCP destination is a validated IP literal."""

    def __init__(
        self,
        hostname: str,
        address: str,
        port: int,
        *,
        timeout: float,
        context: ssl.SSLContext,
    ) -> None:
        super().__init__(hostname, port=port, timeout=timeout, context=context)
        self._validated_address = address
        self._validated_context = context

    def connect(self) -> None:
        self.sock = socket.create_connection(
            (self._validated_address, self.port),
            self.timeout,
        )
        self.sock = self._validated_context.wrap_socket(self.sock, server_hostname=self.host)


class _PinnedProxyHTTPSConnection(http.client.HTTPSConnection):
    """TLS target reached through one policy-approved HTTP proxy address."""

    def __init__(
        self,
        hostname: str,
        port: int,
        *,
        proxy_address: str,
        proxy_port: int,
        timeout: float,
        context: ssl.SSLContext,
    ) -> None:
        super().__init__(hostname, port=port, timeout=timeout, context=context)
        self._proxy_address = proxy_address
        self._proxy_port = proxy_port
        self._validated_context = context
        self.set_tunnel(hostname, port=port)

    def connect(self) -> None:
        self.sock = socket.create_connection(
            (self._proxy_address, self._proxy_port),
            self.timeout,
        )
        cast(Any, self)._tunnel()
        self.sock = self._validated_context.wrap_socket(self.sock, server_hostname=self.host)


class StdlibEgressTransport:
    """HTTP/1.1 transport that connects only to policy-approved addresses.

    Redirects and decompression stay disabled here and are handled by
    :func:`hedron_core.egress.fetch_with_policy`.
    """

    def __init__(
        self,
        *,
        ssl_context: ssl.SSLContext | None = None,
        chunk_size: int = 65_536,
        user_agent: str = "hedron-egress/1",
    ) -> None:
        raw_chunk_size = cast(Any, chunk_size)
        if (
            isinstance(raw_chunk_size, bool)
            or not isinstance(raw_chunk_size, int)
            or raw_chunk_size < 1
        ):
            raise ValueError("chunk_size must be a positive integer")
        self._ssl_context = ssl_context or ssl.create_default_context()
        self._chunk_size = chunk_size
        self._user_agent = user_agent

    def request(self, *, decision: EgressDecision) -> EgressResponse:
        if not decision.resolved_addresses:
            raise EgressTransportError("dns_unresolved")
        parsed = urlsplit(decision.url)
        target = urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
        host_header = _authority(decision.host, decision.port, decision.scheme)
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
            "Host": host_header,
            "User-Agent": self._user_agent,
        }
        connection: http.client.HTTPConnection
        via_proxy = decision.proxy_url is not None
        if via_proxy:
            connection = self._proxy_connection(decision)
            if decision.scheme == "http":
                target = decision.url
        elif decision.scheme == "https":
            connection = _PinnedHTTPSConnection(
                decision.host,
                _address_for_attempt(decision.resolved_addresses, decision.attempt),
                decision.port,
                timeout=decision.connect_deadline_seconds,
                context=self._ssl_context,
            )
        else:
            connection = http.client.HTTPConnection(
                _address_for_attempt(decision.resolved_addresses, decision.attempt),
                decision.port,
                timeout=decision.connect_deadline_seconds,
            )

        try:
            connection.request(
                "GET",
                target,
                headers=headers,
                encode_chunked=False,
            )
            sock = connection.sock
            if sock is None:
                raise EgressTransportError("transport_peer_unavailable", retryable=True)
            peer = str(sock.getpeername()[0])
            sock.settimeout(decision.read_deadline_seconds)
            response = connection.getresponse()
            response_headers = _response_headers(response)
        except EgressTransportError:
            connection.close()
            raise
        except (OSError, http.client.HTTPException, ssl.SSLError) as exc:
            connection.close()
            raise EgressTransportError("transport_failure", retryable=True) from exc

        def body() -> Iterable[bytes]:
            try:
                while True:
                    try:
                        chunk = response.read(self._chunk_size)
                    except (OSError, http.client.HTTPException, ssl.SSLError) as exc:
                        raise EgressTransportError("transport_read_failure") from exc
                    if not chunk:
                        break
                    yield chunk
            finally:
                response.close()
                connection.close()

        return EgressResponse(
            status_code=response.status,
            headers=response_headers,
            body=body(),
            connected_address=peer,
            via_proxy=via_proxy,
            close=lambda: _close_response(response, connection),
        )

    def _proxy_connection(self, decision: EgressDecision) -> http.client.HTTPConnection:
        if decision.proxy_url is None or not decision.proxy_resolved_addresses:
            raise EgressTransportError("proxy_dns_unresolved")
        proxy = urlsplit(decision.proxy_url)
        proxy_port = proxy.port if proxy.port is not None else 80
        proxy_address = _address_for_attempt(decision.proxy_resolved_addresses, decision.attempt)
        if decision.scheme == "https":
            return _PinnedProxyHTTPSConnection(
                decision.host,
                decision.port,
                proxy_address=proxy_address,
                proxy_port=proxy_port,
                timeout=decision.connect_deadline_seconds,
                context=self._ssl_context,
            )
        return http.client.HTTPConnection(
            proxy_address,
            proxy_port,
            timeout=decision.connect_deadline_seconds,
        )


def _address_for_attempt(addresses: tuple[str, ...], attempt: int) -> str:
    return addresses[attempt % len(addresses)]


def _authority(host: str, port: int, scheme: str) -> str:
    display_host = f"[{host}]" if ":" in host else host
    default = 443 if scheme == "https" else 80
    return display_host if port == default else f"{display_host}:{port}"


def _response_headers(response: http.client.HTTPResponse) -> Mapping[str, str]:
    grouped: dict[str, list[str]] = {}
    for raw_name, raw_value in response.getheaders():
        name = str(raw_name).strip().lower()
        grouped.setdefault(name, []).append(str(raw_value).strip())
    for name in _SINGLETON_HEADERS:
        values = grouped.get(name, [])
        if len(values) > 1 and len(set(values)) != 1:
            raise EgressTransportError("conflicting_response_headers")
    return {name: values[-1] for name, values in grouped.items() if values}


def _close_response(
    response: http.client.HTTPResponse,
    connection: http.client.HTTPConnection,
) -> None:
    response.close()
    connection.close()
