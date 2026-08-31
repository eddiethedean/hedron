"""Adversarial and live connection evidence for GitHub issue #555."""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar

from hedron_core.security_plane import (
    EgressPolicy,
    StdlibEgressTransport,
    fetch_with_policy,
)


class _RedirectHandler(BaseHTTPRequestHandler):
    hosts: ClassVar[list[str]] = []

    def do_GET(self) -> None:
        self.hosts.append(self.headers["Host"])
        if self.path == "/start":
            self.send_response(302)
            self.send_header("Location", "/final")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        body = b'{"connection":"pinned"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        del format
        del args


def test_stdlib_transport_connects_to_validated_ip_and_revalidates_redirects() -> None:
    _RedirectHandler.hosts = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _RedirectHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    calls: list[str] = []

    def resolver(host: str) -> tuple[str, ...]:
        calls.append(host)
        return ("127.0.0.1",)

    try:
        port = int(server.server_address[1])
        body = fetch_with_policy(
            f"http://rebind.test:{port}/start",
            policy=EgressPolicy(
                allowed_schemes=frozenset({"http"}),
                allowed_hosts=frozenset({"rebind.test"}),
                allowed_origins=frozenset({f"http://rebind.test:{port}"}),
                allowed_ports=frozenset({port}),
                allow_private_addresses=True,
                max_redirects=1,
                connect_deadline_seconds=2,
                read_deadline_seconds=2,
                total_deadline_seconds=5,
                expected_content_types=frozenset({"application/json"}),
            ),
            transport=StdlibEgressTransport(chunk_size=3),
            resolver=resolver,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert body == b'{"connection":"pinned"}'
    assert calls == ["rebind.test", "rebind.test"]
    assert _RedirectHandler.hosts == [
        f"rebind.test:{port}",
        f"rebind.test:{port}",
    ]
